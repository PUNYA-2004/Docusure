import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

candidates = [
    ("Hindustan Copper", "https://www.hindustancopper.com/Upload/Notice/0-638592318721590740-BRSR%202023-24.pdf"),
    ("Bharat Dynamics", "https://bdl-india.in/sites/default/files/2024-09/BRSR-2023-24.pdf"),
    ("PSP Projects", "https://www.pspprojects.com/wp-content/uploads/2024/08/BRSR-2023-24.pdf"),
    ("IDFC FIRST Bank", "https://www.idfcfirstbank.com/content/dam/idfcfirstbank/pdf/financial-results/FY24/BRSR-FY-2023-24.pdf"),
    ("Minda Corporation", "https://www.sparkminda.com/wp-content/uploads/2024/08/BRSR-Report-2023-24.pdf"),
    ("Vardhman Special Steels", "https://www.vardhmansteel.com/upload/investor/BRSR%202023-24.pdf")
]

for name, url in candidates:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
            cl = resp.headers.get("Content-Length")
            print(f"[OK] {name}: HTTP {resp.status}, Size: {cl} bytes")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
