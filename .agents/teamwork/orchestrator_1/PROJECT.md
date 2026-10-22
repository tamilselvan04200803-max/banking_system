# Project: Smart Banking Mini-Project (Neo4j & Streamlit)

## Architecture
A graph-native banking portal built with Neo4j and Streamlit providing customer relationship management, multi-account ledger processing, multi-hop fund flow tracing, and portfolio analytics.
- **Data Layer**: Neo4j graph database storing 47 nodes across 9 entity types with unique constraints and 8 `TRANSFERRED_TO` transfer edges.
- **Connection Helper (`connection.py`)**: Manages Bolt driver lifecycle via `.env`, parameterized session query execution (`run_query`), and random prefixed ID generator (`new_id`).
- **Database Abstraction**:
  - Live Database (`db.py`): Cypher queries utilizing temporal date string formatting `toString(...)`, 3-part transaction `UNION`, atomic fund transfer with balance checks, and variable-length path money trails `[:TRANSFERRED_TO*1..3]`.
  - Offline Mock Database (`mock_db.py`): In-memory Python store initialized with the exact 47-node dataset, dynamic mutation support, and `reset_mock_db()` for test idempotency.
- **Frontend Layer (`app.py`)**: Multi-screen Streamlit application with sidebar mode switcher ("Live Neo4j" vs "Offline Mock" with auto-probe fallback) spanning 4 screens covering all 20 function contracts.
- **Verification Layer (`test_suite.py`)**: Standalone and pytest-compatible test suite verifying 47-node dataset counts and all Section 8 test assertions.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Dependencies & Config | `requirements.txt`, `.gitignore`, `.env.example` | M1 | R1.1-R1.3 |
| 2 | Initialization Cypher | `load_data.cypher` with 9 constraints, 47 nodes, 8 transfers | M1 | R1.4 |
| 3 | Neo4j Connection Helpers | `connection.py` (`get_driver`, `run_query`, `new_id`) | M1 | R1.5 |
| 4 | Read: Customer Profile | `get_customer(customer_id)` | M2 | R2.1 |
| 5 | Read: Customer Accounts | `get_accounts(customer_id)` | M2 | R2.2 |
| 6 | Read: Total Balance | `get_total_balance(customer_id)` | M2 | R2.3 |
| 7 | Read: Transaction History | `get_transactions(account_number)` (3-part UNION, desc date) | M2 | R2.4 |
| 8 | Read: Customer Loans | `get_loans(customer_id)` | M2 | R2.5 |
| 9 | Read: Repayment Schedule | `get_repayment_schedule(loan_id)` | M2 | R2.6 |
| 10 | Read: Customer Investments | `get_investments(customer_id)` | M2 | R2.7 |
| 11 | Read: Service Requests | `get_service_requests(customer_id)` | M2 | R2.8 |
| 12 | Read: Bank Branches | `get_branches()` | M2 | R2.9 |
| 13 | Manage: Add Customer | `add_customer(...)` with duplicate check | M2 | R2.10 |
| 14 | Manage: Update Contact | `update_customer_contact(customer_id, phone, email)` | M2 | R2.11 |
| 15 | Manage: Open Account | `open_account(...)` linked to customer & branch | M2 | R2.12 |
| 16 | Manage: Close Account | `close_account(account_number)` conditional on balance == 0 | M2 | R2.13 |
| 17 | Manage: Raise Service Req | `raise_service_request(...)` with SR ID & CSE E05 | M2 | R2.14 |
| 18 | Process: Deposit/Withdrawal | `process_transaction(...)` with new_balance | M2 | R2.15 |
| 19 | Process: Atomic Transfer | `transfer_money(from, to, amount)` atomic Cypher/mock | M2 | R2.16 |
| 20 | Analytics: Branch Counts | `get_branch_account_counts()` | M2 | R2.17 |
| 21 | Analytics: Top Customers | `get_top_customers_by_balance(limit=5)` | M2 | R2.18 |
| 22 | Analytics: Large Transfers | `get_large_transfers(min_amount)` | M2 | R2.19 |
| 23 | Analytics: Money Trail | `get_money_trail(account_number)` 1..3 hops | M2 | R2.20 |
| 24 | Offline Mock Implementation | `mock_db.py` covering all 20 functions + state reset | M2 | R1.7, R2 |
| 25 | UI: Sidebar & Mode Switch | Auto-probing toggle ("Live Neo4j" vs "Offline Mock") | M3 | R3 |
| 26 | UI: Screen 1 (Customer) | Customer profile, total balance, contact edit, SRs, new customer | M3 | R3 |
| 27 | UI: Screen 2 (Accounts/Txns)| Account cards, txn history, deposit/withdraw, transfer, open/close | M3 | R3 |
| 28 | UI: Screen 3 (Loans/Invest) | Loans with officer/branch, repayment status pills, investments | M3 | R3 |
| 29 | UI: Screen 4 (Analytics) | Branch distribution, wealth leaderboard, large transfers, money trail | M3 | R3 |
| 30 | Test Suite: Node Counts | Automated verification of 47-node dataset count | M4 | R4 |
| 31 | Test Suite: Contract Tests | Automated verification of 20 functions & Section 8 test cases | M4 | R4 |
| 32 | Project Documentation | `README.md` setup, schema explanation, why Neo4j talking points | M5 | R1.10 |
| 33 | Final E2E Gate & Audit | 100% pass of test suite and forensic integrity verification | M6 | Final |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Infrastructure & Schema | `requirements.txt`, `.gitignore`, `.env.example`, `load_data.cypher`, `connection.py` | none | DONE |
| M2 | Database Contracts | `mock_db.py` and `db.py` (20 functions with exact signatures) | M1 | DONE |
| M3 | Streamlit Application | `app.py` (4 screens + sidebar mode switcher) | M2 | DONE |
| M4 | Automated Test Suite | `test_suite.py` (47 nodes + 20 function assertions) | M2 | DONE |
| M5 | Documentation | `README.md` (architecture, schema, Neo4j talking points) | M3, M4 | DONE |
| M6 | Final E2E Pass & Forensic Audit | Complete verification across all tiers and integrity audit | M1-M5 | IN_PROGRESS |

## Interface Contracts

### `connection.py`
- `get_driver() -> neo4j.Driver`: reads credentials from `.env`, raises or handles if unreachable.
- `run_query(cypher: str, params: dict = None) -> list[dict]`: executes query and returns list of dictionaries.
- `new_id(prefix: str) -> str`: prefix + 8 uppercase alphanumeric characters.

### `db.py` & `mock_db.py` (20 Functions)
All date values returned formatted as string `'YYYY-MM-DD'`.
All mutating functions return `{'success': bool, 'message': str, ...}` and never crash.

1. `get_customer(customer_id: str) -> dict | None`: `{customer_id, name, customer_type, city, phone, email, relationship_manager}`
2. `get_accounts(customer_id: str) -> list[dict]`: `[{account_number, account_type, balance, status, branch_name}]`
3. `get_total_balance(customer_id: str) -> float | int`: numeric sum of balances
4. `get_transactions(account_number: str) -> list[dict]`: `[{txn_id, txn_date, txn_type, amount, other_account}]` (descending by `txn_date`)
5. `get_loans(customer_id: str) -> list[dict]`: `[{loan_id, loan_type, amount, interest_rate, term_months, status, loan_officer, branch_name}]`
6. `get_repayment_schedule(loan_id: str) -> list[dict]`: `[{installment_no, due_date, amount_due, status}]`
7. `get_investments(customer_id: str) -> list[dict]`: `[{investment_id, investment_type, amount, start_date}]`
8. `get_service_requests(customer_id: str) -> list[dict]`: `[{request_id, request_type, description, status, request_date, handled_by}]`
9. `get_branches() -> list[dict]`: `[{branch_id, branch_name}]`
10. `add_customer(customer_id: str, first_name: str, last_name: str, city: str, phone: str, email: str, customer_type: str) -> dict`: `{'success': bool, 'message': str}`
11. `update_customer_contact(customer_id: str, phone: str, email: str) -> dict`: `{'success': bool, 'message': str}`
12. `open_account(account_number: str, customer_id: str, branch_id: str, account_type: str, opening_balance: float | int) -> dict`: `{'success': bool, 'message': str}`
13. `close_account(account_number: str) -> dict`: `{'success': bool, 'message': str}` (succeeds only if balance == 0)
14. `raise_service_request(customer_id: str, request_type: str, description: str) -> dict`: `{'success': bool, 'message': str, 'request_id': str}`
15. `process_transaction(account_number: str, txn_type: str, amount: float | int) -> dict`: `{'success': bool, 'message': str, 'new_balance': float | int}`
16. `transfer_money(from_account: str, to_account: str, amount: float | int) -> dict`: `{'success': bool, 'message': str}`
17. `get_branch_account_counts() -> list[dict]`: `[{branch_name, account_count}]`
18. `get_top_customers_by_balance(limit: int = 5) -> list[dict]`: `[{customer_id, name, total_balance}]`
19. `get_large_transfers(min_amount: float | int) -> list[dict]`: `[{txn_id, from_account, to_account, amount, txn_date}]`
20. `get_money_trail(account_number: str) -> list[dict]`: `[{trail: list[str], hops: int}]`

## Code Layout
```
c:\dbms_da-3-project\
├── .env.example            # Environment template [CREATED]
├── .gitignore              # Git ignore rules [CREATED]
├── requirements.txt        # Python dependencies [CREATED]
├── load_data.cypher        # Neo4j shared dataset (47 nodes, 9 constraints, 8 transfers) [CREATED]
├── connection.py           # Neo4j driver, run_query, new_id [CREATED]
├── db.py                   # Live Cypher implementation of 20 functions [CREATED]
├── mock_db.py              # Offline in-memory mock implementation of 20 functions [CREATED]
├── app.py                  # Streamlit application (4 screens + sidebar toggle)
├── test_suite.py           # Automated test suite (standalone + pytest)
└── README.md               # Setup guide, schema docs, Neo4j talking points
```
