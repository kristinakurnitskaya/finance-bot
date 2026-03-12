"""
Google Sheets API – append transactions to the Transactions sheet.
Uses Service Account credentials from config.
Columns: Date, Type, Category, Account, Amount, Currency, Amount EUR, Note, Month, Year.
Amount EUR is a formula (VLOOKUP from the Rates sheet). Month/Year from date.
"""
from datetime import date
from typing import Any, Optional

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

import config

SHEET_NAME = "Transactions"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Column order: A=Date, B=Type, C=Category, D=Account, E=Amount, F=Currency, G=Amount EUR, H=Note, I=Month, J=Year
COLUMNS = ["Date", "Type", "Category", "Account", "Amount", "Currency", "Amount EUR", "Note", "Month", "Year"]


def _get_sheet_id() -> str:
    return config.get_google_sheet_id()


def _get_credentials() -> Credentials:
    return config.get_google_credentials()


def _get_service():
    """Build Sheets API v4 service."""
    creds = _get_credentials()
    return build("sheets", "v4", credentials=creds)


def _date_str(transaction_date) -> str:
    """ISO date (YYYY-MM-DD) so MONTH(), DATEVALUE() etc. work in Sheets."""
    d = transaction_date or date.today()
    if hasattr(d, "strftime"):
        return d.strftime("%Y-%m-%d")
    return str(d)


def _date_parts(transaction_date) -> tuple[str, int, int]:
    """Return (date_str, month, year) for the given date."""
    d = transaction_date or date.today()
    if not hasattr(d, "month"):
        d = date.today()
    return _date_str(d), getattr(d, "month", date.today().month), getattr(d, "year", date.today().year)


def _get_next_row() -> int:
    """Return the 1-based row index of the next row to append (after existing data)."""
    service = _get_service()
    sheet_id = _get_sheet_id()
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=f"'{SHEET_NAME}'!A:A")
        .execute()
    )
    values = result.get("values") or []
    return len(values) + 1


# Italian month names for column I (no red error styling, works with dashboard)
MONTHS_IT = (
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"
)


def _amount_eur_formula(row: int) -> str:
    """Amount EUR. Semicolons for locale (PL/RU); range $A$2:$B$100; same as your working formula."""
    rates_sheet = config.get_rates_sheet_name()
    ref = f"'{rates_sheet}'!$A$2:$B$100"
    # Use semicolons (;) so formula works in Polish/Russian locale
    return f"=IF(E{row}=\"\";\"\";E{row}*VLOOKUP(F{row};{ref};2;FALSE))"


def _build_row(
    row_index: int,
    date_str: str,
    type_val: str,
    category: str,
    account: str,
    amount: float,
    currency: str,
    note: str,
    month_italian: str,
    year: int,
) -> list:
    """Plain values only (no formatting). Month = Italian name for dashboard."""
    return [
        date_str,
        str(type_val).strip(),
        str(category).strip(),
        str(account).strip(),
        amount,
        str(currency).strip(),
        _amount_eur_formula(row_index),
        str(note)[:500].strip(),
        month_italian,
        year,
    ]


def append_transaction(data: dict[str, Any]) -> bool:
    """
    Append one transaction. Plain values; Month in Italian; Amount EUR formula with IFERROR.
    """
    date_str, month_num, year = _date_parts(data.get("date"))
    month_italian = MONTHS_IT[month_num - 1] if 1 <= month_num <= 12 else ""
    next_row = _get_next_row()
    row = _build_row(
        next_row,
        date_str,
        data.get("type", ""),
        data.get("category", ""),
        data.get("account", ""),
        data.get("amount", 0),
        data.get("currency", "EUR"),
        data.get("note", ""),
        month_italian,
        year,
    )
    return _append_rows([row])


def append_transfer(
    from_account: str,
    to_account: str,
    amount: float,
    currency: str = "EUR",
    transaction_date: Optional[Any] = None,
    note: str = "",
) -> bool:
    """
    Append a transfer as two rows: outflow from source, inflow to destination.
    Each row has Amount EUR formula and Month, Year.
    """
    date_str, month_num, year = _date_parts(transaction_date)
    month_italian = MONTHS_IT[month_num - 1] if 1 <= month_num <= 12 else ""
    note_trimmed = (note or "")[:500]
    next_row = _get_next_row()
    row_out = _build_row(
        next_row,
        date_str,
        "Transfer",
        "Transfer Out",
        from_account,
        -abs(float(amount)),
        currency,
        note_trimmed,
        month_italian,
        year,
    )
    row_in = _build_row(
        next_row + 1,
        date_str,
        "Transfer",
        "Transfer In",
        to_account,
        abs(float(amount)),
        currency,
        note_trimmed,
        month_italian,
        year,
    )
    return _append_rows([row_out, row_in])


def _append_rows(rows: list[list]) -> bool:
    """Write data into the next row(s) without inserting new rows (so formulas keep working)."""
    if not rows:
        return True
    service = _get_service()
    sheet_id = _get_sheet_id()
    start_row = _get_next_row()
    for i, row in enumerate(rows):
        r = start_row + i
        range_str = f"'{SHEET_NAME}'!A{r}:J{r}"
        body = {"values": [row]}
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=range_str,
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()
    return True


# --- Read lists from sheet (same as dropdowns) ---

def get_accounts_from_sheet() -> list[str]:
    """Account names from Accounts sheet column A (same as dropdown in Transactions)."""
    try:
        service = _get_service()
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=_get_sheet_id(), range="Accounts!A2:A100")
            .execute()
        )
        values = result.get("values") or []
        out = [str(r[0]).strip() for r in values if r and str(r[0]).strip()]
        return out if out else []
    except Exception:
        return []


def get_categories_from_sheet() -> list[str]:
    """Expense categories from Dashboard A27:A50 (same order as dropdown)."""
    try:
        service = _get_service()
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=_get_sheet_id(), range="Dashboard!A27:A50")
            .execute()
        )
        values = result.get("values") or []
        out = [str(r[0]).strip() for r in values if r and str(r[0]).strip()]
        return out if out else []
    except Exception:
        return []


def get_income_categories_from_sheet() -> list[str]:
    """Income categories from Dashboard G27:G30."""
    try:
        service = _get_service()
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=_get_sheet_id(), range="Dashboard!G27:G30")
            .execute()
        )
        values = result.get("values") or []
        out = [str(r[0]).strip() for r in values if r and str(r[0]).strip()]
        return out if out else []
    except Exception:
        return []


def get_loans_from_sheet() -> list[str]:
    """Loan names from Loans sheet column A (for Loan Payment – which loan to pay)."""
    try:
        service = _get_service()
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=_get_sheet_id(), range="Loans!A2:A50")
            .execute()
        )
        values = result.get("values") or []
        out = [str(r[0]).strip() for r in values if r and str(r[0]).strip()]
        return out if out else []
    except Exception:
        return []
