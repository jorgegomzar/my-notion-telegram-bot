import enum
from logging import getLogger
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, ConversationHandler

from my_notion_telegram_bot.notion import NotionClient


class ConversationFlags(str, enum.Enum):
    START_OVER = enum.auto()


class AddMediaRowStates(enum.Enum):
    STOPPING = enum.auto()
    SELECTING_MEDIA_TYPE = enum.auto()
    SELECTING_ANIME_SOURCE = enum.auto()
    WAITING_FOR_ANIME_URL = enum.auto()


class AddMediaRowCallbacks(str, enum.Enum):
    STOP = enum.auto()
    ADD_ANIME = enum.auto()
    ADD_MANGA = enum.auto()
    ADD_SERIE = enum.auto()
    ADD_FILM = enum.auto()



async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End Conversation by command."""
    text = "Okay, bye!"

    await update.callback_query.answer()
    getLogger("STOP").info("STOP")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text
    )

    return ConversationHandler.END


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Hi, your chat_id is {update.effective_chat.id}",
    )


async def add_media_row(update: Update, context: ContextTypes.DEFAULT_TYPE) -> AddMediaRowStates:
    """Entrypoint for adding rows to Media DB in Notion."""
    text = (
        "Let's add rows to the media DB in Notion!\n\n"
        "What media type do you want to add?"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="Anime", callback_data=AddMediaRowCallbacks.ADD_ANIME.value),
            InlineKeyboardButton(text="Manga", callback_data=AddMediaRowCallbacks.ADD_MANGA.value),
        ],
        [
            InlineKeyboardButton(text="Serie", callback_data=AddMediaRowCallbacks.ADD_SERIE.value),
            InlineKeyboardButton(text="Film", callback_data=AddMediaRowCallbacks.ADD_FILM.value),
        ],
        [
            InlineKeyboardButton(text="Cancel", callback_data=AddMediaRowCallbacks.STOP.value),
        ],
    ])

    # If we're starting over we don't need to send a new message
    if context.user_data.get(ConversationFlags.START_OVER):
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        await update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[ConversationFlags.START_OVER] = False
    return AddMediaRowStates.SELECTING_MEDIA_TYPE


async def add_media_row_anime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> AddMediaRowStates:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text="Please, paste the URL now...")
    
    return AddMediaRowStates.WAITING_FOR_ANIME_URL


async def add_media_row_manga(update: Update, context: ContextTypes.DEFAULT_TYPE) -> AddMediaRowStates:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text="You selected Manga")

    return ConversationHandler.END


async def add_media_row_serie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> AddMediaRowStates:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text="You selected Serie")

    return ConversationHandler.END

async def add_media_row_film(update: Update, context: ContextTypes.DEFAULT_TYPE) -> AddMediaRowStates:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text="You selected Film")

    return ConversationHandler.END

async def add_media_row_anime_from_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> AddMediaRowStates:
    anime_url = AddMediaRowCallbacks(update.effective_chat.message)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=(
        f"You selected {anime_source.name}\n\n"
        "Please paste the URL now."
    ))

    return ConversationHandler.END

command_handlers = [
    CommandHandler('get_chat_id', get_chat_id),
    ConversationHandler(
        entry_points=[CommandHandler("add_media_row", add_media_row)],
        states={
            AddMediaRowStates.SELECTING_MEDIA_TYPE: [
                CallbackQueryHandler(
                    add_media_row_anime,
                    pattern=f"^{AddMediaRowCallbacks.ADD_ANIME.value}$",
                ),
                CallbackQueryHandler(
                    add_media_row_manga,
                    pattern=f"^{AddMediaRowCallbacks.ADD_MANGA.value}$",
                ),
                CallbackQueryHandler(
                    add_media_row_serie,
                    pattern=f"^{AddMediaRowCallbacks.ADD_SERIE.value}$",
                ),
                CallbackQueryHandler(
                    add_media_row_film,
                    pattern=f"^{AddMediaRowCallbacks.ADD_FILM.value}$",
                ),
            ],
            AddMediaRowStates.WAITING_FOR_ANIME_URL: [CallbackQueryHandler(add_media_row_anime_from_url)],
        },
        fallbacks=[CommandHandler("stop", stop)]
    ),
]


def get_telegram_bot(token: str, notion_client: NotionClient) -> Application:
    app = ApplicationBuilder().token(token).build()
    app.bot_data |= {"notion_client": notion_client}

    for handler in command_handlers:
        app.add_handler(handler)

    return app
