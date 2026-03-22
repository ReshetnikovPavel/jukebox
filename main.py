import logging
import os

import dotenv
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)

import consts
import handlers
import handlers.albums
import handlers.songs
import handlers.video

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


if __name__ == "__main__":
    dotenv.load_dotenv()
    token = os.environ.get(consts.TG_TOKEN_VAR)
    if token is None:
        raise Exception(f"{consts.TG_TOKEN_VAR} env variable is not present")

    application = ApplicationBuilder().token(token).concurrent_updates(True).build()
    application.add_error_handler(handlers.error_handler)
    application.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler(
                    consts.LYRICS_COMMAND, handlers.songs.search_lyrics_handler
                )
            ],
            states={
                consts.CONVERSATION_HANDLER_REPEAT: [
                    CommandHandler(
                        consts.LYRICS_COMMAND, handlers.songs.search_lyrics_handler
                    ),
                    MessageHandler(
                        filters.TEXT & (~filters.COMMAND),
                        handlers.songs.search_lyrics_handler,
                    ),
                ]
            },
            fallbacks=[
                MessageHandler(filters.ALL, handlers.cancel_search_handler),
            ],
        )
    )
    application.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler(consts.VIDEO_COMMAND, handlers.video.search_handler)
            ],
            states={
                consts.CONVERSATION_HANDLER_REPEAT: [
                    CommandHandler(
                        consts.VIDEO_COMMAND, handlers.video.search_handler
                    ),
                    MessageHandler(
                        filters.TEXT & (~filters.COMMAND),
                        handlers.video.search_handler,
                    ),
                ]
            },
            fallbacks=[
                MessageHandler(filters.ALL, handlers.cancel_search_handler),
            ],
        )
    )
    application.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler(consts.ALBUM_COMMAND, handlers.albums.search_handler)
            ],
            states={
                consts.CONVERSATION_HANDLER_REPEAT: [
                    CommandHandler(
                        consts.ALBUM_COMMAND, handlers.albums.search_handler
                    ),
                    MessageHandler(
                        filters.TEXT & (~filters.COMMAND),
                        handlers.albums.search_handler,
                    ),
                ]
            },
            fallbacks=[
                MessageHandler(filters.ALL, handlers.cancel_search_handler),
            ],
        )
    )
    application.add_handler(
        CommandHandler(consts.START_COMMAND, handlers.start_handler)
    )
    application.add_handler(CommandHandler(consts.HELP_COMMAND, handlers.help_handler))
    application.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), handlers.message_handler)
    )
    application.add_handler(CallbackQueryHandler(handlers.callback_handler))
    application.run_polling()
