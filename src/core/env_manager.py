import os
import shutil
import sys
from pathlib import Path

from dotenv import dotenv_values, load_dotenv


def get_env_path() -> Path:
    """
    Defines where the local .env file is stored.
    Windows → %APPDATA%/mdp/.env
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
    Creates an .env from the specified template and, if necessary,
    sets environment variables in the system.
    """
    if not template_path.exists():
        print(f"❌ The template file was not found: {template_path}")
        sys.exit(1)

    env_path = get_env_path()
    shutil.copy(template_path, env_path)
    print(f"✅ .env created from a template: {template_path} → {env_path}")

    if apply:
        set_system_env(env_path)

    return env_path


def set_system_env(env_path: Path):
    """
    Sets environment variables from the .env file.
    On Windows — via `setx`, on Unix — only notification.
    """
    values = dotenv_values(env_path)
    if not values:
        print(f"⚠️ There are no variables to set in the {env_path} file.")
        return

    if os.name == "nt":
        for key, value in values.items():
            cmd = f'setx {key} "{value or ""}" >nul'
            os.system(cmd)
        print("✅ The variables are set to the system environment (Windows).")
        print("🔄 Restart the terminal to apply the changes.")
    else:
        print("💡 On Linux/macOS, variables are not saved globally.")
        print(f"  To use them, run:\n   source {env_path}")


def load_env() -> Path | None:
    """
    Loads the .env from the system path (if any).
    """
    env_path = get_env_path()
    if env_path.exists():
        load_dotenv(env_path)
        return env_path
    return None
