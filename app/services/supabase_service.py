"""Service for persisting data to Supabase.

Wraps Supabase queries for transactions, categories, imports, and profiles.
All queries are scoped to the current user via RLS.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
from supabase import Client

# --- Profiles ---


def ensure_profile(client: Client, user_id: str, email: str) -> dict:
    """Create user profile if it doesn't exist. Return the profile."""
    result = client.table("profiles").select("*").eq("id", user_id).execute()
    if result.data:
        return result.data[0]

    profile = {"id": user_id, "display_name": email.split("@")[0], "currency": "EUR"}
    client.table("profiles").insert(profile).execute()
    return profile


# --- Categories ---


def get_categories(client: Client, user_id: str) -> list[dict]:
    """Get all categories for a user."""
    result = client.table("categories").select("*").eq("user_id", user_id).order("name").execute()
    return result.data


def create_category(client: Client, user_id: str, name: str, color: str) -> dict:
    """Create a new category."""
    result = (
        client.table("categories")
        .insert({"user_id": user_id, "name": name, "color": color})
        .execute()
    )
    return result.data[0]


def seed_default_categories(client: Client, user_id: str) -> list[dict]:
    """Seed default categories for a new user if they have none."""
    existing = get_categories(client, user_id)
    if existing:
        return existing

    from app.services.category_service import DEFAULT_CATEGORIES

    rows = [
        {"user_id": user_id, "name": c["name"], "color": c["color"]} for c in DEFAULT_CATEGORIES
    ]
    result = client.table("categories").insert(rows).execute()
    return result.data


def delete_category(client: Client, category_id: str) -> None:
    """Delete a category."""
    client.table("categories").delete().eq("id", category_id).execute()


# --- Category Rules ---


def get_category_rules(client: Client, user_id: str) -> list[dict]:
    """Get all category rules for a user, joined with category name."""
    result = (
        client.table("category_rules")
        .select("*, categories(name)")
        .eq("user_id", user_id)
        .order("priority", desc=True)
        .execute()
    )
    return result.data


def create_category_rule(
    client: Client, user_id: str, category_id: str, match_pattern: str, priority: int = 0
) -> dict:
    """Create a new category rule."""
    result = (
        client.table("category_rules")
        .insert(
            {
                "user_id": user_id,
                "category_id": category_id,
                "match_pattern": match_pattern,
                "priority": priority,
            }
        )
        .execute()
    )
    return result.data[0]


# --- Imports ---


def create_import(
    client: Client,
    user_id: str,
    file_name: str,
    bank_account_id: str | None = None,
) -> dict:
    """Create an import record."""
    result = (
        client.table("imports")
        .insert(
            {
                "user_id": user_id,
                "file_name": file_name,
                "bank_account_id": bank_account_id,
                "status": "processing",
            }
        )
        .execute()
    )
    return result.data[0]


def update_import_status(
    client: Client, import_id: str, status: str, row_count: int = 0, error: str | None = None
) -> None:
    """Update import status after processing."""
    update: dict[str, Any] = {"status": status, "row_count": row_count}
    if error:
        update["error_message"] = error
    client.table("imports").update(update).eq("id", import_id).execute()


# --- Transactions ---


def save_transactions(
    client: Client,
    user_id: str,
    import_id: str,
    transactions_df: pd.DataFrame,
    bank_account_id: str | None = None,
) -> int:
    """Save parsed transactions to Supabase.

    Returns the number of rows inserted.
    """
    if transactions_df.empty:
        return 0

    rows = []
    for _, row in transactions_df.iterrows():
        rows.append(
            {
                "user_id": user_id,
                "import_id": import_id,
                "bank_account_id": bank_account_id,
                "date": (
                    str(row["date"].date()) if hasattr(row["date"], "date") else str(row["date"])
                ),
                "description": row["description"],
                "trx_type": row.get("trx_type", ""),
                "amount": float(row["amount"]),
                "balance": float(row["balance"]) if pd.notna(row.get("balance")) else None,
                "category_id": row.get("category_id"),
            }
        )

    # Insert in batches of 500 (Supabase limit)
    batch_size = 500
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        client.table("transactions").insert(batch).execute()

    return len(rows)


def get_transactions(
    client: Client,
    user_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
    category_id: str | None = None,
    limit: int = 1000,
) -> pd.DataFrame:
    """Fetch transactions from Supabase as a DataFrame."""
    query = (
        client.table("transactions")
        .select("*, categories(name, color)")
        .eq("user_id", user_id)
        .order("date", desc=True)
        .limit(limit)
    )

    if start_date:
        query = query.gte("date", start_date)
    if end_date:
        query = query.lte("date", end_date)
    if category_id:
        query = query.eq("category_id", category_id)

    result = query.execute()

    if not result.data:
        return pd.DataFrame(
            columns=["date", "description", "trx_type", "amount", "balance", "category"]
        )

    df = pd.DataFrame(result.data)
    # Flatten the joined category name
    if "categories" in df.columns:
        df["category"] = df["categories"].apply(lambda c: c["name"] if c else "Outros")
        df = df.drop(columns=["categories"])
    return df


# --- Bank Accounts ---


def get_bank_accounts(client: Client, user_id: str) -> list[dict]:
    """Get all bank accounts for a user."""
    result = (
        client.table("bank_accounts")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at")
        .execute()
    )
    return result.data


def create_bank_account(client: Client, user_id: str, bank_name: str, account_label: str) -> dict:
    """Create a new bank account."""
    result = (
        client.table("bank_accounts")
        .insert(
            {
                "user_id": user_id,
                "bank_name": bank_name,
                "account_label": account_label,
            }
        )
        .execute()
    )
    return result.data[0]
