import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    ("Source 1", "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFo68dtVwb3Wj7uC8QyAYuDi2Oj2CdxczgVhq0bSzRgSK2v6zkVIcM_T-dtbNCt0drLfZMNFMP6CZC6QDRXWwJY2hEE9M5fBmh8-LDLOLyJo5x45CN2HivsBplt079BMuZ5nygYBAuv6McSccR6IOYkRNY4qTmPtHE5n3oXgcr6dkwQImxa3Sq8M61xrw=="),
    ("Source 2", "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZUU2LJjmhw0nSJbpOT3mJVbgzqzK0HMvziGQ8XReHggBIvqROpOcUOU9xKw_eVK6EwmwMqnutKsAqOt7GDjBdojp5eyIe6FosDq4GtRHW_KMmnOqYElBesiIQRyXOyDGWkGfnBGmcbY2Sknko2fuyQHYiDIkrRtPY0UE8RAgB12ImnqaoftahLGvBxw=="),
    ("Source 3", "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbZfhsCmUsXLDKE-kA46OxqIbFon0sLmElOcrqJngYa3wz2I6ikWDila9hcNRIiTQsYkivB_Lv9CvrZGoKSSm8vYiJBK6LVOaybAz3quzHRTO8qmxxDVPPO8GI0nirwjuD98V37rjeAVk8WWhyaDfuWgd0fwkAjLJLCrinhy08CWyZXfjHZ32aP328vA=="),
    ("Source 4", "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCCwFtMyi08NkdKXlBkfzlu3gBL-EKEO6AE46o3n95f-3Q4mUjHfQ-IVEaHAE_CD8wKBgaeH3SUjBhp_vS2C_PWMEYC_wbqSldPdfzlPc8ldipMh-5cLfgGVbqDRreJe56rEN_NMhFllxlU-bfPcwKbz4tjvmLrogZ7CL1r3WXHo3gTEwIEhSx-u5lzw==")
]

for label, u in urls:
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    try:
        with urllib.request.urlopen(req, context=ctx) as r:
            print(f"{label} -> {r.geturl()} | {r.status} | {r.headers.get('Content-Length')} bytes")
    except Exception as e:
        print(f"{label} -> Error: {e}")
