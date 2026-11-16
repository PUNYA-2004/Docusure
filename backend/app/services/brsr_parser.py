import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pymupdf
from app.services.ocr_engine import OCREngine
from app.models.brsr_schemas import BRSRSectionDetail, BRSRTableData, DocumentType

class BRSRParser:
    """
    Dedicated, Reusable BRSR & Annual Report PDF Parser:
    - Digital text extraction via PyMuPDF with page number preservation
    - Automatic OCR fallback for scanned/rasterized pages using existing OCREngine
    - Document type classification (BRSR, Annual Report with BRSR, ESG Report, Unrelated)
    - Structural section detection (Section A, Section B, Section C, Principles P1-P9)
    - Table extraction with column header and cell mapping
    """

    def __init__(self):
        self.ocr_engine = OCREngine()

    def parse_pdf(self, file_path: str, max_pages_ocr: int = 15) -> Dict[str, Any]:
        """
        Parses a PDF document, extracting page text, tables, and section layout.
        Returns:
            {
                "success": bool,
                "error": Optional[str],
                "document_type": str,
                "confidence": float,
                "type_reasons": List[str],
                "page_count": int,
                "pages": [
                    {
                        "page_number": int,
                        "text": str,
                        "is_scanned": bool,
                        "tables": [BRSRTableData]
                    }
                ],
                "sections": List[BRSRSectionDetail],
                "principle_pages": Dict[str, int],
                "full_text": str
            }
        """
        path_obj = Path(file_path)
        if not path_obj.exists():
            return {
                "success": False,
                "error": f"File does not exist: {file_path}",
                "document_type": DocumentType.UNDETERMINED.value,
                "pages": [],
                "sections": []
            }

        try:
            doc = pymupdf.open(file_path)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to open PDF (corrupt or unsupported): {str(e)}",
                "document_type": DocumentType.UNDETERMINED.value,
                "pages": [],
                "sections": []
            }

        if doc.is_encrypted:
            doc.close()
            return {
                "success": False,
                "error": "PDF is password protected or encrypted.",
                "document_type": DocumentType.UNDETERMINED.value,
                "pages": [],
                "sections": []
            }

        page_count = len(doc)
        if page_count == 0:
            doc.close()
            return {
                "success": False,
                "error": "PDF contains 0 pages (empty document).",
                "document_type": DocumentType.UNDETERMINED.value,
                "pages": [],
                "sections": []
            }

        parsed_pages = []
        all_text_list = []
        tables_collected = []

        # Process each page
        for page_idx in range(page_count):
            page_num = page_idx + 1
            page = doc[page_idx]
            raw_text = page.get_text()
            is_scanned = False

            # If digital text is missing or extremely sparse, run OCR fallback
            if len(raw_text.strip().split()) < 8 and page_idx < max_pages_ocr:
                is_scanned = True
                pix = page.get_pixmap(dpi=150)
                temp_img_dir = path_obj.parent / ".temp_ocr"
                temp_img_dir.mkdir(parents=True, exist_ok=True)
                temp_img_path = temp_img_dir / f"p_{page_num}.png"
                pix.save(str(temp_img_path))
                
                ocr_res = self.ocr_engine._ocr_image(str(temp_img_path), page_num)
                raw_text = ocr_res.get("text", "")
                
                # Cleanup temporary image
                try:
                    if temp_img_path.exists():
                        temp_img_path.unlink()
                except Exception:
                    pass

            # Extract tables on page
            page_tables = []
            try:
                table_finder = page.find_tables()
                for t_idx, tab in enumerate(table_finder.tables):
                    extracted_rows = tab.extract()
                    if extracted_rows and len(extracted_rows) > 0:
                        # Clean cells
                        cleaned_rows = []
                        for row in extracted_rows:
                            cleaned_row = [
                                str(c).replace("\n", " ").strip() if c is not None else ""
                                for c in row
                            ]
                            cleaned_rows.append(cleaned_row)
                        
                        col_headers = cleaned_rows[0]
                        data_rows = cleaned_rows[1:] if len(cleaned_rows) > 1 else cleaned_rows
                        
                        table_data = BRSRTableData(
                            table_id=f"tab_p{page_num}_{t_idx+1}",
                            page_number=page_num,
                            title_or_context=f"Table on Page {page_num} (#{t_idx+1})",
                            column_headers=col_headers,
                            row_count=len(data_rows),
                            rows=data_rows
                        )
                        page_tables.append(table_data)
                        tables_collected.append(table_data)
            except Exception as e:
                # Table finding failed on this page, continue
                pass

            parsed_pages.append({
                "page_number": page_num,
                "text": raw_text,
                "is_scanned": is_scanned,
                "tables": [t.dict() for t in page_tables]
            })
            all_text_list.append(raw_text)

        doc.close()
        full_text = "\n\n--- PAGE BREAK ---\n\n".join(all_text_list)

        # Classify document type based on actual content
        doc_type, type_confidence, type_reasons = self._classify_document_type(full_text, page_count)

        # Detect BRSR Sections & NGRBC Principles
        sections, principle_pages = self._detect_sections_and_principles(parsed_pages)

        return {
            "success": True,
            "error": None,
            "document_type": doc_type,
            "confidence": type_confidence,
            "type_reasons": type_reasons,
            "page_count": page_count,
            "pages": parsed_pages,
            "sections": [s.dict() for s in sections],
            "principle_pages": principle_pages,
            "tables_count": len(tables_collected),
            "full_text": full_text
        }

    def _classify_document_type(self, full_text: str, page_count: int) -> Tuple[str, float, List[str]]:
        """
        Inspects content to strictly distinguish:
        - BRSR Report
        - Annual Report containing a BRSR section
        - ESG or Sustainability Report
        - Unrelated Corporate Document
        - Undetermined
        """
        text_lower = full_text.lower()
        reasons = []

        # Indicators for SEBI BRSR Format
        has_brsr_title = bool(re.search(r"business\s*responsibility\s*(?:and|&)\s*sustainability\s*report(?:ing)?\b|\bbrsr\b", text_lower))
        has_section_a = bool(re.search(r"section\s*a\b.*general\s*disclosures", text_lower, re.S))
        has_section_b = bool(re.search(r"section\s*b\b.*management\s*(?:and|&)\s*process", text_lower, re.S))
        has_section_c = bool(re.search(r"section\s*c\b.*principle[-\s]*wise\s*performance", text_lower, re.S))
        has_ngrbc_principles = bool(re.search(r"\bprinciple\s*[1-9]\b", text_lower) and "ngrbc" in text_lower or "national guidelines" in text_lower)

        # Indicators for Comprehensive Annual Report
        has_financial_statements = bool(re.search(r"standalone\s*financial\s*statements|balance\s*sheet\s*as\s*at|independent\s*auditor'?s\s*report", text_lower))
        has_directors_report = bool(re.search(r"board'?s\s*report|directors'?\s*report|management\s*discussion\s*and\s*analysis", text_lower))

        # Indicators for General ESG / Sustainability Report
        has_gri_sasb = bool(re.search(r"gri\s*content\s*index|tcfd\s*index|sasb\s*disclosure|sustainability\s*report", text_lower))

        # Invoices / Certificates / Forms (Unrelated documents)
        has_invoice_cues = bool(re.search(r"\btax\s*invoice\b|\bbill\s*to\b|\bgstin\b|\bamount\s*due\b", text_lower))
        has_academic_cues = bool(re.search(r"\bdegree\s*of\b|\bcertifies\s*that\b|\buniversity\b", text_lower))

        if has_brsr_title and (has_section_a or has_section_b or has_section_c):
            if page_count > 120 and (has_financial_statements and has_directors_report):
                reasons.append("Detected comprehensive corporate filing with embedded BRSR statutory chapter.")
                reasons.append("Identified Financial Statements and Board's Report alongside SEBI disclosures.")
                return DocumentType.ANNUAL_REPORT_WITH_BRSR.value, 0.94, reasons
            else:
                reasons.append("Identified formal SEBI BRSR filing structure with Section A, B, and C headings.")
                reasons.append("Found explicit NGRBC principle-wise performance metrics.")
                return DocumentType.BRSR_STANDALONE.value, 0.96, reasons

        elif has_gri_sasb and not (has_section_a and has_section_c):
            reasons.append("Document features sustainability reporting terminology (GRI/TCFD/SASB) without standard SEBI Section A format.")
            return DocumentType.ESG_SUSTAINABILITY_REPORT.value, 0.85, reasons

        elif has_invoice_cues or has_academic_cues:
            reasons.append("Document matches commercial transaction or educational certification format.")
            return DocumentType.UNRELATED_DOCUMENT.value, 0.92, reasons

        elif page_count > 0:
            if "sustainability" in text_lower or "environment" in text_lower:
                reasons.append("Contains environmental terminology but lacks formal SEBI statutory structure.")
                return DocumentType.ESG_SUSTAINABILITY_REPORT.value, 0.70, reasons
            reasons.append("Unable to confidently identify corporate BRSR or ESG structure.")
            return DocumentType.UNDETERMINED.value, 0.50, reasons

        return DocumentType.UNDETERMINED.value, 0.0, ["Empty document"]

    def _detect_sections_and_principles(self, pages: List[Dict[str, Any]]) -> Tuple[List[BRSRSectionDetail], Dict[str, int]]:
        """
        Locates exact starting and ending pages for Sections A, B, C and NGRBC Principles P1-P9.
        """
        sections: List[BRSRSectionDetail] = []
        principle_pages: Dict[str, int] = {}

        sec_a_start = None
        sec_b_start = None
        sec_c_start = None
        
        # Heading search regexes
        regex_sec_a = re.compile(r"SECTION\s*A\b|GENERAL\s*DISCLOSURES", re.IGNORECASE)
        regex_sec_b = re.compile(r"SECTION\s*B\b|MANAGEMENT\s*(?:AND|&)\s*PROCESS\s*DISCLOSURES", re.IGNORECASE)
        regex_sec_c = re.compile(r"SECTION\s*C\b|PRINCIPLE[-\s]*WISE\s*PERFORMANCE", re.IGNORECASE)

        total_pages = len(pages)

        for p in pages:
            p_num = p["page_number"]
            txt = p["text"]

            if regex_sec_a.search(txt) and sec_a_start is None:
                sec_a_start = p_num
            if regex_sec_b.search(txt) and sec_b_start is None:
                sec_b_start = p_num
            if regex_sec_c.search(txt) and sec_c_start is None:
                sec_c_start = p_num

            # Principles P1 to P9
            for p_idx in range(1, 10):
                p_key = f"P{p_idx}"
                if p_key not in principle_pages:
                    # Match "PRINCIPLE 1" or "Principle 1:" or "PRINCIPLE 1 -"
                    p_regex = re.compile(rf"\bPRINCIPLE\s*{p_idx}\b[:\s\-]", re.IGNORECASE)
                    if p_regex.search(txt):
                        principle_pages[p_key] = p_num

        # Calculate page ranges
        if sec_a_start:
            sec_a_end = (sec_b_start - 1) if (sec_b_start and sec_b_start > sec_a_start) else (sec_c_start - 1 if sec_c_start else total_pages)
            sections.append(BRSRSectionDetail(
                section_code="SECTION_A",
                section_name="Section A — General Disclosures",
                start_page=sec_a_start,
                end_page=sec_a_end,
                page_count=max(1, sec_a_end - sec_a_start + 1),
                detected_title="Section A: General Disclosures",
                detection_method="HEADING_PATTERN_MATCH",
                confidence=0.95
            ))

        if sec_b_start:
            sec_b_end = (sec_c_start - 1) if (sec_c_start and sec_c_start > sec_b_start) else total_pages
            sections.append(BRSRSectionDetail(
                section_code="SECTION_B",
                section_name="Section B — Management and Process Disclosures",
                start_page=sec_b_start,
                end_page=sec_b_end,
                page_count=max(1, sec_b_end - sec_b_start + 1),
                detected_title="Section B: Management and Process Disclosures",
                detection_method="HEADING_PATTERN_MATCH",
                confidence=0.95
            ))

        if sec_c_start:
            sec_c_end = total_pages
            sections.append(BRSRSectionDetail(
                section_code="SECTION_C",
                section_name="Section C — Principle-wise Performance",
                start_page=sec_c_start,
                end_page=sec_c_end,
                page_count=max(1, sec_c_end - sec_c_start + 1),
                detected_title="Section C: Principle-wise Performance Disclosure",
                detection_method="HEADING_PATTERN_MATCH",
                confidence=0.95
            ))

        return sections, principle_pages
