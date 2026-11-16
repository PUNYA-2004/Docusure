import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

redirects = [
    ("Manali Petrochemicals (BSE)", "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6qmMbPESM2RNR4CjC4-G_7BNY1Uepk6gpgjG1vCJota3A1aAifRo_f7FFQiqBHNrXwddwcSUBpI5Wq1bfsZocYxlfO5zmUNBKkc324lt9cN0cJL8MwG5yt29ItKR16knjBmhI_VI75hmTD-z3Clj4qBx0MVwRMLw0mfR7t17QYR-lcwrfHR3HL80twn8="),
    ("Company 2", "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBhLRceNQczfGPw0k6ghyu6zAwN8uFqMd-d67CWkC5BksWZRlIozrtQRGWHDOpgcLplTQ04XJ-d0x_2ewbyavyOzoDmT9AgZCPewzU3YLCDS3u3MYmKH-t4MUFSglISTFroR3_G_PkdAdA18pjj5yTEdVhkOmqHnd34jb-YGbsMFzv7jT3wfEgY33lWfg0vPjb"),
    ("Company 3", "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5CG_oAW22oo7URjkKVypxLrUB8AHHrG4YyIMtKW0TKmkRsCxSWpaDHpA_80XnSf4jRcuzWNm5WITY-b7sz1q13ojTAiyCxSXklteZU93KrmWPjIgFoiCIdJnMmu1xi8ZWiVxQ0z_QWJdkC_Imw9uAg9NQMcOO3y4o7FATzcwrhuU3lg=="),
    ("Company 4", "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHIH80r-RSsz_PbMtXhzmmiBj7KbbprLzKyqg65hmyoXfSEJDclMw_jXKLGdCt1SaUviq75sJ7Zl5EouoFTizFqezWqh5y_6F9mwZ4BVuU6pgWFwHPX0o2AFsFWY9W4CymbVUtpy1Z3JEUxf5z_2X36ZeLMIKCTXaFs6I6Vd9GCXpfrF2-rVzgFrChIdI71U3ow5pf17Y="),
    ("Company 5", "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsUL70P0oMwJu6zIhzjjZHYpWDLt_VSRArLtcKT45tdz-ogifgYwesIffGGe2ZDcaYdh9y0lrs4zy4c38oCocKUD2yyS9MJ9zLRgjZ0MqyqW5sKysMm5QyYrOiUefwEPY5hF-HgjaVLDkdqY_asSMkjaJKbbEH5tkUWVgtLox3qMytiwwOVTPo6h8kZSPC43KTbA=="),
    ("Company 6", "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYX-3WjUl3Ig1Tqlnwo7auGT2bd3TLdirZ18zCxwQ8Ignd-fNtxuMPUMdm23o5i4-7ZyvBsau4zq9j7zkTWcHuvSiqfPn4cTVJvzbFyOyz69Tv-NGWydLDnsUxIUcp2lZAd00dn17kHLmzB4N8bZlT7tw-1EZgloRUiLe50DoX4-Wh1r3CPmqxSdXclpIIF1UZoYS2RKGBOHq88eeCekjBaaYAXcsXTrXDUdqfsRccCCyt"),
    ("Company 7", "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjhUOJn_Fb8nuGZNtFBVzr887Q-Rg1ByViIyzysuvHLpXybIfo6kor1o6F_3acPSvu76fuHqW5PR_Kd6XROFYxEWKCpLc3qtTkMsTAZZ7c43r6evlA6qEdPm6v78MsaqGBqsii_Jo96cocCkTja5wfL4IK8_XU1ahUmyJMh1pIk3eo90aYTEgTMixkKik=")
]

for label, u in redirects:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            final_url = resp.geturl()
            ctype = resp.headers.get('Content-Type')
            clen = resp.headers.get('Content-Length')
            print(f"[OK] {label}: Final={final_url[:70]} | Type={ctype} | Size={clen}")
    except Exception as e:
        print(f"[FAIL] {label}: {e}")
