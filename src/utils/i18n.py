from __future__ import annotations
import json
from pathlib import Path
from typing import Any

class I18N:
    def __init__(self, lang: str = "ru", base_path: Path | None = None):
        self.lang = lang
        base_path = base_path or Path(__file__).parent.parent / "i18n" / "i18n.json"
        self.translations = self._load(base_path)

    def _load(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"i18n file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get(self, key: str, **kwargs) -> str:
        """
        Получает строку по ключу формата 'section.KEY', например:
        i18n.get("errors.MISSING_TOKEN")
        """
        try:
            section, subkey = key.split(".", 1)
            value = self.translations[section][subkey][self.lang]
            return value.format(**kwargs) if kwargs else value
        except KeyError:
            return f"[{key}]"

# Пример глобального экземпляра
i18n = I18N(lang="en")
