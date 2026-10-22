import sys
import mock_db
from streamlit.testing.v1 import AppTest

def run_adversarial_suite():
    print("=== STARTING ADVERSARIAL STRESS TEST SUITE ===")
    mock_db.reset_mock_db()

    # ---------------------------------------------------------
    # TEST 1: Testing all seed customers across all screens
    # ---------------------------------------------------------
    print("\n--- Test 1: Testing all seed customers across all screens for empty states ---")
    at = AppTest.from_file("app.py", default_timeout=20).run()
    assert len(at.exception) == 0, f"Exception on boot: {at.exception}"

    customers = ["C01", "C02", "C03", "C04", "C05", "C06"]
    screens = [
        "1. Customer Profile & Services",
        "2. Accounts & Transactions",
        "3. Loans & Investments",
        "4. Analytics & Graph Intelligence",
    ]

    for cid in customers:
        at.sidebar.selectbox[0].set_value(cid).run()
        assert len(at.exception) == 0, f"Exception selecting customer {cid}: {at.exception}"
        for scr in screens:
            at.sidebar.radio[1].set_value(scr).run()
            assert len(at.exception) == 0, f"Exception on {cid} screen {scr}: {at.exception}"
    print("Test 1 Passed: All 6 customers rendered on all 4 screens with 0 exceptions.")

    # ---------------------------------------------------------
    # TEST 2: Register C07 via UI and Test Zero-Account Screen 2
    # ---------------------------------------------------------
    print("\n--- Test 2: Register C07 via UI and Test Zero-Account Screen 2 ---")
    at.sidebar.radio[1].set_value("1. Customer Profile & Services").run()
    at.main.text_input[2].set_value("C07")
    at.main.text_input[3].set_value("Aarav")
    at.main.text_input[4].set_value("Chennai")
    at.main.text_input[5].set_value("9876543299")
    at.main.text_input[6].set_value("Sharma")
    at.main.text_input[7].set_value("aarav.sharma@example.com")
    at.main.button[1].click().run()
    assert len(at.exception) == 0
    assert at.session_state["selected_customer_id"] == "C07"
    assert mock_db.get_customer("C07") is not None

    # Now navigate to Screen 2 with C07 (who has 0 accounts)
    at.sidebar.radio[1].set_value("2. Accounts & Transactions").run()
    assert len(at.exception) == 0, f"Exception rendering 0 accounts: {at.exception}"
    warnings = [w.value for w in at.warning]
    assert any("does not own any accounts currently" in str(w) for w in warnings), f"Warning not found in {warnings}"
    print("Test 2 Passed: Zero-account customer displays clean warning without crashing.")

    # ---------------------------------------------------------
    # TEST 3: Customer with 0 loans and 0 investments on Screen 3
    # ---------------------------------------------------------
    print("\n--- Test 3: Customer with 0 loans & 0 investments on Screen 3 ---")
    at.sidebar.radio[1].set_value("3. Loans & Investments").run()
    assert len(at.exception) == 0, f"Exception on Screen 3: {at.exception}"
    infos = [i.value for i in at.info]
    assert any("does not hold any active loan facilities" in str(i) for i in infos), f"Loan info missing: {infos}"
    assert any("has no registered investment portfolio items" in str(i) for i in infos), f"Inv info missing: {infos}"
    print("Test 3 Passed: Zero loans and zero investments empty states rendered cleanly.")

    # ---------------------------------------------------------
    # TEST 4: Customer with 0 service requests on Screen 1
    # ---------------------------------------------------------
    print("\n--- Test 4: Customer with 0 service requests on Screen 1 ---")
    at.sidebar.radio[1].set_value("1. Customer Profile & Services").run()
    assert len(at.exception) == 0, f"Exception on Screen 1: {at.exception}"
    infos = [i.value for i in at.info]
    assert any("No service requests on record" in str(i) for i in infos), f"SR info missing: {infos}"
    print("Test 4 Passed: Zero service requests empty state rendered cleanly.")

    # ---------------------------------------------------------
    # TEST 5: Screen 4 Empty State Filters (High threshold AML & Unknown Trail)
    # ---------------------------------------------------------
    print("\n--- Test 5: High threshold AML & Unknown Trail empty states ---")
    at.sidebar.radio[1].set_value("4. Analytics & Graph Intelligence").run()
    assert len(at.exception) == 0
    # Set threshold very high
    at.main.number_input[0].set_value(9999999.0).run()
    assert len(at.exception) == 0
    infos = [i.value for i in at.info]
    assert any("No transfers found exceeding" in str(i) for i in infos), f"Expected no transfers info in {infos}"

    # Trace unknown account
    at.main.text_input[0].set_value("AC_NONEXISTENT").run()
    at.main.button[0].click().run()
    assert len(at.exception) == 0
    infos = [i.value for i in at.info]
    assert any("No outgoing multi-hop transfer trails found" in str(i) for i in infos), f"Expected trail info in {infos}"
    print("Test 5 Passed: Screen 4 high threshold & non-existent trail empty states verified.")

    # ---------------------------------------------------------
    # TEST 6: Mutation error resilience & error banner inspection
    # ---------------------------------------------------------
    print("\n--- Test 6: Mutation error resilience & error banner inspection ---")
    # Switch to C01 on Screen 1
    at.sidebar.selectbox[0].set_value("C01").run()
    at.sidebar.radio[1].set_value("1. Customer Profile & Services").run()

    # 6.1 Contact update with empty values
    at.main.text_input[0].set_value("").run()
    at.main.button[0].click().run()
    assert len(at.exception) == 0
    assert any("cannot be empty" in str(e.value) for e in at.error), "Expected error banner for empty contact"

    # 6.2 Duplicate customer creation
    at.main.text_input[2].set_value("C01") # Duplicate ID
    at.main.text_input[3].set_value("Samridhi")
    at.main.text_input[4].set_value("Chennai")
    at.main.text_input[5].set_value("9840111111")
    at.main.text_input[6].set_value("Sharma")
    at.main.text_input[7].set_value("duplicate@test.com")
    at.main.button[1].click().run()
    assert len(at.exception) == 0
    assert any("already exists" in str(e.value).lower() for e in at.error), f"Expected duplicate customer error in {at.error}"

    # 6.3 Empty service request description
    at.main.text_area[0].set_value("").run()
    at.main.button[2].click().run()
    assert len(at.exception) == 0
    assert any("Please provide a description" in str(e.value) for e in at.error), "Expected empty SR error"

    # 6.4 Screen 2: Accounts & Transactions Mutations
    at.sidebar.radio[1].set_value("2. Accounts & Transactions").run()
    
    # Locate transaction type radio in main body
    txn_radio = [r for r in at.main.radio if r.label == "Transaction Type"][0]
    txn_radio.set_value("Withdrawal").run()
    # Withdrawal exceeding balance (AC1001 balance is 85000)
    at.main.number_input[0].set_value(9999999.0).run()
    at.main.button[0].click().run()
    assert len(at.exception) == 0
    assert any("insufficient balance" in str(e.value).lower() for e in at.error), f"Expected insufficient balance error in {at.error}"

    # Transfer with same account
    at.main.text_input[0].set_value("AC1001").run()
    at.main.number_input[1].set_value(100.0).run()
    at.main.button[1].click().run()
    assert len(at.exception) == 0
    assert any("must be distinct" in str(e.value).lower() for e in at.error), f"Expected distinct accounts error in {at.error}"

    # Transfer to non-existent account
    at.main.text_input[0].set_value("AC9999_GHOST").run()
    at.main.number_input[1].set_value(100.0).run()
    at.main.button[1].click().run()
    assert len(at.exception) == 0
    assert any("not found" in str(e.value).lower() or "failed" in str(e.value).lower() for e in at.error), f"Expected destination not found error in {at.error}"

    # Transfer exceeding balance
    at.main.text_input[0].set_value("AC1002").run()
    at.main.number_input[1].set_value(9999999.0).run()
    at.main.button[1].click().run()
    assert len(at.exception) == 0
    assert any("insufficient balance" in str(e.value).lower() for e in at.error), f"Expected transfer balance error in {at.error}"

    # Open account without account number
    at.main.text_input[1].set_value("").run()
    at.main.button[2].click().run()
    assert len(at.exception) == 0
    assert any("Account Number is required" in str(e.value) for e in at.error), "Expected account number required error"

    # Close account with non-zero balance
    # C01 owns AC1001 (balance 85000)
    at.main.button[3].click().run()
    assert len(at.exception) == 0
    assert any("cannot close" in str(e.value).lower() or "balance" in str(e.value).lower() for e in at.error), f"Expected cannot close non-zero account error in {at.error}"

    print("Test 6 Passed: All mutation error paths triggered st.error without crashing.")

    # ---------------------------------------------------------
    # TEST 7: Mock State Reset via Sidebar Button
    # ---------------------------------------------------------
    print("\n--- Test 7: Mock State Reset via Sidebar Button ---")
    assert mock_db.get_customer("C07") is not None
    at.sidebar.button[0].click().run()
    assert len(at.exception) == 0
    assert mock_db.get_customer("C07") is None
    print("Test 7 Passed: Mock reset button restored backend store with 0 exceptions.")

    # Final cleanup
    mock_db.reset_mock_db()
    print("\n=== ALL ADVERSARIAL TESTS COMPLETED WITH 100% SUCCESS ===")

if __name__ == "__main__":
    run_adversarial_suite()
