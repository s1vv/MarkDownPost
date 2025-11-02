#!/usr/bin/env python3
import subprocess
import re
from pathlib import Path

# === Настройки ===
PATTERN = re.compile(
    r"PAGE_CREATED"
)  # чувствительно к регистру (r"(?i)WORD" для безрегистрового)
ROOT_DIR = Path(__file__).resolve().parent


def get_git_files() -> list[str]:
    """Получает список всех файлов, не исключённых .gitignore."""
    result = subprocess.run(
        ["git", "ls-files", "-co", "--exclude-standard"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.splitlines()


def search_in_file(path: Path) -> list[str]:
    """Ищет совпадения в файле, возвращает список строк с результатами."""
    matches = []
    try:
        with path.open(encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                if PATTERN.search(line):
                    matches.append(f"{path}:{i}: {line.strip()}")
    except (UnicodeDecodeError, FileNotFoundError):
        pass
    return matches


def main() -> None:
    files = get_git_files()
    for file_path in files:
        full_path = ROOT_DIR / file_path
        if full_path.is_file():
            for match in search_in_file(full_path):
                print(match)


if __name__ == "__main__":
    main()
