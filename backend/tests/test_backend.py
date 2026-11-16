import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import init_db
from app.services.pipeline import DocumentProcessingPipeline

def test_pipeline_on_invoice():
    init_db()
    pipeline = DocumentProcessingPipeline()
    sample_pdf = backend_dir / "app" / "sample_data" / "clean_invoice_10245.pdf"
    
    print(f"Reading sample PDF: {sample_pdf}")
    with open(sample_pdf, "rb") as f:
        pdf_bytes = f.read()
        
    res = pipeline.process(pdf_bytes, "clean_invoice_10245.pdf")
    print("\n--- Pipeline Result ---")
    print(f"Doc ID: {res.document_id}")
    print(f"Type: {res.document_type}")
    print(f"Decision: {res.overall_decision}")
    print(f"Avg Confidence: {res.average_confidence}")
    print(f"Total Fields: {res.total_fields}")
    print(f"Verified Fields: {res.verified_count}")
    print(f"Anomalies: {len(res.anomalies)}")
    
    print("\nExtracted Fields:")
    for f in res.fields:
        ev_text = f.evidence.source_text if f.evidence else "NO EVIDENCE"
        print(f"  [{f.status.value:12}] {f.display_name:25}: {f.value:25} | Conf: {f.confidence * 100:.1f}% | Ev: '{ev_text[:40]}'")
        
    print("\nLine Items Table:")
    for it in res.line_items:
        print(f"  Item: {it.description} | Qty: {it.quantity} | Price: INR {it.unit_price} | Total: INR {it.line_total} (Match: {it.is_match})")
        
    assert res.document_type == "INVOICE"
    assert res.total_fields > 0
    print("\nTest SUCCESSFUL!")

if __name__ == "__main__":
    test_pipeline_on_invoice()
