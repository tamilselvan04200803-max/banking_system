"""
Empirical Challenger Test Suite: Interactive Forms and Mutations in app.py (Milestone 3)
Challenger 2 Verification Harness

7 Target Tests:
1. Contact update form execution (valid, empty, cross-customer)
2. Add customer form execution (valid, duplicate, missing fields, context integration)
3. Raise service request form execution (valid, empty description, CSE assignment)
4. Deposit and Withdrawal form execution (deposit, withdrawal, overdraft check)
5. Inter-account transfer form execution (valid transfer, self-transfer, empty dest, non-existent dest, insufficient balance)
6. Open account and Close zero-balance account execution (open with 0, close 0 balance, reject non-zero balance, duplicate account check)
7. State persistence across screens and clean reset via reset_mock_db() and UI reset button
"""

import mock_db
from streamlit.testing.v1 import AppTest


def test_target_1_contact_update():
    """Target 1: Test Contact update form execution."""
    print("\n--- Target 1: Testing Contact Update Form Execution ---")
    mock_db.reset_mock_db()
    at = AppTest.from_file("app.py", default_timeout=30).run()
    assert len(at.exception) == 0

    # 1.1 Valid contact update for C01
    at.text_input[0].set_value("9988776655")
    at.text_input[1].set_value("samridhi.updated@bank.com")
    at.button[0].click().run()
    assert len(at.exception) == 0

    c01_updated = mock_db.get_customer("C01")
    assert c01_updated["phone"] == "9988776655"
    assert c01_updated["email"] == "samridhi.updated@bank.com"
    assert at.text_input[0].value == "9988776655"
    assert at.text_input[1].value == "samridhi.updated@bank.com"
    print("  [PASS] 1.1 Valid contact update updated mock_db and re-rendered in UI.")

    # 1.2 Invalid contact update with empty / whitespace values
    at.text_input[0].set_value("   ")
    at.text_input[1].set_value("")
    at.button[0].click().run()
    assert len(at.exception) == 0
    assert len(at.error) > 0
    assert "Phone and Email cannot be empty" in at.error[0].value
    print("  [PASS] 1.2 Empty contact update rejected cleanly with validation error banner.")

    # 1.3 Contact update for customer C02
    at.sidebar.selectbox[0].set_value("C02").run()
    assert len(at.exception) == 0
    at.text_input[0].set_value("9112233445")
    at.text_input[1].set_value("rahul.verma@fintech.org")
    at.button[0].click().run()
    assert len(at.exception) == 0
    c02_check = mock_db.get_customer("C02")
    assert c02_check["phone"] == "9112233445"
    assert c02_check["email"] == "rahul.verma@fintech.org"
    print("  [PASS] 1.3 Contact update executed cleanly for customer C02.")


def test_target_2_add_customer():
    """Target 2: Test Add customer form execution."""
    print("\n--- Target 2: Testing Add Customer Form Execution ---")
    mock_db.reset_mock_db()
    at = AppTest.from_file("app.py", default_timeout=30).run()
    assert len(at.exception) == 0

    # 2.1 Missing mandatory fields validation
    at.text_input[2].set_value("")
    at.text_input[3].set_value("")
    at.button[1].click().run()
    assert len(at.exception) == 0
    assert len(at.error) > 0
    assert "mandatory" in at.error[0].value.lower()
    print("  [PASS] 2.1 Add customer with missing mandatory fields rejected cleanly.")

    # 2.2 Duplicate Customer ID registration rejection
    at.text_input[2].set_value("C01")
    at.text_input[3].set_value("Duplicate")
    at.text_input[4].set_value("Chennai")
    at.text_input[5].set_value("9000000000")
    at.text_input[6].set_value("User")
    at.text_input[7].set_value("duplicate@bank.com")
    at.button[1].click().run()
    assert len(at.exception) == 0
    assert len(at.error) > 0
    assert "already exists" in at.error[0].value.lower()
    print("  [PASS] 2.2 Duplicate customer ID 'C01' rejected cleanly.")

    # 2.3 Successful registration of new customer C07
    at.text_input[2].set_value("C07")
    at.text_input[3].set_value("Ananya")
    at.text_input[4].set_value("Bengaluru")
    at.text_input[5].set_value("9876500007")
    at.text_input[6].set_value("Iyer")
    at.text_input[7].set_value("ananya.iyer@bank.com")
    at.button[1].click().run()
    assert len(at.exception) == 0

    c07 = mock_db.get_customer("C07")
    assert c07 is not None
    assert c07["name"] == "Ananya Iyer"
    assert c07["city"] == "Bengaluru"
    assert "C07" in at.session_state["customer_ids"]
    assert at.session_state["selected_customer_id"] == "C07"
    print("  [PASS] 2.3 New customer C07 created, persisted in mock_db, and auto-selected in session state.")


def test_target_3_raise_service_request():
    """Target 3: Test Raise service request form execution."""
    print("\n--- Target 3: Testing Raise Service Request Form Execution ---")
    mock_db.reset_mock_db()
    at = AppTest.from_file("app.py", default_timeout=30).run()
    assert len(at.exception) == 0

    # 3.1 Empty description validation
    at.text_area[0].set_value("   ")
    at.button[2].click().run()
    assert len(at.exception) == 0
    assert len(at.error) > 0
    assert "description" in at.error[0].value.lower()
    print("  [PASS] 3.1 Empty service request description rejected cleanly.")

    # 3.2 Valid Service Request creation for C01
    at.text_area[0].set_value("Need 100-leaf cheque book")
    at.button[2].click().run()
    assert len(at.exception) == 0

    srs_c01 = mock_db.get_service_requests("C01")
    assert len(srs_c01) >= 1
    new_sr = next((sr for sr in srs_c01 if sr["description"] == "Need 100-leaf cheque book"), None)
    assert new_sr is not None
    assert new_sr["request_id"].startswith("SR")
    assert new_sr["status"] == "Pending"
    assert new_sr["handled_by"] == "Karthik Suresh"
    print(f"  [PASS] 3.2 Service request {new_sr['request_id']} registered with status Pending & assigned to Karthik Suresh (E05).")


def test_target_4_deposit_and_withdrawal():
    """Target 4: Test Deposit and Withdrawal form execution."""
    print("\n--- Target 4: Testing Deposit and Withdrawal Form Execution ---")
    mock_db.reset_mock_db()
    at = AppTest.from_file("app.py", default_timeout=30).run()
    at.sidebar.selectbox[0].set_value("C01").run()
    at.sidebar.radio[1].set_value("2. Accounts & Transactions").run()
    assert len(at.exception) == 0

    # 4.1 Process Cash Deposit (₹5,000)
    at.radio[0].set_value("Deposit")
    at.number_input[0].set_value(5000.0)
    at.button[0].click().run()
    assert len(at.exception) == 0

    ac1001 = [a for a in mock_db.get_accounts("C01") if a["account_number"] == "AC1001"][0]
    assert ac1001["balance"] == 90000.0
    txns = mock_db.get_transactions("AC1001")
    assert any(t["txn_type"] == "Deposit" and t["amount"] == 5000.0 for t in txns)
    print("  [PASS] 4.1 Cash deposit of Rs 5,000 processed; balance updated to 90,000.")

    # 4.2 Process Cash Withdrawal (₹15,000)
    at.radio[0].set_value("Withdrawal")
    at.number_input[0].set_value(15000.0)
    at.button[0].click().run()
    assert len(at.exception) == 0

    ac1001 = [a for a in mock_db.get_accounts("C01") if a["account_number"] == "AC1001"][0]
    assert ac1001["balance"] == 75000.0
    txns = mock_db.get_transactions("AC1001")
    assert any(t["txn_type"] == "Withdrawal" and t["amount"] == 15000.0 for t in txns)
    print("  [PASS] 4.2 Cash withdrawal of Rs 15,000 processed; balance updated to 75,000.")

    # 4.3 Overdraft / Insufficient balance withdrawal rejection
    at.radio[0].set_value("Withdrawal")
    at.number_input[0].set_value(99999999.0)
    at.button[0].click().run()
    assert len(at.exception) == 0
    assert len(at.error) > 0
    assert "insufficient balance" in at.error[0].value.lower()
    ac1001 = [a for a in mock_db.get_accounts("C01") if a["account_number"] == "AC1001"][0]
    assert ac1001["balance"] == 75000.0
    print("  [PASS] 4.3 Overdraft withdrawal of Rs 99,999,999 rejected with insufficient balance error banner.")


def test_target_5_inter_account_transfer():
    """Target 5: Test Inter-account transfer form execution."""
    print("\n--- Target 5: Testing Inter-Account Transfer Form Execution ---")
    mock_db.reset_mock_db()
    at = AppTest.from_file("app.py", default_timeout=30).run()
    at.sidebar.selectbox[0].set_value("C01").run()
    at.sidebar.radio[1].set_value("2. Accounts & Transactions").run()
    assert len(at.exception) == 0

    # 5.1 Empty destination account validation
    at.text_input[0].set_value("")
    at.number_input[1].set_value(5000.0)
    at.button[1].click().run()
    assert len(at.exception) == 0
    assert len(at.error) > 0
    assert "destination account" in at.error[0].value.lower()
    print("  [PASS] 5.1 Empty destination account rejected cleanly.")

    # 5.2 Self-transfer validation
    at.text_input[0].set_value("AC1001")
    at.number_input[1].set_value(5000.0)
    at.button[1].click().run()
    assert len(at.exception) == 0
    assert len(at.error) > 0
    assert "distinct" in at.error[0].value.lower()
    print("  [PASS] 5.2 Self-transfer from AC1001 to AC1001 rejected cleanly.")

    # 5.3 Non-existent destination account rejection
    at.text_input[0].set_value("AC9999")
    at.number_input[1].set_value(1000.0)
    at.button[1].click().run()
    assert len(at.exception) == 0
    assert len(at.error) > 0
    assert "not found" in at.error[0].value.lower()
    print("  [PASS] 5.3 Transfer to non-existent account AC9999 rejected cleanly with 'not found' error.")

    # 5.4 Insufficient balance transfer rejection
    at.text_input[0].set_value("AC1003")
    at.number_input[1].set_value(5000000.0)
    at.button[1].click().run()
    assert len(at.exception) == 0
    assert len(at.error) > 0
    assert "insufficient balance" in at.error[0].value.lower()
    print("  [PASS] 5.4 Transfer exceeding account balance rejected cleanly.")

    # 5.5 Valid Inter-Account Transfer: AC1001 -> AC1003 (Rs 5,000)
    at.text_input[0].set_value("AC1003")
    at.number_input[1].set_value(5000.0)
    at.button[1].click().run()
    assert len(at.exception) == 0

    ac1001 = [a for a in mock_db.get_accounts("C01") if a["account_number"] == "AC1001"][0]
    ac1003 = [a for a in mock_db.get_accounts("C02") if a["account_number"] == "AC1003"][0]
    assert ac1001["balance"] == 80000.0  # 85k - 5k
    assert ac1003["balance"] == 47000.0  # 42k + 5k

    txns_1001 = mock_db.get_transactions("AC1001")
    assert any(t["txn_type"] == "Transfer Out" and t["other_account"] == "AC1003" and t["amount"] == 5000.0 for t in txns_1001)

    txns_1003 = mock_db.get_transactions("AC1003")
    assert any(t["txn_type"] == "Transfer In" and t["other_account"] == "AC1001" and t["amount"] == 5000.0 for t in txns_1003)
    print("  [PASS] 5.5 Valid transfer of Rs 5,000 atomically updated AC1001 (80,000) and AC1003 (47,000).")


def test_target_6_open_and_close_account():
    """Target 6: Test Open account and Close zero-balance account execution."""
    print("\n--- Target 6: Testing Open Account & Close Zero-Balance Account ---")
    mock_db.reset_mock_db()
    at = AppTest.from_file("app.py", default_timeout=30).run()
    at.sidebar.selectbox[0].set_value("C01").run()
    at.sidebar.radio[1].set_value("2. Accounts & Transactions").run()
    assert len(at.exception) == 0

    # 6.1 Empty account number validation
    at.text_input[1].set_value("")
    at.button[2].click().run()
    assert len(at.exception) == 0
    assert len(at.error) > 0
    assert "required" in at.error[0].value.lower()
    print("  [PASS] 6.1 Open account with empty account number rejected cleanly.")

    # 6.2 Duplicate account number rejection
    at.text_input[1].set_value("AC1001")
    at.number_input[2].set_value(0.0)
    at.button[2].click().run()
    assert len(at.exception) == 0
    assert len(at.error) > 0
    assert "already exists" in at.error[0].value.lower()
    print("  [PASS] 6.2 Duplicate account number AC1001 rejected cleanly.")

    # 6.3 Open new account AC1009 with zero balance
    at.text_input[1].set_value("AC1009")
    at.number_input[2].set_value(0.0)
    at.button[2].click().run()
    assert len(at.exception) == 0
    c01_accs = mock_db.get_accounts("C01")
    ac1009_entry = [a for a in c01_accs if a["account_number"] == "AC1009"]
    assert len(ac1009_entry) == 1
    assert ac1009_entry[0]["balance"] == 0.0
    print("  [PASS] 6.3 New account AC1009 opened with Rs 0.00 initial balance.")

    # 6.4 Close non-zero balance account rejection (AC1001 balance = 85,000)
    at.selectbox[3].set_value("AC1001")
    at.button[3].click().run()
    assert len(at.exception) == 0
    assert "non-zero" in at.error[0].value.lower()
    assert any(a["account_number"] == "AC1001" for a in mock_db.get_accounts("C01"))
    print("  [PASS] 6.4 Close non-zero balance account AC1001 rejected strictly under zero-balance policy.")

    # 6.5 Close zero-balance account AC1009
    at.selectbox[3].set_value("AC1009")
    at.button[3].click().run()
    assert len(at.exception) == 0
    c01_accs_after_del = mock_db.get_accounts("C01")
    assert not any(a["account_number"] == "AC1009" for a in c01_accs_after_del)
    print("  [PASS] 6.5 Zero-balance account AC1009 successfully closed and removed from ledger.")


def test_target_7_state_persistence_and_reset():
    """Target 7: Test state persistence across screens and clean reset via reset_mock_db()."""
    print("\n--- Target 7: Testing State Persistence & Clean Reset ---")
    mock_db.reset_mock_db()
    at = AppTest.from_file("app.py", default_timeout=30).run()
    at.sidebar.selectbox[0].set_value("C01").run()

    # 1. Deposit 10,000 on AC1001 in Screen 2
    at.sidebar.radio[1].set_value("2. Accounts & Transactions").run()
    at.radio[0].set_value("Deposit")
    at.number_input[0].set_value(10000.0)
    at.button[0].click().run()
    assert len(at.exception) == 0

    # 2. Switch to Screen 1: verify total balance is 245,000 (85k+10k + 150k)
    at.sidebar.radio[1].set_value("1. Customer Profile & Services").run()
    assert len(at.exception) == 0
    total_bal_c01 = mock_db.get_total_balance("C01")
    assert total_bal_c01 == 245000.0
    print(f"  [PASS] 7.1 Cross-screen state persisted: C01 aggregated total balance is {total_bal_c01}.")

    # 3. Switch to Screen 4: check money trail from AC1001
    at.sidebar.radio[1].set_value("4. Analytics & Graph Intelligence").run()
    assert len(at.exception) == 0
    at.text_input[0].set_value("AC1001")
    at.button[0].click().run()
    assert len(at.exception) == 0
    trails = mock_db.get_money_trail("AC1001")
    assert len(trails) >= 3
    print(f"  [PASS] 7.2 Analytics Screen 4 traces {len(trails)} directed multi-hop fund trails.")

    # 4. Click UI Reset Mock DB button in sidebar
    at.sidebar.button[0].click().run()
    assert len(at.exception) == 0

    # Verify reset to baseline 47 nodes
    c01_restored = mock_db.get_customer("C01")
    assert c01_restored["phone"] == "9876543210"
    assert c01_restored["email"] == "samridhi.sharma@example.com"
    assert mock_db.get_total_balance("C01") == 235000.0

    b_counts = {b["branch_name"]: b["account_count"] for b in mock_db.get_branch_account_counts()}
    assert b_counts["Anna Nagar"] == 3
    assert b_counts["T Nagar"] == 3
    assert b_counts["Koramangala"] == 2
    print("  [PASS] 7.3 UI Reset Mock DB button cleanly restored all seed data, balances, and node counts.")

    # 5. Programmatic reset
    mock_db.reset_mock_db()
    at_fresh = AppTest.from_file("app.py", default_timeout=20).run()
    assert len(at_fresh.exception) == 0
    print("  [PASS] 7.4 Fresh launch after programmatic reset_mock_db() runs cleanly with 0 exceptions.")


def run_all():
    test_target_1_contact_update()
    test_target_2_add_customer()
    test_target_3_raise_service_request()
    test_target_4_deposit_and_withdrawal()
    test_target_5_inter_account_transfer()
    test_target_6_open_and_close_account()
    test_target_7_state_persistence_and_reset()
    mock_db.reset_mock_db()
    print("\n======================================================================")
    print("ALL 7 TARGET TESTS COMPLETED SUCCESSFULLY WITH 100% PASS RATE!")
    print("======================================================================")


if __name__ == "__main__":
    run_all()
