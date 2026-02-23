"""
Skrypt sprawdza, do jakich baz ma dostęp integracja Notion, i szuka Income.
Uruchom: python check_notion_income.py
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
token = os.environ.get("NOTION_SECRET")
if not token:
    print("Brak NOTION_SECRET w .env")
    exit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}

# 1) Lista wszystkich baz dostępnych dla integracji
print("Szukam baz dostępnych dla integracji...\n")
resp = requests.post(
    f"{NOTION_API}/search",
    headers=headers,
    json={"filter": {"property": "object", "value": "database"}},
    timeout=10,
)
if not resp.ok:
    print(f"Błąd search: {resp.status_code}\n{resp.text}")
    exit(1)

data = resp.json()
results = data.get("results", [])
print(f"Znaleziono {len(results)} baz(ę/y):\n")
for r in results:
    db_id = r.get("id", "").replace("-", "")
    title = "?"
    raw_title = r.get("title")
    if isinstance(raw_title, list) and raw_title:
        title = raw_title[0].get("plain_text", "?")
    elif isinstance(raw_title, dict):
        arr = raw_title.get("title") or raw_title.get("rich_text") or []
        title = arr[0].get("plain_text", "?") if arr else "?"
    print(f"  ID:   {db_id}")
    print(f"  Tytuł: {title}")
    print()

# 2) Próba bezpośredniego odczytu bazy Income (ID z .env)
income_id = os.environ.get("NOTION_INCOME_DATABASE_ID", "").replace("-", "")
print(f"Próba GET database dla NOTION_INCOME_DATABASE_ID: {income_id}")
resp2 = requests.get(f"{NOTION_API}/databases/{income_id}", headers=headers, timeout=10)
if resp2.ok:
    print("  OK – integracja ma dostęp do tej bazy.")
else:
    print(f"  404 / błąd – integracja NIE ma dostępu: {resp2.status_code} {resp2.text[:200]}")
