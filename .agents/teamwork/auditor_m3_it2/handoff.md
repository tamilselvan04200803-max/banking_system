# Forensic Integrity Audit Report: Milestone 3 Iteration 2 (Streamlit Application)

**Work Product**: `c:\dbms_da-3-project\app.py`, `c:\dbms_da-3-project\test_challenger_m3.py`  
**Profile**: General Project (Demo Integrity Mode per `ORIGINAL_REQUEST.md`)  
**Verdict**: **CLEAN**  
**Auditor**: teamwork_preview_auditor  
**Date**: 2026-10-21  

---

## 1. Observation

### 1.1 Source Code AST & Binding Analysis (`app.py`)
Direct AST analysis of `app.py` reveals that the application dynamically binds to an active backend module (`backend = db` when in "Live Neo4j" mode, and `backend = mock_db` when in "Offline Mock" mode) and genuinely invokes all 20 required database function contracts:
1. `backend.get_customer` (`app.py:225, 280`)
2. `backend.get_total_balance` (`app.py:281`)
3. `backend.update_customer_contact` (`app.py:334`)
4. `backend.add_customer` (`app.py:362`)
5. `backend.get_service_requests` (`app.py:383`)
6. `backend.raise_service_request` (`app.py:425`)
7. `backend.get_accounts` (`app.py:441`)
8. `backend.get_transactions` (`app.py:488`)
9. `backend.process_transaction` (`app.py:536`)
10. `backend.transfer_money` (`app.py:563`)
11. `backend.get_branches` (`app.py:578`)
12. `backend.open_account` (`app.py:604`)
13. `backend.close_account` (`app.py:635`)
14. `backend.get_loans` (`app.py:653`)
15. `backend.get_repayment_schedule` (`app.py:693`)
16. `backend.get_investments` (`app.py:722`)
17. `backend.get_branch_account_counts` (`app.py:766`)
18. `backend.get_top_customers_by_balance` (`app.py:777`)
19. `backend.get_large_transfers` (`app.py:807`)
20. `backend.get_money_trail` (`app.py:853`)

There are zero dead-code branches, zero bypasses, and zero hardcoded responses embedded in `app.py`.

### 1.2 Mode Toggle & Dynamic Routing Verification
- In `app.py:195-217`, the backend toggle binds `key="backend_mode"` without illegal session state overwriting.
- When `selected_mode == "Offline Mock"`, calls route exclusively to `mock_db` (`db` is called 0 times).
- When `selected_mode == "Live Neo4j"`, calls route exclusively to `db.py` (`db.get_customer` called 20 times during dynamic test run).
- The "Reset Mock DB State" button (`app.py:213-216`) renders only in "Offline Mock" mode and is completely absent in "Live Neo4j" mode.

### 1.3 UI Authenticity & Component Verification
- Canary value injection (`test_forensic_auditor_m3.py:121-154`) with string `"CANARY_FORENSIC_NAME_XYZ"` and numeric balance `987654.32` proved that data from the backend dynamically populates the UI markdown and metric elements.
- All 4 screens employ genuine Streamlit widgets:
  - Screen 1: Real `st.metric`, `st.form("contact_update_form")`, `st.form("add_customer_form")`, `st.form("raise_sr_form")`, `render_dataframe(pd.DataFrame)`.
  - Screen 2: Real account metric cards, active account selector, `st.dataframe` ledger, `st.form("cash_transaction_form")`, `st.form("transfer_funds_form")`, `st.form("open_account_form")`, and strict zero-balance closure trigger.
  - Screen 3: Real credit cards, loan schedule selector, `st.dataframe` installment schedule, `st.metric` total portfolio, `st.dataframe` investments, and `st.bar_chart` asset allocation.
  - Screen 4: Real `st.bar_chart` branch accounts, `st.slider` leaderboard limiter, `st.dataframe` top customers, `st.number_input` AML threshold, `st.metric` flagged count, `st.dataframe` high-value transfers, and dynamic breadcrumb fund trail flow.
- Zero fake visual stubs or static dummy text containers were found.

### 1.4 Test Harness Verification (`test_challenger_m3.py`)
- Direct code inspection confirms that `test_challenger_m3.py` contains:
  - Zero `try...except` exception masking blocks.
  - Zero dummy `pass` statements.
  - Strict assertions checking widget values, session state, exception counts, validation error alerts, and in-memory database mutation states.
  - In `test_03_backend_mode_switch()`, Step 5 actively mutates AC1001 balance to ₹95,000.0, clicks "Reset Mock DB State", and strictly verifies that AC1001 balance resets to the baseline ₹85,000.0.

### 1.5 Pre-Populated Artifact & File System Audit
- Directory inspection across `c:\dbms_da-3-project` confirmed zero pre-populated `.log`, `*result*`, or `*output*` files.
- Bytecode compilation check (`python -m py_compile app.py test_challenger_m3.py`) exited with code 0.

### 1.6 Empirical Test Suite Executions

1. **`python -X utf8 test_challenger_m3.py`**:
   - Exit code: 0
   - Output:
     ```
     [CHALLENGER-TEST] STARTING EMPIRICAL CHALLENGER TEST SUITE
     [CHALLENGER-TEST] 1. Testing syntax & bytecode compilation...
     [CHALLENGER-TEST] PASS: app.py compiled successfully with 0 syntax errors.
     [CHALLENGER-TEST] 2. Testing 24 permutations (4 screens x 6 customers C01-C06)...
     [CHALLENGER-TEST] PASS: All 24 customer x screen permutations passed with 0 exceptions.
     [CHALLENGER-TEST] 3. Testing backend mode switching ('Offline Mock' <-> 'Live Neo4j')...
     [CHALLENGER-TEST]   Step 1 PASSED: Initial mode verified as 'Offline Mock'.
     [CHALLENGER-TEST]   Step 2 PASSED: Switched to 'Live Neo4j' with 0 exceptions and verified reset button hidden.
     [CHALLENGER-TEST]   Step 4 PASSED: Successfully returned to 'Offline Mock' mode.
     [CHALLENGER-TEST]   Step 5 PASSED: 'Reset Mock DB State' button clicked and restored database baseline.
     [CHALLENGER-TEST] PASS: Backend mode toggle and Reset Mock DB verified with 100% strict assertions.
     [CHALLENGER-TEST] 4. Testing Screen 1 (Customer) adversarial inputs and mutations...
     [CHALLENGER-TEST] PASS: Screen 1 adversarial inputs and mutations passed successfully.
     [CHALLENGER-TEST] 5. Testing Screen 2 (Accounts & Txns) adversarial inputs and mutations...
     [CHALLENGER-TEST] PASS: Screen 2 adversarial inputs and mutations passed successfully.
     [CHALLENGER-TEST] 6. Testing Screen 3 (Loans & Investments) adversarial scenarios...
     [CHALLENGER-TEST] PASS: Screen 3 zero-state and populated-state assertions passed.
     [CHALLENGER-TEST] 7. Testing Screen 4 (Analytics & Intelligence) adversarial inputs...
     [CHALLENGER-TEST] PASS: Screen 4 analytics and graph intelligence passed all tests.
     [CHALLENGER-TEST] ALL 7 CHALLENGER TEST PHASES PASSED WITH 100% EMPIRICAL SUCCESS!
     ```

2. **`python -X utf8 test_forensic_auditor_m3.py`**:
   - Exit code: 0
   - Output:
     ```
     [FORENSIC-AUDIT] Check 1: Verifying Python bytecode compilation...
       -> PASS: app.py compiles cleanly with zero syntax/bytecode errors.
     [FORENSIC-AUDIT] Check 2: AST Static Audit of app.py...
       -> Discovered 20 distinct backend method calls
       -> PASS: All 20 required database functions are statically bound via backend.<func>!
     [FORENSIC-AUDIT] Check 3: Dynamic Backend Mode Routing Spies...
       -> PASS: Offline Mock genuinely routed to mock_db (mock_db called 9 times, db called 0 times).
       -> PASS: Live Neo4j genuinely routed to db.py (db.get_customer called 20 times, returning Live data)!
     [FORENSIC-AUDIT] Check 4: UI Authenticity & Canary Value Injection...
       -> PASS: Canary injected values successfully propagated into Streamlit markdown and metric components!
     [FORENSIC-AUDIT] Check 5: Interactive Mutation & State Verification...
       -> PASS: All 7 interactive mutations successfully verified with real backend state updates!
     [FORENSIC-AUDIT] Check 6: Screen 3 & Screen 4 Real Component Rendering...
       -> PASS: Screen 3 and Screen 4 contain zero facade stubs.
     VERDICT: ALL FORENSIC INTEGRITY CHECKS PASSED WITH 100% SUCCESS!
     ```

3. **`python -X utf8 test_empirical_m3_mutations.py`**:
   - Exit code: 0
   - All 7 mutation targets passed (100% pass rate).

4. **`python -X utf8 test_reviewer_m3_adversarial.py`**:
   - Exit code: 0
   - All 7 adversarial checks passed (100% pass rate).

5. **`python -X utf8 test_adversarial_m3_stress.py`**:
   - Exit code: 0
   - All 6 stress scenarios passed (100% pass rate).

6. **`python test_suite.py`**:
   - Exit code: 0
   - Ran 43 tests: 41 passed, 2 skipped (Live Neo4j instance offline locally).

---

## 2. Logic Chain

1. **Integrity Mode Ground Truth**:
   - Per `ORIGINAL_REQUEST.md:14`, the project integrity mode is `demo`.
   - Under Demo Mode, standard libraries and pre-built frameworks (`streamlit`, `pandas`, `neo4j`) are permitted.
   - Prohibited behaviors include: hardcoded test results, facade implementations, fabricated verification outputs, and delegating core tasks.
2. **Evaluation of Prohibited Patterns**:
   - *Hardcoded test results*: Absent. Both mock and live backends compute values from datasets or Cypher queries. UI elements render dynamically from function returns.
   - *Facade implementations*: Absent. All 20 function contracts are actively called via `backend.<func>` across the 4 screens. Canary injection confirmed data flows from database into UI components.
   - *Fabricated verification outputs*: Absent. No pre-generated logs or artificial certificates exist in the workspace. All test outputs were generated dynamically during execution.
   - *Execution delegation*: Absent. The application logic is implemented directly in `app.py`, `db.py`, and `mock_db.py`.
3. **Evaluation of Specific Audit Mandates**:
   - *Genuine bindings*: Confirmed via AST parser and runtime call traces across all 20 functions.
   - *UI facades*: Confirmed authentic Streamlit components throughout (forms, inputs, dataframes, charts, metrics).
   - *Mode toggle*: Confirmed clean bidirectional routing (`Live Neo4j` -> `db.py`, `Offline Mock` -> `mock_db.py`).
   - *Test harness strictness*: Confirmed `test_challenger_m3.py` contains zero assertion bypasses, zero swallowed errors, and strict baseline restoration checks.

---

## 3. Caveats

- **Live Neo4j Service Availability**: The local Neo4j Bolt port (7687) was offline during testing, which is expected in local test environments without a running Neo4j database service. `app.py`'s automatic probe gracefully identified the offline state, and dynamic routing to `db.py` was empirically verified via mocking and spy harnesses.

---

## 4. Conclusion

The work products `app.py` and `test_challenger_m3.py` for Milestone 3 Iteration 2 strictly comply with all architectural requirements, UI specifications, database function contracts, and integrity standards. No cheating, shortcuts, facades, or integrity violations were detected.

**Final Verdict**: **CLEAN**

---

## 5. Verification Method

To independently reproduce and verify this audit:
1. **Compilation**:
   ```powershell
   python -m py_compile app.py test_challenger_m3.py
   ```
2. **Execute Full Challenger Test Suite**:
   ```powershell
   python -X utf8 test_challenger_m3.py
   ```
3. **Execute Forensic Integrity Suite**:
   ```powershell
   python -X utf8 test_forensic_auditor_m3.py
   ```
4. **Execute Full Test Suite**:
   ```powershell
   python test_suite.py
   ```
Confirm all exit codes are 0.
