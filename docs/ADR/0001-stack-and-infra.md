# ADR 0001: Stack and Infrastructure Choices

**Status**: Accepted
**Date**: 2026-04-11

## Context

Building a micro SaaS for personal finance analysis targeting Portuguese bank statements. Solo founder with data engineering background. Must be low-cost, AI-agent maintainable, and fast to iterate.

## Decisions

### Frontend: Streamlit
- **Why**: Working prototype already exists. Data-centric UI fits the use case. Fast iteration.
- **Trade-off**: Limited UI customization. May need to migrate to Next.js if consumer-facing features demand it.

### Database + Auth: Supabase
- **Why**: Managed Postgres + Auth + Storage in one service. Free tier (500MB). Row-Level Security for multi-tenancy.
- **Trade-off**: Vendor lock-in on auth. Mitigated by standard Postgres underneath.

### Hosting: Google Cloud Run
- **Why**: Docker containers, scales to zero, generous free tier. User has GCP experience.
- **Trade-off**: Cold starts for Streamlit apps. Acceptable for MVP.

### PDF Parsing: pypdf + custom regex
- **Why**: Already working for CGD. Lightweight, no external API dependencies.
- **Trade-off**: Fragile to PDF format changes. Each bank needs its own parser.

### Package Management: uv
- **Why**: Fast, modern, handles Python versions. Better than pip for reproducible builds.

### Infrastructure: Terraform
- **Why**: User's existing skill. Version-controlled infrastructure.

## Consequences

- All development runs in Docker containers (no local Python needed)
- Each bank parser is isolated and independently testable
- Supabase free tier limits: 500MB DB, 1GB storage, 50K monthly active users
