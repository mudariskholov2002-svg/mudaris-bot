import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# --- 1. FAKE SERVER FÜR RENDER (gegen Port Fehler) ---
def start_fake_server():
    port = int(os.environ.get("PORT", 10000))
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is alive!")
        def log_message(self, format, *args):
            return
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

threading.Thread(target=start_fake_server, daemon=True).start()

# --- 2. KEYS ---
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

if not BOT_TOKEN or not GROQ_KEY:
    print("FEHLER: TELEGRAM_TOKEN oder GROQ_API_KEY fehlt in Environment!")

client = Groq(api_key=GROQ_KEY)

# --- 3. HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salam! Ich bin Mudaris Bot. Schreib mir was!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_text = update.message.text
        print(f"User: {user_text}")

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": user_text}],
            temperature=0.7
        )

        answer = response.choices[0].message.content
        await update.message.reply_text(answer)

    except Exception as e:
        print(f"Fehler: {e}")
        await update.message.reply_text(f"Fehler: {e}")

# --- 4. START ---
print("Bot startet...")
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

# Webhook löschen gegen Conflict
import asyncio
async def delete_webhook():
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
        print("Webhook gelöscht - Bereit!")
    except Exception as e:
        print(f"Webhook Fehler: {e}")

# asyncio loop für Webhook delete
try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(delete_webhook())
except:
    asyncio.run(delete_webhook())

print("Bot is alive! Polling startet...")
app.run_polling(drop_pending_updates=True)
