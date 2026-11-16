import re
import uuid
from typing import Dict, Any, List, Optional, Tuple
from rapidfuzz import fuzz
from app.models.brsr_schemas import (
    BRSRCanonicalObservation, ESGCategory, ExtractionStatus,
    ClassificationConfidence
)
from app.services.brsr_rules import CANONICAL_INDICATORS

class BRSRInformationExtractor:
    """
    Deterministic & Explainable ESG Information Extraction Engine:
    - Rule-based table parsing and row-column value alignment
    - Regex pattern matching for text disclosures
    - RapidFuzz approximate label matching for typographical variations
    - Evidence snippet attribution (page number + surrounding sentence/row)
    - Strict non-hallucination policy (missing is NEVER converted to zero)
    - Explicit classification of zeros, non-disclosures, and cross-references
    """

    @classmethod
    def extract_all(
        cls,
        report_id: str,
        company_name: str,
        financial_year: str,
        industry: str,
        parsed_pdf: Dict[str, Any]
    ) -> List[BRSRCanonicalObservation]:
        observations: List[BRSRCanonicalObservation] = []
        pages = parsed_pdf.get("pages", [])
        sections = parsed_pdf.get("sections", [])
        principle_pages = parsed_pdf.get("principle_pages", {})

        page_text_map = {p["page_number"]: p["text"] for p in pages}
        page_tables_map = {p["page_number"]: p.get("tables", []) for p in pages}

        # For every canonical indicator, run extraction
        for ind_code, ind_def in CANONICAL_INDICATORS.items():
            obs = cls._extract_single_indicator(
                ind_code=ind_code,
                ind_def=ind_def,
                report_id=report_id,
                company_name=company_name,
                financial_year=financial_year,
                industry=industry,
                pages=pages,
                page_text_map=page_text_map,
                page_tables_map=page_tables_map,
                principle_pages=principle_pages,
                sections=sections
            )
            observations.append(obs)

        return observations

    @classmethod
    def _extract_single_indicator(
        cls,
        ind_code: str,
        ind_def: Dict[str, Any],
        report_id: str,
        company_name: str,
        financial_year: str,
        industry: str,
        pages: List[Dict[str, Any]],
        page_text_map: Dict[int, str],
        page_tables_map: Dict[int, List[Dict[str, Any]]],
        principle_pages: Dict[str, int],
        sections: List[Dict[str, Any]]
    ) -> BRSRCanonicalObservation:

        # 1. Specialized extractors for board & workforce metrics
        if ind_code in ["SOC_EMPLOYEES_TOTAL", "SOC_WORKERS_TOTAL", "SOC_GENDER_DIVERSITY_FEMALE",
                        "GOV_BOARD_SIZE", "GOV_WOMEN_DIRECTORS", "GOV_INDEPENDENT_DIRECTORS"]:
            special_res = cls._extract_workforce_and_governance(
                ind_code, ind_def, pages, page_tables_map, sections
            )
            if special_res:
                rep_val, num_val, unit, page_no, snippet, conf, status = special_res
                return cls._build_observation(
                    report_id, company_name, financial_year, industry, ind_def,
                    rep_val, num_val, unit, page_no, snippet,
                    method="TABLE_PARSING" if "Table" in snippet else "REGEX_PATTERN",
                    confidence=conf, status=status
                )

        # 2. Table Extraction
        table_result = cls._extract_from_tables(ind_code, ind_def, page_tables_map, principle_pages, sections)
        if table_result:
            rep_val, num_val, unit, page_no, snippet, conf, status = table_result
            return cls._build_observation(
                report_id, company_name, financial_year, industry, ind_def,
                rep_val, num_val, unit, page_no, snippet,
                method="TABLE_PARSING", confidence=conf, status=status
            )

        # 3. Regex Text Pattern Extraction
        regex_result = cls._extract_from_text_patterns(ind_code, ind_def, pages, principle_pages, sections)
        if regex_result:
            rep_val, num_val, unit, page_no, snippet, conf, status = regex_result
            return cls._build_observation(
                report_id, company_name, financial_year, industry, ind_def,
                rep_val, num_val, unit, page_no, snippet,
                method="REGEX_PATTERN", confidence=conf, status=status
            )

        # 4. Check if cross-referenced elsewhere in annual report
        cross_ref_snippet = cls._check_cross_reference(ind_code, pages, principle_pages)
        if cross_ref_snippet:
            page_no, snip = cross_ref_snippet
            return cls._build_observation(
                report_id, company_name, financial_year, industry, ind_def,
                reported_value="Refer Annual Report Section",
                numeric_value=None,
                unit=ind_def.get("canonical_unit"),
                page_no=page_no,
                snippet=snip,
                method="HEURISTIC_SEARCH",
                confidence=0.85,
                status=ExtractionStatus.NOT_DISCLOSED
            )

        # 5. Not Found
        return cls._build_observation(
            report_id, company_name, financial_year, industry, ind_def,
            reported_value="NOT_FOUND",
            numeric_value=None,
            unit=ind_def.get("canonical_unit"),
            page_no=1,
            snippet="Metric was not identified in the parsed report content.",
            method="HEURISTIC_SEARCH",
            confidence=0.50,
            status=ExtractionStatus.NOT_FOUND
        )

    @classmethod
    def _extract_workforce_and_governance(
        cls,
        ind_code: str,
        ind_def: Dict[str, Any],
        pages: List[Dict[str, Any]],
        page_tables_map: Dict[int, List[Dict[str, Any]]],
        sections: List[Dict[str, Any]]
    ) -> Optional[Tuple[str, Optional[float], Optional[str], int, str, float, Optional[ExtractionStatus]]]:
        
        # Look in Section A pages (typically pages 1-8)
        sec_a_pages = list(range(1, min(10, len(pages) + 1)))
        for s in sections:
            if s["section_code"] == "SECTION_A":
                sec_a_pages = list(range(s["start_page"], min(s["end_page"] + 1, s["start_page"] + 8)))
                break

        for page_no in sec_a_pages:
            tables = page_tables_map.get(page_no, [])
            for table in tables:
                rows = table.get("rows", [])
                for r_idx, row in enumerate(rows):
                    if not row:
                        continue
                    r_clean = " ".join(row).lower()
                    first_cell = row[0].lower().strip()

                    # Total Employees
                    if ind_code == "SOC_EMPLOYEES_TOTAL":
                        if "total employees" in first_cell or "total employees" in r_clean:
                            val, unit = cls._find_first_valid_number(row)
                            if val:
                                return val, cls._parse_numeric(val), "Count", page_no, f"Table on Page {page_no}: [Row {r_idx+1}] " + " | ".join(row[:4]), 0.98, ExtractionStatus.EXTRACTED

                    # Total Workers
                    elif ind_code == "SOC_WORKERS_TOTAL":
                        if "total workers" in first_cell or "total workers" in r_clean:
                            val, unit = cls._find_first_valid_number(row)
                            if val:
                                return val, cls._parse_numeric(val), "Count", page_no, f"Table on Page {page_no}: [Row {r_idx+1}] " + " | ".join(row[:4]), 0.98, ExtractionStatus.EXTRACTED

                    # Female Workforce Composition
                    elif ind_code == "SOC_GENDER_DIVERSITY_FEMALE":
                        if "total employees" in first_cell or "total employees" in r_clean:
                            # Look for % in row
                            for c in row:
                                if "%" in c:
                                    num = cls._parse_numeric(c)
                                    if num and num < 60:  # Female percentage is typically < 60%
                                        return c.strip(), num, "%", page_no, f"Table on Page {page_no}: [Row {r_idx+1}] " + " | ".join(row[:6]), 0.92, ExtractionStatus.EXTRACTED

                    # Board Size
                    elif ind_code == "GOV_BOARD_SIZE":
                        if "board of directors" in first_cell or "board of directors" in r_clean:
                            val, _ = cls._find_first_valid_number(row)
                            if val:
                                num = cls._parse_numeric(val)
                                if num and 3 <= num <= 25:
                                    return val, num, "Count", page_no, f"Table on Page {page_no}: [Row {r_idx+1}] " + " | ".join(row[:4]), 0.98, ExtractionStatus.EXTRACTED

                    # Women Directors
                    elif ind_code == "GOV_WOMEN_DIRECTORS":
                        if "board of directors" in first_cell or "board of directors" in r_clean:
                            # Look for female count or percentage
                            for c in row[1:]:
                                if "%" in c:
                                    num = cls._parse_numeric(c)
                                    return c.strip(), num, "%", page_no, f"Table on Page {page_no}: [Row {r_idx+1}] " + " | ".join(row[:4]), 0.95, ExtractionStatus.EXTRACTED
                            # Or 2nd number
                            numbers = [cls._parse_numeric(c) for c in row if cls._is_number_like(c)]
                            if len(numbers) >= 2:
                                return str(numbers[1]), numbers[1], "Count", page_no, f"Table on Page {page_no}: [Row {r_idx+1}] " + " | ".join(row[:4]), 0.90, ExtractionStatus.EXTRACTED

                    # Independent Directors
                    elif ind_code == "GOV_INDEPENDENT_DIRECTORS":
                        if "independent director" in first_cell or "independent director" in r_clean:
                            val, _ = cls._find_first_valid_number(row)
                            if val:
                                return val, cls._parse_numeric(val), "Count", page_no, f"Table on Page {page_no}: [Row {r_idx+1}] " + " | ".join(row[:4]), 0.92, ExtractionStatus.EXTRACTED

            # Text fallback on same page
            txt = pages[page_no - 1]["text"]
            if ind_code == "SOC_EMPLOYEES_TOTAL":
                m = re.search(r"total\s*employees\s*(?:\([^)]+\))?\s*[:\-]?\s*([0-9,]+)", txt, re.I)
                if m:
                    return m.group(1).strip(), cls._parse_numeric(m.group(1)), "Count", page_no, f"Page {page_no}: " + m.group(0), 0.92, ExtractionStatus.EXTRACTED
            elif ind_code == "SOC_WORKERS_TOTAL":
                m = re.search(r"total\s*workers\s*(?:\([^)]+\))?\s*[:\-]?\s*([0-9,]+)", txt, re.I)
                if m:
                    return m.group(1).strip(), cls._parse_numeric(m.group(1)), "Count", page_no, f"Page {page_no}: " + m.group(0), 0.92, ExtractionStatus.EXTRACTED
            elif ind_code == "GOV_BOARD_SIZE":
                m = re.search(r"board\s*of\s*directors\s*[:\-]?\s*([0-9]{1,2})", txt, re.I)
                if m:
                    return m.group(1).strip(), cls._parse_numeric(m.group(1)), "Count", page_no, f"Page {page_no}: " + m.group(0), 0.92, ExtractionStatus.EXTRACTED

        return None

    @classmethod
    def _extract_from_tables(
        cls,
        ind_code: str,
        ind_def: Dict[str, Any],
        page_tables_map: Dict[int, List[Dict[str, Any]]],
        principle_pages: Dict[str, int],
        sections: List[Dict[str, Any]]
    ) -> Optional[Tuple[str, Optional[float], Optional[str], int, str, float, Optional[ExtractionStatus]]]:
        
        canonical_unit = ind_def.get("canonical_unit")
        target_pages = cls._get_target_pages_for_indicator(ind_def, principle_pages, sections, page_tables_map)

        # Precise matching rules per indicator code
        for page_no in target_pages:
            tables = page_tables_map.get(page_no, [])
            for table in tables:
                rows = table.get("rows", [])
                headers = table.get("column_headers", [])
                val_col = cls._find_current_year_col(headers)

                for r_idx, row in enumerate(rows):
                    if not row:
                        continue
                    first_cell = row[0].lower().strip()
                    row_full = " ".join(row).lower()

                    matched = False

                    # Specific disambiguations
                    if ind_code == "ENV_ENERGY_TOTAL":
                        if ("total energy consumed (a+b+c+d+e+f)" in first_cell or
                            "total energy consumed (a + b + c + d + e + f)" in first_cell or
                            "total energy consumption" in first_cell and "renewable" not in first_cell):
                            matched = True
                    elif ind_code == "ENV_ENERGY_RENEWABLE":
                        if "from renewable sources" in first_cell or "renewable sources (a+b+c)" in first_cell:
                            matched = True
                    elif ind_code == "ENV_ENERGY_NON_RENEWABLE":
                        if "from non-renewable sources" in first_cell or "non- renewable" in first_cell or "non-renewable sources (d+e+f)" in first_cell:
                            matched = True
                    elif ind_code == "ENV_GHG_SCOPE1":
                        if "total scope 1 emissions" in first_cell or ("scope 1" in first_cell and "emission" in row_full and "intensity" not in first_cell):
                            matched = True
                    elif ind_code == "ENV_GHG_SCOPE2":
                        if "total scope 2 emissions" in first_cell or ("scope 2" in first_cell and "emission" in row_full and "intensity" not in first_cell):
                            matched = True
                    elif ind_code == "ENV_GHG_SCOPE3":
                        if "total scope 3 emissions" in first_cell or ("scope 3" in first_cell and "emission" in row_full and "intensity" not in first_cell):
                            matched = True
                    elif ind_code == "ENV_WATER_WITHDRAWAL":
                        if "total volume of water withdrawal" in first_cell or "water withdrawal" in first_cell:
                            matched = True
                    elif ind_code == "ENV_WATER_CONSUMPTION":
                        if "total volume of water consumption" in first_cell or "water consumption" in first_cell:
                            matched = True
                    elif ind_code == "ENV_WASTE_GENERATED":
                        if "total waste generated" in first_cell or "waste generated" in first_cell:
                            matched = True
                    elif ind_code == "ENV_WASTE_RECYCLED":
                        if "recycled in mt" in first_cell or "waste recycled" in first_cell or "recycled" in first_cell:
                            matched = True
                    elif ind_code == "SOC_HEALTH_SAFETY_LTIFR":
                        if "lost time injury frequency rate" in first_cell or "ltifr" in first_cell:
                            matched = True
                    elif ind_code == "SOC_HUMAN_RIGHTS":
                        if any(k in first_cell for k in ["sexual harassment", "child labour", "forced labour", "human rights"]):
                            matched = True
                    elif ind_code == "SOC_CONSUMER_COMPLAINTS":
                        if "total complaints reported" in first_cell or "consumer complaints" in first_cell:
                            matched = True
                    elif ind_code == "GOV_REGULATORY_FINES":
                        if any(k in first_cell for k in ["monetary penalties", "penalties / fines", "strictures"]):
                            matched = True

                    if matched:
                        val_str, unit_str = cls._extract_val_and_unit_from_row(row, val_col, canonical_unit)
                        if val_str is not None:
                            status = None
                            val_lower = val_str.lower()
                            if val_lower in ["0", "0.0", "nil", "zero"]:
                                status = ExtractionStatus.REPORTED_ZERO
                            elif val_lower in ["-", "--", "not disclosed"]:
                                status = ExtractionStatus.NOT_DISCLOSED
                            elif val_lower in ["na", "n.a.", "not applicable"]:
                                status = ExtractionStatus.NOT_APPLICABLE

                            num_val = cls._parse_numeric(val_str)
                            snippet = f"Table on Page {page_no}: [Row {r_idx+1}] " + " | ".join(row[:4])
                            return val_str, num_val, unit_str or canonical_unit, page_no, snippet, 0.96, status

        return None

    @classmethod
    def _extract_from_text_patterns(
        cls,
        ind_code: str,
        ind_def: Dict[str, Any],
        pages: List[Dict[str, Any]],
        principle_pages: Dict[str, int],
        sections: List[Dict[str, Any]]
    ) -> Optional[Tuple[str, Optional[float], Optional[str], int, str, float, Optional[ExtractionStatus]]]:
        
        target_pages = cls._get_target_pages_for_indicator(ind_def, principle_pages, sections, {p["page_number"]: [] for p in pages})

        patterns = []
        if ind_code == "ENV_ENVIRONMENTAL_TARGETS":
            patterns.append(r"(net\s*zero\s*(?:by\s*)?[0-9]{4}|carbon\s*neutral(?:ity)?\s*(?:by\s*)?[0-9]{4}|100%\s*renewable\s*energy)")
        elif ind_code == "GOV_ETHICS_POLICY":
            patterns.append(r"(code\s*of\s*conduct|anti-bribery\s*and\s*anti-corruption\s*policy|anti-corruption\s*policy)")
        elif ind_code == "GOV_WHISTLEBLOWER":
            patterns.append(r"(whistle\s*blower\s*policy|vigil\s*mechanism)")
        elif ind_code == "SOC_CSR_SPENDING":
            patterns.append(r"amount\s*spent\s*on\s*csr[^0-9\n]*[:\-]?\s*(?:rs\.?|inr)?\s*([0-9,]+(?:\.[0-9]+)?)\s*(crores|lakhs)?")
        elif ind_code == "SOC_TRAINING_HOURS":
            patterns.append(r"training\s*on\s*health\s*and\s*safety[^0-9\n]*([0-9]{1,3}(?:\.[0-9]+)?)\s*%")

        for page in pages:
            p_no = page["page_number"]
            if target_pages and p_no not in target_pages:
                continue
            text = page["text"]
            for pat in patterns:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    rep_val = m.group(1).strip()
                    unit = m.group(2).strip() if len(m.groups()) > 1 and m.group(2) else ind_def.get("canonical_unit")
                    num_val = cls._parse_numeric(rep_val)
                    start_char = max(0, m.start() - 50)
                    end_char = min(len(text), m.end() + 60)
                    snippet = f"Page {p_no}: " + text[start_char:end_char].replace("\n", " ").strip()
                    return rep_val, num_val, unit, p_no, snippet, 0.90, ExtractionStatus.EXTRACTED

        return None

    @classmethod
    def _check_cross_reference(cls, ind_code: str, pages: List[Dict[str, Any]], principle_pages: Dict[str, int]) -> Optional[Tuple[int, str]]:
        """Detects if report explicitly redirects disclosure to another annual report section."""
        for p in pages:
            txt = p["text"]
            if "please refer" in txt.lower() or "refer natural capital" in txt.lower() or "refer annual report" in txt.lower():
                m = re.search(r"(please\s*refer[^\n.]+)", txt, re.IGNORECASE)
                if m:
                    return p["page_number"], f"Page {p['page_number']}: {m.group(0).strip()}"
        return None

    @classmethod
    def _get_target_pages_for_indicator(
        cls,
        ind_def: Dict[str, Any],
        principle_pages: Dict[str, int],
        sections: List[Dict[str, Any]],
        page_tables_map: Dict[int, Any]
    ) -> List[int]:
        category = ind_def["esg_category"]
        all_pages = sorted(list(page_tables_map.keys()))
        if not all_pages:
            return []

        # Find section boundaries
        sec_map = {s["section_code"]: (s["start_page"], s["end_page"]) for s in sections}

        if category == "Environmental":
            # Search Section C first
            if "SECTION_C" in sec_map:
                s_start, s_end = sec_map["SECTION_C"]
                cand = [p for p in all_pages if s_start <= p <= s_end]
                if cand:
                    # Append remaining pages after
                    return cand + [p for p in all_pages if p < s_start]
            return all_pages

        elif category == "Social":
            # Social indicators appear in Section A (employees, workers, diversity) and Section C (safety, human rights, complaints)
            if "Section A" in ind_def.get("section", "") and "SECTION_A" in sec_map:
                s_start, s_end = sec_map["SECTION_A"]
                cand = [p for p in all_pages if s_start <= p <= s_end]
                if cand:
                    return cand + [p for p in all_pages if p > s_end]
            elif "SECTION_C" in sec_map:
                s_start, s_end = sec_map["SECTION_C"]
                cand = [p for p in all_pages if s_start <= p <= s_end]
                if cand:
                    return cand + [p for p in all_pages if p < s_start]
            return all_pages

        elif category == "Governance":
            # Governance indicators appear in Section A (board), Section B (policies), and Section C (fines)
            return all_pages

        return all_pages

    @classmethod
    def _find_current_year_col(cls, headers: List[str]) -> int:
        for idx, h in enumerate(headers):
            h_clean = h.lower()
            if any(term in h_clean for term in ["current financial year", "current year", "fy 2023-24", "fy 2025-26", "fy 23-24", "2023-24", "2025-26"]):
                return idx
        return 1 if len(headers) > 1 else 0

    @classmethod
    def _extract_val_and_unit_from_row(cls, row: List[str], col_idx: int, canonical_unit: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        cand_val = row[col_idx].strip() if col_idx < len(row) else ""
        
        # If candidate cell is empty or pure label, look for first valid data cell in row
        if not cand_val or cand_val.lower() in ["parameter", "details", "none", "-"]:
            for c in row[1:]:
                clean_c = c.strip()
                if clean_c and (cls._is_number_like(clean_c) or clean_c.lower() in ["nil", "zero", "na", "not applicable", "-", "yes", "no"]):
                    cand_val = clean_c
                    break

        if not cand_val:
            return None, None

        unit = None
        for c in row:
            c_low = c.lower().strip()
            if c_low in ["gj", "mwh", "kl", "kilolitres", "mt", "metric tonnes", "%", "inr crores", "lakhs", "count"]:
                unit = c.strip()
                break

        return cand_val, unit or canonical_unit

    @classmethod
    def _find_first_valid_number(cls, row: List[str]) -> Tuple[Optional[str], Optional[str]]:
        for c in row[1:]:
            c_clean = c.strip()
            if cls._is_number_like(c_clean):
                return c_clean, None
        return None, None

    @classmethod
    def _is_number_like(cls, s: str) -> bool:
        s_clean = s.replace(",", "").replace("%", "").strip()
        try:
            float(s_clean)
            return True
        except ValueError:
            return False

    @classmethod
    def _parse_numeric(cls, s: str) -> Optional[float]:
        if not s:
            return None
        s_clean = re.sub(r"[#*]+", "", s).replace(",", "").strip()
        m = re.search(r"[-+]?[0-9]*\.?[0-9]+", s_clean)
        if m:
            try:
                return float(m.group(0))
            except Exception:
                return None
        return None

    @classmethod
    def _build_observation(
        cls,
        report_id: str,
        company_name: str,
        financial_year: str,
        industry: str,
        ind_def: Dict[str, Any],
        reported_value: str,
        numeric_value: Optional[float],
        unit: Optional[str],
        page_no: int,
        snippet: str,
        method: str,
        confidence: float,
        status: Optional[ExtractionStatus] = None
    ) -> BRSRCanonicalObservation:
        
        rep_val_clean = str(reported_value).strip()
        rep_val_lower = rep_val_clean.lower()

        if status is not None:
            ext_status = status
        elif rep_val_lower in ["0", "0.0", "nil", "zero"]:
            ext_status = ExtractionStatus.REPORTED_ZERO
        elif rep_val_lower in ["-", "--", "not disclosed", "not reported"]:
            ext_status = ExtractionStatus.NOT_DISCLOSED
        elif rep_val_lower in ["na", "n.a.", "not applicable"]:
            ext_status = ExtractionStatus.NOT_APPLICABLE
        elif rep_val_clean == "NOT_FOUND":
            ext_status = ExtractionStatus.NOT_FOUND
        else:
            ext_status = ExtractionStatus.EXTRACTED

        # Unit Normalization
        canonical_unit = ind_def.get("canonical_unit")
        normalized_value = numeric_value
        normalized_unit = unit or canonical_unit

        conversions = ind_def.get("unit_conversions", {})
        if unit and unit.lower() in conversions and numeric_value is not None:
            factor = conversions[unit.lower()]
            normalized_value = round(numeric_value * factor, 4)
            normalized_unit = canonical_unit

        # Classification Confidence
        if confidence >= 0.90:
            class_conf = ClassificationConfidence.HIGH
        elif confidence >= 0.70:
            class_conf = ClassificationConfidence.MEDIUM
        else:
            class_conf = ClassificationConfidence.UNCLASSIFIED

        obs_id = f"obs_{uuid.uuid4().hex[:12]}"

        return BRSRCanonicalObservation(
            observation_id=obs_id,
            company_name=company_name,
            industry=industry,
            financial_year=financial_year,
            report_id=report_id,
            report_type="BRSR Report",
            section_name=ind_def["section"],
            esg_category=ESGCategory(ind_def["esg_category"]),
            indicator_code=ind_def["code"],
            indicator_name=ind_def["name"],
            reported_value=rep_val_clean,
            numeric_value=numeric_value,
            unit=unit,
            normalized_value=normalized_value,
            normalized_unit=normalized_unit,
            reporting_period=financial_year,
            reporting_boundary="Standalone",
            brsr_principle=ind_def.get("principle"),
            brsr_core_indicator=ind_def.get("brsr_core"),
            source_page=page_no,
            source_text=snippet,
            extraction_method=method,
            classification_status=class_conf,
            extraction_status=ext_status,
            confidence_score=round(confidence, 2),
            review_status="AUTO_VERIFIED" if ext_status == ExtractionStatus.EXTRACTED else "REQUIRES_REVIEW",
            manual_correction_notes=None
        )
