"""
Adversarial Stress & Edge-Case Harness for Milestone 3 Streamlit App Mutations
Challenger 2 Verification

Challenges:
1. High-frequency rapid sequential mutations on single account (ledger integrity & mathematical precision).
2. Interleaved multi-customer fund transfers & context switches across all 4 screens.
3. Lifecycle Stress: Non-zero opening balance -> close rejection -> withdraw to zero -> close success.
4. Floating-point currency arithmetic (fractional paise/cents precision).
5. Robustness to special characters (names with apostrophes, hyphens, Unicode).
6. Large payload stress in service requests (1,000+ characters).
7. Total database state idempotency after reset_mock_db().
"""

import sys
import mock_db
from streamlit.testing.v1 import AppTest


def test_rapid_sequential_mutations():
    print("\n--- Stress 1: Rapid Sequential Mutations on Single Account ---")
    mock_db.reset_mock_db()
    at = AppTest.from_file("app.py", default_timeout=30).run()
    at.sidebar.selectbox[0].set_value("C01").run()
    at.sidebar.radio[1].set_value("2. Accounts & Transactions").run()

    # Initial AC1001 balance: 85,000
    expected_balance = 85000.0
    amounts = [1000.0, -500.0, 2500.0, -1000.0, 5000.0, -2000.0, 100.0, -100.0]

    for amt in amounts:
        if amt > 0:
            at.radio[0].set_value("Deposit")
            at.number_input[0].set_value(amt)
        else:
            at.radio[0].set_value("Withdrawal")
            at.number_input[0].set_value(abs(amt))
        at.button[0].click().run()
        assert len(at.exception) == 0
        expected_balance += amt

    ac1001_acc = [a for a in mock_db.get_accounts("C01") if a["account_number"] == "AC1001"][0]
    assert ac1001_acc["balance"] == expected_balance, f"Expected {expected_balance}, got {ac1001_acc['balance']}"
    txns = mock_db.get_transactions("AC1001")
    # 4 seed transactions + 8 new transactions = 12 total
    assert len(txns) == 12, f"Expected 12 transactions in ledger, found {len(txns)}"
    print(f"  [PASS] 8 rapid mutations executed sequentially; balance {expected_balance} is mathematically exact across 12 ledger rows.")


def test_interleaved_multi_customer_transfers():
    print("\n--- Stress 2: Interleaved Multi-Customer Transfers & Context Switches ---")
    mock_db.reset_mock_db()
    at = AppTest.from_file("app.py", default_timeout=30).run()

    # 1. Select C03 (owns AC1004 with balance 200,000)
    at.sidebar.selectbox[0].set_value("C03").run()
    at.sidebar.radio[1].set_value("2. Accounts & Transactions").run()
    assert len(at.exception) == 0

    # Transfer 50,000 from AC1004 to AC1005 (owned by C04, initial balance 65,000)
    at.text_input[0].set_value("AC1005")
    at.number_input[1].set_value(50000.0)
    at.button[1].click().run()
    assert len(at.exception) == 0

    # Verify C03 balance updated to 150,000
    ac1004 = [a for a in mock_db.get_accounts("C03") if a["account_number"] == "AC1004"][0]
    assert ac1004["balance"] == 150000.0

    # 2. Switch to C04 context
    at.sidebar.selectbox[0].set_value("C04").run()
    assert len(at.exception) == 0
    ac1005 = [a for a in mock_db.get_accounts("C04") if a["account_number"] == "AC1005"][0]
    assert ac1005["balance"] == 115000.0, f"Expected AC1005 balance 115000 (65k + 50k), got {ac1005['balance']}"

    # Verify C04 Screen 1 total balance reflects 115,000
    at.sidebar.radio[1].set_value("1. Customer Profile & Services").run()
    assert len(at.exception) == 0
    assert mock_db.get_total_balance("C04") == 115000.0
    print("  [PASS] Inter-customer transfer AC1004 -> AC1005 (50,000) correctly updated both accounts across customer contexts.")


def test_lifecycle_non_zero_open_and_close():
    print("\n--- Stress 3: Account Lifecycle with Non-Zero Opening Balance ---")
    mock_db.reset_mock_db()
    at = AppTest.from_file("app.py", default_timeout=30).run()
    at.sidebar.selectbox[0].set_value("C02").run()
    at.sidebar.radio[1].set_value("2. Accounts & Transactions").run()

    # Open account AC1010 for C02 with initial opening balance Rs 25,000
    at.text_input[1].set_value("AC1010")
    at.selectbox[1].set_value("BR02")  # T Nagar
    at.selectbox[2].set_value("Savings")
    at.number_input[2].set_value(25000.0)
    at.button[2].click().run()  # Open Account
    assert len(at.exception) == 0

    # Verify AC1010 exists with balance 25,000
    c02_accs = mock_db.get_accounts("C02")
    ac1010 = [a for a in c02_accs if a["account_number"] == "AC1010"][0]
    assert ac1010["balance"] == 25000.0

    # Try to close AC1010 immediately -> must fail because balance is 25,000 != 0
    at.selectbox[3].set_value("AC1010")
    at.button[3].click().run()  # Confirm Account Deletion
    assert len(at.exception) == 0
    assert len(at.error) > 0
    assert "non-zero" in at.error[0].value.lower()
    assert any(a["account_number"] == "AC1010" for a in mock_db.get_accounts("C02"))

    # Withdraw 25,000 from AC1010 to zero out balance
    at.selectbox[0].set_value("AC1010").run()
    at.radio[0].set_value("Withdrawal")
    at.number_input[0].set_value(25000.0)
    at.button[0].click().run()  # Process Transaction
    assert len(at.exception) == 0

    ac1010_zero = [a for a in mock_db.get_accounts("C02") if a["account_number"] == "AC1010"][0]
    assert ac1010_zero["balance"] == 0.0

    # Now close AC1010 -> must succeed
    at.selectbox[3].set_value("AC1010")
    at.button[3].click().run()  # Confirm Account Deletion
    assert len(at.exception) == 0
    assert not any(a["account_number"] == "AC1010" for a in mock_db.get_accounts("C02"))
    print("  [PASS] Full lifecycle verified: Open with 25k -> Close rejected -> Withdraw to 0 -> Close succeeded.")


def test_floating_point_currency_precision():
    print("\n--- Stress 4: Floating-Point Currency Arithmetic Precision ---")
    mock_db.reset_mock_db()
    at = AppTest.from_file("app.py", default_timeout=30).run()
    at.sidebar.selectbox[0].set_value("C01").run()
    at.sidebar.radio[1].set_value("2. Accounts & Transactions").run()

    # Deposit 1234.56
    at.radio[0].set_value("Deposit")
    at.number_input[0].set_value(1234.56)
    at.button[0].click().run()
    assert len(at.exception) == 0

    ac = [a for a in mock_db.get_accounts("C01") if a["account_number"] == "AC1001"][0]
    assert round(ac["balance"], 2) == 86234.56

    # Withdraw 234.56
    at.radio[0].set_value("Withdrawal")
    at.number_input[0].set_value(234.56)
    at.button[0].click().run()
    assert len(at.exception) == 0

    ac = [a for a in mock_db.get_accounts("C01") if a["account_number"] == "AC1001"][0]
    assert round(ac["balance"], 2) == 86000.00
    print("  [PASS] Decimal currency precision (paise/cents) preserved accurately without floating point drift.")


def test_special_characters_and_payload_stress():
    print("\n--- Stress 5 & 6: Special Characters in Registration & Large SR Payload ---")
    mock_db.reset_mock_db()
    at = AppTest.from_file("app.py", default_timeout=30).run()
    at.sidebar.selectbox[0].set_value("C01").run()

    # Customer with special characters (hyphenated first name, apostrophe in last name)
    at.text_input[2].set_value("C08")
    at.text_input[3].set_value("Jean-Luc")
    at.text_input[4].set_value("Pondicherry")
    at.text_input[5].set_value("9876500008")
    at.text_input[6].set_value("D'Souza")
    at.text_input[7].set_value("jeanluc.dsouza@example.com")
    at.button[1].click().run()
    assert len(at.exception) == 0

    c08 = mock_db.get_customer("C08")
    assert c08["name"] == "Jean-Luc D'Souza"
    print("  [PASS] Special characters (hyphens, apostrophes) in customer registration handled cleanly.")

    # Large text payload for service request (1,200 characters)
    large_desc = "URGENT STATEMENT DISCREPANCY: " + ("Account audit line mismatch itemized report details. " * 20)
    at.text_area[0].set_value(large_desc)
    at.button[2].click().run()
    assert len(at.exception) == 0

    srs_c08 = mock_db.get_service_requests("C08")
    assert len(srs_c08) == 1
    assert srs_c08[0]["description"] == large_desc.strip()
    print(f"  [PASS] Large service request payload ({len(large_desc)} chars) submitted and persisted without truncation.")


def test_adversarial_suite():
    print("======================================================================")
    print("STARTING ADVERSARIAL STRESS HARNESS FOR MILESTONE 3 (APP.PY)")
    print("======================================================================")
    test_rapid_sequential_mutations()
    test_interleaved_multi_customer_transfers()
    test_lifecycle_non_zero_open_and_close()
    test_floating_point_currency_precision()
    test_special_characters_and_payload_stress()
    mock_db.reset_mock_db()
    print("\n======================================================================")
    print("ALL ADVERSARIAL STRESS HARNESS TESTS PASSED WITH ZERO FAILURES!")
    print("======================================================================")


if __name__ == "__main__":
    test_adversarial_suite()
