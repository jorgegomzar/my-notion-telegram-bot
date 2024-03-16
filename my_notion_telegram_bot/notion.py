from notion_client import AsyncClient
from pydantic_settings import BaseSettings


class NotionClientConfig(BaseSettings):
    notion_token: str
    notion_media_db: str


class NotionClient:
    def __init__(self) -> None:
        self.config = NotionClientConfig()  # type: ignore
        self.conn = AsyncClient(auth=self.config.notion_token)

    async def get_media_rows(self):
        res = await self.conn.databases.query(**{
            "database_id": self.config.notion_media_db,
            "filter": {
                "property": "anime",
                "rich_text": {
                    "contains": "Metal"
                }
            }
        })
        return res["results"]
