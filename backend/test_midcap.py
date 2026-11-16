import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

candidates = [
    ("Ramkrishna Forgings", "https://ramkrishnaforgings.com/pdf/investors/annual-report/BRSR-2023-24.pdf"),
    ("Gravita India", "https://www.gravitaindia.com/wp-content/uploads/2024/08/BRSR-2023-24.pdf"),
    ("ESAF Bank", "https://www.esafbank.com/assets/pdf/investor-relations/BRSR-2023-24.pdf"),
    ("Jindal Stainless", "https://www.jindalstainless.com/wp-content/uploads/2024/08/BRSR-2023-24.pdf")
]

for name, url in candidates:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
            print(f"[OK] {name}: HTTP {resp.status}, Size: {resp.headers.get('Content-Length')} bytes")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
