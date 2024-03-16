from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler

from my_notion_telegram_bot.notion import NotionClient


MEDIA_ROW_OPTS = {
    "Anime": {
        "Animeid",
        "Animeflv",
        "Jkanime"
    },
}


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Hi, your chat_id is {update.effective_chat.id}",
    )


async def add_media_row(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # TODO: replace with conversation handler --> https://docs.python-telegram-bot.org/en/stable/telegram.ext.conversationhandler.html#conversationhandler
    await update.message.reply_text(
        "Please choose:",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(btn, callback_data=btn)
                for btn in MEDIA_ROW_OPTS.keys()
            ],
        ])
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    new_opts = MEDIA_ROW_OPTS.get(query.data)

    if new_opts:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(btn, callback_data=btn)
                    for btn in new_opts
                ],
            ])
        )
        return
    
    await query.edit_message_text(text="What is the anime title?")


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    notion_client = context.bot_data["notion_client"]
    rows = await notion_client.get_media_rows()

    for row in rows:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=str(row["properties"]["anime"]["title"][0]["text"]["content"]),
        )


command_handlers = [
    CommandHandler('get_chat_id', get_chat_id),
    CommandHandler('add_media_row', add_media_row),
    CallbackQueryHandler(button),
    CommandHandler('test', test),
]


def get_telegram_bot(token: str, notion_client: NotionClient) -> Application:
    app = ApplicationBuilder().token(token).build()
    app.bot_data |= {"notion_client": notion_client}

    for handler in command_handlers:
        app.add_handler(handler)

    return app
