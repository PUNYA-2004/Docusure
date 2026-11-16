import json
from pathlib import Path
import pymupdf
import re

manifest_path = Path("data/reports/reports_manifest.json")
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

for item in manifest:
    p = Path(item["local_file_path"])
    doc = pymupdf.open(str(p))
    print(f"\n==================== {item['company_name']} ({len(doc)} pages) ====================")
    
    sections_found = {}
    for idx, page in enumerate(doc):
        text = page.get_text()
        
        if re.search(r"SECTION\s*A\b|GENERAL\s*DISCLOSURES", text, re.I) and "SECTION_A" not in sections_found:
            sections_found["SECTION_A"] = idx + 1
        if re.search(r"SECTION\s*B\b|MANAGEMENT\s*(?:AND|&)\s*PROCESS", text, re.I) and "SECTION_B" not in sections_found:
            sections_found["SECTION_B"] = idx + 1
        if re.search(r"SECTION\s*C\b|PRINCIPLE[-\s]*WISE\s*PERFORMANCE", text, re.I) and "SECTION_C" not in sections_found:
            sections_found["SECTION_C"] = idx + 1
            
        # Check principles
        for p_num in range(1, 10):
            p_key = f"Principle_{p_num}"
            if re.search(rf"\bPRINCIPLE\s*{p_num}\b|\bP{p_num}\b", text, re.I) and p_key not in sections_found:
                sections_found[p_key] = idx + 1
                
    print("Detected Section Milestones:")
    for k, v in sorted(sections_found.items()):
        print(f"  {k}: Page {v}")
    doc.close()
