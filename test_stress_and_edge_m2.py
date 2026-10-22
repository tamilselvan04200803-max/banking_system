"""
Deep Adversarial and Edge-Case Stress Harness for mock_db.py
Tests state mutations, reset idempotency, graph branching, type safety, and edge boundaries.
"""

import mock_db

def run_stress_tests():
    print("=== STARTING DEEP ADVERSARIAL STRESS HARNESS ===")
    mock_db.reset_mock_db()

    # --- 1. Dynamic Mutation Reflection in Read Functions ---
    print("\n--- Stress 1: Dynamic Mutation Reflection ---")
    # Initial balance for AC1003 is 42000.0 (held by C02)
    # Total balance for C02 initially:
    c02_init_bal = mock_db.get_total_balance("C02")
    assert c02_init_bal == 42000.0

    # Deposit 10000 into AC1003
    dep_res = mock_db.process_transaction("AC1003", "Deposit", 10000.0)
    assert dep_res["success"] is True
    assert dep_res["new_balance"] == 52000.0

    # Check that get_accounts, get_total_balance, and get_top_customers_by_balance reflect this immediately
    assert mock_db.get_total_balance("C02") == 52000.0
    c02_accs = mock_db.get_accounts("C02")
    assert c02_accs[0]["balance"] == 52000.0

    # Check that get_transactions shows this new deposit at the top (today's date)
    c02_txns = mock_db.get_transactions("AC1003")
    assert c02_txns[0]["txn_type"] == "Deposit"
    assert c02_txns[0]["amount"] == 10000.0

    # Transfer 20000 from AC1001 (balance 85000 -> 65000) to AC1003 (52000 -> 72000)
    tr_res = mock_db.transfer_money("AC1001", "AC1003", 20000.0)
    assert tr_res["success"] is True
    assert mock_db.get_total_balance("C01") == 215000.0
    assert mock_db.get_total_balance("C02") == 72000.0

    # get_large_transfers(15000) should now include this new transfer
    l_tr = mock_db.get_large_transfers(15000)
    assert any(t["from_account"] == "AC1001" and t["to_account"] == "AC1003" and t["amount"] == 20000.0 for t in l_tr)

    print("[PASS] Stress 1: Dynamic Mutation Reflection passed")

    # --- 2. Branching Fund Flow in Money Trail ---
    print("\n--- Stress 2: Multi-branch Fund Flow ---")
    # Currently AC1001 has transferred to AC1003. Now let's transfer from AC1001 to AC1007 as well
    mock_db.transfer_money("AC1001", "AC1007", 5000.0)
    trail_1001 = mock_db.get_money_trail("AC1001")
    # AC1001 now branches to AC1003 and AC1007
    direct_hops = [t for t in trail_1001 if t["hops"] == 1]
    assert len(direct_hops) >= 2, f"Expected at least 2 direct hops, got {len(direct_hops)}"
    print("Multi-branch trail rows count:", len(trail_1001))
    print("[PASS] Stress 2: Multi-branch Fund Flow passed")

    # --- 3. Account Lifecycle & Branch Account Distribution ---
    print("\n--- Stress 3: Account Lifecycle & Branch Counts ---")
    # Open an account in Koramangala (BR03) with 0 balance
    open_res = mock_db.open_account("AC9999", "C06", "BR03", "Savings", 0)
    assert open_res["success"] is True
    # Branch counts: Koramangala had 2, now should have 3
    counts = {b["branch_name"]: b["account_count"] for b in mock_db.get_branch_account_counts()}
    assert counts["Koramangala"] == 3

    # Close the account
    close_res = mock_db.close_account("AC9999")
    assert close_res["success"] is True
    # Branch counts should revert to 2
    counts_after = {b["branch_name"]: b["account_count"] for b in mock_db.get_branch_account_counts()}
    assert counts_after["Koramangala"] == 2

    print("[PASS] Stress 3: Account Lifecycle & Branch Counts passed")

    # --- 4. Contact Update & Service Request Reflection ---
    print("\n--- Stress 4: Contact Update & Service Requests ---")
    upd_res = mock_db.update_customer_contact("C01", "9999999999", "samridhi.new@example.com")
    assert upd_res["success"] is True
    c01_updated = mock_db.get_customer("C01")
    assert c01_updated["phone"] == "9999999999"
    assert c01_updated["email"] == "samridhi.new@example.com"

    sr_res = mock_db.raise_service_request("C01", "Address Update", "Moving to new street")
    assert sr_res["success"] is True
    assert sr_res["request_id"].startswith("SR")
    c01_srs = mock_db.get_service_requests("C01")
    assert len(c01_srs) == 2  # SR03 + new SR
    assert c01_srs[0]["request_id"] == sr_res["request_id"]  # sorted desc by date/id
    assert c01_srs[0]["handled_by"] == "Karthik Suresh"

    print("[PASS] Stress 4: Contact Update & Service Requests passed")

    # --- 5. Reset Mock DB Idempotency ---
    print("\n--- Stress 5: Reset Mock DB Idempotency ---")
    mock_db.reset_mock_db()
    # Confirm exact clean baseline restored
    c01_clean = mock_db.get_customer("C01")
    assert c01_clean["phone"] == "9876543210"
    assert c01_clean["email"] == "samridhi.sharma@example.com"
    assert mock_db.get_total_balance("C01") == 235000.0
    assert len(mock_db.get_service_requests("C01")) == 1
    assert len(mock_db.get_transactions("AC1001")) == 4
    counts_clean = {b["branch_name"]: b["account_count"] for b in mock_db.get_branch_account_counts()}
    assert counts_clean["Koramangala"] == 2

    print("[PASS] Stress 5: Reset Mock DB Idempotency passed")

    # --- 6. Edge Inputs & Boundaries ---
    print("\n--- Stress 6: Edge Inputs & Boundaries ---")
    # Top customers limit = 0
    assert mock_db.get_top_customers_by_balance(0) == []
    # Note on negative limit: in Python [:limit] with limit < 0 slices from the end.
    # Let's verify what mock_db currently returns for -1
    neg_result = mock_db.get_top_customers_by_balance(-1)
    print(f"get_top_customers_by_balance(-1) returned {len(neg_result)} rows (Python slice behavior)")

    # Empty string queries
    assert mock_db.get_customer("") is None
    assert mock_db.get_accounts("") == []
    assert mock_db.get_total_balance("") == 0.0
    assert mock_db.get_transactions("") == []
    assert mock_db.get_loans("") == []
    assert mock_db.get_repayment_schedule("") == []
    assert mock_db.get_investments("") == []
    assert mock_db.get_service_requests("") == []
    assert mock_db.get_money_trail("") == []

    print("[PASS] Stress 6: Edge Inputs & Boundaries passed")
    print("\nALL ADVERSARIAL STRESS HARNESS TESTS PASSED CLEANLY!")

if __name__ == "__main__":
    run_stress_tests()
