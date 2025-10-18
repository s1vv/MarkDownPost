import html as html_module
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString, PageElement
from rich.console import Console
from rich.progress import track

from cli.logger_config import logger
from config import settings
from utils.converting_md2html import md_to_html
from utils.extract_from_h1 import extract_title
from utils.upload_img import upload_to_imgbb

console = Console()

# Разрешённые теги Telegraph (упрощённый набор)
ALLOWED_TAGS = {
    "a",
    "aside",
    "b",
    "blockquote",
    "br",
    "code",
    "em",
    "figcaption",
    "figure",
    "h3",
    "h4",
    "hr",
    "i",
    "iframe",
    "img",
    "li",
    "ol",
    "p",
    "pre",
    "s",
    "strong",
    "u",
    "ul",
    "video",
}

# Какие атрибуты разрешать для каких тегов
ALLOWED_ATTRS = {
    "a": ["href", "title"],
    "img": ["src", "alt", "title"],
    "iframe": ["src"],
    "video": ["src"],
}

Node = Union[str, Dict[str, Any]]


def _get_allowed_attrs(tag: Tag) -> Optional[Dict[str, str]]:
    """Возвращает словарь разрешённых атрибутов для тега (или None)."""
    name = tag.name.lower()
    allowed = ALLOWED_ATTRS.get(name)
    if not allowed:
        return None
    out = {}
    for a in allowed:
        val = tag.get(a)
        if val:
            out[a] = val
    return out or None


def _nodes_from_element(el: PageElement) -> List[Node]:
    """Рекурсивно конвертирует элемент BS (Tag или NavigableString) в telegraph-узлы."""

    # Текстовый узел
    if isinstance(el, NavigableString):
        text = str(el)
        if not text.strip():
            return []
        return [html_module.unescape(text)]

    # Если не Tag — пропускаем
    if not isinstance(el, Tag):
        return []

    name = el.name.lower()

    # h1/h2 → h3
    if name in ("h1", "h2"):
        name = "h3"

    # Если тег не разрешён — разворачиваем детей
    if name not in ALLOWED_TAGS:
        result: List[Node] = []
        for c in el.contents:
            if isinstance(c, PageElement):
                result.extend(_nodes_from_element(c))
        return result

    children: List[Node] = []
    for c in el.contents:
        if isinstance(c, PageElement):
            children.extend(_nodes_from_element(c))

    attrs = _get_allowed_attrs(el)

    if name == "img":
        if not attrs or "src" not in attrs:
            return []
        return [{"tag": "img", "attrs": attrs}]

    if name in ("br", "hr"):
        return [{"tag": name}]

    node: Dict[str, Any] = {"tag": name}
    if attrs:
        node["attrs"] = attrs
    if children:
        node["children"] = children

    return [node]


def html_to_telegraph_nodes(html: str) -> List[Node]:
    """Конвертирует HTML-фрагмент (строка) в список telegraph-узлов."""
    soup = BeautifulSoup(html, "html.parser")
    result: List[Node] = []

    # Проходим по верхнему уровню. Если есть body — используем body.contents
    top_level = soup.body.contents if soup.body else soup.contents
    for el in top_level:
        result.extend(_nodes_from_element(el))
    return result


def markdown_to_telegraph_nodes(
    md_path: str,
    imgbb_api_key: Optional[str] = settings.IMGBB_API_KEY,
) -> tuple[List[Node], Optional[str]]:
    """
    Markdown -> HTML -> загрузка локальных img на ImgBB -> замена src -> Telegraph nodes.
    """
    # 1) Markdown -> HTML
    html = md_to_html(md_path)
    title, html = extract_title(html)
    soup = BeautifulSoup(html, "html.parser")

    # 2) Найти локальные изображения
    local_imgs: List[Path] = []
    img_tags: List[Tag] = []
    md_dir = Path(md_path).parent if md_path else Path(".")

    for img in soup.find_all("img"):
        src = img.get("src", "")
        if src and not str(src).startswith("http"):
            local_path = Path(f"{md_dir}/{src}").resolve()
            if not local_path.exists():
                logger.warning("Пропущено: не найдено изображение %s", local_path)
                continue
            local_imgs.append(local_path)
            img_tags.append(img)

    # 3) Загрузка на ImgBB
    if local_imgs:
        if not imgbb_api_key:
            raise RuntimeError("ImgBB API key не задан")
        print(
            f"📤 Найдено {len(local_imgs)} локальных изображений, загружаем на ImgBB..."
        )
        for img_tag, local_path in zip(
            img_tags, track(local_imgs, description="Uploading")
        ):
            try:
                new_url = upload_to_imgbb(str(local_path), imgbb_api_key)
                img_tag["src"] = new_url
                logger.info("Загружено %s → %s", local_path, new_url)
            except Exception as e:
                logger.error("Ошибка загрузки %s: %s", local_path, e)

    # 4) HTML -> Telegraph nodes
    nodes = html_to_telegraph_nodes(str(soup))
    if not nodes:
        raise RuntimeError("Нет данных для публикации")
    return nodes, title
