import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
from pathlib import Path

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''<w:tcMar {nsdecls("w")}>
        <w:top w:w="{top}" w:type="dxa"/>
        <w:bottom w:w="{bottom}" w:type="dxa"/>
        <w:left w:w="{left}" w:type="dxa"/>
        <w:right w:w="{right}" w:type="dxa"/>
    </w:tcMar>''')
    tcPr.append(tcMar)

def generate_synopsis_docx(output_path: Path):
    doc = docx.Document()

    # Set page margins (1 inch)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Primary colors
    NAVY_HEX = "1E3A8A"
    BLUE_HEX = "2563EB"
    DARK_HEX = "111827"
    GRAY_HEX = "4B5563"
    LIGHT_BG = "F3F4F6"

    COLOR_NAVY = RGBColor(30, 58, 138)
    COLOR_BLUE = RGBColor(37, 99, 235)
    COLOR_DARK = RGBColor(17, 24, 39)
    COLOR_GRAY = RGBColor(75, 85, 99)

    # Header Title Banner
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(4)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = title_p.add_run("MCA FINAL-YEAR MAJOR PROJECT SYNOPSIS\n")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(11)
    r_sub.font.bold = True
    r_sub.font.color.rgb = COLOR_BLUE

    r_title = title_p.add_run("DOCUSURE — Intelligent Document Processing, Information Extraction and Verification Using Generative AI")
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(20)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_NAVY

    # Metadata subtitle
    meta_p = doc.add_paragraph()
    meta_p.paragraph_format.space_after = Pt(18)
    meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_meta = meta_p.add_run("Domain: Generative AI • Document AI • Optical Character Recognition • Explainable AI • Anomaly Detection\nCandidate: Punyashree S | Course: Master of Computer Applications (MCA)")
    r_meta.font.name = "Calibri"
    r_meta.font.size = Pt(10)
    r_meta.font.color.rgb = COLOR_GRAY

    # Helper function for Section Headings
    def add_heading_1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = COLOR_NAVY
        # Add a subtle bottom border or divider line under Heading 1
        pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="4" w:color="{NAVY_HEX}"/></w:pBdr>')
        p._p.get_or_add_pPr().append(pBdr)
        return p

    def add_heading_2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = COLOR_BLUE
        return p

    def add_body(text, bold_prefix=None, space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = "Calibri"
            r_pre.font.size = Pt(10.5)
            r_pre.font.bold = True
            r_pre.font.color.rgb = COLOR_DARK
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(10.5)
        run.font.color.rgb = COLOR_DARK
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = "Calibri"
            r_pre.font.size = Pt(10.5)
            r_pre.font.bold = True
            r_pre.font.color.rgb = COLOR_DARK
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(10.5)
        run.font.color.rgb = COLOR_DARK
        return p

    # --- SECTION 1: TITLE ---
    add_heading_1("1. Project Title")
    add_body("DOCUSURE — Intelligent Document Processing, Information Extraction and Verification Using Generative AI")

    # --- SECTION 2: ABSTRACT ---
    add_heading_1("2. Abstract")
    add_body(
        "In modern organizational workflows, institutions process thousands of complex documents daily, including academic certificates, commercial invoices, application forms, property deeds, legal agreements, receipts, and identity filings. Manually reading, transcribing, and verifying these records is slow, expensive, and prone to severe cognitive error. Traditional Optical Character Recognition (OCR) systems extract unstructured text but lack spatial reasoning and contextual understanding, while direct application of Large Language Models (LLMs) suffers from unpredictable hallucinations and ungrounded data fabrication."
    )
    add_body(
        "DOCUSURE is an end-to-end, intelligent document-processing and verification platform that transforms raw document inputs into structured, verified, and explainable intelligence. Built with Python, PyMuPDF, OpenCV, hybrid OCR, and generative schema validation, DOCUSURE not only extracts key-value fields and tabular line items but also: (1) grounds every extracted value to its physical source evidence with exact page numbers, text snippets, and spatial bounding boxes; (2) verifies extracted information against source evidence under a four-tier classification (SUPPORTED, CONTRADICTED, UNSUPPORTED, UNCERTAIN); (3) quantifies confidence scores using calibrated multi-signal estimation; (4) detects arithmetic, chronological, and schema anomalies accompanied by plain-language explainable warnings; (5) evaluates and restores degraded documents (blur, noise, skew, compression) using adaptive preprocessing; (6) supports interactive human-in-the-loop auditing with an immutable transaction log; and (7) synthesizes a simple, human-readable document summary (4–5 lines) explaining the document's basic purpose and verified facts without making unauthorized legal conclusions. DOCUSURE makes document intelligence reliable, traceable, and explainable."
    )

    # --- SECTION 3: INTRODUCTION ---
    add_heading_1("3. Introduction")
    add_body(
        "Manual document interpretation is a major operational bottleneck across commercial, legal, educational, and governmental sectors. Paperwork such as property deeds, sale agreements, encumbrance certificates, commercial tax invoices, and university records contain high densities of technical, administrative, and legal terminology. Lay users and enterprise staff often find it arduous to locate and comprehend essential recorded facts—such as registered property extents, tax identification numbers, line-item totals, and authorized signatures—amidst lengthy legal prose."
    )
    add_body(
        "DOCUSURE addresses this fundamental problem by automating the end-to-end document lifecycle. It ingests multi-page PDFs and images, preprocesses corrupted scans, extracts structured entities into strictly validated schemas, validates arithmetic and chronological consistency, highlights physical proof directly on the original document layout, and presents a plain-language explanation of the document's basic contents for easy human comprehension."
    )

    # --- SECTION 4: PROBLEM STATEMENT ---
    add_heading_1("4. Problem Statement")
    add_body("Traditional document processing and conventional OCR pipelines suffer from several critical shortcomings:")
    add_bullet("Manual and Time-Consuming Reading: Scrutinizing multi-page records manually slows operational velocity and drives up labor overhead.")
    add_bullet("Unstructured Document Layouts: Diverse fonts, multi-column layouts, nested tables, and irregular forms inhibit standardized data capture.")
    add_bullet("OCR Noise and Degradation: Skewed scanning, defocus blur, poor contrast, and sensor noise corrupt text recognition.")
    add_bullet("AI Hallucinations and Silent Failures: Generative models frequently fabricate missing information (e.g. inventing a tax number when absent) without grounded evidence.")
    add_bullet("Lack of Traceable Evidence: Standard tools provide extracted values without linking them back to the exact page coordinates or supporting source sentence.")
    add_bullet("Undetected Arithmetic & Chronological Inconsistencies: Tools fail to identify mathematical discrepancies in tables (e.g. quantity × unit price ≠ line total) or invalid dates.")
    add_bullet("Comprehension Barriers: Complex legal, official, and financial documents remain difficult for non-technical users to understand quickly without simple plain-language summaries.")

    # --- SECTION 5: OBJECTIVES ---
    add_heading_1("5. Objectives of the Project")
    objectives = [
        "To automatically process uploaded multi-page PDF documents and raster images (PNG, JPG, TIFF).",
        "To extract text tokens and spatial layout coordinates (bounding boxes, lines, words) using OCR.",
        "To automatically identify and classify the type of uploaded document (Invoice, Certificate, Form, Receipt).",
        "To extract critical document information into strongly typed, structured schemas enforced by Pydantic.",
        "To provide field-level evidence attribution showing the exact page, verbatim text, and bounding box coordinates.",
        "To verify extracted information against the source document (SUPPORTED, CONTRADICTED, UNSUPPORTED, UNCERTAIN).",
        "To calculate calibrated confidence levels for every extracted field and evaluate reliability via Expected Calibration Error (ECE).",
        "To identify anomalies, mathematical discrepancies, missing mandatory fields, and date inconsistencies with explainable warnings.",
        "To evaluate and improve the processing of poor-quality degraded documents through adaptive computer-vision preprocessing.",
        "To provide an interactive human-in-the-loop review interface for auditing, editing, and approving extracted data.",
        "To maintain a tamper-evident, immutable audit trail of all processing events, anomaly alerts, and reviewer modifications in SQLite.",
        "To generate a concise (4–5 lines / 1 paragraph) plain-language human-readable explanation of the document's core meaning and recorded facts without legal conclusions."
    ]
    for idx, obj in enumerate(objectives, 1):
        add_bullet(obj, bold_prefix=f"Objective {idx}: ")

    # --- SECTION 6: PROPOSED SYSTEM ---
    add_heading_1("6. Proposed System")
    add_body(
        "DOCUSURE implements a comprehensive, 17-stage modular pipeline that unifies ingestion, computer-vision preprocessing, hybrid OCR, document classification, structured extraction, evidence attribution, extraction verification, confidence calibration, anomaly detection, robustness analysis, plain-language summarization, human-in-the-loop review, and immutable audit logging into one cohesive platform."
    )
    add_body(
        "The core operating philosophy of DOCUSURE is: 'Do not simply extract information. Show why the system believes the extracted information is correct.' Every output is traceable, verifiable, and explainable."
    )

    # --- SECTION 7: KEY FEATURES ---
    add_heading_1("7. Key Features")
    features = [
        ("A. Document Upload & Ingestion: ", "Accepts digital and scanned multi-page PDF files and raster image formats (PNG, JPG, TIFF). Generates high-resolution 150 DPI page previews for visual evidence overlay."),
        ("B. Document Preprocessing: ", "Applies minimum-area-rectangle deskewing, Non-Local Means / Gaussian denoising, and Contrast Limited Adaptive Histogram Equalization (CLAHE) to restore corrupted scans."),
        ("C. Spatial OCR & Token Extraction: ", "Extracts textual tokens while preserving exact geometric properties: character spans, word coordinates, line bounding boxes, and block groupings."),
        ("D. Document Classification: ", "Automatically identifies the document category (Invoice, Certificate, Application Form, Receipt) using keyword density heuristics and structural layout markers."),
        ("E. Structured Information Extraction: ", "Converts unstructured text into strict, typed JSON structures validated against Pydantic models. Hallucinations are actively prevented by returning NOT_FOUND for absent fields."),
        ("F. Table & Line-Item Extraction: ", "Extracts tabular row items (Description, Quantity, Unit Price, Line Total) and validates Quantity × Unit Price against printed line totals."),
        ("G. Field-Level Evidence Attribution: ", "Pinpoints the exact source page number, verbatim supporting text snippet, and spatial bounding box coordinates ([ymin, xmin, ymax, xmax]) for every field."),
        ("H. Extraction Verification: ", "Categorizes extracted fields into SUPPORTED (grounded in document), CONTRADICTED (conflicts with document text), UNSUPPORTED (absent from document), or UNCERTAIN (low confidence)."),
        ("I. Confidence Estimation & Calibration: ", "Computes multi-signal confidence scores (HIGH, MEDIUM, LOW) and evaluates reliability using Expected Calibration Error (ECE) and 10-bin Reliability Diagrams."),
        ("J. Document Anomaly Detection: ", "Identifies arithmetic discrepancies in tables and grand totals, chronological date inversions, and missing mandatory schemas, accompanied by plain-language explainable warnings."),
        ("K. Poor-Quality Document Handling & Robustness: ", "Benchmarks extraction degradation under six real-world corruptions (blur, noise, skew, compression, low resolution, faded contrast) and measures OpenCV restoration recovery."),
        ("L. Human-in-the-Loop Review: ", "Implements a three-tier decision gate (AUTO-ACCEPT, REVIEW REQUIRED, REJECT / INVESTIGATE) allowing operators to inspect evidence, edit fields, and record approval."),
        ("M. Immutable Audit Trail: ", "Maintains a persistent, chronological SQLite transaction log capturing all automated decisions, detected anomalies, reviewer edits, and timestamps."),
        ("N. Simple Human-Readable Document Explanation: ", "Generates a concise 4–5 line summary in plain language answering: 'What is this document basically saying?' Explains core recorded facts without offering unauthorized legal advice or conclusions.")
    ]
    for prefix, desc in features:
        add_body(desc, bold_prefix=prefix, space_after=5)

    # --- SECTION 8: SYSTEM ARCHITECTURE ---
    add_heading_1("8. System Architecture")
    add_body("The architecture of DOCUSURE is structured into four distinct, loosely coupled layers:")
    add_bullet("Presentation Layer (React Dashboard): Built with React 18, Vite, and Tailwind CSS. Provides an interactive Document Viewer with glowing bounding-box overlays, extraction tables, anomaly alerts, calibration charts, and review modals.")
    add_bullet("Application & API Layer (FastAPI): High-performance asynchronous REST API built with FastAPI and Uvicorn, handling file upload streams, pipeline coordination, and reviewer actions.")
    add_bullet("Processing & AI Services Layer: Modular micro-services encompassing Document Ingestion (PyMuPDF), Preprocessor (OpenCV), Hybrid OCR Engine, Classifier, Information Extractor (Pydantic), Evidence Locator, Verification Engine, Confidence Calibrator, and Anomaly Detector.")
    add_bullet("Data Persistence Layer (SQLite Database): Embedded database (docusure.db) maintaining relational tables for documents, processed extraction payloads, and immutable audit logs.")

    # --- SECTION 9: TECHNOLOGY STACK ---
    add_heading_1("9. Technology Stack")
    tech_table_data = [
        ("Technology / Tool", "Component", "Purpose in DOCUSURE"),
        ("Python 3.11+", "Core Language", "Backend logic, computer vision, data manipulation, verification algorithms"),
        ("FastAPI", "Web Framework", "High-performance asynchronous RESTful API endpoints and validation"),
        ("Uvicorn", "ASGI Server", "Production-grade asynchronous web server hosting the FastAPI backend"),
        ("React 18", "Frontend Framework", "Responsive single-page web dashboard for interactive document inspection"),
        ("Vite", "Build Tool", "Rapid bundling, asset compilation, and hot module replacement"),
        ("Tailwind CSS", "Styling Engine", "Modern, responsive dark-mode glassmorphic user interface"),
        ("PyMuPDF (fitz)", "Document Processing", "PDF parsing, high-resolution 150 DPI page rendering, spatial text extraction"),
        ("OpenCV (cv2)", "Computer Vision", "Document deskewing, FastNlMeans denoising, CLAHE contrast enhancement"),
        ("Pillow (PIL)", "Image Processing", "Image formatting, format transcoding, dimension inspection"),
        ("Hybrid OCR / EasyOCR", "OCR Engine", "Optical character recognition on scanned images and raster inputs"),
        ("RapidFuzz", "String AI & Matching", "Fuzzy token alignment, partial ratio matching, character Levenshtein distance"),
        ("Pydantic v2", "Data Validation", "Strict schema definition, data coercion, and JSON validation"),
        ("SQLite", "Database Engine", "Embedded persistence for document metadata, extraction states, and audit trails"),
        ("NumPy", "Mathematical Computing", "Array manipulation, spatial coordinate normalization, calibration binning"),
        ("Recharts", "Data Visualization", "Reliability Diagrams, calibration curves, and degradation recovery bar charts"),
        ("Lucide React", "Iconography", "Modern visual icons for navigation, status badges, and metric cards")
    ]

    t = doc.add_table(rows=len(tech_table_data), cols=3)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(tech_table_data):
        for c_idx, val in enumerate(row):
            cell = t.cell(r_idx, c_idx)
            cell.text = val
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.runs[0]
            r.font.name = "Calibri"
            if r_idx == 0:
                set_cell_background(cell, NAVY_HEX)
                r.font.size = Pt(10)
                r.font.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
            else:
                r.font.size = Pt(9.5)
                if r_idx % 2 == 1:
                    set_cell_background(cell, "F9FAFB")
                else:
                    set_cell_background(cell, "FFFFFF")
                if c_idx == 0:
                    r.font.bold = True
                    r.font.color.rgb = COLOR_NAVY
                else:
                    r.font.color.rgb = COLOR_DARK

    # --- SECTION 10: SYSTEM WORKFLOW ---
    add_heading_1("10. System Workflow")
    workflow_steps = [
        "1. User Upload: The operator uploads a multi-page PDF or image document through the web dashboard.",
        "2. Document Ingestion: The backend assigns a unique document ID, creates isolated working folders, and validates file headers.",
        "3. High-Res Rendering: Multi-page PDFs are parsed into individual 150 DPI page PNG previews for visual display.",
        "4. Adaptive Preprocessing: The image undergoes deskewing, noise filtering, and CLAHE contrast enhancement.",
        "5. Spatial OCR Extraction: Words, character spans, line blocks, and spatial bounding boxes are extracted.",
        "6. Document Classification: Keyword density and structural layout markers classify the document type.",
        "7. Schema-Based Extraction: Relevant information fields are extracted according to strongly typed schemas.",
        "8. Table & Line-Item Processing: Tabular rows (Quantity, Unit Price, Line Total) are parsed and mathematically cross-checked.",
        "9. Evidence Attribution: Each extracted field is linked to its exact page number, text span, and bounding box coordinates.",
        "10. Extraction Verification: Field values are verified against source evidence and assigned a verification status.",
        "11. Confidence Estimation: Multi-signal algorithms compute calibrated confidence percentages (HIGH, MEDIUM, LOW).",
        "12. Anomaly Detection: Math checks, date logic, and missing mandatory fields are evaluated, generating explainable warnings.",
        "13. Robustness Benchmark (On-Demand): Evaluates extraction loss under simulated corruptions and restoration recovery.",
        "14. Human-Readable Explanation: The system synthesizes a concise 4–5 line plain-language explanation of the document.",
        "15. Three-Tier Decision Gate: The document is triaged into AUTO-ACCEPT, REVIEW REQUIRED, or REJECT / INVESTIGATE.",
        "16. Human Review & Audit Logging: Quality auditors review evidence, correct values if necessary, and commit audit logs.",
        "17. Interactive Dashboard Presentation: Results, bounding box overlays, anomaly alerts, and audit histories are displayed."
    ]
    for step in workflow_steps:
        add_body(step, space_after=4)

    # --- SECTION 11: EXPECTED OUTPUT ---
    add_heading_1("11. Expected Output")
    add_body("The DOCUSURE system outputs the following comprehensive visual and structured intelligence:")
    add_bullet("Document Classification Header: Displays identified document category, processing latency (ms), and page count.")
    add_bullet("Interactive Document Viewer: Displays original document pages with glowing cyan bounding-box highlights on selected field evidence.")
    add_bullet("Structured Extraction Table: Tabulates field names, extracted values, confidence progress bars, and verification badges.")
    add_bullet("Line-Item Arithmetic Matrix: Details tabular items with calculated vs printed totals and math-match indicators.")
    add_bullet("Explainable Anomaly Alerts: Color-coded alert cards detailing mathematical, temporal, or schema discrepancies with remediation advice.")
    add_bullet("Simple Human-Readable Explanation: A dedicated card providing a 4–5 line plain-language summary of what the document contains.")
    add_bullet("Human Review Interface: Modal dialog providing inline editable fields, reviewer identity inputs, and audit justification notes.")
    add_bullet("Immutable Audit Log: Chronological ledger displaying timestamps, actors, pipeline actions, and JSON modification diffs.")

    # --- SECTION 12: ADVANTAGES ---
    add_heading_1("12. Advantages of DOCUSURE")
    advantages = [
        "Substantial Reduction in Manual Effort: Eliminates the tedious task of reading and transcribing documents manually.",
        "Rapid Turnaround & High Scalability: Processes multi-page records in milliseconds rather than minutes.",
        "Complete Traceability & Grounded Evidence: Every extracted field is physically localized on the original document layout.",
        "Active Hallucination Prevention: Prevents AI fabrication by explicitly returning NOT_FOUND for missing fields.",
        "Automated Mathematical Validation: Catches arithmetic errors in line items and tax calculations that human readers often miss.",
        "Transparent Explainability: Every warning clearly explains why an anomaly occurred in plain human language.",
        "Resilience to Corrupted Documents: Integrated computer-vision preprocessing restores skewed, noisy, or faded scans.",
        "Accessibility for Non-Technical Users: 4–5 line plain-language explanations demystify complex official and legal paperwork.",
        "Streamlined Human-in-the-Loop Workflow: Three-tier decision gate ensures human operators only review uncertain or flagged documents.",
        "Enterprise Governance & Auditability: Permanent SQLite transaction trail satisfies enterprise compliance and accountability standards."
    ]
    for adv in advantages:
        add_bullet(adv)

    # --- SECTION 13: APPLICATIONS ---
    add_heading_1("13. Applications")
    applications = [
        "Academic Institutions & Universities: Automated verification and indexing of degrees, marksheets, and admission forms.",
        "Banking, Financial Services & Insurance (BFSI): Accelerated processing of loan documents, KYC forms, and claim submissions.",
        "Corporate Accounts Payable: Automated extraction, line-item verification, tax checking, and 3-way invoice matching.",
        "Government & Public Administration: Processing citizen applications, property records, certificates, and official filings.",
        "Real Estate & Property Documentation: Extracting key recorded facts from sale agreements, deeds, and encumbrance certificates.",
        "Legal Document Assistance: Summarizing contracts, deeds, and official notices while highlighting supporting evidence clauses.",
        "Healthcare & Hospital Records: Indexing medical intake forms, discharge summaries, and diagnostic billing records.",
        "Supply Chain & Logistics: Processing bills of lading, purchase orders, shipping manifests, and customs declaration documents."
    ]
    for app in applications:
        add_bullet(app)

    # --- SECTION 14: FUTURE SCOPE ---
    add_heading_1("14. Future Scope")
    future_items = [
        "Multilingual & Indic Language Support: Extending OCR and extraction models to process Kannada, Hindi, Tamil, and other regional languages.",
        "Handwritten Text Recognition (HTR): Incorporating specialized recognition models for handwritten forms and medical prescriptions.",
        "Complex Multi-Table & Graph Extraction: Adding deep layout analysis for nested tables, financial balance sheets, and charts.",
        "Digital Signature & Stamp Verification: Validating cryptographic digital signatures and computer-vision seal authentication.",
        "Cross-Document Consistency Checking: Cross-referencing purchase orders, delivery challans, and invoices in multi-document transactions.",
        "Cloud-Native Enterprise Deployment: Containerizing via Docker/Kubernetes with PostgreSQL clustering and Celery distributed task queues.",
        "Mobile Document Capture SDK: Real-time edge document boundary detection, perspective auto-crop, and glare suppression on smartphones.",
        "Active Continual Learning: Leveraging auditor corrections from the audit trail to continually refine extraction heuristics."
    ]
    for f in future_items:
        add_bullet(f)

    # Signature Footer
    doc.add_paragraph().paragraph_format.space_before = Pt(16)
    sig_p = doc.add_paragraph()
    sig_p.paragraph_format.space_after = Pt(2)
    sig_p.paragraph_format.line_spacing = 1.15
    sig_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_sig = sig_p.add_run("Submitted by:\nPunyashree S\nMaster of Computer Applications (MCA)\nDepartment of Computer Applications\n")
    r_sig.font.name = "Calibri"
    r_sig.font.size = Pt(10)
    r_sig.font.bold = True
    r_sig.font.color.rgb = COLOR_NAVY

    doc.save(str(output_path))
    print(f"Successfully generated Word document: {output_path}")

if __name__ == "__main__":
    out_file = Path(__file__).resolve().parent / "DOCUSURE_PROJECT_SYNOPSIS.docx"
    generate_synopsis_docx(out_file)
