import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Let's test IRFC, Sangam Group, Vedanta, etc.
candidates = [
    ("IRFC", "https://irfc.co.in/wp-content/uploads/2024/09/BRSR-Report-2023-24.pdf"),
    ("Sangam", "https://sangamgroup.com/wp-content/uploads/2024/08/BRSR-2023-24.pdf"),
    ("Vedanta", "https://www.vedantalimited.com/img/investor/annualreport/Vedanta-BRSR-Report-2023-24.pdf"),
    ("IRFC_alt", "https://irfc.co.in/wp-content/uploads/2024/08/BRSR-2023-24.pdf"),
    ("Sangam_alt", "https://sangamgroup.com/investor-relations/BRSR-2023-24.pdf")
]

for name, url in candidates:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
            print(f"[OK] {name}: HTTP {resp.status}, Size: {resp.headers.get('Content-Length')}")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
