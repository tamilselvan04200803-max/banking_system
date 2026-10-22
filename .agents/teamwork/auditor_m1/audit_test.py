import os
import re
import sys
import string

print("=== STARTING FORENSIC AUDIT ===")

# 1. Inspect presence of all expected M1 files
root = r"c:\dbms_da-3-project"
expected_files = [
    "requirements.txt",
    ".gitignore",
    ".env.example",
    "load_data.cypher",
    "connection.py"
]

missing = [f for f in expected_files if not os.path.exists(os.path.join(root, f))]
print(f"Missing expected files: {missing}")
assert not missing, f"Missing files: {missing}"

# 2. Check credentials / leakages
env_file = os.path.join(root, ".env")
print(f".env exists in project root: {os.path.exists(env_file)}")

with open(os.path.join(root, ".gitignore"), "r", encoding="utf-8") as f:
    gitignore_content = f.read()
    print(".gitignore ignores .env:", ".env" in gitignore_content)
    print(".gitignore ignores __pycache__/:", "__pycache__" in gitignore_content)
    print(".gitignore ignores .venv/:", ".venv" in gitignore_content)

with open(os.path.join(root, ".env.example"), "r", encoding="utf-8") as f:
    env_example = f.read()
    print(".env.example content:\n" + env_example.strip())

# Check for hardcoded real passwords / leaks
for f in expected_files:
    path = os.path.join(root, f)
    with open(path, "r", encoding="utf-8", errors="ignore") as fp:
        c = fp.read()
        # Ensure dummy password is only in .env.example / connection.py fallback
        if "sk-" in c or "AKIA" in c or "bearer" in c.lower():
            print(f"SUSPICIOUS TOKEN in {f}")

# 3. Audit connection.py
print("\n--- Auditing connection.py ---")
import importlib.util
spec = importlib.util.spec_from_file_location("connection", os.path.join(root, "connection.py"))
conn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conn)

# Check functions
assert hasattr(conn, "get_driver"), "connection.py missing get_driver"
assert hasattr(conn, "run_query"), "connection.py missing run_query"
assert hasattr(conn, "new_id"), "connection.py missing new_id"

# Check new_id randomness and format
ids = [conn.new_id("T") for _ in range(100)]
print(f"Sample new_id('T'): {ids[:5]}")
assert len(set(ids)) == 100, "new_id is not generating unique/random values! Possible hardcoding."
for tid in ids:
    assert tid.startswith("T"), f"ID {tid} does not start with prefix"
    assert len(tid) == 9, f"ID {tid} length is {len(tid)}, expected 9 (prefix + 8 chars)"
    suffix = tid[1:]
    assert all(c in (string.ascii_uppercase + string.digits) for c in suffix), f"ID suffix {suffix} invalid"

# Check get_driver
driver = conn.get_driver()
print(f"Driver type: {type(driver)}")
from neo4j._sync.driver import BoltDriver
assert isinstance(driver, BoltDriver), f"Expected BoltDriver, got {type(driver)}"
# Check singleton
driver2 = conn.get_driver()
assert driver is driver2, "get_driver did not return singleton instance"
conn.close_driver()
assert conn._driver is None, "close_driver failed to reset _driver"

# 4. Check for facade implementation in connection.py
with open(os.path.join(root, "connection.py"), "r", encoding="utf-8") as fp:
    conn_src = fp.read()

# Look for dummy return or facade cheats
assert "session.run(cypher, params)" in conn_src, "run_query lacks genuine session.run call"
assert "GraphDatabase.driver" in conn_src, "get_driver lacks genuine GraphDatabase.driver call"
assert "random.choices" in conn_src, "new_id lacks genuine random generation"

# 5. Audit load_data.cypher
print("\n--- Auditing load_data.cypher ---")
with open(os.path.join(root, "load_data.cypher"), "r", encoding="utf-8") as fp:
    cypher_src = fp.read()

# Check clean-slate delete
assert re.search(r"MATCH\s*\(\s*n\s*\)\s*DETACH\s*DELETE\s*n\s*;", cypher_src, re.I), "Missing MATCH (n) DETACH DELETE n;"

# Check constraints
constraints = re.findall(r"CREATE\s+CONSTRAINT.*?REQUIRE\s+\w+\.(\w+)\s+IS\s+UNIQUE", cypher_src, re.I)
print(f"Constraints detected ({len(constraints)}): {constraints}")
expected_constraints = [
    "branch_id", "emp_id", "customer_id", "account_number",
    "txn_id", "loan_id", "installment_id", "investment_id", "request_id"
]
for ec in expected_constraints:
    assert ec in constraints, f"Missing constraint on {ec}"
assert len(constraints) == 9, f"Expected 9 constraints, found {len(constraints)}"

# Check node definitions and count
labels = ['Branch', 'Employee', 'Customer', 'Account', 'Transaction', 'Loan', 'Installment', 'Investment', 'ServiceRequest']
node_counts = {}
for lbl in labels:
    matches = re.findall(rf"CREATE\s*\(\w+:{lbl}\b", cypher_src)
    node_counts[lbl] = len(matches)

print("Node counts by label:", node_counts)
total_nodes = sum(node_counts.values())
print(f"Total nodes: {total_nodes}")

expected_counts = {
    'Branch': 3,
    'Employee': 6,
    'Customer': 6,
    'Account': 8,
    'Transaction': 8,
    'Loan': 3,
    'Installment': 6,
    'Investment': 4,
    'ServiceRequest': 3
}
assert node_counts == expected_counts, f"Node count mismatch: {node_counts} != {expected_counts}"
assert total_nodes == 47, f"Total node count is {total_nodes}, expected 47"

# Check transfers
transfers = re.findall(r"TRANSFERRED_TO\s*\{\s*txn_id:\s*'([^']+)'", cypher_src)
print(f"Transfers detected ({len(transfers)}): {transfers}")
assert transfers == ['TR1', 'TR2', 'TR3', 'TR4', 'TR5', 'TR6', 'TR7', 'TR8'], f"Transfers mismatch: {transfers}"

# Check relationship types
rel_types = set(re.findall(r":([A-Z_]+)(?:\s*\{|\s*\])", cypher_src))
print(f"Relationship types in cypher ({len(rel_types)}): {sorted(list(rel_types))}")

print("\n=== ALL FORENSIC AUDIT CHECKS PASSED ===")
