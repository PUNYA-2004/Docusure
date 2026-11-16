import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import init_db, get_db_connection, list_brsr_reports, get_brsr_observations
from app.services.brsr_service import brsr_service
from app.services.brsr_rules import CANONICAL_INDICATORS, NGRBC_PRINCIPLES
from app.services.brsr_classifier import BRSRClassifier

def test_brsr_suite():
    print("==================================================")
    print("DOCUSURE — BRSR Pipeline & API Verification Suite")
    print("==================================================")
    
    # 1. DB Verification
    print("\n[Step 1] Initializing Database & Verifying Tables...")
    init_db()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('brsr_reports', 'brsr_observations')")
    tables = [r[0] for r in c.fetchall()]
    conn.close()
    assert "brsr_reports" in tables and "brsr_observations" in tables, "BRSR tables missing!"
    print(f"-> BRSR Tables found: {tables}")
    
    # 2. Canonical Indicators & Rules
    print("\n[Step 2] Verifying Canonical Indicator Definitions...")
    assert len(CANONICAL_INDICATORS) >= 20, f"Expected at least 20 indicators, found {len(CANONICAL_INDICATORS)}"
    assert len(NGRBC_PRINCIPLES) == 9, "Expected 9 NGRBC principles"
    e_inds = [k for k, v in CANONICAL_INDICATORS.items() if v["esg_category"] == "Environmental"]
    s_inds = [k for k, v in CANONICAL_INDICATORS.items() if v["esg_category"] == "Social"]
    g_inds = [k for k, v in CANONICAL_INDICATORS.items() if v["esg_category"] == "Governance"]
    print(f"-> Indicators: {len(CANONICAL_INDICATORS)} total (E: {len(e_inds)}, S: {len(s_inds)}, G: {len(g_inds)})")
    
    # 3. Classifier Rule Check
    print("\n[Step 3] Verifying Multi-Dimensional ESG Classifier...")
    from app.models.brsr_schemas import BRSRCanonicalObservation, ExtractionStatus, ESGCategory
    test_obs = BRSRCanonicalObservation(
        observation_id="test_obs_01",
        report_id="test_rep_01",
        company_name="Titan Company Limited",
        financial_year="2023-24",
        indicator_code="ENV_ENERGY_TOTAL",
        indicator_name="Total Energy Consumption",
        reported_value="235995",
        numeric_value=235995.0,
        unit="GJ",
        source_page=28,
        source_text="Total energy consumption 235,995 GJ",
        extraction_status=ExtractionStatus.EXTRACTED,
        esg_category=ESGCategory.ENVIRONMENTAL
    )
    classified = BRSRClassifier.classify_observation(test_obs)
    assert classified.esg_category == ESGCategory.ENVIRONMENTAL
    assert "Section C" in classified.section_name
    assert "Principle 6" in classified.brsr_principle
    assert "Energy footprint" in classified.brsr_core_indicator
    print(f"-> ENV_ENERGY_TOTAL classification: {classified.esg_category.value} | {classified.section_name} | {classified.brsr_principle} | {classified.brsr_core_indicator}")

    test_obs_s = BRSRCanonicalObservation(
        observation_id="test_obs_02",
        report_id="test_rep_01",
        company_name="Titan Company Limited",
        financial_year="2023-24",
        indicator_code="SOC_GENDER_DIVERSITY_FEMALE",
        indicator_name="Female Workforce Composition",
        reported_value="35.2",
        numeric_value=35.2,
        unit="%",
        source_page=30,
        extraction_status=ExtractionStatus.EXTRACTED,
        esg_category=ESGCategory.SOCIAL
    )
    classified_s = BRSRClassifier.classify_observation(test_obs_s)
    assert classified_s.esg_category == ESGCategory.SOCIAL
    assert "Principle 3" in classified_s.brsr_principle
    print(f"-> SOC_GENDER_DIVERSITY_FEMALE classification: {classified_s.esg_category.value} | {classified_s.brsr_principle}")

    # 4. Reports in Database
    print("\n[Step 4] Querying Loaded Reports in Repository...")
    reports = list_brsr_reports()
    print(f"-> Found {len(reports)} BRSR reports registered in DB.")
    for r in reports:
        print(f"   [{r['report_id'][:8]}] {r['company_name']} | FY {r['financial_year']} | Status: {r['upload_status']}")
    assert len(reports) >= 4, "Expected at least 4 registered company reports"

    # 5. Observations in Database
    print("\n[Step 5] Querying Canonical Observations...")
    obs_all = get_brsr_observations()
    print(f"-> Total canonical observations in DB: {len(obs_all)}")
    assert len(obs_all) >= 50, f"Expected >= 50 observations, found {len(obs_all)}"

    # 6. Verification of Stats & Aggregations
    print("\n[Step 6] Testing Aggregation & Summary Services...")
    from app.main import get_brsr_statistics, get_principles_overview
    stats = get_brsr_statistics()
    print(f"-> Stats Summary: {stats}")
    assert stats["total_reports"] >= 4
    assert stats["total_observations"] > 0
    assert stats["category_counts"]["Environmental"] > 0
    assert stats["category_counts"]["Social"] > 0
    assert stats["category_counts"]["Governance"] > 0

    p_summary = get_principles_overview()
    print(f"-> Principle Summary items: {len(p_summary)}")
    assert len(p_summary) == 9

    # 7. Verification of Data Export
    print("\n[Step 7] Testing Structured Export (JSON & CSV)...")
    json_export = brsr_service.export_dataset_json()
    assert len(json_export) == len(obs_all)
    print(f"-> JSON export verified: {len(json_export)} observations.")

    csv_export = brsr_service.export_dataset_csv()
    csv_lines = csv_export.strip().splitlines()
    assert len(csv_lines) > 50
    print(f"-> CSV export verified: {len(csv_lines)} rows including header.")

    # 8. Human Review Workflow
    print("\n[Step 8] Testing Human Review Status Update...")
    from app.main import review_brsr_observation
    from app.models.brsr_schemas import BRSRManualReviewRequest
    first_obs = obs_all[0]
    review_req = BRSRManualReviewRequest(
        observation_id=first_obs["observation_id"],
        reviewer_name="MCA Auditor",
        reviewer_notes="Verified against official SEBI report page"
    )
    res = review_brsr_observation(first_obs["observation_id"], review_req)
    assert res["status"] == "success"
    
    updated_obs = get_brsr_observations()
    target_updated = next(o for o in updated_obs if o["observation_id"] == first_obs["observation_id"])
    assert target_updated["review_status"] == "MANUALLY_EDITED"
    print(f"-> Successfully updated observation {first_obs['observation_id'][:8]} to MANUALLY_EDITED.")

    print("\n==================================================")
    print("ALL BRSR PIPELINE & CLASSIFICATION TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    test_brsr_suite()
