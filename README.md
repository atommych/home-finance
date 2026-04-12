# Home Finance SaaS

Personal finance dashboard that parses Portuguese bank statement PDFs, auto-categorizes transactions, and visualizes spending trends.

## Features

- Upload bank statement PDFs (CGD supported, more banks coming)
- Auto-extract transactions (date, description, amount, balance)
- Auto-categorize transactions by configurable rules
- Filter and browse transactions by date and category
- Monthly expense charts by category
- CSV export
- Multi-user with Supabase Auth (email/password)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Database | PostgreSQL (Supabase) |
| Auth | Supabase Auth |
| PDF Parsing | pypdf + regex |
| Charts | Altair |
| Hosting | Google Cloud Run |
| IaC | Terraform |
| CI/CD | GitHub Actions |
| Containers | Docker |

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (runs via WSL on Windows)
- A [Supabase](https://supabase.com) account (free tier)
- (For deploy) [gcloud CLI](https://cloud.google.com/sdk/docs/install) + GCP project

## Quick Start

### 1. Clone and configure

```bash
git clone <repo-url>
cd home-finance-saas
cp .env.example .env
# Edit .env with your Supabase credentials
```

### 2. Set up Supabase

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run `supabase/migrations/001_initial_schema.sql`
3. Copy your **Project URL** and **anon key** from Settings > API into `.env`

### 3. Start the app

```bash
make up
```

The app will be available at **http://localhost:8501**

### 4. Use it

1. Create an account (signup form on the app)
2. Go to **Upload** and select your bank statement PDFs
3. View your transactions, charts, and manage categories

## Development

All commands run inside Docker — no local Python installation needed.

```bash
make help          # Show all available commands

# Core workflow
make up            # Start app + database
make down          # Stop everything
make test          # Run tests (22 tests)
make lint          # Check code style
make format        # Auto-format code
make check         # Run lint + tests together

# Database
make db-shell      # Open psql shell
make db-reset      # Destroy and recreate database

# Debugging
make logs          # Follow container logs
make shell         # Open bash in the app container
```

## Project Structure

```
home-finance-saas/
├── app/
│   ├── main.py              # Streamlit entry point
│   ├── auth.py              # Supabase Auth (login/signup)
│   ├── config.py            # Settings (pydantic-settings)
│   ├── database.py          # Supabase client
│   ├── pages/               # Streamlit pages
│   │   ├── 1_Dashboard.py   # Summary stats + charts
│   │   ├── 2_Transactions.py# Browse + filter + export
│   │   ├── 3_Upload.py      # PDF upload + parsing
│   │   ├── 4_Categories.py  # Manage categories + rules
│   │   └── 5_Settings.py    # Profile + preferences
│   ├── parsers/             # Bank statement parsers
│   │   ├── base.py          # Abstract parser interface
│   │   └── cgd.py           # CGD (Caixa Geral de Depositos)
│   ├── services/            # Business logic
│   │   ├── analytics_service.py
│   │   ├── category_service.py
│   │   ├── import_service.py
│   │   └── supabase_service.py
│   └── components/          # Reusable UI widgets
├── tests/                   # pytest tests (22 tests)
├── supabase/migrations/     # SQL schema + RLS policies
├── infra/
│   ├── docker/              # Dockerfile + docker-compose
│   └── terraform/           # GCP Cloud Run config
├── docs/                    # Architecture, ADRs, deploy guide
├── .github/workflows/       # CI (lint+test) + deploy
├── CLAUDE.md                # AI agent conventions
├── Makefile                 # All dev commands
└── pyproject.toml           # Python dependencies
```

## Supported Banks

| Bank | Status | Format |
|------|--------|--------|
| CGD (Caixa Geral de Depositos) | Supported | PDF monthly statements |
| Activo Bank | Planned | PDF monthly statements |
| Millennium BCP | Planned | PDF monthly statements |

Adding a new bank parser: create `app/parsers/your_bank.py` extending `BankParser`, register it in `app/parsers/__init__.py`, and add tests.

## Deployment

Three options — see [docs/DEPLOY.md](docs/DEPLOY.md) for full details.

**Quickest (manual):**

```bash
make build-prod
make deploy-manual GCP_PROJECT=your-project-id
```

**Automated (GitHub Actions):**

Push to `main` triggers build + deploy. Set repository secrets: `GCP_PROJECT_ID`, `GCP_SA_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`.

**Infrastructure as Code (Terraform):**

```bash
make tf-init
make tf-plan
make tf-apply
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_KEY` | Supabase anon/public key | Yes |
| `DEBUG` | Enable debug mode | No (default: false) |

## License

Private — all rights reserved.
