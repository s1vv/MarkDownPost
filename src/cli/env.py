from pathlib import Path

import typer

from core.env_manager import init_env_from_template, load_env

app = typer.Typer(help="Setting Environment Variables")


@app.command()
def init(
    template: Path = typer.Argument(
        ..., help="The path to the .env template (for example, ./env.example)"
    ),
    apply: bool = typer.Option(
        False, "--apply", help="Set variables in the system environment"
    ),
):
    """
    Creates an .env from the specified template and (optionally) applies variables.
    """
    init_env_from_template(template, apply=apply)


@app.command()
def show():
    """Shows the path to the active one .env and environment variables."""
    env_path = load_env()
    if not env_path:
        typer.echo("⚠️ .env not found, run 'mdp init'. ")
        raise typer.Exit()

    from dotenv import dotenv_values
    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(title=f"Current variables ({env_path})")
    table.add_column("The variable", style="cyan")
    table.add_column("Value", style="green")

    for k, v in dotenv_values(env_path).items():
        table.add_row(k, v or "")

    console.print(table)
