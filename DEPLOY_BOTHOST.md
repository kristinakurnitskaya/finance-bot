# Jak wrzucić bota na Bothost.ru

Konto masz już założone. Poniżej kroki, żeby podłączyć repo z GitHub i uruchomić bota.

---

## Krok 1: Wejście na Bothost

1. Wejdź na **[bothost.ru](https://bothost.ru)** i **zaloguj się** (Login).
2. Powinnaś zobaczyć **panel / dashboard** (lista projektów lub „Nowy projekt”).

---

## Krok 2: Nowy projekt

1. Kliknij **„Новый проект”** / **„New Project”** / **„Создать проект”** (w zależności od wersji języka).
2. **Typ bota:** wybierz **Telegram** (albo „Python”, jeśli jest tylko lista języków).
3. **Nazwa projektu:** np. `finance-bot` – zapisz (OK / Create).

---

## Krok 3: Podłączenie kodu z GitHub

1. W ustawieniach projektu znajdź **„Подключить репозиторий”** / **„Connect repository”** / **„Git”** / **„GitHub”**.
2. Kliknij **„GitHub”** (albo GitLab, jeśli tam masz repo).
3. Jeśli pierwszy raz – **zezwoł Bothost na dostęp** do konta GitHub (wybierz „All repositories” albo tylko `finance-bot`).
4. **Wybierz repozytorium:** `kristinakurnitskaya/finance-bot` (albo jak się nazywa Twoje repo).
5. **Gałąź (branch):** zostaw `main` (albo `master`, jeśli tak masz).
6. Zapisz / **Connect**. Bothost powinien „zaciągnąć” kod i pokazać, że repo jest podłączone.

---

## Krok 4: Komenda startowa (jak uruchomić bota)

Bothost musi wiedzieć, co uruchomić. Szukaj w projekcie:

- **„Start Command”** / **„Команда запуска”** / **„Build & Run”** / **„Settings”** → **„Start”**.

Ustaw:

```text
python bot.py
```

Jeśli jest pole **„Build command”** (komenda budowania), możesz zostawić puste albo:

```text
pip install -r requirements.txt
```

Zapisz.  
*(Jeśli Bothost sam wykrywa Python i `requirements.txt`, może nie być potrzeby ustawiać build – wtedy wystarczy start: `python bot.py`.)*

---

## Krok 5: Zmienne środowiskowe (tokeny i Notion)

Bez tego bot nie połączy się z Telegramem ani Notion.

1. W projekcie znajdź **„Variables”** / **„Переменные окружения”** / **„Env”** / **„Environment”** (często w **Settings** projektu albo bota).
2. Dodaj zmienne **po jednej** (Add Variable / Добавить), w formacie **Name** = **Value** (bez spacji wokół `=`):

| Nazwa | Wartość (wklej swoje z lokalnego .env) |
|-------|----------------------------------------|
| `TELEGRAM_BOT_TOKEN` | token z @BotFather |
| `NOTION_SECRET` | secret z Notion (Integrations) |
| `NOTION_EXPENSES_DATABASE_ID` | ID bazy Expenses |
| `NOTION_INCOME_DATABASE_ID` | ID bazy Income |
| `NOTION_ACCOUNTS_DATABASE_ID` | ID bazy Accounts |
| `NOTION_CATEGORIES_DATABASE_ID` | ID bazy Categories |
| `NOTION_TRANSFERS_DATABASE_ID` | ID bazy Transfers |

3. Wszystkie wartości skopiuj z **lokalnego pliku `.env`** (te same co na Macu).
4. Zapisz (Save / Сохранить).

**Uwaga:** Na darmowym planie (Starter) czasem „Variables” są w płatnym (Basic). Jeśli nie widzisz takiej sekcji – napisz do supportu Bothost (Telegram: [@BothostSupport](https://t.me/bothostru)); albo przejdź na Basic (99 ₽/mies), gdzie env są w ofercie.

---

## Krok 6: Deploy (uruchomienie)

1. Kliknij **„Deploy”** / **„Развернуть”** / **„Запустить”** / **„Build and deploy”**.
2. Bothost zbuduje projekt (instalacja z `requirements.txt`) i uruchomi `python bot.py`.
3. Otwórz **„Logs”** / **„Логи”** – powinny pojawić się wpisy z bota (bez czerwonych błędów).

---

## Krok 7: Sprawdzenie w Telegramie

1. W Telegramie napisz do swojego bota **/start** albo wyślij kwotę (np. `10`).
2. Bot powinien odpowiedzieć (wybór typu: Spesa / Entrata itd.).

Jeśli nie odpowiada – w Bothost w **Logs** sprawdź, czy nie ma błędu (brak tokenu, Notion 404 itd.).

---

## Przydatne później

- **Logi:** zawsze w projekcie → **Logs** (podgląd na żywo).
- **Restart bota:** w panelu zwykle jest **Restart** / **Перезапустить**.
- **Aktualizacja kodu:** zrób **push do GitHub** (na gałąź, którą wybrałaś) – Bothost przy auto-deploy sam zrobi nowy build i restart (jeśli masz włączone auto-deploy).
- **Support:** [@BothostSupport](https://t.me/bothostru) w Telegramie, e-mail: support@bothost.ru.

---

## Deploy przez terminal Bothost (ręczny clone z tokenem)

Jeśli w panelu bota jest ikona **>_** (terminal) i chcesz spróbować uruchomić bota ręcznie z tokenem w URL:

1. **Otwórz terminal** – kliknij ikonę **>_** przy projekcie Finance Tracker.
2. W terminalu wklej po kolei (zamień `TWÓJ_GITHUB_TOKEN` na token z GitHub):

```bash
cd /tmp
rm -rf finance-bot
git clone "https://TWÓJ_GITHUB_TOKEN@github.com/kristinakurnitskaya/finance-bot.git"
cd finance-bot
pip install -r requirements.txt
```

3. **Ustaw zmienne** (wklej swoje wartości z `.env` – każda linia to jeden `export`):

```bash
export TELEGRAM_BOT_TOKEN="twoj_token_z_botfather"
export NOTION_SECRET="twoj_notion_secret"
export NOTION_EXPENSES_DATABASE_ID="28450736c8d781c69e06c9b783ed4aed"
export NOTION_INCOME_DATABASE_ID="28450736c8d78129a189dd2594bfce91"
export NOTION_ACCOUNTS_DATABASE_ID="28450736c8d781838c14de070ca79e7e"
export NOTION_CATEGORIES_DATABASE_ID="28450736c8d78149994eca6f1bb1636d"
export NOTION_TRANSFERS_DATABASE_ID="28450736c8d781baa868f729b48567d9"
```

4. **Uruchom bota:**

```bash
python bot.py
```

**Uwaga:** To działa tylko w tej sesji. Po restarcie kontenera (redeploy z panelu) wszystko zniknie – terminal nie zastępuje ustawień Git/Variables w panelu. Na stałe lepiej: **repo public** albo wpisanie tokenu w ustawieniach Git na Bothost.

---

## Krótka checklista

1. Zaloguj się na bothost.ru.
2. Nowy projekt → typ **Telegram** (lub Python).
3. Podłącz **GitHub** → repo **finance-bot**.
4. Ustaw **Start command:** `python bot.py`.
5. W **Variables** dodaj: TELEGRAM_BOT_TOKEN, NOTION_SECRET i wszystkie NOTION_*_DATABASE_ID (skopiuj z lokalnego `.env`).
6. **Deploy** → sprawdź **Logs** → napisz do bota w Telegramie.

Jeśli na którymś kroku interfejs wygląda inaczej (np. brak „Variables” albo „Start command”), napisz, co dokładnie widzisz – dopasujemy kroki do Twojego ekranu.
