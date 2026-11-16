from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ESGCategory(str, Enum):
    ENVIRONMENTAL = "Environmental"
    SOCIAL = "Social"
    GOVERNANCE = "Governance"
    GENERAL = "General"

class BRSRSectionEnum(str, Enum):
    SECTION_A = "Section A — General Disclosures"
    SECTION_B = "Section B — Management and Process Disclosures"
    SECTION_C = "Section C — Principle-wise Performance"
    UNSPECIFIED = "Unspecified / Not Identified"

class ExtractionStatus(str, Enum):
    EXTRACTED = "EXTRACTED"
    REPORTED_ZERO = "REPORTED_ZERO"
    NOT_DISCLOSED = "NOT_DISCLOSED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NOT_FOUND = "NOT_FOUND"
    EXTRACTION_FAILED = "EXTRACTION_FAILED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"

class ClassificationConfidence(str, Enum):
    HIGH = "High-confidence rule match"
    MEDIUM = "Possible match requiring review"
    UNCLASSIFIED = "Unclassified"

class DocumentType(str, Enum):
    BRSR_STANDALONE = "BRSR Report"
    ANNUAL_REPORT_WITH_BRSR = "Annual Report containing BRSR Section"
    ESG_SUSTAINABILITY_REPORT = "ESG or Sustainability Report"
    UNRELATED_DOCUMENT = "Unrelated Corporate Document"
    UNDETERMINED = "Undetermined / Unsupported"

class BRSRReportMetadata(BaseModel):
    report_id: str
    company_name: str
    industry: Optional[str] = "Diversified"
    financial_year: str
    report_title: str
    report_category: str = "BRSR Report"
    source_url: Optional[str] = None
    local_file_path: str
    file_hash_sha256: str
    file_size_bytes: int = 0
    page_count: int = 0
    upload_status: str = "COMPLETED"
    processing_status: str = "PENDING"  # PENDING, PROCESSING, COMPLETED, ERROR
    error_message: Optional[str] = None
    document_type: str = DocumentType.BRSR_STANDALONE.value
    created_at: Optional[str] = None

class BRSRSectionDetail(BaseModel):
    section_code: str  # SECTION_A, SECTION_B, SECTION_C, P1..P9
    section_name: str
    start_page: int
    end_page: int
    page_count: int
    detected_title: str
    detection_method: str = "HEURISTIC_HEADING_MATCH"
    confidence: float = 0.95

class BRSRTableData(BaseModel):
    table_id: str
    page_number: int
    section_code: Optional[str] = None
    title_or_context: str
    column_headers: List[str]
    row_count: int
    rows: List[List[str]]

class BRSRCanonicalObservation(BaseModel):
    observation_id: str
    company_name: str
    industry: Optional[str] = None
    financial_year: str
    report_id: str
    report_type: str = "BRSR Report"
    section_name: str = ""
    esg_category: ESGCategory
    indicator_code: str
    indicator_name: str
    reported_value: str
    numeric_value: Optional[float] = None
    unit: Optional[str] = None
    normalized_value: Optional[float] = None
    normalized_unit: Optional[str] = None
    reporting_period: Optional[str] = None
    reporting_boundary: Optional[str] = "Standalone"
    brsr_principle: Optional[str] = None
    brsr_core_indicator: Optional[str] = None
    source_page: int = 1
    source_text: str = ""
    extraction_method: str = "TABLE_PARSING"  # TABLE_PARSING, REGEX_PATTERN, KEYWORD_HEURISTIC
    classification_status: ClassificationConfidence = ClassificationConfidence.HIGH
    extraction_status: ExtractionStatus = ExtractionStatus.EXTRACTED
    confidence_score: float = 0.90
    review_status: str = "AUTO_VERIFIED"  # AUTO_VERIFIED, REQUIRES_REVIEW, MANUALLY_EDITED
    manual_correction_notes: Optional[str] = None

class BRSRReportProcessingResult(BaseModel):
    report_id: str
    company_name: str
    financial_year: str
    document_type: str
    total_pages: int
    sections: List[BRSRSectionDetail]
    tables_count: int
    total_indicators_extracted: int
    observations: List[BRSRCanonicalObservation]
    processing_time_ms: float
    summary_message: str

class BRSRManualReviewRequest(BaseModel):
    observation_id: str
    corrected_value: Optional[str] = None
    corrected_numeric_value: Optional[float] = None
    corrected_unit: Optional[str] = None
    corrected_esg_category: Optional[str] = None
    corrected_principle: Optional[str] = None
    reviewer_notes: str
    reviewer_name: str = "Quality Reviewer"
