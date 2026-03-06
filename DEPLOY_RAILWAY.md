# Deploy bota na Railway

Bot będzie działał 24/7 jako worker. Railway ma **darmowy trial** (ok. 5 USD kredytu na start) i **1 USD darmowych kredytów miesięcznie** – dla małego bota zwykle starczy.

---

## Co musisz mieć

- Konto na **GitHub** (repo `finance-bot` już tam jest).
- Konto na **Railway** – założysz w kroku 1 (logowanie przez GitHub).

---

## Krok 1: Konto Railway

1. Wejdź na **[railway.app](https://railway.app)**.
2. Kliknij **„Login”** lub **„Start a New Project”**.
3. Zaloguj się przez **GitHub** („Login with GitHub”) – to jednocześnie zakłada konto i daje dostęp do repozytoriów.

---

## Krok 2: Nowy projekt z GitHub

1. Na dashboardzie Railway kliknij **„New Project”**.
2. Wybierz **„Deploy from GitHub repo”**.
3. Jeśli nie widzisz repozytoriów – **„Configure GitHub App”** i zezwól Railway na dostęp do konta (np. wybierz „All repositories” albo tylko `finance-bot`).
4. Wybierz repozytorium **`finance-bot`** (lub `kristinakurnitskaya/finance-bot`).
5. Railway utworzy **serwis** i zacznie pierwszy build (może chwilę potrwać).

---

## Krok 3: Ustawienie zmiennych środowiskowych (.env)

Bez tego bot się nie połączy z Telegramem ani Notion.

1. W projekcie kliknij **serwis** (jedna karta z nazwą repo / „finance-bot”).
2. Przejdź do zakładki **„Variables”** (lub **„Settings”** → **Variables**).
3. Kliknij **„Add Variable”** lub **„RAW Editor”** i wklej zmienne **jedna per linia** w formacie `NAZWA=wartość` (bez spacji wokół `=`):

```
TELEGRAM_BOT_TOKEN=twoj_token_z_botfather
NOTION_SECRET=twoj_notion_secret
NOTION_EXPENSES_DATABASE_ID=28450736c8d781c69e06c9b783ed4aed
NOTION_INCOME_DATABASE_ID=28450736c8d78129a189dd2594bfce91
NOTION_ACCOUNTS_DATABASE_ID=28450736c8d781838c14de070ca79e7e
NOTION_CATEGORIES_DATABASE_ID=28450736c8d78149994eca6f1bb1636d
NOTION_TRANSFERS_DATABASE_ID=28450736c8d781baa868f729b48567d9
```

4. Zamień wartości na **swoje** z lokalnego pliku `.env` (TELEGRAM_BOT_TOKEN, NOTION_SECRET i ewentualnie ID baz, jeśli się różnią).
5. Zapisz (np. **„Add”** / **„Update”**). Railway zrobi **redeploy** po zapisaniu zmiennych.

---

## Krok 4: Komenda startowa (worker)

W repozytorium jest już **Procfile** z wpisem `worker: python bot.py`. Railway może go wykryć automatycznie.

- Jeśli po deployu w **„Deployments”** widać, że serwis się uruchamia i w **„Logs”** są wpisy z bota (np. „Bot uruchomiony…”), **nic więcej nie ustawiaj**.
- Jeśli Railway szuka serwera WWW (błąd typu „no web process”) albo bot się nie uruchamia:

1. W serwisie wejdź w **„Settings”**.
2. Znajdź **„Build”** / **„Deploy”** i pole **„Start Command”** (lub **„Custom Start Command”**).
3. Ustaw:  
   `python bot.py`  
4. Zapisz – Railway zrobi ponowny deploy.

---

## Krok 5: Sprawdzenie w Telegramie

1. W Railway w swoim serwisie otwórz **„Logs”** (zakładka **Deployments** → kliknij ostatni deployment → **View Logs**).
2. Powinny być wpisy z uruchomienia bota (bez czerwonych błędów).
3. W Telegramie wyślij do bota **/start** lub kwotę – bot powinien odpowiadać.

---

## Przydatne informacje

- **Redeploy:** po pushu do GitHub (gałąź podłączona do projektu) Railway sam robi nowy deploy.
- **Logi:** **Deployments** → wybrany deployment → **View Logs**.
- **Koszty:** trial + 1 USD/mies. darmowych kredytów; mały worker zwykle mieści się w limicie. W **Dashboard** → **Usage** / **Billing** zobaczysz zużycie.
- **Jeśli bot nie startuje:** sprawdź Logs (błąd Notion/Telegram?), potem Variables – czy wszystkie zmienne są ustawione i bez literówek.

---

## Krótka checklista

1. Zaloguj się na Railway przez GitHub.
2. New Project → Deploy from GitHub repo → wybierz `finance-bot`.
3. W serwisie: Variables → wklej/ustaw TELEGRAM_BOT_TOKEN, NOTION_SECRET i wszystkie NOTION_*_DATABASE_ID.
4. Jeśli trzeba: Settings → Start Command = `python bot.py`.
5. Sprawdź Logi i odpowiedź bota w Telegramie.
