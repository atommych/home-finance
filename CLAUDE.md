# CLAUDE.md

## Project Overview

Home Finance SaaS is a multi-user personal finance dashboard that parses Portuguese bank statement PDFs, auto-categorizes transactions, and visualizes spending trends. Built with Streamlit (frontend), Supabase (database + auth), and deployed on Google Cloud Run.

## Architecture

- **Frontend**: Streamlit (multi-page app)
- **Database**: PostgreSQL on Supabase (free tier)
- **Auth**: Supabase Auth (email/password + Google OAuth)
- **File Storage**: Supabase Storage (uploaded PDFs)
- **PDF Parsing**: pypdf + custom regex parsers per bank
- **Data Processing**: pandas
- **Charts**: Altair (via Streamlit)
- **Deployment**: Google Cloud Run (Docker container)
- **IaC**: Terraform (GCP resources)
- **CI/CD**: GitHub Actions

## Conventions

### Project Structure
- Streamlit entry point: `app/main.py`
- Pages: `app/pages/` (numbered for sidebar order)
- Bank parsers: `app/parsers/` (one file per bank, all extend `base.py`)
- Business logic: `app/services/` (never in pages or parsers)
- UI components: `app/components/` (reusable Streamlit widgets)
- Database migrations: `supabase/migrations/` (raw SQL, numbered)
- Infrastructure: `infra/terraform/`

### Python
- Python 3.12+
- Package manager: `uv`
- Linting: `ruff`
- Testing: `pytest`
- Type hints on all function signatures
- Use `pydantic-settings` for configuration (`app/config.py`)

### Commands
- Install deps: `uv sync`
- Run app: `uv run streamlit run app/main.py`
- Run tests: `uv run pytest`
- Run linting: `uv run ruff check . && uv run ruff format --check .`
- Format code: `uv run ruff format .`

### Parsers
- Every bank parser extends `BankParser` from `app/parsers/base.py`
- Parsers must implement: `parse(text: str) -> list[Transaction]`
- Parsers are pure functions: text in, structured data out. No I/O, no database calls.
- Each parser has tests with fixture data in `tests/test_parsers/fixtures/`

### Database
- All tables have: `id` (UUID), `user_id` (FK to auth.users), `created_at` (TIMESTAMPTZ)
- Row-Level Security (RLS) on all tables: `user_id = auth.uid()`
- Migrations are raw SQL files in `supabase/migrations/`
- Never modify the database directly — always use migrations

### Services
- One service per domain: `import_service.py`, `category_service.py`, etc.
- Services handle all Supabase queries and business logic
- Pages call services, never query the database directly

### Pages (Streamlit)
- Each page starts with an auth check (`app/auth.py`)
- Use `st.cache_data` for expensive operations
- Keep pages thin — delegate to services and components

### Testing
- Parser tests: use text fixtures (not real PDFs) in `tests/test_parsers/fixtures/`
- Service tests: mock Supabase client
- Every parser must have at least one test with real bank statement text

### Git Conventions
- Branch naming: `feat/xxx`, `fix/xxx`, `chore/xxx`
- Commit messages: conventional commits (`feat:`, `fix:`, `chore:`, `docs:`)
- Always create a PR — never push directly to main

### Common Gotchas
- Portuguese bank statements use European number formatting (periods for date, spaces for thousands)
- Supabase RLS is enabled — always include `user_id` in queries
- pypdf text extraction can vary between PDF versions — always test with real fixtures
- Streamlit reruns the entire script on every interaction — use `st.session_state` for persistence
