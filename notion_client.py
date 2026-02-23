"""
Zapis transakcji do bazy Notion (Expenses).
Kolumny: Expense (Title = komentarz), Date, Category, Amount, Account.
Opcjonalnie: Type, Photo – jeśli są w bazie.
"""
import os
from datetime import date
from typing import Optional

import requests

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def _headers() -> dict:
    token = os.environ.get("NOTION_SECRET")
    if not token:
        raise ValueError("NOTION_SECRET nie jest ustawiony w .env")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


def _get_page_id_by_title(database_id: str, name: str) -> Optional[str]:
    """Znajduje ID strony w bazie Notion po nazwie (tytuł strony)."""
    resp = requests.post(
        f"{NOTION_API}/databases/{database_id}/query",
        headers=_headers(),
        json={"page_size": 100},
        timeout=30,
    )
    if not resp.ok:
        return None
    data = resp.json()
    name_clean = name.strip().lower()
    for page in data.get("results", []):
        props = page.get("properties", {})
        for key, val in props.items():
            if val.get("type") == "title":
                title_list = val.get("title") or []
                if title_list:
                    plain = (title_list[0].get("plain_text") or "").strip().lower()
                    if plain == name_clean:
                        return page.get("id")
                break
    return None


def _get_account_page_id(accounts_database_id: str, account_name: str) -> Optional[str]:
    return _get_page_id_by_title(accounts_database_id, account_name)


def create_expense(
    database_id: str,
    name: str,
    amount: float,
    transaction_type: str,
    category: str,
    account: str,
    description: Optional[str] = None,
    photo_url: Optional[str] = None,
    transaction_date: Optional[date] = None,
    accounts_database_id: Optional[str] = None,
    categories_database_id: Optional[str] = None,
) -> bool:
    """
    Tworzy wpis w bazie Expenses w Notion.
    Account i Category mogą być Relation – podaj accounts_database_id i categories_database_id.
    """
    if transaction_date is None:
        transaction_date = date.today()

    comment = (name or description or "").strip() or "—"

    # Account: Relation albo Select
    account_value = None
    if accounts_database_id:
        page_id = _get_page_id_by_title(accounts_database_id, account)
        if page_id:
            account_value = {"relation": [{"id": page_id}]}
    if account_value is None:
        account_value = {"select": {"name": account}}

    # Category: Relation albo Select
    category_value = None
    if categories_database_id:
        page_id = _get_page_id_by_title(categories_database_id, category)
        if page_id:
            category_value = {"relation": [{"id": page_id}]}
        else:
            raise RuntimeError(f"Nie znaleziono kategorii '{category}' w bazie Categories (Notion). Dodaj ją w Notion.")
    if category_value is None:
        category_value = {"select": {"name": category}}

    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Expense": {"title": [{"text": {"content": comment[:2000]}}]},
            "Date": {"date": {"start": transaction_date.isoformat()}},
            "Category": category_value,
            "Amount": {"number": round(amount, 2)},
            "Account": account_value,
        },
    }

    # Jeśli w Notion masz kolumny Type i Photo, odkomentuj:
    # payload["properties"]["Type"] = {"select": {"name": transaction_type}}
    # if photo_url:
    #     payload["properties"]["Photo"] = {"url": photo_url[:2000]}

    resp = requests.post(
        f"{NOTION_API}/pages",
        headers=_headers(),
        json=payload,
        timeout=30,
    )
    if not resp.ok:
        raise RuntimeError(f"Notion API error: {resp.status_code} {resp.text}")
    return True


def create_income(
    database_id: str,
    comment: str,
    amount: float,
    account: str,
    income_source: str,
    transaction_date: Optional[date] = None,
    accounts_database_id: Optional[str] = None,
) -> bool:
    """
    Tworzy wpis w bazie Income w Notion.
    Kolumny: Income (Title), Amount, Accounts (Relation!), Date, Income Source.
    """
    if transaction_date is None:
        transaction_date = date.today()
    title = (comment or "").strip() or "Entrata"

    # Accounts w Notion to Relation – szukamy page_id w bazie Accounts
    accounts_value = []
    if accounts_database_id:
        page_id = _get_account_page_id(accounts_database_id, account)
        if page_id:
            accounts_value = [{"id": page_id}]
    if not accounts_value:
        raise RuntimeError(f"Nie znaleziono konta '{account}' w bazie Accounts. Dodaj to konto w Notion (baza Accounts).")

    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Income": {"title": [{"text": {"content": title[:2000]}}]},
            "Amount": {"number": round(amount, 2)},
            "Accounts": {"relation": accounts_value},
            "Date": {"date": {"start": transaction_date.isoformat()}},
            "Income Source": {"select": {"name": income_source}},
        },
    }
    resp = requests.post(
        f"{NOTION_API}/pages",
        headers=_headers(),
        json=payload,
        timeout=30,
    )
    if not resp.ok:
        raise RuntimeError(f"Notion API error: {resp.status_code} {resp.text}")
    return True


def create_transfer(
    database_id: str,
    comment: str,
    amount: float,
    from_account: str,
    to_account: str,
    transaction_date: Optional[date] = None,
    accounts_database_id: Optional[str] = None,
) -> bool:
    """
    Tworzy wpis w bazie Transfers w Notion.
    Kolumny: Name (Title), Amount, From (Relation), To (Relation), Date.
    """
    if transaction_date is None:
        transaction_date = date.today()
    title = (comment or "").strip() or "Trasferimento"

    if not accounts_database_id:
        raise RuntimeError("NOTION_ACCOUNTS_DATABASE_ID richiesto per i trasferimenti.")
    from_id = _get_page_id_by_title(accounts_database_id, from_account)
    to_id = _get_page_id_by_title(accounts_database_id, to_account)
    if not from_id:
        raise RuntimeError(f"Nie znaleziono konta '{from_account}' w bazie Accounts.")
    if not to_id:
        raise RuntimeError(f"Nie znaleziono konta '{to_account}' w bazie Accounts.")

    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Transactions": {"title": [{"text": {"content": title[:2000]}}]},
            "Amount": {"number": round(amount, 2)},
            "From Account": {"relation": [{"id": from_id}]},
            "To Account": {"relation": [{"id": to_id}]},
            "Date": {"date": {"start": transaction_date.isoformat()}},
        },
    }
    resp = requests.post(
        f"{NOTION_API}/pages",
        headers=_headers(),
        json=payload,
        timeout=30,
    )
    if not resp.ok:
        raise RuntimeError(f"Notion API error: {resp.status_code} {resp.text}")
    return True
