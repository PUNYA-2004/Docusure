# PROJECT SYNOPSIS

## DOCUSURE — Intelligent Document Processing, Information Extraction and Verification Using Generative AI

**Project Type:** Master of Computer Applications (MCA) Final-Year Major Project  
**Domain:** Generative AI + Document AI + Optical Character Recognition (OCR) + Information Extraction + Explainable AI + Anomaly Detection  

---

### 1. TITLE OF THE PROJECT
**DOCUSURE — Intelligent Document Processing, Information Extraction and Verification Using Generative AI**

---

### 2. ABSTRACT

In modern enterprise and administrative operations, organizations routinely handle large volumes of heterogeneous documents, including academic certificates, commercial invoices, application forms, property records, legal/official filings, receipts, and identity documents. Manually reading, understanding, and extracting key data from these documents is labor-intensive, error-prone, and inefficient. While conventional Optical Character Recognition (OCR) systems can convert rasterized text into raw character streams, they lack structural awareness, semantic context, and verification capabilities. Large Language Models (LLMs) and Generative AI can extract structured entities but are susceptible to hallucinations, silent misreadings, and ungrounded outputs without traceability.

**DOCUSURE** is an end-to-end, intelligent document-processing and verification platform that bridges this critical reliability gap. Built upon a unified architecture combining PyMuPDF, OpenCV computer vision, hybrid OCR, and generative schema validation, DOCUSURE automatically extracts structured key-value entities and tabular line items from scanned and digital PDFs or images. Crucially, the platform goes beyond simple extraction by:
1. **Attributing physical evidence** for every extracted field with source page numbers, text snippets, and spatial bounding-box coordinates.
2. **Verifying extracted information** against source document evidence using a rigorous four-tier status classification (`SUPPORTED`, `CONTRADICTED`, `UNSUPPORTED`, `UNCERTAIN`).
3. **Quantifying confidence levels** using calibrated multi-signal estimation, Expected Calibration Error (ECE), and reliability diagram evaluation.
4. **Detecting domain anomalies and inconsistencies**, such as arithmetic mismatches in line items and tax, chronological date inversions, and missing mandatory fields, accompanied by plain-language explainable warnings.
5. **Evaluating and restoring degraded documents** subjected to real-world blur, sensor noise, perspective skew, low resolution, and compression artifacts through an adaptive computer-vision pipeline.
6. **Empowering human reviewers** through a three-tier decision gate (`AUTO-ACCEPT`, `REVIEW REQUIRED`, `REJECT / INVESTIGATE`) with inline correction and a tamper-evident, immutable audit trail.
7. **Generating concise, human-readable document summaries** (4–5 lines) that explain the core essence and recorded facts of the document in plain language without making unauthorized legal conclusions.

DOCUSURE establishes a reliable, traceable, and explainable document intelligence ecosystem designed for production deployment on standard computing hardware.

---

### 3. INTRODUCTION

Organizations across education, banking, legal administration, property registry, insurance, and government sectors are inundated with physical and digital paperwork. These documents—ranging from complex property ownership records, conveyance deeds, and encumbrance certificates to commercial tax invoices, admission forms, and university degree certificates—contain a dense combination of unstructured prose, tabular data, stamps, and signatures.

Manual examination of these records presents significant operational bottlenecks:
- **High Cognitive Load and Specialized Jargon:** Legal, official, and financial documents are often couched in technical, archaic, or statutory terminology. Non-technical users, administrative staff, and consumers frequently struggle to locate and comprehend vital recorded facts such as consideration amounts, survey numbers, due dates, or signatory validity.
- **Latency and Scalability Limits:** Manual verification requires human operators to scrutinize each page line-by-line, creating turnaround delays in loan approvals, admissions, and procurement workflows.
- **Error Vulnerability:** Repetitive manual data entry suffers from transcription oversights, misinterpretation of smudged figures, and failure to notice internal calculation discrepancies.

DOCUSURE resolves these challenges by introducing an evidence-grounded document understanding architecture. Rather than treating document processing as a black-box extraction task, DOCUSURE delivers structured JSON outputs, highlights visual proof directly on the original document layout, cross-validates arithmetic and chronological rules, and generates an accessible plain-language explanation of the document's basic purpose and key recorded facts.

---

### 4. PROBLEM STATEMENT

A dependable document intelligence system must not merely extract text; it must demonstrate *why* the extracted information is believed to be correct, identify inconsistencies, and safeguard against ungrounded AI hallucinations. Traditional document management workflows and basic OCR setups suffer from the following core problems:

1. **Labor-Intensive Manual Processing:** Reading, verifying, and indexing physical or scanned documents manually is time-consuming and expensive.
2. **Unstructured and Variable Layouts:** Documents vary widely in formatting, typography, language orientation, and table structures across different issuing authorities and vendors.
3. **OCR Noise and Smudged Characters:** Degradation from low-resolution mobile photographs, scanning skew, optical blur, and uneven lighting leads to corrupted character recognition.
4. **Generative Hallucinations and Omissions:** When applied directly, generative models can fabricate plausible-sounding values (e.g., inventing missing tax identification numbers or registration IDs) when a field is absent from the source.
5. **Absence of Traceable Evidence:** Standard extractors output key-value pairs without indicating the exact spatial location or supporting sentence in the original document, forcing operators to manually re-read pages to confirm accuracy.
6. **Undetected Internal Inconsistencies:** Documents may contain conflicting figures—such as invoice line items that fail to sum up to the declared total, or due dates that precede issuance dates—which conventional OCR tools cannot detect.
7. **Opacity and Lack of Explainability:** Typical automated tools flag errors cryptically without explaining the mathematical or logical rationale behind warnings.
8. **Comprehension Barrier in Complex Documents:** Non-expert users find it challenging to quickly grasp the legal or administrative import of complex property records or official notices without simple, plain-language summaries.

---

### 5. OBJECTIVES OF THE PROJECT

The primary objectives of the DOCUSURE system are:

1. **Automated Document Ingestion:** To accept and process heterogeneous multi-page PDF documents and raster images (PNG, JPG, TIFF) through a secure ingestion interface.
2. **High-Fidelity Text & Layout Extraction:** To extract text tokens, character sequences, and precise word/line spatial coordinates using optical character recognition.
3. **Document Type Classification:** To automatically categorize incoming documents into categories (e.g., Commercial Invoices, Academic Certificates, Application Forms, Receipts, Property/Official Documents) based on layout and keyword density.
4. **Schema-Grounded Structured Information Extraction:** To map unstructured document text into strongly validated, typed JSON schemas enforced by Pydantic data models.
5. **Field-Level Evidence Attribution:** To pinpoint the exact source page, supporting text span, and spatial bounding box (`[ymin, xmin, ymax, xmax]`) for every extracted field.
6. **Multi-Tier Extraction Verification:** To verify whether extracted entities are grounded in the source document, classifying each as `SUPPORTED`, `CONTRADICTED`, `UNSUPPORTED`, or `UNCERTAIN`.
7. **Confidence Estimation & Uncertainty Quantification:** To compute calibrated field-level confidence scores and evaluate system reliability using Expected Calibration Error (ECE) and Brier scores.
8. **Rule-Based Anomaly & Inconsistency Detection:** To identify arithmetic discrepancies in tables, temporal inversions in dates, missing mandatory fields, and format violations, generating plain-language explainable warnings.
9. **Document Robustness & Restoration Evaluation:** To evaluate document quality under real-world degradation (blur, noise, skew, compression, low resolution) and improve OCR readability through adaptive OpenCV computer-vision preprocessing (deskew, denoise, CLAHE).
10. **Human-in-the-Loop Review System:** To provide an interactive interface allowing quality auditors to inspect evidence, edit/override values, approve, or reject documents.
11. **Immutable Audit Logging:** To maintain a complete, chronological transaction log capturing all automated decisions, detected anomalies, reviewer edits, and timestamps in a persistent database.
12. **Simple Human-Readable Explanation Generation:** To synthesize a concise (4–5 lines / 1 paragraph) plain-language summary explaining the core meaning and recorded facts of the document without offering unauthorized legal conclusions.

---

### 6. PROPOSED SYSTEM

DOCUSURE proposes a modular, multi-stage processing pipeline that unifies optical character recognition, spatial layout understanding, rule-based verification, and generative explanation into a coherent workflow:

```
                      DOCUMENT (PDF / Image)
                                ↓
                      Document Ingestion
                                ↓
                      Image Preprocessing
                 (Deskew / Denoise / Enhance)
                                ↓
                               OCR
                                ↓
                   Text + Spatial Information
                                ↓
                   Document Classification
                                ↓
              Structured Information Extraction
                                ↓
                    Table & Field Parsing
                                ↓
                     Evidence Attribution
                                ↓
                    Extraction Verification
                                ↓
                     Confidence Estimation
                                ↓
                       Anomaly Detection
                                ↓
               Is Document Quality Sufficient?
                         /           \
                       YES            NO
                        ↓              ↓
                        ↓       Restoration /
                        ↓       Preprocessing
                        ↓              ↓
                        └─────────→ Reprocessing
                                       ↓
                              Verified Extraction
                                       ↓
                           Human-Readable Summary
                                (4–5 lines)
                                       ↓
                                  Human Review
                                 /            \
                              Accept        Edit/Review
                                 \            /
                                  └─────┬────┘
                                        ↓
                                   Audit Trail
                                        ↓
                                  Final Result
```

---

### 7. KEY FEATURES OF DOCUSURE

#### A. Document Upload & Ingestion
- Accepts both digital and scanned multi-page PDF documents as well as standard image formats (PNG, JPG, JPEG, TIFF).
- Generates high-resolution rendered PNG page previews at 150 DPI for visual inspection and evidence overlay.

#### B. Document Preprocessing
- **Deskewing:** Computes the document tilt angle using minimum area bounding rectangles and applies affine transformation to rotate skewed scans back to upright orientation.
- **Denoising:** Applies Non-Local Means / Gaussian filtering to remove scanner grain and sensor noise while preserving sharp font edges.
- **Contrast Enhancement:** Utilizes Contrast Limited Adaptive Histogram Equalization (CLAHE) to restore faded text and thermal ink.

#### C. Spatial OCR & Token Extraction
- Extracts textual tokens while preserving exact geometric properties: character spans, word coordinates, line bounding boxes, and block groupings.
- Supports digital PDF stream extraction and rasterized computer-vision OCR.

#### D. Document Type Classification
- Automatically determines document category (e.g., Commercial Invoice, Academic Certificate, Application Form, Receipt, Property/Official Document) using keyword density heuristics and structural layout markers.
- Selects the matching schema definition for subsequent extraction stages.

#### E. Structured Information Extraction
- Converts unstructured and semi-structured text into strict, typed JSON structures validated against Pydantic schemas.
- **Hallucination Prevention:** If a required field is not present in the document, the system explicitly returns `NOT_FOUND` rather than allowing the AI to invent values.

#### F. Table and Line-Item Extraction
- Identifies tabular line items in invoices and financial documents (Item Description, Quantity, Unit Price, Line Total).
- Automatically calculates `Quantity × Unit Price` and compares the computed product against the printed line total to detect discrepancies.

#### G. Evidence Attribution
- Links every single extracted field to its exact source in the original document.
- Provides the source page number, verbatim supporting sentence snippet, and normalized bounding box coordinates (`[ymin, xmin, ymax, xmax]`), enabling interactive visual highlighting on the user interface.

#### H. Extraction Verification
- Validates extracted values against the grounded source text using strict fuzzy, substring, and numeric equivalence algorithms.
- Classifies each field into one of four standardized verification states:
  - **`SUPPORTED`:** Value is directly backed by ground-truth evidence in the source document.
  - **`CONTRADICTED`:** Extracted value conflicts with printed figures or neighboring text in the document.
  - **`UNSUPPORTED`:** Value cannot be located anywhere in the document (hallucination averted).
  - **`UNCERTAIN`:** Partial alignment or low token recognition confidence; visual inspection required.

#### I. Confidence Estimation & Calibration
- Computes a multi-signal confidence metric combining OCR quality, evidence alignment, and verification status.
- Classifies confidence into `HIGH` (&ge; 90%), `MEDIUM` (70%–89%), and `LOW` (&lt; 70%).
- Implements formal uncertainty calibration routines: calculates Expected Calibration Error (ECE), Brier score, and generates 10-bin Reliability Diagrams.

#### J. Document Anomaly Detection
- Analyzes documents for logical, arithmetic, and format inconsistencies:
  - **Math Inconsistencies:** Checks if item totals sum up to the invoice subtotal, and if subtotal plus tax equals the grand total.
  - **Chronological Date Inversions:** Verifies whether due dates logically follow issuance dates.
  - **Missing Mandatory Schemas:** Flags missing compulsory fields required for legal or business validity.
- Provides explainable warnings explaining *why* an anomaly was flagged (e.g., *"Invoice total INR 58,500 differs from calculated sum of line items INR 45,800 by INR 12,700"*).

#### K. Poor-Quality Document Handling & Robustness
- Evaluates document extraction under six real-world degradation types: defocus blur, Gaussian sensor noise, camera skew (8.5°), severe JPEG compression, downsampled low resolution, and faded contrast.
- Benchmarks Character Error Rate (CER), Word Error Rate (WER), and extraction F1 score across Clean, Degraded, and Preprocessed stages to quantify performance recovery.

#### L. Human-in-the-Loop Review
- Implements a three-tier operational decision gate:
  - `AUTO-ACCEPT`: High confidence and fully verified evidence.
  - `REVIEW REQUIRED`: Medium confidence or minor warnings.
  - `REJECT / INVESTIGATE`: Contradicted values or critical arithmetic discrepancies.
- Provides an intuitive modal for quality auditors to edit values, override statuses, enter audit notes, and commit approvals.

#### M. Immutable Audit Trail
- Maintains a persistent, tamper-evident transaction log in SQLite tracking every action (`UPLOAD`, `CLASSIFICATION`, `PIPELINE_COMPLETE`, `ANOMALY_FLAGGED`, `ROBUSTNESS_TEST`, `HUMAN_REVIEW`).
- Records timestamps, acting user/system identities, and detailed JSON modification diffs.

#### N. Simple Human-Readable Document Explanation
- Generates a concise summary (approximately 4–5 lines / 1 paragraph) in plain, accessible language answering: *"What is this document basically saying?"*
- Designed specifically for non-technical users examining complex property records, legal agreements, official notices, or academic records.
- **Ethical & Safety Guardrails:** Does not provide legal advice, does not draw legal conclusions, does not assert legal validity, does not fabricate unmentioned facts, and explicitly states when information is missing or uncertain.

---

### 8. SYSTEM ARCHITECTURE

DOCUSURE employs a clean, decoupled, client-server architecture:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION TIER (UI)                          │
│                                                                        │
│   React 18 Dashboard  •  Tailwind CSS Glassmorphism  •  Lucide Icons   │
│   Interactive Document Viewer (Canvas BBox Highlighting)  •  Recharts   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / REST API (JSON & Multipart)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         APPLICATION TIER (API)                         │
│                                                                        │
│               FastAPI (Uvicorn Asynchronous Web Server)                │
│    • /api/documents/process         • /api/documents/{id}/review       │
│    • /api/documents/{id}/preview    • /api/documents/{id}/robustness   │
│    • /api/calibration/report        • /api/audit/logs                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Internal Pipeline Services
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        PROCESSING & AI SERVICES                        │
│                                                                        │
│  ┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────┐ │
│  │ Document Ingestion    │ │ OpenCV Preprocessor   │ │ Hybrid OCR    │ │
│  │ (PyMuPDF & PIL)       │ │ (Deskew, Denoise)     │ │ Engine        │ │
│  └───────────────────────┘ └───────────────────────┘ └───────────────┘ │
│  ┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────┐ │
│  │ Document Classifier   │ │ Structured Extractor  │ │ Evidence      │ │
│  │ (Heuristics & Cues)   │ │ (Pydantic Schemas)    │ │ Locator       │ │
│  └───────────────────────┘ └───────────────────────┘ └───────────────┘ │
│  ┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────┐ │
│  │ Verification Engine   │ │ Anomaly & Consistency │ │ Robustness    │ │
│  │ (Status Classifier)   │ │ Checker (XAI)         │ │ Benchmark     │ │
│  └───────────────────────┘ └───────────────────────┘ └───────────────┘ │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ SQL Queries & Audit Logging
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                          DATA PERSISTENCE TIER                         │
│                                                                        │
│       SQLite Embedded Relational Database (docusure.db)                │
│   • documents Table                 • audit_logs Table                 │
│   • robustness_experiments Table    • Encrypted File Storage           │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 9. TECHNOLOGY STACK

| Layer / Component | Technology | Version | Purpose in DOCUSURE |
|---|---|---|---|
| **Programming Language** | Python | 3.11+ | Core backend logic, computer vision, data manipulation |
| **Web API Framework** | FastAPI | 0.136+ | Asynchronous RESTful API endpoints, request validation |
| **API Server Engine** | Uvicorn | 0.49+ | High-performance ASGI production web server |
| **Frontend Framework** | React | 18.x | Dynamic, responsive single-page web dashboard |
| **Frontend Build Tool** | Vite | 8.x | Fast build, bundling, and hot module replacement |
| **Styling & Design System**| Tailwind CSS | 4.x | Modern dark-mode glassmorphic user interface |
| **Document Processing** | PyMuPDF (fitz) | 1.28+ | PDF parsing, spatial token extraction, page rendering |
| **Image Preprocessing** | OpenCV (cv2) | 4.13+ | Deskewing, Gaussian/bilateral denoising, CLAHE enhancement |
| **Imaging Library** | Pillow (PIL) | 12.x | Image manipulation, format conversion, thumbnail generation |
| **OCR Engines** | Hybrid OCR / EasyOCR | 1.7+ | Optical character recognition on raster scans and image inputs |
| **Fuzzy Matching & String AI**| RapidFuzz | 3.14+ | Levenshtein distance, partial string alignment, token matching |
| **Data Validation** | Pydantic | 2.13+ | Strongly-typed schema enforcement, JSON data validation |
| **Embedded Database** | SQLite | 3.x | Persistent storage for processed documents and audit trails |
| **Mathematical Computing**| NumPy | 2.x | Coordinate transformations, array math, calibration bins |
| **Data Visualization** | Recharts | 2.x | Reliability diagrams, calibration curves, degradation charts |
| **Icons & Visual Language**| Lucide React | Latest | Clean iconography for status badges, metrics, and navigation |

---

### 10. SYSTEM WORKFLOW

The complete end-to-end execution workflow of DOCUSURE proceeds through 17 systematic steps:

1. **Document Upload:** The user selects or drags and drops a document (PDF or image) onto the web interface.
2. **File Ingestion:** The backend receives the file stream, assigns a unique document identifier (`doc_id`), and creates a dedicated secure working directory.
3. **Page Rendering:** Multi-page PDFs are parsed into individual high-resolution PNG page images (150 DPI) for visual rendering and evidence overlay.
4. **Adaptive Preprocessing:** The document image undergoes skew angle detection, affine rotation, denoising, and CLAHE contrast equalization.
5. **Spatial OCR:** Optical Character Recognition processes each page to extract textual words, line blocks, character spans, and spatial bounding boxes.
6. **Document Classification:** Keyword density, structural headers, and spatial cues categorize the file (e.g., Invoice, Certificate, Application Form).
7. **Schema-Based Information Extraction:** The system maps the text into predefined target fields specified in typed Pydantic models.
8. **Table & Line-Item Parsing:** If tabular structures exist, row-level items (Quantity, Unit Price, Line Total) are extracted and mathematically evaluated.
9. **Field Evidence Attribution:** The evidence locator searches spatial tokens to link each field value to its exact page number, text snippet, and bounding box coordinates.
10. **Extraction Verification:** The verification engine checks extracted values against ground-truth evidence text, assigning `SUPPORTED`, `CONTRADICTED`, `UNSUPPORTED`, or `UNCERTAIN`.
11. **Confidence Calculation:** Multi-signal confidence scoring computes calibrated probabilities for each field, categorizing them as `HIGH`, `MEDIUM`, or `LOW`.
12. **Anomaly & Consistency Detection:** Deterministic rules check for arithmetic discrepancies, missing mandatory schemas, date inversions, and contradiction alerts.
13. **Robustness Evaluation (Optional/On-Demand):** Evaluates extraction degradation under simulated corruptions and measures restoration recovery via preprocessing.
14. **Simple Human-Readable Explanation Generation:** Synthesizes a concise (4–5 lines / 1 paragraph) plain-language summary describing the document's basic purpose and verified facts without legal advice.
15. **Three-Tier Decision Gate:** The system assigns an overall document recommendation: `AUTO-ACCEPT`, `REVIEW REQUIRED`, or `REJECT / INVESTIGATE`.
16. **Human-in-the-Loop Review & Audit Logging:** If review is required, an operator inspects the visual evidence, modifies fields if necessary, and commits the decision to the immutable SQLite audit trail.
17. **Dashboard Presentation:** The React frontend renders the document preview, evidence bounding boxes, extraction table, anomaly warnings, summary, and audit history.

---

### 11. EXPECTED OUTPUT AND USER INTERFACE

The DOCUSURE React application delivers a unified, production-grade interface organized into specialized views:

1. **Executive Dashboard View:**
   - Summary metric cards: Total Processed Documents, Auto-Accepted Count, Review Required Count, Flagged Anomalies Count, and Average Confidence.
   - 1-Click benchmark evaluation documents for instant testing.
   - Recent documents table with status badges and quick inspection triggers.
2. **Ingest & Extract View:**
   - Drag-and-drop file upload zone supporting PDF, PNG, JPG, JPEG, and TIFF.
   - Optional document type schema pre-selection.
   - Step-by-step animated pipeline progress monitor.
3. **Document Inspector View (Interactive Split View):**
   - **Left Panel (Interactive Document Viewer):** Displays the rendered document page with zoom controls (out, in, 1:1), page navigation, and a glowing cyan bounding-box overlay highlighting the exact physical evidence for whichever field is currently selected.
   - **Right Panel (Extraction Table & Warnings):** Displays all extracted fields, their values, confidence percentage bars, verification status badges, and source text snippets. Includes the invoice line items table with green checkmarks or red arithmetic discrepancy indicators.
   - **Explainable Anomaly Alerts:** Color-coded severity banners (Critical, Warning, Info) detailing the exact mathematical or chronological reason for each warning, showing extracted versus expected values.
   - **Human-Readable Document Summary:** A distinct card presenting the 4–5 line plain-language explanation of the document's core meaning and verified recorded facts.
4. **Human Review Modal:**
   - Inline editable text boxes for overriding field values.
   - Reviewer identity and justification note inputs.
   - Decision buttons (`ACCEPT`, `CORRECT & SAVE`, `REJECT`).
5. **Confidence Calibration & Research View:**
   - 10-bin Reliability Diagram (empirical accuracy versus predicted confidence).
   - Expected Calibration Error (ECE) and Brier score metrics.
   - Multi-model comparative ablation study table.
6. **Robustness Lab View:**
   - Interactive degradation simulator (Blur, Noise, Skew, JPEG Compression, Downsampling, Contrast Fading).
   - Three-stage side-by-side metric comparison table (Clean Original vs Corrupted Input vs Restored Document).
   - Bar chart illustrating performance recovery percentage.
7. **Immutable Audit Trail View:**
   - Chronological timeline ledger recording every document event, system action, detected anomaly, and human reviewer intervention.

---

### 12. ADVANTAGES OF THE SYSTEM

1. **Substantial Reduction in Manual Effort:** Automates the labor-intensive task of reading, cross-referencing, and transcribing multi-page paperwork.
2. **Rapid Turnaround & High Scalability:** Reduces document intake and extraction time from minutes to milliseconds per page.
3. **Traceability & Proof of Evidence:** Every extracted entity is visually grounded on the original document layout, eliminating blind trust in AI outputs.
4. **Active Hallucination Prevention:** Missing fields are explicitly marked as `NOT_FOUND` rather than allowing generative models to invent plausible false data.
5. **Automated Mathematical & Chronological Validation:** Detects internal arithmetic mismatches and inverted date logic that human readers often miss.
6. **Transparent, Explainable Warnings:** Alerts explain the exact reason for discrepancies in plain, human-understandable terms.
7. **Resilience to Poor-Quality Scans:** Integrated computer-vision preprocessing restores skewed, noisy, or faded documents prior to recognition.
8. **Accessibility for Non-Technical Users:** Generates short, simple plain-language explanations that demystify complex official, legal, and academic paperwork.
9. **Controlled Human Supervision:** A three-tier decision gate ensures human operators only review uncertain or flagged documents, maximizing operational efficiency.
10. **Enterprise Compliance & Auditability:** An immutable SQLite transaction trail logs all modifications, satisfying governance and compliance mandates.

---

### 13. APPLICATIONS OF DOCUSURE

- **Academic Institutions & Universities:** Automated verification and archiving of degree certificates, provisional marksheets, and student admission forms.
- **Banking, Financial Services & Insurance (BFSI):** Rapid ingestion of loan application paperwork, identity proofs, financial statements, and insurance claim forms.
- **Corporate Accounting & Accounts Payable:** Automated extraction, line-item arithmetic verification, tax computation, and three-way matching for commercial invoices and vendor receipts.
- **Government & Civic Administration:** Processing citizen application forms, utility documents, tax filings, and public service requests.
- **Property & Real Estate Registry:** Extracting key recorded information from property deeds, sale agreements, encumbrance certificates, and mutation records, providing plain-language summaries for property buyers.
- **Legal Document Assistance:** Assisting legal departments and paralegals in summarizing lengthy contracts, notices, and official agreements while highlighting referenced clauses.
- **Healthcare & Hospital Records:** Indexing patient intake forms, medical discharge summaries, and diagnostic billing records.
- **Supply Chain & Logistics:** Processing bills of lading, purchase orders, shipping manifests, and customs declaration forms.

---

### 14. FUTURE SCOPE

While DOCUSURE delivers a fully functional, verified document intelligence platform, potential future extensions include:

1. **Multilingual & Indic Language Support:** Expanding OCR and extraction models to process documents written in Kannada, Hindi, Tamil, Telugu, and other Indian regional languages.
2. **Handwritten Text Recognition (HTR):** Integrating specialized handwriting recognition models to process handwritten notes, doctor prescriptions, and physical application forms.
3. **Complex Multi-Table & Graph Understanding:** Developing deep layout-analysis algorithms for multi-page nested tables, financial balance sheets, and bar/pie chart data extraction.
4. **Digital Signature & Seal Verification:** Incorporating cryptographic public-key infrastructure checks and computer-vision stamp verification to detect counterfeit seals and signatures.
5. **Cross-Document Consistency Checking:** Expanding verification logic to cross-reference multiple related documents simultaneously (e.g., matching a purchase order against a delivery challan and invoice).
6. **Cloud-Native Enterprise Deployment:** Containerizing the platform using Docker and Kubernetes for scalable cloud deployment with PostgreSQL database clusters and distributed task queues (Celery/Redis).
7. **Mobile Document Capture SDK:** Developing a lightweight smartphone edge-SDK with real-time border detection, auto-cropping, and glare reduction.
8. **Continual Active Learning:** Leveraging auditor corrections from the audit trail to continually refine extraction heuristics and fine-tune lightweight local models.

---

### 15. SPECIALIZED EXTENSION: BRSR REPORT PROCESSING, ESG INFORMATION EXTRACTION AND CLASSIFICATION (FINITELOOP COLLABORATION)

#### 15.1 Context & Regulatory Framework
In collaboration with **Finiteloop** and adhering to statutory directives issued by the **Securities and Exchange Board of India (SEBI)** (Circular *SEBI/HO/CFD/CFD-SEC-2/P/CIR/2023/122*), DOCUSURE has been extended to process, extract, map, and classify **Business Responsibility and Sustainability Reporting (BRSR)** disclosures from top listed Indian corporate entities.

The BRSR framework establishes a structured, quantifiable reporting format based on the nine **National Guidelines on Responsible Business Conduct (NGRBC)** principles, encompassing:
- **Section A:** General Disclosures (Corporate identity, operational boundary, employee counts, CSR overview).
- **Section B:** Management & Process Disclosures (Sustainability policies, governance oversight, stakeholder engagement).
- **Section C:** Principle-wise Performance Disclosures (Essential and Leadership indicators across Principles 1 to 9).
- **SEBI BRSR Core:** A subset of nine high-priority ESG attributes subject to mandatory reasonable assurance.

#### 15.2 Strict Non-LLM Architectural Mandate
In strict compliance with partner directives and enterprise auditability standards, the BRSR intelligence extension operates with **ZERO LLMs or Generative AI APIs**. This eliminates hallucination risk, vendor lock-in, data privacy violations, and API latency, delivering:
1. **100% Deterministic Reproducibility:** Every extracted metric derives from exact PyMuPDF table row cell extraction, coordinate geometry, regex parsing, and RapidFuzz label matching.
2. **Transparent Mathematical Normalization:** Transparent unit conversions (e.g., MWh to GJ, KL to Litres, INR scale adjustments) documented in an open-source rule schema (`brsr_rules.py` / `brsr_rules.json`).
3. **Auditable Evidence Grounding:** Every observation maintains physical PDF page citations and verbatim source text snippets.
4. **Explicit Disclosure State Distinction:** Ensures zero values are never confused with undisclosed or missing data by explicitly distinguishing `EXTRACTED`, `REPORTED_ZERO`, `NOT_DISCLOSED`, `NOT_APPLICABLE`, and `NOT_FOUND`.

#### 15.3 Target Dataset of Official Reports (FY 2023-24)
The system is validated on official SEBI filings from 5 prominent Indian listed entities:
1. **Titan Company Limited** (BSE Scrip: 500114 | CIN: L74999TZ1984PLC001456 | 53 Pages)
2. **Colgate-Palmolive (India) Limited** (BSE Scrip: 500830 | CIN: L24200MH1937PLC002700 | 43 Pages)
3. **Aditya Birla Fashion and Retail Limited** (BSE Scrip: 535755 | CIN: L18101MH2007PLC233901 | 17 Pages)
4. **Manali Petrochemicals Limited** (BSE Scrip: 500268 | CIN: L24294TN1986PLC013087 | 50 Pages)
5. **Kolte-Patil Developers Limited** (BSE Scrip: 532924 | CIN: L45200PN1991PLC129428 | 33 Pages)

#### 15.4 Multi-Dimensional Classification Taxonomy
Extracted disclosures are classified across four orthogonal dimensions:
1. **ESG Pillar:** Environmental ($E$), Social ($S$), or Governance ($G$).
2. **BRSR Section:** Section A, Section B, or Section C.
3. **NGRBC Principle:** Principle 1 (Integrity) through Principle 9 (Consumer Value).
4. **SEBI BRSR Core Attribute:** Designating metrics requiring mandatory third-party assurance.

#### 15.5 Integration & Deliverables
The module exposes dedicated RESTful endpoints (`/api/brsr/...`) and an interactive React interface (`BRSR & ESG Intelligence`) offering five specialized views:
- **Report Repository:** PDF status, metadata, and checksum verification.
- **Parser Results:** Section boundaries, principle page ranges, and table layouts.
- **ESG Extraction:** Extracted metric values with physical page citations and verbatim evidence snippets.
- **Mapping & Classification:** Interactive matrix of canonical disclosures grouped by ESG pillar and NGRBC principle.
- **Review & Data Quality:** Auditor verification interface with manual override capability and export to canonical CSV and JSON formats.

*Note: Cross-company ESG benchmarking and comparative analytics (Week 4) are intentionally decoupled to preserve modularity.*

---

**Submitted by:**  
Candidate Name: Punyashree S  
Course: Master of Computer Applications (MCA)  
Institution: Department of Computer Applications  
Project Title: DOCUSURE — Intelligent Document Processing, Information Extraction and Verification Using Generative AI
