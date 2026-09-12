import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# --- FAKE SERVER FÜR RENDER ---
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

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY)

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hallo! Ich bin  dein Deutschlehrer. Ich wurde von Mudaris erstellt. Wie kann ich dir beim Deutschlernen helfen?")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_text = update.message.text

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": "Du bist Mudaris. Dein Name ist Mudaris. Du bist ein freundlicher Roboter, der von Mudaris hergestellt wurde. Du bist ein Experte für die deutsche Sprache (B1-B2). REGELN: 1. Sprich NUR auf Deutsch. Niemals Englisch, Arabisch oder andere Sprachen. 2. Wenn jemand fragt 'Wie heißt du?', 'Wer bist du?', 'Wer hat dich gemacht?' antworte: 'Ich bin ein Roboter hergestellt von Mudaris.' 3. Deine Aufgabe ist nur Deutsch beibringen: Grammatik erklären, Fehler korrigieren, Beispiele geben. 4. Wenn jemand auf anderer Sprache schreibt, sage auf Deutsch: 'Bitte schreib auf Deutsch, damit ich dir besser helfen kann.'"
                },
                {"role": "user", "content": user_text}
            ],
            temperature=0.6
        )

        await update.message.reply_text(response.choices[0].message.content)

    except Exception as e:
        print(f"Fehler: {e}")
        await update.message.reply_text(f"Fehler: {e}")

# --- START ---
print("Bot startet...")
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

import asyncio
async def delete_webhook():
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
    except:
        pass

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(delete_webhook())
except:
    asyncio.run(delete_webhook())

print("Bot is alive!")
app.run_polling(drop_pending_updates=True)
