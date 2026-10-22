# Original User Request

## Initial Request — 2026-10-21T15:49:44Z

# Teamwork Project Prompt — Draft

> Status: Launched
> Goal: Craft prompt → get user approval → delegate to teamwork_preview
> Requested team: [none — teamwork routes from the description]

Build a complete, production-ready "Smart Banking Mini-Project" using Neo4j and Streamlit strictly following our team specification, graph schema, 20 function contracts, 4 UI screens, and test suite.

Working directory: `c:\dbms_da-3-project`
Integrity mode: demo

## Shared Dataset (`load_data.cypher`)
The exact initialization script with constraints and 47 nodes:
- 3 Branches (BR01 Anna Nagar, BR02 T Nagar, BR03 Koramangala)
- 6 Employees (E01 Ramesh Iyer, E02 Priya Menon RM, E03 Arjun Nair, E04 Divya Rao, E05 Karthik Suresh CSE, E06 Meena Pillai)
- 6 Customers (C01 Samridhi, C02 Rahul, C03 Anita, C04 Suresh, C05 Lakshmi, C06 Vikram)
- 8 Accounts (AC1001-AC1008)
- 8 Transactions (T1-T8)
- 8 Transfers (TR1-TR8 via `TRANSFERRED_TO`)
- 3 Loans (L01-L03)
- 6 Installments
- 4 Investments (I01-I04)
- 3 Service Requests (SR01-SR03)

---

## Requirements

### R1. Project Files & Infrastructure
Create the following files:
1. `requirements.txt`: `neo4j`, `streamlit`, `python-dotenv`, `pandas`
2. `.gitignore`: `.env`, `__pycache__/`, `.venv/`
3. `.env.example`: template with `NEO4J_URI=bolt://localhost:7687`, `NEO4J_USER=neo4j`, `NEO4J_PASSWORD=password`
4. `load_data.cypher`: the complete shared dataset cypher script.
5. `connection.py`: Neo4j driver and query helpers implementing:
   - `get_driver()`: reads `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` from `.env` and returns the Neo4j driver instance.
   - `run_query(cypher, params=None)`: runs any Cypher (read or write) and returns a list of dicts, one per row.
   - `new_id(prefix)`: returns `prefix` + 8 random uppercase characters (e.g. `T3F9A12C`).
6. `db.py`: live database implementation of all 20 functions below using Cypher.
7. `mock_db.py`: fallback mock implementation of all 20 functions returning the exact test data for offline UI/testing.
8. `app.py`: Streamlit frontend with 4 screens and sidebar toggle between `db` and `mock_db`.
9. `test_suite.py`: automated test script verifying the 47 nodes and all 20 functions against Section 8 test cases.
10. `README.md`: setup guide, schema explanation, and "Why Neo4j" demo talking points.

### R2. Exact Database Function Contracts (`db.py` & `mock_db.py`)
All dates must be formatted as strings (`YYYY-MM-DD`) using `toString(...)` in Cypher.
All write functions must wrap execution in `try...except` and return `{'success': bool, 'message': str}` (plus additional keys where specified). No function should crash the app.

**Read Functions (1-9):**
1. `get_customer(customer_id)` -> `{customer_id, name, customer_type, city, phone, email, relationship_manager}` (manager name string or `None`), or `None` if customer does not exist.
2. `get_accounts(customer_id)` -> list of dicts: `[{account_number, account_type, balance, status, branch_name}]`.
3. `get_total_balance(customer_id)` -> float/int (sum of their account balances).
4. `get_transactions(account_number)` -> list of dicts sorted by `txn_date` descending: `[{txn_id, txn_date, txn_type, amount, other_account}]`.
   - `txn_type`: `'Deposit'`, `'Withdrawal'`, `'Transfer In'`, or `'Transfer Out'`.
   - `other_account`: `None` for deposits/withdrawals; target account for `'Transfer Out'`; source account for `'Transfer In'`.
   - Use a 3-part `UNION` in Cypher and sort by `txn_date` descending in Python.
5. `get_loans(customer_id)` -> list of dicts: `[{loan_id, loan_type, amount, interest_rate, term_months, status, loan_officer, branch_name}]`.
6. `get_repayment_schedule(loan_id)` -> list of dicts: `[{installment_no, due_date, amount_due, status}]`.
7. `get_investments(customer_id)` -> list of dicts: `[{investment_id, investment_type, amount, start_date}]`.
8. `get_service_requests(customer_id)` -> list of dicts: `[{request_id, request_type, description, status, request_date, handled_by}]`.
9. `get_branches()` -> list of dicts: `[{branch_id, branch_name}]`.

**Manage Functions (10-14):**
10. `add_customer(customer_id, first_name, last_name, city, phone, email, customer_type)` -> `{'success': bool, 'message': str}`. Fails if customer ID already exists.
11. `update_customer_contact(customer_id, phone, email)` -> `{'success': bool, 'message': str}`.
12. `open_account(account_number, customer_id, branch_id, account_type, opening_balance)` -> `{'success': bool, 'message': str}`. Fails if customer or branch does not exist.
13. `close_account(account_number)` -> `{'success': bool, 'message': str}`. Deletes the account node ONLY if its balance is 0; fails otherwise.
14. `raise_service_request(customer_id, request_type, description)` -> `{'success': bool, 'message': str, 'request_id': str}`. Generates ID via `new_id('SR')`, sets date to current date, status to `'Pending'`, and assigns to Customer Service Executive `E05`.

**Process Functions (15-16):**
15. `process_transaction(account_number, txn_type, amount)` -> `txn_type` is `'Deposit'` or `'Withdrawal'`. Returns `{'success': bool, 'message': str, 'new_balance': number}`. Generates transaction ID via `new_id('T')`. Withdrawal fails if account has insufficient balance.
16. `transfer_money(from_account, to_account, amount)` -> `{'success': bool, 'message': str}`. Runs as a single atomic Cypher query updating balances and creating `TRANSFERRED_TO` with `new_id('TR')`. Fails if from_account has insufficient balance or either account does not exist.

**Analytics Functions (17-20):**
17. `get_branch_account_counts()` -> list of dicts: `[{branch_name, account_count}]`.
18. `get_top_customers_by_balance(limit=5)` -> list of dicts (highest balance first): `[{customer_id, name, total_balance}]`.
19. `get_large_transfers(min_amount)` -> list of dicts: `[{txn_id, from_account, to_account, amount, txn_date}]`.
20. `get_money_trail(account_number)` -> list of dicts: `[{trail, hops}]` where `trail` is a list of account numbers in order along `[:TRANSFERRED_TO*1..3]` and `hops` is the integer length (1 to 3).

### R3. Streamlit Application (`app.py`)
Frontend layout with sidebar mode selector ("Live Neo4j" vs "Offline Mock", defaulting to Live if `.env` connects) and 4 screens:
- **Screen 1: Customer**:
  - Customer selector / lookup displaying profile info and total balance (`get_customer`, `get_total_balance`).
  - Contact update form (`update_customer_contact`).
  - Service requests list & new request creation (`get_service_requests`, `raise_service_request`).
  - Add new customer form (`add_customer`).
- **Screen 2: Accounts and Transactions**:
  - Account cards/table for selected customer (`get_accounts`).
  - Transaction history view with formatted types (`get_transactions`).
  - Deposit & Withdrawal interface with live balance update (`process_transaction`).
  - Inter-account fund transfer interface (`transfer_money`).
  - Open new account form (`get_branches`, `open_account`) and Close zero-balance account button (`close_account`).
- **Screen 3: Loans and Investments**:
  - Customer loans list with branch and officer details (`get_loans`).
  - Repayment schedule with status pill badges (`get_repayment_schedule`).
  - Investment portfolio breakdown (`get_investments`).
- **Screen 4: Analytics**:
  - Branch account distribution chart/table (`get_branch_account_counts`).
  - Leaderboard of top customers by balance (`get_top_customers_by_balance`).
  - High-value transfer monitor (`get_large_transfers`).
  - Multi-hop fund flow / money trail tracer (`get_money_trail`).

### R4. Test Suite (`test_suite.py`)
Automated verification script validating Section 8 test cases against `mock_db` and optionally `db`:
- Verification of 47-node dataset count (3 Branch, 6 Employee, 6 Customer, 8 Account, 8 Transaction, 3 Loan, 6 Installment, 4 Investment, 3 ServiceRequest).
- `get_customer('C01')`: name 'Samridhi Sharma', type 'Premium', RM 'Priya Menon'.
- `get_accounts('C01')`: AC1001 (85000) and AC1002 (150000).
- `get_total_balance('C01')`: exactly 235000.
- `get_transactions('AC1001')`: 4 rows (Deposit 20000, Withdrawal 5000, Transfer Out 8000 to AC1003, Transfer In 2000 from AC1006).
- `get_loans('C01')`: L01 Home Loan, Divya Rao, Anna Nagar Branch.
- `get_repayment_schedule('L01')`: 3 installments (no. 3 is Pending).
- `get_investments('C01')`: I01 Mutual Fund (100000) and I03 Wealth Management (300000).
- `get_service_requests('C01')`: SR03 Cheque Book, Resolved, Karthik Suresh.
- `get_branch_account_counts()`: Anna Nagar 3, T Nagar 3, Koramangala 2.
- `get_top_customers_by_balance(3)`: C01 (235000), C03 (200000), C06 (95000).
- `get_large_transfers(20000)`: TR6 (AC1004->AC1002, 40000) and TR4 (AC1002->AC1007, 25000).
- `get_money_trail('AC1001')`: 3 rows (AC1001->AC1003, AC1001->AC1003->AC1005, AC1001->AC1003->AC1005->AC1006).
- Write operations tests:
  - `process_transaction('AC1003', 'Deposit', 5000)` -> new_balance 47000.
  - `process_transaction('AC1003', 'Withdrawal', 99999999)` -> fails (`success: False`).
  - `transfer_money('AC1001', 'AC1003', 5000)` -> succeeds (`success: True`).
  - `add_customer('C01', ...)` -> fails (duplicate ID).
  - `close_account('AC1008')` -> fails (balance != 0).
  - `open_account('AC1009', 'C02', 'BR02', 'Savings', 0)` then `close_account('AC1009')` -> both succeed.

## Acceptance Criteria

### Data & Driver Verification
- [ ] `connection.py` provides `get_driver()`, `run_query()`, and `new_id()`.
- [ ] `load_data.cypher` initializes exactly 47 nodes and unique constraints cleanly.

### Contract Integrity
- [ ] All 20 functions implemented in `db.py` and `mock_db.py` with identical parameter names and return dictionaries.
- [ ] Date attributes returned as strings (`YYYY-MM-DD`).
- [ ] Write operations caught inside `try...except` returning `{'success': bool, 'message': str}`.

### Streamlit Application
- [ ] `streamlit run app.py` launches and renders all 4 screens without error.
- [ ] Screens correctly bind to their specified subsets of the 20 functions.
- [ ] Sidebar toggle allows switching between live DB and mock DB.

### Automated Testing
- [ ] `python test_suite.py` passes 100% of the assertions for all 20 functions and Section 8 test cases.


## Follow-up — 2026-10-21T18:32:02Z

USER DIRECTIVE: "do it fast". Please accelerate execution immediately. Wrap up Milestone 3 gating, and directly produce and verify `test_suite.py` (testing 47-node count and Section 8 test cases) and `README.md` (setup instructions, architecture, and "Why Neo4j" talking points) so the user can review and run the complete project right now.
