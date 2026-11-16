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
    # search first 3 pages for company name
    full_first3 = ""
    for p_idx in range(min(3, len(doc))):
        full_first3 += doc[p_idx].get_text() + "\n"
    
    # find lines with company name or CIN
    lines = [l.strip() for l in full_first3.split('\n') if l.strip()]
    cin = "UNKNOWN"
    company = "UNKNOWN"
    for l in lines:
        if "CIN" in l.upper() or "L" in l and any(c.isdigit() for c in l) and len(l) == 21:
            cin = l
        if any(w in l.upper() for w in ["LIMITED", "LTD", "DEVELOPERS", "CORPORATION", "INDUSTRIES"]):
            if company == "UNKNOWN" and not any(k in l.upper() for k in ["BSE", "NATIONAL STOCK", "SECRETARY"]):
                company = l
    
    print(f"{label} | Company: {company} | Pages: {len(doc)} | Size: {len(data)} bytes")
    # print first 5 lines safely
    safe_lines = [l.encode('ascii', 'replace').decode('ascii') for l in lines[:6]]
    print("  Header lines:", " /// ".join(safe_lines))
    doc.close()
