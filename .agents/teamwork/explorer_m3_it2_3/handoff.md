# Explorer Investigation Report: Backend Mode Switch Verification & AppTest Test Harness

**Explorer**: teamwork_preview_explorer (Explorer 3 for Milestone 3 Iteration 2)  
**Working Directory**: `c:\dbms_da-3-project\.agents\teamwork\explorer_m3_it2_3\`  
**Date**: 2026-10-21  
**Milestone**: Milestone 3 Iteration 2 — Streamlit Application & Challenger Harness  
**Target Files**:
- `c:\dbms_da-3-project\test_challenger_m3.py` (specifically `test_03_backend_mode_switch()`)
- `c:\dbms_da-3-project\app.py` (lines 172–218, sidebar backend mode selector)

---

## 1. Observation

### 1.1 Review of `test_challenger_m3.py` (`test_03_backend_mode_switch()`)
In `c:\dbms_da-3-project\test_challenger_m3.py`, lines 58–99:
```python
58: def test_03_backend_mode_switch():
59:     log("3. Testing backend mode switching ('Offline Mock' <-> 'Live Neo4j')...")
60:     mock_db.reset_mock_db()
61:     at = AppTest.from_file("app.py", default_timeout=90).run()
62:     assert len(at.exception) == 0
63: 
64:     # Toggle to Live Neo4j mode
65:     log("  Switching to 'Live Neo4j' mode...")
66:     at.sidebar.radio[0].set_value("Live Neo4j").run()
67:     assert len(at.exception) == 0, f"Exception when switching to Live Neo4j: {at.exception}"
68:     assert at.session_state["backend_mode"] == "Live Neo4j"
69: 
70:     # Verify both 'Live Neo4j' and 'Offline Mock' modes can be selected without crash
71:     log("  Verified: 'Live Neo4j' selected with 0 exceptions.")
72: 
73:     # Toggle back to Offline Mock mode
74:     log("  Switching back to 'Offline Mock' mode...")
75:     at.sidebar.radio[0].set_value("Offline Mock").run()
76:     assert len(at.exception) == 0, f"Exception when switching back to Offline Mock: {at.exception}"
77:     mode_switch_back_success = (at.session_state["backend_mode"] == "Offline Mock")
78:     if not mode_switch_back_success:
79:         log("  [BUG-FOUND-1] Mode toggle trap: Cannot switch from 'Live Neo4j' back to 'Offline Mock'!")
80:         log("                Active mode remained: " + at.session_state["backend_mode"])
81:     else:
82:         log("  Switched back to 'Offline Mock' successfully.")
83: 
84:     # Test "Reset Mock DB State" sidebar button
85:     log("  Testing 'Reset Mock DB State' button...")
86:     reset_btn = None
87:     for b in at.sidebar.button:
88:         if "Reset Mock DB State" in b.label:
89:             reset_btn = b
90:             break
91:     if reset_btn is not None:
92:         reset_btn.click().run()
93:         assert len(at.exception) == 0, f"Exception after clicking Reset Mock DB: {at.exception}"
94:         log("  PASS: Reset Mock DB State clicked with 0 exceptions.")
95:     else:
96:         log("  [CONSEQUENCE-OF-BUG-1] 'Reset Mock DB State' button is unreachable because app is trapped in Live Neo4j mode!")
97: 
98:     log("PASS: Backend mode toggle and Reset Mock DB tested successfully with 0 crashes.")
```

**Flaws Observed in Current Test Harness**:
1. **No Initial Mode Assertion**: The function does not verify the initial state probed or initialized into `session_state["backend_mode"]` and rendered by `at.sidebar.radio[0]`.
2. **Soft Failure / Missing Assertion on Switch Back**: Line 77 evaluates `mode_switch_back_success = (at.session_state["backend_mode"] == "Offline Mock")`, but lines 78–80 merely log a warning rather than raising an `AssertionError`.
3. **Soft Failure / Missing Assertion on Reset Button**: Line 91 conditionally checks `if reset_btn is not None:`, falling back to line 96 logging `[CONSEQUENCE-OF-BUG-1]`, followed immediately by line 98: `log("PASS: Backend mode toggle and Reset Mock DB tested successfully with 0 crashes.")`.
4. **False Positive Exit Code**: Because the test harness does not assert, running `python test_challenger_m3.py` exits with status `0` even while the Mode Toggle Trap bug is active in `app.py`.

### 1.2 Empirical Execution of `test_challenger_m3.py`
Running `python test_challenger_m3.py` produced the following verbatim log:
```
[CHALLENGER-TEST] 3. Testing backend mode switching ('Offline Mock' <-> 'Live Neo4j')...
[CHALLENGER-TEST]   Switching to 'Live Neo4j' mode...
[CHALLENGER-TEST]   Verified: 'Live Neo4j' selected with 0 exceptions.
[CHALLENGER-TEST]   Switching back to 'Offline Mock' mode...
[CHALLENGER-TEST]   [BUG-FOUND-1] Mode toggle trap: Cannot switch from 'Live Neo4j' back to 'Offline Mock'!
[CHALLENGER-TEST]                 Active mode remained: Live Neo4j
[CHALLENGER-TEST]   Testing 'Reset Mock DB State' button...
[CHALLENGER-TEST]   [CONSEQUENCE-OF-BUG-1] 'Reset Mock DB State' button is unreachable because app is trapped in Live Neo4j mode!
[CHALLENGER-TEST] PASS: Backend mode toggle and Reset Mock DB tested successfully with 0 crashes.
```

### 1.3 Analysis of `app.py` Lines 172–218
In `c:\dbms_da-3-project\app.py`:
```python
172: # 1. Probe & Initialize Backend Mode
173: if "backend_mode" not in st.session_state:
174:     is_live_avail = probe_live_neo4j()
175:     st.session_state["backend_mode"] = "Live Neo4j" if is_live_avail else "Offline Mock"
...
195: selected_mode = st.sidebar.radio(
196:     "Active Data Backend",
197:     options=["Live Neo4j", "Offline Mock"],
198:     index=0 if st.session_state["backend_mode"] == "Live Neo4j" else 1,
199:     help="Switch between live Neo4j database or the deterministic in-memory offline mock dataset.",
200: )
201: st.session_state["backend_mode"] = selected_mode
202: 
203: # Determine active backend module
204: if selected_mode == "Live Neo4j":
...
211: else:
212:     backend = mock_db
213:     st.sidebar.info("🟡 Running in Offline Mock Mode")
214:     if st.sidebar.button("🔄 Reset Mock DB State", use_container_width=True):
215:         mock_db.reset_mock_db()
216:         st.sidebar.success("Mock DB restored to baseline 47 nodes!")
217:         st.rerun()
```

### 1.4 Crucial Finding: `StreamlitWidgetAlreadyInstantiatedError`
During empirical testing of Streamlit's widget session state binding:
If an implementer updates `st.sidebar.radio` with `key="backend_mode"` but leaves line 201 (`st.session_state["backend_mode"] = selected_mode`) in place, Streamlit throws:
```
StreamlitWidgetAlreadyInstantiatedError: `st.session_state.backend_mode` cannot be modified after the widget with key `backend_mode` is instantiated.
```
Therefore, `st.session_state["backend_mode"] = selected_mode` must be **completely removed** when `key="backend_mode"` is introduced.

---

## 2. Logic Chain

1. **Test Harness Integrity**:
   - A verification test harness must be strict: when an expected feature or invariant fails, it must raise an `AssertionError` that halts test execution and exits with non-zero status code.
   - The current `test_03_backend_mode_switch()` converts hard failures into informational log messages (`[BUG-FOUND-1]`), which masks defects during automated CI and worker gating.
2. **AppTest State Model & Verification Sequence**:
   - `AppTest.from_file("app.py", default_timeout=90).run()` boots Streamlit and executes script lines 1 to end.
   - At startup, `st.session_state["backend_mode"]` is initialized to `"Live Neo4j"` if port 7687 responds, or `"Offline Mock"` if unreachable.
   - In Step 1: The test must assert `initial_mode in ("Live Neo4j", "Offline Mock")` and assert `at.sidebar.radio[0].value == initial_mode`.
   - In Step 2: The test sets `at.sidebar.radio[0].set_value("Live Neo4j").run()`. The test must assert that `at.session_state["backend_mode"] == "Live Neo4j"`, `at.sidebar.radio[0].value == "Live Neo4j"`, and that the "Reset Mock DB State" button is NOT rendered in Live mode.
   - In Step 3 & 4: The test sets `at.sidebar.radio[0].set_value("Offline Mock").run()`. The test must strictly assert that `at.session_state["backend_mode"] == "Offline Mock"` and `at.sidebar.radio[0].value == "Offline Mock"`.
   - In Step 5: The test filters `at.sidebar.button` for `"Reset Mock DB State"`. It must strictly assert that exactly 1 such button exists (`len(mock_reset_btns) == 1`).
   - To verify the reset button's actual functionality (not just superficial presence): The test mutates a record (e.g. `mock_db.process_transaction("AC1001", "Deposit", 10000.0)`), clicks the reset button via `reset_btn.click().run()`, and asserts that AC1001's balance is restored to the baseline 85,000.0.
3. **Application Remediation (`app.py`)**:
   - In `app.py`, `st.sidebar.radio` currently uses dynamic `index=...` without a widget key. This causes the radio widget to recalculate its selection from `st.session_state["backend_mode"]` before the new widget value is processed, creating the toggle trap.
   - Binding `key="backend_mode"` allows Streamlit's two-way state binding to handle synchronization automatically.
   - Deleting line 201 prevents `StreamlitWidgetAlreadyInstantiatedError`.

---

## 3. Caveats

1. **Read-Only Scope**: In compliance with the subagent read-only constraint, neither `app.py` nor `test_challenger_m3.py` was directly modified on disk. All formulations and test runs were verified against runtime duplicates.
2. **Network/Offline State**: In an environment without a running Neo4j instance on port 7687, `probe_live_neo4j()` evaluates to `False`, so the initial mode is `"Offline Mock"`. The test sequence is written defensively to support both environments where Neo4j is running and where it is offline.
3. **Timeout Safeguards**: In offline mode, switching to "Live Neo4j" triggers socket connection attempts in `get_customer_label` that time out after a few seconds. The timeout of 90 seconds in `AppTest.from_file("app.py", default_timeout=90)` is necessary and sufficient.

---

## 4. Conclusion & Recommendations

### 4.1 Recommended Implementation Code for Worker M3 (`app.py`)
In `c:\dbms_da-3-project\app.py`, lines 195–201:

**Target to Replace**:
```python
selected_mode = st.sidebar.radio(
    "Active Data Backend",
    options=["Live Neo4j", "Offline Mock"],
    index=0 if st.session_state["backend_mode"] == "Live Neo4j" else 1,
    help="Switch between live Neo4j database or the deterministic in-memory offline mock dataset.",
)
st.session_state["backend_mode"] = selected_mode
```

**Replacement**:
```python
selected_mode = st.sidebar.radio(
    "Active Data Backend",
    options=["Live Neo4j", "Offline Mock"],
    key="backend_mode",
    help="Switch between live Neo4j database or the deterministic in-memory offline mock dataset.",
)
```
*(Notice: Line 201 `st.session_state["backend_mode"] = selected_mode` is omitted entirely).*

---

### 4.2 Exact Recommended Code for `test_challenger_m3.py` (`test_03_backend_mode_switch`)
Replace `test_03_backend_mode_switch()` in `c:\dbms_da-3-project\test_challenger_m3.py` (lines 58–99) with the following complete, strict assertion sequence:

```python
def test_03_backend_mode_switch():
    log("3. Testing backend mode switching ('Offline Mock' <-> 'Live Neo4j')...")
    mock_db.reset_mock_db()
    at = AppTest.from_file("app.py", default_timeout=90).run()
    assert len(at.exception) == 0, f"Startup exceptions: {at.exception}"

    # 1. Verify Initial mode (probed or default)
    initial_mode = at.session_state.get("backend_mode")
    assert initial_mode in ("Live Neo4j", "Offline Mock"), (
        f"Invalid initial backend_mode in session_state: {initial_mode}"
    )
    assert at.sidebar.radio[0].value == initial_mode, (
        f"Initial sidebar radio value '{at.sidebar.radio[0].value}' does not match "
        f"session_state '{initial_mode}'"
    )
    if initial_mode == "Offline Mock":
        assert any("Reset Mock DB State" in b.label for b in at.sidebar.button), (
            "Reset Mock DB button should be rendered in initial Offline Mock mode"
        )
    log(f"  Step 1 PASSED: Initial mode verified as '{initial_mode}'.")

    # 2. Switch to 'Live Neo4j' mode
    log("  Step 2: Switching to 'Live Neo4j' mode...")
    at.sidebar.radio[0].set_value("Live Neo4j").run()
    assert len(at.exception) == 0, f"Exception when switching to Live Neo4j: {at.exception}"
    assert at.session_state["backend_mode"] == "Live Neo4j", (
        f"Failed to update session_state to 'Live Neo4j', got: '{at.session_state.get('backend_mode')}'"
    )
    assert at.sidebar.radio[0].value == "Live Neo4j", (
        f"Sidebar radio value expected 'Live Neo4j', got: '{at.sidebar.radio[0].value}'"
    )
    # Verify Reset Mock DB button is absent in Live mode
    live_reset_btns = [b for b in at.sidebar.button if "Reset Mock DB State" in b.label]
    assert len(live_reset_btns) == 0, (
        "Reset Mock DB button should NOT be rendered in 'Live Neo4j' mode"
    )
    log("  Step 2 PASSED: Switched to 'Live Neo4j' with 0 exceptions and verified reset button hidden.")

    # 3. Switch back to 'Offline Mock' mode
    log("  Step 3: Switching back to 'Offline Mock' mode...")
    at.sidebar.radio[0].set_value("Offline Mock").run()
    assert len(at.exception) == 0, f"Exception when switching back to Offline Mock: {at.exception}"

    # 4. Verify session_state and radio value returned to 'Offline Mock'
    assert at.session_state["backend_mode"] == "Offline Mock", (
        f"Mode toggle trap! Expected 'Offline Mock', got: '{at.session_state.get('backend_mode')}'"
    )
    assert at.sidebar.radio[0].value == "Offline Mock", (
        f"Mode toggle trap! Expected radio 'Offline Mock', got: '{at.sidebar.radio[0].value}'"
    )
    log("  Step 4 PASSED: Successfully returned to 'Offline Mock' mode.")

    # 5. Verify 'Reset Mock DB State' button is accessible and functional
    log("  Step 5: Verifying 'Reset Mock DB State' button accessibility...")
    mock_reset_btns = [b for b in at.sidebar.button if "Reset Mock DB State" in b.label]
    assert len(mock_reset_btns) == 1, (
        f"Expected exactly 1 'Reset Mock DB State' button in Offline Mock mode, found {len(mock_reset_btns)}"
    )
    reset_btn = mock_reset_btns[0]

    # Mutate state so we can verify reset effect
    mock_db.process_transaction("AC1001", "Deposit", 10000.0)
    mutated_bal = next(a["balance"] for a in mock_db.get_accounts("C01") if a["account_number"] == "AC1001")
    assert mutated_bal == 95000.0, f"Expected mutated balance 95000.0, got {mutated_bal}"

    # Click the Reset Mock DB State button
    reset_btn.click().run()
    assert len(at.exception) == 0, f"Exception after clicking Reset Mock DB: {at.exception}"
    assert at.session_state["backend_mode"] == "Offline Mock"

    # Verify that mock DB state was restored to baseline
    restored_bal = next(a["balance"] for a in mock_db.get_accounts("C01") if a["account_number"] == "AC1001")
    assert restored_bal == 85000.0, f"Expected restored balance 85000.0, got {restored_bal}"
    log("  Step 5 PASSED: 'Reset Mock DB State' button clicked and restored database baseline.")

    log("PASS: Backend mode toggle and Reset Mock DB verified with 100% strict assertions.")
```

---

## 5. Verification Method

To independently verify the test sequence and application behavior:

### 5.1 Verification Against Current Code (Proving Strict Failure of Buggy Code)
Run:
```powershell
powershell -Command @"
@'
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('app.py', default_timeout=90).run()
at.sidebar.radio[0].set_value('Live Neo4j').run()
at.sidebar.radio[0].set_value('Offline Mock').run()
assert at.session_state['backend_mode'] == 'Offline Mock', 'TRAPPED IN LIVE NEO4J!'
'@ | python -
"@
```
*Result on current `app.py`*: Raises `AssertionError: TRAPPED IN LIVE NEO4J!`.

### 5.2 Verification Against Remediated Code (Proving 100% Success)
Run:
```powershell
powershell -Command @"
@'
import os, mock_db
from streamlit.testing.v1 import AppTest

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

target = '''selected_mode = st.sidebar.radio(
    \"Active Data Backend\",
    options=[\"Live Neo4j\", \"Offline Mock\"],
    index=0 if st.session_state[\"backend_mode\"] == \"Live Neo4j\" else 1,
    help=\"Switch between live Neo4j database or the deterministic in-memory offline mock dataset.\",
)
st.session_state[\"backend_mode\"] = selected_mode'''

replacement = '''selected_mode = st.sidebar.radio(
    \"Active Data Backend\",
    options=[\"Live Neo4j\", \"Offline Mock\"],
    key=\"backend_mode\",
    help=\"Switch between live Neo4j database or the deterministic in-memory offline mock dataset.\",
)'''

temp_file = '_temp_verify.py'
with open(temp_file, 'w', encoding='utf-8') as f:
    f.write(code.replace(target, replacement))

try:
    at = AppTest.from_file(temp_file, default_timeout=90).run()
    # Step 1: initial mode
    assert at.session_state['backend_mode'] in ('Live Neo4j', 'Offline Mock')
    # Step 2: switch to Live Neo4j
    at.sidebar.radio[0].set_value('Live Neo4j').run()
    assert at.session_state['backend_mode'] == 'Live Neo4j'
    assert not any('Reset Mock DB State' in b.label for b in at.sidebar.button)
    # Step 3 & 4: switch back to Offline Mock
    at.sidebar.radio[0].set_value('Offline Mock').run()
    assert at.session_state['backend_mode'] == 'Offline Mock'
    # Step 5: reset button accessible and functional
    reset_btns = [b for b in at.sidebar.button if 'Reset Mock DB State' in b.label]
    assert len(reset_btns) == 1
    mock_db.process_transaction('AC1001', 'Deposit', 10000.0)
    reset_btns[0].click().run()
    assert at.session_state['backend_mode'] == 'Offline Mock'
    assert mock_db.get_accounts('C01')[0]['balance'] == 85000.0
    print('ALL 5 STEPS PASSED WITH 100% SUCCESS!')
finally:
    if os.path.exists(temp_file):
        os.remove(temp_file)
'@ | python -
"@
```
*Result on remediated code*: Prints `ALL 5 STEPS PASSED WITH 100% SUCCESS!` and exits with code 0.
