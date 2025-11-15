import os
import platform
from pathlib import Path

from dotenv import load_dotenv

from cli.logger_config import logger
from i18n.i18n_keys import I18NKey
from utils.i18n import i18n

# 1. Локальный .env рядом с проектом
local_env = Path("../.env")

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
    logger.debug(f"Local .env: {local_env}")
elif default_env.exists():
    load_dotenv(default_env)
    ENV_FILE = default_env
    logger.debug(f"Dafault .env: {default_env}")
else:
    logger.critical(i18n.get(I18NKey.ERRORS_ENV_NOT_FOUND))
    # Create a default file automatically (if necessary)
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        default_env.touch(exist_ok=True)
        ENV_FILE = default_env
        logger.debug(f"Empty .env: {default_env}")
        # do not call load_dotenv — the file is empty, but the path is known
    except Exception as e:
        logger.error(i18n.get(I18NKey.ERRORS_SAVE_ERROR), e)
        ENV_FILE = None

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL = os.getenv("TELEGRAM_CHANNEL")
TELEGRAPH_ACCESS_TOKEN = os.getenv("TELEGRAPH_ACCESS_TOKEN")
AUTHOR_NAME = os.getenv("AUTHOR_NAME", "Автор")
AUTHOR_URL = os.getenv("AUTHOR_URL", "https://")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
ADD_ID = False
