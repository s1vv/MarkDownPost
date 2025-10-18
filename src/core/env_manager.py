import os
import shutil
import sys
from pathlib import Path

from dotenv import dotenv_values, load_dotenv


def get_env_path() -> Path:
    """
    Определяет, где хранится локальный .env файл.
    Windows → %APPDATA%\mdp\.env
    Linux/macOS → ~/.config/mdp/.env
    """
    if os.name == "nt":
        base_dir = Path(os.getenv("APPDATA", Path.home()))
    else:
        base_dir = Path.home() / ".config"
    env_dir = base_dir / "mdp"
    env_dir.mkdir(parents=True, exist_ok=True)
    return env_dir / ".env"


def init_env_from_template(template_path: Path, apply: bool = False) -> Path:
    """
    Создаёт .env из указанного шаблона и при необходимости
    устанавливает переменные окружения в систему.
    """
    if not template_path.exists():
        print(f"❌ Файл шаблона не найден: {template_path}")
        sys.exit(1)

    env_path = get_env_path()
    shutil.copy(template_path, env_path)
    print(f"✅ .env создан из шаблона: {template_path} → {env_path}")

    if apply:
        set_system_env(env_path)

    return env_path


def set_system_env(env_path: Path):
    """
    Устанавливает переменные окружения из файла .env.
    На Windows — через `setx`, на Unix — только уведомление.
    """
    values = dotenv_values(env_path)
    if not values:
        print(f"⚠️  В файле {env_path} нет переменных для установки.")
        return

    if os.name == "nt":
        for key, value in values.items():
            cmd = f'setx {key} "{value or ""}" >nul'
            os.system(cmd)
        print("✅ Переменные установлены в системное окружение (Windows).")
        print("🔄 Перезапустите терминал, чтобы применить изменения.")
    else:
        print("💡 В Linux/macOS переменные не сохраняются глобально.")
        print(f"  Чтобы использовать их, выполните:\n   source {env_path}")


def load_env() -> Path | None:
    """
    Загружает .env из системного пути (если есть).
    """
    env_path = get_env_path()
    if env_path.exists():
        load_dotenv(env_path)
        return env_path
    return None
