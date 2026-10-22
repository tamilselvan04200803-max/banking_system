## 2026-10-21T16:05:22Z
You are teamwork_preview_worker for Milestone 1: Infrastructure & Schema.
Your working directory is `c:\dbms_da-3-project\.agents\teamwork\worker_m1\`.
Read `c:\dbms_da-3-project\.agents\teamwork\ORIGINAL_REQUEST.md`.
Also read:
- `c:\dbms_da-3-project\.agents\teamwork\orchestrator_1\PROJECT.md`
- `c:\dbms_da-3-project\.agents\teamwork\spec_miner_schema\handoff.md`

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Write Ownership (You exclusively own and create these files in `c:\dbms_da-3-project`):
- `c:\dbms_da-3-project\requirements.txt`
- `c:\dbms_da-3-project\.gitignore`
- `c:\dbms_da-3-project\.env.example`
- `c:\dbms_da-3-project\load_data.cypher`
- `c:\dbms_da-3-project\connection.py`

Your tasks:
1. `requirements.txt`: specify `neo4j`, `streamlit`, `python-dotenv`, `pandas`.
2. `.gitignore`: include `.env`, `__pycache__/`, `.venv/`.
3. `.env.example`: template with `NEO4J_URI=bolt://localhost:7687`, `NEO4J_USER=neo4j`, `NEO4J_PASSWORD=password`.
4. `load_data.cypher`: the complete shared dataset cypher script with:
   - Clean-slate delete (`MATCH (n) DETACH DELETE n;`)
   - 9 unique constraints on entity IDs (`Branch.branch_id`, `Employee.emp_id`, `Customer.customer_id`, `Account.account_number`, `Transaction.txn_id`, `Loan.loan_id`, `Installment.installment_id`, `Investment.investment_id`, `ServiceRequest.request_id`)
   - Exact 47 nodes: 3 Branches, 6 Employees, 6 Customers, 8 Accounts, 8 Transactions, 3 Loans, 6 Installments, 4 Investments, 3 Service Requests.
   - All relationships: `ASSIGNED_TO`, `HOLDS`, `HELD_AT`, `HAS_TRANSACTION` / `PERFORMED`, `TRANSFERRED_TO` (8 transfers TR1-TR8 with amount and txn_date matching test cases), `TAKEN`, `SANCTIONED_BY`, `HAS_INSTALLMENT`, `INVESTED_IN`, `RAISED`.
5. `connection.py`:
   - `get_driver()`: loads environment variables with `dotenv.load_dotenv()`, reads `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`. Safely handles driver creation.
   - `run_query(cypher, params=None)`: runs any Cypher (read or write) and returns a list of dicts, one per row.
   - `new_id(prefix)`: returns prefix + 8 random uppercase alphanumeric characters (e.g. `T3F9A12C`).
6. Validate your files: compile check `connection.py` using `python -m py_compile connection.py`.
7. Write your handoff report to `c:\dbms_da-3-project\.agents\teamwork\worker_m1\handoff.md` with:
   - Summary of files created
   - Verification command and output
8. Notify the caller via `send_message`.
