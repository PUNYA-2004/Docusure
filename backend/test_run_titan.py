from app.services.brsr_parser import BRSRParser
from app.services.brsr_extractor import BRSRInformationExtractor
from app.config import REPORTS_DIR

parser = BRSRParser()
pdf_path = REPORTS_DIR / "Titan Company Limited" / "2023-24" / "report.pdf"
res = parser.parse_pdf(str(pdf_path))
observations = BRSRInformationExtractor.extract_all(
    report_id="titan_23_24",
    company_name="Titan Company Limited",
    financial_year="2023-24",
    industry="Consumer Goods & Lifestyle",
    parsed_pdf=res
)

print(f"Total Canonical Indicators: {len(observations)}")
for o in observations:
    status = o.extraction_status.value
    unit_str = o.unit if o.unit else ""
    norm_str = f"-> Normalized: {o.normalized_value} {o.normalized_unit}" if o.normalized_value is not None else ""
    print(f"[{o.esg_category.value:13}] {o.indicator_name:38} | {status:14} | Val: {o.reported_value} {unit_str} {norm_str} (Page {o.source_page})")
