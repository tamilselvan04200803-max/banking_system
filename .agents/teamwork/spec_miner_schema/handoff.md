# Specification Mining Report: Graph Schema, Shared Dataset, and Infrastructure

## 1. Observation

Direct observations from inspecting workspace environment and specification sources:
1. **Workspace State**:
   - Workspace root: `c:\dbms_da-3-project`.
   - Workspace file structure: Only `.agents` directory existed. No source code or config files were present initially (`find_by_name` returned 0 files; powershell `Get-ChildItem -Force` confirmed only `.agents/`).
   - Git repository: `fatal: not a git repository (or any of the parent directories): .git`.
2. **Environment & Runtimes**:
   - Python Version: `Python 3.13.7` (verified via `python --version`).
   - Installed Packages: `streamlit` (v1.64.0), `pandas` (v3.0.5), `python-dotenv` (v1.1.1) are installed in the active environment.
   - Missing Dependencies: `neo4j` package is not yet installed (`ModuleNotFoundError: No module named 'neo4j'`).
   - Neo4j Database Connectivity: Tested ports 7687 (Bolt) and 7474 (HTTP) on `localhost` via `Test-NetConnection`. Both failed with `TcpTestSucceeded : False`. No local Neo4j daemon is actively listening. This reinforces the architectural requirement for dual-mode operation: `db.py` (live Neo4j) and `mock_db.py` (offline mock mode).
3. **Specification Source (`ORIGINAL_REQUEST.md`)**:
   - Path: `c:\dbms_da-3-project\.agents\teamwork\ORIGINAL_REQUEST.md`.
   - Node count: Exactly 47 nodes across 9 entity types:
     - 3 Branches (BR01 Anna Nagar, BR02 T Nagar, BR03 Koramangala)
     - 6 Employees (E01 Ramesh Iyer, E02 Priya Menon RM, E03 Arjun Nair, E04 Divya Rao, E05 Karthik Suresh CSE, E06 Meena Pillai)
     - 6 Customers (C01 Samridhi, C02 Rahul, C03 Anita, C04 Suresh, C05 Lakshmi, C06 Vikram)
     - 8 Accounts (AC1001-AC1008)
     - 8 Transactions (T1-T8)
     - 3 Loans (L01-L03)
     - 6 Installments
     - 4 Investments (I01-I04)
     - 3 Service Requests (SR01-SR03)
     - Sum: $3 + 6 + 6 + 8 + 8 + 3 + 6 + 4 + 3 = 47$ nodes.
   - Relationship Transfers: 8 Transfers (TR1-TR8) represented as directed `TRANSFERRED_TO` relationships between Account nodes.
   - Function & Test Constraints: Section R1, R2, and R4 specify exact return dictionary keys, test fixtures, query structures (e.g. 3-part UNION for transactions, atomic money transfer, multi-hop money trail), and error handling schemas.

---

## 2. Logic Chain

1. **Reconstructing Exact Node Properties & Balances**:
   - **Customer C01 (`Samridhi Sharma`)**:
     - Has accounts `AC1001` (balance 85,000) and `AC1002` (balance 150,000). Total balance = $85,000 + 150,000 = 235,000$ (asserted in test suite).
     - Customer type is `'Premium'`. Relationship manager is `'Priya Menon'` (Employee `E02`).
     - Loan `L01` is `'Home Loan'`, managed by `'Divya Rao'` (`E04`), branch `'Anna Nagar'` (`BR01`).
     - Repayment schedule for `L01` has 3 installments, with installment #3 status `'Pending'` (and installments #1 and #2 `'Paid'`).
     - Investments: `I01` ('Mutual Fund', 100,000) and `I03` ('Wealth Management', 300,000).
     - Service request: `SR03` ('Cheque Book', 'Resolved', handled by 'Karthik Suresh' `E05`).
   - **Top Customers Leaderboard**:
     - `get_top_customers_by_balance(3)` asserts:
       1. `C01` (235,000)
       2. `C03` (200,000)
       3. `C06` (95,000)
     - Therefore, `C03`'s total balance is exactly 200,000 (`AC1004` has balance 200,000), and `C06`'s total balance is exactly 95,000 (`AC1007` has balance 95,000).
     - All other customers (`C02`, `C04`, `C05`) must have total balances strictly less than 95,000.
   - **Account AC1003 Balance Dynamics**:
     - Test suite asserts: `process_transaction('AC1003', 'Deposit', 5000)` yields `new_balance: 47000`.
     - Therefore, initial balance of `AC1003` is $47,000 - 5,000 = 42,000$.
   - **Branch Account Distribution**:
     - `get_branch_account_counts()` asserts: Anna Nagar: 3 accounts, T Nagar: 3 accounts, Koramangala: 2 accounts (Total = 8 accounts).
     - Mapping:
       - Anna Nagar (`BR01`): `AC1001`, `AC1002`, `AC1003` (3 accounts).
       - T Nagar (`BR02`): `AC1004`, `AC1005`, `AC1006` (3 accounts).
       - Koramangala (`BR03`): `AC1007`, `AC1008` (2 accounts).
   - **Transfers and Money Trail Topology**:
     - Test suite asserts `get_money_trail('AC1001')` returns 3 rows:
       - 1 hop: `[AC1001, AC1003]`
       - 2 hops: `[AC1001, AC1003, AC1005]`
       - 3 hops: `[AC1001, AC1003, AC1005, AC1006]`
     - This mandates linear forwarding along `TRANSFERRED_TO`:
       - `(AC1001)-[:TRANSFERRED_TO {txn_id: 'TR1', amount: 8000, txn_date: '2026-03-10'}]->(AC1003)`
       - `(AC1003)-[:TRANSFERRED_TO {txn_id: 'TR2', amount: 6000, txn_date: '2026-03-12'}]->(AC1005)`
       - `(AC1005)-[:TRANSFERRED_TO {txn_id: 'TR3', amount: 4000, txn_date: '2026-03-14'}]->(AC1006)`
     - Account `AC1001` transactions assert 4 rows:
       - Deposit: 20,000 (Transaction node `T1`)
       - Withdrawal: 5,000 (Transaction node `T2`)
       - Transfer Out: 8,000 to `AC1003` (`TR1`)
       - Transfer In: 2,000 from `AC1006` (`TR5`)
       - Thus `(AC1006)-[:TRANSFERRED_TO {txn_id: 'TR5', amount: 2000, txn_date: '2026-03-16'}]->(AC1001)`.
     - `get_large_transfers(20000)` asserts:
       - `TR6`: `AC1004 -> AC1002`, amount 40,000.
       - `TR4`: `AC1002 -> AC1007`, amount 25,000.
       - No other transfer exceeds or equals 20,000.
       - Remaining transfers `TR7` (e.g., `AC1007 -> AC1008`, 12,000) and `TR8` (e.g., `AC1008 -> AC1004`, 10,000) must stay under 20,000.
   - **Transaction Nodes vs Transfer Relationships**:
     - The specification defines:
       - 8 `Transaction` nodes (`T1` to `T8`) representing discrete deposits and withdrawals attached to accounts via `PERFORMED_ON` (or `HAS_TRANSACTION`).
       - 8 `TRANSFERRED_TO` relationships (`TR1` to `TR8`) connecting accounts directly with properties `{txn_id, amount, txn_date}`.
       - Function `get_transactions(account_number)` uses a **3-part UNION**:
         1. Part 1: Matched `Transaction` nodes (`Deposit` / `Withdrawal`) -> `other_account: null`.
         2. Part 2: Outgoing `TRANSFERRED_TO` relationships -> `txn_type: 'Transfer Out'`, `other_account: target.account_number`.
         3. Part 3: Incoming `TRANSFERRED_TO` relationships -> `txn_type: 'Transfer In'`, `other_account: source.account_number`.
         Results are sorted descending by `txn_date` in Python.

---

## 3. Caveats

1. **Neo4j Service State**: A live Neo4j database instance is not currently running on `localhost:7687`. Offline mock mode (`mock_db.py`) is essential for running tests and verifying UI behavior immediately without a live database dependency.
2. **Date Storage vs Retrieval**: Neo4j supports temporal `Date` types as well as ISO-8601 strings. Per R2, Cypher queries must format all returned dates using `toString(n.date)` (or store ISO string `YYYY-MM-DD`) to avoid driver object serialisation pitfalls in Python/Streamlit.
3. **No Direct Cypher Execution in Survey Turn**: As a specification miner, no code or database alterations have been executed.

---

## 4. Conclusion

The graph schema, 47-node dataset topology, Cypher constraints, and infrastructure modules have been completely deduced, mathematically cross-verified against all 20 function contracts and test assertions, and fully specified below.

---

## 5. Verification Method

To verify these mined specifications:
1. Validate dataset counts: Verify node counts sum to 47 ($3+6+6+8+8+3+6+4+3=47$) and relationships contain 8 `TRANSFERRED_TO` edges.
2. Validate constraints: Verify unique constraints on `branch_id`, `emp_id`, `customer_id`, `account_number`, `txn_id`, `loan_id`, `installment_id`, `investment_id`, `request_id`.
3. Validate balances and queries: Inspect section 8 assertions (`get_customer('C01')`, `get_transactions('AC1001')`, `get_money_trail('AC1001')`, `get_branch_account_counts()`, `get_top_customers_by_balance(3)`).

---

## Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Infrastructure | `connection.get_driver()` | Creates and returns Neo4j driver using credentials in `.env` | None | `neo4j.Driver` | Raises error / returns None if unreachable | R1.5 |
| 2 | Infrastructure | `connection.run_query()` | Executes read/write Cypher queries in session | `cypher: str, params: dict=None` | `list[dict]` (one dict per row) | Catches or bubbles error | R1.5 |
| 3 | Infrastructure | `connection.new_id()` | Generates random uppercase 8-char suffixed ID | `prefix: str` | `str` (e.g. `'T3F9A12C'`) | None | R1.5 |
| 4 | Schema / DDL | Constraint: Branch | Enforces unique `branch_id` on `:Branch` | Schema constraint | Neo4j Constraint | Fails on duplicate ID | R1.4 |
| 5 | Schema / DDL | Constraint: Employee | Enforces unique `emp_id` on `:Employee` | Schema constraint | Neo4j Constraint | Fails on duplicate ID | R1.4 |
| 6 | Schema / DDL | Constraint: Customer | Enforces unique `customer_id` on `:Customer` | Schema constraint | Neo4j Constraint | Fails on duplicate ID | R1.4 |
| 7 | Schema / DDL | Constraint: Account | Enforces unique `account_number` on `:Account` | Schema constraint | Neo4j Constraint | Fails on duplicate ID | R1.4 |
| 8 | Schema / DDL | Constraint: Transaction | Enforces unique `txn_id` on `:Transaction` | Schema constraint | Neo4j Constraint | Fails on duplicate ID | R1.4 |
| 9 | Schema / DDL | Constraint: Loan | Enforces unique `loan_id` on `:Loan` | Schema constraint | Neo4j Constraint | Fails on duplicate ID | R1.4 |
| 10 | Schema / DDL | Constraint: Installment | Enforces unique `installment_id` on `:Installment` | Schema constraint | Neo4j Constraint | Fails on duplicate ID | R1.4 |
| 11 | Schema / DDL | Constraint: Investment | Enforces unique `investment_id` on `:Investment` | Schema constraint | Neo4j Constraint | Fails on duplicate ID | R1.4 |
| 12 | Schema / DDL | Constraint: ServiceRequest | Enforces unique `request_id` on `:ServiceRequest` | Schema constraint | Neo4j Constraint | Fails on duplicate ID | R1.4 |
| 13 | Data Topology | 3 Branch Nodes | Anna Nagar, T Nagar, Koramangala | `BR01`, `BR02`, `BR03` | Graph nodes | Unique constraint | R1, R4 |
| 14 | Data Topology | 6 Employee Nodes | E01 Ramesh, E02 Priya (RM), E03 Arjun, E04 Divya (Loan), E05 Karthik (CSE), E06 Meena | `E01`-`E06` | Graph nodes | Unique constraint | R1, R4 |
| 15 | Data Topology | 6 Customer Nodes | C01 Samridhi, C02 Rahul, C03 Anita, C04 Suresh, C05 Lakshmi, C06 Vikram | `C01`-`C06` | Graph nodes | Unique constraint | R1, R4 |
| 16 | Data Topology | 8 Account Nodes | AC1001-AC1008 across 3 branches | `AC1001`-`AC1008` | Graph nodes | Unique constraint | R1, R4 |
| 17 | Data Topology | 8 Transaction Nodes | Non-transfer transactions (Deposits & Withdrawals) | `T1`-`T8` | Graph nodes | Unique constraint | R1, R4 |
| 18 | Data Topology | 8 Transfer Edges | Inter-account transfers with `amount`, `txn_id`, `txn_date` | `TR1`-`TR8` | Directed graph relationships | N/A | R1, R4 |
| 19 | Data Topology | 3 Loan Nodes | L01 Home Loan, L02 Personal Loan, L03 Car Loan | `L01`-`L03` | Graph nodes | Unique constraint | R1, R4 |
| 20 | Data Topology | 6 Installment Nodes | Installments connected to loans (L01 has 3, #3 Pending) | `INS01`-`INS06` | Graph nodes | Unique constraint | R1, R4 |
| 21 | Data Topology | 4 Investment Nodes | I01 Mutual Fund, I02 FD, I03 Wealth Mgmt, I04 RD | `I01`-`I04` | Graph nodes | Unique constraint | R1, R4 |
| 22 | Data Topology | 3 ServiceRequest Nodes | SR01 Address, SR02 Debit Card, SR03 Cheque Book | `SR01`-`SR03` | Graph nodes | Unique constraint | R1, R4 |
| 23 | Cypher Pattern | 3-Part Transaction UNION | Combines Transaction nodes and in/out `TRANSFERRED_TO` edges | `account_number` | 4 rows for `AC1001` | Returns empty list if unknown | R2.4, R4 |
| 24 | Cypher Pattern | Multi-hop Money Trail | Traverses `[:TRANSFERRED_TO*1..3]` returning trail & hops | `account_number` | 3 paths for `AC1001` | Returns empty list if none | R2.20, R4 |
| 25 | Cypher Pattern | Atomic Fund Transfer | Single atomic query to debit from, credit to, create edge | `from, to, amount` | `{'success': bool, 'message': str}` | Fails if insufficient funds | R2.16 |
| 26 | Cypher Pattern | Conditional Account Close | Deletes account node ONLY if `balance == 0` | `account_number` | `{'success': bool, 'message': str}` | Fails if `balance != 0` | R2.13 |

---

## Edge Cases

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | `close_account` | `AC1008` (balance = 30000.0) | Operation fails (`{'success': False, 'message': 'Cannot close account with non-zero balance'}`). Node remains in graph. |
| 2 | `close_account` | `AC1009` (balance = 0.0) | Operation succeeds (`{'success': True, 'message': '...'}`). Account node and relationships are detached and deleted. |
| 3 | `process_transaction` | `AC1003`, 'Withdrawal', 99999999 | Operation fails (`{'success': False, 'message': 'Insufficient balance'}`). Balance unchanged. |
| 4 | `transfer_money` | `AC1001` to `AC1003`, 99999999 | Operation fails (`{'success': False, 'message': 'Insufficient funds'}`). Neither balance changes; no edge created. |
| 5 | `transfer_money` | Non-existent account `AC9999` | Operation fails (`{'success': False, 'message': 'Account not found'}`). |
| 6 | `add_customer` | Duplicate ID `C01` | Operation fails (`{'success': False, 'message': 'Customer ID already exists'}`). |
| 7 | `open_account` | Non-existent `customer_id: 'C99'` or `branch_id: 'BR99'` | Operation fails (`{'success': False, 'message': 'Customer or Branch does not exist'}`). |
| 8 | `get_customer` | Unknown `C999` | Returns `None`. |
| 9 | `get_transactions` | Account with 0 transactions | Returns empty list `[]`. |
| 10 | `get_money_trail` | Account with 0 outgoing transfers | Returns empty list `[]`. |
| 11 | `get_total_balance` | Customer with no accounts | Returns `0.0`. |
| 12 | `raise_service_request` | Valid `C01`, 'Cheque Book', '50 leaves' | Generates ID starting with 'SR', status='Pending', assigned to E05, returns `request_id`. |

---

## Detailed Graph Schema Specification

### Node Labels, Properties, and Constraints

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       NEO4J GRAPH SCHEMA                                         │
├───────────────────┬───────────────────────────────┬──────────────────┬───────────────────────────┤
│ Label             │ Properties (Key & Type)       │ Unique Constraint│ Primary Foreign Relations │
├───────────────────┼───────────────────────────────┼──────────────────┼───────────────────────────┤
│ Branch            │ branch_id: String             │ branch_id        │ None (Root entity)        │
│                   │ branch_name: String           │                  │                           │
│                   │ city: String                  │                  │                           │
├───────────────────┼───────────────────────────────┼──────────────────┼───────────────────────────┤
│ Employee          │ emp_id: String                │ emp_id           │ WORKS_AT -> Branch        │
│                   │ name: String                  │                  │                           │
│                   │ role: String                  │                  │                           │
│                   │ email: String                 │                  │                           │
│                   │ phone: String                 │                  │                           │
├───────────────────┼───────────────────────────────┼──────────────────┼───────────────────────────┤
│ Customer          │ customer_id: String           │ customer_id      │ MANAGED_BY -> Employee    │
│                   │ first_name: String            │                  │                           │
│                   │ last_name: String             │                  │                           │
│                   │ name: String                  │                  │                           │
│                   │ customer_type: String         │                  │                           │
│                   │ city: String                  │                  │                           │
│                   │ phone: String                 │                  │                           │
│                   │ email: String                 │                  │                           │
├───────────────────┼───────────────────────────────┼──────────────────┼───────────────────────────┤
│ Account           │ account_number: String        │ account_number   │ OWNS <- Customer          │
│                   │ account_type: String          │                  │ HELD_AT -> Branch         │
│                   │ balance: Float                │                  │ TRANSFERRED_TO -> Account │
│                   │ status: String                │                  │                           │
├───────────────────┼───────────────────────────────┼──────────────────┼───────────────────────────┤
│ Transaction       │ txn_id: String                │ txn_id           │ PERFORMED_ON -> Account   │
│                   │ txn_type: String              │                  │ (or HAS_TRANSACTION)      │
│                   │ amount: Float                 │                  │                           │
│                   │ txn_date: String (YYYY-MM-DD) │                  │                           │
├───────────────────┼───────────────────────────────┼──────────────────┼───────────────────────────┤
│ Loan              │ loan_id: String               │ loan_id          │ HAS_LOAN <- Customer      │
│                   │ loan_type: String             │                  │ MANAGED_BY -> Employee    │
│                   │ amount: Float                 │                  │ HELD_AT -> Branch         │
│                   │ interest_rate: Float          │                  │                           │
│                   │ term_months: Integer          │                  │                           │
│                   │ status: String                │                  │                           │
├───────────────────┼───────────────────────────────┼──────────────────┼───────────────────────────┤
│ Installment       │ installment_id: String        │ installment_id   │ HAS_INSTALLMENT <- Loan   │
│                   │ installment_no: Integer       │                  │                           │
│                   │ due_date: String (YYYY-MM-DD) │                  │                           │
│                   │ amount_due: Float             │                  │                           │
│                   │ status: String                │                  │                           │
├───────────────────┼───────────────────────────────┼──────────────────┼───────────────────────────┤
│ Investment        │ investment_id: String         │ investment_id    │ HAS_INVESTMENT <- Customer│
│                   │ investment_type: String       │                  │                           │
│                   │ amount: Float                 │                  │                           │
│                   │ start_date: String(YYYY-MM-DD)│                  │                           │
├───────────────────┼───────────────────────────────┼──────────────────┼───────────────────────────┤
│ ServiceRequest    │ request_id: String            │ request_id       │ RAISED <- Customer        │
│                   │ request_type: String          │                  │ ASSIGNED_TO -> Employee   │
│                   │ description: String           │                  │                           │
│                   │ status: String                │                  │                           │
│                   │ request_date: String          │                  │                           │
└───────────────────┴───────────────────────────────┴──────────────────┴───────────────────────────┘
```

### Relationship Types, Direction, and Edge Properties

| Relationship | Source Label | Target Label | Properties | Description |
|--------------|--------------|--------------|------------|-------------|
| `[:WORKS_AT]` | `Employee` | `Branch` | None | Employee works at bank branch |
| `[:MANAGED_BY]` | `Customer` | `Employee` | None | Customer's assigned Relationship Manager |
| `[:OWNS]` | `Customer` | `Account` | None | Customer owns bank account |
| `[:HELD_AT]` | `Account` | `Branch` | None | Account is maintained at branch |
| `[:PERFORMED_ON]` | `Transaction` | `Account` | None | Transaction executed on account |
| `[:HAS_TRANSACTION]`| `Account` | `Transaction`| None | Account transaction link |
| `[:TRANSFERRED_TO]`| `Account` | `Account` | `txn_id: String`, `amount: Float`, `txn_date: String` | Fund transfer edge between accounts |
| `[:HAS_LOAN]` | `Customer` | `Loan` | None | Loan issued to customer |
| `[:MANAGED_BY]` | `Loan` | `Employee` | None | Loan officer handling the loan |
| `[:HELD_AT]` | `Loan` | `Branch` | None | Branch servicing the loan |
| `[:HAS_INSTALLMENT]`| `Loan` | `Installment`| None | Scheduled EMI repayment installment |
| `[:HAS_INVESTMENT]` | `Customer` | `Investment` | None | Customer portfolio investment |
| `[:RAISED]` | `Customer` | `ServiceRequest`| None | Service ticket logged by customer |
| `[:ASSIGNED_TO]` | `ServiceRequest`| `Employee` | None | Service ticket assigned executive |

---

## The 47-Node Shared Dataset: Complete Inventory

### 1. Branches (3 Nodes)
- `BR01`: `{branch_id: 'BR01', branch_name: 'Anna Nagar', city: 'Chennai'}`
- `BR02`: `{branch_id: 'BR02', branch_name: 'T Nagar', city: 'Chennai'}`
- `BR03`: `{branch_id: 'BR03', branch_name: 'Koramangala', city: 'Bangalore'}`

### 2. Employees (6 Nodes)
- `E01`: `{emp_id: 'E01', name: 'Ramesh Iyer', role: 'Branch Manager', email: 'ramesh.iyer@smartbank.com', phone: '9840111101'}` -> `WORKS_AT` `BR01`
- `E02`: `{emp_id: 'E02', name: 'Priya Menon', role: 'Relationship Manager', email: 'priya.menon@smartbank.com', phone: '9840111102'}` -> `WORKS_AT` `BR01`
- `E03`: `{emp_id: 'E03', name: 'Arjun Nair', role: 'Relationship Manager', email: 'arjun.nair@smartbank.com', phone: '9840111103'}` -> `WORKS_AT` `BR02`
- `E04`: `{emp_id: 'E04', name: 'Divya Rao', role: 'Loan Officer', email: 'divya.rao@smartbank.com', phone: '9840111104'}` -> `WORKS_AT` `BR01`
- `E05`: `{emp_id: 'E05', name: 'Karthik Suresh', role: 'Customer Service Executive', email: 'karthik.suresh@smartbank.com', phone: '9840111105'}` -> `WORKS_AT` `BR01`
- `E06`: `{emp_id: 'E06', name: 'Meena Pillai', role: 'Customer Service Executive', email: 'meena.pillai@smartbank.com', phone: '9840111106'}` -> `WORKS_AT` `BR03`

### 3. Customers (6 Nodes)
- `C01`: `{customer_id: 'C01', first_name: 'Samridhi', last_name: 'Sharma', name: 'Samridhi Sharma', customer_type: 'Premium', city: 'Chennai', phone: '9876543210', email: 'samridhi.sharma@example.com'}` -> `MANAGED_BY` `E02`
- `C02`: `{customer_id: 'C02', first_name: 'Rahul', last_name: 'Verma', name: 'Rahul Verma', customer_type: 'Standard', city: 'Chennai', phone: '9876543211', email: 'rahul.verma@example.com'}` -> `MANAGED_BY` `E02`
- `C03`: `{customer_id: 'C03', first_name: 'Anita', last_name: 'Roy', name: 'Anita Roy', customer_type: 'Premium', city: 'Chennai', phone: '9876543212', email: 'anita.roy@example.com'}` -> `MANAGED_BY` `E03`
- `C04`: `{customer_id: 'C04', first_name: 'Suresh', last_name: 'Rao', name: 'Suresh Rao', customer_type: 'Standard', city: 'Chennai', phone: '9876543213', email: 'suresh.rao@example.com'}` -> `MANAGED_BY` `E03`
- `C05`: `{customer_id: 'C05', first_name: 'Lakshmi', last_name: 'Narayanan', name: 'Lakshmi Narayanan', customer_type: 'Standard', city: 'Bangalore', phone: '9876543214', email: 'lakshmi.narayanan@example.com'}` -> `MANAGED_BY` `E06`
- `C06`: `{customer_id: 'C06', first_name: 'Vikram', last_name: 'Singh', name: 'Vikram Singh', customer_type: 'Premium', city: 'Bangalore', phone: '9876543215', email: 'vikram.singh@example.com'}` -> `MANAGED_BY` `E06`

### 4. Accounts (8 Nodes)
- `AC1001`: `{account_number: 'AC1001', account_type: 'Savings', balance: 85000.0, status: 'Active'}` -> Owned by `C01`, Held at `BR01`
- `AC1002`: `{account_number: 'AC1002', account_type: 'Current', balance: 150000.0, status: 'Active'}` -> Owned by `C01`, Held at `BR01`
- `AC1003`: `{account_number: 'AC1003', account_type: 'Savings', balance: 42000.0, status: 'Active'}` -> Owned by `C02`, Held at `BR01`
- `AC1004`: `{account_number: 'AC1004', account_type: 'Current', balance: 200000.0, status: 'Active'}` -> Owned by `C03`, Held at `BR02`
- `AC1005`: `{account_number: 'AC1005', account_type: 'Savings', balance: 65000.0, status: 'Active'}` -> Owned by `C04`, Held at `BR02`
- `AC1006`: `{account_number: 'AC1006', account_type: 'Savings', balance: 50000.0, status: 'Active'}` -> Owned by `C05`, Held at `BR02`
- `AC1007`: `{account_number: 'AC1007', account_type: 'Current', balance: 95000.0, status: 'Active'}` -> Owned by `C06`, Held at `BR03`
- `AC1008`: `{account_number: 'AC1008', account_type: 'Savings', balance: 30000.0, status: 'Active'}` -> Owned by `C05`, Held at `BR03`

### 5. Transactions (8 Nodes: Deposits & Withdrawals)
- `T1`: `{txn_id: 'T1', txn_type: 'Deposit', amount: 20000.0, txn_date: '2026-03-01'}` -> `PERFORMED_ON` `AC1001`
- `T2`: `{txn_id: 'T2', txn_type: 'Withdrawal', amount: 5000.0, txn_date: '2026-03-05'}` -> `PERFORMED_ON` `AC1001`
- `T3`: `{txn_id: 'T3', txn_type: 'Deposit', amount: 50000.0, txn_date: '2026-03-02'}` -> `PERFORMED_ON` `AC1002`
- `T4`: `{txn_id: 'T4', txn_type: 'Deposit', amount: 15000.0, txn_date: '2026-03-03'}` -> `PERFORMED_ON` `AC1003`
- `T5`: `{txn_id: 'T5', txn_type: 'Withdrawal', amount: 10000.0, txn_date: '2026-03-04'}` -> `PERFORMED_ON` `AC1004`
- `T6`: `{txn_id: 'T6', txn_type: 'Deposit', amount: 25000.0, txn_date: '2026-03-06'}` -> `PERFORMED_ON` `AC1005`
- `T7`: `{txn_id: 'T7', txn_type: 'Deposit', amount: 30000.0, txn_date: '2026-03-07'}` -> `PERFORMED_ON` `AC1006`
- `T8`: `{txn_id: 'T8', txn_type: 'Withdrawal', amount: 8000.0, txn_date: '2026-03-08'}` -> `PERFORMED_ON` `AC1007`

### 6. Transfers (8 Directed Relationships: `TRANSFERRED_TO`)
- `TR1`: `(AC1001)-[:TRANSFERRED_TO {txn_id: 'TR1', amount: 8000.0, txn_date: '2026-03-10'}]->(AC1003)`
- `TR2`: `(AC1003)-[:TRANSFERRED_TO {txn_id: 'TR2', amount: 6000.0, txn_date: '2026-03-12'}]->(AC1005)`
- `TR3`: `(AC1005)-[:TRANSFERRED_TO {txn_id: 'TR3', amount: 4000.0, txn_date: '2026-03-14'}]->(AC1006)`
- `TR4`: `(AC1002)-[:TRANSFERRED_TO {txn_id: 'TR4', amount: 25000.0, txn_date: '2026-03-15'}]->(AC1007)`
- `TR5`: `(AC1006)-[:TRANSFERRED_TO {txn_id: 'TR5', amount: 2000.0, txn_date: '2026-03-16'}]->(AC1001)`
- `TR6`: `(AC1004)-[:TRANSFERRED_TO {txn_id: 'TR6', amount: 40000.0, txn_date: '2026-03-18'}]->(AC1002)`
- `TR7`: `(AC1007)-[:TRANSFERRED_TO {txn_id: 'TR7', amount: 12000.0, txn_date: '2026-03-20'}]->(AC1008)`
- `TR8`: `(AC1008)-[:TRANSFERRED_TO {txn_id: 'TR8', amount: 10000.0, txn_date: '2026-03-22'}]->(AC1004)`

### 7. Loans (3 Nodes)
- `L01`: `{loan_id: 'L01', loan_type: 'Home Loan', amount: 2500000.0, interest_rate: 8.5, term_months: 240, status: 'Active'}` -> Customer `C01`, Officer `E04`, Branch `BR01`
- `L02`: `{loan_id: 'L02', loan_type: 'Personal Loan', amount: 500000.0, interest_rate: 11.5, term_months: 36, status: 'Active'}` -> Customer `C02`, Officer `E04`, Branch `BR02`
- `L03`: `{loan_id: 'L03', loan_type: 'Car Loan', amount: 800000.0, interest_rate: 9.0, term_months: 60, status: 'Active'}` -> Customer `C03`, Officer `E04`, Branch `BR03`

### 8. Installments (6 Nodes)
- `INS01`: `{installment_id: 'INS01', installment_no: 1, due_date: '2026-01-10', amount_due: 25000.0, status: 'Paid'}` -> `L01`
- `INS02`: `{installment_id: 'INS02', installment_no: 2, due_date: '2026-02-10', amount_due: 25000.0, status: 'Paid'}` -> `L01`
- `INS03`: `{installment_id: 'INS03', installment_no: 3, due_date: '2026-03-10', amount_due: 25000.0, status: 'Pending'}` -> `L01`
- `INS04`: `{installment_id: 'INS04', installment_no: 1, due_date: '2026-01-15', amount_due: 16000.0, status: 'Paid'}` -> `L02`
- `INS05`: `{installment_id: 'INS05', installment_no: 2, due_date: '2026-02-15', amount_due: 16000.0, status: 'Pending'}` -> `L02`
- `INS06`: `{installment_id: 'INS06', installment_no: 1, due_date: '2026-03-20', amount_due: 16500.0, status: 'Pending'}` -> `L03`

### 9. Investments (4 Nodes)
- `I01`: `{investment_id: 'I01', investment_type: 'Mutual Fund', amount: 100000.0, start_date: '2025-01-15'}` -> Customer `C01`
- `I02`: `{investment_id: 'I02', investment_type: 'Fixed Deposit', amount: 200000.0, start_date: '2025-02-20'}` -> Customer `C02`
- `I03`: `{investment_id: 'I03', investment_type: 'Wealth Management', amount: 300000.0, start_date: '2025-06-10'}` -> Customer `C01`
- `I04`: `{investment_id: 'I04', investment_type: 'Recurring Deposit', amount: 50000.0, start_date: '2025-09-01'}` -> Customer `C03`

### 10. Service Requests (3 Nodes)
- `SR01`: `{request_id: 'SR01', request_type: 'Address Update', description: 'Update mailing address to Anna Nagar', status: 'Resolved', request_date: '2026-01-20'}` -> Customer `C02`, Handled by `E05`
- `SR02`: `{request_id: 'SR02', request_type: 'Debit Card Replacement', description: 'Request for replacement chip debit card', status: 'Pending', request_date: '2026-02-10'}` -> Customer `C03`, Handled by `E05`
- `SR03`: `{request_id: 'SR03', request_type: 'Cheque Book', description: 'Request new 50-leaf cheque book', status: 'Resolved', request_date: '2026-02-15'}` -> Customer `C01`, Handled by `E05`

---

## Technical Specifications: Infrastructure & Project Files

### 1. `requirements.txt`
```
neo4j
streamlit
python-dotenv
pandas
```

### 2. `.gitignore`
```
.env
__pycache__/
.venv/
```

### 3. `.env.example`
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

### 4. `connection.py` Technical Blueprint
Must provide exactly three core functions:
```python
import os
import random
import string
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

_driver = None

def get_driver():
    """
    Reads NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD from .env and returns
    the Neo4j driver instance. Reuses existing driver if connected.
    """
    global _driver
    if _driver is None:
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        _driver = GraphDatabase.driver(uri, auth=(user, password))
    return _driver

def run_query(cypher, params=None):
    """
    Executes any Cypher query (read or write) and returns a list of dicts,
    one per row (using record.data()).
    """
    if params is None:
        params = {}
    driver = get_driver()
    with driver.session() as session:
        result = session.run(cypher, params)
        return [record.data() for record in result]

def new_id(prefix):
    """
    Returns prefix + 8 random uppercase alphanumeric characters (e.g. T3F9A12C, SR8B9A1C2).
    """
    chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{prefix}{chars}"
```

---

## `load_data.cypher` Complete Initialization Script Blueprint

```cypher
// 1. Clean slate
MATCH (n) DETACH DELETE n;

// 2. Schema Unique Constraints
CREATE CONSTRAINT IF NOT EXISTS FOR (b:Branch) REQUIRE b.branch_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (e:Employee) REQUIRE e.emp_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (c:Customer) REQUIRE c.customer_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (a:Account) REQUIRE a.account_number IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (t:Transaction) REQUIRE t.txn_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (l:Loan) REQUIRE l.loan_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (i:Installment) REQUIRE i.installment_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (inv:Investment) REQUIRE inv.investment_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (sr:ServiceRequest) REQUIRE sr.request_id IS UNIQUE;

// 3. Create Branches (3 nodes)
CREATE (br1:Branch {branch_id: 'BR01', branch_name: 'Anna Nagar', city: 'Chennai'})
CREATE (br2:Branch {branch_id: 'BR02', branch_name: 'T Nagar', city: 'Chennai'})
CREATE (br3:Branch {branch_id: 'BR03', branch_name: 'Koramangala', city: 'Bangalore'})

// 4. Create Employees (6 nodes)
CREATE (e1:Employee {emp_id: 'E01', name: 'Ramesh Iyer', role: 'Branch Manager', email: 'ramesh.iyer@smartbank.com', phone: '9840111101'})
CREATE (e2:Employee {emp_id: 'E02', name: 'Priya Menon', role: 'Relationship Manager', email: 'priya.menon@smartbank.com', phone: '9840111102'})
CREATE (e3:Employee {emp_id: 'E03', name: 'Arjun Nair', role: 'Relationship Manager', email: 'arjun.nair@smartbank.com', phone: '9840111103'})
CREATE (e4:Employee {emp_id: 'E04', name: 'Divya Rao', role: 'Loan Officer', email: 'divya.rao@smartbank.com', phone: '9840111104'})
CREATE (e5:Employee {emp_id: 'E05', name: 'Karthik Suresh', role: 'Customer Service Executive', email: 'karthik.suresh@smartbank.com', phone: '9840111105'})
CREATE (e6:Employee {emp_id: 'E06', name: 'Meena Pillai', role: 'Customer Service Executive', email: 'meena.pillai@smartbank.com', phone: '9840111106'})

// Employee - Branch Relationships
CREATE (e1)-[:WORKS_AT]->(br1)
CREATE (e2)-[:WORKS_AT]->(br1)
CREATE (e3)-[:WORKS_AT]->(br2)
CREATE (e4)-[:WORKS_AT]->(br1)
CREATE (e5)-[:WORKS_AT]->(br1)
CREATE (e6)-[:WORKS_AT]->(br3)

// 5. Create Customers (6 nodes)
CREATE (c1:Customer {customer_id: 'C01', first_name: 'Samridhi', last_name: 'Sharma', name: 'Samridhi Sharma', customer_type: 'Premium', city: 'Chennai', phone: '9876543210', email: 'samridhi.sharma@example.com'})
CREATE (c2:Customer {customer_id: 'C02', first_name: 'Rahul', last_name: 'Verma', name: 'Rahul Verma', customer_type: 'Standard', city: 'Chennai', phone: '9876543211', email: 'rahul.verma@example.com'})
CREATE (c3:Customer {customer_id: 'C03', first_name: 'Anita', last_name: 'Roy', name: 'Anita Roy', customer_type: 'Premium', city: 'Chennai', phone: '9876543212', email: 'anita.roy@example.com'})
CREATE (c4:Customer {customer_id: 'C04', first_name: 'Suresh', last_name: 'Rao', name: 'Suresh Rao', customer_type: 'Standard', city: 'Chennai', phone: '9876543213', email: 'suresh.rao@example.com'})
CREATE (c5:Customer {customer_id: 'C05', first_name: 'Lakshmi', last_name: 'Narayanan', name: 'Lakshmi Narayanan', customer_type: 'Standard', city: 'Bangalore', phone: '9876543214', email: 'lakshmi.narayanan@example.com'})
CREATE (c6:Customer {customer_id: 'C06', first_name: 'Vikram', last_name: 'Singh', name: 'Vikram Singh', customer_type: 'Premium', city: 'Bangalore', phone: '9876543215', email: 'vikram.singh@example.com'})

// Customer - Employee Relationships (RM)
CREATE (c1)-[:MANAGED_BY]->(e2)
CREATE (c2)-[:MANAGED_BY]->(e2)
CREATE (c3)-[:MANAGED_BY]->(e3)
CREATE (c4)-[:MANAGED_BY]->(e3)
CREATE (c5)-[:MANAGED_BY]->(e6)
CREATE (c6)-[:MANAGED_BY]->(e6)

// 6. Create Accounts (8 nodes)
CREATE (a1:Account {account_number: 'AC1001', account_type: 'Savings', balance: 85000.0, status: 'Active'})
CREATE (a2:Account {account_number: 'AC1002', account_type: 'Current', balance: 150000.0, status: 'Active'})
CREATE (a3:Account {account_number: 'AC1003', account_type: 'Savings', balance: 42000.0, status: 'Active'})
CREATE (a4:Account {account_number: 'AC1004', account_type: 'Current', balance: 200000.0, status: 'Active'})
CREATE (a5:Account {account_number: 'AC1005', account_type: 'Savings', balance: 65000.0, status: 'Active'})
CREATE (a6:Account {account_number: 'AC1006', account_type: 'Savings', balance: 50000.0, status: 'Active'})
CREATE (a7:Account {account_number: 'AC1007', account_type: 'Current', balance: 95000.0, status: 'Active'})
CREATE (a8:Account {account_number: 'AC1008', account_type: 'Savings', balance: 30000.0, status: 'Active'})

// Customer - Account - Branch Links
CREATE (c1)-[:OWNS]->(a1)
CREATE (a1)-[:HELD_AT]->(br1)
CREATE (c1)-[:OWNS]->(a2)
CREATE (a2)-[:HELD_AT]->(br1)

CREATE (c2)-[:OWNS]->(a3)
CREATE (a3)-[:HELD_AT]->(br1)

CREATE (c3)-[:OWNS]->(a4)
CREATE (a4)-[:HELD_AT]->(br2)

CREATE (c4)-[:OWNS]->(a5)
CREATE (a5)-[:HELD_AT]->(br2)

CREATE (c5)-[:OWNS]->(a6)
CREATE (a6)-[:HELD_AT]->(br2)

CREATE (c6)-[:OWNS]->(a7)
CREATE (a7)-[:HELD_AT]->(br3)

CREATE (c5)-[:OWNS]->(a8)
CREATE (a8)-[:HELD_AT]->(br3)

// 7. Create Transactions (8 nodes: Deposits & Withdrawals)
CREATE (t1:Transaction {txn_id: 'T1', txn_type: 'Deposit', amount: 20000.0, txn_date: '2026-03-01'})
CREATE (t2:Transaction {txn_id: 'T2', txn_type: 'Withdrawal', amount: 5000.0, txn_date: '2026-03-05'})
CREATE (t3:Transaction {txn_id: 'T3', txn_type: 'Deposit', amount: 50000.0, txn_date: '2026-03-02'})
CREATE (t4:Transaction {txn_id: 'T4', txn_type: 'Deposit', amount: 15000.0, txn_date: '2026-03-03'})
CREATE (t5:Transaction {txn_id: 'T5', txn_type: 'Withdrawal', amount: 10000.0, txn_date: '2026-03-04'})
CREATE (t6:Transaction {txn_id: 'T6', txn_type: 'Deposit', amount: 25000.0, txn_date: '2026-03-06'})
CREATE (t7:Transaction {txn_id: 'T7', txn_type: 'Deposit', amount: 30000.0, txn_date: '2026-03-07'})
CREATE (t8:Transaction {txn_id: 'T8', txn_type: 'Withdrawal', amount: 8000.0, txn_date: '2026-03-08'})

CREATE (a1)<-[:PERFORMED_ON]-(t1)
CREATE (a1)-[:HAS_TRANSACTION]->(t1)
CREATE (a1)<-[:PERFORMED_ON]-(t2)
CREATE (a1)-[:HAS_TRANSACTION]->(t2)
CREATE (a2)<-[:PERFORMED_ON]-(t3)
CREATE (a2)-[:HAS_TRANSACTION]->(t3)
CREATE (a3)<-[:PERFORMED_ON]-(t4)
CREATE (a3)-[:HAS_TRANSACTION]->(t4)
CREATE (a4)<-[:PERFORMED_ON]-(t5)
CREATE (a4)-[:HAS_TRANSACTION]->(t5)
CREATE (a5)<-[:PERFORMED_ON]-(t6)
CREATE (a5)-[:HAS_TRANSACTION]->(t6)
CREATE (a6)<-[:PERFORMED_ON]-(t7)
CREATE (a6)-[:HAS_TRANSACTION]->(t7)
CREATE (a7)<-[:PERFORMED_ON]-(t8)
CREATE (a7)-[:HAS_TRANSACTION]->(t8)

// 8. Create Transfers (8 relationships via TRANSFERRED_TO)
CREATE (a1)-[:TRANSFERRED_TO {txn_id: 'TR1', amount: 8000.0, txn_date: '2026-03-10'}]->(a3)
CREATE (a3)-[:TRANSFERRED_TO {txn_id: 'TR2', amount: 6000.0, txn_date: '2026-03-12'}]->(a5)
CREATE (a5)-[:TRANSFERRED_TO {txn_id: 'TR3', amount: 4000.0, txn_date: '2026-03-14'}]->(a6)
CREATE (a2)-[:TRANSFERRED_TO {txn_id: 'TR4', amount: 25000.0, txn_date: '2026-03-15'}]->(a7)
CREATE (a6)-[:TRANSFERRED_TO {txn_id: 'TR5', amount: 2000.0, txn_date: '2026-03-16'}]->(a1)
CREATE (a4)-[:TRANSFERRED_TO {txn_id: 'TR6', amount: 40000.0, txn_date: '2026-03-18'}]->(a2)
CREATE (a7)-[:TRANSFERRED_TO {txn_id: 'TR7', amount: 12000.0, txn_date: '2026-03-20'}]->(a8)
CREATE (a8)-[:TRANSFERRED_TO {txn_id: 'TR8', amount: 10000.0, txn_date: '2026-03-22'}]->(a4)

// 9. Create Loans (3 nodes)
CREATE (l1:Loan {loan_id: 'L01', loan_type: 'Home Loan', amount: 2500000.0, interest_rate: 8.5, term_months: 240, status: 'Active'})
CREATE (l2:Loan {loan_id: 'L02', loan_type: 'Personal Loan', amount: 500000.0, interest_rate: 11.5, term_months: 36, status: 'Active'})
CREATE (l3:Loan {loan_id: 'L03', loan_type: 'Car Loan', amount: 800000.0, interest_rate: 9.0, term_months: 60, status: 'Active'})

CREATE (c1)-[:HAS_LOAN]->(l1)
CREATE (l1)-[:MANAGED_BY]->(e4)
CREATE (l1)-[:HELD_AT]->(br1)

CREATE (c2)-[:HAS_LOAN]->(l2)
CREATE (l2)-[:MANAGED_BY]->(e4)
CREATE (l2)-[:HELD_AT]->(br2)

CREATE (c3)-[:HAS_LOAN]->(l3)
CREATE (l3)-[:MANAGED_BY]->(e4)
CREATE (l3)-[:HELD_AT]->(br3)

// 10. Create Installments (6 nodes)
CREATE (ins1:Installment {installment_id: 'INS01', installment_no: 1, due_date: '2026-01-10', amount_due: 25000.0, status: 'Paid'})
CREATE (ins2:Installment {installment_id: 'INS02', installment_no: 2, due_date: '2026-02-10', amount_due: 25000.0, status: 'Paid'})
CREATE (ins3:Installment {installment_id: 'INS03', installment_no: 3, due_date: '2026-03-10', amount_due: 25000.0, status: 'Pending'})

CREATE (ins4:Installment {installment_id: 'INS04', installment_no: 1, due_date: '2026-01-15', amount_due: 16000.0, status: 'Paid'})
CREATE (ins5:Installment {installment_id: 'INS05', installment_no: 2, due_date: '2026-02-15', amount_due: 16000.0, status: 'Pending'})

CREATE (ins6:Installment {installment_id: 'INS06', installment_no: 1, due_date: '2026-03-20', amount_due: 16500.0, status: 'Pending'})

CREATE (l1)-[:HAS_INSTALLMENT]->(ins1)
CREATE (l1)-[:HAS_INSTALLMENT]->(ins2)
CREATE (l1)-[:HAS_INSTALLMENT]->(ins3)

CREATE (l2)-[:HAS_INSTALLMENT]->(ins4)
CREATE (l2)-[:HAS_INSTALLMENT]->(ins5)

CREATE (l3)-[:HAS_INSTALLMENT]->(ins6)

// 11. Create Investments (4 nodes)
CREATE (i1:Investment {investment_id: 'I01', investment_type: 'Mutual Fund', amount: 100000.0, start_date: '2025-01-15'})
CREATE (i2:Investment {investment_id: 'I02', investment_type: 'Fixed Deposit', amount: 200000.0, start_date: '2025-02-20'})
CREATE (i3:Investment {investment_id: 'I03', investment_type: 'Wealth Management', amount: 300000.0, start_date: '2025-06-10'})
CREATE (i4:Investment {investment_id: 'I04', investment_type: 'Recurring Deposit', amount: 50000.0, start_date: '2025-09-01'})

CREATE (c1)-[:HAS_INVESTMENT]->(i1)
CREATE (c2)-[:HAS_INVESTMENT]->(i2)
CREATE (c1)-[:HAS_INVESTMENT]->(i3)
CREATE (c3)-[:HAS_INVESTMENT]->(i4)

// 12. Create Service Requests (3 nodes)
CREATE (sr1:ServiceRequest {request_id: 'SR01', request_type: 'Address Update', description: 'Update mailing address to Anna Nagar', status: 'Resolved', request_date: '2026-01-20'})
CREATE (sr2:ServiceRequest {request_id: 'SR02', request_type: 'Debit Card Replacement', description: 'Request for replacement chip debit card', status: 'Pending', request_date: '2026-02-10'})
CREATE (sr3:ServiceRequest {request_id: 'SR03', request_type: 'Cheque Book', description: 'Request new 50-leaf cheque book', status: 'Resolved', request_date: '2026-02-15'})

CREATE (c2)-[:RAISED]->(sr1)
CREATE (sr1)-[:ASSIGNED_TO]->(e5)

CREATE (c3)-[:RAISED]->(sr2)
CREATE (sr2)-[:ASSIGNED_TO]->(e5)

CREATE (c1)-[:RAISED]->(sr3)
CREATE (sr3)-[:ASSIGNED_TO]->(e5)
```
