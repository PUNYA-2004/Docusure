import urllib.request
import ssl
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Let's check some URLs
urls = [
    ("Hindustan Copper", "https://www.hindustancopper.com/Upload/Notice/0-638592318721590740-BRSR%202023-24.pdf"),
    ("Suzlon Energy", "https://www.suzlon.com/pdf/investor-relations/financial-results/FY24/Suzlon-BRSR-Report-FY-2023-24.pdf"),
    ("JBM Auto", "https://www.jbmgroup.com/wp-content/uploads/2024/08/BRSR-Report-2023-24.pdf"),
    ("Paras Defence", "https://www.parasdefence.com/investor-relations/annual-reports/BRSR-2023-24.pdf"),
    ("Bandhan Bank", "https://bandhanbank.com/sites/default/files/2024-07/BRSR_Report_2023_24.pdf")
]

for name, url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
            print(f"[OK] {name}: HTTP {resp.status}, Size: {resp.headers.get('Content-Length')}")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
