import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

candidates = [
    ("Hindustan Copper", "https://www.hindustancopper.com/Upload/Notice/0-638592318721590740-BRSR%202023-24.pdf"),
    ("NTPC", "https://ntpc.co.in/sites/default/files/annual_report/NTPC_BRSR_2023-24.pdf"),
    ("GAIL", "https://gailonline.com/pdf/Investors/AnnualReport/BRSR_2023-24.pdf"),
    ("NMDC", "https://www.nmdc.co.in/Docs/AnnualReports/NMDC_BRSR_2023-24.pdf"),
    ("Coal India", "https://www.coalindia.in/media/documents/BRSR_Report_2023-24.pdf"),
    ("BEL", "https://bel-india.in/Documentviews.aspx?fileName=BRSR_2023-24.pdf"),
    ("PowerGrid", "https://www.powergrid.in/sites/default/files/inline-files/BRSR%202023-24.pdf"),
    ("BHEL", "https://www.bhel.com/assets/downloads/BRSR_2023_24.pdf"),
    ("SAIL", "https://sail.co.in/sites/default/files/2024-08/BRSR-2023-24.pdf"),
    ("NHPC", "https://www.nhpcindia.com/writereaddata/Images/pdf/BRSR_2023-24.pdf")
]

for name, url in candidates:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
            print(f"[OK] {name}: HTTP {resp.status}, Size: {resp.headers.get('Content-Length')}")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
