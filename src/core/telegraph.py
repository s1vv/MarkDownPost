from typing import Any, Dict, Optional

import requests
from telegraph import Telegraph

from utils.md2telegraph import markdown_to_telegraph_nodes

TELEGRAPH_UPLOAD_URL = "https://telegra.ph/upload"
TELEGRAPH_API_URL = "https://api.telegra.ph"

def _get_token_telegraph() -> str:
    from config.settings import ENV_FILE, AUTHOR_NAME
    from core.telegraph import Telegraph
    from dotenv import load_dotenv, set_key
    from utils.i18n import i18n
    from i18n.i18n_keys import I18NKey
    from cli.logger_config import logger
    
    answer = input(i18n.get(I18NKey.TELEGRAPH_ENV_TOKEN_REQUEST)).strip().lower()

    if answer not in ["y", "yes", "д", "да"]:
        logger.warning(i18n.get(I18NKey.TELEGRAPH_ENV_TOKEN_NOT_CREATED))
        raise SystemExit(1)

    # Создаём новый аккаунт в Telegraph
    telegraph = Telegraph()
    acc = telegraph.create_account(short_name=AUTHOR_NAME)
    new_token = acc["access_token"]
    logger.info(i18n.get(f"{I18NKey.TELEGRAPH_ENV_TOKEN_CREATED} {new_token}"))

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
        logger.info(f"{i18n.get(I18NKey.SUCCESS_SAVE_SUCCESS)} {ENV_FILE}")
        # Подгрузим обновлённые переменные (опционально)
        load_dotenv(ENV_FILE, override=True)
    except Exception as e:
        logger.error(f"{i18n.get(I18NKey.ERRORS_SAVE_ERROR)} {ENV_FILE} {e}")

    return new_token

class TelegraphClient:
    def __init__(self, access_token: str | None):
        if access_token is None or not access_token:
            access_token = _get_token_telegraph()
        self.client = Telegraph(access_token)
        self.access_token = access_token

    def upload_file(self, path: str) -> str:
        """
        Uploads a file (jpg/png/gif/mp4/mp3) to Telegraph and returns the URL. Outdated?
        """
        with open(path, "rb") as f:
            r = requests.post(TELEGRAPH_UPLOAD_URL, files={"file": f})
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list) and data and "src" in data[0]:
            return "https://telegra.ph" + data[0]["src"]
        raise RuntimeError(f"Telegraph upload error: {data}")

    def create_page(
        self,
        title: str | None,
        md_path: str,
        author_name: Optional[str] = None,
        author_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creates a new page in the Telegraph.
        Returns the API's JSON response.
        """
        html_content, title_from_html = markdown_to_telegraph_nodes(md_path)
        title = title or title_from_html or "None"
        result_tgraph = self.client.create_page(
            title, html_content, author_name, author_url
        )
        return result_tgraph

    def edit_page(
        self,
        path: str,
        title: str | None,
        md_path: str,
        author_name: Optional[str] = None,
        author_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Edits an existing page.
        """
        html_content, title_from_html = markdown_to_telegraph_nodes(md_path)
        title = title or title_from_html or "None"
        result = self.client.edit_page(
            path, title, html_content, author_name, author_url
        )
        return result

    def get_page(self, path: str, return_content: bool = True) -> Dict[str, Any]:
        """
        Retrieves the page by path.
        """
        params = {"return_content": str(return_content).lower()}
        r = requests.get(f"{TELEGRAPH_API_URL}/getPage/{path}", params=params)
        r.raise_for_status()
        return r.json()

    def get_pages_list(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Retrieves the list of account pages.
        """
        params = {
            "access_token": self.access_token,
            "limit": limit,
            "offset": offset,
        }
        r = requests.get(f"{TELEGRAPH_API_URL}/getPageList", params=params)
        return r.json()

    def delete_page(self, path: str, title: str = "Deleted") -> dict:
        """
        Simulation of page deletion — we erase the empty HTML.
        """
        html_content = [{"tag": "p", "children": [" "]}]
        result = self.client.edit_page(
            path=path, title=title, author_name="", author_url="", content=html_content
        )
        return result
