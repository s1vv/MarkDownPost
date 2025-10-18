import asyncio
import logging
from datetime import timedelta
from pathlib import Path
from typing import Optional, Union

from telegram import Bot, InputFile, LinkPreviewOptions, Message
from telegram.error import RetryAfter, TelegramError

from utils.converting_md2html import md_to_html
from utils.html_for_telegram import sanitize_html_for_telegram

logger = logging.getLogger(__name__)


class TelegramClient:
    def __init__(self, token: str) -> None:
        """Создает клиента Telegram API."""
        self.bot = Bot(token=token)

    async def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        parse_mode: Optional[str] = "HTML",
        disable_web_page_preview: bool = False,
        link_preview_options=LinkPreviewOptions(
            is_disabled=False,
            prefer_large_media=False,  # маленькое превью
            show_above_text=False,  # превью под текстом
        ),
    ) -> Optional[Message | TelegramError]:
        """Отправка текстового сообщения."""
        try:
            return await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview,
                link_preview_options=link_preview_options,
                connect_timeout=20.0,
            )
        except RetryAfter as e:
            if isinstance(e.retry_after, timedelta):
                delay: float = e.retry_after.total_seconds()
            else:
                delay = float(e.retry_after)
            logger.warning(f"Rate limit, жду {delay:.2f} сек...")
            await asyncio.sleep(delay)
            return await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview,
            )
        except TelegramError as e:
            return e

    async def edit_message(
        self,
        chat_id: Union[int, str],
        message_id: int,
        new_text: str,
        parse_mode: Optional[str] = "HTML",
        disable_web_page_preview: bool = False,
    ) -> Optional[Message | TelegramError | bool]:
        """Редактирует существующее сообщение по ID."""
        try:
            return await self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=new_text,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview,
                connect_timeout=20.0,
            )
        except RetryAfter as e:
            if isinstance(e.retry_after, timedelta):
                delay = e.retry_after.total_seconds()
            else:
                delay = float(e.retry_after)
            logger.warning(f"Rate limit при редактировании, жду {delay:.2f} сек...")
            await asyncio.sleep(delay)
            return await self.edit_message(
                chat_id, message_id, new_text, parse_mode, disable_web_page_preview
            )
        except TelegramError as e:
            return e

    async def send_photo(
        self,
        chat_id: Union[int, str],
        photo_path: str,
        md_path: Optional[str] = None,
        parse_mode: Optional[str] = "HTML",
    ) -> Optional[Message]:
        """Отправка изображения с подписью."""
        html: Optional[str] = None
        if md_path:
            html = md_to_html(md_path)
            html = sanitize_html_for_telegram(html=html, base_path=md_path)
        try:
            if not photo_path.startswith("http"):
                path = Path(photo_path).expanduser().resolve()
                with open(path, "rb") as photo_file:
                    input_file = InputFile(photo_file)
            else:
                input_file = photo_path
            return await self.bot.send_photo(
                chat_id=chat_id,
                photo=input_file,
                caption=html or md_path,
                connect_timeout=20.0,
                parse_mode=parse_mode,
            )
        except RetryAfter as e:
            if isinstance(e.retry_after, timedelta):
                delay = e.retry_after.total_seconds()
            else:
                delay = float(e.retry_after)
            logger.warning(f"Rate limit при отправке фото, жду {delay:.2f} сек...")
            await asyncio.sleep(delay)
            return await self.send_photo(chat_id, photo_path, md_path, parse_mode)
        except TelegramError as e:
            logger.error(f"Ошибка при отправке фото: {e}")
            return None
        except FileNotFoundError:
            logger.error(f"Файл не найден: {photo_path}")
            return None

    async def edit_photo(
        self,
        chat_id: Union[int, str],
        message_id: int,
        md_path: Optional[str] = None,
        parse_mode: Optional[str] = "HTML",
    ) -> Message | bool:
        """Отправка изображения с подписью."""
        html: Optional[str] = None
        if md_path:
            html = md_to_html(md_path)
            html = sanitize_html_for_telegram(html=html, base_path=md_path)
        try:
            return await self.bot.edit_message_caption(
                chat_id=chat_id,
                message_id=message_id,
                caption=html or md_path,
                connect_timeout=20.0,
                parse_mode=parse_mode,
            )
        except RetryAfter as e:
            if isinstance(e.retry_after, timedelta):
                delay = e.retry_after.total_seconds()
            else:
                delay = float(e.retry_after)
            logger.warning(f"Rate limit при отправке фото, жду {delay:.2f} сек...")
            await asyncio.sleep(delay)
            return await self.edit_photo(chat_id, message_id, md_path, parse_mode)

    async def delete_message(self, chat_id: Union[int, str], message_id: int) -> bool:
        """Удаляет сообщение по ID."""
        try:
            await self.bot.delete_message(
                chat_id=chat_id,
                message_id=message_id,
                connect_timeout=20.0,
            )
            return True
        except TelegramError as e:
            logger.error(f"Ошибка при удалении сообщения: {e}")
            return False
