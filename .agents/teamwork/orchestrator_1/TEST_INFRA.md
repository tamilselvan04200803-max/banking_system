# E2E Test Infra: Smart Banking Mini-Project

## Test Philosophy
- Opaque-box and contract-driven verification.
- Validates both offline mock implementation (`mock_db.py`) and live Neo4j database (`db.py`).
- Verification methodology: Category-Partition + Boundary Value Analysis + Pairwise Combinations + Real-World Workloads.

## Feature Inventory & Test Coverage
| # | Feature / Function | Tier 1: Feature Coverage | Tier 2: Boundary & Corner | Tier 3: Combinations | Tier 4: Real-World Scenarios |
|---|--------------------|:------------------------:|:-------------------------:|:--------------------:|:----------------------------:|
| 1 | `get_customer` | Normal lookup C01 | Non-existent customer | RM mapping | Customer profile load |
| 2 | `get_accounts` | Accounts for C01 | Customer with 0 accounts | Multiple branch links | Portfolio view |
| 3 | `get_total_balance`| Sum for C01 | Customer with 0 balance | Post-deposit/transfer | Credit evaluation |
| 4 | `get_transactions` | AC1001 history | Account with 0 txns | 3-part UNION order | Statement generation |
| 5 | `get_loans` | Loans for C01 | Customer with no loans | Officer & branch join | Loan management |
| 6 | `get_repayment_schedule`| Schedule for L01 | Invalid loan ID | Pending installment | Schedule check |
| 7 | `get_investments` | Investments for C01| Customer with no inv | Multiple asset types | Wealth analysis |
| 8 | `get_service_requests`| Requests for C01 | No requests | CSE E05 assignment | Customer support |
| 9 | `get_branches` | 3 branches | Branch listing | Account association | Branch selector |
| 10 | `add_customer` | New valid customer | Duplicate customer ID | New customer workflow | Customer onboarding |
| 11 | `update_customer_contact`| Update C01 phone/email| Non-existent customer | Verify profile reflects | Contact update |
| 12 | `open_account` | Open new AC1009 | Invalid branch/cust | Open + transact | Account creation |
| 13 | `close_account` | Close zero-bal account| Non-zero bal account | Close non-existent | Account closure |
| 14 | `raise_service_request`| Valid SR creation | Empty description | SR ID format & CSE | Service ticket lifecycle |
| 15 | `process_transaction`| Deposit & Withdrawal | Overdraft / 0 balance | Mutation updates bal | Cash desk operations |
| 16 | `transfer_money` | Inter-account transfer| Same account / Overdraft| Multi-step transfer chain| Inter-bank transfer |
| 17 | `get_branch_account_counts`| Branch breakdown | All branches covered | Account counts sum | Branch reporting |
| 18 | `get_top_customers_by_balance`| Top 3 / Top 5 | Limit <= 0 / out of range| Descending balance order| High-net-worth report |
| 19 | `get_large_transfers` | Min amount filter | Higher than max transfer | Multi-transfer sort | Anti-money laundering |
| 20 | `get_money_trail` | AC1001 3-hop chain | Account with 0 transfers | Loop / terminal node | Fraud investigation |

## Test Suite Architecture (`test_suite.py`)
- **Direct CLI Execution**: `python test_suite.py` with colored terminal output and exit code 0/1.
- **Pytest Runner**: `pytest test_suite.py -v`.
- **Backend Flags**:
  - Default: tests `mock_db`
  - `--live`: tests live `db` (against Neo4j instance)
  - `--all`: runs against both backends
- **Section 8 Test Assertions**: 21 concrete assertion checkpoints validating node counts, balances, transfers, and mutations.
