# main.py
from cli import app


@app.command("help-all")
def help_all():
    """Показать помощь по всем командам и подкомандам."""
    import click
    from typer.main import get_command

    cli = get_command(app)

    def print_help_recursive(cmd: click.Command, parent_name: str = ""):
        ctx = click.Context(cmd)
        full_name = f"{parent_name} {cmd.name}".strip()
        print(f"\n{'=' * 80}\nHELP для: {full_name or 'root'}\n{'=' * 80}")
        print(cmd.get_help(ctx))
        if isinstance(cmd, click.Group):
            for sub_name, sub_cmd in cmd.commands.items():
                print_help_recursive(sub_cmd, full_name)

    print_help_recursive(cli)


def main():
    """Точка входа для pipx."""
    app()


if __name__ == "__main__":
    main()
