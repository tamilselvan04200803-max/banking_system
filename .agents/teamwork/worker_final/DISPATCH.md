# DISPATCH — worker_final

## Mission
Execute repository-wide end-to-end verification across all files and test suites for final project sign-off.

## Tasks
1. Execute bytecode compilation for all project Python files:
   `python -m py_compile app.py connection.py db.py mock_db.py test_suite.py`
2. Run standalone unittest test suite:
   `python test_suite.py`
   Confirm 41 passed, 2 skipped (live), 0 failures, 0 errors.
3. Run pytest test suite:
   `pytest -p no:schemathesis test_suite.py -v`
   Confirm 41 passed, 2 skipped (live), 0 failures, 0 errors.
4. Run full Challenger test suite:
   `python -X utf8 test_challenger_m3.py`
   Confirm all 7 phases pass with exit code 0.
5. Verify Mermaid diagram rendering:
   `python .agents\teamwork\worker_m5_it2\verify_readme_mermaid.py`
   Confirm HTTP 200 for both diagrams.
6. Check file tree integrity:
   - `requirements.txt`
   - `.gitignore`
   - `.env.example`
   - `load_data.cypher`
   - `connection.py`
   - `db.py`
   - `mock_db.py`
   - `app.py`
   - `test_suite.py`
   - `README.md`
7. Write comprehensive verification report to `c:\dbms_da-3-project\.agents\teamwork\worker_final\handoff.md`.
8. Notify caller via `send_message`.
