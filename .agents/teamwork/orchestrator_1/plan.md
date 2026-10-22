# Plan: Smart Banking Mini-Project (Neo4j & Streamlit)

## Objective
Build a complete, production-ready "Smart Banking Mini-Project" using Neo4j and Streamlit strictly following the team specification, graph schema, 20 function contracts, 4 UI screens, and test suite.

## Methodology & Pattern
Project Orchestration Pattern with Dual Track:
1. **Implementation Track**:
   - M1: Project Files & Infrastructure (`requirements.txt`, `.gitignore`, `.env.example`, `load_data.cypher`, `connection.py`)
   - M2: Complete 20-Function Database Contracts (`mock_db.py` offline and `db.py` live Cypher queries)
   - M3: Streamlit Application (`app.py` with 4 screens, cards, forms, and sidebar mode toggle)
   - M4: Documentation (`README.md` setup, schema explanation, why Neo4j talking points)
   - M5: Final E2E Pass and Forensic Audit
2. **E2E Testing Track**:
   - Build `test_suite.py` covering all 47 nodes, 20 functions, and Section 8 test cases.
   - Run verification across mock and live DB.

## Subagent Allocation
- Survey: 3 Spec Miners / Explorers to examine workspace, Neo4j schema details, Cypher queries, and UI screen bindings.
- Workers: Implement individual modules with strict write ownership.
- Reviewers: 2 independent reviewers for code quality, contract compliance, error handling, date formatting.
- Challengers: Adversarial verification of 20 functions, edge cases, negative tests.
- Forensic Auditor: Check for genuine Cypher implementation, no hardcoded cheating, no fake mocks.

## Execution Timeline
- Step 1: Dispatch 3 parallel Explorers / Spec Miners for Survey.
- Step 2: Merge survey reports into `PROJECT.md` and `TEST_INFRA.md`.
- Step 3: Sequential milestone execution and gating.
- Step 4: Final verification and report to Sentinel.
