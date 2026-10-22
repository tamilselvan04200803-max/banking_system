"""
In-Memory Mock Database Implementation for Smart Banking Mini-Project
Provides an offline, mutable simulation of the 47-node Neo4j graph dataset.
Matches all 20 database function signatures and return schemas.
"""

import copy
import datetime
import random
import string

try:
    from connection import new_id
except Exception:
    def new_id(prefix: str) -> str:
        chars = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f"{prefix}{chars}"


# ==============================================================================
# Seed Dataset Definition (Exact 47 Nodes & 8 Transfers)
# ==============================================================================

SEED_BRANCHES = [
    {"branch_id": "BR01", "branch_name": "Anna Nagar", "city": "Chennai"},
    {"branch_id": "BR02", "branch_name": "T Nagar", "city": "Chennai"},
    {"branch_id": "BR03", "branch_name": "Koramangala", "city": "Bangalore"},
]

SEED_EMPLOYEES = [
    {"emp_id": "E01", "name": "Ramesh Iyer", "role": "Branch Manager", "email": "ramesh.iyer@smartbank.com", "phone": "9840111101", "branch_id": "BR01"},
    {"emp_id": "E02", "name": "Priya Menon", "role": "Relationship Manager", "email": "priya.menon@smartbank.com", "phone": "9840111102", "branch_id": "BR01"},
    {"emp_id": "E03", "name": "Arjun Nair", "role": "Relationship Manager", "email": "arjun.nair@smartbank.com", "phone": "9840111103", "branch_id": "BR02"},
    {"emp_id": "E04", "name": "Divya Rao", "role": "Loan Officer", "email": "divya.rao@smartbank.com", "phone": "9840111104", "branch_id": "BR01"},
    {"emp_id": "E05", "name": "Karthik Suresh", "role": "Customer Service Executive", "email": "karthik.suresh@smartbank.com", "phone": "9840111105", "branch_id": "BR01"},
    {"emp_id": "E06", "name": "Meena Pillai", "role": "Customer Service Executive", "email": "meena.pillai@smartbank.com", "phone": "9840111106", "branch_id": "BR03"},
]

SEED_CUSTOMERS = [
    {"customer_id": "C01", "first_name": "Samridhi", "last_name": "Sharma", "name": "Samridhi Sharma", "customer_type": "Premium", "city": "Chennai", "phone": "9876543210", "email": "samridhi.sharma@example.com", "rm_emp_id": "E02"},
    {"customer_id": "C02", "first_name": "Rahul", "last_name": "Verma", "name": "Rahul Verma", "customer_type": "Standard", "city": "Chennai", "phone": "9876543211", "email": "rahul.verma@example.com", "rm_emp_id": "E02"},
    {"customer_id": "C03", "first_name": "Anita", "last_name": "Roy", "name": "Anita Roy", "customer_type": "Premium", "city": "Chennai", "phone": "9876543212", "email": "anita.roy@example.com", "rm_emp_id": "E03"},
    {"customer_id": "C04", "first_name": "Suresh", "last_name": "Rao", "name": "Suresh Rao", "customer_type": "Standard", "city": "Chennai", "phone": "9876543213", "email": "suresh.rao@example.com", "rm_emp_id": "E03"},
    {"customer_id": "C05", "first_name": "Lakshmi", "last_name": "Narayanan", "name": "Lakshmi Narayanan", "customer_type": "Standard", "city": "Bangalore", "phone": "9876543214", "email": "lakshmi.narayanan@example.com", "rm_emp_id": "E06"},
    {"customer_id": "C06", "first_name": "Vikram", "last_name": "Singh", "name": "Vikram Singh", "customer_type": "Premium", "city": "Bangalore", "phone": "9876543215", "email": "vikram.singh@example.com", "rm_emp_id": "E06"},
]

SEED_ACCOUNTS = [
    {"account_number": "AC1001", "customer_id": "C01", "branch_id": "BR01", "account_type": "Savings", "balance": 85000.0, "status": "Active"},
    {"account_number": "AC1002", "customer_id": "C01", "branch_id": "BR01", "account_type": "Current", "balance": 150000.0, "status": "Active"},
    {"account_number": "AC1003", "customer_id": "C02", "branch_id": "BR01", "account_type": "Savings", "balance": 42000.0, "status": "Active"},
    {"account_number": "AC1004", "customer_id": "C03", "branch_id": "BR02", "account_type": "Current", "balance": 200000.0, "status": "Active"},
    {"account_number": "AC1005", "customer_id": "C04", "branch_id": "BR02", "account_type": "Savings", "balance": 65000.0, "status": "Active"},
    {"account_number": "AC1006", "customer_id": "C05", "branch_id": "BR02", "account_type": "Savings", "balance": 50000.0, "status": "Active"},
    {"account_number": "AC1007", "customer_id": "C06", "branch_id": "BR03", "account_type": "Current", "balance": 95000.0, "status": "Active"},
    {"account_number": "AC1008", "customer_id": "C05", "branch_id": "BR03", "account_type": "Savings", "balance": 30000.0, "status": "Active"},
]

SEED_TRANSACTIONS = [
    {"txn_id": "T1", "account_number": "AC1001", "txn_type": "Deposit", "amount": 20000.0, "txn_date": "2026-03-01"},
    {"txn_id": "T2", "account_number": "AC1001", "txn_type": "Withdrawal", "amount": 5000.0, "txn_date": "2026-03-05"},
    {"txn_id": "T3", "account_number": "AC1002", "txn_type": "Deposit", "amount": 50000.0, "txn_date": "2026-03-02"},
    {"txn_id": "T4", "account_number": "AC1003", "txn_type": "Deposit", "amount": 15000.0, "txn_date": "2026-03-03"},
    {"txn_id": "T5", "account_number": "AC1004", "txn_type": "Withdrawal", "amount": 10000.0, "txn_date": "2026-03-04"},
    {"txn_id": "T6", "account_number": "AC1005", "txn_type": "Deposit", "amount": 25000.0, "txn_date": "2026-03-06"},
    {"txn_id": "T7", "account_number": "AC1006", "txn_type": "Deposit", "amount": 30000.0, "txn_date": "2026-03-07"},
    {"txn_id": "T8", "account_number": "AC1007", "txn_type": "Withdrawal", "amount": 8000.0, "txn_date": "2026-03-08"},
]

SEED_TRANSFERS = [
    {"txn_id": "TR1", "from_account": "AC1001", "to_account": "AC1003", "amount": 8000.0, "txn_date": "2026-03-10"},
    {"txn_id": "TR2", "from_account": "AC1003", "to_account": "AC1005", "amount": 6000.0, "txn_date": "2026-03-12"},
    {"txn_id": "TR3", "from_account": "AC1005", "to_account": "AC1006", "amount": 4000.0, "txn_date": "2026-03-14"},
    {"txn_id": "TR4", "from_account": "AC1002", "to_account": "AC1007", "amount": 25000.0, "txn_date": "2026-03-15"},
    {"txn_id": "TR5", "from_account": "AC1006", "to_account": "AC1001", "amount": 2000.0, "txn_date": "2026-03-16"},
    {"txn_id": "TR6", "from_account": "AC1004", "to_account": "AC1002", "amount": 40000.0, "txn_date": "2026-03-18"},
    {"txn_id": "TR7", "from_account": "AC1007", "to_account": "AC1008", "amount": 12000.0, "txn_date": "2026-03-20"},
    {"txn_id": "TR8", "from_account": "AC1008", "to_account": "AC1004", "amount": 10000.0, "txn_date": "2026-03-22"},
]

SEED_LOANS = [
    {"loan_id": "L01", "customer_id": "C01", "loan_type": "Home Loan", "amount": 2500000.0, "interest_rate": 8.5, "term_months": 240, "status": "Active", "loan_officer_emp_id": "E04", "branch_id": "BR01"},
    {"loan_id": "L02", "customer_id": "C02", "loan_type": "Personal Loan", "amount": 500000.0, "interest_rate": 11.5, "term_months": 36, "status": "Active", "loan_officer_emp_id": "E04", "branch_id": "BR02"},
    {"loan_id": "L03", "customer_id": "C03", "loan_type": "Car Loan", "amount": 800000.0, "interest_rate": 9.0, "term_months": 60, "status": "Active", "loan_officer_emp_id": "E04", "branch_id": "BR03"},
]

SEED_INSTALLMENTS = [
    {"installment_id": "INS01", "loan_id": "L01", "installment_no": 1, "due_date": "2026-01-10", "amount_due": 25000.0, "status": "Paid"},
    {"installment_id": "INS02", "loan_id": "L01", "installment_no": 2, "due_date": "2026-02-10", "amount_due": 25000.0, "status": "Paid"},
    {"installment_id": "INS03", "loan_id": "L01", "installment_no": 3, "due_date": "2026-03-10", "amount_due": 25000.0, "status": "Pending"},
    {"installment_id": "INS04", "loan_id": "L02", "installment_no": 1, "due_date": "2026-01-15", "amount_due": 16000.0, "status": "Paid"},
    {"installment_id": "INS05", "loan_id": "L02", "installment_no": 2, "due_date": "2026-02-15", "amount_due": 16000.0, "status": "Pending"},
    {"installment_id": "INS06", "loan_id": "L03", "installment_no": 1, "due_date": "2026-03-20", "amount_due": 16500.0, "status": "Pending"},
]

SEED_INVESTMENTS = [
    {"investment_id": "I01", "customer_id": "C01", "investment_type": "Mutual Fund", "amount": 100000.0, "start_date": "2025-01-15"},
    {"investment_id": "I02", "customer_id": "C02", "investment_type": "Fixed Deposit", "amount": 200000.0, "start_date": "2025-02-20"},
    {"investment_id": "I03", "customer_id": "C01", "investment_type": "Wealth Management", "amount": 300000.0, "start_date": "2025-06-10"},
    {"investment_id": "I04", "customer_id": "C03", "investment_type": "Recurring Deposit", "amount": 50000.0, "start_date": "2025-09-01"},
]

SEED_SERVICE_REQUESTS = [
    {"request_id": "SR01", "customer_id": "C02", "request_type": "Address Update", "description": "Update mailing address to Anna Nagar", "status": "Resolved", "request_date": "2026-01-20", "assigned_emp_id": "E05"},
    {"request_id": "SR02", "customer_id": "C03", "request_type": "Debit Card Replacement", "description": "Request for replacement chip debit card", "status": "Pending", "request_date": "2026-02-10", "assigned_emp_id": "E05"},
    {"request_id": "SR03", "customer_id": "C01", "request_type": "Cheque Book", "description": "Request new 50-leaf cheque book", "status": "Resolved", "request_date": "2026-02-15", "assigned_emp_id": "E05"},
]

# In-memory mutable collections
_BRANCHES = []
_EMPLOYEES = []
_CUSTOMERS = []
_ACCOUNTS = []
_TRANSACTIONS = []
_TRANSFERS = []
_LOANS = []
_INSTALLMENTS = []
_INVESTMENTS = []
_SERVICE_REQUESTS = []


def reset_mock_db() -> None:
    """
    Restores the in-memory mock database to the exact 47-node baseline dataset.
    Used for test suite isolation and reproducible test execution.
    """
    global _BRANCHES, _EMPLOYEES, _CUSTOMERS, _ACCOUNTS, _TRANSACTIONS
    global _TRANSFERS, _LOANS, _INSTALLMENTS, _INVESTMENTS, _SERVICE_REQUESTS

    _BRANCHES = copy.deepcopy(SEED_BRANCHES)
    _EMPLOYEES = copy.deepcopy(SEED_EMPLOYEES)
    _CUSTOMERS = copy.deepcopy(SEED_CUSTOMERS)
    _ACCOUNTS = copy.deepcopy(SEED_ACCOUNTS)
    _TRANSACTIONS = copy.deepcopy(SEED_TRANSACTIONS)
    _TRANSFERS = copy.deepcopy(SEED_TRANSFERS)
    _LOANS = copy.deepcopy(SEED_LOANS)
    _INSTALLMENTS = copy.deepcopy(SEED_INSTALLMENTS)
    _INVESTMENTS = copy.deepcopy(SEED_INVESTMENTS)
    _SERVICE_REQUESTS = copy.deepcopy(SEED_SERVICE_REQUESTS)


# Initialize immediately on module load
reset_mock_db()


# ==============================================================================
# Read Functions (1-9)
# ==============================================================================

def get_customer(customer_id: str) -> dict | None:
    """
    Fetch customer profile and assigned Relationship Manager.
    Returns dict or None if not found.
    """
    cust = next((c for c in _CUSTOMERS if c["customer_id"] == customer_id), None)
    if not cust:
        return None
    rm = next((e for e in _EMPLOYEES if e["emp_id"] == cust.get("rm_emp_id")), None)
    return {
        "customer_id": cust["customer_id"],
        "name": cust["name"],
        "customer_type": cust["customer_type"],
        "city": cust["city"],
        "phone": cust["phone"],
        "email": cust["email"],
        "relationship_manager": rm["name"] if rm else None,
    }


def get_accounts(customer_id: str) -> list[dict]:
    """
    Fetch all accounts held by a customer along with branch name.
    Returns list of account dicts sorted by account number.
    """
    results = []
    for acc in _ACCOUNTS:
        if acc["customer_id"] == customer_id:
            branch = next((b for b in _BRANCHES if b["branch_id"] == acc["branch_id"]), None)
            results.append({
                "account_number": acc["account_number"],
                "account_type": acc["account_type"],
                "balance": acc["balance"],
                "status": acc["status"],
                "branch_name": branch["branch_name"] if branch else "",
            })
    results.sort(key=lambda x: x["account_number"])
    return results


def get_total_balance(customer_id: str) -> float | int:
    """
    Calculate the sum of all account balances for a customer.
    Returns numeric total balance (or 0 if customer not found / has no accounts).
    """
    accounts = [a for a in _ACCOUNTS if a["customer_id"] == customer_id]
    if not accounts:
        return 0.0
    return sum(a["balance"] for a in accounts)


def get_transactions(account_number: str) -> list[dict]:
    """
    Fetch consolidated transaction history (Deposits, Withdrawals, In/Out Transfers)
    for an account sorted by txn_date descending.
    """
    rows = []
    # 1. Non-transfer transactions (Deposits & Withdrawals)
    for txn in _TRANSACTIONS:
        if txn["account_number"] == account_number:
            rows.append({
                "txn_id": txn["txn_id"],
                "txn_date": txn["txn_date"],
                "txn_type": txn["txn_type"],
                "amount": txn["amount"],
                "other_account": None,
            })
    # 2. Transfers Out
    for tr in _TRANSFERS:
        if tr["from_account"] == account_number:
            rows.append({
                "txn_id": tr["txn_id"],
                "txn_date": tr["txn_date"],
                "txn_type": "Transfer Out",
                "amount": tr["amount"],
                "other_account": tr["to_account"],
            })
    # 3. Transfers In
    for tr in _TRANSFERS:
        if tr["to_account"] == account_number:
            rows.append({
                "txn_id": tr["txn_id"],
                "txn_date": tr["txn_date"],
                "txn_type": "Transfer In",
                "amount": tr["amount"],
                "other_account": tr["from_account"],
            })

    rows.sort(key=lambda x: (str(x.get("txn_date") or ""), str(x.get("txn_id") or "")), reverse=True)
    return rows


def get_loans(customer_id: str) -> list[dict]:
    """
    Fetch all loans taken by a customer with loan officer name and branch name.
    Returns list of loan dicts.
    """
    results = []
    for l in _LOANS:
        if l["customer_id"] == customer_id:
            officer = next((e for e in _EMPLOYEES if e["emp_id"] == l.get("loan_officer_emp_id")), None)
            branch = next((b for b in _BRANCHES if b["branch_id"] == l.get("branch_id")), None)
            results.append({
                "loan_id": l["loan_id"],
                "loan_type": l["loan_type"],
                "amount": l["amount"],
                "interest_rate": l["interest_rate"],
                "term_months": l["term_months"],
                "status": l["status"],
                "loan_officer": officer["name"] if officer else None,
                "branch_name": branch["branch_name"] if branch else None,
            })
    results.sort(key=lambda x: x["loan_id"])
    return results


def get_repayment_schedule(loan_id: str) -> list[dict]:
    """
    Fetch installment schedule for a loan ordered by installment number.
    Returns list of installment dicts.
    """
    results = []
    for inst in _INSTALLMENTS:
        if inst["loan_id"] == loan_id:
            results.append({
                "installment_no": inst["installment_no"],
                "due_date": inst["due_date"],
                "amount_due": inst["amount_due"],
                "status": inst["status"],
            })
    results.sort(key=lambda x: x["installment_no"])
    return results


def get_investments(customer_id: str) -> list[dict]:
    """
    Fetch investment portfolio items for a customer.
    Returns list of investment dicts.
    """
    results = []
    for inv in _INVESTMENTS:
        if inv["customer_id"] == customer_id:
            results.append({
                "investment_id": inv["investment_id"],
                "investment_type": inv["investment_type"],
                "amount": inv["amount"],
                "start_date": inv["start_date"],
            })
    results.sort(key=lambda x: x["investment_id"])
    return results


def get_service_requests(customer_id: str) -> list[dict]:
    """
    Fetch customer service requests with handling employee name.
    Returns list of service request dicts.
    """
    results = []
    for sr in _SERVICE_REQUESTS:
        if sr["customer_id"] == customer_id:
            emp = next((e for e in _EMPLOYEES if e["emp_id"] == sr.get("assigned_emp_id")), None)
            results.append({
                "request_id": sr["request_id"],
                "request_type": sr["request_type"],
                "description": sr["description"],
                "status": sr["status"],
                "request_date": sr["request_date"],
                "handled_by": emp["name"] if emp else None,
            })
    results.sort(key=lambda x: (str(x.get("request_date") or ""), str(x.get("request_id") or "")), reverse=True)
    return results


def get_branches() -> list[dict]:
    """
    List all bank branches.
    Returns list of branch dicts with branch_id and branch_name.
    """
    results = [{"branch_id": b["branch_id"], "branch_name": b["branch_name"]} for b in _BRANCHES]
    results.sort(key=lambda x: x["branch_id"])
    return results


# ==============================================================================
# Manage Functions (10-14)
# ==============================================================================

def add_customer(
    customer_id: str,
    first_name: str,
    last_name: str,
    city: str,
    phone: str,
    email: str,
    customer_type: str,
) -> dict:
    """
    Create a new customer node. Fails if customer_id already exists.
    Returns {'success': bool, 'message': str}.
    """
    try:
        if any(c["customer_id"] == customer_id for c in _CUSTOMERS):
            return {"success": False, "message": f"Customer ID {customer_id} already exists"}
        full_name = f"{first_name} {last_name}".strip()
        _CUSTOMERS.append({
            "customer_id": customer_id,
            "first_name": first_name,
            "last_name": last_name,
            "name": full_name,
            "customer_type": customer_type,
            "city": city,
            "phone": phone,
            "email": email,
            "rm_emp_id": None,
        })
        return {"success": True, "message": f"Customer {customer_id} added successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def update_customer_contact(customer_id: str, phone: str, email: str) -> dict:
    """
    Update contact phone and email for an existing customer.
    Returns {'success': bool, 'message': str}.
    """
    try:
        cust = next((c for c in _CUSTOMERS if c["customer_id"] == customer_id), None)
        if not cust:
            return {"success": False, "message": f"Customer {customer_id} not found"}
        cust["phone"] = phone
        cust["email"] = email
        return {"success": True, "message": "Customer contact updated successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def open_account(
    account_number: str,
    customer_id: str,
    branch_id: str,
    account_type: str,
    opening_balance: float | int,
) -> dict:
    """
    Open a new account linked to a customer and branch.
    Fails if customer or branch does not exist, or account_number already exists.
    Returns {'success': bool, 'message': str}.
    """
    try:
        if opening_balance < 0:
            return {"success": False, "message": "Opening balance cannot be negative"}
        if any(a["account_number"] == account_number for a in _ACCOUNTS):
            return {"success": False, "message": f"Account {account_number} already exists"}
        if not any(c["customer_id"] == customer_id for c in _CUSTOMERS):
            return {"success": False, "message": f"Customer {customer_id} does not exist"}
        if not any(b["branch_id"] == branch_id for b in _BRANCHES):
            return {"success": False, "message": f"Branch {branch_id} does not exist"}

        _ACCOUNTS.append({
            "account_number": account_number,
            "customer_id": customer_id,
            "branch_id": branch_id,
            "account_type": account_type,
            "balance": float(opening_balance),
            "status": "Active",
        })
        return {"success": True, "message": "Account opened successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def close_account(account_number: str) -> dict:
    """
    Close and delete an account node ONLY if its balance is exactly 0.
    Fails if account does not exist or balance != 0.
    Returns {'success': bool, 'message': str}.
    """
    try:
        idx = next((i for i, a in enumerate(_ACCOUNTS) if a["account_number"] == account_number), None)
        if idx is None:
            return {"success": False, "message": f"Account {account_number} not found"}
        acc = _ACCOUNTS[idx]
        if acc["balance"] != 0:
            return {"success": False, "message": f"Cannot close account with non-zero balance ({acc['balance']})"}
        del _ACCOUNTS[idx]
        return {"success": True, "message": f"Account {account_number} closed successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def raise_service_request(customer_id: str, request_type: str, description: str) -> dict:
    """
    Create a new service request assigned to Customer Service Executive E05.
    Returns {'success': bool, 'message': str, 'request_id': str}.
    """
    try:
        if not any(c["customer_id"] == customer_id for c in _CUSTOMERS):
            return {"success": False, "message": f"Customer {customer_id} not found", "request_id": ""}
        req_id = new_id("SR")
        today = datetime.date.today().strftime("%Y-%m-%d")
        _SERVICE_REQUESTS.append({
            "request_id": req_id,
            "customer_id": customer_id,
            "request_type": request_type,
            "description": description,
            "status": "Pending",
            "request_date": today,
            "assigned_emp_id": "E05",
        })
        return {
            "success": True,
            "message": "Service request created successfully",
            "request_id": req_id,
        }
    except Exception as e:
        return {"success": False, "message": str(e), "request_id": ""}


# ==============================================================================
# Process Functions (15-16)
# ==============================================================================

def process_transaction(account_number: str, txn_type: str, amount: float | int) -> dict:
    """
    Process a Deposit or Withdrawal for an account and update balance.
    Withdrawal fails if balance is insufficient.
    Returns {'success': bool, 'message': str, 'new_balance': float | int}.
    """
    try:
        if amount <= 0:
            return {"success": False, "message": "Amount must be positive", "new_balance": 0.0}
        if txn_type not in ("Deposit", "Withdrawal"):
            return {"success": False, "message": f"Invalid transaction type: {txn_type}", "new_balance": 0.0}
        acc = next((a for a in _ACCOUNTS if a["account_number"] == account_number), None)
        if not acc:
            return {"success": False, "message": f"Account {account_number} not found", "new_balance": 0.0}

        if txn_type == "Withdrawal" and acc["balance"] < amount:
            return {"success": False, "message": "Insufficient balance", "new_balance": acc["balance"]}

        if txn_type == "Deposit":
            acc["balance"] += float(amount)
        else:
            acc["balance"] -= float(amount)

        txn_id = new_id("T")
        today = datetime.date.today().strftime("%Y-%m-%d")
        _TRANSACTIONS.append({
            "txn_id": txn_id,
            "account_number": account_number,
            "txn_type": txn_type,
            "amount": float(amount),
            "txn_date": today,
        })
        return {
            "success": True,
            "message": f"{txn_type} successful",
            "new_balance": acc["balance"],
        }
    except Exception as e:
        return {"success": False, "message": str(e), "new_balance": 0.0}


def transfer_money(from_account: str, to_account: str, amount: float | int) -> dict:
    """
    Atomically transfer funds between accounts and record TRANSFERRED_TO relationship.
    Fails if insufficient balance, invalid account, or same account.
    Returns {'success': bool, 'message': str}.
    """
    try:
        if from_account == to_account:
            return {"success": False, "message": "Cannot transfer to the same account"}
        if amount <= 0:
            return {"success": False, "message": "Transfer amount must be positive"}
        from_acc = next((a for a in _ACCOUNTS if a["account_number"] == from_account), None)
        if not from_acc:
            return {"success": False, "message": f"Source account {from_account} not found"}
        to_acc = next((a for a in _ACCOUNTS if a["account_number"] == to_account), None)
        if not to_acc:
            return {"success": False, "message": f"Destination account {to_account} not found"}
        if from_acc["balance"] < amount:
            return {"success": False, "message": "Insufficient balance"}

        from_acc["balance"] -= float(amount)
        to_acc["balance"] += float(amount)

        txn_id = new_id("TR")
        today = datetime.date.today().strftime("%Y-%m-%d")
        _TRANSFERS.append({
            "txn_id": txn_id,
            "from_account": from_account,
            "to_account": to_account,
            "amount": float(amount),
            "txn_date": today,
        })
        return {
            "success": True,
            "message": f"Transferred {amount} from {from_account} to {to_account} successfully",
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


# ==============================================================================
# Analytics Functions (17-20)
# ==============================================================================

def get_branch_account_counts() -> list[dict]:
    """
    Count total accounts located at each branch.
    Returns list of dicts with branch_name and account_count.
    """
    counts = {b["branch_name"]: 0 for b in _BRANCHES}
    for acc in _ACCOUNTS:
        branch = next((b for b in _BRANCHES if b["branch_id"] == acc["branch_id"]), None)
        if branch:
            counts[branch["branch_name"]] = counts.get(branch["branch_name"], 0) + 1
    result = [{"branch_name": k, "account_count": v} for k, v in counts.items()]
    result.sort(key=lambda x: (-x["account_count"], x["branch_name"]))
    return result


def get_top_customers_by_balance(limit: int = 5) -> list[dict]:
    """
    Leaderboard of top customers by aggregated account balance in descending order.
    Returns list of dicts with customer_id, name, and total_balance.
    """
    cust_totals = []
    for c in _CUSTOMERS:
        cid = c["customer_id"]
        total = sum(a["balance"] for a in _ACCOUNTS if a["customer_id"] == cid)
        cust_totals.append({
            "customer_id": cid,
            "name": c["name"],
            "total_balance": total,
        })
    cust_totals.sort(key=lambda x: (-x["total_balance"], x["customer_id"]))
    return cust_totals[:limit]


def get_large_transfers(min_amount: float | int) -> list[dict]:
    """
    Filter all transfers with amount >= min_amount, sorted by amount descending.
    Returns list of transfer dicts.
    """
    matched = [
        {
            "txn_id": tr["txn_id"],
            "from_account": tr["from_account"],
            "to_account": tr["to_account"],
            "amount": tr["amount"],
            "txn_date": tr["txn_date"],
        }
        for tr in _TRANSFERS
        if tr["amount"] >= min_amount
    ]
    matched.sort(key=lambda x: (x["amount"], x["txn_date"]), reverse=True)
    return matched


def get_money_trail(account_number: str) -> list[dict]:
    """
    Trace directed multi-hop transfer chains (1 to 3 hops) starting from account_number.
    Returns list of dicts with trail (list of account numbers) and hops (int).
    """
    results = []
    # Breadth-first exploration for 1..3 hops
    queue = []
    for tr in _TRANSFERS:
        if tr["from_account"] == account_number:
            queue.append(([tr["from_account"], tr["to_account"]], {tr["txn_id"]}, 1))

    while queue:
        trail, used_txns, hops = queue.pop(0)
        results.append({"trail": trail, "hops": hops})
        if hops < 3:
            curr = trail[-1]
            for next_tr in _TRANSFERS:
                if next_tr["from_account"] == curr and next_tr["txn_id"] not in used_txns:
                    queue.append((
                        trail + [next_tr["to_account"]],
                        used_txns | {next_tr["txn_id"]},
                        hops + 1,
                    ))

    results.sort(key=lambda x: (x["hops"], x["trail"]))
    return results
