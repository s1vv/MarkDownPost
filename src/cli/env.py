from pathlib import Path

import typer

from core.env_manager import init_env_from_template, load_env

app = typer.Typer(help="Установка переменных окружения")


@app.command()
def init(
    template: Path = typer.Argument(
        ..., help="Путь к .env шаблону (например, ./env.example)"
    ),
    apply: bool = typer.Option(
        False, "--apply", help="Установить переменные в системное окружение"
    ),
):
    """
    Создаёт .env из указанного шаблона и (опционально) применяет переменные.
    """
    init_env_from_template(template, apply=apply)


@app.command()
def show():
    """Показывает путь к активному .env и переменные окружения."""
    env_path = load_env()
    if not env_path:
        typer.echo("⚠️  .env не найден, выполните `mdp init`.")
        raise typer.Exit()

    from dotenv import dotenv_values
    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(title=f"Текущие переменные ({env_path})")
    table.add_column("Переменная", style="cyan")
    table.add_column("Значение", style="green")

    for k, v in dotenv_values(env_path).items():
        table.add_row(k, v or "")

    console.print(table)
