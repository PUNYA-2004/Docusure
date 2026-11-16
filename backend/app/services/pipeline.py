import time
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.models.schemas import (
    DocumentProcessResponse, ExtractedField, LineItem, DocumentAnomaly,
    VerificationStatus, OverallDecision, EvidenceAttribution, ConfidenceLevel
)
from app.config import DOCUMENT_SCHEMAS
from app.services.ingestion import DocumentIngestionService
from app.services.ocr_engine import OCREngine
from app.services.classifier import DocumentClassifier
from app.services.extractor import InformationExtractor
from app.services.evidence_locator import EvidenceLocator
from app.services.verifier import ExtractionVerifier
from app.services.confidence_calibrator import ConfidenceCalibrator
from app.services.anomaly_detector import AnomalyDetector
from app.database import save_document, add_audit_log

class DocumentProcessingPipeline:
    def __init__(self):
        self.ocr_engine = OCREngine()

    def process(
        self,
        file_bytes: bytes,
        filename: str,
        forced_doc_type: Optional[str] = None
    ) -> DocumentProcessResponse:
        start_time = time.time()
        
        # 1. Document Ingestion
        ingest_res = DocumentIngestionService.process_upload(file_bytes, filename)
        doc_id = ingest_res["document_id"]
        file_path = ingest_res["file_path"]
        page_count = ingest_res["page_count"]
        pages_info = ingest_res["pages"]

        add_audit_log(doc_id, "UPLOAD", "SYSTEM", {
            "filename": filename,
            "page_count": page_count,
            "is_pdf": ingest_res["is_pdf"]
        })

        # 2. OCR & Token Extraction (Words, Lines, Bounding Boxes)
        token_res = self.ocr_engine.extract_document_tokens(file_path, pages_info)
        full_text = token_res["full_text"]
        pages_tokens = token_res["pages"]

        # 3. Document Classification
        if forced_doc_type and forced_doc_type.upper() in DOCUMENT_SCHEMAS:
            doc_type = forced_doc_type.upper()
            classification_conf = 1.0
            classification_reasons = ["User manually specified document type."]
        else:
            cls_res = DocumentClassifier.classify(full_text)
            doc_type = cls_res.document_type
            classification_conf = cls_res.confidence
            classification_reasons = cls_res.reasons

        add_audit_log(doc_id, "CLASSIFICATION", "SYSTEM", {
            "predicted_type": doc_type,
            "confidence": classification_conf,
            "reasons": classification_reasons
        })

        # 4. Schema-based Structured Extraction
        raw_extraction = InformationExtractor.extract(doc_type, full_text, pages_tokens)
        extracted_fields_dict = raw_extraction["fields"]
        extracted_line_items = raw_extraction["line_items"]

        # 5. Evidence Attribution, Verification, & Confidence Scoring
        schema_rules = DOCUMENT_SCHEMAS.get(doc_type, [])
        processed_fields: List[ExtractedField] = []

        for rule in schema_rules:
            fname = rule["name"]
            fdisplay = rule["display"]
            is_req = rule.get("required", False)

            extracted_val = extracted_fields_dict.get(fname, "NOT_FOUND")

            # 5a. Evidence Attribution (VERITAS)
            evidence = EvidenceLocator.locate_evidence(fname, extracted_val, pages_tokens)

            # 5b. Extraction Verification
            status, verif_reason, correction = ExtractionVerifier.verify_field(
                field_name=fname,
                extracted_val=extracted_val,
                evidence=evidence,
                ocr_confidence=0.98 if ingest_res["is_pdf"] else 0.85
            )

            # 5c. Confidence Estimation & Calibration
            ev_score = evidence.matched_score if evidence else 0.0
            confidence, conf_level = ConfidenceCalibrator.estimate_field_confidence(
                status=status,
                evidence_score=ev_score,
                ocr_confidence=0.98 if ingest_res["is_pdf"] else 0.85,
                field_required=is_req
            )

            processed_fields.append(ExtractedField(
                field_name=fname,
                display_name=fdisplay,
                value=extracted_val,
                confidence=confidence,
                confidence_level=conf_level,
                status=status,
                evidence=evidence,
                verification_reason=verif_reason,
                suggested_correction=correction
            ))

        # Also locate evidence for line items
        for item in extracted_line_items:
            item_ev = EvidenceLocator.locate_evidence("item", item.description, pages_tokens)
            item.evidence = item_ev

        # 6. Anomaly & Consistency Detection (SENTINEL)
        anomalies = AnomalyDetector.analyze_document(
            doc_type=doc_type,
            fields=processed_fields,
            line_items=extracted_line_items
        )

        for ano in anomalies:
            add_audit_log(doc_id, "ANOMALY_FLAGGED", "SYSTEM", {
                "field": ano.field_name,
                "severity": ano.severity,
                "title": ano.title,
                "reason": ano.reason
            })

        # 7. Overall Decision Determination
        # AUTO-ACCEPT, REVIEW REQUIRED, REJECT / INVESTIGATE
        has_contradiction = any(f.status == VerificationStatus.CONTRADICTED for f in processed_fields)
        has_critical_anomaly = any(a.severity == "CRITICAL" for a in anomalies)
        avg_confidence = round(sum(f.confidence for f in processed_fields) / max(1, len(processed_fields)), 3)

        if has_contradiction or has_critical_anomaly:
            decision = OverallDecision.REJECT_INVESTIGATE
        elif avg_confidence < 0.85 or any(f.confidence_level == ConfidenceLevel.LOW for f in processed_fields) or len(anomalies) > 0:
            decision = OverallDecision.REVIEW_REQUIRED
        else:
            decision = OverallDecision.AUTO_ACCEPT

        # Calculate counts
        verified_count = sum(1 for f in processed_fields if f.status == VerificationStatus.SUPPORTED)
        uncertain_count = sum(1 for f in processed_fields if f.status == VerificationStatus.UNCERTAIN)
        contradicted_count = sum(1 for f in processed_fields if f.status == VerificationStatus.CONTRADICTED)
        unsupported_count = sum(1 for f in processed_fields if f.status == VerificationStatus.UNSUPPORTED)

        processing_time_ms = round((time.time() - start_time) * 1000, 2)
        upload_time_str = datetime.utcnow().isoformat()

        response = DocumentProcessResponse(
            document_id=doc_id,
            filename=filename,
            document_type=doc_type,
            page_count=page_count,
            pages_preview_urls=[p["preview_url"] for p in pages_info],
            overall_decision=decision,
            average_confidence=avg_confidence,
            total_fields=len(processed_fields),
            verified_count=verified_count,
            uncertain_count=uncertain_count,
            contradicted_count=contradicted_count,
            unsupported_count=unsupported_count,
            anomaly_count=len(anomalies),
            fields=processed_fields,
            line_items=extracted_line_items,
            anomalies=anomalies,
            ocr_raw_text=full_text,
            processing_time_ms=processing_time_ms,
            upload_timestamp=upload_time_str
        )

        # 8. Persist to Database
        save_document({
            "id": doc_id,
            "filename": filename,
            "file_path": file_path,
            "doc_type": doc_type,
            "page_count": page_count,
            "upload_time": upload_time_str,
            "overall_decision": decision.value,
            "average_confidence": avg_confidence,
            "raw_ocr_text": full_text,
            "processed_data": response.model_dump()
        })

        add_audit_log(doc_id, "PIPELINE_COMPLETE", "SYSTEM", {
            "decision": decision.value,
            "average_confidence": avg_confidence,
            "verified_fields": verified_count,
            "anomalies": len(anomalies),
            "processing_time_ms": processing_time_ms
        })

        return response
