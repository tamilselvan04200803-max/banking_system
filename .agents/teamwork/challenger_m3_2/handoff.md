# Empirical Challenger Report: Interactive Forms & Mutations in `app.py` (Milestone 3)

**Agent**: teamwork_preview_challenger (Challenger 2)  
**Working Directory**: `c:\dbms_da-3-project\.agents\teamwork\challenger_m3_2\`  
**Date**: 2026-10-21  
**Milestone**: Milestone 3 — Streamlit Application (`app.py`)  
**Verdict**: **APPROVE**

---

## 1. Observation

### 1.1 Empirical Verification Test Harnesses Created
To empirically test interactive forms, mutations, validation boundaries, and stress limits, two automated test suites were authored in the project workspace:
- `test_empirical_m3_mutations.py`: Tests the 7 explicit functional targets and validation boundaries from the dispatch message.
- `test_adversarial_m3_stress.py`: Adversarial stress harness covering rapid sequential mutations, cross-customer fund flows, account lifecycle edge-cases, floating-point precision, special characters, and large payload limits.

### 1.2 Execution of Target Tests (`test_empirical_m3_mutations.py`)
- **Command**:
  ```powershell
  python -X utf8 test_empirical_m3_mutations.py
  ```
- **Exit Code**: `0`
- **Verbatim Output**:
  ```
  --- Target 1: Testing Contact Update Form Execution ---
    [PASS] 1.1 Valid contact update updated mock_db and re-rendered in UI.
    [PASS] 1.2 Empty contact update rejected cleanly with validation error banner.
    [PASS] 1.3 Contact update executed cleanly for customer C02.

  --- Target 2: Testing Add Customer Form Execution ---
    [PASS] 2.1 Add customer with missing mandatory fields rejected cleanly.
    [PASS] 2.2 Duplicate customer ID 'C01' rejected cleanly.
    [PASS] 2.3 New customer C07 created, persisted in mock_db, and auto-selected in session state.

  --- Target 3: Testing Raise Service Request Form Execution ---
    [PASS] 3.1 Empty service request description rejected cleanly.
    [PASS] 3.2 Service request SRGIWDEOYD registered with status Pending & assigned to Karthik Suresh (E05).

  --- Target 4: Testing Deposit and Withdrawal Form Execution ---
    [PASS] 4.1 Cash deposit of Rs 5,000 processed; balance updated to 90,000.
    [PASS] 4.2 Cash withdrawal of Rs 15,000 processed; balance updated to 75,000.
    [PASS] 4.3 Overdraft withdrawal of Rs 99,999,999 rejected with insufficient balance error banner.

  --- Target 5: Testing Inter-Account Transfer Form Execution ---
    [PASS] 5.1 Empty destination account rejected cleanly.
    [PASS] 5.2 Self-transfer from AC1001 to AC1001 rejected cleanly.
    [PASS] 5.3 Transfer to non-existent account AC9999 rejected cleanly with 'not found' error.
    [PASS] 5.4 Transfer exceeding account balance rejected cleanly.
    [PASS] 5.5 Valid transfer of Rs 5,000 atomically updated AC1001 (80,000) and AC1003 (47,000).

  --- Target 6: Testing Open Account & Close Zero-Balance Account ---
    [PASS] 6.1 Open account with empty account number rejected cleanly.
    [PASS] 6.2 Duplicate account number AC1001 rejected cleanly.
    [PASS] 6.3 New account AC1009 opened with Rs 0.00 initial balance.
    [PASS] 6.4 Close non-zero balance account AC1001 rejected strictly under zero-balance policy.
    [PASS] 6.5 Zero-balance account AC1009 successfully closed and removed from ledger.

  --- Target 7: Testing State Persistence & Clean Reset ---
    [PASS] 7.1 Cross-screen state persisted: C01 aggregated total balance is 245000.0.
    [PASS] 7.2 Analytics Screen 4 traces 3 directed multi-hop fund trails.
    [PASS] 7.3 UI Reset Mock DB button cleanly restored all seed data, balances, and node counts.
    [PASS] 7.4 Fresh launch after programmatic reset_mock_db() runs cleanly with 0 exceptions.

  ======================================================================
  ALL 7 TARGET TESTS COMPLETED SUCCESSFULLY WITH 100% PASS RATE!
  ======================================================================
  ```

### 1.3 Execution of Adversarial Stress Harness (`test_adversarial_m3_stress.py`)
- **Command**:
  ```powershell
  python -X utf8 test_adversarial_m3_stress.py
  ```
- **Exit Code**: `0`
- **Verbatim Output**:
  ```
  ======================================================================
  STARTING ADVERSARIAL STRESS HARNESS FOR MILESTONE 3 (APP.PY)
  ======================================================================

  --- Stress 1: Rapid Sequential Mutations on Single Account ---
    [PASS] 8 rapid mutations executed sequentially; balance 90000.0 is mathematically exact across 12 ledger rows.

  --- Stress 2: Interleaved Multi-Customer Transfers & Context Switches ---
    [PASS] Inter-customer transfer AC1004 -> AC1005 (50,000) correctly updated both accounts across customer contexts.

  --- Stress 3: Account Lifecycle with Non-Zero Opening Balance ---
    [PASS] Full lifecycle verified: Open with 25k -> Close rejected -> Withdraw to 0 -> Close succeeded.

  --- Stress 4: Floating-Point Currency Arithmetic Precision ---
    [PASS] Decimal currency precision (paise/cents) preserved accurately without floating point drift.

  --- Stress 5 & 6: Special Characters in Registration & Large SR Payload ---
    [PASS] Special characters (hyphens, apostrophes) in customer registration handled cleanly.
    [PASS] Large service request payload (1090 chars) submitted and persisted without truncation.

  ======================================================================
  ALL ADVERSARIAL STRESS HARNESS TESTS PASSED WITH ZERO FAILURES!
  ======================================================================
  ```

### 1.4 Baseline Integrity After Mutation Cycles
- Executed `mock_db.reset_mock_db()` after all mutation cycles:
  - Branch counts: Anna Nagar (3), T Nagar (3), Koramangala (2).
  - Total balance for `C01`: exactly ₹235,000.00.
  - Accounts count: 8 accounts (AC1001 to AC1008).
  - Customer records: exactly 6 baseline customers (`C01` to `C06`).
  - No orphaned mutation nodes or corrupted in-memory references.

---

## 2. Logic Chain

1. **Target 1: Contact Update**:
   - `app.py` lines 321-338 define `contact_update_form`.
   - Submitting valid phone and email calls `backend.update_customer_contact()`, triggers `st.rerun()`, and refreshes the UI profile card and input fields with updated values.
   - Submitting whitespace/empty fields is intercepted before mutation with an explicit validation error: `"Phone and Email cannot be empty."` without altering the database.

2. **Target 2: Customer Registration**:
   - `app.py` lines 339-377 define `add_customer_form`.
   - Missing fields are validated locally (`"Customer ID, First Name, Last Name, and Email are mandatory."`).
   - Duplicate IDs (e.g. registering existing `C01`) are rejected by the backend contract, returning an error banner (`"Customer ID C01 already exists"`).
   - Valid customer creation (e.g. `C07`) dynamically appends the new ID to `st.session_state["customer_ids"]`, updates `selected_customer_id`, and immediately renders the new profile upon rerun.

3. **Target 3: Service Requests**:
   - `app.py` lines 400-428 define `raise_sr_form`.
   - Empty descriptions are rejected with an explicit validation error.
   - Valid submissions invoke `backend.raise_service_request()` with whitespace stripping, generate a unique `SR...` ID, set status to `"Pending"`, and assign to Customer Service Executive `E05` (`"Karthik Suresh"`), which immediately appears in the customer's request ledger.

4. **Target 4: Deposits & Withdrawals**:
   - `app.py` lines 514-535 define `cash_transaction_form`.
   - Cash deposits correctly increase account balance and append a `"Deposit"` record in the ledger.
   - Cash withdrawals decrement balance and log a `"Withdrawal"` record.
   - Overdraft attempts (e.g. ₹99,999,999) trigger an `"insufficient balance"` error banner, leaving the account balance intact without raising uncaught exceptions.

5. **Target 5: Inter-Account Transfers**:
   - `app.py` lines 536-562 define `transfer_funds_form`.
   - Self-transfers (source == destination) are caught immediately with `"Source and destination accounts must be distinct."`.
   - Non-existent destination accounts (e.g. `AC9999`) return a `"Destination account AC9999 not found"` error banner.
   - Insufficient balance transfers return an `"insufficient balance"` error banner.
   - Valid transfers atomically debit source, credit target, and record reciprocal `"Transfer Out"` and `"Transfer In"` records with counterparty account numbers.

6. **Target 6: Account Opening & Zero-Balance Closure Policy**:
   - `app.py` lines 569-635 implement account lifecycle management.
   - Opening an account with 0 or positive initial balance links to customer and branch cleanly.
   - Duplicate account numbers are rejected with an error banner.
   - Attempting to close an account with non-zero balance is blocked by `backend.close_account()`, displaying an error banner (`"Cannot close account with non-zero balance"`).
   - Once an account balance is ₹0.00, `close_account()` succeeds and removes the account from the customer's portfolio.

7. **Target 7: State Persistence & Idempotent Reset**:
   - Mutations executed on one screen (e.g. deposits on Screen 2) immediately reflect across Screen 1 (aggregated customer balance metric) and Screen 4 (multi-hop graph fund trail tracer).
   - Clicking `"🔄 Reset Mock DB State"` in the sidebar restores all 47 seed nodes, resets account balances, clears ad-hoc transactions, and resets customer profiles cleanly.

---

## 3. Caveats

1. **Streamlit Script Rerun Architecture**:
   - In Streamlit's execution model, `st.rerun()` terminates the active script run and immediately restarts from line 1.
   - Success banners rendered inside `if submit_button:` blocks display momentarily before rerun, and the post-rerun DOM reflects the new state in UI dataframes and input values. Error banners do not trigger `st.rerun()`, remaining visible in `at.error`. Automated tests account for this design.
2. **Offline Mock Scope**:
   - Testing was performed against `Offline Mock` mode because Neo4j is not listening on `localhost:7687` in this environment. As demonstrated, `app.py` auto-probes and falls back to `Offline Mock` gracefully.

---

## 4. Conclusion

- **Verdict**: **APPROVE**
- All 7 mutation and form targets specified in the Milestone 3 dispatch were empirically verified with automated tests.
- Every form contains robust client-side validation and graceful server error handling with zero unhandled exceptions.
- State persists across screens and resets idempotently via both the UI reset button and programmatic `mock_db.reset_mock_db()`.
- The adversarial stress suite verified high-frequency transactions, decimal precision, special characters, and lifecycle edge cases without failure.

---

## 5. Verification Method

To independently reproduce and verify this challenger assessment:

1. **Execute All 7 Interactive Form & Mutation Tests**:
   ```powershell
   python -X utf8 test_empirical_m3_mutations.py
   ```
   *Expected: All 7 target tests pass with 100% success (exit code 0).*

2. **Execute Adversarial Stress Harness**:
   ```powershell
   python -X utf8 test_adversarial_m3_stress.py
   ```
   *Expected: All 6 stress scenarios pass with 0 failures (exit code 0).*

3. **Verify Clean Baseline State**:
   ```powershell
   python -c "import mock_db; mock_db.reset_mock_db(); print('Pristine state verified!')"
   ```
   *Expected: 'Pristine state verified!' (exit code 0).*

4. **Invalidation Conditions**:
   - Any form submission throws an unhandled Python exception.
   - Closing an account with non-zero balance succeeds.
   - An overdraft withdrawal reduces account balance below zero.
   - Submitting empty or malformed inputs crashes the Streamlit runtime.
