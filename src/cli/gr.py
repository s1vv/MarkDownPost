import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import typer
from rich.console import Console
from rich.table import Table

from cli.logger_config import logger
from config import settings
from core.telegraph import TelegraphClient

app = typer.Typer(help="Команды для TeleGraph")
console = Console()

if not settings.TELEGRAM_BOT_TOKEN:
    logger.warning("❌ Token отсутствует")

if not settings.TELEGRAM_CHANNEL:
    logger.warning("❌ Tg канал отсутствует")

client = TelegraphClient(settings.TELEGRAPH_ACCESS_TOKEN or "None")
channel = settings.TELEGRAM_CHANNEL or "None"


@app.command()
def edit(page_path: str, md_path: str):
    """
    Редактирует сообщение в Telegram-канале.
    """
    result = client.edit_page(
        path=page_path,
        md_path=md_path,
        author_name=settings.AUTHOR_NAME,
        author_url=settings.AUTHOR_URL,
        title=None,
    )
    if result["path"] == page_path:
        logger.info(f"Страница {result["url"]} отредактирована")
    else:
        logger.warning(f"Ошибка редактирования страницы: {page_path}")


@app.command()
def post(md_path: str, title=None):
    """
    Пост страницы в Telegraph
    """
    result = client.create_page(md_path=md_path, title=title)
    if result.get("url"):
        logger.info(f"Страница доступна по адресу: {result["url"]}")
    else:
        logger.warning(f"Ошибка создания страницы из: {md_path}")


@app.command()
def get_pages_list(
    output_path: str = typer.Option(
        None,
        help="Путь к файлу для сохранения результата (папка или имя файла). Если не указан — вывод в консоль.",
    ),
    limit: int = typer.Option(50, help="Количество элементов за один запрос к API"),
):
    """
    Возвращает список страниц аккаунта.
    Если указан параметр --output-path, сохраняет результат в Excel-файл (с добавлением timestamp).
    Иначе — печатает краткую таблицу в консоль.
    """
    all_pages: list[dict] = []
    offset = 0

    # пагинация: запрашиваем пока не соберём total_count страниц
    while True:
        try:
            data = client.get_pages_list(limit=limit, offset=offset)
        except Exception as e:
            logger.critical(f"Ошибка при запросе к Telegraph API: {e}")
            sys.exit(1)

        if not isinstance(data, dict):
            logger.critical(
                "Ошибка: ответ API не является словарём (ожидалось .json())."
            )
            sys.exit(1)

        if not data.get("ok"):
            logger.critical(f"Ошибка Telegraph API: {data}")
            sys.exit(1)

        result = data.get("result", {})
        pages = result.get("pages", [])
        # pages — список словарей; добавляем их в общий список
        all_pages.extend(pages)

        total_count = result.get("total_count", 0) or 0
        offset += limit

        if offset >= total_count:
            break

    # Нет данных
    if not all_pages:
        logger.warning("В ответе нет страниц для отображения или сохранения.")
        return

    # Если путь не указан — печатаем короткую таблицу в консоль
    if not output_path:
        table = Table(title="Список страниц", show_lines=False)
        table.add_column("№", justify="right", style="cyan", no_wrap=True)
        table.add_column("Заголовок", style="bold")
        table.add_column("Путь", style="magenta")
        table.add_column("Просмотры", justify="right", style="green")

        for i, page in enumerate(all_pages, start=1):
            title = page.get("title", "-")
            if title == "Deleted":
                continue
            path = page.get("path", "-")
            views = str(page.get("views", "-"))
            table.add_row(str(i), title, path, views)

        console.print(table)
        return

    # Если указан путь — сохраняем в Excel с timestamp
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    out_path = Path(output_path)

    # Если указан каталог — положим файл туда
    if out_path.exists() and out_path.is_dir():
        out_path = out_path / f"pages_list_{timestamp}.xlsx"
    else:
        # если указан файл с расширением — вставим timestamp перед расширением
        if out_path.suffix:
            out_path = out_path.with_name(
                f"{out_path.stem}_{timestamp}{out_path.suffix}"
            )
        else:
            # если указан путь без расширения — дополним .xlsx
            out_path = out_path.with_name(f"{out_path.name}_{timestamp}.xlsx")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Сохраняем в Excel
    try:
        df = pd.DataFrame(all_pages)
        # если DataFrame пустой — предупредим
        if df.empty:
            logger.warning("Данные для сохранения пусты — файл не создан.")
            return

        df.to_excel(out_path, index=False)
        logger.info(f"Результат сохранён: {out_path.resolve()} (строк: {len(df)})")
    except Exception as e:
        logger.warning(f"Ошибка при сохранении в Excel: {e}")
        # на всякий случай можно сохранить исходный JSON рядом
        try:
            fallback = out_path.with_suffix(".json")
            with open(fallback, "w", encoding="utf-8") as f:
                json.dump({"pages": all_pages}, f, ensure_ascii=False, indent=2)
            logger.warning(
                f"Сохранение в Excel не удалось — создал fallback JSON: {fallback}"
            )
        except Exception as e2:
            logger.critical(f"Не удалось сохранить ни Excel, ни JSON fallback: {e2}")
            sys.exit(1)


@app.command()
def rm(path: str):
    result = client.delete_page(path)
    logger.info(f"{path} - {result["title"]}")


app.command("e", help="Алиас для edit")(edit)
app.command("p", help="Алиас для post")(post)
app.command("gpl", help="Алиас для get_pages_list")(get_pages_list)
