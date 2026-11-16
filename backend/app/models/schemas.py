from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class VerificationStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    UNSUPPORTED = "UNSUPPORTED"
    UNCERTAIN = "UNCERTAIN"

class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"       # >= 90%
    MEDIUM = "MEDIUM"   # 70% - 89%
    LOW = "LOW"         # < 70%

class OverallDecision(str, Enum):
    AUTO_ACCEPT = "AUTO-ACCEPT"
    REVIEW_REQUIRED = "REVIEW REQUIRED"
    REJECT_INVESTIGATE = "REJECT / INVESTIGATE"

class EvidenceAttribution(BaseModel):
    page: int = 1
    source_text: str = ""
    # Normalized bbox: [ymin, xmin, ymax, xmax] from 0.0 to 1.0
    bbox: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])
    # Pixel bbox: [x0, y0, x1, y1]
    pixel_bbox: List[int] = Field(default_factory=lambda: [0, 0, 0, 0])
    matched_score: float = 1.0
    detection_method: str = "EXACT_ALIGNMENT"

class ExtractedField(BaseModel):
    field_name: str
    display_name: str
    value: str
    normalized_value: Optional[str] = None
    confidence: float
    confidence_level: ConfidenceLevel
    status: VerificationStatus
    evidence: Optional[EvidenceAttribution] = None
    verification_reason: str
    is_edited: bool = False
    original_value: Optional[str] = None
    suggested_correction: Optional[str] = None

class LineItem(BaseModel):
    item_id: int
    description: str
    quantity: float
    unit_price: float
    line_total: float
    computed_total: float
    is_match: bool
    discrepancy: float = 0.0
    evidence: Optional[EvidenceAttribution] = None

class DocumentAnomaly(BaseModel):
    anomaly_id: str
    field_name: Optional[str] = None
    severity: str  # "CRITICAL", "WARNING", "INFO"
    title: str
    reason: str
    extracted_value: Optional[str] = None
    calculated_or_expected: Optional[str] = None
    recommended_action: str

class DocumentClassificationResult(BaseModel):
    document_type: str  # "INVOICE", "CERTIFICATE", "APPLICATION_FORM", "RECEIPT", "UNKNOWN"
    confidence: float
    reasons: List[str]
    detected_keywords: List[str] = Field(default_factory=list)

class DocumentProcessResponse(BaseModel):
    document_id: str
    filename: str
    document_type: str
    page_count: int
    pages_preview_urls: List[str]
    overall_decision: OverallDecision
    average_confidence: float
    total_fields: int
    verified_count: int
    uncertain_count: int
    contradicted_count: int
    unsupported_count: int
    anomaly_count: int
    fields: List[ExtractedField]
    line_items: List[LineItem] = Field(default_factory=list)
    anomalies: List[DocumentAnomaly] = Field(default_factory=list)
    ocr_raw_text: str = ""
    processing_time_ms: float
    upload_timestamp: str

class HumanReviewRequest(BaseModel):
    document_id: str
    decision: str  # "ACCEPTED", "REJECTED", "MODIFIED"
    reviewer_name: str = "Quality Reviewer"
    notes: Optional[str] = ""
    field_corrections: Dict[str, str] = Field(default_factory=dict)

class AuditLogEntry(BaseModel):
    log_id: str
    document_id: str
    timestamp: str
    action: str  # "UPLOAD", "EXTRACTION", "VERIFICATION", "ANOMALY_FLAGGED", "HUMAN_EDIT", "DECISION_FINALIZED"
    actor: str
    details: Dict[str, Any]

class CalibrationBin(BaseModel):
    bin_lower: float
    bin_upper: float
    mean_confidence: float
    observed_accuracy: float
    sample_count: int

class CalibrationReport(BaseModel):
    expected_calibration_error: float
    brier_score: float
    total_samples: int
    bins: List[CalibrationBin]
    accuracy_high_confidence: float
    accuracy_medium_confidence: float
    accuracy_low_confidence: float

class RobustnessMetricSet(BaseModel):
    condition: str
    char_error_rate: float
    word_error_rate: float
    extraction_precision: float
    extraction_recall: float
    extraction_f1: float
    verification_accuracy: float
    average_confidence: float

class RobustnessComparisonResponse(BaseModel):
    document_id: str
    clean_metrics: RobustnessMetricSet
    degraded_metrics: RobustnessMetricSet
    preprocessed_metrics: RobustnessMetricSet
    degradation_type: str
    recovery_percentage: float
