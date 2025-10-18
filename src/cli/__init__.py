import importlib
import pkgutil

import typer

from cli.logger_config import logger

app = typer.Typer(help="Главное CLI-приложение")


@app.callback()
def main():
    """Главная точка входа для CLI."""
    logger.debug("Контекст приложения инициализирован")


# Автоматическое подключение подкоманд
for module_info in pkgutil.iter_modules(__path__):
    if module_info.name in ["__init__", "logger_config"]:
        continue

    module = importlib.import_module(f"{__name__}.{module_info.name}")

    if hasattr(module, "app"):
        sub_app = getattr(module, "app")
        if isinstance(sub_app, typer.Typer):
            app.add_typer(sub_app, name=module_info.name)
            logger.debug(f"Подключен модуль: {module_info.name}")
        else:
            logger.warning(f"Модуль {module_info.name} не содержит Typer.app")
