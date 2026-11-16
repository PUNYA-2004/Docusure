import re
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.schemas import DocumentAnomaly, ExtractedField, LineItem, VerificationStatus
from app.config import DOCUMENT_SCHEMAS

class AnomalyDetector:
    """
    SENTINEL-inspired Explainable Document Anomaly & Inconsistency Detection:
    Performs deterministic arithmetic checks, temporal chronology validation,
    missing-field detection, and evidence contradiction analysis.
    """

    @classmethod
    def analyze_document(
        cls,
        doc_type: str,
        fields: List[ExtractedField],
        line_items: List[LineItem]
    ) -> List[DocumentAnomaly]:
        anomalies: List[DocumentAnomaly] = []
        field_map = {f.field_name: f for f in fields}

        # Check 1: Mandatory Schema Fields Missing
        schema = DOCUMENT_SCHEMAS.get(doc_type.upper(), [])
        for rule in schema:
            fname = rule["name"]
            if rule.get("required", False):
                field_obj = field_map.get(fname)
                if not field_obj or field_obj.value == "NOT_FOUND" or field_obj.status == VerificationStatus.UNSUPPORTED:
                    anomalies.append(DocumentAnomaly(
                        anomaly_id=f"ano_{uuid.uuid4().hex[:8]}",
                        field_name=fname,
                        severity="CRITICAL",
                        title=f"Mandatory Field Missing: {rule['display']}",
                        reason=f"The required field '{rule['display']}' could not be detected or verified in the document.",
                        extracted_value="NOT_FOUND",
                        calculated_or_expected="Valid document token",
                        recommended_action="Manual entry or document rescan required."
                    ))

        # Check 2: Contradicted Fields
        for f in fields:
            if f.status == VerificationStatus.CONTRADICTED:
                anomalies.append(DocumentAnomaly(
                    anomaly_id=f"ano_{uuid.uuid4().hex[:8]}",
                    field_name=f.field_name,
                    severity="CRITICAL",
                    title=f"Evidence Contradiction: {f.display_name}",
                    reason=f.verification_reason,
                    extracted_value=f.value,
                    calculated_or_expected=f.suggested_correction or (f.evidence.source_text if f.evidence else "N/A"),
                    recommended_action="Review highlighted document evidence and confirm correct figure."
                ))

        # Check 3: Invoice Math Consistency (Line Items vs Total)
        if doc_type.upper() == "INVOICE":
            # 3a. Line item math: Quantity * Unit Price vs Line Total
            for item in line_items:
                if not item.is_match:
                    anomalies.append(DocumentAnomaly(
                        anomaly_id=f"ano_{uuid.uuid4().hex[:8]}",
                        field_name="line_items",
                        severity="WARNING",
                        title=f"Line Item Math Discrepancy ({item.description})",
                        reason=f"For '{item.description}', Quantity ({item.quantity}) × Unit Price (INR {item.unit_price:,.2f}) equals INR {item.computed_total:,.2f}, but extracted line total is INR {item.line_total:,.2f} (Discrepancy: INR {item.discrepancy:,.2f}).",
                        extracted_value=f"INR {item.line_total:,.2f}",
                        calculated_or_expected=f"INR {item.computed_total:,.2f}",
                        recommended_action="Check for unitemized discount, tax component, or calculation error."
                    ))

            # 3b. Sum of line items vs Grand Total
            total_field = field_map.get("total_amount")
            if total_field and total_field.value != "NOT_FOUND" and line_items:
                try:
                    total_val = float(re.sub(r"[^\d.]", "", total_field.value))
                    items_sum = sum(item.line_total for item in line_items)
                    tax_field = field_map.get("tax_amount")
                    tax_val = float(re.sub(r"[^\d.]", "", tax_field.value)) if tax_field and tax_field.value != "NOT_FOUND" else 0.0

                    expected_total = items_sum + tax_val
                    discrepancy = round(abs(total_val - expected_total), 2)
                    if discrepancy > 1.0:
                        anomalies.append(DocumentAnomaly(
                            anomaly_id=f"ano_{uuid.uuid4().hex[:8]}",
                            field_name="total_amount",
                            severity="CRITICAL",
                            title="Invoice Total Mismatch with Line Items",
                            reason=f"Extracted grand total (INR {total_val:,.2f}) differs from calculated sum of line items + tax (INR {expected_total:,.2f}) by INR {discrepancy:,.2f}.",
                            extracted_value=f"INR {total_val:,.2f}",
                            calculated_or_expected=f"INR {expected_total:,.2f}",
                            recommended_action="Verify line items table against invoice summary."
                        ))
                except ValueError:
                    pass

            # 3c. Date Logic (Invoice Date vs Due Date)
            inv_date_f = field_map.get("invoice_date")
            due_date_f = field_map.get("due_date")
            if inv_date_f and due_date_f and inv_date_f.value != "NOT_FOUND" and due_date_f.value != "NOT_FOUND":
                inv_dt = cls._parse_date(inv_date_f.value)
                due_dt = cls._parse_date(due_date_f.value)
                if inv_dt and due_dt and due_dt < inv_dt:
                    anomalies.append(DocumentAnomaly(
                        anomaly_id=f"ano_{uuid.uuid4().hex[:8]}",
                        field_name="due_date",
                        severity="WARNING",
                        title="Temporal Chronology Inversion",
                        reason=f"Invoice Due Date ({due_date_f.value}) precedes the Invoice Issuance Date ({inv_date_f.value}), which is an operational impossibility.",
                        extracted_value=due_date_f.value,
                        calculated_or_expected=f"Date on or after {inv_date_f.value}",
                        recommended_action="Verify dates on the invoice document header."
                    ))

        # Check 4: Uncertain/Low Confidence Warnings
        for f in fields:
            if f.confidence < 0.70 and f.value != "NOT_FOUND" and f.status != VerificationStatus.CONTRADICTED:
                anomalies.append(DocumentAnomaly(
                    anomaly_id=f"ano_{uuid.uuid4().hex[:8]}",
                    field_name=f.field_name,
                    severity="INFO",
                    title=f"Low Extraction Confidence ({f.display_name})",
                    reason=f"Confidence for '{f.display_name}' is {round(f.confidence * 100, 1)}% due to OCR ambiguity or partial text match. {f.verification_reason}",
                    extracted_value=f.value,
                    calculated_or_expected="Verified token",
                    recommended_action="Human operator review recommended."
                ))

        return anomalies

    @staticmethod
    def _parse_date(date_str: str) -> Optional[datetime]:
        clean = date_str.strip().replace("/", "-").replace(".", "-")
        formats = ["%d-%m-%Y", "%Y-%m-%d", "%m-%d-%Y", "%d-%m-%y"]
        for fmt in formats:
            try:
                return datetime.strptime(clean, fmt)
            except ValueError:
                continue
        return None
