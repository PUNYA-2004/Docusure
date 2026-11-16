import urllib.request
import ssl
import os
import pymupdf

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = {
    'Manali Petrochemicals': 'https://www.bseindia.com/XBRLFILES/BRSRPDFUploadDocument/BRSR_500268_04092026202208.pdf',
    'Ramkrishna Forgings': 'https://ramkrishnaforgings.com/wp-content/uploads/2024/08/BRSR-FY-2023-24.pdf',
    'BSE Scrip 532610': 'https://www.bseindia.com/XBRLFILES/BRSRPDFUploadDocument/BRSR_532610_10092024194038.pdf',
    'NHPC': 'https://nsearchives.nseindia.com/corporate/NHPC_02082024181825_SE_Intimation_2024.pdf',
    'India Power': 'https://nsearchives.nseindia.com/corporate/DPSCLTD_05092024123048_BusinessResponsibilityandSustainabilityReport.pdf'
}

for name, u in urls.items():
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            data = r.read()
        doc = pymupdf.open(stream=data, filetype='pdf')
        pages = len(doc)
        txt0 = doc[0].get_text()[:300].replace('\n', ' ')
        print(f"[SUCCESS] {name} | Size: {len(data)} bytes | Pages: {pages} | P1: {txt0[:90]}")
        doc.close()
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
