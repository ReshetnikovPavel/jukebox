from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler


async def cancel_search_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    chat = update.effective_chat
    assert chat is not None

    await context.bot.send_message(chat.id, "Поиск отменен. Напишите запрос или команду")
    return ConversationHandler.END
