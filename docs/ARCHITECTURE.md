# Architecture

## Overview

Home Finance SaaS is a personal finance dashboard that parses Portuguese bank statement PDFs, categorizes transactions, and visualizes spending trends.

## System Diagram

```
┌──────────────────────────────────────────────┐
│         Docker Container (Cloud Run)         │
│   Streamlit App (Dashboard + Upload UI)      │
│   ├── Upload PDFs → parsers/ (per bank)      │
│   ├── Transaction browser + filters          │
│   ├── Category management + rules            │
│   └── Charts (Altair)                        │
└──────────────────┬───────────────────────────┘
                   │ Supabase Client SDK
┌──────────────────▼───────────────────────────┐
│              Supabase                         │
│   ├── Auth (email + Google OAuth)            │
│   ├── Postgres (transactions, categories)    │
│   ├── Storage (uploaded PDFs)                │
│   └── Row-Level Security (tenant isolation)  │
└──────────────────────────────────────────────┘
```

## Key Design Decisions

- **Streamlit**: Chosen for speed of iteration and data-centric UI. Trade-off: limited customization vs traditional frontend.
- **Pluggable parsers**: Each bank has its own parser class extending `BankParser`. Pure functions: text in, transactions out.
- **Supabase**: Managed Postgres + Auth + Storage. Eliminates need for separate auth and DB services.
- **Session state (MVP)**: Transactions stored in `st.session_state` before Supabase integration. Will migrate to persistent DB.

## Data Flow

1. User uploads PDF → `BankParser.extract_pdf_text()` → raw text
2. Bank-specific parser → `list[Transaction]`
3. Category rules applied → DataFrame with categories
4. Stored in session state (MVP) / Supabase (production)
5. Pages read from session state / Supabase for display

## Directory Layout

See `CLAUDE.md` for full conventions.
