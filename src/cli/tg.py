import asyncio
from typing import Optional

import typer
from telegram import Message

from cli.logger_config import logger
from config import settings
from core.telegram import TelegramClient
from utils.converting_md2html import md_to_html
from utils.html_for_telegram import sanitize_html_for_telegram

app = typer.Typer(help="Команды для Telegram")

if not settings.TELEGRAM_BOT_TOKEN:
    logger.error("❌ Token отсутствует")

if not settings.TELEGRAM_CHANNEL:
    logger.error("❌ Tg канал отсутствует")

client = TelegramClient(settings.TELEGRAM_BOT_TOKEN or "None")
channel = settings.TELEGRAM_CHANNEL or "None"


@app.command()
def edit(msg_id: int, md_path: str):
    """
    Редактирует сообщение в Telegram-канале.
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
            logger.info(f"✅Отредактирован пост ID: {msg_id}")
        else:
            logger.warning(f"❌Ошибка редактирования ID {msg_id}: {result}")

    asyncio.run(_edit(msg_id, md_path))


@app.command()
def post(md_path: str):
    """
    Пост сообщение в Telegram-канале и добавление в него ID
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
            logger.debug(f"✅Опубликован пост ID: {msg_id}")
            return msg_id
        else:
            logger.warning(f"❌Ошибка публикации: {result}")
            return None

    async def _edit(msg_id: int) -> None:
        new_text = clean_html + "\n" + str(msg_id)
        result = await client.edit_message(channel, msg_id, new_text)
        if isinstance(result, Message):
            logger.info(f"✅Опубликован пост ID: {msg_id}")
        else:
            logger.warning(f"❌Ошибка поста ID {msg_id}: {result}")

    async def main():
        try:
            msg_id = await _post(clean_html)
            if msg_id is not None and settings.ADD_ID:
                await _edit(msg_id)
        except Exception as e:
            logger.warning(f"Ошибка постинга: {e}")

    asyncio.run(main())


@app.command()
def rm(msg_id: int):
    """
    Удаление из Telegram-канала сообщения по ID
    """

    async def _rm() -> None:
        res = await client.delete_message(chat_id=channel, message_id=msg_id)
        logger.info(f"Удаление поста ID {msg_id}: {'да' if res else 'нет'}")

    asyncio.run(_rm())


@app.command()
def img_post(photo_path: str, md_path: Optional[str] = None):
    """
    Пост изображения в Telegram-канал.
    Можно указать путь к локальному изображению или ссылку https
    \ntg img-post <photo_path> --md-path <option>
    """

    async def _img_post(photo_path: str, md_path: Optional[str]) -> None:
        res = await client.send_photo(
            chat_id=channel, photo_path=photo_path, md_path=md_path
        )
        if res:
            logger.info(f"Пост ID: {res.message_id}")
        else:
            logger.warning(f"Ошибка рамщешения поста {photo_path}: {res}")

    asyncio.run(_img_post(photo_path, md_path))


@app.command()
def img_edit(post_id: int, md_path: Optional[str] = None):
    """
    Редактировать текст изображения, само изображение для редактирования не доступно.
    Если передать только <post_id> то текст изображения удалится
    """

    async def _img_edit(post_id: int, md_path: Optional[str] = None) -> None:
        res = await client.edit_photo(
            chat_id=channel, message_id=post_id, md_path=md_path
        )

        if isinstance(res, Message):
            logger.info(f"Отредактирован пост ID: {res.message_id}")
        else:
            logger.warning(f"Ошибка редактирования поста: {res}")

    asyncio.run(_img_edit(post_id=post_id, md_path=md_path))


app.command("e", help="Алиас для edit")(edit)
app.command("p", help="Алиас для post")(post)
app.command("ip", help="Алиас для img_post")(img_post)
app.command("ie", help="Алиас для img_edit")(img_edit)
