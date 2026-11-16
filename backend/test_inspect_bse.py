import urllib.request
import ssl
import pymupdf

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

scrip_urls = [
    ("Scrip 500268", "https://www.bseindia.com/XBRLFILES/BRSRPDFUploadDocument/BRSR_500268_04092026202208.pdf"),
    ("Scrip 532924", "https://www.bseindia.com/XBRLFILES/BRSRPDFUploadDocument/BRSR_532924_03072026224756.pdf"),
    ("Scrip 500830", "https://www.bseindia.com/XBRLFILES/BRSRPDFUploadDocument/BRSR_500830_04072026150703.pdf"),
    ("Scrip 500114", "https://www.bseindia.com/XBRLFILES/BRSRPDFUploadDocument/BRSR_500114_03072026141930.pdf"),
    ("Scrip 535755", "https://www.bseindia.com/XBRLFILES/BRSRPDFUploadDocument/BRSR_535755_31072026205742.pdf")
]

for label, url in scrip_urls:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    with urllib.request.urlopen(req, context=ctx) as r:
        data = r.read()
    doc = pymupdf.open(stream=data, filetype='pdf')
    print(f"\n==================== {label} ({len(doc)} pages, {len(data)} bytes) ====================")
    for p_idx in range(min(2, len(doc))):
        text = doc[p_idx].get_text().strip()
        lines = [l.strip() for l in text.split('\n') if l.strip()][:15]
        print(f"--- Page {p_idx+1} ---")
        for line in lines:
            print("  ", line)
    doc.close()
