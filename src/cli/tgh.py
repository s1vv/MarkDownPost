import asyncio
from typing import Optional

import typer
from telegram import Message

from cli.logger_config import logger
from config import settings
from core.telegram import TelegramClient
from core.telegraph import TelegraphClient
from utils.i18n import i18n
from i18n.i18n_keys import I18NKey

app = typer.Typer(help=i18n.get(I18NKey.CLI_TELEGRAPH_TELEGRAM_COMMAND))

if not settings.TELEGRAM_BOT_TOKEN:
    logger.critical(f"{i18n.get(I18NKey.ERRORS_MISSING_TOKEN)}: Telegram")
if not settings.TELEGRAM_CHANNEL:
    logger.critical(f"{i18n.get(I18NKey.ERRORS_MISSING_CHANNEL)}")

TgClient = TelegramClient(settings.TELEGRAM_BOT_TOKEN or "None")
GrClient = TelegraphClient(settings.TELEGRAPH_ACCESS_TOKEN)
channel = settings.TELEGRAM_CHANNEL or "None"


@app.command(help=i18n.get(I18NKey.CLI_TELEGRAPH_TELEGRAM_COMMAND))
def post(md_path: str, title: Optional[str] = None):
    """
    A post in the Telegraph and a link to the Telegram page
    """
    result = GrClient.create_page(title=title, md_path=md_path)
    if result.get("url"):
        logger.info(f": {result["url"]}")

        async def _send_msg(url: str):
            result = await TgClient.send_message(chat_id=channel, text=url)
            if isinstance(result, Message):
                logger.info(
                    f"{i18n.get(I18NKey.SUCCESS_RESULT)} ID: {result.message_id}"
                )
            else:
                logger.warning(f"{i18n.get(I18NKey.ERRORS_API_ERROR)} {md_path}")

        asyncio.run(_send_msg(result["url"]))
    else:
        logger.warning(f"{i18n.get(I18NKey.ERRORS_API_ERROR)} {md_path}: {result}")


app.command("p", help=i18n.get(I18NKey.ALIAS_POST))(post)
