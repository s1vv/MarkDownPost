import re
from pathlib import Path

from bs4 import BeautifulSoup

from utils.upload_img import upload_to_imgbb

# -----------------------------------------------------
# Основной санитайзер
# -----------------------------------------------------
ALLOWED_TAGS = {
    "b",
    "strong",
    "i",
    "em",
    "u",
    "ins",
    "s",
    "strike",
    "del",
    "a",
    "code",
    "pre",
    "blockquote",
    "br",
}

TAG_MAP = {
    "h1": "b",
    "h2": "b",
    "h3": "b",
    "h4": "b",
    "h5": "b",
    "h6": "b",
    "em": "i",
    "strong": "b",
    "strike": "s",
    "del": "s",
    "ins": "u",
}


def sanitize_html_for_telegram(
    html: str, base_path: str | Path, imgbb_api_key: str | None = None
) -> str:
    """
    Преобразует HTML в формат, допустимый для Telegram.
    Удаляет опасные теги, конвертирует списки и при необходимости загружает изображения.
    """
    soup = BeautifulSoup(html, "html.parser")

    # --- Заголовки → <b>
    for tag_name, replacement in TAG_MAP.items():
        for tag in soup.find_all(tag_name):
            tag.name = replacement

    # --- Списки (<ul>/<ol>)
    for ul in soup.find_all("ul"):
        items = []
        for li in ul.find_all("li"):
            text = li.get_text(" ", strip=True)
            items.append(f"• {text}")
        ul.replace_with("\n".join(items))

    for ol in soup.find_all("ol"):
        items = []
        for i, li in enumerate(ol.find_all("li"), start=1):
            text = li.get_text(" ", strip=True)
            items.append(f"{i}. {text}")
        ol.replace_with("\n".join(items))

    # --- Изображения
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src:
            img.decompose()
            continue

        # локальные файлы → загрузка на ImgBB
        if not str(src).startswith("http"):
            if imgbb_api_key:
                local_path = Path(f"{base_path}/{src}")
                try:
                    url = upload_to_imgbb(str(local_path), imgbb_api_key)
                    img.replace_with(f"\n{url}\n")
                except Exception as e:
                    img.replace_with(f"[Ошибка загрузки изображения: {e}]")
            else:
                img.replace_with(f"[локальное изображение: {src}]")
        else:
            img.replace_with(f"\n{src}\n")

    # --- Очистка недопустимых тегов
    for tag in soup.find_all(True):
        if tag.name not in ALLOWED_TAGS:
            tag.unwrap()
        else:
            # оставить только href в <a>
            if tag.name == "a":
                href = tag.get("href")
                tag.attrs = {"href": href} if href else {}
            else:
                tag.attrs = {}

    text = str(soup)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
