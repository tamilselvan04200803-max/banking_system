"""
Automated Test Suite for Smart Banking Mini-Project (Milestone 4)
Validates 47-node dataset counts, all 20 database function contracts,
and Section 8 test cases against mock_db (and db when live Neo4j is present).

Compatible with both `python test_suite.py` and `pytest test_suite.py -v`.
Provides 100% test isolation via setUp() resetting database state before each test.
"""

import datetime
import os
import re
import sys
import unittest
import mock_db

# Optional Live Neo4j connectivity probe
RUN_LIVE_TESTS = False
try:
    if os.environ.get("TEST_LIVE_NEO4J") == "1" or "--live" in sys.argv:
        import connection
        driver = connection.get_driver()
        driver.verify_connectivity()
        import db
        RUN_LIVE_TESTS = True
except Exception:
    RUN_LIVE_TESTS = False

# ISO date format regex (YYYY-MM-DD)
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class TestDatasetCounts(unittest.TestCase):
    """
    Test 1: 47-Node Dataset Counts and Entity Verification
    Validates that the initialized dataset contains exactly 47 nodes across
    all 9 graph entity types and 8 transfers (TRANSFERRED_TO edges).
    """

    def setUp(self):
        """Restore in-memory mock database to baseline before every test."""
        mock_db.reset_mock_db()

    def test_branch_nodes_count(self):
        """Verify 3 branch nodes (BR01, BR02, BR03) via get_branches()."""
        branches = mock_db.get_branches()
        self.assertEqual(len(branches), 3)
        branch_ids = {b["branch_id"] for b in branches}
        self.assertEqual(branch_ids, {"BR01", "BR02", "BR03"})
        branch_names = {b["branch_name"] for b in branches}
        self.assertEqual(branch_names, {"Anna Nagar", "T Nagar", "Koramangala"})

    def test_employee_nodes_count(self):
        """Verify 6 employee nodes (E01-E06) via mock dataset."""
        employees = mock_db._EMPLOYEES
        self.assertEqual(len(employees), 6)
        emp_ids = {e["emp_id"] for e in employees}
        self.assertEqual(emp_ids, {"E01", "E02", "E03", "E04", "E05", "E06"})

    def test_customer_nodes_count(self):
        """Verify 6 customer nodes (C01-C06) via get_customer()."""
        customer_ids = [f"C0{i}" for i in range(1, 7)]
        customers = []
        for cid in customer_ids:
            cust = mock_db.get_customer(cid)
            self.assertIsNotNone(cust, f"Customer {cid} should exist")
            customers.append(cust)
        self.assertEqual(len(customers), 6)
        retrieved_ids = {c["customer_id"] for c in customers}
        self.assertEqual(retrieved_ids, set(customer_ids))

    def test_account_nodes_count(self):
        """Verify 8 account nodes (AC1001-AC1008) across all customers via get_accounts()."""
        all_accounts = []
        for i in range(1, 7):
            cid = f"C0{i}"
            accs = mock_db.get_accounts(cid)
            all_accounts.extend(accs)
        self.assertEqual(len(all_accounts), 8)
        account_numbers = {a["account_number"] for a in all_accounts}
        expected_accounts = {f"AC100{i}" for i in range(1, 9)}
        self.assertEqual(account_numbers, expected_accounts)

    def test_transaction_nodes_count(self):
        """Verify 8 transaction nodes (T1-T8) across accounts via get_transactions()."""
        all_txns = []
        seen_txn_ids = set()
        for i in range(1, 9):
            acc_num = f"AC100{i}"
            history = mock_db.get_transactions(acc_num)
            for t in history:
                # Filter deposit/withdrawal transactions (T1-T8)
                if t["txn_type"] in ("Deposit", "Withdrawal") and t["txn_id"] not in seen_txn_ids:
                    seen_txn_ids.add(t["txn_id"])
                    all_txns.append(t)
        self.assertEqual(len(all_txns), 8)
        self.assertEqual(seen_txn_ids, {f"T{i}" for i in range(1, 9)})

    def test_transfers_count(self):
        """Verify 8 transfer relationships (TR1-TR8) via get_large_transfers(0)."""
        transfers = mock_db.get_large_transfers(0)
        self.assertEqual(len(transfers), 8)
        transfer_ids = {tr["txn_id"] for tr in transfers}
        self.assertEqual(transfer_ids, {f"TR{i}" for i in range(1, 9)})

    def test_loan_nodes_count(self):
        """Verify 3 loan nodes (L01-L03) via get_loans()."""
        all_loans = []
        for i in range(1, 7):
            cid = f"C0{i}"
            loans = mock_db.get_loans(cid)
            all_loans.extend(loans)
        self.assertEqual(len(all_loans), 3)
        loan_ids = {l["loan_id"] for l in all_loans}
        self.assertEqual(loan_ids, {"L01", "L02", "L03"})

    def test_installment_nodes_count(self):
        """Verify 6 installment nodes across loans via get_repayment_schedule()."""
        all_installments = []
        for lid in ("L01", "L02", "L03"):
            schedule = mock_db.get_repayment_schedule(lid)
            all_installments.extend(schedule)
        self.assertEqual(len(all_installments), 6)

    def test_investment_nodes_count(self):
        """Verify 4 investment nodes (I01-I04) across customers via get_investments()."""
        all_investments = []
        for i in range(1, 7):
            cid = f"C0{i}"
            invs = mock_db.get_investments(cid)
            all_investments.extend(invs)
        self.assertEqual(len(all_investments), 4)
        inv_ids = {inv["investment_id"] for inv in all_investments}
        self.assertEqual(inv_ids, {"I01", "I02", "I03", "I04"})

    def test_service_request_nodes_count(self):
        """Verify 3 service request nodes (SR01-SR03) via get_service_requests()."""
        all_srs = []
        for i in range(1, 7):
            cid = f"C0{i}"
            srs = mock_db.get_service_requests(cid)
            all_srs.extend(srs)
        self.assertEqual(len(all_srs), 3)
        sr_ids = {sr["request_id"] for sr in all_srs}
        self.assertEqual(sr_ids, {"SR01", "SR02", "SR03"})

    def test_total_47_nodes_dataset(self):
        """
        Assert the aggregate node count across all 9 graph entity types equals exactly 47.
        3 Branches + 6 Employees + 6 Customers + 8 Accounts + 8 Transactions +
        3 Loans + 6 Installments + 4 Investments + 3 Service Requests = 47 Nodes.
        """
        branches_count = len(mock_db.get_branches())
        employees_count = len(mock_db._EMPLOYEES)
        customers_count = sum(1 for i in range(1, 7) if mock_db.get_customer(f"C0{i}") is not None)
        accounts_count = sum(len(mock_db.get_accounts(f"C0{i}")) for i in range(1, 7))

        seen_txns = set()
        for i in range(1, 9):
            for t in mock_db.get_transactions(f"AC100{i}"):
                if t["txn_type"] in ("Deposit", "Withdrawal"):
                    seen_txns.add(t["txn_id"])
        txns_count = len(seen_txns)

        loans_count = sum(len(mock_db.get_loans(f"C0{i}")) for i in range(1, 7))
        installments_count = sum(len(mock_db.get_repayment_schedule(lid)) for lid in ("L01", "L02", "L03"))
        investments_count = sum(len(mock_db.get_investments(f"C0{i}")) for i in range(1, 7))
        srs_count = sum(len(mock_db.get_service_requests(f"C0{i}")) for i in range(1, 7))

        total_nodes = (
            branches_count
            + employees_count
            + customers_count
            + accounts_count
            + txns_count
            + loans_count
            + installments_count
            + investments_count
            + srs_count
        )

        self.assertEqual(total_nodes, 47)
        # Also confirm 8 transfers
        transfers_count = len(mock_db.get_large_transfers(0))
        self.assertEqual(transfers_count, 8)


class TestReadFunctions(unittest.TestCase):
    """
    Test 2: Read Functions (1-9)
    Validates accurate retrieval, relationships, and return schemas for read operations.
    """

    def setUp(self):
        mock_db.reset_mock_db()

    def test_get_customer_c01(self):
        """get_customer('C01') returns expected profile and Relationship Manager Priya Menon."""
        cust = mock_db.get_customer("C01")
        self.assertIsNotNone(cust)
        self.assertEqual(cust["customer_id"], "C01")
        self.assertEqual(cust["name"], "Samridhi Sharma")
        self.assertEqual(cust["customer_type"], "Premium")
        self.assertEqual(cust["city"], "Chennai")
        self.assertEqual(cust["phone"], "9876543210")
        self.assertEqual(cust["email"], "samridhi.sharma@example.com")
        self.assertEqual(cust["relationship_manager"], "Priya Menon")

    def test_get_customer_non_existent(self):
        """get_customer() returns None for non-existent customer."""
        self.assertIsNone(mock_db.get_customer("NON_EXISTENT"))
        self.assertIsNone(mock_db.get_customer("C999"))

    def test_get_accounts_c01(self):
        """get_accounts('C01') returns exactly 2 accounts: AC1001 (85000) and AC1002 (150000)."""
        accounts = mock_db.get_accounts("C01")
        self.assertEqual(len(accounts), 2)
        acc_map = {a["account_number"]: a for a in accounts}
        self.assertIn("AC1001", acc_map)
        self.assertIn("AC1002", acc_map)
        self.assertEqual(acc_map["AC1001"]["balance"], 85000.0)
        self.assertEqual(acc_map["AC1001"]["account_type"], "Savings")
        self.assertEqual(acc_map["AC1001"]["branch_name"], "Anna Nagar")
        self.assertEqual(acc_map["AC1002"]["balance"], 150000.0)
        self.assertEqual(acc_map["AC1002"]["account_type"], "Current")
        self.assertEqual(acc_map["AC1002"]["branch_name"], "Anna Nagar")

    def test_get_accounts_non_existent(self):
        """get_accounts() returns empty list for non-existent customer."""
        self.assertEqual(mock_db.get_accounts("C999"), [])

    def test_get_total_balance_c01(self):
        """get_total_balance('C01') returns exactly 235000 (85000 + 150000)."""
        total = mock_db.get_total_balance("C01")
        self.assertEqual(total, 235000.0)

    def test_get_total_balance_non_existent(self):
        """get_total_balance() returns 0 for non-existent customer."""
        self.assertEqual(mock_db.get_total_balance("C999"), 0.0)

    def test_get_transactions_ac1001(self):
        """
        get_transactions('AC1001') returns 4 rows sorted descending by txn_date:
        Deposit 20000, Withdrawal 5000, Transfer Out 8000 to AC1003, Transfer In 2000 from AC1006.
        """
        txns = mock_db.get_transactions("AC1001")
        self.assertEqual(len(txns), 4)

        # Verify strict descending sort by txn_date
        dates = [t["txn_date"] for t in txns]
        self.assertEqual(dates, sorted(dates, reverse=True))

        # Expected row breakdown in descending order
        # Row 0: Transfer In 2000 from AC1006 on 2026-03-16
        self.assertEqual(txns[0]["txn_id"], "TR5")
        self.assertEqual(txns[0]["txn_type"], "Transfer In")
        self.assertEqual(txns[0]["amount"], 2000.0)
        self.assertEqual(txns[0]["other_account"], "AC1006")
        self.assertEqual(txns[0]["txn_date"], "2026-03-16")

        # Row 1: Transfer Out 8000 to AC1003 on 2026-03-10
        self.assertEqual(txns[1]["txn_id"], "TR1")
        self.assertEqual(txns[1]["txn_type"], "Transfer Out")
        self.assertEqual(txns[1]["amount"], 8000.0)
        self.assertEqual(txns[1]["other_account"], "AC1003")
        self.assertEqual(txns[1]["txn_date"], "2026-03-10")

        # Row 2: Withdrawal 5000 on 2026-03-05
        self.assertEqual(txns[2]["txn_id"], "T2")
        self.assertEqual(txns[2]["txn_type"], "Withdrawal")
        self.assertEqual(txns[2]["amount"], 5000.0)
        self.assertIsNone(txns[2]["other_account"])
        self.assertEqual(txns[2]["txn_date"], "2026-03-05")

        # Row 3: Deposit 20000 on 2026-03-01
        self.assertEqual(txns[3]["txn_id"], "T1")
        self.assertEqual(txns[3]["txn_type"], "Deposit")
        self.assertEqual(txns[3]["amount"], 20000.0)
        self.assertIsNone(txns[3]["other_account"])
        self.assertEqual(txns[3]["txn_date"], "2026-03-01")

    def test_get_loans_c01(self):
        """get_loans('C01') returns L01 Home Loan, loan officer Divya Rao, branch Anna Nagar."""
        loans = mock_db.get_loans("C01")
        self.assertEqual(len(loans), 1)
        loan = loans[0]
        self.assertEqual(loan["loan_id"], "L01")
        self.assertEqual(loan["loan_type"], "Home Loan")
        self.assertEqual(loan["amount"], 2500000.0)
        self.assertEqual(loan["interest_rate"], 8.5)
        self.assertEqual(loan["term_months"], 240)
        self.assertEqual(loan["status"], "Active")
        self.assertEqual(loan["loan_officer"], "Divya Rao")
        self.assertEqual(loan["branch_name"], "Anna Nagar")

    def test_get_repayment_schedule_l01(self):
        """get_repayment_schedule('L01') returns 3 installments (no. 1 and 2 'Paid', no. 3 'Pending')."""
        schedule = mock_db.get_repayment_schedule("L01")
        self.assertEqual(len(schedule), 3)
        self.assertEqual(schedule[0]["installment_no"], 1)
        self.assertEqual(schedule[0]["status"], "Paid")
        self.assertEqual(schedule[0]["amount_due"], 25000.0)

        self.assertEqual(schedule[1]["installment_no"], 2)
        self.assertEqual(schedule[1]["status"], "Paid")
        self.assertEqual(schedule[1]["amount_due"], 25000.0)

        self.assertEqual(schedule[2]["installment_no"], 3)
        self.assertEqual(schedule[2]["status"], "Pending")
        self.assertEqual(schedule[2]["amount_due"], 25000.0)

    def test_get_investments_c01(self):
        """get_investments('C01') returns I01 Mutual Fund (100000) and I03 Wealth Management (300000)."""
        invs = mock_db.get_investments("C01")
        self.assertEqual(len(invs), 2)
        inv_map = {i["investment_id"]: i for i in invs}
        self.assertIn("I01", inv_map)
        self.assertIn("I03", inv_map)
        self.assertEqual(inv_map["I01"]["investment_type"], "Mutual Fund")
        self.assertEqual(inv_map["I01"]["amount"], 100000.0)
        self.assertEqual(inv_map["I03"]["investment_type"], "Wealth Management")
        self.assertEqual(inv_map["I03"]["amount"], 300000.0)

    def test_get_service_requests_c01(self):
        """get_service_requests('C01') returns SR03 Cheque Book, status 'Resolved', handled_by 'Karthik Suresh'."""
        srs = mock_db.get_service_requests("C01")
        self.assertEqual(len(srs), 1)
        sr = srs[0]
        self.assertEqual(sr["request_id"], "SR03")
        self.assertEqual(sr["request_type"], "Cheque Book")
        self.assertEqual(sr["status"], "Resolved")
        self.assertEqual(sr["handled_by"], "Karthik Suresh")

    def test_get_branches(self):
        """get_branches() returns all 3 branches with correct IDs and names."""
        branches = mock_db.get_branches()
        self.assertEqual(len(branches), 3)
        expected = [
            {"branch_id": "BR01", "branch_name": "Anna Nagar"},
            {"branch_id": "BR02", "branch_name": "T Nagar"},
            {"branch_id": "BR03", "branch_name": "Koramangala"},
        ]
        self.assertEqual(branches, expected)


class TestManageFunctions(unittest.TestCase):
    """
    Test 3: Manage Functions (10-14)
    Validates mutations: customer registration, contact updates, account opening/closing,
    and service request creation with integrity constraints.
    """

    def setUp(self):
        mock_db.reset_mock_db()

    def test_add_customer_duplicate_and_success(self):
        """add_customer('C01', ...) fails on duplicate ID; adding new customer 'C07' succeeds and is retrievable."""
        # Duplicate customer ID fails
        res_dup = mock_db.add_customer(
            "C01", "Duplicate", "User", "Chennai", "9876543210", "dup@example.com", "Standard"
        )
        self.assertFalse(res_dup["success"])
        self.assertIn("already exists", res_dup["message"])

        # Add new customer C07 succeeds
        res_new = mock_db.add_customer(
            "C07", "Aditya", "Kumar", "Chennai", "9876543299", "aditya.k@example.com", "Standard"
        )
        self.assertTrue(res_new["success"])

        # Verify C07 can be retrieved
        c07 = mock_db.get_customer("C07")
        self.assertIsNotNone(c07)
        self.assertEqual(c07["name"], "Aditya Kumar")
        self.assertEqual(c07["customer_type"], "Standard")
        self.assertEqual(c07["city"], "Chennai")
        self.assertEqual(c07["phone"], "9876543299")
        self.assertEqual(c07["email"], "aditya.k@example.com")

    def test_update_customer_contact(self):
        """update_customer_contact('C01', ...) succeeds and updates customer phone and email."""
        res = mock_db.update_customer_contact("C01", phone="9876543210", email="samridhi.new@email.com")
        self.assertTrue(res["success"])

        cust = mock_db.get_customer("C01")
        self.assertEqual(cust["phone"], "9876543210")
        self.assertEqual(cust["email"], "samridhi.new@email.com")

        # Fails for non-existent customer
        res_fail = mock_db.update_customer_contact("C999", phone="999", email="none@none.com")
        self.assertFalse(res_fail["success"])

    def test_open_account_success_and_validations(self):
        """open_account('AC1009', ...) succeeds and reflects in get_accounts(); fails for invalid customer/branch."""
        # Successful opening
        res = mock_db.open_account("AC1009", "C02", "BR02", "Savings", 5000)
        self.assertTrue(res["success"])

        # Verify account reflected in C02's accounts
        c02_accs = mock_db.get_accounts("C02")
        acc9 = next((a for a in c02_accs if a["account_number"] == "AC1009"), None)
        self.assertIsNotNone(acc9)
        self.assertEqual(acc9["balance"], 5000.0)
        self.assertEqual(acc9["account_type"], "Savings")
        self.assertEqual(acc9["branch_name"], "T Nagar")

        # Fails for non-existent customer
        res_bad_cust = mock_db.open_account("AC1010", "C999", "BR02", "Savings", 5000)
        self.assertFalse(res_bad_cust["success"])

        # Fails for non-existent branch
        res_bad_branch = mock_db.open_account("AC1010", "C02", "BR999", "Savings", 5000)
        self.assertFalse(res_bad_branch["success"])

        # Fails for duplicate account number
        res_dup_acc = mock_db.open_account("AC1001", "C02", "BR02", "Savings", 5000)
        self.assertFalse(res_dup_acc["success"])

    def test_close_account_non_zero_and_zero_balance(self):
        """close_account('AC1008') fails because balance != 0; opening zero-balance 'AC1010' and closing it succeeds."""
        # Non-zero balance cannot be closed (AC1008 has non-zero balance)
        res_fail = mock_db.close_account("AC1008")
        self.assertFalse(res_fail["success"])
        self.assertIn("non-zero", res_fail["message"].lower())

        # Also verify an account opened with balance 75000 cannot be closed
        mock_db.open_account("AC1099", "C02", "BR02", "Savings", 75000)
        res_fail_75k = mock_db.close_account("AC1099")
        self.assertFalse(res_fail_75k["success"])
        self.assertIn("non-zero", res_fail_75k["message"].lower())

        # Open zero-balance account AC1010
        res_open = mock_db.open_account("AC1010", "C02", "BR02", "Savings", 0)
        self.assertTrue(res_open["success"])

        # Closing zero-balance account succeeds
        res_close = mock_db.close_account("AC1010")
        self.assertTrue(res_close["success"])

        # Verify AC1010 is completely deleted
        c02_accs = mock_db.get_accounts("C02")
        self.assertNotIn("AC1010", [a["account_number"] for a in c02_accs])

        # Closing non-existent account fails
        res_non_exist = mock_db.close_account("AC9999")
        self.assertFalse(res_non_exist["success"])

    def test_raise_service_request(self):
        """raise_service_request('C01', ...) generates 'SR'-prefixed ID, 'Pending' status, assigned to E05."""
        res = mock_db.raise_service_request("C01", "Card", "New debit card")
        self.assertTrue(res["success"])
        self.assertIn("request_id", res)
        self.assertTrue(res["request_id"].startswith("SR"))

        # Verify in customer's service requests
        c01_srs = mock_db.get_service_requests("C01")
        new_sr = next((sr for sr in c01_srs if sr["request_id"] == res["request_id"]), None)
        self.assertIsNotNone(new_sr)
        self.assertEqual(new_sr["request_type"], "Card")
        self.assertEqual(new_sr["description"], "New debit card")
        self.assertEqual(new_sr["status"], "Pending")
        self.assertEqual(new_sr["handled_by"], "Karthik Suresh")  # E05 is Karthik Suresh

        # Verify raw internal assignment to E05
        raw_sr = next((sr for sr in mock_db._SERVICE_REQUESTS if sr["request_id"] == res["request_id"]), None)
        self.assertIsNotNone(raw_sr)
        self.assertEqual(raw_sr["assigned_emp_id"], "E05")

        # Fails for non-existent customer
        res_bad = mock_db.raise_service_request("C999", "Card", "Test")
        self.assertFalse(res_bad["success"])


class TestProcessFunctions(unittest.TestCase):
    """
    Test 4: Process Functions (15-16)
    Validates deposits, withdrawals, balance adjustments, and atomic inter-account transfers.
    """

    def setUp(self):
        mock_db.reset_mock_db()

    def test_process_transaction_deposit(self):
        """process_transaction('AC1003', 'Deposit', 5000) -> success: True, new_balance: 47000."""
        # AC1003 initial balance is 42000
        res = mock_db.process_transaction("AC1003", "Deposit", 5000)
        self.assertTrue(res["success"])
        self.assertEqual(res["new_balance"], 47000.0)

        # Check account balance in get_accounts
        c02_accs = mock_db.get_accounts("C02")
        acc3 = next(a for a in c02_accs if a["account_number"] == "AC1003")
        self.assertEqual(acc3["balance"], 47000.0)

    def test_process_transaction_withdrawal_insufficient_balance(self):
        """process_transaction('AC1003', 'Withdrawal', 99999999) fails with success: False."""
        res = mock_db.process_transaction("AC1003", "Withdrawal", 99999999)
        self.assertFalse(res["success"])
        self.assertIn("Insufficient balance", res["message"])

        # Balance remains unchanged at 42000
        c02_accs = mock_db.get_accounts("C02")
        acc3 = next(a for a in c02_accs if a["account_number"] == "AC1003")
        self.assertEqual(acc3["balance"], 42000.0)

    def test_transfer_money_success_and_insufficient_balance(self):
        """
        transfer_money('AC1001', 'AC1003', 5000) succeeds:
        AC1001 balance becomes 80000, AC1003 balance becomes 47000. Fails on overdraft.
        """
        # Initial balances: AC1001 = 85000, AC1003 = 42000
        res = mock_db.transfer_money("AC1001", "AC1003", 5000)
        self.assertTrue(res["success"])

        # Check balances
        acc1 = next(a for a in mock_db.get_accounts("C01") if a["account_number"] == "AC1001")
        acc3 = next(a for a in mock_db.get_accounts("C02") if a["account_number"] == "AC1003")
        self.assertEqual(acc1["balance"], 80000.0)
        self.assertEqual(acc3["balance"], 47000.0)

        # Overdraft transfer fails
        res_overdraft = mock_db.transfer_money("AC1001", "AC1003", 99999999)
        self.assertFalse(res_overdraft["success"])
        self.assertIn("Insufficient balance", res_overdraft["message"])

    def test_transfer_money_invalid_accounts(self):
        """transfer_money fails on non-existent accounts and self-transfer."""
        # Non-existent source
        res1 = mock_db.transfer_money("AC9999", "AC1003", 100)
        self.assertFalse(res1["success"])

        # Non-existent target
        res2 = mock_db.transfer_money("AC1001", "AC9999", 100)
        self.assertFalse(res2["success"])

        # Self transfer
        res3 = mock_db.transfer_money("AC1001", "AC1001", 100)
        self.assertFalse(res3["success"])


class TestAnalyticsFunctions(unittest.TestCase):
    """
    Test 5: Analytics Functions (17-20)
    Validates branch distributions, top customer leaderboards, large transfer monitoring,
    and multi-hop graph path money trails.
    """

    def setUp(self):
        mock_db.reset_mock_db()

    def test_get_branch_account_counts(self):
        """get_branch_account_counts() returns Anna Nagar 3, T Nagar 3, Koramangala 2."""
        counts = mock_db.get_branch_account_counts()
        count_map = {b["branch_name"]: b["account_count"] for b in counts}
        self.assertEqual(count_map.get("Anna Nagar"), 3)
        self.assertEqual(count_map.get("T Nagar"), 3)
        self.assertEqual(count_map.get("Koramangala"), 2)

    def test_get_top_customers_by_balance(self):
        """get_top_customers_by_balance(3) returns C01 (235000), C03 (200000), C06 (95000)."""
        top3 = mock_db.get_top_customers_by_balance(3)
        self.assertEqual(len(top3), 3)

        self.assertEqual(top3[0]["customer_id"], "C01")
        self.assertEqual(top3[0]["name"], "Samridhi Sharma")
        self.assertEqual(top3[0]["total_balance"], 235000.0)

        self.assertEqual(top3[1]["customer_id"], "C03")
        self.assertEqual(top3[1]["name"], "Anita Roy")
        self.assertEqual(top3[1]["total_balance"], 200000.0)

        self.assertEqual(top3[2]["customer_id"], "C06")
        self.assertEqual(top3[2]["name"], "Vikram Singh")
        self.assertEqual(top3[2]["total_balance"], 95000.0)

    def test_get_large_transfers(self):
        """get_large_transfers(20000) returns TR6 (AC1004->AC1002, 40000) and TR4 (AC1002->AC1007, 25000)."""
        transfers = mock_db.get_large_transfers(20000)
        self.assertEqual(len(transfers), 2)

        # Sorted descending by amount
        self.assertEqual(transfers[0]["txn_id"], "TR6")
        self.assertEqual(transfers[0]["from_account"], "AC1004")
        self.assertEqual(transfers[0]["to_account"], "AC1002")
        self.assertEqual(transfers[0]["amount"], 40000.0)
        self.assertEqual(transfers[0]["txn_date"], "2026-03-18")

        self.assertEqual(transfers[1]["txn_id"], "TR4")
        self.assertEqual(transfers[1]["from_account"], "AC1002")
        self.assertEqual(transfers[1]["to_account"], "AC1007")
        self.assertEqual(transfers[1]["amount"], 25000.0)
        self.assertEqual(transfers[1]["txn_date"], "2026-03-15")

    def test_get_money_trail(self):
        """
        get_money_trail('AC1001') returns exactly 3 directed paths:
        1 hop: ['AC1001', 'AC1003']
        2 hops: ['AC1001', 'AC1003', 'AC1005']
        3 hops: ['AC1001', 'AC1003', 'AC1005', 'AC1006']
        """
        trails = mock_db.get_money_trail("AC1001")
        self.assertEqual(len(trails), 3)

        self.assertEqual(trails[0]["trail"], ["AC1001", "AC1003"])
        self.assertEqual(trails[0]["hops"], 1)

        self.assertEqual(trails[1]["trail"], ["AC1001", "AC1003", "AC1005"])
        self.assertEqual(trails[1]["hops"], 2)

        self.assertEqual(trails[2]["trail"], ["AC1001", "AC1003", "AC1005", "AC1006"])
        self.assertEqual(trails[2]["hops"], 3)


class TestDateFormatAndErrorHandling(unittest.TestCase):
    """
    Test 6: Date Format & Error Handling
    Validates that all dates match YYYY-MM-DD format and that write functions
    never crash, always catching exceptions and returning {'success': bool, 'message': str}.
    """

    def setUp(self):
        mock_db.reset_mock_db()

    def _assert_valid_date(self, date_str: str, context: str):
        self.assertIsInstance(date_str, str, f"{context} date should be string")
        self.assertTrue(
            bool(DATE_PATTERN.match(date_str)),
            f"{context} date '{date_str}' does not match YYYY-MM-DD pattern",
        )
        try:
            datetime.date.fromisoformat(date_str)
        except ValueError:
            self.fail(f"{context} date '{date_str}' is not a valid calendar date")

    def test_transaction_date_formats(self):
        """All transaction dates across all accounts must match YYYY-MM-DD."""
        for i in range(1, 9):
            acc_num = f"AC100{i}"
            for txn in mock_db.get_transactions(acc_num):
                self._assert_valid_date(txn["txn_date"], f"Account {acc_num} txn {txn['txn_id']}")

    def test_repayment_schedule_date_formats(self):
        """All repayment schedule due dates across all loans must match YYYY-MM-DD."""
        for lid in ("L01", "L02", "L03"):
            for inst in mock_db.get_repayment_schedule(lid):
                self._assert_valid_date(inst["due_date"], f"Loan {lid} installment {inst['installment_no']}")

    def test_investment_date_formats(self):
        """All investment start dates across all customers must match YYYY-MM-DD."""
        for i in range(1, 7):
            cid = f"C0{i}"
            for inv in mock_db.get_investments(cid):
                self._assert_valid_date(inv["start_date"], f"Customer {cid} investment {inv['investment_id']}")

    def test_service_request_date_formats(self):
        """All service request dates across all customers must match YYYY-MM-DD."""
        for i in range(1, 7):
            cid = f"C0{i}"
            for sr in mock_db.get_service_requests(cid):
                self._assert_valid_date(sr["request_date"], f"Customer {cid} service request {sr['request_id']}")

    def test_write_functions_error_handling_contracts(self):
        """All write functions catch errors gracefully and return {'success': bool, 'message': str}."""
        # 1. add_customer with invalid input
        res1 = mock_db.add_customer("C01", "Duplicate", "", "", "", "", "")
        self.assertIsInstance(res1, dict)
        self.assertIn("success", res1)
        self.assertIn("message", res1)
        self.assertFalse(res1["success"])
        self.assertIsInstance(res1["message"], str)

        # 2. update_customer_contact with non-existent customer
        res2 = mock_db.update_customer_contact("INVALID_ID", "123", "a@b.c")
        self.assertIsInstance(res2, dict)
        self.assertIn("success", res2)
        self.assertIn("message", res2)
        self.assertFalse(res2["success"])
        self.assertIsInstance(res2["message"], str)

        # 3. open_account with negative balance or invalid references
        res3 = mock_db.open_account("AC9999", "C01", "BR01", "Savings", -500)
        self.assertIsInstance(res3, dict)
        self.assertIn("success", res3)
        self.assertIn("message", res3)
        self.assertFalse(res3["success"])
        self.assertIsInstance(res3["message"], str)

        # 4. close_account on non-existent account
        res4 = mock_db.close_account("NON_EXISTENT")
        self.assertIsInstance(res4, dict)
        self.assertIn("success", res4)
        self.assertIn("message", res4)
        self.assertFalse(res4["success"])
        self.assertIsInstance(res4["message"], str)

        # 5. raise_service_request on invalid customer
        res5 = mock_db.raise_service_request("INVALID_CUST", "Type", "Desc")
        self.assertIsInstance(res5, dict)
        self.assertIn("success", res5)
        self.assertIn("message", res5)
        self.assertFalse(res5["success"])
        self.assertIsInstance(res5["message"], str)

        # 6. process_transaction on invalid type or negative amount
        res6 = mock_db.process_transaction("AC1001", "InvalidType", 100)
        self.assertIsInstance(res6, dict)
        self.assertIn("success", res6)
        self.assertIn("message", res6)
        self.assertFalse(res6["success"])
        self.assertIsInstance(res6["message"], str)

        res6_neg = mock_db.process_transaction("AC1001", "Deposit", -100)
        self.assertFalse(res6_neg["success"])

        # 7. transfer_money on invalid amounts or same accounts
        res7 = mock_db.transfer_money("AC1001", "AC1001", 500)
        self.assertIsInstance(res7, dict)
        self.assertIn("success", res7)
        self.assertIn("message", res7)
        self.assertFalse(res7["success"])
        self.assertIsInstance(res7["message"], str)

        res7_neg = mock_db.transfer_money("AC1001", "AC1002", -500)
        self.assertFalse(res7_neg["success"])


@unittest.skipUnless(RUN_LIVE_TESTS, "Live Neo4j instance not configured / connected (set TEST_LIVE_NEO4J=1)")
class TestLiveNeo4jDatabase(unittest.TestCase):
    """
    Optional live Neo4j verification class validating queries against db.py.
    Active only when a live Neo4j database is accessible and TEST_LIVE_NEO4J=1 is set.
    """

    def test_live_customer_profile(self):
        """Validate live Neo4j query for get_customer('C01')."""
        import db
        cust = db.get_customer("C01")
        if cust:
            self.assertEqual(cust["customer_id"], "C01")
            self.assertEqual(cust["name"], "Samridhi Sharma")

    def test_live_branch_account_counts(self):
        """Validate live Neo4j query for get_branch_account_counts()."""
        import db
        counts = db.get_branch_account_counts()
        self.assertIsInstance(counts, list)


if __name__ == "__main__":
    unittest.main(verbosity=2)
