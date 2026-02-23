# Finance Bot – Telegram → Notion

Bot do Telegrama: wysyłasz zdjęcie paragonu lub sumę, wybierasz typ / kategorię / konto, wpis ląduje w Notion.

## Co jest zrobione

- **Notion:** integracja + Share na bazę Expenses (szczegóły w **NOTION_SETUP.md** i **NOTION_STRUKTURA_BAZ.md**).
- **Bot:** Python, `python-telegram-bot`, zapis do bazy **Expenses** w Notion.

## Uruchomienie (lokalnie)

### 1. Zależności

```bash
cd "/Users/kristina/Desktop/finance bot"
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Konfiguracja

- Skopiuj `.env.example` do `.env`.
- Wypełnij w `.env`:
  - **TELEGRAM_BOT_TOKEN** – token od [@BotFather](https://t.me/BotFather) (New Bot → skopiuj token).
  - **NOTION_SECRET** – Internal Integration Secret z [Notion → My integrations](https://www.notion.so/my-integrations).
  - **NOTION_EXPENSES_DATABASE_ID** – ID bazy Expenses (z URL strony bazy, 32 znaki).

ID bazy: otwórz bazę Expenses w przeglądarce; w URL jest np.  
`.../xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx?v=...` – ten ciąg `x` to ID (możesz z myślnikami lub bez).

### 3. Notion – nazwy kolumn

W bazie **Expenses** kolumny muszą się nazywać dokładnie: **Name**, **Amount**, **Type**, **Category**, **Account**, **Utente**, **Date**, **Description**, **Photo**.  
Typy: Title, Number, Select, Select, Select, Select, Date, Text, URL.  
W Selectach muszą być dokładnie te same opcje co w bocie (np. Type: Spesa, Entrata, Investimento, Trasferimento; konta: Revolut, Banca Polacca, Muserbank, Contanti, Altro). Listę kategorii i kont możesz zmienić w `bot.py` (zmienne `CATEGORIES`, `ACCOUNTS`, `USERS`).

### 4. Uruchomienie bota

```bash
python bot.py
```

W Telegramie: `/start`, potem wyślij sumę (np. `25.50`) lub zdjęcie – bot zapyta o typ, kategorię, konto, kto – i zapisze wpis w Notion.

## Komendy

- **/start** – powitanie i krótka instrukcja.
- **/add** – rozpoczęcie dodawania transakcji (bot poprosi o sumę).

Możesz też od razu wysłać liczbę (np. `45.50`) lub zdjęcie – wtedy bot też rozpocznie flow.

## Deploy (działanie 24/7)

Żeby bot działał bez włączonego komputera, trzeba go wrzucić na serwer, np.:

- **Railway** / **Render** (free tier) – dodaj repozytorium, zmienne z `.env` ustaw w panelu, uruchom `python bot.py`.
- **VPS** (Hetzner, DigitalOcean itd.) – zainstaluj Pythona, skopiuj projekt, ustaw `.env`, uruchom w `screen` lub jako usługę (systemd).

Szczegóły zależą od wybranej platformy; gdy wybierzesz jedną, można rozpisać kroki.

## Pliki

- `bot.py` – logika Telegrama i flow (suma → typ → kategoria → konto → kto → zapis).
- `notion_client.py` – zapis jednego wpisu do bazy Expenses w Notion.
- `NOTION_SETUP.md` – przygotowanie Notion pod integrację.
- `NOTION_STRUKTURA_BAZ.md` – struktura baz „od zera”.
