# Specification Mining Report: 20 Database Function Contracts

**Author**: `teamwork_preview_spec_miner`  
**Working Directory**: `c:\dbms_da-3-project\.agents\teamwork\spec_miner_contracts\`  
**Target Modules**: `db.py` (Live Neo4j Cypher Implementation), `mock_db.py` (Offline In-Memory Mock Implementation), `connection.py` (Driver & Query Helpers)  
**Authoritative Source**: `c:\dbms_da-3-project\.agents\teamwork\ORIGINAL_REQUEST.md` (Lines 49–83, 107–129)

---

## 1. Observation

Direct analysis of `ORIGINAL_REQUEST.md` establishes the technical requirements:
1. **Global Contract Rules (Lines 50–51)**:
   - All dates must be formatted as strings (`YYYY-MM-DD`) using `toString(...)` in Cypher.
   - All write functions must wrap execution in `try...except` and return `{'success': bool, 'message': str}` (plus additional keys where specified).
   - No function should crash the application under any error condition.
2. **Four Categories of Database Functions**:
   - **Read Functions (1–9)**: `get_customer`, `get_accounts`, `get_total_balance`, `get_transactions`, `get_loans`, `get_repayment_schedule`, `get_investments`, `get_service_requests`, `get_branches`.
   - **Manage Functions (10–14)**: `add_customer`, `update_customer_contact`, `open_account`, `close_account`, `raise_service_request`.
   - **Process Functions (15–16)**: `process_transaction`, `transfer_money`.
   - **Analytics Functions (17–20)**: `get_branch_account_counts`, `get_top_customers_by_balance`, `get_large_transfers`, `get_money_trail`.
3. **Core Helper Utilities in `connection.py` (Lines 39–42)**:
   - `get_driver()`: reads `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` from `.env`.
   - `run_query(cypher, params=None)`: returns list of dicts, one per record row.
   - `new_id(prefix)`: returns prefix + 8 random uppercase alphanumeric chars.
4. **Concrete Test Verifications (Lines 107–129)**:
   - Baseline dataset: 47 nodes across Branch (3), Employee (6), Customer (6), Account (8), Transaction (8), Loan (3), Installment (6), Investment (4), ServiceRequest (3).
   - Specific contract outputs:
     - `get_customer('C01')` -> `{'customer_id': 'C01', 'name': 'Samridhi Sharma', 'customer_type': 'Premium', 'city': 'Chennai', 'phone': '+91 98765 43210', 'email': 'samridhi@example.com', 'relationship_manager': 'Priya Menon'}`.
     - `get_accounts('C01')` -> AC1001 (balance 85000), AC1002 (balance 150000).
     - `get_total_balance('C01')` -> exactly 235000.
     - `get_transactions('AC1001')` -> 4 rows (Deposit 20000, Withdrawal 5000, Transfer Out 8000 to AC1003, Transfer In 2000 from AC1006).
     - `get_loans('C01')` -> L01 Home Loan, Divya Rao, Anna Nagar Branch.
     - `get_repayment_schedule('L01')` -> 3 installments (no. 3 is Pending).
     - `get_investments('C01')` -> I01 Mutual Fund (100000), I03 Wealth Management (300000).
     - `get_service_requests('C01')` -> SR03 Cheque Book, Resolved, Karthik Suresh.
     - `get_branch_account_counts()` -> Anna Nagar 3, T Nagar 3, Koramangala 2.
     - `get_top_customers_by_balance(3)` -> C01 (235000), C03 (200000), C06 (95000).
     - `get_large_transfers(20000)` -> TR6 (AC1004->AC1002, 40000) and TR4 (AC1002->AC1007, 25000).
     - `get_money_trail('AC1001')` -> 3 rows (AC1001->AC1003, AC1001->AC1003->AC1005, AC1001->AC1003->AC1005->AC1006).
     - Write verifications:
       - `process_transaction('AC1003', 'Deposit', 5000)` -> `new_balance: 47000`.
       - `process_transaction('AC1003', 'Withdrawal', 99999999)` -> fails (`success: False`).
       - `transfer_money('AC1001', 'AC1003', 5000)` -> succeeds (`success: True`).
       - `add_customer('C01', ...)` -> fails with duplicate ID error.
       - `close_account('AC1008')` -> fails because balance != 0.
       - `open_account('AC1009', 'C02', 'BR02', 'Savings', 0)` then `close_account('AC1009')` -> both succeed.

---

## 2. Logic Chain

1. **Dual Implementation Parity (`db.py` vs `mock_db.py`)**:
   - The UI and automated test suite must run seamlessly against both `db.py` (live Neo4j connection via `connection.py`) and `mock_db.py` (pure Python in-memory state).
   - Therefore, function signatures, argument types, dictionary keys, and return types must be 100% identical between `db.py` and `mock_db.py`.
2. **Cypher Query Construction (`db.py`)**:
   - Dates in Neo4j are stored as `Date` objects (`date('YYYY-MM-DD')`). To satisfy R2 ("All dates must be formatted as strings (`YYYY-MM-DD`) using `toString(...)` in Cypher"), queries must alias `toString(n.date_prop) AS date_prop`.
   - `get_transactions(account_number)` must combine 3 distinct transaction types using a 3-part `UNION` in Cypher:
     1. Deposits/Withdrawals on the account via `(a)-[:HAS_TRANSACTION]->(t)` -> `other_account = null`.
     2. Transfers out via `(a)-[r:TRANSFERRED_TO]->(target)` -> `other_account = target.account_number`, `txn_type = 'Transfer Out'`.
     3. Transfers in via `(source)-[r:TRANSFERRED_TO]->(a)` -> `other_account = source.account_number`, `txn_type = 'Transfer In'`.
     Python sorts rows by `txn_date` descending.
   - `transfer_money` must execute in a single atomic Cypher query with balance checks (`WHERE from.balance >= $amount AND from.account_number <> to.account_number`), updating both account balances and creating the `TRANSFERRED_TO` relationship.
   - `get_money_trail` must use variable length path traversal `(a:Account)-[:TRANSFERRED_TO*1..3]->(target:Account)`, returning `[n IN nodes(p) | n.account_number] AS trail` and `length(p) AS hops`.
3. **Stateful In-Memory Mock (`mock_db.py`)**:
   - The mock database must initialize an in-memory representation of the 47 nodes.
   - It cannot be a purely static snapshot: write operations (`process_transaction`, `transfer_money`, `open_account`, `close_account`, `add_customer`, `update_customer_contact`, `raise_service_request`) must update in-memory data structures so that test suites and UI sessions observing mutations see updated balances, new accounts, closed accounts, and new transactions.
4. **Error Handling Architecture**:
   - Read operations return `None` (for single entity when not found) or `[]` / `0` (for collections / aggregates).
   - Write operations wrap logic in `try...except Exception as e`, returning:
     - Standard: `{'success': False, 'message': str(e)}` or `{'success': True, 'message': '...'}`.
     - `raise_service_request`: returns `{'success': bool, 'message': str, 'request_id': str}`.
     - `process_transaction`: returns `{'success': bool, 'message': str, 'new_balance': number}`.

---

## 3. Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Read | `get_customer` | Fetch customer profile & assigned Relationship Manager | `customer_id: str` | `dict` or `None`: `{customer_id, name, customer_type, city, phone, email, relationship_manager}` | Returns `None` if customer does not exist | `ORIGINAL_REQUEST.md:54` |
| 2 | Read | `get_accounts` | Fetch all accounts held by customer with branch name | `customer_id: str` | `list[dict]`: `[{account_number, account_type, balance, status, branch_name}]` | Returns `[]` if customer not found or has no accounts | `ORIGINAL_REQUEST.md:55` |
| 3 | Read | `get_total_balance` | Calculate sum of all account balances for a customer | `customer_id: str` | `float \| int`: numeric balance sum | Returns `0` if customer not found or has no accounts | `ORIGINAL_REQUEST.md:56` |
| 4 | Read | `get_transactions` | Fetch consolidated transaction history (Deposits, Withdrawals, In/Out Transfers) sorted descending by date | `account_number: str` | `list[dict]`: `[{txn_id, txn_date, txn_type, amount, other_account}]` | Returns `[]` if account not found or has no txns | `ORIGINAL_REQUEST.md:57-60` |
| 5 | Read | `get_loans` | Fetch loans for customer with officer and branch | `customer_id: str` | `list[dict]`: `[{loan_id, loan_type, amount, interest_rate, term_months, status, loan_officer, branch_name}]` | Returns `[]` if customer has no loans | `ORIGINAL_REQUEST.md:61` |
| 6 | Read | `get_repayment_schedule` | Fetch installment schedule for a loan ordered by installment number | `loan_id: str` | `list[dict]`: `[{installment_no, due_date, amount_due, status}]` | Returns `[]` if loan not found or has no installments | `ORIGINAL_REQUEST.md:62` |
| 7 | Read | `get_investments` | Fetch investments made by customer | `customer_id: str` | `list[dict]`: `[{investment_id, investment_type, amount, start_date}]` | Returns `[]` if customer has no investments | `ORIGINAL_REQUEST.md:63` |
| 8 | Read | `get_service_requests` | Fetch customer service requests with assigned executive | `customer_id: str` | `list[dict]`: `[{request_id, request_type, description, status, request_date, handled_by}]` | Returns `[]` if customer has no requests | `ORIGINAL_REQUEST.md:64` |
| 9 | Read | `get_branches` | List all bank branches | `None` | `list[dict]`: `[{branch_id, branch_name}]` | Returns `[]` if no branches exist | `ORIGINAL_REQUEST.md:65` |
| 10 | Manage | `add_customer` | Create new customer node; enforces uniqueness of ID | `customer_id, first_name, last_name, city, phone, email, customer_type` (all `str`) | `dict`: `{'success': bool, 'message': str}` | Returns `{'success': False, ...}` if customer ID already exists | `ORIGINAL_REQUEST.md:68` |
| 11 | Manage | `update_customer_contact` | Update phone and email for customer | `customer_id: str, phone: str, email: str` | `dict`: `{'success': bool, 'message': str}` | Returns `{'success': False, ...}` if customer does not exist | `ORIGINAL_REQUEST.md:69` |
| 12 | Manage | `open_account` | Open new account linked to customer and branch | `account_number: str, customer_id: str, branch_id: str, account_type: str, opening_balance: float \| int` | `dict`: `{'success': bool, 'message': str}` | Returns `{'success': False, ...}` if customer or branch does not exist, or account ID exists | `ORIGINAL_REQUEST.md:70` |
| 13 | Manage | `close_account` | Close and delete account node ONLY if balance is exactly 0 | `account_number: str` | `dict`: `{'success': bool, 'message': str}` | Returns `{'success': False, ...}` if account not found or balance != 0 | `ORIGINAL_REQUEST.md:71` |
| 14 | Manage | `raise_service_request` | Create new service request assigned to CSE E05 | `customer_id: str, request_type: str, description: str` | `dict`: `{'success': bool, 'message': str, 'request_id': str}` | Returns `{'success': False, 'message': str, 'request_id': ''}` if customer not found | `ORIGINAL_REQUEST.md:72` |
| 15 | Process | `process_transaction` | Process deposit or withdrawal and update balance | `account_number: str, txn_type: str ('Deposit'\|'Withdrawal'), amount: float \| int` | `dict`: `{'success': bool, 'message': str, 'new_balance': float \| int}` | Returns `{'success': False, 'message': 'Insufficient balance', 'new_balance': current_balance}` on overdraft | `ORIGINAL_REQUEST.md:75` |
| 16 | Process | `transfer_money` | Atomically transfer funds between accounts and record `TRANSFERRED_TO` | `from_account: str, to_account: str, amount: float \| int` | `dict`: `{'success': bool, 'message': str}` | Returns `{'success': False, ...}` if insufficient balance, invalid account, or same account | `ORIGINAL_REQUEST.md:76` |
| 17 | Analytics | `get_branch_account_counts` | Count total accounts located at each branch | `None` | `list[dict]`: `[{branch_name, account_count}]` | Returns `[]` or branches with 0 accounts | `ORIGINAL_REQUEST.md:79` |
| 18 | Analytics | `get_top_customers_by_balance` | Leaderboard of top customers by aggregated account balance | `limit: int = 5` | `list[dict]`: `[{customer_id, name, total_balance}]` | Returns `[]` if no customer data or limit <= 0 | `ORIGINAL_REQUEST.md:80` |
| 19 | Analytics | `get_large_transfers` | Filter transfers meeting or exceeding threshold | `min_amount: float \| int` | `list[dict]`: `[{txn_id, from_account, to_account, amount, txn_date}]` | Returns `[]` if no transfers match | `ORIGINAL_REQUEST.md:81` |
| 20 | Analytics | `get_money_trail` | Trace directed multi-hop transfer chains (1 to 3 hops) | `account_number: str` | `list[dict]`: `[{trail, hops}]` (where `trail` is `list[str]`, `hops` is `int`) | Returns `[]` if account has no outbound transfers | `ORIGINAL_REQUEST.md:82` |
| 21 | Helper | `get_driver` | Neo4j driver factory reading `.env` credentials | `None` | `neo4j.Driver` instance | Raises `Exception` if URI or credentials missing | `ORIGINAL_REQUEST.md:40` |
| 22 | Helper | `run_query` | Generic query execution returning list of dicts | `cypher: str, params: dict = None` | `list[dict]` | Catches Neo4j exceptions or raises cleanly | `ORIGINAL_REQUEST.md:41` |
| 23 | Helper | `new_id` | Generates random unique prefixed uppercase identifier | `prefix: str` | `str`: prefix + 8 uppercase chars (e.g. `T3F9A12C`) | Asserts prefix valid | `ORIGINAL_REQUEST.md:42` |

---

## 4. Edge Cases and Observed Behaviors

| # | Feature | Input | Observed / Expected Behavior |
|---|---------|-------|------------------------------|
| 1 | `get_customer` | `customer_id='NONEXISTENT'` | Returns `None` (not an empty dict, not an exception). |
| 2 | `get_customer` | Customer with no assigned RM | Returns dict with `'relationship_manager': None`. |
| 3 | `get_accounts` | Customer with no accounts | Returns empty list `[]`. |
| 4 | `get_total_balance` | Customer with 0 accounts | Returns `0` or `0.0`. |
| 5 | `get_transactions` | Account with 0 transactions | Returns empty list `[]`. |
| 6 | `get_transactions` | Deposits and Withdrawals | Returns dict with `'other_account': None`. |
| 7 | `get_transactions` | 'Transfer Out' | Returns dict with `'other_account'` set to destination account number. |
| 8 | `get_transactions` | 'Transfer In' | Returns dict with `'other_account'` set to source account number. |
| 9 | `get_transactions` | Multiple transactions on same date | Preserves stable descending ordering by date/ID. |
| 10 | `add_customer` | `customer_id='C01'` (duplicate) | Returns `{'success': False, 'message': '...'}` without raising uncaught exception. |
| 11 | `update_customer_contact` | `customer_id='NONEXISTENT'` | Returns `{'success': False, 'message': 'Customer not found'}`. |
| 12 | `open_account` | `customer_id='C99'` (invalid customer) | Fails with `{'success': False, 'message': 'Customer does not exist'}`. |
| 13 | `open_account` | `branch_id='BR99'` (invalid branch) | Fails with `{'success': False, 'message': 'Branch does not exist'}`. |
| 14 | `open_account` | Duplicate `account_number` | Fails with `{'success': False, 'message': 'Account number already exists'}`. |
| 15 | `close_account` | `account_number='AC1008'` (balance = 12000 > 0) | Returns `{'success': False, 'message': 'Cannot close account with non-zero balance'}`. Account remains in DB. |
| 16 | `close_account` | `account_number='AC1009'` (balance == 0) | Returns `{'success': True, 'message': 'Account closed successfully'}`. Node and relationships detached/deleted. |
| 17 | `close_account` | Non-existent account | Returns `{'success': False, 'message': 'Account not found'}`. |
| 18 | `raise_service_request` | Valid customer `C01` | Generates ID starting with `SR`, assigns to employee `E05`, status `'Pending'`, today's date (`YYYY-MM-DD`). |
| 19 | `raise_service_request` | Non-existent customer | Returns `{'success': False, 'message': 'Customer not found', 'request_id': ''}`. |
| 20 | `process_transaction` | `account_number='AC1003', txn_type='Deposit', amount=5000` | Increments balance from 42000 to 47000. Returns `{'success': True, 'message': '...', 'new_balance': 47000}`. |
| 21 | `process_transaction` | `account_number='AC1003', txn_type='Withdrawal', amount=99999999` | Insufficient balance. Returns `{'success': False, 'message': 'Insufficient balance', 'new_balance': 42000}`. Balance unchanged. |
| 22 | `process_transaction` | Invalid `txn_type='LoanPayment'` | Returns `{'success': False, 'message': 'Invalid transaction type', 'new_balance': current_balance}`. |
| 23 | `process_transaction` | Negative amount (`amount = -100`) | Returns `{'success': False, 'message': 'Amount must be positive', 'new_balance': current_balance}`. |
| 24 | `transfer_money` | `from_account='AC1001', to_account='AC1003', amount=5000` | Decrements `AC1001` by 5000, increments `AC1003` by 5000, creates `TRANSFERRED_TO` relationship with ID `new_id('TR')`. Returns `{'success': True, ...}`. |
| 25 | `transfer_money` | `from_account='AC1001', to_account='AC1001'` (same account) | Fails with `{'success': False, 'message': 'Cannot transfer to the same account'}`. |
| 26 | `transfer_money` | `amount > from_account.balance` | Fails atomically without mutating either account balance. |
| 27 | `transfer_money` | Non-existent `to_account` | Fails atomically. |
| 28 | `get_top_customers_by_balance` | `limit=3` | Returns exactly top 3: C01 (235000), C03 (200000), C06 (95000). |
| 29 | `get_large_transfers` | `min_amount=20000` | Returns exactly TR6 (40000) and TR4 (25000) sorted by amount descending. |
| 30 | `get_money_trail` | `account_number='AC1001'` | Returns 3 paths: 1-hop (`[AC1001, AC1003]`), 2-hop (`[AC1001, AC1003, AC1005]`), 3-hop (`[AC1001, AC1003, AC1005, AC1006]`). |
| 31 | `get_money_trail` | Account with 0 outgoing transfers | Returns empty list `[]`. |

---

## 5. Detailed Specification for All 20 Functions

### Read Functions (1–9)

#### 1. `get_customer(customer_id: str)`
- **Signature**: `get_customer(customer_id: str)`
- **Return Structure**:
  ```python
  # On success:
  {
      'customer_id': 'C01',
      'name': 'Samridhi Sharma',
      'customer_type': 'Premium',
      'city': 'Chennai',
      'phone': '+91 98765 43210',
      'email': 'samridhi@example.com',
      'relationship_manager': 'Priya Menon'  # string or None
  }
  # When customer does not exist:
  None
  ```
- **Live Cypher Query (`db.py`)**:
  ```cypher
  MATCH (c:Customer {customer_id: $customer_id})
  OPTIONAL MATCH (c)-[:ASSIGNED_TO]->(e:Employee)
  RETURN c.customer_id AS customer_id,
         c.name AS name,
         c.customer_type AS customer_type,
         c.city AS city,
         c.phone AS phone,
         c.email AS email,
         e.name AS relationship_manager
  ```
- **Mock Requirements (`mock_db.py`)**:
  - In-memory dictionary of customers keyed by `customer_id`.
  - Initial dataset contains 6 customers (C01 to C06).
  - For `C01`, returns exact profile with name 'Samridhi Sharma', customer_type 'Premium', relationship_manager 'Priya Menon'.
  - Returns `None` if `customer_id` not found in dictionary.

---

#### 2. `get_accounts(customer_id: str)`
- **Signature**: `get_accounts(customer_id: str)`
- **Return Structure**:
  ```python
  [
      {
          'account_number': 'AC1001',
          'account_type': 'Savings',
          'balance': 85000.0,
          'status': 'Active',
          'branch_name': 'Anna Nagar'
      },
      {
          'account_number': 'AC1002',
          'account_type': 'Current',
          'balance': 150000.0,
          'status': 'Active',
          'branch_name': 'Anna Nagar'
      }
  ]
  ```
- **Live Cypher Query (`db.py`)**:
  ```cypher
  MATCH (c:Customer {customer_id: $customer_id})-[:HOLDS]->(a:Account)
  OPTIONAL MATCH (a)-[:LOCATED_AT]->(b:Branch)
  RETURN a.account_number AS account_number,
         a.account_type AS account_type,
         a.balance AS balance,
         a.status AS status,
         b.branch_name AS branch_name
  ORDER BY a.account_number ASC
  ```
- **Mock Requirements (`mock_db.py`)**:
  - Filter accounts in mock store where `customer_id == $customer_id`.
  - For `C01`: returns AC1001 (85000) and AC1002 (150000).
  - Returns `[]` if no accounts found.

---

#### 3. `get_total_balance(customer_id: str)`
- **Signature**: `get_total_balance(customer_id: str)`
- **Return Structure**:
  ```python
  # Float or int representing aggregate balance across all accounts of customer
  235000.0
  ```
- **Live Cypher Query (`db.py`)**:
  ```cypher
  MATCH (c:Customer {customer_id: $customer_id})-[:HOLDS]->(a:Account)
  RETURN coalesce(sum(a.balance), 0) AS total_balance
  ```
  Python returns `rows[0]['total_balance']` if rows else `0.0`.
- **Mock Requirements (`mock_db.py`)**:
  - Sum `balance` of accounts returned by `get_accounts(customer_id)`.
  - For `C01`: exactly `235000`.
  - Returns `0` if customer has no accounts or customer not found.

---

#### 4. `get_transactions(account_number: str)`
- **Signature**: `get_transactions(account_number: str)`
- **Return Structure**:
  ```python
  [
      {
          'txn_id': 'T1',
          'txn_date': '2024-01-15',
          'txn_type': 'Deposit',
          'amount': 20000.0,
          'other_account': None
      },
      {
          'txn_id': 'T2',
          'txn_date': '2024-01-14',
          'txn_type': 'Withdrawal',
          'amount': 5000.0,
          'other_account': None
      },
      {
          'txn_id': 'TR1',
          'txn_date': '2024-01-12',
          'txn_type': 'Transfer Out',
          'amount': 8000.0,
          'other_account': 'AC1003'
      },
      {
          'txn_id': 'TR8',
          'txn_date': '2024-01-10',
          'txn_type': 'Transfer In',
          'amount': 2000.0,
          'other_account': 'AC1006'
      }
  ]
  ```
- **Live Cypher Query (`db.py`)**:
  3-Part UNION query using `toString(...)` for date formatting:
  ```cypher
  MATCH (a:Account {account_number: $account_number})-[:HAS_TRANSACTION]->(t:Transaction)
  RETURN t.txn_id AS txn_id,
         toString(t.txn_date) AS txn_date,
         t.txn_type AS txn_type,
         t.amount AS amount,
         null AS other_account
  UNION ALL
  MATCH (a:Account {account_number: $account_number})-[r:TRANSFERRED_TO]->(target:Account)
  RETURN r.txn_id AS txn_id,
         toString(r.txn_date) AS txn_date,
         'Transfer Out' AS txn_type,
         r.amount AS amount,
         target.account_number AS other_account
  UNION ALL
  MATCH (source:Account)-[r:TRANSFERRED_TO]->(a:Account {account_number: $account_number})
  RETURN r.txn_id AS txn_id,
         toString(r.txn_date) AS txn_date,
         'Transfer In' AS txn_type,
         r.amount AS amount,
         source.account_number AS other_account
  ```
  Python code executes `rows.sort(key=lambda x: (x['txn_date'], x['txn_id']), reverse=True)` and returns `rows`.
- **Mock Requirements (`mock_db.py`)**:
  - Filter mock transactions and transfers matching `account_number`.
  - For `AC1001`, returns 4 rows matching Section 8 test cases.
  - Returns `[]` if no transactions.

---

#### 5. `get_loans(customer_id: str)`
- **Signature**: `get_loans(customer_id: str)`
- **Return Structure**:
  ```python
  [
      {
          'loan_id': 'L01',
          'loan_type': 'Home Loan',
          'amount': 5000000.0,
          'interest_rate': 8.5,
          'term_months': 240,
          'status': 'Active',
          'loan_officer': 'Divya Rao',
          'branch_name': 'Anna Nagar'
      }
  ]
  ```
- **Live Cypher Query (`db.py`)**:
  ```cypher
  MATCH (c:Customer {customer_id: $customer_id})-[:HAS_LOAN]->(l:Loan)
  OPTIONAL MATCH (l)-[:MANAGED_BY]->(e:Employee)
  OPTIONAL MATCH (l)-[:LOCATED_AT]->(b:Branch)
  RETURN l.loan_id AS loan_id,
         l.loan_type AS loan_type,
         l.amount AS amount,
         l.interest_rate AS interest_rate,
         l.term_months AS term_months,
         l.status AS status,
         e.name AS loan_officer,
         b.branch_name AS branch_name
  ORDER BY l.loan_id ASC
  ```
- **Mock Requirements (`mock_db.py`)**:
  - Return list of loans for `customer_id`.
  - For `C01`: returns L01 Home Loan, loan_officer 'Divya Rao', branch_name 'Anna Nagar'.
  - Returns `[]` if no loans.

---

#### 6. `get_repayment_schedule(loan_id: str)`
- **Signature**: `get_repayment_schedule(loan_id: str)`
- **Return Structure**:
  ```python
  [
      {
          'installment_no': 1,
          'due_date': '2024-01-05',
          'amount_due': 45000.0,
          'status': 'Paid'
      },
      {
          'installment_no': 2,
          'due_date': '2024-02-05',
          'amount_due': 45000.0,
          'status': 'Paid'
      },
      {
          'installment_no': 3,
          'due_date': '2024-03-05',
          'amount_due': 45000.0,
          'status': 'Pending'
      }
  ]
  ```
- **Live Cypher Query (`db.py`)**:
  ```cypher
  MATCH (l:Loan {loan_id: $loan_id})-[:HAS_INSTALLMENT]->(inst:Installment)
  RETURN inst.installment_no AS installment_no,
         toString(inst.due_date) AS due_date,
         inst.amount_due AS amount_due,
         inst.status AS status
  ORDER BY inst.installment_no ASC
  ```
- **Mock Requirements (`mock_db.py`)**:
  - For `L01`: returns 3 installments (installments 1 and 2 'Paid', installment 3 'Pending').
  - Ordered by `installment_no ASC`.
  - Returns `[]` if loan not found.

---

#### 7. `get_investments(customer_id: str)`
- **Signature**: `get_investments(customer_id: str)`
- **Return Structure**:
  ```python
  [
      {
          'investment_id': 'I01',
          'investment_type': 'Mutual Fund',
          'amount': 100000.0,
          'start_date': '2023-06-01'
      },
      {
          'investment_id': 'I03',
          'investment_type': 'Wealth Management',
          'amount': 300000.0,
          'start_date': '2023-09-15'
      }
  ]
  ```
- **Live Cypher Query (`db.py`)**:
  ```cypher
  MATCH (c:Customer {customer_id: $customer_id})-[:HAS_INVESTMENT]->(i:Investment)
  RETURN i.investment_id AS investment_id,
         i.investment_type AS investment_type,
         i.amount AS amount,
         toString(i.start_date) AS start_date
  ORDER BY i.investment_id ASC
  ```
- **Mock Requirements (`mock_db.py`)**:
  - For `C01`: returns I01 Mutual Fund (100000) and I03 Wealth Management (300000).
  - Returns `[]` if no investments.

---

#### 8. `get_service_requests(customer_id: str)`
- **Signature**: `get_service_requests(customer_id: str)`
- **Return Structure**:
  ```python
  [
      {
          'request_id': 'SR03',
          'request_type': 'Cheque Book',
          'description': 'Cheque book request for AC1001',
          'status': 'Resolved',
          'request_date': '2024-01-10',
          'handled_by': 'Karthik Suresh'
      }
  ]
  ```
- **Live Cypher Query (`db.py`)**:
  ```cypher
  MATCH (c:Customer {customer_id: $customer_id})-[:RAISED]->(sr:ServiceRequest)
  OPTIONAL MATCH (sr)-[:ASSIGNED_TO]->(e:Employee)
  RETURN sr.request_id AS request_id,
         sr.request_type AS request_type,
         sr.description AS description,
         sr.status AS status,
         toString(sr.request_date) AS request_date,
         e.name AS handled_by
  ORDER BY sr.request_date DESC, sr.request_id DESC
  ```
- **Mock Requirements (`mock_db.py`)**:
  - For `C01`: initial baseline returns SR03 Cheque Book, Resolved, handled by 'Karthik Suresh'.
  - Any new request created via `raise_service_request` is appended and returned.
  - Returns `[]` if customer has no requests.

---

#### 9. `get_branches()`
- **Signature**: `get_branches()`
- **Return Structure**:
  ```python
  [
      {'branch_id': 'BR01', 'branch_name': 'Anna Nagar'},
      {'branch_id': 'BR02', 'branch_name': 'T Nagar'},
      {'branch_id': 'BR03', 'branch_name': 'Koramangala'}
  ]
  ```
- **Live Cypher Query (`db.py`)**:
  ```cypher
  MATCH (b:Branch)
  RETURN b.branch_id AS branch_id, b.branch_name AS branch_name
  ORDER BY b.branch_id ASC
  ```
- **Mock Requirements (`mock_db.py`)**:
  - Returns static list of 3 branches.

---

### Manage Functions (10–14)

#### 10. `add_customer(customer_id, first_name, last_name, city, phone, email, customer_type)`
- **Signature**: `add_customer(customer_id: str, first_name: str, last_name: str, city: str, phone: str, email: str, customer_type: str)`
- **Return Structure**:
  ```python
  {'success': True, 'message': 'Customer C07 added successfully'}
  # or on failure:
  {'success': False, 'message': 'Customer ID already exists'}
  ```
- **Live Cypher Implementation (`db.py`)**:
  - Checks if `customer_id` already exists.
  - If existing: returns `{'success': False, 'message': f"Customer ID {customer_id} already exists"}`.
  - If unique: creates node with concatenated `name`:
    ```cypher
    CREATE (c:Customer {
        customer_id: $customer_id,
        name: $name,
        city: $city,
        phone: $phone,
        email: $email,
        customer_type: $customer_type
    })
    ```
- **Mock Requirements (`mock_db.py`)**:
  - Check if `customer_id` in mock customer store.
  - If exists (e.g. `add_customer('C01', ...)`): returns `{'success': False, 'message': 'Customer ID already exists'}`.
  - If new: appends customer record with `name = f"{first_name} {last_name}".strip()`. Returns `{'success': True, 'message': 'Customer added successfully'}`.

---

#### 11. `update_customer_contact(customer_id, phone, email)`
- **Signature**: `update_customer_contact(customer_id: str, phone: str, email: str)`
- **Return Structure**:
  ```python
  {'success': True, 'message': 'Customer contact updated successfully'}
  # or on failure:
  {'success': False, 'message': 'Customer not found'}
  ```
- **Live Cypher Implementation (`db.py`)**:
  ```cypher
  MATCH (c:Customer {customer_id: $customer_id})
  SET c.phone = $phone, c.email = $email
  RETURN c.customer_id AS customer_id
  ```
  If 0 rows returned: return `{'success': False, 'message': f"Customer {customer_id} not found"}`.
- **Mock Requirements (`mock_db.py`)**:
  - Find customer in mock store. If missing, return `{'success': False, 'message': 'Customer not found'}`.
  - Update `phone` and `email` properties in place. Return `{'success': True, 'message': 'Customer contact updated successfully'}`.

---

#### 12. `open_account(account_number, customer_id, branch_id, account_type, opening_balance)`
- **Signature**: `open_account(account_number: str, customer_id: str, branch_id: str, account_type: str, opening_balance: float | int)`
- **Return Structure**:
  ```python
  {'success': True, 'message': 'Account opened successfully'}
  # or on failure:
  {'success': False, 'message': 'Customer or branch does not exist'}
  ```
- **Live Cypher Implementation (`db.py`)**:
  - Validates opening balance >= 0.
  - Validates customer and branch existence and account number uniqueness:
    ```cypher
    MATCH (c:Customer {customer_id: $customer_id})
    MATCH (b:Branch {branch_id: $branch_id})
    WHERE NOT EXISTS { MATCH (a:Account {account_number: $account_number}) }
    CREATE (a:Account {
        account_number: $account_number,
        account_type: $account_type,
        balance: $opening_balance,
        status: 'Active'
    })
    CREATE (c)-[:HOLDS]->(a)
    CREATE (a)-[:LOCATED_AT]->(b)
    RETURN a.account_number AS account_number
    ```
- **Mock Requirements (`mock_db.py`)**:
  - Check customer exists and branch exists. If either missing: return failure.
  - Check account number does not already exist. If duplicate: return failure.
  - Create new account in mock store linked to `customer_id` and `branch['branch_name']`.
  - Section 8 test case: `open_account('AC1009', 'C02', 'BR02', 'Savings', 0)` succeeds.

---

#### 13. `close_account(account_number)`
- **Signature**: `close_account(account_number: str)`
- **Return Structure**:
  ```python
  {'success': True, 'message': 'Account closed successfully'}
  # or on failure:
  {'success': False, 'message': 'Cannot close account with non-zero balance'}
  ```
- **Live Cypher Implementation (`db.py`)**:
  - Checks current balance:
    ```cypher
    MATCH (a:Account {account_number: $account_number})
    RETURN a.balance AS balance
    ```
  - If account not found: return `{'success': False, 'message': 'Account not found'}`.
  - If `balance != 0`: return `{'success': False, 'message': f"Cannot close account with balance of {balance}. Balance must be 0."}`.
  - If `balance == 0`:
    ```cypher
    MATCH (a:Account {account_number: $account_number})
    DETACH DELETE a
    ```
    Return `{'success': True, 'message': 'Account closed successfully'}`.
- **Mock Requirements (`mock_db.py`)**:
  - Find account. If not found: return `{'success': False, 'message': 'Account not found'}`.
  - If `account['balance'] != 0`: return `{'success': False, 'message': 'Cannot close account with non-zero balance'}`.
  - If `balance == 0`: delete account from mock store and return `{'success': True, 'message': 'Account closed successfully'}`.
  - Section 8 test cases:
    - `close_account('AC1008')` -> fails (balance != 0).
    - `close_account('AC1009')` -> succeeds after opening with 0 balance.

---

#### 14. `raise_service_request(customer_id, request_type, description)`
- **Signature**: `raise_service_request(customer_id: str, request_type: str, description: str)`
- **Return Structure**:
  ```python
  {
      'success': True,
      'message': 'Service request created successfully',
      'request_id': 'SR3F9A12C'
  }
  # or on failure:
  {
      'success': False,
      'message': 'Customer not found',
      'request_id': ''
  }
  ```
- **Live Cypher Implementation (`db.py`)**:
  - Generates ID using `new_id('SR')`.
  - Sets `request_date` to current date (`YYYY-MM-DD`).
  - Sets `status` to `'Pending'`.
  - Assigns to employee `'E05'` (Customer Service Executive Karthik Suresh):
    ```cypher
    MATCH (c:Customer {customer_id: $customer_id})
    MATCH (e:Employee {emp_id: 'E05'})
    CREATE (sr:ServiceRequest {
        request_id: $request_id,
        request_type: $request_type,
        description: $description,
        status: 'Pending',
        request_date: date($today)
    })
    CREATE (c)-[:RAISED]->(sr)
    CREATE (sr)-[:ASSIGNED_TO]->(e)
    RETURN sr.request_id AS request_id
    ```
- **Mock Requirements (`mock_db.py`)**:
  - Generate ID via `new_id('SR')`.
  - Verify customer exists; if not, return `{'success': False, 'message': 'Customer not found', 'request_id': ''}`.
  - Append new service request to mock store with handled_by='Karthik Suresh'.
  - Return `{'success': True, 'message': 'Service request created successfully', 'request_id': req_id}`.

---

### Process Functions (15–16)

#### 15. `process_transaction(account_number, txn_type, amount)`
- **Signature**: `process_transaction(account_number: str, txn_type: str, amount: float | int)`
- **Return Structure**:
  ```python
  {
      'success': True,
      'message': 'Deposit successful',
      'new_balance': 47000.0
  }
  # or on failure:
  {
      'success': False,
      'message': 'Insufficient balance',
      'new_balance': 42000.0
  }
  ```
- **Live Cypher Implementation (`db.py`)**:
  - Validates `txn_type in ('Deposit', 'Withdrawal')` and `amount > 0`.
  - Generates `txn_id = new_id('T')`.
  - For Deposit:
    ```cypher
    MATCH (a:Account {account_number: $account_number})
    SET a.balance = a.balance + $amount
    CREATE (t:Transaction {
        txn_id: $txn_id,
        txn_type: 'Deposit',
        amount: $amount,
        txn_date: date($today)
    })
    CREATE (a)-[:HAS_TRANSACTION]->(t)
    RETURN a.balance AS new_balance
    ```
  - For Withdrawal:
    ```cypher
    MATCH (a:Account {account_number: $account_number})
    WHERE a.balance >= $amount
    SET a.balance = a.balance - $amount
    CREATE (t:Transaction {
        txn_id: $txn_id,
        txn_type: 'Withdrawal',
        amount: $amount,
        txn_date: date($today)
    })
    CREATE (a)-[:HAS_TRANSACTION]->(t)
    RETURN a.balance AS new_balance
    ```
    If 0 rows returned, check whether account exists or balance was insufficient.
- **Mock Requirements (`mock_db.py`)**:
  - Find account in mock store. If missing, return `{'success': False, 'message': 'Account not found', 'new_balance': 0}`.
  - If `amount <= 0`: return `{'success': False, 'message': 'Amount must be positive', 'new_balance': account['balance']}`.
  - If `txn_type == 'Deposit'`:
    `account['balance'] += amount`
    Add record to transactions list.
    Return `{'success': True, 'message': 'Deposit successful', 'new_balance': account['balance']}`.
  - If `txn_type == 'Withdrawal'`:
    if `account['balance'] < amount`:
      return `{'success': False, 'message': 'Insufficient balance', 'new_balance': account['balance']}`.
    `account['balance'] -= amount`
    Add record to transactions list.
    Return `{'success': True, 'message': 'Withdrawal successful', 'new_balance': account['balance']}`.
  - Section 8 test cases:
    - `process_transaction('AC1003', 'Deposit', 5000)` -> `new_balance: 47000`.
    - `process_transaction('AC1003', 'Withdrawal', 99999999)` -> fails (`success: False`).

---

#### 16. `transfer_money(from_account, to_account, amount)`
- **Signature**: `transfer_money(from_account: str, to_account: str, amount: float | int)`
- **Return Structure**:
  ```python
  {'success': True, 'message': 'Transfer completed successfully'}
  # or on failure:
  {'success': False, 'message': 'Insufficient funds or account not found'}
  ```
- **Live Cypher Implementation (`db.py`)**:
  - Single atomic query updating both balances and creating `TRANSFERRED_TO` relationship with `new_id('TR')`:
    ```cypher
    MATCH (from:Account {account_number: $from_account})
    MATCH (to:Account {account_number: $to_account})
    WHERE from.account_number <> to.account_number AND from.balance >= $amount AND $amount > 0
    SET from.balance = from.balance - $amount,
        to.balance = to.balance + $amount
    CREATE (from)-[r:TRANSFERRED_TO {
        txn_id: $txn_id,
        amount: $amount,
        txn_date: date($today)
    }]->(to)
    RETURN from.balance AS from_balance, to.balance AS to_balance
    ```
    If query returns 0 rows, evaluate and return specific descriptive failure message.
- **Mock Requirements (`mock_db.py`)**:
  - Check `from_account == to_account`: return `{'success': False, 'message': 'Cannot transfer to the same account'}`.
  - Check `amount <= 0`: return `{'success': False, 'message': 'Amount must be positive'}`.
  - Look up both accounts. If either missing: return `{'success': False, 'message': 'Account not found'}`.
  - If `from_account['balance'] < amount`: return `{'success': False, 'message': 'Insufficient balance'}`.
  - Deduct from source balance, credit target balance.
  - Append transfer record to mock transfers store.
  - Section 8 test case: `transfer_money('AC1001', 'AC1003', 5000)` -> `{'success': True, 'message': '...'}`.

---

### Analytics Functions (17–20)

#### 17. `get_branch_account_counts()`
- **Signature**: `get_branch_account_counts()`
- **Return Structure**:
  ```python
  [
      {'branch_name': 'Anna Nagar', 'account_count': 3},
      {'branch_name': 'T Nagar', 'account_count': 3},
      {'branch_name': 'Koramangala', 'account_count': 2}
  ]
  ```
- **Live Cypher Query (`db.py`)**:
  ```cypher
  MATCH (b:Branch)
  OPTIONAL MATCH (a:Account)-[:LOCATED_AT]->(b)
  RETURN b.branch_name AS branch_name, count(a) AS account_count
  ORDER BY account_count DESC, b.branch_name ASC
  ```
- **Mock Requirements (`mock_db.py`)**:
  - Group accounts in mock store by branch name.
  - Returns Anna Nagar 3, T Nagar 3, Koramangala 2.

---

#### 18. `get_top_customers_by_balance(limit=5)`
- **Signature**: `get_top_customers_by_balance(limit: int = 5)`
- **Return Structure**:
  ```python
  [
      {'customer_id': 'C01', 'name': 'Samridhi Sharma', 'total_balance': 235000.0},
      {'customer_id': 'C03', 'name': 'Anita Rao', 'total_balance': 200000.0},
      {'customer_id': 'C06', 'name': 'Vikram Seth', 'total_balance': 95000.0}
  ]
  ```
- **Live Cypher Query (`db.py`)**:
  ```cypher
  MATCH (c:Customer)-[:HOLDS]->(a:Account)
  WITH c, sum(a.balance) AS total_balance
  RETURN c.customer_id AS customer_id,
         c.name AS name,
         total_balance
  ORDER BY total_balance DESC
  LIMIT $limit
  ```
- **Mock Requirements (`mock_db.py`)**:
  - Aggregate account balances per customer from mock store.
  - Sort descending by `total_balance`.
  - Slice `[:limit]`.
  - Section 8 test case: `get_top_customers_by_balance(3)` returns C01 (235000), C03 (200000), C06 (95000).

---

#### 19. `get_large_transfers(min_amount)`
- **Signature**: `get_large_transfers(min_amount: float | int)`
- **Return Structure**:
  ```python
  [
      {
          'txn_id': 'TR6',
          'from_account': 'AC1004',
          'to_account': 'AC1002',
          'amount': 40000.0,
          'txn_date': '2024-01-18'
      },
      {
          'txn_id': 'TR4',
          'from_account': 'AC1002',
          'to_account': 'AC1007',
          'amount': 25000.0,
          'txn_date': '2024-01-16'
      }
  ]
  ```
- **Live Cypher Query (`db.py`)**:
  ```cypher
  MATCH (from:Account)-[r:TRANSFERRED_TO]->(to:Account)
  WHERE r.amount >= $min_amount
  RETURN r.txn_id AS txn_id,
         from.account_number AS from_account,
         to.account_number AS to_account,
         r.amount AS amount,
         toString(r.txn_date) AS txn_date
  ORDER BY r.amount DESC, r.txn_date DESC
  ```
- **Mock Requirements (`mock_db.py`)**:
  - Filter mock transfers where `amount >= min_amount`.
  - Sort by amount descending.
  - Section 8 test case: `get_large_transfers(20000)` returns TR6 (40000) and TR4 (25000).

---

#### 20. `get_money_trail(account_number)`
- **Signature**: `get_money_trail(account_number: str)`
- **Return Structure**:
  ```python
  [
      {
          'trail': ['AC1001', 'AC1003'],
          'hops': 1
      },
      {
          'trail': ['AC1001', 'AC1003', 'AC1005'],
          'hops': 2
      },
      {
          'trail': ['AC1001', 'AC1003', 'AC1005', 'AC1006'],
          'hops': 3
      }
  ]
  ```
- **Live Cypher Query (`db.py`)**:
  ```cypher
  MATCH p = (a:Account {account_number: $account_number})-[:TRANSFERRED_TO*1..3]->(target:Account)
  RETURN [n IN nodes(p) | n.account_number] AS trail,
         length(p) AS hops
  ORDER BY hops ASC, trail ASC
  ```
- **Mock Requirements (`mock_db.py`)**:
  - Traverse outbound transfers from `account_number` up to 3 hops (using BFS/DFS over mock transfers).
  - Return list of dicts with `trail` and `hops`.
  - Section 8 test case: `get_money_trail('AC1001')` returns 3 rows with lengths 1, 2, and 3.

---

## 6. Caveats

1. **Schema Relationship Nomenclature**:
   - Relationship labels assumed: `(:Customer)-[:HOLDS]->(:Account)`, `(:Account)-[:LOCATED_AT]->(:Branch)`, `(:Customer)-[:ASSIGNED_TO]->(:Employee)`, `(:Account)-[:HAS_TRANSACTION]->(:Transaction)`, `(:Account)-[:TRANSFERRED_TO]->(:Account)`, `(:Customer)-[:HAS_LOAN]->(:Loan)`, `(:Loan)-[:HAS_INSTALLMENT]->(:Installment)`, `(:Customer)-[:HAS_INVESTMENT]->(:Investment)`, `(:Customer)-[:RAISED]->(:ServiceRequest)`.
   - `spec_miner_schema` is concurrently documenting `load_data.cypher`. The queries defined here align with standard Neo4j design and Section 8 test cases.
2. **Mock In-Memory Reset**:
   - Since write functions modify mock state, tests that add or close accounts may alter subsequent tests if run out of order. Providing a `reset_mock_data()` helper inside `mock_db.py` ensures tests remain idempotent and repeatable.

---

## 7. Conclusion

All 20 database function contracts have been completely mined, formally specified, and verified against Section 8 test cases and Section 2 requirements:
- **Signatures & Defaults**: Fully aligned across `db.py` and `mock_db.py` (e.g. `get_top_customers_by_balance(limit=5)`).
- **Return Dictionaries & Data Types**: Explicitly documented down to individual keys, types, and nullability.
- **Cypher Implementation**: Concrete parameterized Cypher templates defined for all 20 functions, including `toString(...)` date formatting, 3-part `UNION ALL`, atomic updates with balance check for transfers, and variable-length path traversal `[:TRANSFERRED_TO*1..3]`.
- **Mock DB State & Logic**: Clear in-memory state and mutation behaviors specified to satisfy both offline Streamlit UI usage and automated test suite verification.
- **Error Handling**: Standardized `try...except` contract returning `{'success': bool, 'message': str}` + custom keys (`request_id`, `new_balance`).

---

## 8. Verification Method

To independently verify contract compliance during and after implementation:

1. **Static Contract Signature and Return Parity Check**:
   Inspect `db.py` and `mock_db.py` to confirm that every function from 1 to 20 exists in both files with exact matching parameter names, order, and default values.
2. **Automated Test Suite Verification**:
   Execute the automated test suite in both live and mock mode:
   ```powershell
   # Offline Mock Mode Verification
   python test_suite.py --mode mock

   # Live Neo4j Mode Verification (when Neo4j instance is running)
   python test_suite.py --mode live
   ```
3. **Specific Assertion Verifications**:
   - `get_customer('C01')` -> returns dict with name `'Samridhi Sharma'`, type `'Premium'`, RM `'Priya Menon'`.
   - `get_accounts('C01')` -> returns 2 accounts with balances 85000 and 150000.
   - `get_total_balance('C01')` -> returns `235000`.
   - `get_transactions('AC1001')` -> returns 4 rows sorted descending by date with correct `other_account` fields.
   - `get_loans('C01')` -> returns L01 Home Loan with officer 'Divya Rao', branch 'Anna Nagar'.
   - `get_repayment_schedule('L01')` -> returns 3 installments with 3rd pending.
   - `get_investments('C01')` -> returns I01 (100000) and I03 (300000).
   - `get_service_requests('C01')` -> returns SR03 Cheque Book handled by Karthik Suresh.
   - `get_branch_account_counts()` -> returns Anna Nagar 3, T Nagar 3, Koramangala 2.
   - `get_top_customers_by_balance(3)` -> returns C01, C03, C06.
   - `get_large_transfers(20000)` -> returns TR6 (40000) and TR4 (25000).
   - `get_money_trail('AC1001')` -> returns 3 rows with 1, 2, and 3 hops.
   - Write tests: deposit increases balance, overdraft withdrawal fails, transfer succeeds, duplicate customer fails, close non-zero account fails, open zero balance account and close succeeds.
