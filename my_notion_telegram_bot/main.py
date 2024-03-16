from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from my_notion_telegram_bot.notion import NotionClient
from my_notion_telegram_bot.telegram import get_telegram_bot
from my_notion_telegram_bot.utils import get_logger


class MyNotionTelegramBotConfig(BaseSettings):
    telegram_token: str


class MyNotionTelegramBot:
    def __init__(self):
        load_dotenv()
        self.config = MyNotionTelegramBotConfig()  # type: ignore
        self.logger = get_logger(self.__class__.__name__)

        try:
            self.notion_client = NotionClient()
        except Exception as e:
            self.logger.error("Could not init Notion client")
            raise e

        try:
            self.telegram_bot = get_telegram_bot(
                self.config.telegram_token,
                self.notion_client
            )
        except Exception as e:
            self.logger.error("Could not init Telegram Bot")
            raise e

        self.logger.info("Ready")

    def run(self):
        self.logger.info("Running")
        self.telegram_bot.run_polling()  # type: ignore
        self.logger.info("Bye")
