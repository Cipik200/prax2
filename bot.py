import asyncio
import subprocess
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
# Ensure we handle the case where ALLOWED_USER_ID might be missing or not an int
try:
    ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", 0))
except (ValueError, TypeError):
    ALLOWED_USER_ID = 0

if not TOKEN or ALLOWED_USER_ID == 0:
    raise ValueError("Missing or invalid TELEGRAM_TOKEN or ALLOWED_USER_ID in .env file")

def is_allowed(user_id):
    return user_id == ALLOWED_USER_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        logger.warning(f"Unauthorized access attempt by {update.effective_user.id}")
        return
    await update.message.reply_text("ПК ГОТОВ")

async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        return

    program = " ".join(context.args)
    if not program:
        await update.message.reply_text("Использование: /run <программа>")
        return

    try:
        # Popen is non-blocking, which is good for a bot
        subprocess.Popen(program, shell=True)
        await update.message.reply_text(f"Запустил: {program}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        return

    await update.message.reply_text("Выключаю ПК...")
    os.system("shutdown /s /t 5")

async def main():
    # 1. Build the application
    app = ApplicationBuilder().token(TOKEN).build()

    # 2. Add your handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("run", run))
    app.add_handler(CommandHandler("off", shutdown))

    # 3. Manual Startup (Bypasses the run_polling bug in 3.14)
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    logger.info("Bot is running. Press Ctrl+C to stop.")

    # 4. Keep the bot running until interrupted
    stop_event = asyncio.Event()
    
    # This allows the bot to shut down cleanly on Ctrl+C
    try:
        await stop_event.wait()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping bot...")
    finally:
        # 5. Graceful shutdown
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass # Handle the exit cleanly