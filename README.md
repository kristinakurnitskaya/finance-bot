# Finance Telegram Bot

Telegram bot that records financial transactions and saves them to Google Sheets. Production-ready and deployable on Railway.

## Stack

- Python
- python-telegram-bot
- Google Sheets API
- python-dotenv

## Project structure

```
finance bot/
├── bot.py          # Telegram bot and conversation flow
├── sheets.py       # Google Sheets – append_transaction()
├── parser.py       # parse_amount() – amount + currency
├── config.py       # Env: token, sheet ID, credentials
├── requirements.txt
├── .env            # Your secrets (not in git)
├── .env.example    # Template
└── README.md
```

## 1. Create a Telegram bot

1. Open [@BotFather](https://t.me/BotFather) in Telegram.
2. Send `/newbot`, choose name and username.
3. Copy the **token** (e.g. `123456:ABC-DEF...`).
4. Put it in `.env` as `TELEGRAM_BOT_TOKEN=...`.

## 2. Connect Google Sheets

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project (or use existing).
3. Enable **Google Sheets API**.
4. Create a **Service Account** (APIs & Services → Credentials → Create credentials → Service account).
5. Create a key (JSON) and download it.
6. Open your Google Sheet. Share it with the service account email (e.g. `xxx@yyy.iam.gserviceaccount.com`) as **Editor**.
7. From the sheet URL copy the **Spreadsheet ID** (the long string between `/d/` and `/edit`).
8. In `.env`:
   - `GOOGLE_SHEETS_SPREADSHEET_ID=your_id`
   - Either paste the whole JSON content as one line in `GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'`  
     **or** save the JSON file and set `GOOGLE_SERVICE_ACCOUNT_FILE=./path/to/file.json`.

## 3. Sheet setup

Create a sheet named **Transactions** with a header row (10 columns):

| Date | Type | Category | Account | Amount | Currency | Amount EUR | Note | Month | Year |

The bot appends rows below this. It fills **Month** and **Year** from the transaction date, and **Amount EUR** with a formula that uses exchange rates from another tab.

**Exchange rates tab:** Name the tab **ExchangeRates** (or set `GOOGLE_SHEETS_RATES_SHEET` in `.env`). Columns: Currency, Rate to EUR. You can use `=GOOGLEFINANCE("CURRENCY:USDEUR")` etc. in that tab.

| Currency | Rate to EUR |
|----------|-------------|
| EUR      | 1.00        |
| USD      | 0.86        |
| PLN      | 0.23        |

Amount EUR in Transactions is computed as `Amount × Rate to EUR` for the row’s Currency.

Dates are stored as **YYYY-MM-DD**. Sum by month using column I (Month) and J (Year), or filter by Amount EUR (column G).

## 4. Run locally

```bash
# Create venv and install
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/activate

# Run
python bot.py
```

Or use the script:

```bash
./run_bot.sh
```

## 5. Deploy on Railway

1. Push the project to GitHub (without `.env`).
2. In [Railway](https://railway.app/), New Project → Deploy from GitHub → select repo.
3. Add environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `GOOGLE_SHEETS_SPREADSHEET_ID`
   - `GOOGLE_SERVICE_ACCOUNT_JSON` (paste the full JSON string).
4. Set start command: `python bot.py`.
5. Deploy.

Railway will run `python bot.py` and keep the bot running.

## Flow

1. User sends an **amount** (e.g. `12`, `50 EUR`, `100 USD`).
2. Bot asks for **type**: Expense, Income, Transfer, Investment, Loan Payment.
3. Bot asks for **category** (inline list).
4. Bot asks for **account** (inline list).
5. Bot asks for **note** (optional; user can type or press Skip).
6. Bot appends the row to Google Sheets and sends a confirmation.

## Errors

- **Invalid amount** → Bot replies with examples.
- **Missing env** → Script exits with a clear message (e.g. `TELEGRAM_BOT_TOKEN missing`).
