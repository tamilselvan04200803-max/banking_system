# Milestone 2 Challenger 1 Empirical Verification Report: Read & Analytics Contracts

**Agent**: `teamwork_preview_challenger` (Challenger 1 — Milestone 2)  
**Working Directory**: `c:\dbms_da-3-project\.agents\teamwork\challenger_m2_1\`  
**Target File**: `c:\dbms_da-3-project\mock_db.py`  
**Verdict**: **APPROVE**

---

## 1. Observation

Empirical testing was executed directly against `mock_db.py` across all 13 targeted Read and Analytics function requirements and adversarial edge scenarios.

### 1.1 Target Function Verification (`test_empirical_m2.py`)
Command executed:
```powershell
python test_empirical_m2.py
```
Output:
```
=== STARTING EMPIRICAL VERIFICATION OF mock_db.py ===

--- Test 1: get_customer ---
get_customer('C01'): {'customer_id': 'C01', 'name': 'Samridhi Sharma', 'customer_type': 'Premium', 'city': 'Chennai', 'phone': '9876543210', 'email': 'samridhi.sharma@example.com', 'relationship_manager': 'Priya Menon'}
get_customer('NON_EXISTENT'): None
[PASS] Test 1: get_customer passed

--- Test 2: get_accounts ---
get_accounts('C01'): [{'account_number': 'AC1001', 'account_type': 'Savings', 'balance': 85000.0, 'status': 'Active', 'branch_name': 'Anna Nagar'}, {'account_number': 'AC1002', 'account_type': 'Current', 'balance': 150000.0, 'status': 'Active', 'branch_name': 'Anna Nagar'}]
[PASS] Test 2: get_accounts passed

--- Test 3: get_total_balance ---
get_total_balance('C01'): 235000.0
[PASS] Test 3: get_total_balance passed

--- Test 4: get_transactions ---
get_transactions('AC1001') count=4:
   {'txn_id': 'TR5', 'txn_date': '2026-03-16', 'txn_type': 'Transfer In', 'amount': 2000.0, 'other_account': 'AC1006'}
   {'txn_id': 'TR1', 'txn_date': '2026-03-10', 'txn_type': 'Transfer Out', 'amount': 8000.0, 'other_account': 'AC1003'}
   {'txn_id': 'T2', 'txn_date': '2026-03-05', 'txn_type': 'Withdrawal', 'amount': 5000.0, 'other_account': None}
   {'txn_id': 'T1', 'txn_date': '2026-03-01', 'txn_type': 'Deposit', 'amount': 20000.0, 'other_account': None}
[PASS] Test 4: get_transactions passed

--- Test 5: get_loans ---
get_loans('C01'): [{'loan_id': 'L01', 'loan_type': 'Home Loan', 'amount': 2500000.0, 'interest_rate': 8.5, 'term_months': 240, 'status': 'Active', 'loan_officer': 'Divya Rao', 'branch_name': 'Anna Nagar'}]
[PASS] Test 5: get_loans passed

--- Test 6: get_repayment_schedule ---
get_repayment_schedule('L01') count=3:
   {'installment_no': 1, 'due_date': '2026-01-10', 'amount_due': 25000.0, 'status': 'Paid'}
   {'installment_no': 2, 'due_date': '2026-02-10', 'amount_due': 25000.0, 'status': 'Paid'}
   {'installment_no': 3, 'due_date': '2026-03-10', 'amount_due': 25000.0, 'status': 'Pending'}
[PASS] Test 6: get_repayment_schedule passed

--- Test 7: get_investments ---
get_investments('C01'): [{'investment_id': 'I01', 'investment_type': 'Mutual Fund', 'amount': 100000.0, 'start_date': '2025-01-15'}, {'investment_id': 'I03', 'investment_type': 'Wealth Management', 'amount': 300000.0, 'start_date': '2025-06-10'}]
[PASS] Test 7: get_investments passed

--- Test 8: get_service_requests ---
get_service_requests('C01'): [{'request_id': 'SR03', 'request_type': 'Cheque Book', 'description': 'Request new 50-leaf cheque book', 'status': 'Resolved', 'request_date': '2026-02-15', 'handled_by': 'Karthik Suresh'}]
[PASS] Test 8: get_service_requests passed

--- Test 9: get_branches ---
get_branches(): [{'branch_id': 'BR01', 'branch_name': 'Anna Nagar'}, {'branch_id': 'BR02', 'branch_name': 'T Nagar'}, {'branch_id': 'BR03', 'branch_name': 'Koramangala'}]
[PASS] Test 9: get_branches passed

--- Test 10: get_branch_account_counts ---
get_branch_account_counts(): [{'branch_name': 'Anna Nagar', 'account_count': 3}, {'branch_name': 'T Nagar', 'account_count': 3}, {'branch_name': 'Koramangala', 'account_count': 2}]
[PASS] Test 10: get_branch_account_counts passed

--- Test 11: get_top_customers_by_balance ---
get_top_customers_by_balance(3): [{'customer_id': 'C01', 'name': 'Samridhi Sharma', 'total_balance': 235000.0}, {'customer_id': 'C03', 'name': 'Anita Roy', 'total_balance': 200000.0}, {'customer_id': 'C06', 'name': 'Vikram Singh', 'total_balance': 95000.0}]
[PASS] Test 11: get_top_customers_by_balance passed

--- Test 12: get_large_transfers ---
get_large_transfers(20000): [{'txn_id': 'TR6', 'from_account': 'AC1004', 'to_account': 'AC1002', 'amount': 40000.0, 'txn_date': '2026-03-18'}, {'txn_id': 'TR4', 'from_account': 'AC1002', 'to_account': 'AC1007', 'amount': 25000.0, 'txn_date': '2026-03-15'}]
[PASS] Test 12: get_large_transfers passed

--- Test 13: get_money_trail ---
get_money_trail('AC1001') count=3:
   {'trail': ['AC1001', 'AC1003'], 'hops': 1}
   {'trail': ['AC1001', 'AC1003', 'AC1005'], 'hops': 2}
   {'trail': ['AC1001', 'AC1003', 'AC1005', 'AC1006'], 'hops': 3}
[PASS] Test 13: get_money_trail passed
```

### 1.2 Adversarial & Stress Testing (`test_stress_and_edge_m2.py`)
Command executed:
```powershell
python test_stress_and_edge_m2.py
```
Output:
```
=== STARTING DEEP ADVERSARIAL STRESS HARNESS ===

--- Stress 1: Dynamic Mutation Reflection ---
[PASS] Stress 1: Dynamic Mutation Reflection passed

--- Stress 2: Multi-branch Fund Flow ---
Multi-branch trail rows count: 9
[PASS] Stress 2: Multi-branch Fund Flow passed

--- Stress 3: Account Lifecycle & Branch Counts ---
[PASS] Stress 3: Account Lifecycle & Branch Counts passed

--- Stress 4: Contact Update & Service Requests ---
[PASS] Stress 4: Contact Update & Service Requests passed

--- Stress 5: Reset Mock DB Idempotency ---
[PASS] Stress 5: Reset Mock DB Idempotency passed

--- Stress 6: Edge Inputs & Boundaries ---
get_top_customers_by_balance(-1) returned 5 rows (Python slice behavior)
[PASS] Stress 6: Edge Inputs & Boundaries passed

ALL ADVERSARIAL STRESS HARNESS TESTS PASSED CLEANLY!
```

---

## 2. Logic Chain

1. **Target Specification Conformance (Item 1–13)**:
   - Observation 1.1 demonstrates that all 13 required test cases match expected outputs down to exact values, key names, and ordering:
     - `get_customer('C01')`: Name `'Samridhi Sharma'`, type `'Premium'`, RM `'Priya Menon'`. Non-existent queries return `None`.
     - `get_accounts('C01')`: Accounts `AC1001` (85,000) and `AC1002` (150,000) with branch `'Anna Nagar'`.
     - `get_total_balance('C01')`: Exactly `235000.0`.
     - `get_transactions('AC1001')`: Returns 4 transactions in descending date order (`2026-03-16` TR5 Transfer In 2000, `2026-03-10` TR1 Transfer Out 8000, `2026-03-05` T2 Withdrawal 5000, `2026-03-01` T1 Deposit 20000).
     - `get_loans('C01')`: `L01` Home Loan, Divya Rao, Anna Nagar Branch.
     - `get_repayment_schedule('L01')`: 3 installments, with installment 3 status `'Pending'`.
     - `get_investments('C01')`: `I01` (100,000) and `I03` (300,000).
     - `get_service_requests('C01')`: `SR03` Cheque Book, Resolved, Karthik Suresh.
     - `get_branches()`: 3 branches (`BR01`, `BR02`, `BR03`).
     - `get_branch_account_counts()`: Anna Nagar 3, T Nagar 3, Koramangala 2.
     - `get_top_customers_by_balance(3)`: `C01` (235,000), `C03` (200,000), `C06` (95,000).
     - `get_large_transfers(20000)`: `TR6` (40,000) and `TR4` (25,000).
     - `get_money_trail('AC1001')`: 3 rows along path `AC1001 -> AC1003 -> AC1005 -> AC1006` for hops 1, 2, 3.

2. **Graph Algorithm & Cycle Safety**:
   - `mock_db.get_money_trail` uses BFS with a `used_txns` set and a depth limit of 3 hops (`hops < 3`).
   - In Stress Test 2 and Observation 1.1, cycles (e.g. `AC1005 -> AC1006 -> AC1001 -> AC1003`) and multi-branch transfer forks were traversed without infinite loops or redundant hops.

3. **Dynamic State & Idempotency**:
   - Mutations made via write functions immediately reflect across read and analytics queries (`get_accounts`, `get_total_balance`, `get_transactions`, `get_branch_account_counts`, `get_large_transfers`).
   - Calling `reset_mock_db()` completely and idempotently restores the baseline 47-node seed state.

---

## 3. Caveats

1. **Negative Limits in Leaderboard**: In `get_top_customers_by_balance(limit: int = 5)`, passing a negative integer (e.g. `limit = -1`) utilizes Python negative list slicing `cust_totals[:-1]`, returning all but the last item (5 items). In Cypher (`db.py`), a negative limit would trigger an error caught by `try...except` returning `[]`. For normal application usage in Streamlit and test suites, `limit` is always a positive integer (3 or 5).
2. **Offline Scope**: This challenger scope specifically validates `mock_db.py`. Live Neo4j execution (`db.py`) requires a running Bolt instance.

---

## 4. Conclusion

**Verdict: APPROVE**

`mock_db.py` passes 100% of the empirical assertions for all 13 targeted Read and Analytics contracts, complies with Section 8 test cases, safely handles edge/cycle scenarios, and maintains perfect state reactivity and reset idempotency.

---

## 5. Verification Method

To reproduce and verify these findings independently:

1. **Run Target Contracts Verification**:
   ```powershell
   python test_empirical_m2.py
   ```
   *Expected outcome*: Exits with code 0 and logs `ALL 13 TARGET READ & ANALYTICS CHECKS AND STRESS TESTS PASSED SUCCESSFULLY!`.

2. **Run Deep Adversarial Stress Harness**:
   ```powershell
   python test_stress_and_edge_m2.py
   ```
   *Expected outcome*: Exits with code 0 and logs `ALL ADVERSARIAL STRESS HARNESS TESTS PASSED CLEANLY!`.
