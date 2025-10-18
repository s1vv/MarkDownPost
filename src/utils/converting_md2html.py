import sys
from pathlib import Path

import markdown as mdlib

from cli.logger_config import logger


def md_to_html(path: str) -> str:
    try:
        md_file = Path(path).expanduser().resolve()
        if not md_file.exists():
            logger.error(f"Файл markdown не найден: {md_file}")
            sys.exit(1)
        md_text = md_file.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Ошибка открытия файла *.md: {e}")
        sys.exit(1)

    return mdlib.markdown(md_text, extensions=["extra", "sane_lists"])
