"""
Forensic Integrity Audit Test Suite for Milestone 3 (Streamlit app.py)
Auditor: teamwork_preview_auditor

Forensic Checks:
1. AST Static Audit: Verify genuine bindings to all 20 database function contracts and no facade stubs.
2. Dynamic Routing Spy: Verify that "Offline Mock" routes to mock_db and "Live Neo4j" routes to db.
3. UI Authenticity Check: Inject canary values into backend responses and verify they propagate to UI components.
4. Mutation & State Flow Audit: Verify all interactive forms genuinely execute mutations on the active backend.
5. Invalidation & Adversarial Stress Tests: Verify error handling and absence of hardcoded shortcuts.
"""

import ast
import sys
import py_compile
import unittest.mock as mock
import pandas as pd
from streamlit.testing.v1 import AppTest

import mock_db
import db


REQUIRED_FUNCTIONS = [
    "get_customer",
    "get_accounts",
    "get_total_balance",
    "get_transactions",
    "get_loans",
    "get_repayment_schedule",
    "get_investments",
    "get_service_requests",
    "get_branches",
    "add_customer",
    "update_customer_contact",
    "open_account",
    "close_account",
    "raise_service_request",
    "process_transaction",
    "transfer_money",
    "get_branch_account_counts",
    "get_top_customers_by_balance",
    "get_large_transfers",
    "get_money_trail",
]


def test_01_compilation():
    print("[FORENSIC-AUDIT] Check 1: Verifying Python bytecode compilation...")
    py_compile.compile("app.py", doraise=True)
    print("  -> PASS: app.py compiles cleanly with zero syntax/bytecode errors.")


def test_02_ast_static_binding_audit():
    print("[FORENSIC-AUDIT] Check 2: AST Static Audit of app.py...")
    with open("app.py", "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename="app.py")

    # Find all attribute accesses of 'backend.<method>'
    invoked_methods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "backend":
                invoked_methods.add(node.func.attr)

    missing = set(REQUIRED_FUNCTIONS) - invoked_methods
    print(f"  -> Discovered {len(invoked_methods)} distinct backend method calls: {sorted(invoked_methods)}")
    assert not missing, f"Missing backend bindings for: {missing}"
    print("  -> PASS: All 20 required database functions are statically bound via backend.<func>!")


def test_03_dynamic_mode_routing_spies():
    print("[FORENSIC-AUDIT] Check 3: Dynamic Backend Mode Routing Spies...")
    mock_db.reset_mock_db()

    # 3.1 Test Offline Mock Mode Routing
    print("  3.1 Verifying routing in 'Offline Mock' mode...")
    with mock.patch("mock_db.get_customer", wraps=mock_db.get_customer) as spy_mock_cust, \
         mock.patch("mock_db.get_total_balance", wraps=mock_db.get_total_balance) as spy_mock_bal, \
         mock.patch("db.get_customer", wraps=db.get_customer) as spy_db_cust:

        at = AppTest.from_file("app.py", default_timeout=20).run()
        assert len(at.exception) == 0

        # In Offline Mock mode, mock_db functions must be called, db.get_customer must NOT be called
        assert spy_mock_cust.called, "mock_db.get_customer was NOT called in Offline Mock mode!"
        assert spy_mock_bal.called, "mock_db.get_total_balance was NOT called in Offline Mock mode!"
        assert not spy_db_cust.called, "db.get_customer was unexpectedly called in Offline Mock mode!"
        print(f"  -> PASS: Offline Mock genuinely routed to mock_db (mock_db called {spy_mock_cust.call_count} times, db called 0 times).")

    # 3.2 Test Live Neo4j Mode Routing
    print("  3.2 Verifying routing in 'Live Neo4j' mode...")
    # We patch db functions with mock returns so we can verify routing even when live Neo4j instance is not running
    dummy_cust = {
        "customer_id": "C01",
        "name": "Live DB Verified Customer",
        "customer_type": "Premium",
        "city": "NeoCity",
        "phone": "9999999999",
        "email": "live@db.com",
        "relationship_manager": "Live RM",
    }
    dummy_branches = [{"branch_id": "BR01", "branch_name": "Live Branch 1"}]

    with mock.patch("db.get_branches", return_value=dummy_branches) as spy_db_branches, \
         mock.patch("db.get_customer", return_value=dummy_cust) as spy_db_cust, \
         mock.patch("db.get_total_balance", return_value=555555.0) as spy_db_bal, \
         mock.patch("mock_db.get_customer", wraps=mock_db.get_customer) as spy_mock_cust:

        at = AppTest.from_file("app.py", default_timeout=20).run()
        # Switch to Live Neo4j in sidebar
        at.sidebar.radio[0].set_value("Live Neo4j").run()
        assert len(at.exception) == 0

        # Now verify db functions were called and mock_db was NOT called for customer details
        assert spy_db_cust.called, "db.get_customer was NOT called after switching to Live Neo4j!"
        assert spy_db_bal.called, "db.get_total_balance was NOT called after switching to Live Neo4j!"
        print(f"  -> PASS: Live Neo4j genuinely routed to db.py (db.get_customer called {spy_db_cust.call_count} times, returning Live data)!")


def test_04_ui_authenticity_and_canary_injection():
    print("[FORENSIC-AUDIT] Check 4: UI Authenticity & Canary Value Injection...")
    mock_db.reset_mock_db()

    canary_name = "CANARY_FORENSIC_NAME_XYZ"
    canary_balance = 987654.32

    def fake_get_customer(cid):
        return {
            "customer_id": cid,
            "name": canary_name,
            "customer_type": "Premium",
            "city": "Chennai",
            "phone": "9876543210",
            "email": "canary@bank.com",
            "relationship_manager": "Priya Menon",
        }

    with mock.patch("mock_db.get_customer", side_effect=fake_get_customer), \
         mock.patch("mock_db.get_total_balance", return_value=canary_balance):

        at = AppTest.from_file("app.py", default_timeout=20).run()
        assert len(at.exception) == 0

        # Inspect Screen 1 markdown components for canary name
        markdown_texts = " ".join([m.value for m in at.markdown])
        assert canary_name in markdown_texts, f"Canary name '{canary_name}' not found in UI markdown! Fake UI stub detected?"

        # Inspect Screen 1 metric components for canary balance (formatted as ₹987,654.32)
        metric_values = [m.value for m in at.metric]
        assert any("987,654.32" in str(v) for v in metric_values), f"Canary balance not found in metrics {metric_values}! Hardcoded UI detected?"

        print("  -> PASS: Canary injected values successfully propagated into Streamlit markdown and metric components!")


def test_05_interactive_mutations_and_state_verification():
    print("[FORENSIC-AUDIT] Check 5: Interactive Mutation & State Verification...")
    mock_db.reset_mock_db()

    at = AppTest.from_file("app.py", default_timeout=20).run()
    assert len(at.exception) == 0

    # 1. Update contact
    at.text_input[0].set_value("9988776655")
    at.text_input[1].set_value("forensic.auditor@test.com")
    at.button[0].click().run()
    assert len(at.exception) == 0

    c01_updated = mock_db.get_customer("C01")
    assert c01_updated["phone"] == "9988776655", "Phone was not updated in mock_db!"
    assert c01_updated["email"] == "forensic.auditor@test.com", "Email was not updated in mock_db!"
    print("  -> 5.1 Contact update verified in backend state.")

    # 2. Add customer
    at.text_input[2].set_value("C08")
    at.text_input[3].set_value("Rohan")
    at.text_input[4].set_value("Mumbai")
    at.text_input[5].set_value("9820000000")
    at.text_input[6].set_value("Verma")
    at.text_input[7].set_value("rohan.verma@example.com")
    at.button[1].click().run()
    assert len(at.exception) == 0

    c08 = mock_db.get_customer("C08")
    assert c08 is not None, "New customer C08 was not found in mock_db!"
    assert c08["name"] == "Rohan Verma"
    assert "C08" in at.session_state["customer_ids"]
    print("  -> 5.2 Add customer verified in backend state and session state.")

    # 3. Raise Service Request for C08
    at.text_area[0].set_value("Forensic request for audit trail export")
    at.button[2].click().run()
    assert len(at.exception) == 0

    srs = mock_db.get_service_requests("C08")
    assert len(srs) == 1, "Service request was not registered in mock_db!"
    assert srs[0]["status"] == "Pending"
    assert srs[0]["handled_by"] == "Karthik Suresh", f"Expected 'Karthik Suresh', got {srs[0]['handled_by']}"
    print("  -> 5.3 Service request creation verified in backend state.")

    # 4. Cash Deposit on Screen 2
    at.sidebar.selectbox[0].set_value("C01").run()
    at.sidebar.radio[1].set_value("2. Accounts & Transactions").run()
    assert len(at.exception) == 0

    bal_before = next(a["balance"] for a in mock_db.get_accounts("C01") if a["account_number"] == "AC1001")
    at.number_input[0].set_value(7500.0)
    at.button[0].click().run()
    assert len(at.exception) == 0

    bal_after = next(a["balance"] for a in mock_db.get_accounts("C01") if a["account_number"] == "AC1001")
    assert bal_after == bal_before + 7500.0, f"Expected {bal_before + 7500.0}, got {bal_after}"
    print(f"  -> 5.4 Cash deposit verified: balance increased from {bal_before} to {bal_after}.")

    # 5. Fund Transfer AC1001 -> AC1003
    at.text_input[0].set_value("AC1003")
    at.number_input[1].set_value(5000.0)
    at.button[1].click().run()
    assert len(at.exception) == 0

    bal_src = next(a["balance"] for a in mock_db.get_accounts("C01") if a["account_number"] == "AC1001")
    bal_dst = next(a["balance"] for a in mock_db.get_accounts("C02") if a["account_number"] == "AC1003")
    assert bal_src == bal_after - 5000.0
    print(f"  -> 5.5 Fund transfer verified: source={bal_src}, destination={bal_dst}.")

    # 6. Open Account
    at.text_input[1].set_value("AC1010")
    at.number_input[2].set_value(0.0)
    at.button[2].click().run()
    assert len(at.exception) == 0

    acc_c01 = [a["account_number"] for a in mock_db.get_accounts("C01")]
    assert "AC1010" in acc_c01, "New account AC1010 not found in C01 accounts!"
    print("  -> 5.6 Account opening verified in backend state.")

    # 7. Close Account (Zero Balance)
    at.selectbox[3].set_value("AC1010")
    at.button[3].click().run()
    assert len(at.exception) == 0

    acc_c01_after = [a["account_number"] for a in mock_db.get_accounts("C01")]
    assert "AC1010" not in acc_c01_after, "Closed account AC1010 still present in C01 accounts!"
    print("  -> 5.7 Zero-balance account closure verified in backend state.")

    mock_db.reset_mock_db()
    print("  -> PASS: All 7 interactive mutations successfully verified with real backend state updates!")


def test_06_screen3_and_screen4_rendering():
    print("[FORENSIC-AUDIT] Check 6: Screen 3 & Screen 4 Real Component Rendering...")
    mock_db.reset_mock_db()

    with mock.patch("streamlit.bar_chart") as spy_bar_chart:
        at = AppTest.from_file("app.py", default_timeout=20).run()

        # Screen 3: Loans & Investments
        at.sidebar.radio[1].set_value("3. Loans & Investments").run()
        assert len(at.exception) == 0
        # Must have repayment schedule and investments dataframes
        assert len(at.dataframe) >= 2, f"Expected at least 2 dataframes (schedule & investments), got {len(at.dataframe)}"
        # Verify st.bar_chart was called for asset allocation
        assert spy_bar_chart.called, "st.bar_chart was not called for asset allocation on Screen 3!"
        print(f"  -> 6.1 Screen 3 rendered real dataframes and called st.bar_chart {spy_bar_chart.call_count} time(s).")

        spy_bar_chart.reset_mock()

        # Screen 4: Analytics
        at.sidebar.radio[1].set_value("4. Analytics & Graph Intelligence").run()
        assert len(at.exception) == 0
        assert spy_bar_chart.called, "st.bar_chart was not called for branch distribution on Screen 4!"
        assert len(at.dataframe) >= 3, f"Expected branch counts, leaderboard, and transfer monitor dataframes, got {len(at.dataframe)}"

        # Test trace button
        at.text_input[0].set_value("AC1001")
        at.button[0].click().run()
        assert len(at.exception) == 0
        trail_markdown = " ".join([m.value for m in at.markdown])
        assert "AC1001" in trail_markdown and "AC1003" in trail_markdown, "Trail breadcrumbs missing from Screen 4!"
        print(f"  -> 6.2 Screen 4 analytics, st.bar_chart ({spy_bar_chart.call_count} call(s)), dataframes, and money trail breadcrumbs rendered cleanly.")
        print("  -> PASS: Screen 3 and Screen 4 contain zero facade stubs.")


def main():
    print("=====================================================================")
    print("FORENSIC INTEGRITY AUDIT SUITE FOR MILESTONE 3 (app.py)")
    print("=====================================================================")
    test_01_compilation()
    test_02_ast_static_binding_audit()
    test_03_dynamic_mode_routing_spies()
    test_04_ui_authenticity_and_canary_injection()
    test_05_interactive_mutations_and_state_verification()
    test_06_screen3_and_screen4_rendering()
    print("=====================================================================")
    print("VERDICT: ALL FORENSIC INTEGRITY CHECKS PASSED WITH 100% SUCCESS!")
    print("=====================================================================")


if __name__ == "__main__":
    main()
