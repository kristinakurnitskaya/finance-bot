"""
Telegram Finance Bot – records transactions step-by-step and saves to Google Sheets.
Production-ready, deployable on Railway.
"""
import asyncio
import warnings
from datetime import date

warnings.filterwarnings("ignore", category=FutureWarning, message=".*Python.*")

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import config
from parser import parse_amount
from sheets import (
    append_transaction,
    append_transfer,
    get_accounts_from_sheet,
    get_categories_from_sheet,
    get_income_categories_from_sheet,
    get_loans_from_sheet,
)

# --- Constants ---

TRANSACTION_TYPES = ["Expense", "Income", "Transfer", "Loan Payment"]

CATEGORIES = [
    "Food",
    "Eating Out",
    "Gioia",
    "Taxi",
    "Transport",
    "Treatments",
    "Cosmetics",
    "Health",
    "House",
    "Sport",
    "Tech",
    "Learning",
    "Presents",
    "Bills",
    "Apartment",
    "Travels",
    "Clothes Paolo",
    "Clothes Kris",
    "Events",
    "Netflix",
    "Documents",
    "Charities",
    "Relax",
    "Internet",
]

# Kategorie tylko dla Income (Salary, Sales, Gifts, From Parents + opcja nowa)
INCOME_CATEGORIES = ["Salary", "Sales", "Gifts", "From Parents"]

ACCOUNTS = [
    "Revolut Paolo",
    "Revolut Kris",
    "Santander Paolo",
    "Santander Kris",
    "Cash",
    "Financial cushion",
    "Credit Card",
]

# In-memory state: chat_id -> {step, amount, currency, type, category, account, note}
STATE: dict[int, dict] = {}


def _keyboard(items: list[str], prefix: str, cols: int = 2) -> InlineKeyboardMarkup:
    """Build inline keyboard with prefix for callback_data."""
    buttons = [InlineKeyboardButton(x, callback_data=f"{prefix}:{x}") for x in items]
    rows = [buttons[i : i + cols] for i in range(0, len(buttons), cols)]
    return InlineKeyboardMarkup(rows)


# --- Handlers ---

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Send an amount to record a transaction.\n\n"
        "Examples:\n"
        "12\n"
        "12.50\n"
        "50 EUR\n"
        "100 USD"
    )


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    text = (update.message.text or "").strip()

    # No active transaction – expect amount
    if chat_id not in STATE:
        result = parse_amount(text)
        if result is None:
            await update.message.reply_text(
                "Please send a valid amount.\n\n"
                "Examples:\n"
                "12\n"
                "12.50\n"
                "50 EUR\n"
                "100 USD"
            )
            return
        amount, currency = result
        STATE[chat_id] = {
            "step": "type",
            "amount": amount,
            "currency": currency,
        }
        await update.message.reply_text(
            "What type of transaction is this?",
            reply_markup=_keyboard(TRANSACTION_TYPES, "type", cols=2),
        )
        return

    data = STATE[chat_id]
    step = data.get("step")

    if step == "income_category_new":
        # User wpisał nazwę nowej kategorii dla Income → pytamy o konto
        data["category"] = text[:200] if text else "Other"
        data["step"] = "account"
        accounts = await asyncio.to_thread(get_accounts_from_sheet)
        await update.message.reply_text(
            "Select account",
            reply_markup=_keyboard(accounts or ACCOUNTS, "acc", cols=2),
        )
        return

    if step == "note":
        # User sent note text (or we treat any text as note)
        data["note"] = text[:500] if text else ""
        data["step"] = "done"
        await _save_and_confirm(update, context, chat_id, data)
        return

    # Any other step – only amount is valid input; we're waiting for buttons
    result = parse_amount(text)
    if result:
        amount, currency = result
        STATE[chat_id] = {
            "step": "type",
            "amount": amount,
            "currency": currency,
        }
        await update.message.reply_text(
            "What type of transaction is this?",
            reply_markup=_keyboard(TRANSACTION_TYPES, "type", cols=2),
        )
    else:
        await update.message.reply_text("Use the buttons above to choose, or send a new amount to start over.")


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat.id

    if chat_id not in STATE:
        await context.bot.send_message(chat_id, "Session expired. Send an amount to start.")
        return

    data = STATE[chat_id]
    parts = q.data.split(":", 1)
    action = parts[0]
    value = parts[1] if len(parts) > 1 else ""

    if action == "type":
        data["type"] = value
        if value == "Income":
            data["step"] = "income_category"
            income_cats = await asyncio.to_thread(get_income_categories_from_sheet)
            income_buttons = (income_cats or INCOME_CATEGORIES) + ["Add new"]
            await q.message.reply_text(
                "Select income category",
                reply_markup=_keyboard(income_buttons, "inc_cat", cols=2),
            )
        elif value == "Transfer":
            data["step"] = "transfer_from"
            accounts = await asyncio.to_thread(get_accounts_from_sheet)
            await q.message.reply_text(
                "From which account?",
                reply_markup=_keyboard(accounts or ACCOUNTS, "from_acc", cols=2),
            )
        elif value == "Loan Payment":
            data["step"] = "loan"
            loans = await asyncio.to_thread(get_loans_from_sheet)
            if not loans:
                await q.message.reply_text(
                    "No loans in the Loans sheet. Add loan names in Loans!A2:A and try again.",
                )
                data["step"] = "type"
                return
            await q.message.reply_text(
                "Which loan?",
                reply_markup=_keyboard(loans, "loan", cols=2),
            )
        else:
            data["step"] = "category"
            categories = await asyncio.to_thread(get_categories_from_sheet)
            await q.message.reply_text(
                "Select category",
                reply_markup=_keyboard(categories or CATEGORIES, "cat", cols=2),
            )

    elif action == "from_acc":
        data["from_account"] = value
        data["step"] = "transfer_to"
        accounts = await asyncio.to_thread(get_accounts_from_sheet)
        await q.message.reply_text(
            "To which account?",
            reply_markup=_keyboard(accounts or ACCOUNTS, "to_acc", cols=2),
        )

    elif action == "to_acc":
        data["to_account"] = value
        data["step"] = "note"
        await q.message.reply_text(
            "Add a note? (optional)\n\nType a note or press Skip.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Skip", callback_data="note:__skip__")],
            ]),
        )

    elif action == "loan":
        data["loan"] = value  # loan name -> Category (C) for Loans formula
        data["step"] = "loan_account"
        accounts = await asyncio.to_thread(get_accounts_from_sheet)
        await q.message.reply_text(
            "From which account? (paying from)",
            reply_markup=_keyboard(accounts or ACCOUNTS, "loan_acc", cols=2),
        )

    elif action == "loan_acc":
        data["account"] = value  # bank account (Santander Paolo) -> D
        data["category"] = data.get("loan", "")  # loan name -> C for Loans formula
        data["step"] = "note"
        await q.message.reply_text(
            "Add a note? (optional)\n\nType a note or press Skip.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Skip", callback_data="note:__skip__")],
            ]),
        )

    elif action == "inc_cat":
        if value == "Add new":
            data["step"] = "income_category_new"
            await q.message.reply_text("Enter the new category name (e.g. Freelance, Bonus):")
        else:
            data["category"] = value
            data["step"] = "account"
            accounts = await asyncio.to_thread(get_accounts_from_sheet)
            await q.message.reply_text(
                "Select account",
                reply_markup=_keyboard(accounts or ACCOUNTS, "acc", cols=2),
            )

    elif action == "cat":
        data["category"] = value
        data["step"] = "account"
        accounts = await asyncio.to_thread(get_accounts_from_sheet)
        await q.message.reply_text(
            "Select account",
            reply_markup=_keyboard(accounts or ACCOUNTS, "acc", cols=2),
        )

    elif action == "acc":
        data["account"] = value
        data["step"] = "note"
        await q.message.reply_text(
            "Add a note? (optional)\n\nType a note or press Skip.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Skip", callback_data="note:__skip__")],
            ]),
        )

    elif action == "note" and value == "__skip__":
        data["note"] = ""
        data["step"] = "done"
        await _save_and_confirm(update, context, chat_id, data)


async def _save_and_confirm(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    data: dict,
) -> None:
    """Write transaction to Sheets and send confirmation."""
    try:
        if data.get("type") == "Transfer":
            await asyncio.to_thread(
                append_transfer,
                data.get("from_account", ""),
                data.get("to_account", ""),
                data.get("amount", 0),
                data.get("currency", "EUR"),
                date.today(),
                data.get("note", ""),
            )
            payload = {
                "type": "Transfer",
                "amount": data.get("amount", 0),
                "currency": data.get("currency", "EUR"),
                "note": data.get("note", ""),
            }
        else:
            raw_amount = data.get("amount", 0)
            # Expense, Loan Payment = minus (outflow); Income = plus (inflow)
            if data.get("type") in ("Expense", "Loan Payment"):
                amount = -abs(float(raw_amount))
            else:
                amount = abs(float(raw_amount))
            payload = {
                "date": date.today(),
                "type": data.get("type", ""),
                "category": data.get("category", ""),
                "account": data.get("account", ""),
                "amount": amount,
                "currency": data.get("currency", "EUR"),
                "note": data.get("note", ""),
            }
            await asyncio.to_thread(append_transaction, payload)
    except Exception as e:
        await context.bot.send_message(chat_id, f"Error saving: {str(e)[:200]}")
        return
    finally:
        if chat_id in STATE:
            del STATE[chat_id]

    msg = (
        "Transaction saved ✅\n\n"
        f"Amount: {payload['amount']} {payload['currency']}\n"
        f"Type: {payload['type']}\n"
    )
    if payload["type"] == "Transfer":
        msg += f"From: {data.get('from_account', '')} → To: {data.get('to_account', '')}\n"
    elif payload["type"] == "Loan Payment":
        msg += f"Loan: {data.get('loan', '')}\nAccount: {payload['account']}\n"
    else:
        msg += f"Category: {payload['category']}\nAccount: {payload['account']}\n"
    if payload.get("note"):
        msg += f"\nNote: {payload['note'][:100]}"
    await context.bot.send_message(chat_id, msg)


def main() -> None:
    token = config.get_telegram_token()
    # Validate Google config on startup
    config.get_google_sheet_id()
    config.get_google_credentials()

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
    app.add_handler(CallbackQueryHandler(on_callback))

    print("Bot running. Send an amount in Telegram to start.")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
