# Database Schema

See `supabase/migrations/001_initial_schema.sql` for the full schema.

## Tables

- **profiles** - User profiles (extends Supabase Auth)
- **bank_accounts** - User's bank accounts (CGD, Activo Bank, Millennium)
- **imports** - Track uploaded PDF files and their processing status
- **categories** - User-defined spending categories with colors
- **category_rules** - Pattern-matching rules for auto-categorization
- **transactions** - Parsed transactions from bank statements

## Key Relationships

```
profiles 1──* bank_accounts
profiles 1──* categories
profiles 1──* imports
categories 1──* category_rules
bank_accounts 1──* transactions
imports 1──* transactions
categories 1──* transactions
```

## Row-Level Security

All tables enforce `user_id = auth.uid()` via Supabase RLS policies.
