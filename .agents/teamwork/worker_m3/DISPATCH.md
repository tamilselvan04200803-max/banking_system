## 2026-10-21T16:49:43Z
You are teamwork_preview_worker for Milestone 3: Streamlit Application (app.py).
Your working directory is `c:\dbms_da-3-project\.agents\teamwork\worker_m3\`.
Read `c:\dbms_da-3-project\.agents\teamwork\ORIGINAL_REQUEST.md`.
Also read:
- `c:\dbms_da-3-project\.agents\teamwork\orchestrator_1\PROJECT.md`
- `c:\dbms_da-3-project\.agents\teamwork\explorer_ui_and_tests\handoff.md`
- `c:\dbms_da-3-project\mock_db.py`
- `c:\dbms_da-3-project\db.py`

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Write Ownership (You exclusively own and create this file in `c:\dbms_da-3-project`):
- `c:\dbms_da-3-project\app.py`

Your tasks:
Build the complete, production-ready Streamlit application in `app.py`:
1. Sidebar & Backend Mode Switcher:
   - Radio or selectbox: "Live Neo4j" vs "Offline Mock".
   - Auto-detection: probe connection via `db.get_branches()`; if successful default to "Live Neo4j", otherwise default to "Offline Mock" with status badge (`🟢 Neo4j Database: Connected` or `🟡 Running in Offline Mock Mode`).
   - Store active backend in `backend = db if mode == "Live Neo4j" else mock_db`.
   - Global Customer Selector dropdown (`C01` to `C06`), defaulted to `C01`, stored in `st.session_state`.
   - Navigation radio across 4 screens.

2. Screen 1: Customer Profile & Services:
   - Profile banner: Name, Customer Type badge, City, Phone, Email, Relationship Manager via `backend.get_customer(customer_id)`.
   - Total Balance KPI metric via `backend.get_total_balance(customer_id)`.
   - Contact update form (phone, email) via `backend.update_customer_contact`.
   - Service requests list with status pill badges via `backend.get_service_requests`.
   - Raise service request form (type, description) via `backend.raise_service_request`.
   - Add new customer form (ID, first name, last name, city, phone, email, type) via `backend.add_customer`.

3. Screen 2: Accounts & Transactions:
   - Customer accounts table / cards (Account #, Type, Balance, Status, Branch) via `backend.get_accounts`.
   - Account selector for transactions.
   - Transaction history table with formatted types (Deposit, Withdrawal, Transfer In, Transfer Out), counterparty account, descending by date via `backend.get_transactions`.
   - Deposit & Withdrawal form with amount and live balance update via `backend.process_transaction`.
   - Fund transfer form (source, target, amount) via `backend.transfer_money`.
   - Open new account form (branch selector via `backend.get_branches`, account type, opening balance) via `backend.open_account`.
   - Close zero-balance account button with warning alert via `backend.close_account`.

4. Screen 3: Loans & Investments:
   - Customer loans cards/table (Loan ID, Type, Amount, Interest Rate, Term, Status, Loan Officer, Branch) via `backend.get_loans`.
   - Repayment schedule with status pill badges (Paid, Pending, Overdue) via `backend.get_repayment_schedule`.
   - Investment portfolio breakdown table and metric via `backend.get_investments`.

5. Screen 4: Analytics & Graph Intelligence:
   - Branch account distribution chart (`st.bar_chart`) and table via `backend.get_branch_account_counts`.
   - Wealth leaderboard of top customers by total balance (with Top N slider) via `backend.get_top_customers_by_balance`.
   - High-value transfer monitor with threshold input (default 20,000) via `backend.get_large_transfers`.
   - Multi-hop fund flow / money trail tracer (e.g. `AC1001`) rendering interactive hop sequence (`AC1001 ➔ AC1003 ➔ AC1005 (2 hops)`) via `backend.get_money_trail`.

6. Visual Polish & Robustness:
   - Use clean card containers, KPI metric blocks, badges, and alerts.
   - All mutation actions inspect `res['success']` and display `st.success(res['message'])` or `st.error(res['message'])`.
   - Clean empty states for users with no loans, investments, or service requests.
   - Never crash the application under any error condition.

7. Validation:
   - Bytecode compilation: `python -m py_compile app.py`.
   - Test headless launch or smoke test script.

8. Write handoff report to `c:\dbms_da-3-project\.agents\teamwork\worker_m3\handoff.md`.
9. Notify caller via `send_message`.
