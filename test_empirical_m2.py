"""
Empirical verification harness for Milestone 2 Database Contracts: mock_db.py
Tests all 13 targeted Read and Analytics requirements + edge cases.
"""

import sys
import mock_db

def run_tests():
    print("=== STARTING EMPIRICAL VERIFICATION OF mock_db.py ===")
    mock_db.reset_mock_db()
    
    # ---------------------------------------------------------
    # 1. get_customer('C01')
    # ---------------------------------------------------------
    print("\n--- Test 1: get_customer ---")
    c01 = mock_db.get_customer("C01")
    print("get_customer('C01'):", c01)
    assert c01 is not None, "c01 should not be None"
    assert c01["customer_id"] == "C01", f"Expected C01, got {c01.get('customer_id')}"
    assert c01["name"] == "Samridhi Sharma", f"Expected Samridhi Sharma, got {c01.get('name')}"
    assert c01["customer_type"] == "Premium", f"Expected Premium, got {c01.get('customer_type')}"
    assert c01["relationship_manager"] == "Priya Menon", f"Expected Priya Menon, got {c01.get('relationship_manager')}"
    
    # Non-existent customer
    c_none = mock_db.get_customer("NON_EXISTENT")
    print("get_customer('NON_EXISTENT'):", c_none)
    assert c_none is None, f"Expected None for non-existent customer, got {c_none}"
    print("[PASS] Test 1: get_customer passed")

    # ---------------------------------------------------------
    # 2. get_accounts('C01')
    # ---------------------------------------------------------
    print("\n--- Test 2: get_accounts ---")
    accs = mock_db.get_accounts("C01")
    print("get_accounts('C01'):", accs)
    assert len(accs) == 2, f"Expected 2 accounts, got {len(accs)}"
    acc_map = {a["account_number"]: a for a in accs}
    assert "AC1001" in acc_map, "AC1001 missing"
    assert "AC1002" in acc_map, "AC1002 missing"
    assert acc_map["AC1001"]["balance"] == 85000.0, f"Expected 85000, got {acc_map['AC1001']['balance']}"
    assert acc_map["AC1002"]["balance"] == 150000.0, f"Expected 150000, got {acc_map['AC1002']['balance']}"
    
    # Non-existent customer accounts
    acc_none = mock_db.get_accounts("NON_EXISTENT")
    assert acc_none == [], f"Expected empty list for non-existent customer accounts, got {acc_none}"
    print("[PASS] Test 2: get_accounts passed")

    # ---------------------------------------------------------
    # 3. get_total_balance('C01')
    # ---------------------------------------------------------
    print("\n--- Test 3: get_total_balance ---")
    tot = mock_db.get_total_balance("C01")
    print("get_total_balance('C01'):", tot)
    assert tot == 235000.0, f"Expected 235000, got {tot}"
    
    # Non-existent customer total balance
    tot_none = mock_db.get_total_balance("NON_EXISTENT")
    assert tot_none == 0.0, f"Expected 0.0, got {tot_none}"
    print("[PASS] Test 3: get_total_balance passed")

    # ---------------------------------------------------------
    # 4. get_transactions('AC1001')
    # ---------------------------------------------------------
    print("\n--- Test 4: get_transactions ---")
    txns = mock_db.get_transactions("AC1001")
    print(f"get_transactions('AC1001') count={len(txns)}:")
    for t in txns:
        print("  ", t)
    assert len(txns) == 4, f"Expected 4 transactions, got {len(txns)}"
    
    # Check descending order by txn_date
    dates = [t["txn_date"] for t in txns]
    assert dates == sorted(dates, reverse=True), f"Dates not in descending order: {dates}"
    
    # Check the 4 expected entries
    types = [t["txn_type"] for t in txns]
    assert "Deposit" in types
    assert "Withdrawal" in types
    assert "Transfer Out" in types
    assert "Transfer In" in types
    
    # Specific detail checks
    dep = next(t for t in txns if t["txn_type"] == "Deposit")
    assert dep["amount"] == 20000.0
    assert dep["other_account"] is None

    wth = next(t for t in txns if t["txn_type"] == "Withdrawal")
    assert wth["amount"] == 5000.0
    assert wth["other_account"] is None

    tout = next(t for t in txns if t["txn_type"] == "Transfer Out")
    assert tout["amount"] == 8000.0
    assert tout["other_account"] == "AC1003"

    tin = next(t for t in txns if t["txn_type"] == "Transfer In")
    assert tin["amount"] == 2000.0
    assert tin["other_account"] == "AC1006"

    # Non-existent account transactions
    tx_none = mock_db.get_transactions("NON_EXISTENT")
    assert tx_none == [], f"Expected empty list, got {tx_none}"
    print("[PASS] Test 4: get_transactions passed")

    # ---------------------------------------------------------
    # 5. get_loans('C01')
    # ---------------------------------------------------------
    print("\n--- Test 5: get_loans ---")
    loans = mock_db.get_loans("C01")
    print("get_loans('C01'):", loans)
    assert len(loans) == 1, f"Expected 1 loan, got {len(loans)}"
    l01 = loans[0]
    assert l01["loan_id"] == "L01"
    assert l01["loan_type"] == "Home Loan"
    assert l01["loan_officer"] == "Divya Rao"
    assert l01["branch_name"] == "Anna Nagar"
    
    # Non-existent customer loans
    loans_none = mock_db.get_loans("NON_EXISTENT")
    assert loans_none == []
    print("[PASS] Test 5: get_loans passed")

    # ---------------------------------------------------------
    # 6. get_repayment_schedule('L01')
    # ---------------------------------------------------------
    print("\n--- Test 6: get_repayment_schedule ---")
    sched = mock_db.get_repayment_schedule("L01")
    print(f"get_repayment_schedule('L01') count={len(sched)}:")
    for s in sched:
        print("  ", s)
    assert len(sched) == 3, f"Expected 3 installments, got {len(sched)}"
    assert [s["installment_no"] for s in sched] == [1, 2, 3]
    assert sched[0]["status"] == "Paid"
    assert sched[1]["status"] == "Paid"
    assert sched[2]["status"] == "Pending"
    
    # Non-existent loan schedule
    sched_none = mock_db.get_repayment_schedule("NON_EXISTENT")
    assert sched_none == []
    print("[PASS] Test 6: get_repayment_schedule passed")

    # ---------------------------------------------------------
    # 7. get_investments('C01')
    # ---------------------------------------------------------
    print("\n--- Test 7: get_investments ---")
    invs = mock_db.get_investments("C01")
    print("get_investments('C01'):", invs)
    assert len(invs) == 2, f"Expected 2 investments, got {len(invs)}"
    inv_map = {i["investment_id"]: i for i in invs}
    assert "I01" in inv_map and inv_map["I01"]["amount"] == 100000.0
    assert "I03" in inv_map and inv_map["I03"]["amount"] == 300000.0
    
    # Non-existent customer investments
    inv_none = mock_db.get_investments("NON_EXISTENT")
    assert inv_none == []
    print("[PASS] Test 7: get_investments passed")

    # ---------------------------------------------------------
    # 8. get_service_requests('C01')
    # ---------------------------------------------------------
    print("\n--- Test 8: get_service_requests ---")
    srs = mock_db.get_service_requests("C01")
    print("get_service_requests('C01'):", srs)
    assert len(srs) == 1, f"Expected 1 service request, got {len(srs)}"
    sr03 = srs[0]
    assert sr03["request_id"] == "SR03"
    assert sr03["request_type"] == "Cheque Book"
    assert sr03["status"] == "Resolved"
    assert sr03["handled_by"] == "Karthik Suresh"
    
    # Non-existent customer service requests
    sr_none = mock_db.get_service_requests("NON_EXISTENT")
    assert sr_none == []
    print("[PASS] Test 8: get_service_requests passed")

    # ---------------------------------------------------------
    # 9. get_branches()
    # ---------------------------------------------------------
    print("\n--- Test 9: get_branches ---")
    branches = mock_db.get_branches()
    print("get_branches():", branches)
    assert len(branches) == 3, f"Expected 3 branches, got {len(branches)}"
    branch_names = {b["branch_name"] for b in branches}
    assert branch_names == {"Anna Nagar", "T Nagar", "Koramangala"}
    print("[PASS] Test 9: get_branches passed")

    # ---------------------------------------------------------
    # 10. get_branch_account_counts()
    # ---------------------------------------------------------
    print("\n--- Test 10: get_branch_account_counts ---")
    bcounts = mock_db.get_branch_account_counts()
    print("get_branch_account_counts():", bcounts)
    bcount_map = {b["branch_name"]: b["account_count"] for b in bcounts}
    assert bcount_map["Anna Nagar"] == 3, f"Expected 3 for Anna Nagar, got {bcount_map.get('Anna Nagar')}"
    assert bcount_map["T Nagar"] == 3, f"Expected 3 for T Nagar, got {bcount_map.get('T Nagar')}"
    assert bcount_map["Koramangala"] == 2, f"Expected 2 for Koramangala, got {bcount_map.get('Koramangala')}"
    print("[PASS] Test 10: get_branch_account_counts passed")

    # ---------------------------------------------------------
    # 11. get_top_customers_by_balance(3)
    # ---------------------------------------------------------
    print("\n--- Test 11: get_top_customers_by_balance ---")
    top3 = mock_db.get_top_customers_by_balance(3)
    print("get_top_customers_by_balance(3):", top3)
    assert len(top3) == 3, f"Expected 3 top customers, got {len(top3)}"
    assert top3[0]["customer_id"] == "C01" and top3[0]["total_balance"] == 235000.0
    assert top3[1]["customer_id"] == "C03" and top3[1]["total_balance"] == 200000.0
    assert top3[2]["customer_id"] == "C06" and top3[2]["total_balance"] == 95000.0
    print("[PASS] Test 11: get_top_customers_by_balance passed")

    # ---------------------------------------------------------
    # 12. get_large_transfers(20000)
    # ---------------------------------------------------------
    print("\n--- Test 12: get_large_transfers ---")
    l_transfers = mock_db.get_large_transfers(20000)
    print("get_large_transfers(20000):", l_transfers)
    assert len(l_transfers) == 2, f"Expected 2 large transfers, got {len(l_transfers)}"
    assert l_transfers[0]["txn_id"] == "TR6" and l_transfers[0]["amount"] == 40000.0
    assert l_transfers[1]["txn_id"] == "TR4" and l_transfers[1]["amount"] == 25000.0
    print("[PASS] Test 12: get_large_transfers passed")

    # ---------------------------------------------------------
    # 13. get_money_trail('AC1001')
    # ---------------------------------------------------------
    print("\n--- Test 13: get_money_trail ---")
    trail = mock_db.get_money_trail("AC1001")
    print(f"get_money_trail('AC1001') count={len(trail)}:")
    for tr in trail:
        print("  ", tr)
    assert len(trail) == 3, f"Expected 3 rows in money trail, got {len(trail)}"
    assert trail[0] == {"trail": ["AC1001", "AC1003"], "hops": 1}
    assert trail[1] == {"trail": ["AC1001", "AC1003", "AC1005"], "hops": 2}
    assert trail[2] == {"trail": ["AC1001", "AC1003", "AC1005", "AC1006"], "hops": 3}
    
    # Non-existent account trail
    trail_none = mock_db.get_money_trail("NON_EXISTENT")
    assert trail_none == []
    print("[PASS] Test 13: get_money_trail passed")

    # ---------------------------------------------------------
    # Adversarial / Stress Tests
    # ---------------------------------------------------------
    print("\n--- Adversarial & Stress Testing ---")
    # A. Cycle handling in get_money_trail
    # In SEED_TRANSFERS: TR3: AC1005->AC1006, TR5: AC1006->AC1001
    # If starting at AC1005: AC1005->AC1006 (hop 1) -> AC1001 (hop 2) -> AC1003 (hop 3)
    trail_c = mock_db.get_money_trail("AC1005")
    print("Money trail from AC1005 (cycle-testing):", trail_c)
    assert len(trail_c) == 3
    assert trail_c[0]["hops"] == 1 and trail_c[0]["trail"] == ["AC1005", "AC1006"]
    assert trail_c[1]["hops"] == 2 and trail_c[1]["trail"] == ["AC1005", "AC1006", "AC1001"]
    assert trail_c[2]["hops"] == 3 and trail_c[2]["trail"] == ["AC1005", "AC1006", "AC1001", "AC1003"]

    # B. Transfer query with limit > total customers
    top_all = mock_db.get_top_customers_by_balance(100)
    assert len(top_all) == 6, f"Expected 6 customers, got {len(top_all)}"

    # C. get_large_transfers with boundary = 0
    all_tr = mock_db.get_large_transfers(0)
    assert len(all_tr) == 8, f"Expected 8 transfers, got {len(all_tr)}"

    # D. get_large_transfers with very high threshold
    high_tr = mock_db.get_large_transfers(1000000)
    assert high_tr == []

    print("\nALL 13 TARGET READ & ANALYTICS CHECKS AND STRESS TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
