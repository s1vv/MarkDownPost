import asyncio
from typing import Optional

import typer
from telegram import Message

from cli.logger_config import logger
from config import settings
from core.telegram import TelegramClient
from core.telegraph import TelegraphClient

app = typer.Typer(help="Пост Telegragph и ссылки в TG")

if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAPH_ACCESS_TOKEN:
    logger.critical("TG или Telegrah токен не найден")
if not settings.TELEGRAM_CHANNEL:
    logger.critical("ID TG канала не найдено")

TgClient = TelegramClient(settings.TELEGRAM_BOT_TOKEN or "None")
GrClient = TelegraphClient(settings.TELEGRAPH_ACCESS_TOKEN or "None")
channel = settings.TELEGRAM_CHANNEL or "None"


@app.command()
def post(md_path: str, title: Optional[str] = None):
    """
    Создание страницы в Telegragh и её пост TG
    """
    result = GrClient.create_page(title=title, md_path=md_path)
    if result.get("url"):
        logger.info(f"Страница создана: {result["url"]}")

        async def _send_msg(url: str):
            result = await TgClient.send_message(chat_id=channel, text=url)
            if isinstance(result, Message):
                logger.info(f"Пост в TG ID: {result.message_id}")
            else:
                logger.warning(f"Ошибка поста в TG: {md_path}")

        asyncio.run(_send_msg(result["url"]))
    else:
        logger.warning(f"Ошибка создания страницы {md_path} в Telegraph: {result}")


app.command("p", help="Алиас для post")(post)
