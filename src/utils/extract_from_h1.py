import re


def extract_title(html: str) -> tuple[str | None, str]:
    """
    Извлекает содержимое первого <h1>...</h1> и возвращает (title, html_without_h1).
    Если <h1> не найден — возвращает None.
    """
    match = re.search(r"<h1[^>]*>(.*?)</h1>", html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None, html

    title = re.sub(r"<.*?>", "", match.group(1)).strip()  # чистый текст из заголовка
    cleaned_html = re.sub(
        r"<h1[^>]*>.*?</h1>", "", html, count=1, flags=re.IGNORECASE | re.DOTALL
    )
    cleaned_html = re.sub(
        r"\s*\n\s*", "\n", cleaned_html
    ).strip()  # убираем пустые строки и пробелы

    return title, cleaned_html
