// ==============================================================================
// Smart Banking Mini-Project: Shared Graph Dataset Initialization
// Neo4j 5+ Compatible Cypher Script
// Total Nodes: Exactly 47
// Constraints: 9 Unique ID Constraints
// ==============================================================================

// 1. Clean slate
MATCH (n) DETACH DELETE n;

// 2. Schema Unique Constraints (9 Entity Types)
CREATE CONSTRAINT IF NOT EXISTS FOR (b:Branch) REQUIRE b.branch_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (e:Employee) REQUIRE e.emp_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (c:Customer) REQUIRE c.customer_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (a:Account) REQUIRE a.account_number IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (t:Transaction) REQUIRE t.txn_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (l:Loan) REQUIRE l.loan_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (i:Installment) REQUIRE i.installment_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (inv:Investment) REQUIRE inv.investment_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (sr:ServiceRequest) REQUIRE sr.request_id IS UNIQUE;

// 3. Create Branches (3 nodes)
CREATE (br1:Branch {branch_id: 'BR01', branch_name: 'Anna Nagar', city: 'Chennai'})
CREATE (br2:Branch {branch_id: 'BR02', branch_name: 'T Nagar', city: 'Chennai'})
CREATE (br3:Branch {branch_id: 'BR03', branch_name: 'Koramangala', city: 'Bangalore'})

// 4. Create Employees (6 nodes)
CREATE (e1:Employee {emp_id: 'E01', name: 'Ramesh Iyer', role: 'Branch Manager', email: 'ramesh.iyer@smartbank.com', phone: '9840111101'})
CREATE (e2:Employee {emp_id: 'E02', name: 'Priya Menon', role: 'Relationship Manager', email: 'priya.menon@smartbank.com', phone: '9840111102'})
CREATE (e3:Employee {emp_id: 'E03', name: 'Arjun Nair', role: 'Relationship Manager', email: 'arjun.nair@smartbank.com', phone: '9840111103'})
CREATE (e4:Employee {emp_id: 'E04', name: 'Divya Rao', role: 'Loan Officer', email: 'divya.rao@smartbank.com', phone: '9840111104'})
CREATE (e5:Employee {emp_id: 'E05', name: 'Karthik Suresh', role: 'Customer Service Executive', email: 'karthik.suresh@smartbank.com', phone: '9840111105'})
CREATE (e6:Employee {emp_id: 'E06', name: 'Meena Pillai', role: 'Customer Service Executive', email: 'meena.pillai@smartbank.com', phone: '9840111106'})

// Employee - Branch Relationships
CREATE (e1)-[:WORKS_AT]->(br1)
CREATE (e2)-[:WORKS_AT]->(br1)
CREATE (e3)-[:WORKS_AT]->(br2)
CREATE (e4)-[:WORKS_AT]->(br1)
CREATE (e5)-[:WORKS_AT]->(br1)
CREATE (e6)-[:WORKS_AT]->(br3)

// 5. Create Customers (6 nodes)
CREATE (c1:Customer {customer_id: 'C01', first_name: 'Samridhi', last_name: 'Sharma', name: 'Samridhi Sharma', customer_type: 'Premium', city: 'Chennai', phone: '9876543210', email: 'samridhi.sharma@example.com'})
CREATE (c2:Customer {customer_id: 'C02', first_name: 'Rahul', last_name: 'Verma', name: 'Rahul Verma', customer_type: 'Standard', city: 'Chennai', phone: '9876543211', email: 'rahul.verma@example.com'})
CREATE (c3:Customer {customer_id: 'C03', first_name: 'Anita', last_name: 'Roy', name: 'Anita Roy', customer_type: 'Premium', city: 'Chennai', phone: '9876543212', email: 'anita.roy@example.com'})
CREATE (c4:Customer {customer_id: 'C04', first_name: 'Suresh', last_name: 'Rao', name: 'Suresh Rao', customer_type: 'Standard', city: 'Chennai', phone: '9876543213', email: 'suresh.rao@example.com'})
CREATE (c5:Customer {customer_id: 'C05', first_name: 'Lakshmi', last_name: 'Narayanan', name: 'Lakshmi Narayanan', customer_type: 'Standard', city: 'Bangalore', phone: '9876543214', email: 'lakshmi.narayanan@example.com'})
CREATE (c6:Customer {customer_id: 'C06', first_name: 'Vikram', last_name: 'Singh', name: 'Vikram Singh', customer_type: 'Premium', city: 'Bangalore', phone: '9876543215', email: 'vikram.singh@example.com'})

// Customer - Employee Relationships (RM assignment)
CREATE (c1)-[:ASSIGNED_TO]->(e2)
CREATE (c1)-[:MANAGED_BY]->(e2)
CREATE (c2)-[:ASSIGNED_TO]->(e2)
CREATE (c2)-[:MANAGED_BY]->(e2)
CREATE (c3)-[:ASSIGNED_TO]->(e3)
CREATE (c3)-[:MANAGED_BY]->(e3)
CREATE (c4)-[:ASSIGNED_TO]->(e3)
CREATE (c4)-[:MANAGED_BY]->(e3)
CREATE (c5)-[:ASSIGNED_TO]->(e6)
CREATE (c5)-[:MANAGED_BY]->(e6)
CREATE (c6)-[:ASSIGNED_TO]->(e6)
CREATE (c6)-[:MANAGED_BY]->(e6)

// 6. Create Accounts (8 nodes)
CREATE (a1:Account {account_number: 'AC1001', account_type: 'Savings', balance: 85000.0, status: 'Active'})
CREATE (a2:Account {account_number: 'AC1002', account_type: 'Current', balance: 150000.0, status: 'Active'})
CREATE (a3:Account {account_number: 'AC1003', account_type: 'Savings', balance: 42000.0, status: 'Active'})
CREATE (a4:Account {account_number: 'AC1004', account_type: 'Current', balance: 200000.0, status: 'Active'})
CREATE (a5:Account {account_number: 'AC1005', account_type: 'Savings', balance: 65000.0, status: 'Active'})
CREATE (a6:Account {account_number: 'AC1006', account_type: 'Savings', balance: 50000.0, status: 'Active'})
CREATE (a7:Account {account_number: 'AC1007', account_type: 'Current', balance: 95000.0, status: 'Active'})
CREATE (a8:Account {account_number: 'AC1008', account_type: 'Savings', balance: 30000.0, status: 'Active'})

// Customer - Account - Branch Links
// AC1001 (C01, BR01 Anna Nagar)
CREATE (c1)-[:HOLDS]->(a1)
CREATE (c1)-[:OWNS]->(a1)
CREATE (a1)-[:HELD_AT]->(br1)
CREATE (a1)-[:LOCATED_AT]->(br1)

// AC1002 (C01, BR01 Anna Nagar)
CREATE (c1)-[:HOLDS]->(a2)
CREATE (c1)-[:OWNS]->(a2)
CREATE (a2)-[:HELD_AT]->(br1)
CREATE (a2)-[:LOCATED_AT]->(br1)

// AC1003 (C02, BR01 Anna Nagar)
CREATE (c2)-[:HOLDS]->(a3)
CREATE (c2)-[:OWNS]->(a3)
CREATE (a3)-[:HELD_AT]->(br1)
CREATE (a3)-[:LOCATED_AT]->(br1)

// AC1004 (C03, BR02 T Nagar)
CREATE (c3)-[:HOLDS]->(a4)
CREATE (c3)-[:OWNS]->(a4)
CREATE (a4)-[:HELD_AT]->(br2)
CREATE (a4)-[:LOCATED_AT]->(br2)

// AC1005 (C04, BR02 T Nagar)
CREATE (c4)-[:HOLDS]->(a5)
CREATE (c4)-[:OWNS]->(a5)
CREATE (a5)-[:HELD_AT]->(br2)
CREATE (a5)-[:LOCATED_AT]->(br2)

// AC1006 (C05, BR02 T Nagar)
CREATE (c5)-[:HOLDS]->(a6)
CREATE (c5)-[:OWNS]->(a6)
CREATE (a6)-[:HELD_AT]->(br2)
CREATE (a6)-[:LOCATED_AT]->(br2)

// AC1007 (C06, BR03 Koramangala)
CREATE (c6)-[:HOLDS]->(a7)
CREATE (c6)-[:OWNS]->(a7)
CREATE (a7)-[:HELD_AT]->(br3)
CREATE (a7)-[:LOCATED_AT]->(br3)

// AC1008 (C05, BR03 Koramangala)
CREATE (c5)-[:HOLDS]->(a8)
CREATE (c5)-[:OWNS]->(a8)
CREATE (a8)-[:HELD_AT]->(br3)
CREATE (a8)-[:LOCATED_AT]->(br3)

// 7. Create Transactions (8 nodes: Non-transfer deposits and withdrawals)
CREATE (t1:Transaction {txn_id: 'T1', txn_type: 'Deposit', amount: 20000.0, txn_date: '2026-03-01'})
CREATE (t2:Transaction {txn_id: 'T2', txn_type: 'Withdrawal', amount: 5000.0, txn_date: '2026-03-05'})
CREATE (t3:Transaction {txn_id: 'T3', txn_type: 'Deposit', amount: 50000.0, txn_date: '2026-03-02'})
CREATE (t4:Transaction {txn_id: 'T4', txn_type: 'Deposit', amount: 15000.0, txn_date: '2026-03-03'})
CREATE (t5:Transaction {txn_id: 'T5', txn_type: 'Withdrawal', amount: 10000.0, txn_date: '2026-03-04'})
CREATE (t6:Transaction {txn_id: 'T6', txn_type: 'Deposit', amount: 25000.0, txn_date: '2026-03-06'})
CREATE (t7:Transaction {txn_id: 'T7', txn_type: 'Deposit', amount: 30000.0, txn_date: '2026-03-07'})
CREATE (t8:Transaction {txn_id: 'T8', txn_type: 'Withdrawal', amount: 8000.0, txn_date: '2026-03-08'})

// Transaction - Account links
CREATE (a1)-[:HAS_TRANSACTION]->(t1)
CREATE (t1)-[:PERFORMED]->(a1)
CREATE (t1)-[:PERFORMED_ON]->(a1)

CREATE (a1)-[:HAS_TRANSACTION]->(t2)
CREATE (t2)-[:PERFORMED]->(a1)
CREATE (t2)-[:PERFORMED_ON]->(a1)

CREATE (a2)-[:HAS_TRANSACTION]->(t3)
CREATE (t3)-[:PERFORMED]->(a2)
CREATE (t3)-[:PERFORMED_ON]->(a2)

CREATE (a3)-[:HAS_TRANSACTION]->(t4)
CREATE (t4)-[:PERFORMED]->(a3)
CREATE (t4)-[:PERFORMED_ON]->(a3)

CREATE (a4)-[:HAS_TRANSACTION]->(t5)
CREATE (t5)-[:PERFORMED]->(a4)
CREATE (t5)-[:PERFORMED_ON]->(a4)

CREATE (a5)-[:HAS_TRANSACTION]->(t6)
CREATE (t6)-[:PERFORMED]->(a5)
CREATE (t6)-[:PERFORMED_ON]->(a5)

CREATE (a6)-[:HAS_TRANSACTION]->(t7)
CREATE (t7)-[:PERFORMED]->(a6)
CREATE (t7)-[:PERFORMED_ON]->(a6)

CREATE (a7)-[:HAS_TRANSACTION]->(t8)
CREATE (t8)-[:PERFORMED]->(a7)
CREATE (t8)-[:PERFORMED_ON]->(a7)

// 8. Create Transfers (8 directed relationships via TRANSFERRED_TO)
CREATE (a1)-[:TRANSFERRED_TO {txn_id: 'TR1', amount: 8000.0, txn_date: '2026-03-10'}]->(a3)
CREATE (a3)-[:TRANSFERRED_TO {txn_id: 'TR2', amount: 6000.0, txn_date: '2026-03-12'}]->(a5)
CREATE (a5)-[:TRANSFERRED_TO {txn_id: 'TR3', amount: 4000.0, txn_date: '2026-03-14'}]->(a6)
CREATE (a2)-[:TRANSFERRED_TO {txn_id: 'TR4', amount: 25000.0, txn_date: '2026-03-15'}]->(a7)
CREATE (a6)-[:TRANSFERRED_TO {txn_id: 'TR5', amount: 2000.0, txn_date: '2026-03-16'}]->(a1)
CREATE (a4)-[:TRANSFERRED_TO {txn_id: 'TR6', amount: 40000.0, txn_date: '2026-03-18'}]->(a2)
CREATE (a7)-[:TRANSFERRED_TO {txn_id: 'TR7', amount: 12000.0, txn_date: '2026-03-20'}]->(a8)
CREATE (a8)-[:TRANSFERRED_TO {txn_id: 'TR8', amount: 10000.0, txn_date: '2026-03-22'}]->(a4)

// 9. Create Loans (3 nodes)
CREATE (l1:Loan {loan_id: 'L01', loan_type: 'Home Loan', amount: 2500000.0, interest_rate: 8.5, term_months: 240, status: 'Active'})
CREATE (l2:Loan {loan_id: 'L02', loan_type: 'Personal Loan', amount: 500000.0, interest_rate: 11.5, term_months: 36, status: 'Active'})
CREATE (l3:Loan {loan_id: 'L03', loan_type: 'Car Loan', amount: 800000.0, interest_rate: 9.0, term_months: 60, status: 'Active'})

// Loan relationships
CREATE (c1)-[:TAKEN]->(l1)
CREATE (c1)-[:HAS_LOAN]->(l1)
CREATE (l1)-[:SANCTIONED_BY]->(e4)
CREATE (l1)-[:MANAGED_BY]->(e4)
CREATE (l1)-[:HELD_AT]->(br1)
CREATE (l1)-[:LOCATED_AT]->(br1)

CREATE (c2)-[:TAKEN]->(l2)
CREATE (c2)-[:HAS_LOAN]->(l2)
CREATE (l2)-[:SANCTIONED_BY]->(e4)
CREATE (l2)-[:MANAGED_BY]->(e4)
CREATE (l2)-[:HELD_AT]->(br2)
CREATE (l2)-[:LOCATED_AT]->(br2)

CREATE (c3)-[:TAKEN]->(l3)
CREATE (c3)-[:HAS_LOAN]->(l3)
CREATE (l3)-[:SANCTIONED_BY]->(e4)
CREATE (l3)-[:MANAGED_BY]->(e4)
CREATE (l3)-[:HELD_AT]->(br3)
CREATE (l3)-[:LOCATED_AT]->(br3)

// 10. Create Installments (6 nodes)
CREATE (ins1:Installment {installment_id: 'INS01', installment_no: 1, due_date: '2026-01-10', amount_due: 25000.0, status: 'Paid'})
CREATE (ins2:Installment {installment_id: 'INS02', installment_no: 2, due_date: '2026-02-10', amount_due: 25000.0, status: 'Paid'})
CREATE (ins3:Installment {installment_id: 'INS03', installment_no: 3, due_date: '2026-03-10', amount_due: 25000.0, status: 'Pending'})

CREATE (ins4:Installment {installment_id: 'INS04', installment_no: 1, due_date: '2026-01-15', amount_due: 16000.0, status: 'Paid'})
CREATE (ins5:Installment {installment_id: 'INS05', installment_no: 2, due_date: '2026-02-15', amount_due: 16000.0, status: 'Pending'})

CREATE (ins6:Installment {installment_id: 'INS06', installment_no: 1, due_date: '2026-03-20', amount_due: 16500.0, status: 'Pending'})

// Loan - Installment links
CREATE (l1)-[:HAS_INSTALLMENT]->(ins1)
CREATE (l1)-[:HAS_INSTALLMENT]->(ins2)
CREATE (l1)-[:HAS_INSTALLMENT]->(ins3)

CREATE (l2)-[:HAS_INSTALLMENT]->(ins4)
CREATE (l2)-[:HAS_INSTALLMENT]->(ins5)

CREATE (l3)-[:HAS_INSTALLMENT]->(ins6)

// 11. Create Investments (4 nodes)
CREATE (i1:Investment {investment_id: 'I01', investment_type: 'Mutual Fund', amount: 100000.0, start_date: '2025-01-15'})
CREATE (i2:Investment {investment_id: 'I02', investment_type: 'Fixed Deposit', amount: 200000.0, start_date: '2025-02-20'})
CREATE (i3:Investment {investment_id: 'I03', investment_type: 'Wealth Management', amount: 300000.0, start_date: '2025-06-10'})
CREATE (i4:Investment {investment_id: 'I04', investment_type: 'Recurring Deposit', amount: 50000.0, start_date: '2025-09-01'})

// Customer - Investment links
CREATE (c1)-[:INVESTED_IN]->(i1)
CREATE (c1)-[:HAS_INVESTMENT]->(i1)

CREATE (c2)-[:INVESTED_IN]->(i2)
CREATE (c2)-[:HAS_INVESTMENT]->(i2)

CREATE (c1)-[:INVESTED_IN]->(i3)
CREATE (c1)-[:HAS_INVESTMENT]->(i3)

CREATE (c3)-[:INVESTED_IN]->(i4)
CREATE (c3)-[:HAS_INVESTMENT]->(i4)

// 12. Create Service Requests (3 nodes)
CREATE (sr1:ServiceRequest {request_id: 'SR01', request_type: 'Address Update', description: 'Update mailing address to Anna Nagar', status: 'Resolved', request_date: '2026-01-20'})
CREATE (sr2:ServiceRequest {request_id: 'SR02', request_type: 'Debit Card Replacement', description: 'Request for replacement chip debit card', status: 'Pending', request_date: '2026-02-10'})
CREATE (sr3:ServiceRequest {request_id: 'SR03', request_type: 'Cheque Book', description: 'Request new 50-leaf cheque book', status: 'Resolved', request_date: '2026-02-15'})

// Customer - Service Request - Employee links
CREATE (c2)-[:RAISED]->(sr1)
CREATE (sr1)-[:ASSIGNED_TO]->(e5)

CREATE (c3)-[:RAISED]->(sr2)
CREATE (sr2)-[:ASSIGNED_TO]->(e5)

CREATE (c1)-[:RAISED]->(sr3)
CREATE (sr3)-[:ASSIGNED_TO]->(e5)
;
