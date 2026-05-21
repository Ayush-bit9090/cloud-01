from flask import Flask
from threading import Thread

from telegram import (
    Update
)

from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)

import os

# =====================================
# WEB SERVER FOR RENDER
# =====================================

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))

    web_app.run(
        host="0.0.0.0",
        port=port
    )

Thread(target=run_web).start()

# =====================================
# BOT TOKEN
# =====================================

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# =====================================
# STORAGE FOLDER
# =====================================

SAVE_FOLDER = "downloads"

os.makedirs(
    SAVE_FOLDER,
    exist_ok=True
)

# =====================================
# START COMMAND
# =====================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "✅ Storage Bot Online!\n\n"
        "📦 Send files to save them\n"
        "📂 Use /files to get files back\n"
        "📊 Use /stats for storage info"
    )

    await update.message.reply_text(text)

# =====================================
# SAVE FILES
# =====================================

async def save_media(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message

    file = None
    filename = None

    if message.photo:

        file = await message.photo[-1].get_file()

        filename = (
            f"{file.file_unique_id}.jpg"
        )

    elif message.video:

        file = await message.video.get_file()

        filename = (
            f"{file.file_unique_id}.mp4"
        )

    elif message.document:

        file = await message.document.get_file()

        filename = (
            message.document.file_name
        )

    elif message.audio:

        file = await message.audio.get_file()

        filename = (
            f"{file.file_unique_id}.mp3"
        )

    if file:

        path = os.path.join(
            SAVE_FOLDER,
            filename
        )

        await file.download_to_drive(path)

        await update.message.reply_text(
            f"✅ Saved: {filename}"
        )

# =====================================
# GET FILES
# =====================================

async def get_files(update: Update, context: ContextTypes.DEFAULT_TYPE):

    files = os.listdir(SAVE_FOLDER)

    if not files:

        await update.message.reply_text(
            "❌ No files found."
        )

        return

    await update.message.reply_text(
        f"📂 Sending {len(files)} files..."
    )

    for file_name in files:

        file_path = os.path.join(
            SAVE_FOLDER,
            file_name
        )

        try:

            with open(file_path, "rb") as f:

                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=f,
                    filename=file_name
                )

        except Exception as e:

            print(e)

# =====================================
# STORAGE STATS
# =====================================

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    files = os.listdir(SAVE_FOLDER)

    total_size = 0

    for file_name in files:

        total_size += os.path.getsize(
            os.path.join(
                SAVE_FOLDER,
                file_name
            )
        )

    total_size_mb = round(
        total_size / (1024 * 1024),
        2
    )

    await update.message.reply_text(
        f"📊 Files: {len(files)}\n"
        f"💾 Size: {total_size_mb} MB"
    )

# =====================================
# RUN BOT
# =====================================

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(
    CommandHandler(
        "start",
        start
    )
)

app.add_handler(
    CommandHandler(
        "files",
        get_files
    )
)

app.add_handler(
    CommandHandler(
        "stats",
        stats
    )
)

app.add_handler(
    MessageHandler(
        filters.PHOTO
        | filters.VIDEO
        | filters.Document.ALL
        | filters.AUDIO,
        save_media
    )
)

print("Bot started")

app.run_polling()
