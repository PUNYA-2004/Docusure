from app.database import init_db, list_brsr_reports, get_brsr_observations
from app.services.brsr_service import BRSRProcessingService

init_db()
service = BRSRProcessingService()
seed_res = service.seed_initial_reports_manifest()
print("Seeding Result:", seed_res)

reports = list_brsr_reports()
print(f"Total Reports Registered: {len(reports)}")

for r in reports:
    c_name = r["company_name"]
    rep_id = r["report_id"]
    print(f"\nProcessing: {c_name} ({r['financial_year']})...")
    res = service.process_report(rep_id)
    print(f"  Classification: {res.document_type}")
    print(f"  Pages: {res.total_pages} | Tables: {res.tables_count}")
    print(f"  Indicators Extracted: {res.total_indicators_extracted} / {len(res.observations)}")
    print(f"  Processing Time: {res.processing_time_ms} ms")

all_obs = get_brsr_observations()
print(f"\nTotal Observations in Common Structured Dataset: {len(all_obs)}")
extracted_obs = [o for o in all_obs if o["extraction_status"] in ["EXTRACTED", "REPORTED_ZERO"]]
print(f"Successfully Extracted / Reported Zero Disclosures: {len(extracted_obs)}")
