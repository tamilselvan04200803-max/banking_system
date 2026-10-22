import base64
import json
import re
import urllib.request
import urllib.error

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

mermaid_blocks = re.findall(r"```mermaid\s*\n(.*?)```", readme, re.DOTALL)
print(f"Total Mermaid blocks found in README.md: {len(mermaid_blocks)}")

all_passed = True
for i, block in enumerate(mermaid_blocks, 1):
    b = block.strip()
    obj = {"code": b, "mermaid": {"theme": "default"}}
    b64 = base64.urlsafe_b64encode(json.dumps(obj).encode("utf-8")).decode("ascii")
    req = urllib.request.Request(f"https://mermaid.ink/svg/{b64}", headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()
            print(f"Diagram {i}: HTTP {resp.status}, SVG size {len(content)} bytes - PASS")
    except urllib.error.HTTPError as e:
        all_passed = False
        print(f"Diagram {i}: FAILED HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:200]}")
    except Exception as e:
        all_passed = False
        print(f"Diagram {i}: ERROR: {e}")

if all_passed:
    print("ALL MERMAID DIAGRAMS IN README.MD PASSED VERIFICATION!")
else:
    raise SystemExit(1)
