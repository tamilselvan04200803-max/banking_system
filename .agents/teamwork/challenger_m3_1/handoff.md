# Challenger Evaluation Report: Milestone 3 Streamlit Application (`app.py`)

**Challenger**: teamwork_preview_challenger (Challenger 1)  
**Working Directory**: `c:\dbms_da-3-project\.agents\teamwork\challenger_m3_1\`  
**Date**: 2026-10-21  
**Milestone**: Milestone 3 — Streamlit Web Application (`app.py`)  
**Verdict**: **REQUEST_CHANGES**

---

## 1. Observation

### 1.1 Navigation Matrix Verification (24 Permutations)
- **Tool**: `streamlit.testing.v1.AppTest` executed via `test_challenger_m3.py`.
- **Command**:
  ```powershell
  python -X utf8 test_challenger_m3.py
  ```
- **Observations**:
  - Initialized `AppTest` from `app.py`.
  - Iterated all 6 seed customers (`C01`, `C02`, `C03`, `C04`, `C05`, `C06`) across all 4 screens:
    1. `1. Customer Profile & Services`
    2. `2. Accounts & Transactions`
    3. `3. Loans & Investments`
    4. `4. Analytics & Graph Intelligence`
  - Verbatim Log Output:
    ```
    [CHALLENGER-TEST] 2. Testing 24 permutations (4 screens x 6 customers C01-C06)...
    [CHALLENGER-TEST]   Verified permutation 1/24: Customer=C01 | Screen='1. Customer Profile & Services' -> 0 exceptions
    ...
    [CHALLENGER-TEST]   Verified permutation 24/24: Customer=C06 | Screen='4. Analytics & Graph Intelligence' -> 0 exceptions
    [CHALLENGER-TEST] PASS: All 24 customer x screen permutations passed with 0 exceptions.
    ```
  - Result: `len(at.exception) == 0` across all 24 permutations.

### 1.2 Mode Switch Verification & Discovery of Bug #1 (Mode Toggle Trap)
- **Test**: Switching from `"Offline Mock"` -> `"Live Neo4j"`, then switching back from `"Live Neo4j"` -> `"Offline Mock"`.
- **Observations**:
  1. Switching to `"Live Neo4j"` succeeds with 0 exceptions (`at.sidebar.radio[0].set_value("Live Neo4j").run()`).
  2. Attempting to switch back to `"Offline Mock"` fails silently:
     ```python
     at.sidebar.radio[0].set_value("Offline Mock").run()
     print(at.sidebar.radio[0].value)               # Output: 'Live Neo4j'
     print(at.session_state["backend_mode"])       # Output: 'Live Neo4j'
     ```
  3. **Root Cause**: In `c:\dbms_da-3-project\app.py`, lines 195–201:
     ```python
     selected_mode = st.sidebar.radio(
         "Active Data Backend",
         options=["Live Neo4j", "Offline Mock"],
         index=0 if st.session_state["backend_mode"] == "Live Neo4j" else 1,
         help="Switch between live Neo4j database or the deterministic in-memory offline mock dataset.",
     )
     st.session_state["backend_mode"] = selected_mode
     ```
     Because `key="backend_mode"` is omitted and `index` is dynamically evaluated from `st.session_state["backend_mode"]`, on the rerun triggered by selecting `"Offline Mock"`, `st.session_state["backend_mode"]` is still `"Live Neo4j"` at the moment `st.sidebar.radio` is evaluated. Streamlit passes `index=0`, which immediately forces the widget value back to `"Live Neo4j"`.
  4. **Empirical Reproduction**:
     ```powershell
     python -c "
     from streamlit.testing.v1 import AppTest
     at = AppTest.from_file('app.py', default_timeout=90).run()
     at.sidebar.radio[0].set_value('Live Neo4j').run()
     at.sidebar.radio[0].set_value('Offline Mock').run()
     print('Active mode:', at.session_state['backend_mode'])
     assert at.session_state['backend_mode'] == 'Offline Mock'
     "
     ```
     Verbatim Output:
     ```
     Active mode: Live Neo4j
     AssertionError
     ```
  5. **Consequence**: Once a user selects `"Live Neo4j"` in the sidebar toggle, they are permanently locked into Live mode. In an offline environment (where Neo4j is not running), this causes every subsequent interaction to wait ~40 seconds on Bolt socket timeouts, and the user can never switch back to `"Offline Mock"`. Furthermore, the `"🔄 Reset Mock DB State"` button is rendered only when in `"Offline Mock"` mode, making it permanently inaccessible.

### 1.3 Interactive Mutation & Adversarial Edge Cases
- **Screens 1–4 Stress Testing**:
  - Screen 1: Empty contact update rejected with error banner; duplicate customer ID `C01` rejected; missing mandatory customer registration fields rejected; valid customer registration `C07` succeeds and updates customer selector; empty service request description rejected; valid service request succeeds with status `'Pending'` and handled by `'Karthik Suresh'`.
  - Screen 2: Cash deposit increments balance; excessive withdrawal (₹999,999,999) rejected with `"Insufficient balance"`; self-transfer rejected with `"Source and destination accounts must be distinct"`; transfer to non-existent account `AC9999` rejected with `"Destination account AC9999 not found"`; valid transfer updates source and destination balances atomically; opening duplicate account rejected; opening zero-balance account succeeds; closing non-zero balance account rejected; closing zero-balance account succeeds.
  - Screen 3: Zero-facility customer `C04` and `C05` display info messages without crash; loan `L01` and `L02` display repayment schedules with status badges; investment portfolios render asset allocation bar charts cleanly.
  - Screen 4: Leaderboard slider functions at boundary limits (1 and 10); high-value AML filter handles zero matches cleanly with informational banner; multi-hop fund tracer handles `AC1001` (3 paths) and `AC9999` (0 paths) cleanly.

---

## 2. Logic Chain

1. **Requirement R3 & Parent Dispatch**:
   - R3 requires: *"Frontend layout with sidebar mode selector ('Live Neo4j' vs 'Offline Mock'...) Sidebar toggle allows switching between live DB and mock DB."*
   - Parent dispatch instructed: *"Verify both 'Live Neo4j' and 'Offline Mock' modes can be selected without crash."*
2. **Finding**:
   - While selecting `"Live Neo4j"` does not crash the process, the toggle is unidirectional. Once `"Live Neo4j"` is selected, selecting `"Offline Mock"` does NOT switch back to `"Offline Mock"`.
   - The user is permanently trapped in `"Live Neo4j"`.
   - When Neo4j is offline on `localhost:7687`, `format_func=get_customer_label` in `app.py:243` sequentially queries all 6 customers, each taking 4.07 seconds to time out (total ~25s), plus page-level queries (another 12-16s). The entire UI hangs for ~40 seconds per interaction.
   - Because the user cannot toggle back to `"Offline Mock"`, the app becomes unusable without closing the browser tab and clearing session state.
3. **Remediation**:
   - Streamlit provides native two-way widget-to-session state binding via `key="backend_mode"`.
   - Modifying `app.py` lines 195–201 to use `key="backend_mode"` instead of `index=...` resolves the issue completely and allows seamless bidirectional switching.

---

## 3. Caveats

1. **Neo4j Offline Environment**: In this test environment, Neo4j is not running on `bolt://localhost:7687`. Testing of "Live Neo4j" mode was performed against the offline fallback and connection timeout paths.
2. **Review-Only Constraint**: As Challenger 1 operating under the review-only constraint, implementation code in `app.py` was NOT modified. The recommended fix is provided for Worker M3.

---

## 4. Conclusion

**Verdict**: **REQUEST_CHANGES**

`app.py` is exceptionally well-structured, compliant with all 20 function contracts, and passed all 24 screen/customer permutations with 0 exceptions. However, the sidebar mode selector contains a **Mode Toggle Trap bug** that prevents switching from `"Live Neo4j"` back to `"Offline Mock"`.

### Required Action for Worker M3:
In `c:\dbms_da-3-project\app.py`, lines 195–201, replace:
```python
selected_mode = st.sidebar.radio(
    "Active Data Backend",
    options=["Live Neo4j", "Offline Mock"],
    index=0 if st.session_state["backend_mode"] == "Live Neo4j" else 1,
    help="Switch between live Neo4j database or the deterministic in-memory offline mock dataset.",
)
st.session_state["backend_mode"] = selected_mode
```
With:
```python
selected_mode = st.sidebar.radio(
    "Active Data Backend",
    options=["Live Neo4j", "Offline Mock"],
    key="backend_mode",
    help="Switch between live Neo4j database or the deterministic in-memory offline mock dataset.",
)
```

---

## 5. Verification Method

To independently reproduce the bug and verify the fix:

### 5.1 Mode Switch Reproduction (Fails on current app.py):
```powershell
python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('app.py', default_timeout=90).run()
print('Initial mode:', at.session_state['backend_mode'])
at.sidebar.radio[0].set_value('Live Neo4j').run()
print('After selecting Live:', at.session_state['backend_mode'])
at.sidebar.radio[0].set_value('Offline Mock').run()
print('After selecting Mock:', at.session_state['backend_mode'])
assert at.session_state['backend_mode'] == 'Offline Mock', 'TRAPPED IN LIVE MODE!'
"
```
*Current output: AssertionError (active mode remains `'Live Neo4j'`).*

### 5.2 Full Empirical Suite Verification:
```powershell
python -X utf8 test_challenger_m3.py
```
*Expected after fix: All 7 phases pass with exit code 0 and bidirectional switching verified.*
