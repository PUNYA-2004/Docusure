import time
import json
import csv
import io
import hashlib
import urllib.request
import ssl
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.config import REPORTS_DIR, BASE_DIR
from app.models.brsr_schemas import (
    BRSRReportMetadata, BRSRCanonicalObservation, BRSRReportProcessingResult,
    DocumentType, ExtractionStatus, ClassificationConfidence
)
from app.services.brsr_parser import BRSRParser
from app.services.brsr_extractor import BRSRInformationExtractor
from app.services.brsr_classifier import BRSRClassifier
from app.database import (
    save_brsr_report, get_brsr_report, list_brsr_reports,
    save_brsr_observations, get_brsr_observations, update_brsr_observation,
    get_brsr_report_by_hash
)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

class BRSRProcessingService:
    """
    Coordinates end-to-end BRSR Intelligence Workflow:
    1. Report Collection & Ingestion (Local File, Upload, Public URL)
    2. PDF Parsing & Document Classification
    3. Section & Principle Localization
    4. Deterministic ESG Extraction
    5. Unit Normalization & Mapping
    6. Multi-dimensional ESG & Principle Classification
    7. Database Persistence
    8. Dataset Export (CSV / JSON)
    """

    def __init__(self):
        self.parser = BRSRParser()

    def register_or_import_report(
        self,
        company_name: str,
        financial_year: str,
        industry: Optional[str] = "Diversified",
        file_bytes: Optional[bytes] = None,
        filename: Optional[str] = None,
        source_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Registers a report from uploaded bytes, existing path, or public URL."""
        if file_bytes is None and source_url:
            # Download from public URL
            try:
                req = urllib.request.Request(
                    source_url,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                )
                with urllib.request.urlopen(req, timeout=25, context=ctx) as resp:
                    file_bytes = resp.read()
                filename = filename or f"{company_name.replace(' ', '_')}_{financial_year}_BRSR.pdf"
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to download report from URL: {str(e)}"
                }

        if not file_bytes:
            return {"success": False, "error": "No file content or valid URL provided."}

        # Calculate file hash for duplicate detection
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        existing = get_brsr_report_by_hash(file_hash)
        if existing:
            return {
                "success": True,
                "is_duplicate": True,
                "message": f"Report already exists in repository (Duplicate detected via SHA-256: {file_hash[:12]}...).",
                "report": existing
            }

        # Save to organized directory
        safe_company = "".join(c for c in company_name if c.isalnum() or c in (" ", "-", "_")).strip()
        target_dir = REPORTS_DIR / safe_company / financial_year
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / (filename or "report.pdf")

        with open(target_file, "wb") as f:
            f.write(file_bytes)

        report_id = f"brsr_{safe_company[:6].lower()}_{financial_year.replace('-', '')}_{file_hash[:6]}"
        rel_path = str(target_file.relative_to(BASE_DIR.parent))

        report_data = {
            "report_id": report_id,
            "company_name": company_name,
            "industry": industry,
            "financial_year": financial_year,
            "report_title": f"Business Responsibility & Sustainability Report {financial_year}",
            "report_category": "BRSR Report",
            "source_url": source_url or "Manual Upload",
            "local_file_path": rel_path,
            "file_hash_sha256": file_hash,
            "file_size_bytes": len(file_bytes),
            "page_count": 0,
            "upload_status": "COMPLETED",
            "processing_status": "READY_FOR_PARSING",
            "error_message": None,
            "document_type": DocumentType.BRSR_STANDALONE.value,
            "created_at": datetime.utcnow().isoformat()
        }

        save_brsr_report(report_data)
        return {
            "success": True,
            "is_duplicate": False,
            "message": f"Successfully registered BRSR report for {company_name} ({financial_year}).",
            "report": report_data
        }

    def process_report(self, report_id: str) -> BRSRReportProcessingResult:
        """Runs the complete parsing, extraction, and classification pipeline on a report."""
        start_time = time.time()
        report = get_brsr_report(report_id)
        if not report:
            raise ValueError(f"Report ID '{report_id}' not found.")

        local_path = BASE_DIR.parent / report["local_file_path"]
        if not local_path.exists():
            # Check relative to REPORTS_DIR directly
            safe_comp = report["company_name"]
            alt_path = REPORTS_DIR / safe_comp / report["financial_year"] / "report.pdf"
            if alt_path.exists():
                local_path = alt_path
            else:
                raise FileNotFoundError(f"Report PDF file not found at: {local_path}")

        # 1. Parse PDF
        parse_res = self.parser.parse_pdf(str(local_path))
        if not parse_res["success"]:
            report["processing_status"] = "ERROR"
            report["error_message"] = parse_res.get("error")
            save_brsr_report(report)
            raise RuntimeError(f"Parsing failed: {parse_res.get('error')}")

        doc_type = parse_res["document_type"]
        page_count = parse_res["page_count"]
        sections_dict = parse_res["sections"]

        # 2. Extract ESG Indicators
        observations = BRSRInformationExtractor.extract_all(
            report_id=report_id,
            company_name=report["company_name"],
            financial_year=report["financial_year"],
            industry=report.get("industry", "Diversified"),
            parsed_pdf=parse_res
        )

        # 3. Classify Observations
        classified_observations = BRSRClassifier.classify_all(observations)

        # 4. Save to Database
        obs_dicts = [obs.dict() for obs in classified_observations]
        save_brsr_observations(obs_dicts)

        report["page_count"] = page_count
        report["document_type"] = doc_type
        report["processing_status"] = "COMPLETED"
        report["parsed_data"] = {
            "sections": sections_dict,
            "tables_count": parse_res.get("tables_count", 0),
            "principle_pages": parse_res.get("principle_pages", {}),
            "classification_confidence": parse_res.get("confidence", 0.95),
            "type_reasons": parse_res.get("type_reasons", [])
        }
        save_brsr_report(report)

        processing_time_ms = round((time.time() - start_time) * 1000, 2)
        extracted_count = sum(1 for o in classified_observations if o.extraction_status in [ExtractionStatus.EXTRACTED, ExtractionStatus.REPORTED_ZERO])

        return BRSRReportProcessingResult(
            report_id=report_id,
            company_name=report["company_name"],
            financial_year=report["financial_year"],
            document_type=doc_type,
            total_pages=page_count,
            sections=sections_dict,
            tables_count=parse_res.get("tables_count", 0),
            total_indicators_extracted=extracted_count,
            observations=classified_observations,
            processing_time_ms=processing_time_ms,
            summary_message=f"Successfully extracted {extracted_count} indicators across Environmental, Social, and Governance categories."
        )

    def export_dataset_csv(
        self,
        company_name: Optional[str] = None,
        financial_year: Optional[str] = None,
        esg_category: Optional[str] = None
    ) -> str:
        """Exports observations into canonical CSV string."""
        observations = get_brsr_observations(
            company_name=company_name,
            esg_category=esg_category
        )
        if financial_year:
            observations = [o for o in observations if o["financial_year"] == financial_year]

        output = io.StringIO()
        fieldnames = [
            "observation_id", "company_name", "industry", "financial_year", "report_type",
            "section_name", "esg_category", "indicator_code", "indicator_name",
            "reported_value", "numeric_value", "unit", "normalized_value", "normalized_unit",
            "reporting_period", "reporting_boundary", "brsr_principle", "brsr_core_indicator",
            "source_page", "source_text", "extraction_method", "classification_status",
            "extraction_status", "confidence_score", "review_status"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for obs in observations:
            writer.writerow(obs)
        return output.getvalue()

    def export_dataset_json(
        self,
        company_name: Optional[str] = None,
        financial_year: Optional[str] = None,
        esg_category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Exports observations into canonical structured JSON."""
        observations = get_brsr_observations(
            company_name=company_name,
            esg_category=esg_category
        )
        if financial_year:
            observations = [o for o in observations if o["financial_year"] == financial_year]
        return observations

    def seed_initial_reports_manifest(self):
        """Loads and processes collected reports if present in manifest."""
        manifest_file = REPORTS_DIR / "reports_manifest.json"
        if not manifest_file.exists():
            return {"seeded": 0}

        with open(manifest_file, "r", encoding="utf-8") as f:
            records = json.load(f)

        seeded_count = 0
        for rec in records:
            p = BASE_DIR.parent / rec["local_file_path"]
            if not p.exists():
                continue
            with open(p, "rb") as f:
                data = f.read()
            fhash = hashlib.sha256(data).hexdigest()
            report_id = f"brsr_{rec['company_name'][:6].lower()}_{rec['financial_year'].replace('-', '')}_{fhash[:6]}"
            
            existing = get_brsr_report(report_id)
            if not existing:
                report_dict = {
                    "report_id": report_id,
                    "company_name": rec["company_name"],
                    "industry": rec.get("industry", "Diversified"),
                    "financial_year": rec["financial_year"],
                    "report_title": rec["report_title"],
                    "report_category": rec["report_category"],
                    "source_url": rec["source_url"],
                    "local_file_path": rec["local_file_path"],
                    "file_hash_sha256": fhash,
                    "file_size_bytes": len(data),
                    "page_count": rec.get("page_count", 0),
                    "upload_status": "COMPLETED",
                    "processing_status": "READY_FOR_PARSING",
                    "error_message": None,
                    "document_type": DocumentType.BRSR_STANDALONE.value,
                    "created_at": datetime.utcnow().isoformat()
                }
                save_brsr_report(report_dict)
                seeded_count += 1

        return {"seeded": seeded_count, "total_manifest": len(records)}

    def get_page_preview_file(self, report_id: str, page_num: int) -> Optional[Path]:
        """Renders and returns path to page preview PNG image."""
        report = get_brsr_report(report_id)
        if not report:
            return None
        local_path = BASE_DIR.parent / report["local_file_path"]
        if not local_path.exists():
            safe_comp = report["company_name"]
            alt_path = REPORTS_DIR / safe_comp / report["financial_year"] / "report.pdf"
            if alt_path.exists():
                local_path = alt_path
            else:
                return None

        previews_dir = local_path.parent / "previews"
        previews_dir.mkdir(parents=True, exist_ok=True)
        preview_file = previews_dir / f"page_{page_num}.png"
        
        if not preview_file.exists():
            import pymupdf
            try:
                doc = pymupdf.open(str(local_path))
                if page_num < 1 or page_num > len(doc):
                    doc.close()
                    return None
                page = doc[page_num - 1]
                pix = page.get_pixmap(dpi=150)
                pix.save(str(preview_file))
                doc.close()
            except Exception:
                return None
            
        return preview_file


brsr_service = BRSRProcessingService()
