from telegram.ext import Application, CommandHandler

application = Application.builder().token(BOT_TOKEN).build()

application.add_handler(CommandHandler("start", start))

if __name__ == "__main__":
    application.run_polling()
