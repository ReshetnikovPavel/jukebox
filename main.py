import logging
import os

import dotenv
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

import consts
import handlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


if __name__ == "__main__":
    dotenv.load_dotenv()
    token = os.environ.get(consts.TG_TOKEN_VAR)
    if token is None:
        raise Exception(f"{consts.TG_TOKEN_VAR} env variable is not present")

    application = ApplicationBuilder().token(token).concurrent_updates(True).build()
    application.add_handler(CommandHandler("start", handlers.start_handler))
    application.add_handler(CallbackQueryHandler(handlers.callback_handler))
    application.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), handlers.message_handler)
    )
    application.run_polling()
