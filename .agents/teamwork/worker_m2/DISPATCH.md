## 2026-10-21T16:25:36Z
You are teamwork_preview_worker for Milestone 2: Database Contracts (mock_db.py & db.py).
Your working directory is `c:\dbms_da-3-project\.agents\teamwork\worker_m2\`.
Read `c:\dbms_da-3-project\.agents\teamwork\ORIGINAL_REQUEST.md`.
Also read:
- `c:\dbms_da-3-project\.agents\teamwork\orchestrator_1\PROJECT.md`
- `c:\dbms_da-3-project\.agents\teamwork\spec_miner_contracts\handoff.md`

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Write Ownership (You exclusively own and create these files in `c:\dbms_da-3-project`):
- `c:\dbms_da-3-project\mock_db.py`
- `c:\dbms_da-3-project\db.py`

Your tasks:
1. `mock_db.py`:
   - Implement an in-memory mutable data store initialized with the exact 47-node dataset and 8 transfers.
   - Implement all 20 functions with exact signatures, parameters, and return types matching the specification:
     - Read (1-9): `get_customer`, `get_accounts`, `get_total_balance`, `get_transactions`, `get_loans`, `get_repayment_schedule`, `get_investments`, `get_service_requests`, `get_branches`.
     - Manage (10-14): `add_customer`, `update_customer_contact`, `open_account`, `close_account`, `raise_service_request`.
     - Process (15-16): `process_transaction`, `transfer_money`.
     - Analytics (17-20): `get_branch_account_counts`, `get_top_customers_by_balance`, `get_large_transfers`, `get_money_trail`.
   - Provide `reset_mock_db()` function that restores the in-memory dataset to the initial seed state.
   - Ensure all write operations mutate in-memory state dynamically (so successive reads reflect new accounts, balance changes, transfers, and new service requests).
   - Ensure all dates are strings formatted as `YYYY-MM-DD`.

2. `db.py`:
   - Live Neo4j Cypher implementation of all 20 functions with identical signatures and return dictionary schemas as `mock_db.py`.
   - Uses `connection.run_query` and `connection.new_id`.
   - All dates in Cypher returned as strings using `toString(...)` in the Cypher query.
   - `get_transactions(account_number)` uses a 3-part `UNION` in Cypher (part 1: deposits/withdrawals, part 2: transfer out, part 3: transfer in) and sorts results by `txn_date` descending in Python.
   - `transfer_money(from_account, to_account, amount)` executes as a single atomic Cypher query updating balances and creating `TRANSFERRED_TO` with `new_id('TR')`.
   - `get_money_trail(account_number)` uses Cypher variable-length path matching `[:TRANSFERRED_TO*1..3]`.
   - `close_account(account_number)` deletes the Account node ONLY if its balance is 0.
   - All write functions wrap execution in `try...except` and return `{'success': bool, 'message': str}` (plus additional keys where specified). No function should crash.

3. Parity & Validation:
   - Compile both files: `python -m py_compile mock_db.py db.py`.
   - Verify parity of all 20 function signatures and docstrings between `db.py` and `mock_db.py`.
   - Run a test script testing all 20 functions on `mock_db.py` to confirm 100% of Section 8 test cases pass.

4. Write handoff report to `c:\dbms_da-3-project\.agents\teamwork\worker_m2\handoff.md`.
5. Notify caller via `send_message`.
