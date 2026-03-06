"""
Zapis transakcji do arkusza Transactions w Google Sheets.
Kolumny: A=Date, B=Type, C=Category, D=Account, E=Amount, F=Currency, G=Amount_EUR, H=Note, I=Month, J=Year.
Bot uzupełnia A-F i H. G, I, J są formułami – uzupełniamy przy appendzie.
"""
import os
import json
import time
from datetime import date
from typing import Optional

import httplib2
from google_auth_httplib2 import AuthorizedHttp
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
TIMEOUT_SEC = 90
MAX_RETRIES = 2


def _get_service():
    """Tworzy klienta Google Sheets API z credentials z .env (timeout 90s)."""
    creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not creds_json:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON nie jest ustawiony w .env")
    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    http = AuthorizedHttp(creds, http=httplib2.Http(timeout=TIMEOUT_SEC))
    return build("sheets", "v4", http=http, cache_discovery=False)


def _execute_with_retry(request):
    """Wykonuje request z retry przy timeout (do 2 ponowień)."""
    last_err = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            return request.execute()
        except Exception as e:
            err_str = str(e).lower()
            if "timeout" in err_str or "timed out" in err_str:
                last_err = e
                if attempt < MAX_RETRIES:
                    time.sleep(2)
                    continue
            raise
    if last_err:
        raise last_err


def _append_row(
    service,
    spreadsheet_id: str,
    sheet_name: str,
    values: list,
    formulas: Optional[dict] = None,
) -> int:
    """
    Dopisuje wiersz do arkusza. values = [A, B, C, D, E, F, H] (bez G, I, J – to formuły).
    Zwraca numer wiersza, do którego dopisano.
    """
    sheets = service.spreadsheets()

    # Pobierz ostatni wiersz z danymi
    result = _execute_with_retry(
        sheets.values()
        .get(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_name}'!A:A",
        )
    )
    rows = result.get("values", [])
    next_row = len(rows) + 1

    # A–F to kolumny 0–5, H to kolumna 7. G=6, I=8, J=9 – formuły
    # values: [Date, Type, Category, Account, Amount, Currency] + [Note]
    row_data = values[:6] + [""] + [values[6] if len(values) > 6 else ""]  # G puste, H=Note
    range_str = f"'{sheet_name}'!A{next_row}:H{next_row}"
    body = {"values": [row_data]}
    _execute_with_retry(
        sheets.values().update(
            spreadsheetId=spreadsheet_id,
            range=range_str,
            valueInputOption="USER_ENTERED",
            body=body,
        )
    )

    # Uzupełnij formuły G, I, J
    if next_row >= 2:
        if formulas is None:
            # G = Amount_EUR: dla EUR = E, inaczej VLOOKUP (fallback dla braku EUR w ExchangeRates)
            formulas = {
                f"G{next_row}": f'=IF(E{next_row}="","",IF(UPPER(F{next_row})="EUR",E{next_row},E{next_row}*IFERROR(VLOOKUP(F{next_row},ExchangeRates!$A$2:$B$100,2,FALSE),1)))',
                f"I{next_row}": f'=IF(A{next_row}="","",TEXT(A{next_row},"MMMM"))',
                f"J{next_row}": f'=IF(A{next_row}="","",YEAR(A{next_row}))',
            }
        up_body = {
            "data": [
                {
                    "range": f"'{sheet_name}'!{cell}",
                    "values": [[formula]],
                }
                for cell, formula in formulas.items()
            ],
            "valueInputOption": "USER_ENTERED",
        }
        _execute_with_retry(
            sheets.values().batchUpdate(spreadsheetId=spreadsheet_id, body=up_body)
        )

    return next_row


def append_expense(
    category: str,
    account: str,
    amount: float,
    note: str = "",
    transaction_date: Optional[date] = None,
) -> bool:
    """Dopisuje wydatek (Type=Expense, Amount dodatni – typ w kolumnie Type)."""
    if transaction_date is None:
        transaction_date = date.today()
    spreadsheet_id = os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID")
    sheet_name = os.environ.get("GOOGLE_SHEETS_TRANSACTIONS_SHEET", "Transactions")
    if not spreadsheet_id:
        raise ValueError("GOOGLE_SHEETS_SPREADSHEET_ID nie jest ustawiony")
    service = _get_service()
    amt = abs(amount)
    values = [
        transaction_date.isoformat(),
        "Expense",
        category,
        account,
        amt,
        "EUR",
        (note or "Transazione")[:500],
    ]
    _append_row(service, spreadsheet_id, sheet_name, values)
    return True


def append_income(
    category: str,
    account: str,
    amount: float,
    income_source: str = "Salary",
    note: str = "",
    transaction_date: Optional[date] = None,
) -> bool:
    """Dopisuje przychód (Type=Income, Amount dodatni)."""
    if transaction_date is None:
        transaction_date = date.today()
    spreadsheet_id = os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID")
    sheet_name = os.environ.get("GOOGLE_SHEETS_TRANSACTIONS_SHEET", "Transactions")
    if not spreadsheet_id:
        raise ValueError("GOOGLE_SHEETS_SPREADSHEET_ID nie jest ustawiony")
    service = _get_service()
    amt = abs(amount)
    # Category w Income = Income Source (Salary, Sales, Gifts, From Parents)
    values = [
        transaction_date.strftime("%d.%m.%Y"),
        "Income",
        income_source,
        account,
        amt,
        "EUR",
        (note or "Entrata")[:500],
    ]
    _append_row(service, spreadsheet_id, sheet_name, values)
    return True


def append_investment(
    category: str,
    account: str,
    amount: float,
    note: str = "",
    transaction_date: Optional[date] = None,
) -> bool:
    """Dopisuje inwestycję (Type=Investment, Amount dodatni – rozróżnienie przez Type)."""
    if transaction_date is None:
        transaction_date = date.today()
    spreadsheet_id = os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID")
    sheet_name = os.environ.get("GOOGLE_SHEETS_TRANSACTIONS_SHEET", "Transactions")
    if not spreadsheet_id:
        raise ValueError("GOOGLE_SHEETS_SPREADSHEET_ID nie jest ustawiony")
    service = _get_service()
    amt = abs(amount)
    values = [
        transaction_date.strftime("%d.%m.%Y"),
        "Investment",
        category,
        account,
        amt,
        "EUR",
        (note or "Investimento")[:500],
    ]
    _append_row(service, spreadsheet_id, sheet_name, values)
    return True


def append_transfer(
    from_account: str,
    to_account: str,
    amount: float,
    note: str = "",
    transaction_date: Optional[date] = None,
) -> bool:
    """Dopisuje transfer – dwa wiersze: outflow (-) z from, inflow (+) do to."""
    if transaction_date is None:
        transaction_date = date.today()
    spreadsheet_id = os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID")
    sheet_name = os.environ.get("GOOGLE_SHEETS_TRANSACTIONS_SHEET", "Transactions")
    if not spreadsheet_id:
        raise ValueError("GOOGLE_SHEETS_SPREADSHEET_ID nie jest ustawiony")
    service = _get_service()
    amt = abs(amount)
    note_val = (note or "Trasferimento")[:500]

    # Wiersz 1: -amount z from_account (outflow)
    values1 = [
        transaction_date.isoformat(),
        "Transfer",
        "Transfer",
        from_account,
        -amt,
        "EUR",
        note_val,
    ]
    _append_row(service, spreadsheet_id, sheet_name, values1)

    # Wiersz 2: +amount do to_account
    values2 = [
        transaction_date.strftime("%d.%m.%Y"),
        "Transfer",
        "Transfer",
        to_account,
        amt,
        "EUR",
        note_val,
    ]
    _append_row(service, spreadsheet_id, sheet_name, values2)
    return True
