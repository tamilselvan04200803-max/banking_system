"""
Live Neo4j Database Implementation for Smart Banking Mini-Project
Executes Cypher queries against Neo4j via connection.py helper utilities.
Matches all 20 database function signatures and return schemas with mock_db.py.
"""

import datetime
from connection import new_id, run_query


# ==============================================================================
# Read Functions (1-9)
# ==============================================================================

def get_customer(customer_id: str) -> dict | None:
    """
    Fetch customer profile and assigned Relationship Manager.
    Returns dict or None if not found.
    """
    try:
        query = """
        MATCH (c:Customer {customer_id: $customer_id})
        OPTIONAL MATCH (c)-[:ASSIGNED_TO]->(e:Employee)
        RETURN c.customer_id AS customer_id,
               c.name AS name,
               c.customer_type AS customer_type,
               c.city AS city,
               c.phone AS phone,
               c.email AS email,
               e.name AS relationship_manager
        """
        rows = run_query(query, {"customer_id": customer_id})
        if not rows:
            return None
        return rows[0]
    except Exception:
        return None


def get_accounts(customer_id: str) -> list[dict]:
    """
    Fetch all accounts held by a customer along with branch name.
    Returns list of account dicts sorted by account number.
    """
    try:
        query = """
        MATCH (c:Customer {customer_id: $customer_id})-[:HOLDS]->(a:Account)
        OPTIONAL MATCH (a)-[:LOCATED_AT]->(b:Branch)
        RETURN a.account_number AS account_number,
               a.account_type AS account_type,
               a.balance AS balance,
               a.status AS status,
               b.branch_name AS branch_name
        ORDER BY a.account_number ASC
        """
        return run_query(query, {"customer_id": customer_id})
    except Exception:
        return []


def get_total_balance(customer_id: str) -> float | int:
    """
    Calculate the sum of all account balances for a customer.
    Returns numeric total balance (or 0 if customer not found / has no accounts).
    """
    try:
        query = """
        MATCH (c:Customer {customer_id: $customer_id})-[:HOLDS]->(a:Account)
        RETURN coalesce(sum(a.balance), 0) AS total_balance
        """
        rows = run_query(query, {"customer_id": customer_id})
        if rows:
            return rows[0].get("total_balance", 0.0)
        return 0.0
    except Exception:
        return 0.0


def get_transactions(account_number: str) -> list[dict]:
    """
    Fetch consolidated transaction history (Deposits, Withdrawals, In/Out Transfers)
    for an account sorted by txn_date descending.
    """
    try:
        query = """
        MATCH (a:Account {account_number: $account_number})-[:HAS_TRANSACTION]->(t:Transaction)
        RETURN t.txn_id AS txn_id,
               toString(t.txn_date) AS txn_date,
               t.txn_type AS txn_type,
               t.amount AS amount,
               null AS other_account
        UNION ALL
        MATCH (a:Account {account_number: $account_number})-[r:TRANSFERRED_TO]->(target:Account)
        RETURN r.txn_id AS txn_id,
               toString(r.txn_date) AS txn_date,
               'Transfer Out' AS txn_type,
               r.amount AS amount,
               target.account_number AS other_account
        UNION ALL
        MATCH (source:Account)-[r:TRANSFERRED_TO]->(a:Account {account_number: $account_number})
        RETURN r.txn_id AS txn_id,
               toString(r.txn_date) AS txn_date,
               'Transfer In' AS txn_type,
               r.amount AS amount,
               source.account_number AS other_account
        """
        rows = run_query(query, {"account_number": account_number})
        rows.sort(key=lambda x: (str(x.get("txn_date") or ""), str(x.get("txn_id") or "")), reverse=True)
        return rows
    except Exception:
        return []


def get_loans(customer_id: str) -> list[dict]:
    """
    Fetch all loans taken by a customer with loan officer name and branch name.
    Returns list of loan dicts.
    """
    try:
        query = """
        MATCH (c:Customer {customer_id: $customer_id})-[:HAS_LOAN]->(l:Loan)
        OPTIONAL MATCH (l)-[:MANAGED_BY]->(e:Employee)
        OPTIONAL MATCH (l)-[:LOCATED_AT]->(b:Branch)
        RETURN l.loan_id AS loan_id,
               l.loan_type AS loan_type,
               l.amount AS amount,
               l.interest_rate AS interest_rate,
               l.term_months AS term_months,
               l.status AS status,
               e.name AS loan_officer,
               b.branch_name AS branch_name
        ORDER BY l.loan_id ASC
        """
        return run_query(query, {"customer_id": customer_id})
    except Exception:
        return []


def get_repayment_schedule(loan_id: str) -> list[dict]:
    """
    Fetch installment schedule for a loan ordered by installment number.
    Returns list of installment dicts.
    """
    try:
        query = """
        MATCH (l:Loan {loan_id: $loan_id})-[:HAS_INSTALLMENT]->(i:Installment)
        RETURN i.installment_no AS installment_no,
               toString(i.due_date) AS due_date,
               i.amount_due AS amount_due,
               i.status AS status
        ORDER BY i.installment_no ASC
        """
        return run_query(query, {"loan_id": loan_id})
    except Exception:
        return []


def get_investments(customer_id: str) -> list[dict]:
    """
    Fetch investment portfolio items for a customer.
    Returns list of investment dicts.
    """
    try:
        query = """
        MATCH (c:Customer {customer_id: $customer_id})-[:HAS_INVESTMENT]->(i:Investment)
        RETURN i.investment_id AS investment_id,
               i.investment_type AS investment_type,
               i.amount AS amount,
               toString(i.start_date) AS start_date
        ORDER BY i.investment_id ASC
        """
        return run_query(query, {"customer_id": customer_id})
    except Exception:
        return []


def get_service_requests(customer_id: str) -> list[dict]:
    """
    Fetch customer service requests with handling employee name.
    Returns list of service request dicts.
    """
    try:
        query = """
        MATCH (c:Customer {customer_id: $customer_id})-[:RAISED]->(sr:ServiceRequest)
        OPTIONAL MATCH (sr)-[:ASSIGNED_TO]->(e:Employee)
        RETURN sr.request_id AS request_id,
               sr.request_type AS request_type,
               sr.description AS description,
               sr.status AS status,
               toString(sr.request_date) AS request_date,
               e.name AS handled_by
        ORDER BY sr.request_date DESC, sr.request_id DESC
        """
        return run_query(query, {"customer_id": customer_id})
    except Exception:
        return []


def get_branches() -> list[dict]:
    """
    List all bank branches.
    Returns list of branch dicts with branch_id and branch_name.
    """
    try:
        query = """
        MATCH (b:Branch)
        RETURN b.branch_id AS branch_id, b.branch_name AS branch_name
        ORDER BY b.branch_id ASC
        """
        return run_query(query)
    except Exception:
        return []


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
        check = run_query(
            "MATCH (c:Customer {customer_id: $customer_id}) RETURN c.customer_id AS id",
            {"customer_id": customer_id},
        )
        if check:
            return {"success": False, "message": f"Customer ID {customer_id} already exists"}

        full_name = f"{first_name} {last_name}".strip()
        query = """
        CREATE (c:Customer {
            customer_id: $customer_id,
            first_name: $first_name,
            last_name: $last_name,
            name: $name,
            city: $city,
            phone: $phone,
            email: $email,
            customer_type: $customer_type
        })
        """
        run_query(
            query,
            {
                "customer_id": customer_id,
                "first_name": first_name,
                "last_name": last_name,
                "name": full_name,
                "city": city,
                "phone": phone,
                "email": email,
                "customer_type": customer_type,
            },
        )
        return {"success": True, "message": f"Customer {customer_id} added successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def update_customer_contact(customer_id: str, phone: str, email: str) -> dict:
    """
    Update contact phone and email for an existing customer.
    Returns {'success': bool, 'message': str}.
    """
    try:
        query = """
        MATCH (c:Customer {customer_id: $customer_id})
        SET c.phone = $phone, c.email = $email
        RETURN c.customer_id AS customer_id
        """
        rows = run_query(query, {"customer_id": customer_id, "phone": phone, "email": email})
        if not rows:
            return {"success": False, "message": f"Customer {customer_id} not found"}
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

        ac_check = run_query(
            "MATCH (a:Account {account_number: $account_number}) RETURN a.account_number AS id",
            {"account_number": account_number},
        )
        if ac_check:
            return {"success": False, "message": f"Account {account_number} already exists"}

        c_check = run_query(
            "MATCH (c:Customer {customer_id: $customer_id}) RETURN c.customer_id AS id",
            {"customer_id": customer_id},
        )
        if not c_check:
            return {"success": False, "message": f"Customer {customer_id} does not exist"}

        b_check = run_query(
            "MATCH (b:Branch {branch_id: $branch_id}) RETURN b.branch_id AS id",
            {"branch_id": branch_id},
        )
        if not b_check:
            return {"success": False, "message": f"Branch {branch_id} does not exist"}

        create_query = """
        MATCH (c:Customer {customer_id: $customer_id})
        MATCH (b:Branch {branch_id: $branch_id})
        CREATE (a:Account {
            account_number: $account_number,
            account_type: $account_type,
            balance: $opening_balance,
            status: 'Active'
        })
        CREATE (c)-[:HOLDS]->(a)
        CREATE (c)-[:OWNS]->(a)
        CREATE (a)-[:LOCATED_AT]->(b)
        CREATE (a)-[:HELD_AT]->(b)
        """
        run_query(
            create_query,
            {
                "account_number": account_number,
                "customer_id": customer_id,
                "branch_id": branch_id,
                "account_type": account_type,
                "opening_balance": float(opening_balance),
            },
        )
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
        rows = run_query(
            "MATCH (a:Account {account_number: $account_number}) RETURN a.balance AS balance",
            {"account_number": account_number},
        )
        if not rows:
            return {"success": False, "message": f"Account {account_number} not found"}

        balance = rows[0].get("balance", 0.0)
        if balance != 0:
            return {"success": False, "message": f"Cannot close account with non-zero balance ({balance})"}

        run_query(
            "MATCH (a:Account {account_number: $account_number}) DETACH DELETE a",
            {"account_number": account_number},
        )
        return {"success": True, "message": f"Account {account_number} closed successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def raise_service_request(customer_id: str, request_type: str, description: str) -> dict:
    """
    Create a new service request assigned to Customer Service Executive E05.
    Returns {'success': bool, 'message': str, 'request_id': str}.
    """
    try:
        c_check = run_query(
            "MATCH (c:Customer {customer_id: $customer_id}) RETURN c.customer_id AS id",
            {"customer_id": customer_id},
        )
        if not c_check:
            return {"success": False, "message": f"Customer {customer_id} not found", "request_id": ""}

        req_id = new_id("SR")
        today = datetime.date.today().strftime("%Y-%m-%d")
        query = """
        MATCH (c:Customer {customer_id: $customer_id})
        MATCH (e:Employee {emp_id: 'E05'})
        CREATE (sr:ServiceRequest {
            request_id: $request_id,
            request_type: $request_type,
            description: $description,
            status: 'Pending',
            request_date: $today
        })
        CREATE (c)-[:RAISED]->(sr)
        CREATE (sr)-[:ASSIGNED_TO]->(e)
        RETURN sr.request_id AS request_id
        """
        run_query(
            query,
            {
                "customer_id": customer_id,
                "request_id": req_id,
                "request_type": request_type,
                "description": description,
                "today": today,
            },
        )
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

        ac_rows = run_query(
            "MATCH (a:Account {account_number: $account_number}) RETURN a.balance AS balance",
            {"account_number": account_number},
        )
        if not ac_rows:
            return {"success": False, "message": f"Account {account_number} not found", "new_balance": 0.0}

        current_balance = ac_rows[0].get("balance", 0.0)
        if txn_type == "Withdrawal" and current_balance < amount:
            return {"success": False, "message": "Insufficient balance", "new_balance": current_balance}

        txn_id = new_id("T")
        today = datetime.date.today().strftime("%Y-%m-%d")

        if txn_type == "Deposit":
            res = run_query(
                """
                MATCH (a:Account {account_number: $account_number})
                SET a.balance = a.balance + $amount
                CREATE (t:Transaction {
                    txn_id: $txn_id,
                    txn_type: 'Deposit',
                    amount: $amount,
                    txn_date: $today
                })
                CREATE (a)-[:HAS_TRANSACTION]->(t)
                CREATE (t)-[:PERFORMED_ON]->(a)
                RETURN a.balance AS new_balance
                """,
                {"account_number": account_number, "amount": float(amount), "txn_id": txn_id, "today": today},
            )
        else:
            res = run_query(
                """
                MATCH (a:Account {account_number: $account_number})
                SET a.balance = a.balance - $amount
                CREATE (t:Transaction {
                    txn_id: $txn_id,
                    txn_type: 'Withdrawal',
                    amount: $amount,
                    txn_date: $today
                })
                CREATE (a)-[:HAS_TRANSACTION]->(t)
                CREATE (t)-[:PERFORMED_ON]->(a)
                RETURN a.balance AS new_balance
                """,
                {"account_number": account_number, "amount": float(amount), "txn_id": txn_id, "today": today},
            )

        new_bal = res[0].get("new_balance", current_balance) if res else current_balance
        return {
            "success": True,
            "message": f"{txn_type} successful",
            "new_balance": new_bal,
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

        txn_id = new_id("TR")
        today = datetime.date.today().strftime("%Y-%m-%d")

        # Single atomic Cypher query updating balances and creating TRANSFERRED_TO relationship
        query = """
        MATCH (from:Account {account_number: $from_account})
        MATCH (to:Account {account_number: $to_account})
        WHERE from.account_number <> to.account_number AND from.balance >= $amount AND $amount > 0
        SET from.balance = from.balance - $amount,
            to.balance = to.balance + $amount
        CREATE (from)-[r:TRANSFERRED_TO {
            txn_id: $txn_id,
            amount: $amount,
            txn_date: $today
        }]->(to)
        RETURN from.balance AS from_balance, to.balance AS to_balance
        """
        rows = run_query(
            query,
            {
                "from_account": from_account,
                "to_account": to_account,
                "amount": float(amount),
                "txn_id": txn_id,
                "today": today,
            },
        )
        if rows:
            return {
                "success": True,
                "message": f"Transferred {amount} from {from_account} to {to_account} successfully",
            }

        # If atomic query returned 0 rows, diagnose cause for accurate failure message
        from_rows = run_query(
            "MATCH (a:Account {account_number: $acc}) RETURN a.balance AS balance",
            {"acc": from_account},
        )
        if not from_rows:
            return {"success": False, "message": f"Source account {from_account} not found"}

        to_rows = run_query(
            "MATCH (a:Account {account_number: $acc}) RETURN a.account_number",
            {"acc": to_account},
        )
        if not to_rows:
            return {"success": False, "message": f"Destination account {to_account} not found"}

        if from_rows[0].get("balance", 0.0) < amount:
            return {"success": False, "message": "Insufficient balance"}

        return {"success": False, "message": "Transfer failed"}
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
    try:
        query = """
        MATCH (b:Branch)
        OPTIONAL MATCH (a:Account)-[:LOCATED_AT]->(b)
        RETURN b.branch_name AS branch_name, count(a) AS account_count
        ORDER BY account_count DESC, b.branch_name ASC
        """
        return run_query(query)
    except Exception:
        return []


def get_top_customers_by_balance(limit: int = 5) -> list[dict]:
    """
    Leaderboard of top customers by aggregated account balance in descending order.
    Returns list of dicts with customer_id, name, and total_balance.
    """
    try:
        query = """
        MATCH (c:Customer)-[:HOLDS]->(a:Account)
        WITH c, sum(a.balance) AS total_balance
        RETURN c.customer_id AS customer_id,
               c.name AS name,
               total_balance
        ORDER BY total_balance DESC, c.customer_id ASC
        LIMIT $limit
        """
        return run_query(query, {"limit": limit})
    except Exception:
        return []


def get_large_transfers(min_amount: float | int) -> list[dict]:
    """
    Filter all transfers with amount >= min_amount, sorted by amount descending.
    Returns list of transfer dicts.
    """
    try:
        query = """
        MATCH (from:Account)-[r:TRANSFERRED_TO]->(to:Account)
        WHERE r.amount >= $min_amount
        RETURN r.txn_id AS txn_id,
               from.account_number AS from_account,
               to.account_number AS to_account,
               r.amount AS amount,
               toString(r.txn_date) AS txn_date
        ORDER BY r.amount DESC, txn_date DESC
        """
        return run_query(query, {"min_amount": float(min_amount)})
    except Exception:
        return []


def get_money_trail(account_number: str) -> list[dict]:
    """
    Trace directed multi-hop transfer chains (1 to 3 hops) starting from account_number.
    Returns list of dicts with trail (list of account numbers) and hops (int).
    """
    try:
        query = """
        MATCH p = (a:Account {account_number: $account_number})-[:TRANSFERRED_TO*1..3]->(target:Account)
        RETURN [n IN nodes(p) | n.account_number] AS trail,
               length(p) AS hops
        ORDER BY hops ASC, trail ASC
        """
        return run_query(query, {"account_number": account_number})
    except Exception:
        return []
