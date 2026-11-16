import re
from typing import Dict, Any, List
from app.models.schemas import DocumentClassificationResult

class DocumentClassifier:
    """
    Deterministic & Heuristic Document Classifier:
    Analyzes document text, lexical cues, and structural tokens to determine
    the document category and recommend the appropriate extraction schema.
    """

    KEYWORD_PATTERNS = {
        "INVOICE": {
            "primary": [
                r"\binvoice\b", r"\btax invoice\b", r"\bbill to\b", r"\binvoice no\b",
                r"\binvoice number\b", r"\bgst\b", r"\bgstin\b", r"\bsubtotal\b",
                r"\bamount due\b", r"\btotal amount\b", r"\bunit price\b", r"\bhsn\b"
            ],
            "weights": 2.5
        },
        "CERTIFICATE": {
            "primary": [
                r"\bcertificate\b", r"\bcertifies that\b", r"\bhas successfully completed\b",
                r"\bdegree of\b", r"\bconferred upon\b", r"\bacademic year\b",
                r"\bregistration no\b", r"\broll no\b", r"\bdivision\b", r"\bvice chancellor\b",
                r"\bdirector\b", r"\bgrade\b"
            ],
            "weights": 2.5
        },
        "APPLICATION_FORM": {
            "primary": [
                r"\bapplication form\b", r"\bapplicant\b", r"\bdate of birth\b", r"\bdob\b",
                r"\bpermanent address\b", r"\bpersonal details\b", r"\bpassport size\b",
                r"\bsignature of applicant\b", r"\bdeclaration\b", r"\bapplication id\b",
                r"\breference no\b", r"\bgender\b"
            ],
            "weights": 2.2
        },
        "RECEIPT": {
            "primary": [
                r"\breceipt\b", r"\bcash receipt\b", r"\bpayment receipt\b", r"\btransaction id\b",
                r"\bpos terminal\b", r"\bmerchant\b", r"\bstore\b", r"\bchange due\b",
                r"\bcashier\b", r"\bcard ending\b"
            ],
            "weights": 2.0
        }
    }

    @classmethod
    def classify(cls, full_text: str) -> DocumentClassificationResult:
        text_lower = full_text.lower()
        scores: Dict[str, float] = {doc_type: 0.0 for doc_type in cls.KEYWORD_PATTERNS}
        matched_cues: Dict[str, List[str]] = {doc_type: [] for doc_type in cls.KEYWORD_PATTERNS}

        for doc_type, pattern_info in cls.KEYWORD_PATTERNS.items():
            for pattern in pattern_info["primary"]:
                matches = re.findall(pattern, text_lower)
                if matches:
                    scores[doc_type] += len(matches) * pattern_info["weights"]
                    matched_cues[doc_type].append(pattern.replace(r"\b", ""))

        # Find best match
        best_type = "UNKNOWN"
        best_score = 0.0
        for doc_type, score in scores.items():
            if score > best_score:
                best_score = score
                best_type = doc_type

        # Calculate confidence
        total_score = sum(scores.values())
        if total_score > 0 and best_score >= 2.0:
            confidence = min(0.99, max(0.65, best_score / (total_score + 1.0) + 0.35))
        else:
            best_type = "INVOICE"  # Default fallback for demo/general docs
            confidence = 0.60
            matched_cues[best_type] = ["heuristic default"]

        reasons = [
            f"Detected characteristic tokens: {', '.join(matched_cues[best_type][:4])}",
            f"Categorized as {best_type} with classification confidence {round(confidence * 100, 1)}%"
        ]

        return DocumentClassificationResult(
            document_type=best_type,
            confidence=round(confidence, 3),
            reasons=reasons,
            detected_keywords=matched_cues[best_type]
        )
