import base64
import json
import re
import urllib.request
import urllib.error

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

mermaid_blocks = re.findall(r"```mermaid\s*\n(.*?)```", readme, re.DOTALL)

# Test Diagram 1
b1 = mermaid_blocks[0].strip()
obj1 = {"code": b1, "mermaid": {"theme": "default"}}
b64_1 = base64.urlsafe_b64encode(json.dumps(obj1).encode("utf-8")).decode("ascii")
req1 = urllib.request.Request(f"https://mermaid.ink/svg/{b64_1}", headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req1, timeout=10) as resp:
    print(f"Diagram 1: HTTP {resp.status}, size {len(resp.read())}")

# Test Diagram 2 as-is:
b2_orig = mermaid_blocks[1].strip()
obj2_orig = {"code": b2_orig, "mermaid": {"theme": "default"}}
b64_2_orig = base64.urlsafe_b64encode(json.dumps(obj2_orig).encode("utf-8")).decode("ascii")
req2_orig = urllib.request.Request(f"https://mermaid.ink/svg/{b64_2_orig}", headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req2_orig, timeout=10) as resp:
        print(f"Diagram 2 (original): HTTP {resp.status}")
except urllib.error.HTTPError as e:
    print(f"Diagram 2 (original): Failed with HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:150]}")

# Test Diagram 2 with fix:
b2_fixed = b2_orig.replace(
    'Account -->|TRANSFERRED_TO<br/>{txn_id, amount, txn_date}| Account',
    'Account -->|"TRANSFERRED_TO<br/>{txn_id, amount, txn_date}"| Account'
)
obj2_fixed = {"code": b2_fixed, "mermaid": {"theme": "default"}}
b64_2_fixed = base64.urlsafe_b64encode(json.dumps(obj2_fixed).encode("utf-8")).decode("ascii")
req2_fixed = urllib.request.Request(f"https://mermaid.ink/svg/{b64_2_fixed}", headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req2_fixed, timeout=10) as resp:
    print(f"Diagram 2 (fixed): HTTP {resp.status}, size {len(resp.read())}")
