from typing import Dict, Any, List, Optional
from app.models.brsr_schemas import (
    BRSRCanonicalObservation, ESGCategory, ClassificationConfidence
)
from app.services.brsr_rules import CANONICAL_INDICATORS, NGRBC_PRINCIPLES

class BRSRClassifier:
    """
    Deterministic & Explainable ESG Classification Engine:
    - Multi-dimensional classification:
        1. ESG Category (Environmental, Social, Governance)
        2. BRSR Section (Section A, Section B, Section C)
        3. NGRBC Principle Mapping (Principles 1 through 9)
        4. SEBI BRSR Core Mapping (Assurance Attributes)
    - Rule-based confidence assignment
    - Explainable decision traces
    """

    @classmethod
    def classify_observation(cls, obs: BRSRCanonicalObservation) -> BRSRCanonicalObservation:
        code = obs.indicator_code
        ind_def = CANONICAL_INDICATORS.get(code)

        if not ind_def:
            obs.classification_status = ClassificationConfidence.UNCLASSIFIED
            obs.confidence_score = 0.50
            return obs

        # 1. ESG Category
        obs.esg_category = ESGCategory(ind_def["esg_category"])

        # 2. BRSR Section
        obs.section_name = ind_def["section"]

        # 3. NGRBC Principle Mapping
        obs.brsr_principle = ind_def.get("principle")

        # 4. BRSR Core Attribute
        obs.brsr_core_indicator = ind_def.get("brsr_core")

        # 5. Classification Confidence
        if obs.reported_value not in ["NOT_FOUND", "EXTRACTION_FAILED"]:
            obs.classification_status = ClassificationConfidence.HIGH
            obs.confidence_score = 0.95
        else:
            obs.classification_status = ClassificationConfidence.MEDIUM
            obs.confidence_score = 0.60

        return obs

    @classmethod
    def classify_all(cls, observations: List[BRSRCanonicalObservation]) -> List[BRSRCanonicalObservation]:
        return [cls.classify_observation(obs) for obs in observations]

    @classmethod
    def get_principle_summary(cls, observations: List[BRSRCanonicalObservation]) -> Dict[str, Any]:
        """Summarizes disclosures by NGRBC Principle."""
        summary = {f"P{i}": {"count": 0, "indicators": []} for i in range(1, 10)}
        for obs in observations:
            p_val = obs.brsr_principle or ""
            for i in range(1, 10):
                if f"Principle {i}" in p_val:
                    summary[f"P{i}"]["count"] += 1
                    summary[f"P{i}"]["indicators"].append({
                        "name": obs.indicator_name,
                        "value": obs.reported_value,
                        "unit": obs.unit,
                        "status": obs.extraction_status.value
                    })
        return summary
