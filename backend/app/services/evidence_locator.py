import re
from typing import Dict, Any, List, Optional
from rapidfuzz import fuzz
from app.models.schemas import EvidenceAttribution

class EvidenceLocator:
    """
    VERITAS-inspired Field-Level Evidence Attribution Engine:
    Locates the exact source region, line, and bounding box coordinates for each extracted field.
    """

    @classmethod
    def locate_evidence(
        cls,
        field_name: str,
        extracted_value: str,
        pages_tokens: List[Dict[str, Any]]
    ) -> Optional[EvidenceAttribution]:
        """
        Scans document pages to find the source text snippet and precise bounding box.
        """
        if not extracted_value or extracted_value == "NOT_FOUND":
            return None

        val_clean = extracted_value.strip()
        val_numeric_only = re.sub(r"[^\d.]", "", val_clean)

        best_match: Optional[EvidenceAttribution] = None
        best_score = 0.0

        for page in pages_tokens:
            page_num = page["page_number"]
            words = page.get("words", [])
            lines = page.get("lines", [])

            # Strategy 1: Check lines for direct or partial match
            for line in lines:
                line_text = line["text"]
                # 1a. Direct substring match
                if val_clean.lower() in line_text.lower():
                    score = 1.0
                    return EvidenceAttribution(
                        page=page_num,
                        source_text=line_text.strip(),
                        bbox=line["bbox"],
                        pixel_bbox=line["pixel_bbox"],
                        matched_score=score,
                        detection_method="EXACT_LINE_SUBSTRING"
                    )

                # 1b. Numeric equivalence match (e.g. ₹45,800 matches 45,800 or 45800)
                if val_numeric_only and len(val_numeric_only) >= 3:
                    line_numeric = re.sub(r"[^\d.]", "", line_text)
                    if val_numeric_only in line_numeric:
                        score = 0.95
                        if score > best_score:
                            best_score = score
                            best_match = EvidenceAttribution(
                                page=page_num,
                                source_text=line_text.strip(),
                                bbox=line["bbox"],
                                pixel_bbox=line["pixel_bbox"],
                                matched_score=score,
                                detection_method="NUMERIC_ALIGNMENT"
                            )

                # 1c. RapidFuzz fuzzy match
                ratio = fuzz.partial_ratio(val_clean.lower(), line_text.lower()) / 100.0
                if ratio > 0.82 and ratio > best_score:
                    best_score = ratio
                    best_match = EvidenceAttribution(
                        page=page_num,
                        source_text=line_text.strip(),
                        bbox=line["bbox"],
                        pixel_bbox=line["pixel_bbox"],
                        matched_score=round(ratio, 3),
                        detection_method="FUZZY_LINE_ALIGNMENT"
                    )

            # Strategy 2: Multi-word sliding window across individual word tokens
            if len(words) > 0 and (best_score < 0.85):
                target_words = val_clean.lower().split()
                w_len = len(target_words)
                if w_len > 0:
                    for i in range(len(words) - w_len + 1):
                        window = words[i : i + w_len]
                        window_text = " ".join([w["text"] for w in window]).lower()
                        score = fuzz.ratio(" ".join(target_words), window_text) / 100.0
                        if score > 0.80 and score > best_score:
                            best_score = score
                            # Union of word bboxes
                            ymin = min([w["bbox"][0] for w in window])
                            xmin = min([w["bbox"][1] for w in window])
                            ymax = max([w["bbox"][2] for w in window])
                            xmax = max([w["bbox"][3] for w in window])

                            px0 = min([w["pixel_bbox"][0] for w in window])
                            py0 = min([w["pixel_bbox"][1] for w in window])
                            px1 = max([w["pixel_bbox"][2] for w in window])
                            py1 = max([w["pixel_bbox"][3] for w in window])

                            best_match = EvidenceAttribution(
                                page=page_num,
                                source_text=" ".join([w["text"] for w in window]),
                                bbox=[round(ymin, 4), round(xmin, 4), round(ymax, 4), round(xmax, 4)],
                                pixel_bbox=[px0, py0, px1, py1],
                                matched_score=round(score, 3),
                                detection_method="WORD_SPAN_UNION"
                            )

        return best_match
