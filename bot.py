"""
Telegram bot: odbiera zdjęcia/tekst z sumą, pyta o typ/kategorię/konto, zapisuje do Notion.
Uruchom: python bot.py (wymaga .env z TELEGRAM_BOT_TOKEN, NOTION_SECRET, NOTION_EXPENSES_DATABASE_ID).
"""
import os
import re
from decimal import InvalidOperation, Decimal
from typing import Optional

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from notion_client import create_expense, create_income, create_transfer

load_dotenv()

# Stan „w trakcie dodawania” per użytkownik (chat_id)
pending: dict[int, dict] = {}

# Listy do przycisków – dopasuj do swoich opcji w Notion (Select)
TYPES = ["Spesa", "Entrata", "Investimento", "Trasferimento"]
CATEGORIES = [
    "Food", "Eating Out", "Gioia", "Taxi", "Transport",
    "Treatments", "Cosmetics", "Health", "House", "Sport",
    "Tech", "Learning", "Presents", "Bills", "Apartment",
    "Travels", "Clothes Paolo", "Clothes Kris", "Events", "Netflix",
    "Internet", "Documents", "Charities", "New page", "Relax",
]
ACCOUNTS = ["Santander Paolo", "Santander Kris", "Revolut Paolo", "Revolut Kris", "Contanti"]
INCOME_SOURCES = ["Salary", "Sales", "Gifts", "From Parents"]


def parse_amount(text: str) -> Optional[float]:
    """Wyciąga liczbę z tekstu (np. 45,50 lub 45.50)."""
    text = text.strip().replace(",", ".")
    try:
        return float(Decimal(text))
    except (InvalidOperation, ValueError):
        return None


def get_photo_url(context: ContextTypes.DEFAULT_TYPE, file_id: str) -> Optional[str]:
    """Zwraca publiczny URL zdjęcia z Telegrama (do zapisu w Notion)."""
    try:
        token = context.bot.token
        f = context.bot.get_file(file_id)
        return f"https://api.telegram.org/file/bot{token}/{f.file_path}"
    except Exception:
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"[Bot] /start od chat_id={update.effective_chat.id}")
    await update.message.reply_text(
        "Ciao! Invia una somma (es. 25.50) o una foto dello scontrino.\n"
        "Comandi: /start – questo messaggio, /add – aggiungi transazione."
    )


async def add_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Rozpoczyna dodawanie transakcji – prosi o sumę."""
    pending[update.effective_chat.id] = {"step": "amount"}
    await update.message.reply_text("Inviami l'importo (es. 45.50) o una foto.")


def keyboard(items: list[str], prefix: str, cols: int = 2) -> InlineKeyboardMarkup:
    """Przyciski inline (prefix:value), w rzędach po cols."""
    flat = [InlineKeyboardButton(name, callback_data=f"{prefix}:{name}") for name in items]
    rows = [flat[i : i + cols] for i in range(0, len(flat), cols)]
    return InlineKeyboardMarkup(rows)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    msg = update.message
    text = (msg.text or "").strip()
    print(f"[Bot] Wiadomość od {chat_id}: zdjęcie={bool(msg.photo)} tekst={repr(text)[:50]}")

    # Zdjęcie
    if msg.photo:
        pending[chat_id] = {
            "step": "amount",
            "photo_file_id": msg.photo[-1].file_id,
        }
        await msg.reply_text("Foto ricevuta. Inviami l'importo (es. 12.50).")
        return

    # Tekst
    if chat_id not in pending or pending[chat_id].get("step") != "amount":
        amount = parse_amount(text)
        if amount is not None and amount > 0:
            pending[chat_id] = {"step": "amount", "amount": amount, "name": text[:200]}
            print(f"[Bot] Kwota OK, wysyłam Tipo? do {chat_id}")
            try:
                await ask_type(update, context)
            except Exception as e:
                print(f"[Bot] Błąd w ask_type: {e}")
                await msg.reply_text(f"Errore: {e}")
        else:
            await msg.reply_text("Invia un importo (es. 45.50) o una foto, oppure /add")
        return

    # W stanie amount i użytkownik wysłał tekst – traktuj jako sumę
    amount = parse_amount(text)
    if amount is not None and amount > 0:
        pending[chat_id]["amount"] = amount
        pending[chat_id]["name"] = text[:200] or "Transazione"
        try:
            await ask_type(update, context)
        except Exception as e:
            print(f"[Bot] Błąd w ask_type: {e}")
            await msg.reply_text(f"Errore: {e}")
    else:
        await msg.reply_text("Scrivi un numero (es. 45.50).")


async def ask_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    msg = update.message or (update.callback_query and update.callback_query.message)
    if msg is None:
        print("[Bot] ask_type: msg jest None")
        return
    try:
        await msg.reply_text("Tipo?")
        await msg.reply_text(
            "Wybierz:",
            reply_markup=keyboard(TYPES, "type"),
        )
        print(f"[Bot] Tipo? wysłane do {chat_id}")
    except Exception as e:
        print(f"[Bot] ask_type reply_text błąd: {e}")
        raise
    pending[chat_id]["step"] = "type"


async def ask_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    msg = update.message or (update.callback_query and update.callback_query.message)
    await msg.reply_text(
        "Categoria?",
        reply_markup=keyboard(CATEGORIES, "cat", cols=2),
    )
    pending[chat_id]["step"] = "category"


async def ask_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    msg = update.message or (update.callback_query and update.callback_query.message)
    await msg.reply_text(
        "Conto?",
        reply_markup=keyboard(ACCOUNTS, "acc"),
    )
    pending[chat_id]["step"] = "account"


async def ask_income_source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    msg = update.message or (update.callback_query and update.callback_query.message)
    await msg.reply_text(
        "Income Source?",
        reply_markup=keyboard(INCOME_SOURCES, "src"),
    )
    pending[chat_id]["step"] = "income_source"


async def ask_transfer_from(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    msg = update.message or (update.callback_query and update.callback_query.message)
    await msg.reply_text(
        "Da quale conto? (From)",
        reply_markup=keyboard(ACCOUNTS, "from_acc"),
    )
    pending[chat_id]["step"] = "transfer_from"


async def ask_transfer_to(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    msg = update.message or (update.callback_query and update.callback_query.message)
    await msg.reply_text(
        "A quale conto? (To)",
        reply_markup=keyboard(ACCOUNTS, "to_acc"),
    )
    pending[chat_id]["step"] = "transfer_to"


async def save_to_notion_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if chat_id not in pending:
        await update.callback_query.answer("Sessione scaduta. Usa /add.")
        return
    data = pending[chat_id]
    db_id = os.environ.get("NOTION_TRANSFERS_DATABASE_ID")
    if not db_id or len(db_id) != 32:
        await update.callback_query.answer("NOTION_TRANSFERS_DATABASE_ID mancante in .env", show_alert=True)
        return
    try:
        accounts_db_id = os.environ.get("NOTION_ACCOUNTS_DATABASE_ID")
        create_transfer(
            database_id=db_id,
            comment=data.get("name") or "Trasferimento",
            amount=float(data["amount"]),
            from_account=data["from_account"],
            to_account=data["to_account"],
            accounts_database_id=accounts_db_id,
        )
    except Exception as e:
        print(f"[Bot] Błąd Notion (Transfers): {e}")
        err_msg = str(e)[:80]
        await update.callback_query.answer(f"Notion: {err_msg}", show_alert=True)
        return
    del pending[chat_id]
    await update.callback_query.answer("Salvato in Notion (Transfer).")
    await update.callback_query.message.reply_text("Salvato in Notion (Transfer).")


async def save_to_notion_income(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    print(f"[Bot] save_to_notion_income dla chat_id={chat_id}")
    if chat_id not in pending:
        await update.callback_query.answer("Sessione scaduta. Usa /add.")
        return
    data = pending[chat_id]
    db_id = os.environ.get("NOTION_INCOME_DATABASE_ID")
    if not db_id or len(db_id) != 32:
        print(f"[Bot] Brak NOTION_INCOME_DATABASE_ID (len={len(db_id or '')})")
        await update.callback_query.answer("NOTION_INCOME_DATABASE_ID mancante in .env", show_alert=True)
        return
    try:
        accounts_db_id = os.environ.get("NOTION_ACCOUNTS_DATABASE_ID")
        create_income(
            database_id=db_id,
            comment=data.get("name") or "Entrata",
            amount=float(data["amount"]),
            account=data["account"],
            income_source=data.get("income_source", "Salary"),
            accounts_database_id=accounts_db_id,
        )
    except Exception as e:
        print(f"[Bot] Błąd Notion (Income): {e}")
        err_msg = str(e)[:80]
        await update.callback_query.answer(f"Notion: {err_msg}", show_alert=True)
        return
    del pending[chat_id]
    await update.callback_query.answer("Salvato in Notion (Income).")
    await update.callback_query.message.reply_text("Salvato in Notion (Income).")


async def save_to_notion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if chat_id not in pending:
        await update.callback_query.answer("Sessione scaduta. Usa /add.")
        return

    data = pending[chat_id]
    db_id = os.environ.get("NOTION_EXPENSES_DATABASE_ID")
    if not db_id:
        await update.callback_query.answer("NOTION_EXPENSES_DATABASE_ID mancante.", show_alert=True)
        return

    photo_url = None
    if data.get("photo_file_id"):
        photo_url = get_photo_url(context, data["photo_file_id"])

    try:
        accounts_db_id = os.environ.get("NOTION_ACCOUNTS_DATABASE_ID")
        categories_db_id = os.environ.get("NOTION_CATEGORIES_DATABASE_ID")
        create_expense(
            database_id=db_id,
            name=data.get("name") or "Transazione",
            amount=float(data["amount"]),
            transaction_type=data["type"],
            category=data["category"],
            account=data["account"],
            photo_url=photo_url,
            accounts_database_id=accounts_db_id,
            categories_database_id=categories_db_id,
        )
    except Exception as e:
        print(f"[Bot] Błąd Notion (Expenses): {e}")
        err_msg = str(e)[:80]
        await update.callback_query.answer(f"Notion: {err_msg}", show_alert=True)
        return

    del pending[chat_id]
    await update.callback_query.answer("Salvato in Notion.")
    await update.callback_query.message.reply_text("Salvato in Notion.")


async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    chat_id = update.effective_chat.id
    data = pending.get(chat_id, {})
    step = data.get("step")
    action, value = (q.data.split(":", 1) + [""])[:2]
    print(f"[Bot] Callback: step={step!r} action={action!r} value={value!r}")

    await q.answer()
    if chat_id not in pending:
        await q.message.reply_text("Sessione scaduta. Usa /add.")
        return

    data = pending[chat_id]
    step = data.get("step")
    action, value = (q.data.split(":", 1) + [""])[:2]

    if step == "type" and action == "type":
        data["type"] = value
        if value.strip().lower() == "entrata":
            pending[chat_id]["step"] = "account"
            await ask_account(update, context)
        elif value.strip().lower() == "trasferimento":
            pending[chat_id]["step"] = "transfer_from"
            await ask_transfer_from(update, context)
        else:
            await ask_category(update, context)
    elif step == "transfer_from" and action == "from_acc":
        data["from_account"] = value
        await ask_transfer_to(update, context)
    elif step == "transfer_to" and action == "to_acc":
        data["to_account"] = value
        await save_to_notion_transfer(update, context)
    elif step == "category" and action == "cat":
        data["category"] = value
        await ask_account(update, context)
    elif step == "account" and action == "acc":
        data["account"] = value
        if data.get("type") == "Entrata":
            await ask_income_source(update, context)
        else:
            await save_to_notion(update, context)
    elif step == "income_source" and action == "src":
        data["income_source"] = value
        print(f"[Bot] Zapisuję Income: {value}")
        await save_to_notion_income(update, context)
    else:
        print(f"[Bot] Callback nie dopasowany: step={step!r} action={action!r}")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    err = context.error
    print(f"[Bot] Nieobsłużony błąd: {err}")
    if update and isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(f"Errore: {str(err)[:80]}")


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Ustaw TELEGRAM_BOT_TOKEN w .env")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_cmd))
    app.add_handler(MessageHandler(filters.PHOTO | (filters.TEXT & ~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_error_handler(error_handler)

    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token or ":" not in token:
        raise SystemExit("Błąd: TELEGRAM_BOT_TOKEN w .env jest pusty lub w złym formacie.")
    db_id = os.environ.get("NOTION_EXPENSES_DATABASE_ID", "")
    if not db_id or len(db_id) != 32:
        raise SystemExit("Błąd: NOTION_EXPENSES_DATABASE_ID w .env jest pusty lub nie ma 32 znaków.")
    print("Bot uruchomiony. Wyślij /start do bota w Telegramie.")
    print("(Ctrl+C = wyjście)\n")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
