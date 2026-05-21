from flask import Flask
from threading import Thread

from telegram import Update

from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)

import os
import json

# =====================================
# WEB SERVER FOR RENDER
# =====================================

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Bot is running!"

def run_web():

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    web_app.run(
        host="0.0.0.0",
        port=port
    )

Thread(target=run_web).start()

# =====================================
# BOT TOKEN
# =====================================

BOT_TOKEN = os.environ.get(
    "BOT_TOKEN"
)

# =====================================
# FILE DATABASE
# =====================================

DB_FILE = "files.json"

if not os.path.exists(DB_FILE):

    with open(DB_FILE, "w") as f:

        json.dump([], f)

# =====================================
# LOAD FILE IDS
# =====================================

def load_files():

    with open(DB_FILE, "r") as f:

        return json.load(f)

# =====================================
# SAVE FILE IDS
# =====================================

def save_files(data):

    with open(DB_FILE, "w") as f:

        json.dump(data, f)

# =====================================
# START COMMAND
# =====================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "✅ File ID Storage Bot\n\n"
        "📦 Send files to save\n"
        "⚡ Fast cloud resend\n"
        "📂 Use /files to get files"
    )

    await update.message.reply_text(text)

# =====================================
# SAVE FILE IDS
# =====================================

async def save_media(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message

    file_data = None

    if message.photo:

        file_data = {
            "type": "photo",
            "file_id": message.photo[-1].file_id
        }

    elif message.video:

        file_data = {
            "type": "video",
            "file_id": message.video.file_id
        }

    elif message.document:

        file_data = {
            "type": "document",
            "file_id": message.document.file_id
        }

    elif message.audio:

        file_data = {
            "type": "audio",
            "file_id": message.audio.file_id
        }

    if file_data:

        data = load_files()

        data.append(file_data)

        save_files(data)

        await update.message.reply_text(
            "✅ File saved instantly!"
        )

# =====================================
# SEND FILES BACK
# =====================================

async def get_files(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = load_files()

    if not data:

        await update.message.reply_text(
            "❌ No saved files."
        )

        return

    await update.message.reply_text(
        f"📂 Sending {len(data)} files..."
    )

    for item in data:

        try:

            if item["type"] == "photo":

                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=item["file_id"]
                )

            elif item["type"] == "video":

                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=item["file_id"]
                )

            elif item["type"] == "document":

                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=item["file_id"]
                )

            elif item["type"] == "audio":

                await context.bot.send_audio(
                    chat_id=update.effective_chat.id,
                    audio=item["file_id"]
                )

        except Exception as e:

            print(e)

# =====================================
# STATS
# =====================================

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = load_files()

    await update.message.reply_text(
        f"📊 Saved files: {len(data)}"
    )

# =====================================
# DELETE ALL
# =====================================

async def delete_all(update: Update, context: ContextTypes.DEFAULT_TYPE):

    save_files([])

    await update.message.reply_text(
        "🗑 All saved file IDs deleted."
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
    CommandHandler(
        "deleteall",
        delete_all
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
