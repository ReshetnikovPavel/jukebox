import logging
import os
from typing import Any, Callable

import dotenv
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import consts
import handlers
import handlers.albums
import handlers.songs
import handlers.video

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def add_query_handler(
    application: Application,
    command: str,
    handler: Callable[[Update, ContextTypes.DEFAULT_TYPE], Any],
) -> None:
    application.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler(command, handler)],
            states={
                consts.CONVERSATION_HANDLER_REPEAT: [
                    CommandHandler(command, handler),
                    MessageHandler(filters.TEXT & (~filters.COMMAND), handler),
                ]
            },
            fallbacks=[
                MessageHandler(filters.ALL, handlers.cancel_search_handler),
            ],
        )
    )


if __name__ == "__main__":
    dotenv.load_dotenv()
    token = os.environ.get(consts.TG_TOKEN_VAR)
    if token is None:
        raise Exception(f"{consts.TG_TOKEN_VAR} env variable is not present")

    application = ApplicationBuilder().token(token).concurrent_updates(True).build()

    application.add_error_handler(handlers.error_handler)

    add_query_handler(application, consts.TRACK_COMMAND, handlers.songs.search_handler)
    add_query_handler(application, consts.LYRICS_COMMAND, handlers.songs.search_lyrics_handler)
    add_query_handler(application, consts.VIDEO_COMMAND, handlers.video.search_handler)
    add_query_handler(application, consts.ALBUM_COMMAND, handlers.albums.search_handler)

    application.add_handler(CommandHandler(consts.START_COMMAND, handlers.start_handler))
    application.add_handler(CommandHandler(consts.HELP_COMMAND, handlers.help_handler))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handlers.message_handler))
    application.add_handler(CallbackQueryHandler(handlers.callback_handler))

    application.run_polling()
