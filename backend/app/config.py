import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
REPORTS_DIR = PROJECT_ROOT / "data" / "reports"
UPLOAD_DIR = BASE_DIR / "uploads"
STATIC_DIR = BASE_DIR / "static"
DB_PATH = BASE_DIR / "docusure.db"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Thresholds
HIGH_CONFIDENCE_THRESHOLD = 0.90
MEDIUM_CONFIDENCE_THRESHOLD = 0.70
FUZZY_MATCH_THRESHOLD = 80  # out of 100 for RapidFuzz

# Document Types Supported
SUPPORTED_DOC_TYPES = [
    "INVOICE",
    "CERTIFICATE",
    "APPLICATION_FORM",
    "RECEIPT"
]

# Field Schemas per Document Type
DOCUMENT_SCHEMAS = {
    "INVOICE": [
        {"name": "vendor_name", "display": "Vendor Name", "required": True},
        {"name": "invoice_number", "display": "Invoice Number", "required": True},
        {"name": "invoice_date", "display": "Invoice Date", "required": True},
        {"name": "due_date", "display": "Due Date", "required": False},
        {"name": "customer_name", "display": "Customer Name", "required": False},
        {"name": "gst_number", "display": "GST / Tax ID", "required": False},
        {"name": "subtotal_amount", "display": "Subtotal Amount", "required": False},
        {"name": "tax_amount", "display": "Tax Amount", "required": False},
        {"name": "total_amount", "display": "Total Amount", "required": True},
        {"name": "payment_terms", "display": "Payment Terms", "required": False}
    ],
    "CERTIFICATE": [
        {"name": "recipient_name", "display": "Student / Recipient Name", "required": True},
        {"name": "institution_name", "display": "Institution / University", "required": True},
        {"name": "course_name", "display": "Course / Degree Title", "required": True},
        {"name": "certificate_number", "display": "Certificate ID / Roll No", "required": True},
        {"name": "issue_date", "display": "Date of Issuance", "required": True},
        {"name": "grade_or_score", "display": "Grade / Division / Marks", "required": False},
        {"name": "issuing_authority", "display": "Issuing Authority / Signatory", "required": True}
    ],
    "APPLICATION_FORM": [
        {"name": "applicant_name", "display": "Applicant Full Name", "required": True},
        {"name": "application_id", "display": "Application / Reference No", "required": True},
        {"name": "date_of_birth", "display": "Date of Birth", "required": True},
        {"name": "email_address", "display": "Email Address", "required": True},
        {"name": "phone_number", "display": "Phone / Mobile", "required": True},
        {"name": "applied_position", "display": "Applied Program / Position", "required": True},
        {"name": "submission_date", "display": "Submission Date", "required": True},
        {"name": "verification_status_source", "display": "Eligibility / Source Status", "required": False}
    ],
    "RECEIPT": [
        {"name": "store_name", "display": "Store / Merchant Name", "required": True},
        {"name": "receipt_number", "display": "Receipt # / Transaction ID", "required": True},
        {"name": "transaction_date", "display": "Transaction Date", "required": True},
        {"name": "payment_method", "display": "Payment Method", "required": False},
        {"name": "tax_amount", "display": "Tax / VAT Amount", "required": False},
        {"name": "total_amount", "display": "Total Paid", "required": True}
    ]
}
