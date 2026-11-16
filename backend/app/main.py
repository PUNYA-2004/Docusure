import os
import shutil
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import UPLOAD_DIR, STATIC_DIR
from app.database import (
    init_db, list_documents, get_document_by_id, add_audit_log,
    get_audit_logs, update_document_review, list_brsr_reports,
    get_brsr_report, get_brsr_observations, update_brsr_observation
)
from app.models.schemas import (
    DocumentProcessResponse, HumanReviewRequest, CalibrationReport,
    RobustnessComparisonResponse
)
from app.models.brsr_schemas import BRSRManualReviewRequest, BRSRReportProcessingResult
from app.services.pipeline import DocumentProcessingPipeline
from app.services.confidence_calibrator import ConfidenceCalibrator
from app.services.robustness import RobustnessSuite
from app.services.brsr_service import BRSRProcessingService
from app.services.brsr_classifier import BRSRClassifier

app = FastAPI(
    title="DOCUSURE Document AI & BRSR ESG API",
    description="Evidence-Grounded Document Verification & BRSR ESG Information Extraction and Classification Platform",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = DocumentProcessingPipeline()
brsr_service = BRSRProcessingService()

@app.on_event("startup")
def startup_event():
    init_db()
    # Seed the 5 genuine BRSR reports from repository manifest
    brsr_service.seed_initial_reports_manifest()

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "service": "DOCUSURE Backend",
        "version": "1.0.0",
        "mode": "CPU-Optimized Evidence & Verification Engine"
    }

@app.post("/api/documents/process", response_model=DocumentProcessResponse)
async def process_document(
    file: UploadFile = File(...),
    doc_type: Optional[str] = Form(None)
):
    try:
        file_bytes = await file.read()
        res = pipeline.process(file_bytes=file_bytes, filename=file.filename, forced_doc_type=doc_type)
        return res
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@app.get("/api/documents")
def get_recent_documents(limit: int = 50):
    return list_documents(limit=limit)

@app.get("/api/documents/{doc_id}")
def get_document(doc_id: str):
    doc = get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@app.get("/api/documents/{doc_id}/pages/{page_num}/preview")
def get_page_preview(doc_id: str, page_num: int):
    preview_file = UPLOAD_DIR / doc_id / "previews" / f"page_{page_num}.png"
    if not preview_file.exists():
        raise HTTPException(status_code=404, detail=f"Page preview not found: {preview_file}")
    return FileResponse(str(preview_file), media_type="image/png")

@app.post("/api/documents/{doc_id}/review")
def review_document(doc_id: str, req: HumanReviewRequest):
    doc = get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    processed = doc["processed_data"]
    fields = processed.get("fields", [])

    # Apply manual corrections if any
    for f in fields:
        fname = f["field_name"]
        if fname in req.field_corrections:
            orig = f["value"]
            new_val = req.field_corrections[fname]
            f["original_value"] = orig
            f["value"] = new_val
            f["is_edited"] = True
            f["status"] = "SUPPORTED"  # Human verified
            f["confidence"] = 1.0
            f["confidence_level"] = "HIGH"
            f["verification_reason"] = f"Manually verified and corrected by reviewer ({req.reviewer_name})."

    # Update overall decision
    if req.decision == "ACCEPTED":
        new_decision = "AUTO-ACCEPT"
    elif req.decision == "REJECTED":
        new_decision = "REJECT / INVESTIGATE"
    else:
        new_decision = "REVIEW REQUIRED"

    processed["overall_decision"] = new_decision
    update_document_review(
        doc_id=doc_id,
        reviewer=req.reviewer_name,
        decision=new_decision,
        notes=req.notes or "",
        updated_processed_data=processed
    )

    add_audit_log(doc_id, "HUMAN_REVIEW", req.reviewer_name, {
        "decision": req.decision,
        "notes": req.notes,
        "corrections": req.field_corrections
    })

    return {
        "status": "success",
        "message": f"Document review recorded as {req.decision}",
        "document_id": doc_id,
        "updated_decision": new_decision
    }

@app.post("/api/documents/{doc_id}/robustness", response_model=RobustnessComparisonResponse)
def test_robustness(
    doc_id: str,
    degradation_type: str = Query("BLUR", pattern="^(BLUR|NOISE|ROTATION|JPEG_COMPRESSION|LOW_RESOLUTION|CONTRAST_FADED)$")
):
    doc = get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    preview_file = UPLOAD_DIR / doc_id / "previews" / "page_1.png"
    if not preview_file.exists():
        raise HTTPException(status_code=404, detail="Page 1 preview missing for degradation experiment")

    clean_text = doc.get("raw_ocr_text", "")
    res = RobustnessSuite.run_robustness_experiment(
        doc_id=doc_id,
        preview_image_path=str(preview_file),
        clean_text=clean_text,
        degradation_type=degradation_type
    )

    add_audit_log(doc_id, "ROBUSTNESS_TEST", "SYSTEM", {
        "degradation_type": degradation_type,
        "recovery_percentage": res.recovery_percentage
    })

    return res

@app.get("/api/calibration/report", response_model=CalibrationReport)
def get_calibration_report():
    return ConfidenceCalibrator._generate_benchmark_calibration()

@app.get("/api/audit/logs")
def get_logs(doc_id: Optional[str] = None, limit: int = 100):
    return get_audit_logs(doc_id=doc_id, limit=limit)

@app.get("/api/sample-docs")
def list_sample_documents():
    sample_dir = Path(__file__).resolve().parent / "sample_data"
    files = list(sample_dir.glob("*.pdf"))
    return [
        {
            "filename": f.name,
            "display_name": f.stem.replace("_", " ").title(),
            "size_kb": round(f.stat().st_size / 1024, 1)
        }
        for f in files
    ]

@app.post("/api/sample-docs/{sample_filename}/process", response_model=DocumentProcessResponse)
def process_sample_document(sample_filename: str):
    sample_path = Path(__file__).resolve().parent / "sample_data" / sample_filename
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail=f"Sample file {sample_filename} not found")

    with open(sample_path, "rb") as f:
        file_bytes = f.read()

    return pipeline.process(file_bytes=file_bytes, filename=sample_filename)

# =============================================================================
# BRSR & ESG INTELLIGENCE API ROUTES
# =============================================================================

@app.get("/api/brsr/reports")
def get_brsr_reports_list(
    company: Optional[str] = None,
    year: Optional[str] = None
):
    """Lists all collected and registered BRSR reports with search/filters."""
    return list_brsr_reports(company_filter=company, year_filter=year)

@app.get("/api/brsr/reports/{report_id}")
def get_single_brsr_report(report_id: str):
    """Retrieves metadata and parsed sections/tables for a specific BRSR report."""
    rep = get_brsr_report(report_id)
    if not rep:
        raise HTTPException(status_code=404, detail=f"BRSR report '{report_id}' not found.")
    return rep

@app.post("/api/brsr/reports/upload")
async def upload_brsr_report(
    file: UploadFile = File(...),
    company_name: str = Form(...),
    financial_year: str = Form("2023-24"),
    industry: Optional[str] = Form("Diversified")
):
    """Uploads a single BRSR PDF report and registers it in the repository."""
    file_bytes = await file.read()
    res = brsr_service.register_or_import_report(
        company_name=company_name,
        financial_year=financial_year,
        industry=industry,
        file_bytes=file_bytes,
        filename=file.filename
    )
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Failed to register report."))
    return res

@app.post("/api/brsr/reports/import-url")
def import_brsr_from_url(
    source_url: str = Form(...),
    company_name: str = Form(...),
    financial_year: str = Form("2023-24"),
    industry: Optional[str] = Form("Diversified")
):
    """Imports a BRSR report from an accessible public PDF URL."""
    res = brsr_service.register_or_import_report(
        company_name=company_name,
        financial_year=financial_year,
        industry=industry,
        source_url=source_url
    )
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Failed to import from URL."))
    return res

@app.post("/api/brsr/reports/{report_id}/process", response_model=BRSRReportProcessingResult)
def process_brsr_report(report_id: str):
    """Triggers the full non-LLM PDF parser, ESG extractor, and classifier on a report."""
    try:
        return brsr_service.process_report(report_id)
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"BRSR processing failed: {str(e)}")

@app.get("/api/brsr/reports/{report_id}/pages/{page_num}/preview")
def get_brsr_page_preview(report_id: str, page_num: int):
    """Returns rendered page preview PNG image."""
    preview_path = brsr_service.get_page_preview_file(report_id, page_num)
    if not preview_path or not preview_path.exists():
        raise HTTPException(status_code=404, detail=f"Page {page_num} preview not available for {report_id}.")
    return FileResponse(str(preview_path), media_type="image/png")

@app.get("/api/brsr/observations")
def get_canonical_observations(
    report_id: Optional[str] = None,
    company: Optional[str] = None,
    category: Optional[str] = None,
    indicator: Optional[str] = None,
    principle: Optional[str] = None,
    review_status: Optional[str] = None
):
    """Queries the common structured ESG dataset with multi-dimensional filters."""
    return get_brsr_observations(
        report_id=report_id,
        company_name=company,
        esg_category=category,
        indicator_code=indicator,
        principle=principle,
        review_status=review_status
    )

@app.post("/api/brsr/observations/{observation_id}/review")
def review_brsr_observation(observation_id: str, req: BRSRManualReviewRequest):
    """Allows manual auditor correction of extracted ESG values or mappings."""
    updates: Dict[str, Any] = {
        "review_status": "MANUALLY_EDITED",
        "manual_correction_notes": f"[{req.reviewer_name}] {req.reviewer_notes}"
    }
    if req.corrected_value is not None:
        updates["reported_value"] = req.corrected_value
    if req.corrected_numeric_value is not None:
        updates["numeric_value"] = req.corrected_numeric_value
        updates["normalized_value"] = req.corrected_numeric_value
    if req.corrected_unit is not None:
        updates["unit"] = req.corrected_unit
        updates["normalized_unit"] = req.corrected_unit
    if req.corrected_esg_category is not None:
        updates["esg_category"] = req.corrected_esg_category
    if req.corrected_principle is not None:
        updates["brsr_principle"] = req.corrected_principle

    update_brsr_observation(observation_id, updates)
    return {
        "status": "success",
        "message": f"Observation '{observation_id}' updated successfully.",
        "updates": updates
    }

@app.get("/api/brsr/principles/summary")
def get_principles_overview(report_id: Optional[str] = None):
    """Aggregates disclosures across the 9 NGRBC principles."""
    observations = get_brsr_observations(report_id=report_id)
    # Convert dicts back to schema representation for summary helper
    from app.models.brsr_schemas import BRSRCanonicalObservation
    obs_objs = [BRSRCanonicalObservation(**o) for o in observations]
    return BRSRClassifier.get_principle_summary(obs_objs)

@app.get("/api/brsr/export")
def export_brsr_data(
    format: str = Query("csv", pattern="^(csv|json)$"),
    company: Optional[str] = None,
    year: Optional[str] = None,
    category: Optional[str] = None
):
    """Exports the common structured ESG dataset to CSV or JSON format."""
    if format.lower() == "csv":
        from fastapi.responses import Response
        csv_str = brsr_service.export_dataset_csv(company_name=company, financial_year=year, esg_category=category)
        return Response(
            content=csv_str,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=docusure_brsr_esg_{year or 'all'}.csv"}
        )
    else:
        return brsr_service.export_dataset_json(company_name=company, financial_year=year, esg_category=category)

@app.get("/api/brsr/stats")
def get_brsr_statistics():
    """Returns high-level statistics for BRSR dashboard views."""
    reports = list_brsr_reports()
    obs = get_brsr_observations()
    
    comp_set = set(r["company_name"] for r in reports)
    categories = {"Environmental": 0, "Social": 0, "Governance": 0}
    statuses = {"EXTRACTED": 0, "REPORTED_ZERO": 0, "NOT_DISCLOSED": 0, "NOT_APPLICABLE": 0, "NOT_FOUND": 0}
    
    for o in obs:
        cat = o.get("esg_category")
        if cat in categories:
            categories[cat] += 1
        st = o.get("extraction_status")
        if st in statuses:
            statuses[st] += 1

    return {
        "total_reports": len(reports),
        "total_companies": len(comp_set),
        "total_observations": len(obs),
        "category_counts": categories,
        "status_counts": statuses,
        "companies": sorted(list(comp_set))
    }

