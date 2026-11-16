import re
from typing import Dict, Any, Tuple, Optional
from rapidfuzz import fuzz
from app.models.schemas import VerificationStatus, EvidenceAttribution

class ExtractionVerifier:
    """
    Verification Engine:
    Validates whether extracted entities are grounded in source evidence.
    Classifies status into:
    - SUPPORTED: Value directly backed by document evidence
    - CONTRADICTED: Extracted value conflicts with source evidence
    - UNSUPPORTED: Value fabricated/not present in document
    - UNCERTAIN: Low OCR confidence or ambiguous partial match
    """

    @classmethod
    def verify_field(
        cls,
        field_name: str,
        extracted_val: str,
        evidence: Optional[EvidenceAttribution],
        ocr_confidence: float = 0.95
    ) -> Tuple[VerificationStatus, str, Optional[str]]:
        """
        Returns: (VerificationStatus, verification_reason, suggested_correction)
        """
        # Case 1: Value not found or empty
        if not extracted_val or extracted_val == "NOT_FOUND":
            return (
                VerificationStatus.UNSUPPORTED,
                "Field was not found in the source document (Hallucination prevented).",
                None
            )

        # Case 2: No evidence could be located anywhere in the document
        if evidence is None:
            return (
                VerificationStatus.UNSUPPORTED,
                f"Extracted value '{extracted_val}' could not be located in any page of the document.",
                None
            )

        source_text = evidence.source_text
        match_score = evidence.matched_score

        # Case 3: Uncertain due to poor OCR quality
        if ocr_confidence < 0.65:
            return (
                VerificationStatus.UNCERTAIN,
                f"OCR token confidence is low ({round(ocr_confidence * 100, 1)}%). Visual inspection required.",
                None
            )

        # Case 4: Contradiction Check - Check if number or code differs slightly
        # E.g. extracted ₹48,500 while document says ₹45,800
        extracted_nums = re.findall(r"\d+", extracted_val)
        source_nums = re.findall(r"\d+", source_text)

        if extracted_nums and source_nums:
            # If both have numbers but they differ while sharing the field label context
            if any(num in source_text for num in extracted_nums):
                # Extracted number exists directly in the source text
                pass
            elif match_score >= 0.70 and match_score < 0.95:
                # Close match in label context, but values differ!
                # E.g. "Total Amount: 45,800" vs "48,500"
                suggested = source_nums[-1] if len(source_nums) > 0 else None
                return (
                    VerificationStatus.CONTRADICTED,
                    f"Extracted value '{extracted_val}' contradicts source evidence text: '{source_text}'.",
                    suggested
                )

        # Case 5: Direct Support
        if match_score >= 0.85:
            return (
                VerificationStatus.SUPPORTED,
                f"Ground-truth match verified against page {evidence.page} evidence with {round(match_score * 100, 1)}% alignment.",
                None
            )
        elif match_score >= 0.70:
            return (
                VerificationStatus.UNCERTAIN,
                f"Partial evidence alignment ({round(match_score * 100, 1)}%). Human verification advised.",
                None
            )
        else:
            return (
                VerificationStatus.UNSUPPORTED,
                f"Evidence text '{source_text}' has insufficient alignment ({round(match_score * 100, 1)}%) with extracted value.",
                None
            )
