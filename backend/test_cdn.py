import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    ("Reliance Industries", "https://www.ril.com/ar2023-24/pdf/BRSR.pdf"),
    ("Reliance ar", "https://www.ril.com/DownloadFiles/BRSR-Report-2023-24.pdf"),
    ("Vedanta", "https://www.vedantalimited.com/investor-relations/annual-reports/Vedanta-BRSR-Report-2023-24.pdf"),
    ("Tata Motors", "https://www.tatamotors.com/wp-content/uploads/2024/07/brsr-2023-24.pdf")
]

for name, u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
            print(f"[OK] {name}: {resp.status}, {resp.headers.get('Content-Length')} bytes")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
