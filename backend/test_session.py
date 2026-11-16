import requests

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
})

urls = [
    ("Tata Steel", "https://www.tatasteel.com/media/20569/integrated-report-2023-24.pdf"),
    ("Titan", "https://www.titancompany.in/sites/default/files/2024-07/Titan-Integrated-Annual-Report-2023-24.pdf"),
    ("ITC", "https://www.itcportal.com/about-itc/shareholder-value/annual-reports/itc-annual-report-2024/pdf/Report-and-Accounts-2024.pdf"),
    ("Tata Power", "https://www.tatapower.com/pdf/investor-relations/brsr-2023-24.pdf"),
    ("Wipro", "https://www.wipro.com/content/dam/nexus/en/investor/annual-reports/2023-2024/wipro-annual-report-2023-24.pdf")
]

for name, url in urls:
    try:
        r = session.head(url, timeout=10, allow_redirects=True, verify=False)
        print(f"[{r.status_code}] {name}: Content-Type={r.headers.get('content-type')}, Length={r.headers.get('content-length')}")
    except Exception as e:
        print(f"[ERR] {name}: {e}")
