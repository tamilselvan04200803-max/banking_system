"""
Empirical Challenger Test Suite for Milestone 3 (Streamlit app.py)
Adversarial Verification, Edge Case Mining, and Navigation Permutations.
"""

import sys
import py_compile
import pandas as pd
from streamlit.testing.v1 import AppTest
import mock_db

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def log(msg: str):
    print(f"[CHALLENGER-TEST] {msg}", flush=True)


def test_01_compilation():
    log("1. Testing syntax & bytecode compilation...")
    py_compile.compile("app.py", doraise=True)
    log("PASS: app.py compiled successfully with 0 syntax errors.")


def test_02_navigation_matrix():
    log("2. Testing 24 permutations (4 screens x 6 customers C01-C06)...")
    mock_db.reset_mock_db()
    at = AppTest.from_file("app.py", default_timeout=25).run()
    assert len(at.exception) == 0, f"Startup exceptions: {at.exception}"

    customers = ["C01", "C02", "C03", "C04", "C05", "C06"]
    screens = [
        "1. Customer Profile & Services",
        "2. Accounts & Transactions",
        "3. Loans & Investments",
        "4. Analytics & Graph Intelligence",
    ]

    count = 0
    for cid in customers:
        # Select customer in sidebar selectbox
        at.sidebar.selectbox[0].set_value(cid).run()
        assert len(at.exception) == 0, f"Exception selecting customer {cid}: {at.exception}"
        assert at.session_state["selected_customer_id"] == cid

        for scr in screens:
            # Select screen in sidebar radio
            at.sidebar.radio[1].set_value(scr).run()
            assert len(at.exception) == 0, f"Exception on customer {cid}, screen '{scr}': {at.exception}"
            count += 1
            log(f"  Verified permutation {count}/24: Customer={cid} | Screen='{scr}' -> 0 exceptions")

    assert count == 24
    log(f"PASS: All 24 customer x screen permutations passed with 0 exceptions.")


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



def test_04_screen1_adversarial_and_mutations():
    log("4. Testing Screen 1 (Customer) adversarial inputs and mutations...")
    mock_db.reset_mock_db()
    at = AppTest.from_file("app.py", default_timeout=25).run()
    at.sidebar.selectbox[0].set_value("C01").run()
    at.sidebar.radio[1].set_value("1. Customer Profile & Services").run()
    assert len(at.exception) == 0

    # 4.1 Contact update with empty strings
    log("  4.1 Attempting contact update with empty inputs...")
    at.text_input[0].set_value("   ")
    at.text_input[1].set_value("   ")
    at.button[0].click().run()
    assert len(at.exception) == 0
    assert any("cannot be empty" in err.value for err in at.error), "Expected validation error for empty contact"

    # 4.2 Valid contact update
    log("  4.2 Valid contact update...")
    at.text_input[0].set_value("9840112233")
    at.text_input[1].set_value("samridhi.updated@bank.com")
    at.button[0].click().run()
    assert len(at.exception) == 0

    cust_check = mock_db.get_customer("C01")
    assert cust_check["phone"] == "9840112233"
    assert cust_check["email"] == "samridhi.updated@bank.com"
    log("  PASS: Contact updated verified in DB.")

    # 4.3 Add customer with duplicate ID
    log("  4.3 Attempting to register customer with duplicate ID 'C01'...")
    at.text_input[2].set_value("C01")
    at.text_input[3].set_value("Clone")
    at.text_input[4].set_value("Chennai")
    at.text_input[5].set_value("9000000000")
    at.text_input[6].set_value("User")
    at.text_input[7].set_value("clone@bank.com")
    at.button[1].click().run()
    assert len(at.exception) == 0
    assert any("already exists" in err.value for err in at.error), "Expected duplicate ID error"

    # 4.4 Add customer with empty mandatory fields
    log("  4.4 Attempting to register customer with missing fields...")
    at.text_input[2].set_value("C07")
    at.text_input[3].set_value("")
    at.text_input[4].set_value("Chennai")
    at.text_input[5].set_value("")
    at.text_input[6].set_value("")
    at.text_input[7].set_value("")
    at.button[1].click().run()
    assert len(at.exception) == 0
    assert any("mandatory" in err.value for err in at.error), "Expected mandatory fields error"

    # 4.5 Register brand new customer C07 successfully
    log("  4.5 Registering new customer C07...")
    at.text_input[2].set_value("C07")
    at.text_input[3].set_value("Ananya")
    at.text_input[4].set_value("Bengaluru")
    at.text_input[5].set_value("9888877777")
    at.text_input[6].set_value("Deshmukh")
    at.text_input[7].set_value("ananya.d@example.com")
    at.button[1].click().run()
    assert len(at.exception) == 0
    assert "C07" in at.session_state["customer_ids"]
    assert at.session_state["selected_customer_id"] == "C07"

    # 4.6 Raise service request with empty description
    log("  4.6 Raising service request with empty description...")
    at.text_area[0].set_value("   ")
    at.button[2].click().run()
    assert len(at.exception) == 0
    assert any("provide a description" in err.value for err in at.error), "Expected description validation error"

    # 4.7 Raise valid service request
    log("  4.7 Raising valid service request...")
    at.text_area[0].set_value("Urgent request for international debit card activation.")
    at.button[2].click().run()
    assert len(at.exception) == 0
    srs = mock_db.get_service_requests("C07")
    assert len(srs) == 1
    assert srs[0]["status"] == "Pending"
    assert srs[0]["handled_by"] in ("Karthik Suresh", "E05")

    log("PASS: Screen 1 adversarial inputs and mutations passed successfully.")


def test_05_screen2_adversarial_and_mutations():
    log("5. Testing Screen 2 (Accounts & Txns) adversarial inputs and mutations...")
    mock_db.reset_mock_db()
    at = AppTest.from_file("app.py", default_timeout=25).run()

    at.sidebar.selectbox[0].set_value("C01").run()
    at.sidebar.radio[1].set_value("2. Accounts & Transactions").run()
    assert len(at.exception) == 0

    # 5.3 Deposit ₹5000 on AC1001
    init_bal = mock_db.get_accounts("C01")[0]["balance"]
    log(f"  5.3 Depositing ₹5000 into AC1001 (initial balance: {init_bal})...")
    at.number_input[0].set_value(5000.0)
    at.button[0].click().run()
    assert len(at.exception) == 0
    new_bal = next(a["balance"] for a in mock_db.get_accounts("C01") if a["account_number"] == "AC1001")
    assert new_bal == init_bal + 5000.0

    # 5.4 Withdrawal exceeding balance (Adversarial)
    log("  5.4 Testing withdrawal exceeding balance (₹999,999,999)...")
    at.radio[0].set_value("Withdrawal").run()
    at.number_input[0].set_value(999999999.0)
    at.button[0].click().run()
    assert len(at.exception) == 0
    assert any("Insufficient" in err.value for err in at.error), "Expected insufficient funds error"

    # 5.5 Fund Transfer: Self-transfer adversarial check (AC1001 -> AC1001)
    log("  5.5 Testing self-transfer (AC1001 -> AC1001)...")
    at.text_input[0].set_value("AC1001")
    at.number_input[1].set_value(1000.0)
    at.button[1].click().run()
    assert len(at.exception) == 0
    assert any("distinct" in err.value for err in at.error), "Expected distinct accounts error"

    # 5.6 Fund Transfer: Non-existent destination account (AC1001 -> AC9999)
    log("  5.6 Testing transfer to non-existent account (AC1001 -> AC9999)...")
    at.text_input[0].set_value("AC9999")
    at.number_input[1].set_value(1000.0)
    at.button[1].click().run()
    assert len(at.exception) == 0
    assert any("not found" in err.value or "does not exist" in err.value for err in at.error), "Expected account not found error"

    # 5.7 Fund Transfer: Exceeding balance
    log("  5.7 Testing transfer exceeding balance...")
    at.text_input[0].set_value("AC1003")
    at.number_input[1].set_value(999999999.0)
    at.button[1].click().run()
    assert len(at.exception) == 0
    assert any("Insufficient" in err.value for err in at.error), "Expected insufficient funds error"

    # 5.8 Valid Fund Transfer: AC1001 -> AC1003 ₹3,000
    log("  5.8 Executing valid transfer: AC1001 -> AC1003 ₹3,000...")
    src_before = next(a["balance"] for a in mock_db.get_accounts("C01") if a["account_number"] == "AC1001")
    dst_before = mock_db.get_accounts("C02")[0]["balance"]
    at.text_input[0].set_value("AC1003")
    at.number_input[1].set_value(3000.0)
    at.button[1].click().run()
    assert len(at.exception) == 0
    src_after = next(a["balance"] for a in mock_db.get_accounts("C01") if a["account_number"] == "AC1001")
    dst_after = mock_db.get_accounts("C02")[0]["balance"]
    assert src_after == src_before - 3000.0
    assert dst_after == dst_before + 3000.0
    log(f"  PASS: Transfer verified (src {src_before}->{src_after}, dst {dst_before}->{dst_after}).")

    # 5.9 Open Account: Duplicate account number
    log("  5.9 Attempting to open duplicate account AC1001...")
    at.text_input[1].set_value("AC1001")
    at.number_input[2].set_value(500.0)
    at.button[2].click().run()
    assert len(at.exception) == 0
    assert any("already exists" in err.value for err in at.error), "Expected duplicate account error"

    # 5.10 Open Account: Valid new account AC1010 with 0 balance
    log("  5.10 Opening new account AC1010 with ₹0.00 balance...")
    at.text_input[1].set_value("AC1010")
    at.number_input[2].set_value(0.0)
    at.button[2].click().run()
    assert len(at.exception) == 0
    assert any(a["account_number"] == "AC1010" for a in mock_db.get_accounts("C01"))

    # 5.11 Close Account: Attempting to close non-zero account AC1001
    log("  5.11 Attempting to close non-zero balance account AC1001...")
    at.selectbox[3].set_value("AC1001")
    at.button[3].click().run()
    assert len(at.exception) == 0
    assert any("Cannot close account" in err.value or "balance is not zero" in err.value for err in at.error)
    assert any(a["account_number"] == "AC1001" for a in mock_db.get_accounts("C01"))

    # 5.12 Close Account: Closing zero-balance account AC1010
    log("  5.12 Closing zero-balance account AC1010...")
    at.selectbox[3].set_value("AC1010")
    at.button[3].click().run()
    assert len(at.exception) == 0
    assert not any(a["account_number"] == "AC1010" for a in mock_db.get_accounts("C01"))
    log("  PASS: Zero-balance account AC1010 closed successfully.")

    log("PASS: Screen 2 adversarial inputs and mutations passed successfully.")


def test_06_screen3_adversarial():
    log("6. Testing Screen 3 (Loans & Investments) adversarial scenarios...")
    mock_db.reset_mock_db()
    at = AppTest.from_file("app.py", default_timeout=25).run()

    # 6.1 Customer C04 has zero loans and zero investments in baseline dataset
    at.sidebar.selectbox[0].set_value("C04").run()
    at.sidebar.radio[1].set_value("3. Loans & Investments").run()
    assert len(at.exception) == 0
    assert any("does not hold any active loan facilities" in i.value for i in at.info)
    assert any("no registered investment portfolio items" in i.value for i in at.info)

    # 6.2 Customer C01: Loan L01 with 3 installments, and 2 investments
    at.sidebar.selectbox[0].set_value("C01").run()
    assert len(at.exception) == 0
    assert len(at.dataframe) >= 2  # Repayment schedule df and Investments df

    # 6.3 Customer C02: Has loan L02 and investment I02
    at.sidebar.selectbox[0].set_value("C02").run()
    assert len(at.exception) == 0
    assert len(at.dataframe) >= 2  # Repayment schedule df and Investments df

    # 6.4 Customer C05: No loans and no investments
    at.sidebar.selectbox[0].set_value("C05").run()
    assert len(at.exception) == 0
    assert any("does not hold any active loan facilities" in i.value for i in at.info)
    assert any("no registered investment portfolio items" in i.value for i in at.info)

    log("PASS: Screen 3 zero-state and populated-state assertions passed.")


def test_07_screen4_adversarial():
    log("7. Testing Screen 4 (Analytics & Intelligence) adversarial inputs...")
    mock_db.reset_mock_db()
    at = AppTest.from_file("app.py", default_timeout=25).run()
    at.sidebar.radio[1].set_value("4. Analytics & Graph Intelligence").run()
    assert len(at.exception) == 0

    # 7.1 Leaderboard slider boundary testing
    log("  7.1 Testing leaderboard slider at limits (1 and 10)...")
    at.slider[0].set_value(1).run()
    assert len(at.exception) == 0
    at.slider[0].set_value(10).run()
    assert len(at.exception) == 0

    # 7.2 High-value transfer threshold filter testing
    log("  7.2 Testing threshold with no matches (₹999,999,999)...")
    at.number_input[0].set_value(999999999.0).run()
    assert len(at.exception) == 0
    assert any("No transfers found exceeding" in i.value for i in at.info)

    log("  7.3 Testing threshold with normal value (₹20,000)...")
    at.number_input[0].set_value(20000.0).run()
    assert len(at.exception) == 0

    # 7.4 Money Trail Tracer: AC1001 (should find 3 trails)
    log("  7.4 Testing money trail for AC1001...")
    at.text_input[0].set_value("AC1001")
    at.button[0].click().run()
    assert len(at.exception) == 0
    assert any("Discovered **3** directed fund trail" in s.value for s in at.success)

    # 7.5 Money Trail Tracer: Non-existent account AC9999
    log("  7.5 Testing money trail for unknown AC9999...")
    at.text_input[0].set_value("AC9999")
    at.button[0].click().run()
    assert len(at.exception) == 0
    assert any("No outgoing multi-hop transfer trails found" in i.value for i in at.info)

    log("PASS: Screen 4 analytics and graph intelligence passed all tests.")


def main():
    log("STARTING EMPIRICAL CHALLENGER TEST SUITE")
    test_01_compilation()
    test_02_navigation_matrix()
    test_03_backend_mode_switch()
    test_04_screen1_adversarial_and_mutations()
    test_05_screen2_adversarial_and_mutations()
    test_06_screen3_adversarial()
    test_07_screen4_adversarial()
    mock_db.reset_mock_db()
    log("==================================================================")
    log("ALL 7 CHALLENGER TEST PHASES PASSED WITH 100% EMPIRICAL SUCCESS!")
    log("==================================================================")


if __name__ == "__main__":
    main()
