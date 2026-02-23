# Deploy bota na Render

Bot musi działać jako **Background Worker** (proces w tle), żeby cały czas odbierał wiadomości z Telegrama. Na darmowym planie Render **Web Services** usypiają po ~15 min – do bota nadającego się do użytku potrzebny jest **Background Worker** (płatny, ok. 7 USD/mies.) albo inna platforma z darmowym workerem (np. Railway).

---

## Krok 1: Projekt w GitHub

1. Załóż repozytorium na [github.com](https://github.com) (np. `finance-bot`).
2. W terminalu w folderze projektu:

```bash
cd "/Users/kristina/Desktop/finance bot"
git init
git add .
git commit -m "Finance bot + Notion"
git branch -M main
git remote add origin https://github.com/TWOJA_NAZWA/finance-bot.git
git push -u origin main
```

(Zamień `TWOJA_NAZWA` i `finance-bot` na swoje repo. **Nie** commituj pliku `.env` – jest w `.gitignore`.)

---

## Krok 2: Render – nowy Background Worker

1. Wejdź na [dashboard.render.com](https://dashboard.render.com/).
2. **New +** → **Background Worker**.
3. **Connect a repository** → wybierz GitHub i repozytorium z botem (np. `finance-bot`).
4. Ustaw:
   - **Name:** `finance-bot` (dowolna nazwa).
   - **Environment:** `Python 3`.
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
   - **Plan:** wybierz plan (np. płatny, jeśli chcesz workera 24/7).

---

## Krok 3: Zmienne środowiskowe (Environment Variables)

W Render: w ustawieniach workera → **Environment** → **Add Environment Variable**. Dodaj **każdą** z poniższych (wartości skopiuj ze swojego `.env`):

| Key | Gdzie wziąć wartość |
|-----|----------------------|
| `TELEGRAM_BOT_TOKEN` | Token z @BotFather |
| `NOTION_SECRET` | Notion → My integrations → Internal Integration Secret |
| `NOTION_EXPENSES_DATABASE_ID` | ID bazy Expenses (32 znaki) |
| `NOTION_INCOME_DATABASE_ID` | ID bazy Incomes |
| `NOTION_ACCOUNTS_DATABASE_ID` | ID bazy Accounts |
| `NOTION_CATEGORIES_DATABASE_ID` | ID bazy Categories |
| `NOTION_TRANSFERS_DATABASE_ID` | ID bazy Transfers |

Wartości **nie** mogą być puste. Skopiuj je z lokalnego pliku `.env`.

---

## Krok 4: Deploy

1. Kliknij **Create Background Worker**.
2. Render zbuduje projekt i uruchomi `python bot.py`.
3. W zakładce **Logs** zobaczysz logi bota (np. „Bot uruchomiony…”).
4. Wyślij wiadomość do bota w Telegramie – powinien odpowiadać.

---

## Ważne

- **Płatny plan:** Background Worker na Render jest płatny (ok. 7 USD/mies.). Darmowe są tylko Web Services, które usypiają – nie nadają się do bota z pollingiem.
- **Aktualizacje:** po zmianach w kodzie zrób `git add .` → `git commit -m "opis"` → `git push`. Render sam zrobi nowy deploy.
- **Logi i błędy:** w Render → Twój worker → **Logs**. Tam zobaczysz ewentualne błędy Notion/Telegram.

---

## Alternatywa: Railway (darmowy limit)

Na [railway.app](https://railway.app) możesz uruchomić ten sam projekt (New Project → Deploy from GitHub). Railway ma darmowy miesięczny limit – po jego wykorzystaniu trzeba doładować kredyty. Start command: `python bot.py`; zmienne środowiskowe ustaw w zakładce **Variables**.
