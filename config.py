"""
Configuration from environment variables.
Supports .env via python-dotenv.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent / ".env")


def get_telegram_token() -> str:
    """Telegram Bot token (from @BotFather)."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    if not token or ":" not in token:
        raise ValueError("Set TELEGRAM_BOT_TOKEN or TELEGRAM_TOKEN in .env")
    return token


def get_google_sheet_id() -> str:
    """Google Spreadsheet ID (from the sheet URL)."""
    sheet_id = os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID") or os.environ.get("GOOGLE_SHEET_ID")
    if not sheet_id:
        raise ValueError("Set GOOGLE_SHEETS_SPREADSHEET_ID or GOOGLE_SHEET_ID in .env")
    return sheet_id


def get_rates_sheet_name() -> str:
    """Name of the sheet/tab with Currency and Rate to EUR (for Amount EUR formula). Matches 'ExchangeRates' tab."""
    return os.environ.get("GOOGLE_SHEETS_RATES_SHEET") or "ExchangeRates"


def get_google_credentials():
    """
    Google Service Account credentials.
    Supports:
    - GOOGLE_SERVICE_ACCOUNT_JSON: JSON string in .env (e.g. for Railway)
    - GOOGLE_SERVICE_ACCOUNT_FILE: path to JSON file
    """
    import json
    from google.oauth2.service_account import Credentials

    json_str = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if json_str:
        try:
            info = json.loads(json_str)
            return Credentials.from_service_account_info(info)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid GOOGLE_SERVICE_ACCOUNT_JSON: {e}")

    path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    if path and os.path.isfile(path):
        return Credentials.from_service_account_file(path)

    raise ValueError(
        "Set GOOGLE_SERVICE_ACCOUNT_JSON (JSON string) or "
        "GOOGLE_SERVICE_ACCOUNT_FILE (path) in .env"
    )
