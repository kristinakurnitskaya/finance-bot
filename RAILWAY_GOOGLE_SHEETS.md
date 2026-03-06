# Deploy bota na Railway z Google Sheets

Jeśli bot jest na Railway, **Telegram wysyła wszystkie wiadomości do Railway**, nie do laptopa. Musisz zaktualizować konfigurację na Railway.

---

## Krok 1: Zaktualizuj zmienne na Railway

1. Wejdź na **[railway.app](https://railway.app)** → swój projekt → serwis bota.
2. Zakładka **Variables** (lub **Settings** → Variables).
3. **Usuń** stare zmienne Notion:
   - `NOTION_SECRET`
   - `NOTION_EXPENSES_DATABASE_ID`
   - `NOTION_INCOME_DATABASE_ID`
   - `NOTION_ACCOUNTS_DATABASE_ID`
   - `NOTION_CATEGORIES_DATABASE_ID`
   - `NOTION_TRANSFERS_DATABASE_ID`

4. **Dodaj** zmienne Google Sheets:

| Nazwa | Wartość |
|-------|---------|
| `TELEGRAM_BOT_TOKEN` | (bez zmian – ten sam co masz) |
| `GOOGLE_SHEETS_SPREADSHEET_ID` | ID arkusza (np. `1uawVJD9ksJa1oz3C9gKhubwMMgxCzO94Xlk_1EbcoR0`) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | **Cała** zawartość pliku JSON konta serwisowego w jednej linii |

5. Dla `GOOGLE_SERVICE_ACCOUNT_JSON`:
   - Otwórz plik JSON z Google Cloud (np. `finance-bot-489413-xxx.json`)
   - Skopiuj **całość** od `{` do `}`
   - Usuń entery – ma być jedna długa linia
   - Wklej jako wartość zmiennej (Railway przyjmuje długie wartości)

6. **Zapisz** – Railway zrobi redeploy.

---

## Krok 2: Wypchnij kod na GitHub

Aby Railway miał aktualny kod (Google Sheets zamiast Notion):

```bash
cd "/Users/kristina/Desktop/finance bot"
git add .
git commit -m "Migracja na Google Sheets"
git push origin main
```

(Railway sam wykryje push i zrobi nowy deploy.)

---

## Krok 3: Sprawdź Logi

1. Railway → Deployments → ostatni deployment → **View Logs**
2. Powinno być: `Bot uruchomiony. Wyślij /start do bota w Telegramie.`
3. Brak błędów o Notion ani `GOOGLE_SERVICE_ACCOUNT_JSON nie jest ustawiony`

---

## Krok 4: Zatrzymaj bota na laptopie

Jeśli uruchamiasz bota lokalnie, **zatrzymaj go** (Ctrl+C). Niech działa tylko Railway – unikniesz konfliktów.

---

## Podsumowanie

- **Railway** = bot działa 24/7, odbiera wszystkie wiadomości z Telegrama
- **Laptop** = bot działa tylko gdy jest włączony i terminal otwarty
- Przy jednym tokenie Telegram wysyła aktualizacje do **jednego** klienta – ten, który polluje (zazwyczaj Railway)
