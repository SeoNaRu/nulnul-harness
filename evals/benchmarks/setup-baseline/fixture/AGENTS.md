# Reading queue working agreement

- Keep the project dependency-free and use Python's standard library.
- `reading_queue.py` owns routing; `tests/test_reading_queue.py` owns its completion check.
- Run `python3 -B -m unittest discover -s tests -p 'test_*.py' -v` before reporting completion.
- Existing maintainer role: preserve the routing API and synthesize the final result.
- Do not use network, credentials, external writes, global registration, or deployment.
