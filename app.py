"""
Smart Banking Portal - Streamlit Web Application
Milestone 3 Implementation

Supports:
- Dual Backend Toggle: Live Neo4j vs Offline Mock Database with auto-detection probe.
- Global Customer Context Selector with persistent state.
- 4 Production-Grade Financial Screens covering all 20 Database Function Contracts.
- Graph-native fund flow tracing, repayment scheduling, and real-time ledger updates.
"""

import streamlit as st
import pandas as pd
import socket

# Import both backend implementations
import mock_db
import db


# ==============================================================================
# Page Configuration & Custom Styling
# ==============================================================================

st.set_page_config(
    page_title="Smart Banking Portal | Neo4j Graph Core",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
/* Banking Portal Global Theme */
.main-header {
    font-size: 2.1rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
}
.sub-header {
    font-size: 1.05rem;
    color: #94a3b8;
    margin-bottom: 1.5rem;
}
.portal-card {
    background-color: rgba(148, 163, 184, 0.08);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 10px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.metric-container {
    background: rgba(148, 163, 184, 0.08);
    border-left: 4px solid #2563eb;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
}
.badge-premium {
    background-color: #fef3c7;
    color: #92400e;
    font-weight: 600;
    padding: 0.2rem 0.6rem;
    border-radius: 9999px;
    font-size: 0.8rem;
    border: 1px solid #fde68a;
    display: inline-block;
}
.badge-standard {
    background-color: #e0f2fe;
    color: #0369a1;
    font-weight: 600;
    padding: 0.2rem 0.6rem;
    border-radius: 9999px;
    font-size: 0.8rem;
    border: 1px solid #bae6fd;
    display: inline-block;
}
.badge-status-resolved, .badge-status-paid {
    background-color: #dcfce7;
    color: #166534;
    font-weight: 600;
    padding: 0.15rem 0.5rem;
    border-radius: 9999px;
    font-size: 0.8rem;
}
.badge-status-pending {
    background-color: #fef9c3;
    color: #854d0e;
    font-weight: 600;
    padding: 0.15rem 0.5rem;
    border-radius: 9999px;
    font-size: 0.8rem;
}
.badge-status-overdue {
    background-color: #fee2e2;
    color: #991b1b;
    font-weight: 600;
    padding: 0.15rem 0.5rem;
    border-radius: 9999px;
    font-size: 0.8rem;
}
.hop-node {
    display: inline-block;
    background-color: #1e293b;
    color: #ffffff;
    font-weight: 600;
    font-family: monospace;
    padding: 0.35rem 0.75rem;
    border-radius: 6px;
    margin: 0.2rem;
}
.hop-arrow {
    display: inline-block;
    color: #3b82f6;
    font-weight: 700;
    font-size: 1.1rem;
    margin: 0 0.3rem;
}
.hop-pill {
    display: inline-block;
    background-color: rgba(148, 163, 184, 0.2);
    color: #94a3b8;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.2rem 0.5rem;
    border-radius: 9999px;
    margin-left: 0.6rem;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==============================================================================
# Helper Formatting Utilities
# ==============================================================================

def format_inr(amount: float | int | None) -> str:
    """Formats numeric value to Indian Rupee currency representation."""
    if amount is None:
        return "₹0.00"
    try:
        val = float(amount)
        return f"₹{val:,.2f}"
    except (ValueError, TypeError):
        return f"₹{amount}"


def probe_live_neo4j() -> bool:
    """Probes whether Neo4j port 7687 is listening with a fast 200ms timeout."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.2)
            if s.connect_ex(('127.0.0.1', 7687)) == 0:
                branches = db.get_branches()
                return isinstance(branches, list) and len(branches) > 0
        return False
    except Exception:
        return False


def render_dataframe(df: pd.DataFrame) -> None:
    """Render a DataFrame stretching to container width cleanly across Streamlit versions."""
    try:
        st.dataframe(df, width="stretch", hide_index=True)
    except TypeError:
        st.dataframe(df, use_container_width=True, hide_index=True)


# ==============================================================================
# Session State Initialization & Sidebar Mode Switcher
# ==============================================================================

# 1. Probe & Initialize Backend Mode
if "backend_mode" not in st.session_state:
    is_live_avail = probe_live_neo4j()
    st.session_state["backend_mode"] = "Live Neo4j" if is_live_avail else "Offline Mock"

# 2. Customer ID pool initialization
if "customer_ids" not in st.session_state:
    st.session_state["customer_ids"] = ["C01", "C02", "C03", "C04", "C05", "C06"]

if "selected_customer_id" not in st.session_state:
    st.session_state["selected_customer_id"] = "C01"


# --- Sidebar Branding ---
st.sidebar.markdown("## 🏦 Smart Banking")
st.sidebar.markdown(
    "<small style='color: #64748b;'>Graph-Native Retail & Corporate Portal</small>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

# --- Backend Mode Switcher ---
st.sidebar.markdown("### ⚙️ Database Engine")
selected_mode = st.sidebar.radio(
    "Active Data Backend",
    options=["Offline Mock", "Live Neo4j"] if not probe_live_neo4j() else ["Live Neo4j", "Offline Mock"],
    key="backend_mode",
    help="Switch between live Neo4j database or the deterministic in-memory offline mock dataset.",
)

# Determine active backend module
if selected_mode == "Live Neo4j":
    if probe_live_neo4j():
        backend = db
        st.sidebar.success("🟢 Neo4j Database: Connected")
    else:
        # Fallback to mock_db so fields and queries are never blank
        backend = mock_db
        st.sidebar.warning("🟡 Live Neo4j: Offline (Port 7687)")
        st.sidebar.caption("No Neo4j server detected on port 7687. Safe fallback to Mock DB is active so all 4 screens work!")
        if st.sidebar.button("👉 Switch to Offline Mock (Clean Status)", use_container_width=True):
            st.session_state["backend_mode"] = "Offline Mock"
            st.rerun()
else:
    backend = mock_db
    st.sidebar.success("🟢 Offline Mock Database: Active")
    st.sidebar.caption("47 nodes & 20 banking functions loaded in-memory.")
    if st.sidebar.button("🔄 Reset Mock DB State", use_container_width=True):
        mock_db.reset_mock_db()
        st.sidebar.success("Mock DB restored to baseline 47 nodes!")
        st.rerun()

st.sidebar.markdown("---")

# --- Global Customer Selector ---
st.sidebar.markdown("### 👤 Customer Context")

def get_customer_label(cid: str) -> str:
    try:
        c = backend.get_customer(cid)
        if c and c.get("name"):
            return f"{cid} - {c['name']} ({c.get('customer_type', 'Standard')})"
    except Exception:
        pass
    return cid

# Synchronize customer selection state (supports staged programmatic updates)
if "pending_customer_id" in st.session_state:
    st.session_state["customer_selector"] = st.session_state.pop("pending_customer_id")
elif "customer_selector" not in st.session_state:
    st.session_state["customer_selector"] = st.session_state.get("selected_customer_id", st.session_state["customer_ids"][0])

if st.session_state["customer_selector"] not in st.session_state["customer_ids"]:
    st.session_state["customer_selector"] = st.session_state["customer_ids"][0]

active_cid = st.sidebar.selectbox(
    "Active Customer",
    options=st.session_state["customer_ids"],
    key="customer_selector",
    format_func=get_customer_label,
    help="Select the active customer to inspect accounts, transactions, loans, and profile.",
)
st.session_state["selected_customer_id"] = active_cid

st.sidebar.markdown("---")

# --- Navigation Menu ---
SCREEN_CUSTOMER = "1. Customer Profile & Services"
SCREEN_ACCOUNTS = "2. Accounts & Transactions"
SCREEN_LOANS = "3. Loans & Investments"
SCREEN_ANALYTICS = "4. Analytics & Graph Intelligence"

screen = st.sidebar.radio(
    "Navigation",
    options=[SCREEN_CUSTOMER, SCREEN_ACCOUNTS, SCREEN_LOANS, SCREEN_ANALYTICS],
    key="navigation_screen",
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "⚡ Built with Streamlit & Neo4j Cypher Graph Engine.<br>"
    "Complies with all 20 Database API Contracts.",
    unsafe_allow_html=True,
)


# ==============================================================================
# Screen 1: Customer Profile & Services
# ==============================================================================

if screen == SCREEN_CUSTOMER:
    st.markdown("<div class='main-header'>Customer Profile & Relationship Management</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>View KYC profile, manage contact records, raise service requests, and register new customers.</div>", unsafe_allow_html=True)

    cust = backend.get_customer(active_cid)
    total_balance = backend.get_total_balance(active_cid)

    if not cust:
        st.warning(f"Customer `{active_cid}` was not found in the active database.")
    else:
        # Profile Top Banner
        c_type = cust.get("customer_type", "Standard")
        badge_class = "badge-premium" if c_type == "Premium" else "badge-standard"

        col_p1, col_p2 = st.columns([3, 1])
        with col_p1:
            st.markdown(
                f"""
                <div class='portal-card'>
                    <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;'>
                        <h2 style='margin: 0;'>{cust.get('name', 'N/A')}</h2>
                        <span class='{badge_class}'>{c_type} Client</span>
                    </div>
                    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.75rem; margin-top: 1rem;'>
                        <div><strong style='opacity: 0.7;'>Customer ID:</strong> <code style='font-size: 0.95rem;'>{cust.get('customer_id')}</code></div>
                        <div><strong style='opacity: 0.7;'>City:</strong> <span>{cust.get('city', 'N/A')}</span></div>
                        <div><strong style='opacity: 0.7;'>Phone:</strong> <span>{cust.get('phone', 'N/A')}</span></div>
                        <div><strong style='opacity: 0.7;'>Email:</strong> <span>{cust.get('email', 'N/A')}</span></div>
                        <div><strong style='opacity: 0.7;'>Relationship Manager:</strong> <span style='color: #38bdf8; font-weight: 600;'>{cust.get('relationship_manager') or 'None Assigned'}</span></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_p2:
            st.metric(
                label="Aggregated Account Balance",
                value=format_inr(total_balance),
                help="Sum of balances across all accounts owned by this customer.",
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Two-Column Operations: Contact Update & Service Requests
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("### ✏️ Contact Details Update")
            with st.form("contact_update_form"):
                st.caption(f"Update contact information for {cust.get('name')}.")
                new_phone = st.text_input("Mobile Phone Number", value=cust.get("phone", ""))
                new_email = st.text_input("Email Address", value=cust.get("email", ""))
                submit_contact = st.form_submit_button("Update Contact", use_container_width=True)

                if submit_contact:
                    if not new_phone.strip() or not new_email.strip():
                        st.error("Phone and Email cannot be empty.")
                    else:
                        res = backend.update_customer_contact(active_cid, new_phone.strip(), new_email.strip())
                        if res.get("success"):
                            st.success(res.get("message", "Contact updated successfully!"))
                            st.rerun()
                        else:
                            st.error(res.get("message", "Failed to update contact."))

            # Register New Customer Section
            with st.expander("➕ Register New Customer", expanded=False):
                with st.form("add_customer_form"):
                    st.caption("Enroll a new retail or corporate customer into the banking graph.")
                    new_cid = st.text_input("Customer ID (e.g. C07)", value="").strip()
                    c_col1, c_col2 = st.columns(2)
                    with c_col1:
                        first_name = st.text_input("First Name").strip()
                        city = st.text_input("City", value="Chennai").strip()
                        phone = st.text_input("Phone Number").strip()
                    with c_col2:
                        last_name = st.text_input("Last Name").strip()
                        cust_type = st.selectbox("Customer Classification", ["Standard", "Premium"])
                        email = st.text_input("Email Address").strip()

                    submit_new_cust = st.form_submit_button("Register Customer", use_container_width=True)

                    if submit_new_cust:
                        if not new_cid or not first_name or not last_name or not email:
                            st.error("Customer ID, First Name, Last Name, and Email are mandatory.")
                        else:
                            res = backend.add_customer(
                                customer_id=new_cid,
                                first_name=first_name,
                                last_name=last_name,
                                city=city,
                                phone=phone,
                                email=email,
                                customer_type=cust_type,
                            )
                            if res.get("success"):
                                if new_cid not in st.session_state["customer_ids"]:
                                    st.session_state["customer_ids"].append(new_cid)
                                st.session_state["pending_customer_id"] = new_cid
                                st.session_state["selected_customer_id"] = new_cid
                                st.success(res.get("message", "Customer registered successfully!"))
                                st.rerun()
                            else:
                                st.error(res.get("message", "Failed to register customer."))

        with col_right:
            st.markdown("### 📋 Service Requests")
            service_requests = backend.get_service_requests(active_cid)

            if service_requests:
                sr_data = []
                for sr in service_requests:
                    status = sr.get("status", "Pending")
                    status_badge = f"🟢 {status}" if status == "Resolved" else f"🟡 {status}"
                    sr_data.append({
                        "Request ID": sr.get("request_id"),
                        "Type": sr.get("request_type"),
                        "Description": sr.get("description"),
                        "Status": status_badge,
                        "Date": sr.get("request_date"),
                        "Handled By": sr.get("handled_by") or "CSE E05",
                    })
                render_dataframe(pd.DataFrame(sr_data))
            else:
                st.info(f"No service requests on record for customer {active_cid}.")

            # Raise New Service Request
            with st.expander("📝 Raise New Service Request", expanded=False):
                with st.form("raise_sr_form"):
                    st.caption("Submit a support or banking instrument request.")
                    sr_type = st.selectbox(
                        "Request Category",
                        [
                            "Cheque Book",
                            "Debit Card Replacement",
                            "Address Update",
                            "Account Statement",
                            "Internet Banking Reset",
                            "Loan Restructuring",
                            "General Inquiry",
                        ],
                    )
                    sr_desc = st.text_area("Request Description", placeholder="Enter specific details...")
                    submit_sr = st.form_submit_button("Submit Service Request", use_container_width=True)

                    if submit_sr:
                        if not sr_desc.strip():
                            st.error("Please provide a description for the request.")
                        else:
                            res = backend.raise_service_request(active_cid, sr_type, sr_desc.strip())
                            if res.get("success"):
                                st.success(f"{res.get('message')} (Request ID: {res.get('request_id')})")
                                st.rerun()
                            else:
                                st.error(res.get("message", "Failed to submit request."))


# ==============================================================================
# Screen 2: Accounts & Transactions
# ==============================================================================

elif screen == SCREEN_ACCOUNTS:
    st.markdown("<div class='main-header'>Accounts & Transactions Processing</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Manage checking and savings accounts, process deposits/withdrawals, execute transfers, and manage account lifecycles.</div>", unsafe_allow_html=True)

    accounts = backend.get_accounts(active_cid)

    if not accounts:
        st.warning(f"Customer `{active_cid}` does not own any accounts currently.")
    else:
        # Accounts Card Overview
        st.markdown(f"#### 💳 Accounts Held by {get_customer_label(active_cid)}")
        acc_cols = st.columns(len(accounts))
        for idx, acc in enumerate(accounts):
            with acc_cols[idx]:
                status_color = "green" if acc.get("status") == "Active" else "gray"
                st.metric(
                    label=f"{acc['account_number']} • {acc['account_type']}",
                    value=format_inr(acc["balance"]),
                    delta=f"{acc['status']} @ {acc.get('branch_name', '')}",
                    delta_color="normal" if acc.get("status") == "Active" else "off",
                )

        st.markdown("---")

        # Active Account Picker
        acc_numbers = [a["account_number"] for a in accounts]
        acc_state_key = f"active_account_{active_cid}"
        if acc_state_key not in st.session_state or st.session_state[acc_state_key] not in acc_numbers:
            st.session_state[acc_state_key] = acc_numbers[0]

        col_pick, col_bal = st.columns([3, 1])
        with col_pick:
            selected_acc_num = st.selectbox(
                "Select Active Account for Operations & Ledger Inspection",
                options=acc_numbers,
                key=acc_state_key,
                format_func=lambda acc_no: next(
                    (f"{a['account_number']} — {a['account_type']} (Balance: {format_inr(a['balance'])}) [{a['branch_name']}]"
                     for a in accounts if a["account_number"] == acc_no),
                    acc_no,
                ),
            )
        active_account_data = next((a for a in accounts if a["account_number"] == selected_acc_num), accounts[0])
        with col_bal:
            st.metric(
                label=f"Balance: {selected_acc_num}",
                value=format_inr(active_account_data["balance"]),
            )

        # Transaction History
        st.markdown(f"### 📜 Consolidated Transaction History ({selected_acc_num})")
        txns = backend.get_transactions(selected_acc_num)

        if txns:
            txn_rows = []
            for t in txns:
                t_type = t.get("txn_type", "")
                if t_type == "Deposit":
                    type_display = "🟢 Deposit"
                elif t_type == "Withdrawal":
                    type_display = "🔴 Withdrawal"
                elif t_type == "Transfer In":
                    type_display = "📥 Transfer In"
                elif t_type == "Transfer Out":
                    type_display = "📤 Transfer Out"
                else:
                    type_display = t_type

                txn_rows.append({
                    "Txn ID": t.get("txn_id"),
                    "Date": t.get("txn_date"),
                    "Type": type_display,
                    "Amount": format_inr(t.get("amount")),
                    "Counterparty Account": t.get("other_account") or "—",
                })
            render_dataframe(pd.DataFrame(txn_rows))
        else:
            st.info(f"No transactions recorded for account {selected_acc_num}.")

        st.markdown("---")

        # Two-Column Operations: Cash Transactions & Fund Transfers
        op_col1, op_col2 = st.columns(2)

        with op_col1:
            st.markdown("### 💵 Deposit / Withdrawal")
            with st.form("cash_transaction_form"):
                st.caption(f"Perform cash deposit or withdrawal on {selected_acc_num}.")
                txn_type = st.radio("Transaction Type", ["Deposit", "Withdrawal"], horizontal=True)
                amount = st.number_input(
                    "Amount (₹)",
                    min_value=1.0,
                    value=5000.0,
                    step=500.0,
                    format="%.2f",
                )
                submit_txn = st.form_submit_button("Process Transaction", use_container_width=True)

                if submit_txn:
                    res = backend.process_transaction(selected_acc_num, txn_type, amount)
                    if res.get("success"):
                        st.success(f"{res.get('message')} • New Balance: {format_inr(res.get('new_balance'))}")
                        st.rerun()
                    else:
                        st.error(res.get("message", "Transaction failed."))

        with op_col2:
            st.markdown("### 🔄 Inter-Account Fund Transfer")
            with st.form("transfer_funds_form"):
                st.caption(f"Execute atomic fund transfer from {selected_acc_num}.")
                to_account_input = st.text_input("Destination Account Number (e.g. AC1003)", value="").strip()
                transfer_amount = st.number_input(
                    "Transfer Amount (₹)",
                    min_value=1.0,
                    value=2000.0,
                    step=500.0,
                    format="%.2f",
                )
                submit_transfer = st.form_submit_button("Transfer Funds", use_container_width=True)

                if submit_transfer:
                    if not to_account_input:
                        st.error("Please enter a destination account number.")
                    elif to_account_input == selected_acc_num:
                        st.error("Source and destination accounts must be distinct.")
                    else:
                        res = backend.transfer_money(selected_acc_num, to_account_input, transfer_amount)
                        if res.get("success"):
                            st.success(res.get("message", "Transfer executed successfully!"))
                            st.rerun()
                        else:
                            st.error(res.get("message", "Transfer failed."))

    st.markdown("<br>", unsafe_allow_html=True)

    # Account Lifecycle Operations (Open & Close)
    st.markdown("### ⚙️ Account Lifecycle Management")
    mgt_col1, mgt_col2 = st.columns(2)

    with mgt_col1:
        with st.expander("➕ Open New Account", expanded=False):
            branches = backend.get_branches()
            branch_options = [b["branch_id"] for b in branches]
            branch_labels = {b["branch_id"]: f"{b['branch_id']} - {b['branch_name']}" for b in branches}

            with st.form("open_account_form"):
                st.caption(f"Create a new deposit account for customer {active_cid}.")
                new_acc_no = st.text_input("New Account Number (e.g. AC1009)").strip()
                selected_branch = st.selectbox(
                    "Branch Location",
                    options=branch_options,
                    format_func=lambda bid: branch_labels.get(bid, bid),
                )
                acc_type = st.selectbox("Account Classification", ["Savings", "Current"])
                opening_bal = st.number_input(
                    "Initial Opening Balance (₹)",
                    min_value=0.0,
                    value=0.0,
                    step=1000.0,
                    format="%.2f",
                )
                submit_open = st.form_submit_button("Open Account", use_container_width=True)

                if submit_open:
                    if not new_acc_no:
                        st.error("Account Number is required.")
                    else:
                        res = backend.open_account(
                            account_number=new_acc_no,
                            customer_id=active_cid,
                            branch_id=selected_branch,
                            account_type=acc_type,
                            opening_balance=opening_bal,
                        )
                        if res.get("success"):
                            st.success(res.get("message", "Account opened successfully!"))
                            st.rerun()
                        else:
                            st.error(res.get("message", "Failed to open account."))

    with mgt_col2:
        with st.expander("⚠️ Close Account (Zero-Balance Strict Rule)", expanded=False):
            st.caption("Under banking policy, accounts can **ONLY** be closed if their balance is exactly ₹0.00.")
            if accounts:
                close_target = st.selectbox(
                    "Select Account to Terminate",
                    options=acc_numbers,
                    key="close_acc_selector",
                )
                target_acc_info = next((a for a in accounts if a["account_number"] == close_target), None)
                if target_acc_info:
                    current_b = target_acc_info.get("balance", 0.0)
                    if current_b == 0:
                        st.success(f"Account {close_target} has ₹0.00 balance and is eligible for closure.")
                    else:
                        st.warning(f"Account {close_target} has balance of {format_inr(current_b)}. You must withdraw or transfer funds to zero out balance first.")

                if st.button("Confirm Account Deletion", type="secondary", use_container_width=True):
                    res = backend.close_account(close_target)
                    if res.get("success"):
                        st.success(res.get("message", f"Account {close_target} deleted."))
                        st.rerun()
                    else:
                        st.error(res.get("message", "Cannot close account."))
            else:
                st.info("No accounts available to close.")


# ==============================================================================
# Screen 3: Loans & Investments
# ==============================================================================

elif screen == SCREEN_LOANS:
    st.markdown("<div class='main-header'>Loans & Investment Portfolios</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Inspect credit facilities, installment repayment schedules, and wealth management investments.</div>", unsafe_allow_html=True)

    loans = backend.get_loans(active_cid)

    # 1. Loans Section
    st.markdown("### 🏦 Credit & Loan Facilities")
    if loans:
        loan_cards = st.columns(len(loans))
        for idx, l in enumerate(loans):
            with loan_cards[idx]:
                st.markdown(
                    f"""
                    <div class='portal-card'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <strong>Loan #{l['loan_id']}</strong>
                            <span class='badge-status-paid'>{l.get('status', 'Active')}</span>
                        </div>
                        <h3 style='margin: 0.25rem 0;'>{format_inr(l['amount'])}</h3>
                        <p style='opacity: 0.75; margin: 0;'>{l.get('loan_type')}</p>
                        <hr style='margin: 0.5rem 0; opacity: 0.2;'>
                        <small>
                            • Interest Rate: <b>{l.get('interest_rate')}%</b><br>
                            • Term: <b>{l.get('term_months')} months</b><br>
                            • Officer: <b>{l.get('loan_officer') or 'N/A'}</b><br>
                            • Branch: <b>{l.get('branch_name') or 'N/A'}</b>
                        </small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Repayment Schedule Sub-Section
        loan_ids = [l["loan_id"] for l in loans]
        loan_state_key = f"active_loan_{active_cid}"
        if loan_state_key not in st.session_state or st.session_state[loan_state_key] not in loan_ids:
            st.session_state[loan_state_key] = loan_ids[0]

        selected_loan = st.selectbox(
            "Inspect Repayment Schedule for Loan Facility",
            options=loan_ids,
            key=loan_state_key,
        )
        schedule = backend.get_repayment_schedule(selected_loan)

        if schedule:
            sched_rows = []
            for inst in schedule:
                st_val = inst.get("status", "Pending")
                if st_val == "Paid":
                    st_pill = "🟢 Paid"
                elif st_val == "Pending":
                    st_pill = "🟡 Pending"
                else:
                    st_pill = f"🔴 {st_val}"

                sched_rows.append({
                    "Installment #": inst.get("installment_no"),
                    "Due Date": inst.get("due_date"),
                    "Amount Due": format_inr(inst.get("amount_due")),
                    "Status": st_pill,
                })
            render_dataframe(pd.DataFrame(sched_rows))
        else:
            st.info(f"No installments scheduled for loan {selected_loan}.")
    else:
        st.info(f"Customer {active_cid} does not hold any active loan facilities.")

    st.markdown("<br><hr>", unsafe_allow_html=True)

    # 2. Investment Portfolio Section
    st.markdown("### 📈 Wealth Management & Investments")
    investments = backend.get_investments(active_cid)

    if investments:
        total_inv = sum(inv.get("amount", 0) for inv in investments)
        col_inv_metric, col_inv_space = st.columns([1, 2])
        with col_inv_metric:
            st.metric(label="Total Investment Value", value=format_inr(total_inv))

        inv_col1, inv_col2 = st.columns([3, 2])
        with inv_col1:
            inv_rows = [
                {
                    "Investment ID": inv.get("investment_id"),
                    "Product Category": inv.get("investment_type"),
                    "Principal Amount": format_inr(inv.get("amount")),
                    "Start Date": inv.get("start_date"),
                }
                for inv in investments
            ]
            render_dataframe(pd.DataFrame(inv_rows))

        with inv_col2:
            inv_df = pd.DataFrame(investments)
            grouped = inv_df.groupby("investment_type")["amount"].sum().reset_index()
            grouped.columns = ["Investment Type", "Amount (₹)"]
            st.caption("Asset Allocation Breakdown")
            st.bar_chart(grouped.set_index("Investment Type"))
    else:
        st.info(f"Customer {active_cid} has no registered investment portfolio items.")


# ==============================================================================
# Screen 4: Analytics & Graph Intelligence
# ==============================================================================

elif screen == SCREEN_ANALYTICS:
    st.markdown("<div class='main-header'>Bank-Wide Analytics & Graph Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Branch distribution analytics, customer wealth leaderboard, AML high-value transfer monitor, and multi-hop graph fund tracing.</div>", unsafe_allow_html=True)

    # Row 1: Branch Account Distribution & Wealth Leaderboard
    col_an1, col_an2 = st.columns(2)

    with col_an1:
        st.markdown("### 🏦 Branch Account Distribution")
        branch_counts = backend.get_branch_account_counts()
        if branch_counts:
            b_df = pd.DataFrame(branch_counts)
            st.bar_chart(b_df.set_index("branch_name")["account_count"])
            render_dataframe(b_df.rename(columns={"branch_name": "Branch", "account_count": "Total Accounts"}))
        else:
            st.info("No branch account distribution data available.")

    with col_an2:
        st.markdown("### 🏆 Customer Wealth Leaderboard")
        top_n = st.slider("Leaderboard Display Limit", min_value=1, max_value=10, value=5, key="analytics_leaderboard_limit")
        top_customers = backend.get_top_customers_by_balance(limit=top_n)
        if top_customers:
            leader_rows = [
                {
                    "Rank": f"#{idx + 1}",
                    "Customer ID": tc.get("customer_id"),
                    "Name": tc.get("name"),
                    "Total Balance": format_inr(tc.get("total_balance")),
                }
                for idx, tc in enumerate(top_customers)
            ]
            render_dataframe(pd.DataFrame(leader_rows))
        else:
            st.info("No leaderboard data available.")

    st.markdown("<br><hr>", unsafe_allow_html=True)

    # Row 2: High-Value Transfer Monitor
    st.markdown("### 🚨 AML High-Value Transfer Audit Monitor")
    st.caption("Filters transfers meeting or exceeding the specified compliance audit threshold.")
    threshold_col, count_col = st.columns([2, 1])
    with threshold_col:
        min_threshold = st.number_input(
            "Minimum Transfer Amount Threshold (₹)",
            min_value=1000.0,
            value=20000.0,
            step=5000.0,
            format="%.2f",
            key="analytics_aml_threshold",
        )
    large_transfers = backend.get_large_transfers(min_threshold)
    with count_col:
        st.metric(
            label="Flagged Transactions",
            value=len(large_transfers),
            help=f"Transfers >= {format_inr(min_threshold)}",
        )

    if large_transfers:
        lt_rows = [
            {
                "Transfer Txn ID": lt.get("txn_id"),
                "Origin Account": lt.get("from_account"),
                "Destination Account": lt.get("to_account"),
                "Amount": format_inr(lt.get("amount")),
                "Execution Date": lt.get("txn_date"),
            }
            for lt in large_transfers
        ]
        render_dataframe(pd.DataFrame(lt_rows))
    else:
        st.info(f"No transfers found exceeding {format_inr(min_threshold)}.")

    st.markdown("<br><hr>", unsafe_allow_html=True)

    # Row 3: Multi-Hop Fund Flow (Money Trail Tracer)
    st.markdown("### 🕸️ Multi-Hop Fund Flow & Money Trail Tracer")
    st.caption(
        "Leverages Neo4j variable-length path traversal (<code>[:TRANSFERRED_TO*1..3]</code>) "
        "to follow the cascade of funds across up to 3 hops from an origin account.",
        unsafe_allow_html=True,
    )

    trail_input_col, trail_btn_col = st.columns([3, 1])
    with trail_input_col:
        trail_origin = st.text_input(
            "Origin Account Number to Trace",
            value="AC1001",
            help="Enter any account number (e.g. AC1001, AC1002, AC1004) to discover all directed transfer pathways.",
            key="analytics_trail_origin",
        ).strip()
    with trail_btn_col:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        search_trails = st.button("Trace Fund Trails", use_container_width=True)

    if trail_origin:
        trails = backend.get_money_trail(trail_origin)
        if trails:
            st.success(f"Discovered **{len(trails)}** directed fund trail(s) originating from `{trail_origin}`:")
            for idx, item in enumerate(trails):
                trail_nodes = item.get("trail", [])
                hops = item.get("hops", len(trail_nodes) - 1)

                # Render HTML Breadcrumb representation
                nodes_html = []
                for n_idx, node in enumerate(trail_nodes):
                    if n_idx == 0:
                        nodes_html.append(f"<span class='hop-node' style='background-color:#2563eb;'>{node}</span>")
                    elif n_idx == len(trail_nodes) - 1:
                        nodes_html.append(f"<span class='hop-node' style='background-color:#059669;'>{node}</span>")
                    else:
                        nodes_html.append(f"<span class='hop-node'>{node}</span>")

                chain_str = "<span class='hop-arrow'>➔</span>".join(nodes_html)
                st.markdown(
                    f"""
                    <div class='portal-card' style='padding: 0.75rem 1rem; margin-bottom: 0.5rem; display: flex; align-items: center; justify-content: space-between;'>
                        <div>
                            <strong>Path #{idx + 1}:</strong> {chain_str}
                        </div>
                        <span class='hop-pill'>{hops} {'hop' if hops == 1 else 'hops'}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info(f"No outgoing multi-hop transfer trails found originating from account `{trail_origin}`.")
