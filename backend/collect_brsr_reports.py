import os
import hashlib
import urllib.request
import ssl
import json
from pathlib import Path
import pymupdf

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "reports"
DATA_DIR.mkdir(parents=True, exist_ok=True)

REPORTS_METADATA = [
    {
        "company_name": "Titan Company Limited",
        "industry": "Consumer Goods & Lifestyle (Jewelry, Watches, Eyewear)",
        "financial_year": "2023-24",
        "report_title": "Business Responsibility & Sustainability Report (BRSR) 2023-24",
        "report_category": "BRSR Report",
        "source_url": "https://www.bseindia.com/XBRLFILES/BRSRPDFUploadDocument/BRSR_500114_03072026141930.pdf",
        "cin": "L74999TZ1984PLC001456",
        "bse_scrip": "500114"
    },
    {
        "company_name": "Colgate-Palmolive (India) Limited",
        "industry": "Fast Moving Consumer Goods (FMCG / Oral Care)",
        "financial_year": "2023-24",
        "report_title": "Business Responsibility & Sustainability Report (BRSR) 2023-24",
        "report_category": "BRSR Report",
        "source_url": "https://www.bseindia.com/XBRLFILES/BRSRPDFUploadDocument/BRSR_500830_04072026150703.pdf",
        "cin": "L24200MH1937PLC002700",
        "bse_scrip": "500830"
    },
    {
        "company_name": "Aditya Birla Fashion and Retail Limited",
        "industry": "Apparel & Retail",
        "financial_year": "2023-24",
        "report_title": "Business Responsibility & Sustainability Report (BRSR) 2023-24",
        "report_category": "BRSR Report",
        "source_url": "https://www.bseindia.com/XBRLFILES/BRSRPDFUploadDocument/BRSR_535755_31072026205742.pdf",
        "cin": "L18101MH2007PLC233901",
        "bse_scrip": "535755"
    },
    {
        "company_name": "Manali Petrochemicals Limited",
        "industry": "Chemicals & Petrochemicals",
        "financial_year": "2023-24",
        "report_title": "Business Responsibility and Sustainability Report (BRSR) 2023-24",
        "report_category": "BRSR Report",
        "source_url": "https://www.bseindia.com/XBRLFILES/BRSRPDFUploadDocument/BRSR_500268_04092026202208.pdf",
        "cin": "L24294TN1986PLC013087",
        "bse_scrip": "500268"
    },
    {
        "company_name": "Kolte-Patil Developers Limited",
        "industry": "Real Estate & Infrastructure Development",
        "financial_year": "2023-24",
        "report_title": "Business Responsibility & Sustainability Reporting (BRSR) 2023-24",
        "report_category": "BRSR Report",
        "source_url": "https://www.bseindia.com/XBRLFILES/BRSRPDFUploadDocument/BRSR_532924_03072026224756.pdf",
        "cin": "L45200PN1991PLC129428",
        "bse_scrip": "532924"
    }
]

def calculate_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def collect_reports():
    manifest = []
    print(f"Starting collection of {len(REPORTS_METADATA)} BRSR reports...")
    
    for meta in REPORTS_METADATA:
        c_name = meta["company_name"]
        fy = meta["financial_year"]
        target_dir = DATA_DIR / c_name / fy
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "report.pdf"
        
        print(f"\nFetching: {c_name} ({fy})...")
        print(f"  URL: {meta['source_url']}")
        
        try:
            req = urllib.request.Request(
                meta["source_url"],
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
                data = resp.read()
            
            with open(target_file, "wb") as f:
                f.write(data)
            
            file_hash = calculate_sha256(data)
            doc = pymupdf.open(str(target_file))
            page_count = len(doc)
            doc.close()
            
            record = {
                **meta,
                "local_file_path": str(target_file.relative_to(BASE_DIR)),
                "file_size_bytes": len(data),
                "page_count": page_count,
                "file_hash_sha256": file_hash,
                "download_status": "COMPLETED",
                "processing_status": "READY_FOR_PARSING"
            }
            manifest.append(record)
            print(f"  [SUCCESS] Saved {len(data):,} bytes ({page_count} pages) to {record['local_file_path']}")
            print(f"  SHA-256: {file_hash[:16]}...")
        except Exception as e:
            print(f"  [ERROR] Failed to download {c_name}: {e}")
            record = {
                **meta,
                "local_file_path": str(target_file.relative_to(BASE_DIR)),
                "file_size_bytes": 0,
                "page_count": 0,
                "file_hash_sha256": "",
                "download_status": f"FAILED: {str(e)}",
                "processing_status": "ERROR"
            }
            manifest.append(record)
            
    manifest_path = DATA_DIR / "reports_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest saved to {manifest_path} with {len(manifest)} reports.")

if __name__ == "__main__":
    collect_reports()
