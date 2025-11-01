import json
from logging import ERROR
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import typer
from rich.console import Console
from rich.table import Table

from cli.logger_config import logger
from config import settings
from core.telegraph import TelegraphClient
from utils.i18n import i18n
from i18n.i18n_keys import I18NKey

app = typer.Typer(help=i18n.get(I18NKey.CLI_TELEGRAPH_COMMANDS))
console = Console()

if not settings.TELEGRAM_BOT_TOKEN:
    logger.warning(i18n.get(I18NKey.ERRORS_MISSING_TOKEN))

telegraph_token = None

def _get_token_telegraph() -> str:
    from config.settings import ENV_FILE, AUTHOR_NAME
    from core.telegraph import Telegraph
    from dotenv import load_dotenv, set_key

    answer = input(i18n.get(I18NKey.TELEGRAPH_ENV_TOKEN_REQUEST)).strip().lower()

    if answer not in ["y", "yes", "д", "да"]:
        logger.warning(i18n.get(I18NKey.TELEGRAPH_ENV_TOKEN_NOT_CREATED))
        raise SystemExit(1)

    # Создаём новый аккаунт в Telegraph
    telegraph = Telegraph()
    acc = telegraph.create_account(short_name=AUTHOR_NAME)
    new_token = acc["access_token"]
    logger.info(i18n.get(I18NKey.TELEGRAPH_ENV_TOKEN_CREATED), new_token)

    # Сохраняем токен в тот .env, который реально используется (ENV_FILE)
    if not ENV_FILE:
        logger.error(i18n.get(I18NKey.ERRORS_ENV_NOT_FOUND))
        return new_token

    try:
        # set_key ожидает путь как строку или Path; убедимся что директория и файл существуют
        ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not ENV_FILE.exists():
            ENV_FILE.touch()
        # Записываем в файл .env
        set_key(str(ENV_FILE), "TELEGRAPH_ACCESS_TOKEN", new_token)
        logger.info(i18n.get(I18NKey.SUCCESS_SAVE_SUCCESS), ENV_FILE)
        # Подгрузим обновлённые переменные (опционально)
        load_dotenv(ENV_FILE, override=True)
    except Exception as e:
        logger.error(i18n.get(I18NKey.ERRORS_SAVE_ERROR), ENV_FILE, e)

    return new_token

if not settings.TELEGRAPH_ACCESS_TOKEN:
    telegraph_token = _get_token_telegraph()
    
client = TelegraphClient(telegraph_token or "None")


@app.command(help=i18n.get(I18NKey.CLI_GR_EDIT))
def edit(page_path: str, md_path: str, title: Optional[str] = None):
    """
    Page Editing: mdp gr edit page-address path/to/file.md, optionally use --title, then title is not extracted from # in .md"
    """
    result = client.edit_page(
        path=page_path,
        md_path=md_path,
        author_name=settings.AUTHOR_NAME,
        author_url=settings.AUTHOR_URL,
        title=title,
    )
    if result["path"] == page_path:
        logger.info(f"{i18n.get(I18NKey.SUCCESS_SAVE_SUCCESS)} {result["url"]}")
    else:
        logger.warning(f"{i18n.get(I18NKey.ERRORS_API_ERROR)} {page_path}")


@app.command(help=i18n.get(I18NKey.CLI_GR_POST))
def post(md_path: str, title=None):
    """
    "Creating a page: mdp gr post path/to/file.md, optionally use --title,
    then title is not extracted from # in .md""
    """
    result = client.create_page(md_path=md_path, title=title)
    if result.get("url"):
        logger.info(f"{i18n.get(I18NKey.SUCCESS_SAVE_SUCCESS)} {result["url"]}")
    else:
        logger.warning(f"{i18n.get(I18NKey.ERRORS_API_ERROR)} {md_path}")


@app.command()
def get_pages_list(
    output_path: str = typer.Option(None),
    limit: int = typer.Option(50),
):
    """
    Retrieves the list of account pages.
    If the --output-path parameter is specified, saves the result to an Excel file (with timestamp added).
    Otherwise, it prints a short table to the console.
    """
    all_pages: list[dict] = []
    offset = 0

    while True:
        try:
            data = client.get_pages_list(limit=limit, offset=offset)
        except Exception as e:
            logger.critical(f"{i18n.get(I18NKey.ERRORS_API_ERROR)} {e}")
            sys.exit(1)

        if not isinstance(data, dict):
            logger.critical(f"{i18n.get(I18NKey.ERRORS_API_ERROR)} !=.json")
            sys.exit(1)

        if not data.get("ok"):
            logger.critical(f"{i18n.get(I18NKey.ERRORS_API_ERROR)} {data}")
            sys.exit(1)

        result = data.get("result", {})
        pages = result.get("pages", [])
        all_pages.extend(pages)

        total_count = result.get("total_count", 0) or 0
        offset += limit

        if offset >= total_count:
            break

    if not all_pages:
        logger.warning(f"{i18n.get(I18NKey.ERRORS_API_ERROR)} no data")
        return

    # If the path is not specified, we print a short table to the console.
    if not output_path:
        table = Table(title=i18n.get(I18NKey.TABLE_TITLES_PGS_LST), show_lines=False)
        table.add_column("№", justify="right", style="cyan", no_wrap=True)
        table.add_column(i18n.get(I18NKey.TABLE_TITLES_TITLE), style="bold")
        table.add_column(i18n.get(I18NKey.TABLE_TITLES_PATH), style="magenta")
        table.add_column(
            i18n.get(I18NKey.TABLE_TITLES_VIEWS), justify="right", style="green"
        )

        for i, page in enumerate(all_pages, start=1):
            title = page.get("title", "-")
            if title == "Deleted":
                continue
            path = page.get("path", "-")
            views = str(page.get("views", "-"))
            table.add_row(str(i), title, path, views)

        console.print(table)
        return

    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    out_path = Path(output_path)

    if out_path.exists() and out_path.is_dir():
        out_path = out_path / f"pages_list_{timestamp}.xlsx"
    else:
        if out_path.suffix:
            out_path = out_path.with_name(
                f"{out_path.stem}_{timestamp}{out_path.suffix}"
            )
        else:
            out_path = out_path.with_name(f"{out_path.name}_{timestamp}.xlsx")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        df = pd.DataFrame(all_pages)
        if df.empty:
            logger.warning(f"{i18n.get(I18NKey.ERRORS_SAVE_ERROR)} no data")
            return

        df.to_excel(out_path, index=False)
        logger.info(
            f"{i18n.get(I18NKey.SUCCESS_SAVE_SUCCESS)} {out_path.resolve()}: {len(df)})"
        )
    except Exception as e:
        logger.warning(f"{i18n.get(I18NKey.ERRORS_SAVE_ERROR)} {e}")
        try:
            fallback = out_path.with_suffix(".json")
            with open(fallback, "w", encoding="utf-8") as f:
                json.dump({"pages": all_pages}, f, ensure_ascii=False, indent=2)
            logger.warning(f"{I18NKey.ERRORS_SAVE_ERROR} -> {fallback}")
        except Exception as e2:
            logger.critical(f"{I18NKey.ERRORS_SAVE_ERROR} {e2}")
            sys.exit(1)


@app.command()
def rm(path: str):
    result = client.delete_page(path)
    logger.info(f"{path} - {result["title"]}")


app.command("e", help=i18n.get(I18NKey.ALIAS_EDIT))(edit)
app.command("p", help=i18n.get(I18NKey.ALIAS_POST))(post)
app.command("gpl", help=i18n.get(I18NKey.ALIAS_GET_PAGES_LIST))(get_pages_list)

