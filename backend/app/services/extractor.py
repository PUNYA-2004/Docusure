import re
from typing import Dict, Any, List, Optional
from app.models.schemas import LineItem

class InformationExtractor:
    """
    Schema-based Information Extraction Engine:
    Extracts structured key-value entities and line-item tables.
    Never hallucinates missing data - returns 'NOT_FOUND' if unsupported.
    """

    @classmethod
    def extract(cls, doc_type: str, full_text: str, pages_tokens: List[Dict[str, Any]]) -> Dict[str, Any]:
        doc_type_upper = doc_type.upper()
        if doc_type_upper == "INVOICE":
            return cls._extract_invoice(full_text, pages_tokens)
        elif doc_type_upper == "CERTIFICATE":
            return cls._extract_certificate(full_text, pages_tokens)
        elif doc_type_upper == "APPLICATION_FORM":
            return cls._extract_application_form(full_text, pages_tokens)
        elif doc_type_upper == "RECEIPT":
            return cls._extract_receipt(full_text, pages_tokens)
        else:
            return cls._extract_generic(full_text, pages_tokens)

    @classmethod
    def _extract_invoice(cls, text: str, pages_tokens: List[Dict[str, Any]]) -> Dict[str, Any]:
        fields = {}
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        # 1. Vendor Name
        vendor = "NOT_FOUND"
        for i, l in enumerate(lines[:6]):
            # If line is header like TAX INVOICE, look at next line
            if l.lower() in ["tax invoice", "invoice", "commercial invoice", "original invoice"]:
                if i + 1 < len(lines):
                    vendor = lines[i + 1]
                    break
            elif any(s in l.lower() for s in ["pvt", "ltd", "technologies", "inc", "corp", "solutions", "hardware", "systems"]):
                vendor = l
                break
        fields["vendor_name"] = vendor

        # 2. Invoice Number: e.g. "Invoice Number: INV-10245" or "Invoice No: 123"
        inv_no_m = re.search(r"\b(?:invoice\s*(?:number|no\.?|#)|inv[-_\s]*(?:no\.?|num\.?|#))\s*[:#\-]?\s*([A-Za-z0-9\-_/]+)", text, re.IGNORECASE)
        fields["invoice_number"] = inv_no_m.group(1).strip() if inv_no_m else "NOT_FOUND"

        # 3. Invoice Date
        date_m = re.search(r"\b(?:invoice\s*date|dated|issue\s*date)\s*[:#\-]?\s*([0-9]{1,2}[-/.][0-9]{1,2}[-/.][0-9]{2,4})", text, re.IGNORECASE)
        fields["invoice_date"] = date_m.group(1).strip() if date_m else "NOT_FOUND"

        # 4. Due Date
        due_m = re.search(r"\b(?:due\s*date|payment\s*due)\s*[:#\-]?\s*([0-9]{1,2}[-/.][0-9]{1,2}[-/.][0-9]{2,4})", text, re.IGNORECASE)
        fields["due_date"] = due_m.group(1).strip() if due_m else "NOT_FOUND"

        # 5. Customer Name (after Bill To:)
        cust_name = "NOT_FOUND"
        for i, l in enumerate(lines):
            if "bill to" in l.lower() or "customer" in l.lower():
                # check next line
                if i + 1 < len(lines):
                    cand = lines[i + 1].strip()
                    if cand and not any(k in cand.lower() for k in ["invoice", "date", "phone", "gst"]):
                        cust_name = cand
                        break
        fields["customer_name"] = cust_name

        # 6. GST / Tax Number (Indian 15-char format)
        gst_m = re.search(r"\b([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1})\b", text)
        if not gst_m:
            gst_loose = re.search(r"\b(?:gstin|gst\s*(?:no|number)|tax\s*id)\s*[:#\-]?\s*([A-Za-z0-9]{10,16})", text, re.IGNORECASE)
            fields["gst_number"] = gst_loose.group(1).strip() if gst_loose else "NOT_FOUND"
        else:
            fields["gst_number"] = gst_m.group(1).strip()

        # 7. Subtotal Amount
        sub_m = re.search(r"\b(?:subtotal(?:\s*amount)?|sub-total|net\s*amount)\s*[:#\-]?\s*(?:INR|Rs\.?|\$)?\s*([0-9,]+(?:\.[0-9]{2})?)", text, re.IGNORECASE)
        fields["subtotal_amount"] = sub_m.group(1).replace(",", "").strip() if sub_m else "NOT_FOUND"

        # 8. Tax Amount
        tax_m = re.search(r"\b(?:tax(?:\s*amount)?|gst(?:\s*amount)?|vat)(?:\s*\([^)]+\))?\s*[:#\-]?\s*(?:INR|Rs\.?|\$)?\s*([0-9,]+(?:\.[0-9]{2})?)", text, re.IGNORECASE)
        fields["tax_amount"] = tax_m.group(1).replace(",", "").strip() if tax_m else "NOT_FOUND"

        # 9. Total Amount (negative lookbehind for sub)
        tot_m = re.search(r"(?<!sub)\b(?:total\s*amount|grand\s*total|amount\s*payable|balance\s*due|\btotal\b)\s*[:#\-]?\s*(?:INR|Rs\.?|\$)?\s*([0-9,]+(?:\.[0-9]{2})?)", text, re.IGNORECASE)
        fields["total_amount"] = tot_m.group(1).replace(",", "").strip() if tot_m else "NOT_FOUND"

        # 10. Payment Terms
        terms_m = re.search(r"(?:payment\s*terms|terms)[:\s]*([^\n]+)", text, re.IGNORECASE)
        fields["payment_terms"] = terms_m.group(1).strip() if terms_m else "NOT_FOUND"

        # Table Line Items Extraction
        line_items = cls._extract_table_line_items(lines)

        return {
            "fields": fields,
            "line_items": line_items,
            "raw_extraction": fields
        }

    @classmethod
    def _extract_table_line_items(cls, lines: List[str]) -> List[LineItem]:
        items: List[LineItem] = []
        i = 0
        n = len(lines)

        while i < n:
            l = lines[i]
            # Check for table header row
            if "item description" in l.lower() or "description" in l.lower():
                i += 1
                # Skip header tags like Qty, Unit Price, Line Total
                while i < n and lines[i].lower() in ["qty", "unit price", "line total", "price", "amount", "rate"]:
                    i += 1
                
                # Now parse rows:
                # Typically:
                # lines[i] = Description
                # lines[i+1] = Qty
                # lines[i+2] = Unit Price
                # lines[i+3] = Line Total
                item_idx = 1
                while i + 3 < n:
                    cand_desc = lines[i]
                    cand_qty_str = lines[i+1]
                    cand_price_str = lines[i+2]
                    cand_total_str = lines[i+3]

                    # Stop if we hit Subtotal or Total or Payment
                    if any(k in cand_desc.lower() for k in ["subtotal", "tax", "total", "payment", "authorized"]):
                        break

                    try:
                        # Qty is usually integer or small float
                        qty = float(cand_qty_str.replace(",", ""))
                        price = float(re.sub(r"[^\d.]", "", cand_price_str))
                        line_total = float(re.sub(r"[^\d.]", "", cand_total_str))

                        computed = round(qty * price, 2)
                        disc = round(abs(computed - line_total), 2)
                        items.append(LineItem(
                            item_id=item_idx,
                            description=cand_desc,
                            quantity=qty,
                            unit_price=price,
                            line_total=line_total,
                            computed_total=computed,
                            is_match=(disc < 0.05),
                            discrepancy=disc
                        ))
                        item_idx += 1
                        i += 4
                    except (ValueError, TypeError):
                        # Not a 4-line item row
                        i += 1
                break
            i += 1

        return items

    @classmethod
    def _extract_certificate(cls, text: str, pages_tokens: List[Dict[str, Any]]) -> Dict[str, Any]:
        fields = {}
        # 1. Recipient Name
        m = re.search(r"(?:certify\s+that|conferred\s+upon|awarded\s+to|presented\s+to)[:\s]*\n?([A-Za-z\s.]{3,35})", text, re.IGNORECASE)
        fields["recipient_name"] = m.group(1).split("\n")[0].strip() if m else "NOT_FOUND"

        # 2. Institution Name
        inst_m = re.search(r"(NATIONAL\s+INSTITUTE\s+OF\s+TECHNOLOGY|[A-Za-z\s.,&]{4,50}(?:UNIVERSITY|INSTITUTE|COLLEGE))", text, re.IGNORECASE)
        fields["institution_name"] = inst_m.group(1).split("\n")[0].strip() if inst_m else "NOT_FOUND"

        # 3. Course Name
        c_m = re.search(r"(?:degree\s+of|curriculum\s+and\s+conferred\s+the\s+degree\s+of)[:\s]*\n?([A-Za-z0-9\s.,&()-]{3,50})", text, re.IGNORECASE)
        fields["course_name"] = c_m.group(1).split("\n")[0].strip() if c_m else "NOT_FOUND"

        # 4. Certificate Number
        num_m = re.search(r"(?:certificate\s*(?:number|no|id)|roll\s*no)[:\s]*([A-Za-z0-9\-_/]+)", text, re.IGNORECASE)
        fields["certificate_number"] = num_m.group(1).strip() if num_m else "NOT_FOUND"

        # 5. Issue Date
        date_m = re.search(r"(?:date\s*of\s*issue|issued\s*on|date)[:\s]*([0-9]{1,2}[-/.][0-9]{1,2}[-/.][0-9]{2,4})", text, re.IGNORECASE)
        fields["issue_date"] = date_m.group(1).strip() if date_m else "NOT_FOUND"

        # 6. Grade / Score
        g_m = re.search(r"(?:grade|score|division)[:\s]*([A-Za-z0-9.+%()\s]+(?:\bdivision\b|\bdistinction\b|\bclass\b)?)", text, re.IGNORECASE)
        fields["grade_or_score"] = g_m.group(1).split("\n")[0].strip() if g_m else "NOT_FOUND"

        # 7. Issuing Authority
        auth_m = re.search(r"(?:authorized\s*signatory|dean|director|registrar)[:\s]*([A-Za-z\s.]{3,35})", text, re.IGNORECASE)
        fields["issuing_authority"] = auth_m.group(1).split("\n")[0].strip() if auth_m else "NOT_FOUND"

        return {"fields": fields, "line_items": [], "raw_extraction": fields}

    @classmethod
    def _extract_application_form(cls, text: str, pages_tokens: List[Dict[str, Any]]) -> Dict[str, Any]:
        fields = {}
        # 1. Applicant Name
        m = re.search(r"(?:applicant\s*name|name\s*of\s*applicant)[:\s]*([A-Za-z\s.]{3,35})", text, re.IGNORECASE)
        fields["applicant_name"] = m.group(1).strip() if m else "NOT_FOUND"

        # 2. Application ID
        app_m = re.search(r"(?:application\s*(?:id|no|number)|reference\s*no)[:\s]*([A-Za-z0-9\-_/]+)", text, re.IGNORECASE)
        fields["application_id"] = app_m.group(1).strip() if app_m else "NOT_FOUND"

        # 3. DOB
        dob_m = re.search(r"(?:date\s*of\s*birth|dob)[:\s]*([0-9]{1,2}[-/.][0-9]{1,2}[-/.][0-9]{2,4})", text, re.IGNORECASE)
        fields["date_of_birth"] = dob_m.group(1).strip() if dob_m else "NOT_FOUND"

        # 4. Email
        em_m = re.search(r"\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b", text)
        fields["email_address"] = em_m.group(1).strip() if em_m else "NOT_FOUND"

        # 5. Phone
        ph_m = re.search(r"(?:phone(?:\s*number)?|mobile)[:\s]*(\+?[0-9\-\s]{10,15})", text, re.IGNORECASE)
        fields["phone_number"] = ph_m.group(1).strip() if ph_m else "NOT_FOUND"

        # 6. Applied Position
        pos_m = re.search(r"(?:applied\s*position|program|course)[:\s]*([A-Za-z0-9\s.,&()-]{3,50})", text, re.IGNORECASE)
        fields["applied_position"] = pos_m.group(1).strip() if pos_m else "NOT_FOUND"

        # 7. Submission Date
        sub_m = re.search(r"(?:submission\s*date|submitted\s*on)[:\s]*([0-9]{1,2}[-/.][0-9]{1,2}[-/.][0-9]{2,4})", text, re.IGNORECASE)
        fields["submission_date"] = sub_m.group(1).strip() if sub_m else "NOT_FOUND"

        # 8. Verification Status
        stat_m = re.search(r"(?:eligibility\s*status|status)[:\s]*([A-Za-z0-9\s]+)", text, re.IGNORECASE)
        fields["verification_status_source"] = stat_m.group(1).strip() if stat_m else "NOT_FOUND"

        return {"fields": fields, "line_items": [], "raw_extraction": fields}

    @classmethod
    def _extract_receipt(cls, text: str, pages_tokens: List[Dict[str, Any]]) -> Dict[str, Any]:
        fields = {}
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        fields["store_name"] = lines[0] if lines else "NOT_FOUND"
        rcpt_m = re.search(r"(?:receipt\s*#|trans\s*id|bill\s*no)[:\s]*([A-Za-z0-9\-_]+)", text, re.IGNORECASE)
        fields["receipt_number"] = rcpt_m.group(1).strip() if rcpt_m else "NOT_FOUND"
        date_m = re.search(r"([0-9]{1,2}[-/.][0-9]{1,2}[-/.][0-9]{2,4})", text)
        fields["transaction_date"] = date_m.group(1).strip() if date_m else "NOT_FOUND"
        pay_m = re.search(r"(?:cash|credit\s*card|debit\s*card|upi|mastercard|visa)", text, re.IGNORECASE)
        fields["payment_method"] = pay_m.group(0).upper() if pay_m else "NOT_FOUND"
        tax_m = re.search(r"(?:tax|vat)[:\s]*(?:₹|Rs\.?|\$)?\s*([0-9,]+(?:\.[0-9]{2})?)", text, re.IGNORECASE)
        fields["tax_amount"] = tax_m.group(1).replace(",", "").strip() if tax_m else "NOT_FOUND"
        tot_m = re.search(r"(?:total|amount|net)[:\s]*(?:₹|Rs\.?|\$)?\s*([0-9,]+(?:\.[0-9]{2})?)", text, re.IGNORECASE)
        fields["total_amount"] = tot_m.group(1).replace(",", "").strip() if tot_m else "NOT_FOUND"
        return {"fields": fields, "line_items": [], "raw_extraction": fields}

    @classmethod
    def _extract_generic(cls, text: str, pages_tokens: List[Dict[str, Any]]) -> Dict[str, Any]:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        return {
            "fields": {
                "document_title": lines[0] if lines else "NOT_FOUND",
                "detected_date": "NOT_FOUND"
            },
            "line_items": [],
            "raw_extraction": {}
        }
