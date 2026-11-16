import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

candidates = [
    ("HDFC Life", "https://www.hdfclife.com/content/dam/hdfclife-pws/investor-relations/governance/pdf/BRSR-2023-24.pdf"),
    ("Lupin", "https://www.lupin.com/wp-content/uploads/2024/07/BRSR-Report-2023-24.pdf"),
    ("Manali Petrochemicals", "https://www.manalipetro.com/wp-content/uploads/2024/08/BRSR-2023-24.pdf"),
    ("KFintech", "https://www.kfintech.com/wp-content/uploads/2024/08/BRSR-2023-24.pdf")
]

for name, url in candidates:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
            print(f"[OK] {name}: HTTP {resp.status}, Size: {resp.headers.get('Content-Length')} bytes")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
