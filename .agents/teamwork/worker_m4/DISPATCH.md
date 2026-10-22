# DISPATCH

## 2026-10-21T18:34:18Z
You are teamwork_preview_worker for Milestone 4: Test Suite Implementation (`test_suite.py`).
Your working directory is `c:\dbms_da-3-project\.agents\teamwork\worker_m4\`.
Read `c:\dbms_da-3-project\.agents\teamwork\ORIGINAL_REQUEST.md` (specifically Section R4, Section 8, and Acceptance Criteria).
Also read:
- `c:\dbms_da-3-project\.agents\teamwork\orchestrator_1\PROJECT.md`
- `c:\dbms_da-3-project\mock_db.py`
- `c:\dbms_da-3-project\db.py`

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Write Ownership (You exclusively own and create this file in `c:\dbms_da-3-project`):
- `c:\dbms_da-3-project\test_suite.py`

Your tasks:
Create `c:\dbms_da-3-project\test_suite.py`:
1. Use standard Python `unittest` test classes (compatible with both `python test_suite.py` and `pytest test_suite.py -v`).
2. Provide `setUp()` calling `mock_db.reset_mock_db()` before every test method to guarantee 100% test isolation.
3. Implement test cases covering all requirements from Section R4 & Section 8 of `ORIGINAL_REQUEST.md`:
   - Test 1: 47-Node Dataset Counts:
     - 3 Branches (BR01, BR02, BR03 via `mock_db.get_branches()`)
     - 6 Employees (E01-E06 via mock dataset)
     - 6 Customers (C01-C06 via `mock_db.get_customer`)
     - 8 Accounts (AC1001-AC1008 across all customers via `mock_db.get_accounts`)
     - 8 Transactions (T1-T8 across accounts via `mock_db.get_transactions`)
     - 8 Transfers (TR1-TR8 via `mock_db.get_large_transfers(0)`)
     - 3 Loans (L01-L03 via `mock_db.get_loans`)
     - 6 Installments (across loans via `mock_db.get_repayment_schedule`)
     - 4 Investments (I01-I04 across customers via `mock_db.get_investments`)
     - 3 Service Requests (SR01-SR03 via `mock_db.get_service_requests`)
     - Assert total node count equals 47.
   - Test 2: Read Functions (1-9):
     - `get_customer('C01')`: name 'Samridhi Sharma', customer_type 'Premium', relationship_manager 'Priya Menon'. Non-existent customer returns `None`.
     - `get_accounts('C01')`: exactly 2 accounts: AC1001 (balance 85000) and AC1002 (balance 150000).
     - `get_total_balance('C01')`: exactly 235000.
     - `get_transactions('AC1001')`: 4 rows sorted desc by `txn_date` (Deposit 20000, Withdrawal 5000, Transfer Out 8000 to AC1003, Transfer In 2000 from AC1006).
     - `get_loans('C01')`: L01 Home Loan, loan officer Divya Rao, branch Anna Nagar.
     - `get_repayment_schedule('L01')`: 3 installments (installment 3 is 'Pending', 1 and 2 are 'Paid').
     - `get_investments('C01')`: I01 Mutual Fund (100000) and I03 Wealth Management (300000).
     - `get_service_requests('C01')`: SR03 Cheque Book, status 'Resolved', handled_by 'Karthik Suresh'.
     - `get_branches()`: 3 branches.
   - Test 3: Manage Functions (10-14):
     - `add_customer('C01', ...)` fails with `success: False` (duplicate ID). Adding new customer `C07` succeeds and can be retrieved.
     - `update_customer_contact('C01', phone='9876543210', email='samridhi.new@email.com')` succeeds and updates customer data.
     - `open_account('AC1009', 'C02', 'BR02', 'Savings', 5000)` succeeds and reflects in `get_accounts('C02')`. Fails for invalid customer/branch.
     - `close_account('AC1008')` fails because balance is 75000 (!= 0). Opening zero-balance account `AC1010` and closing it succeeds.
     - `raise_service_request('C01', 'Card', 'New debit card')` succeeds, generates ID with 'SR' prefix, status 'Pending', assigned to 'E05'.
   - Test 4: Process Functions (15-16):
     - `process_transaction('AC1003', 'Deposit', 5000)` -> `success: True`, `new_balance: 47000`.
     - `process_transaction('AC1003', 'Withdrawal', 99999999)` -> fails (`success: False`).
     - `transfer_money('AC1001', 'AC1003', 5000)` -> `success: True`, AC1001 balance becomes 80000, AC1003 balance becomes 47000 (from 42000). Fails if balance insufficient.
   - Test 5: Analytics Functions (17-20):
     - `get_branch_account_counts()`: Anna Nagar 3, T Nagar 3, Koramangala 2.
     - `get_top_customers_by_balance(3)`: C01 (235000), C03 (200000), C06 (95000).
     - `get_large_transfers(20000)`: exactly TR6 (AC1004->AC1002, 40000) and TR4 (AC1002->AC1007, 25000).
     - `get_money_trail('AC1001')`: exactly 3 rows with trails `['AC1001', 'AC1003']` (1 hop), `['AC1001', 'AC1003', 'AC1005']` (2 hops), `['AC1001', 'AC1003', 'AC1005', 'AC1006']` (3 hops).
   - Test 6: Date Format & Error Handling:
     - Verify all dates in transactions, schedules, investments, and service requests match `YYYY-MM-DD`.
     - Verify write functions catch exceptions and return `{'success': bool, 'message': str}`.
4. Validation:
   - Bytecode compile: `python -m py_compile test_suite.py`.
   - Run test suite: `python test_suite.py` and verify all tests pass with 0 failures, 0 errors.
   - Run with pytest if available: `pytest test_suite.py -v`.
5. Write handoff report to `c:\dbms_da-3-project\.agents\teamwork\worker_m4\handoff.md`.
6. Notify caller via `send_message`.
