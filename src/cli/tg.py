import asyncio
from typing import Optional

import typer
from telegram import Message

from cli.logger_config import logger
from config import settings
from core.telegram import TelegramClient
from utils.converting_md2html import md_to_html
from utils.html_for_telegram import sanitize_html_for_telegram
from utils.i18n import i18n
from i18n.i18n_keys import I18NKey


app = typer.Typer(help=i18n.get(I18NKey.CLI_TELEGRAM_COMMANDS))

if not settings.TELEGRAM_BOT_TOKEN:
    logger.error(i18n.get(I18NKey.ERRORS_MISSING_TOKEN))

if not settings.TELEGRAM_CHANNEL:
    logger.error(i18n.get(I18NKey.ERRORS_MISSING_CHANNEL))

client = TelegramClient(settings.TELEGRAM_BOT_TOKEN or "None")
channel = settings.TELEGRAM_CHANNEL or "None"


@app.command(help=i18n.get(I18NKey.CLI_TG_EDIT))
def edit(msg_id: int, md_path: str):
    """
    Edits a message in the Telegram channel.
    """

    async def _edit(msg_id: int, md_path: str) -> None:
        html = md_to_html(md_path)
        clean_html = sanitize_html_for_telegram(
            html,
            base_path=md_path,
            imgbb_api_key=settings.IMGBB_API_KEY,
        )
        result = await client.edit_message(channel, msg_id, clean_html)
        if isinstance(result, Message):
            logger.info(f"{i18n.get(I18NKey.SUCCESS_SAVE_SUCCESS)} ID {msg_id}")
        else:
            logger.warning(
                f"{i18n.get(I18NKey.ERRORS_API_ERROR)} ID {msg_id}: {result}"
            )

    asyncio.run(_edit(msg_id, md_path))


@app.command(help=i18n.get(I18NKey.CLI_TG_POST))
def post(md_path: str):
    """
    Posting a message in the Telegram channel and adding an ID to it (optional)
    """
    html = md_to_html(md_path)
    clean_html = sanitize_html_for_telegram(
        html,
        base_path=md_path,
        imgbb_api_key=settings.IMGBB_API_KEY,
    )

    async def _post(text) -> Optional[int]:
        result = await client.send_message(chat_id=channel, text=text)
        if isinstance(result, Message):
            msg_id = result.message_id
            logger.info(f"{i18n.get(I18NKey.SUCCESS_SAVE_SUCCESS)} ID {msg_id}")
            return msg_id
        else:
            logger.warning(f"{i18n.get(I18NKey.ERRORS_API_ERROR)} {result}")
            return None

    async def _edit(msg_id: int) -> None:
        new_text = clean_html + "\n" + str(msg_id)
        result = await client.edit_message(channel, msg_id, new_text)
        if isinstance(result, Message):
            logger.info(f"{i18n.get(I18NKey.SUCCESS_SAVE_SUCCESS)} ID {msg_id}")
        else:
            logger.warning(
                f"{i18n.get(I18NKey.ERRORS_API_ERROR)} ID {msg_id}: {result}"
            )

    async def main():
        try:
            msg_id = await _post(clean_html)
            if msg_id is not None and settings.ADD_ID:
                await _edit(msg_id)
        except Exception as e:
            logger.warning(f"{i18n.get(I18NKey.ERRORS_API_ERROR)} {e}")

    asyncio.run(main())


@app.command(help=i18n.get(I18NKey.CLI_TG_RM_MSG))
def rm(msg_id: int):
    """
    Deleting a message by ID from the Telegram channel
    """

    async def _rm() -> None:
        res = await client.delete_message(chat_id=channel, message_id=msg_id)
        logger.info(
            f"{i18n.get(I18NKey.SUCCESS_RESULT)} ID {msg_id}: {'yes' if res else 'no'}"
        )

    asyncio.run(_rm())


@app.command(help=i18n.get(I18NKey.CLI_TG_IMG_POST))
def img_post(photo_path: str, md_path: Optional[str] = None):
    """
    Post the image to the Telegram channel.
    """

    async def _img_post(photo_path: str, md_path: Optional[str]) -> None:
        res = await client.send_photo(
            chat_id=channel, photo_path=photo_path, md_path=md_path
        )
        if res:
            logger.info(f"{i18n.get(I18NKey.SUCCESS_RESULT)}  ID: {res.message_id}")
        else:
            logger.warning(f"{i18n.get(I18NKey.ERRORS_API_ERROR)}  {photo_path}: {res}")

    asyncio.run(_img_post(photo_path, md_path))


@app.command(help=i18n.get(I18NKey.CLI_TG_IMG_EDIT))
def img_edit(msg_id: int, md_path: Optional[str] = None):
    """
    Edit the text of the image, the image itself is not available for editing.
    """

    async def _img_edit(msg_id: int, md_path: Optional[str] = None) -> None:
        res = await client.edit_photo(
            chat_id=channel, message_id=msg_id, md_path=md_path
        )

        if isinstance(res, Message):
            logger.info(
                f"{i18n.get(I18NKey.SUCCESS_SAVE_SUCCESS)} ID: {res.message_id}"
            )
        else:
            logger.warning(f"{i18n.get(I18NKey.ERRORS_API_ERROR)} {res}")

    asyncio.run(_img_edit(msg_id, md_path))


app.command("e", help=i18n.get(I18NKey.ALIAS_EDIT))(edit)
app.command("p", help=i18n.get(I18NKey.ALIAS_POST))(post)
app.command("ip", help=i18n.get(I18NKey.ALIAS_IMG_POST))(img_post)
app.command("ie", help=i18n.get(I18NKey.ALIAS_TG_IMG_EDIT))(img_edit)
