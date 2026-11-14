# High-Performance Coding Standards & Rules

## 1. Code Quality & Verification
- **Automated Verification:** Always run existing unit tests (`pytest`) before declaring any code change complete.
- **Type Safety:** Use strict Python 3.11+ type hints (`typing.Optional`, `typing.List`, `typing.Dict`) on all function signatures.
- **Dependency Hygiene:** Never add or pin unverified package versions. Always verify compatibility before writing `requirements.txt`.

## 2. Database & Data Integrity
- **Transactions:** Always execute database mutations within transactions (`with db.transaction():`).
- **Parameterized Queries:** Never use f-strings or string concatenation for SQL queries; always use `?` placeholders.
- **High Concurrency:** Keep SQLite in WAL mode (`PRAGMA journal_mode=WAL;`) with `synchronous=NORMAL` and indexed lookups.

## 3. API Resilience & Error Handling
- **Graceful Retries:** External API calls (YouTube Data API, Instagram, Google Drive) must implement exponential backoff and handle quota limits gracefully.
- **Structured Logging:** Use the `logging` module with timestamps and component tags. Avoid raw `print` statements in core modules.
- **Zero Secrets in Code:** Credentials and session cookies must strictly reside in environment variables or encrypted secrets.
