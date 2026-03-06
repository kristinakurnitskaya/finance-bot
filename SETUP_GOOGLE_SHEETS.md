# Konfiguracja bota z Google Sheets

Bot zapisuje transakcje do arkusza **Transactions** w Google Sheets zamiast Notion.

---

## 1. Utwórz Service Account w Google Cloud

1. Wejdź na [console.cloud.google.com](https://console.cloud.google.com).
2. Utwórz nowy projekt (lub wybierz istniejący).
3. **APIs & Services** → **Library** → włącz **Google Sheets API**.
4. **APIs & Services** → **Credentials** → **Create credentials** → **Service account**.
5. Nadaj nazwę (np. `finance-bot`), **Create and Continue**, **Done**.
6. Kliknij w utworzony service account → zakładka **Keys**.
7. **Add Key** → **Create new key** → **JSON** → **Create**. Pobierze się plik JSON (klucz prywatny – nie udostępniaj).

---

## 2. Udostępnij arkusz service accountowi

1. Otwórz swój arkusz „Finance Tracker” (Family Finance System) w Google Sheets.
2. Kliknij **Udostępnij** (Share).
3. Wklej **adres e-mail** z JSON (np. `finance-bot@twoj-projekt.iam.gserviceaccount.com`).
4. Uprawnienia: **Editor** (może edytować).
5. **Wyślij**.

---

## 3. Skopiuj Spreadsheet ID

Z adresu arkusza w przeglądarce:

```
https://docs.google.com/spreadsheets/d/1ABC...XYZ/edit
                                       ^^^^^^^^^^^^
                                       to jest ID
```

Skopiuj fragment między `/d/` a `/edit`.

---

## 4. Skonfiguruj .env

1. Otwórz plik `.env` w projekcie (albo utwórz z `.env.example`).
2. Dodaj/zmień:

```
TELEGRAM_BOT_TOKEN=twoj_token_z_botfather
GOOGLE_SHEETS_SPREADSHEET_ID=1ABC...XYZ
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account", ...cała zawartość JSON...}
```

Dla `GOOGLE_SERVICE_ACCOUNT_JSON`:
- Otwórz pobrany plik JSON w edytorze.
- Skopiuj **całą** zawartość (od `{` do `}`).
- Wklej jako jedną linię (możesz usunąć entery i zbędne spacje).
- Opakuj w cudzysłów, jeśli wartość zawiera znaki specjalne – w `.env` zwykle nie trzeba, bo nie ma spacji.

**Uwaga:** Na Railway w **Variables** wklej JSON jako wartość zmiennej `GOOGLE_SERVICE_ACCOUNT_JSON` – całość w jednej linii (minified JSON).

---

## 5. Uruchom bota

```bash
pip install -r requirements.txt
python bot.py
```

Wyślij do bota w Telegramie kwotę (np. `10`), wybierz typ, kategorię, konto – transakcja powinna pojawić się w arkuszu **Transactions**.

---

## Kolumny w arkuszu Transactions

Bot dopisuje wiersze z kolumnami:
- **A**: Data (YYYY-MM-DD)
- **B**: Type (Expense, Income, Transfer, Investment)
- **C**: Category
- **D**: Account
- **E**: Amount (dodatni dla Expense/Income/Investment – typ w kolumnie B; Transfer = 2 wiersze: outflow -X, inflow +X)
- **F**: Currency (domyślnie EUR)
- **G**: Amount_EUR (formuła – bot uzupełnia automatycznie)
- **H**: Note
- **I**: Month (formuła)
- **J**: Year (formuła)

Kontakty muszą zgadzać się z listą w arkuszu **Accounts** (Revolut Paolo, Santander Kris itd.).
