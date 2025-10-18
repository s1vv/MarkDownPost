from __future__ import annotations

import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text

console = Console()


class ColorFormatter(logging.Formatter):
    LEVEL_STYLES = {
        "DEBUG": "dim white",
        "INFO": "bold cyan",
        "WARNING": "bold yellow",
        "ERROR": "bold red",
        "CRITICAL": "bold red on white",
    }

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        style = self.LEVEL_STYLES.get(record.levelname, "")
        if style:
            return Text(message, style=style).plain
        return message


handler = RichHandler(console=console, show_path=False)
handler.setFormatter(
    ColorFormatter(
        "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d — %(funcName)s() — %(message)s",
        datefmt="%H:%M:%S",
    )
)

logger = logging.getLogger("cli")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
