import logging
import os

import dotenv
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters, CallbackQueryHandler,
)

import handlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


if __name__ == "__main__":
    dotenv.load_dotenv()
    token = os.environ.get("TG_TOKEN")
    if token is None:
        raise Exception("TG_TOKEN env variable is not present")

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", handlers.start_handler))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handlers.search_handler))
    application.add_handler(CallbackQueryHandler(handlers.callback_handler))
    application.run_polling()
