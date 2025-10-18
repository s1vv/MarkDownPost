from typing import Any, Dict, Optional

import requests
from telegraph import Telegraph

from utils.md2telegraph import markdown_to_telegraph_nodes

TELEGRAPH_UPLOAD_URL = "https://telegra.ph/upload"
TELEGRAPH_API_URL = "https://api.telegra.ph"


class TelegraphClient:
    def __init__(self, access_token: str | None):
        self.client = Telegraph(access_token=access_token)
        self.access_token = access_token

    def upload_file(self, path: str) -> str:
        """
        Загружает файл (jpg/png/gif/mp4/mp3) на Telegraph и возвращает URL. Устарел?
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
        Создаёт новую страницу в Telegraph.
        Возвращает JSON-ответ API.
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
        Редактирует существующую страницу.
        """
        html_content, title_from_html = markdown_to_telegraph_nodes(md_path)
        title = title or title_from_html or "None"
        result = self.client.edit_page(
            path, title, html_content, author_name, author_url
        )
        return result

    def get_page(self, path: str, return_content: bool = True) -> Dict[str, Any]:
        """
        Получает страницу по path.
        """
        params = {"return_content": str(return_content).lower()}
        r = requests.get(f"{TELEGRAPH_API_URL}/getPage/{path}", params=params)
        r.raise_for_status()
        return r.json()

    def get_pages_list(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Возвращает список страниц аккаунта.
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
        Симуляция удаления страницы — затираем пустым HTML.
        """
        html_content = [
            {"tag": "p", "children": [" "]}  # минимальный блок, API примет
        ]  # пустая страница
        result = self.client.edit_page(
            path=path, title=title, author_name="", author_url="", content=html_content
        )
        return result
