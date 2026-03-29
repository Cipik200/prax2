
import subprocess
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8642464175:AAFIOd5dv2hiSW4Y1ElrcRk5o6jeFUkZCRQ"
ALLOWED_USER_ID = 5805433248

def is_allowed(user_id):
    return user_id == ALLOWED_USER_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        return
    await update.message.reply_text("ПК ГОТОВ")

async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        return

    program = " ".join(context.args)

    if not program:
        await update.message.reply_text(".exe")
        return

    try:
        subprocess.Popen(program)
        await update.message.reply_text(f"Запустил: {program}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        return

    await update.message.reply_text("Выключаю ПК...")
    os.system("shutdown /s /t 0")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("run", run))
app.add_handler(CommandHandler("off", shutdown))

app.run_polling()