import os, tempfile
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

BOT_TOKEN=os.getenv("TELEGRAM_TOKEN")
GROQ_KEY=os.getenv("GROQ_API_KEY")
client=Groq(api_key=GROQ_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom Mudaris! Ich bin dein Deutsch Lehrer 🇩🇪\nSchick mir eine Sprachnachricht auf Deutsch!")

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎧 Höre zu...")
    voice_file = await context.bot.get_file(update.message.voice.file_id)
    tmp = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
    await voice_file.download_to_drive(tmp.name)
    with open(tmp.name, "rb") as f:
        text = client.audio.transcriptions.create(file=(tmp.name, f.read()), model="whisper-large-v3", language="de", response_format="text")
    await update.message.reply_text(f'✅ Du sagtest: "{text}"')
    response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f'Du bist Deutschlehrer. Student sagte: "{text}". Korrigiere. Format: ❌ Falsch: original\n✅ Richtig: korrigiert\n📖 Erklärung: auf Tajikisch\n❓ Frage: weiter auf Deutsch'}])
    await update.message.reply_text(response.choices[0].message.content)
    os.remove(tmp.name)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
