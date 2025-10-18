import os
import platform
from pathlib import Path

from dotenv import load_dotenv, set_key
from telegraph import Telegraph

from cli.logger_config import logger

# 1. Локальный .env рядом с проектом
local_env = Path("../../.env")

# 2. Дефолтный путь в конфиге пользователя
system = platform.system()
if system == "Windows":
    config_dir = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming")) / "mdp"
else:
    config_dir = Path.home() / ".config" / "mdp"

default_env = config_dir / ".env"

# --- Выбор и загрузка .env ---
ENV_FILE: Path | None = None

if local_env.exists():
    load_dotenv(local_env)
    ENV_FILE = local_env
    logger.debug(f"Используется локальный .env: {local_env}")
elif default_env.exists():
    load_dotenv(default_env)
    ENV_FILE = default_env
    logger.debug(f"Используется дефолтный .env: {default_env}")
else:
    logger.critical(
        "⚠️ Файл .env не найден, используйте: mdp env init <путь_к_шаблону> "
        "или будет создан дефолтный .env в конфиге пользователя."
    )
    # Создадим дефолтный файл автоматически (если нужно)
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        default_env.touch(exist_ok=True)
        ENV_FILE = default_env
        logger.info(f"Создан пустой .env: {default_env}")
        # не вызываем load_dotenv — файл пустой, но путь известен
    except Exception as e:
        logger.error("Не удалось создать дефолтный .env: %s", e)
        ENV_FILE = None  # дальше нужно учитывать этот случай

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL = os.getenv("TELEGRAM_CHANNEL")
TELEGRAPH_ACCESS_TOKEN = os.getenv("TELEGRAPH_ACCESS_TOKEN")
AUTHOR_NAME = os.getenv("AUTHOR_NAME", "Автор")
AUTHOR_URL = os.getenv("AUTHOR_URL", "https://")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
ADD_ID = False


def get_token_telegraph() -> str:
    # если токен уже в окружении — возвращаем его
    if TELEGRAPH_ACCESS_TOKEN:
        return TELEGRAPH_ACCESS_TOKEN

    answer = (
        input(
            "TELEGRAPH_ACCESS_TOKEN не найден. Создать новый аккаунт и сохранить токен? (y/n): "
        )
        .strip()
        .lower()
    )

    if answer not in ["y", "yes", "д", "да"]:
        logger.warning("Отказ от создания Telegraph-аккаунта. Завершение работы.")
        raise SystemExit(1)

    # Создаём новый аккаунт в Telegraph
    telegraph = Telegraph()
    acc = telegraph.create_account(short_name=AUTHOR_NAME)
    new_token = acc["access_token"]
    logger.info("Создан новый Telegraph аккаунт. Токен: %s", new_token)

    # Сохраняем токен в тот .env, который реально используется (ENV_FILE)
    if not ENV_FILE:
        logger.error("Путь для сохранения .env не определён. Токен не сохранён автоматически.")
        return new_token

    try:
        # set_key ожидает путь как строку или Path; убедимся что директория и файл существуют
        ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not ENV_FILE.exists():
            ENV_FILE.touch()
        # Записываем в файл .env
        set_key(str(ENV_FILE), "TELEGRAPH_ACCESS_TOKEN", new_token)
        logger.info("TELEGRAPH_ACCESS_TOKEN сохранён в %s", ENV_FILE)
        # Подгрузим обновлённые переменные (опционально)
        load_dotenv(ENV_FILE, override=True)
    except Exception as e:
        logger.error("Не удалось записать TELEGRAPH_ACCESS_TOKEN в %s: %s", ENV_FILE, e)

    return new_token

