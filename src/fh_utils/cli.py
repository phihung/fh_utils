from logging import getLogger
from pathlib import Path
from typing import Annotated

import rich
import typer

from fh_utils import __version__, server

app = typer.Typer(rich_markup_mode="rich", pretty_exceptions_enable=False)
logger = getLogger(__name__)


def version_callback(value: bool) -> None:
    if value:
        rich.print(f"fh_utils CLI version: [green]{__version__}[/green]")
        raise typer.Exit()


@app.callback()
def callback(
    version: Annotated[
        bool | None,
        typer.Option("--version", help="Show the version and exit.", callback=version_callback),
    ] = None,
) -> None:
    """
    fh_utils CLI - The [bold]fh_utils[/bold] command line app. 😎

    Manage your [bold]FastHTML[/bold] projects, run your FastHTML apps, and more.

    Read more in the docs: [link]https://github.com/phihung/fh_utils/[/link].
    """


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def dev(
    path: Path,
    *,
    app: str = "app",
    host: str = "0.0.0.0",
    port: int = 5001,
    reload: server.ReloadType = server.ReloadType.FAST,
    live: bool = False,
    ctx: typer.Context,
):
    """Start FastHTML app in [green]dev mode[/green].

    The command accepts uvicorn arguments such as --reload-include and --log-level (see [green]uvicorn[/green] --help for more).
    """
    extra_args = _parse_uvicorn_argument(ctx.args)
    try:
        server.serve_dev(
            path=path, app=app, host=host, port=port, reload=reload, live=live, **extra_args
        )
    except server.CliException as e:  # pragma: no cover
        logger.error(str(e))
        raise typer.Exit(code=1) from None


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def run(
    path: Path,
    *,
    app: str = "app",
    host: str = "0.0.0.0",
    port: int = 5001,
    ctx: typer.Context,
):
    """Start FastHTML app in [green]production mode[/green].

    The command accepts uvicorn arguments such as --reload-include and --log-level (see [green]uvicorn[/green] --help for more).
    """
    extra_args = _parse_uvicorn_argument(ctx.args)
    try:
        server.serve_prod(path=path, app=app, host=host, port=port, **extra_args)
    except server.CliException as e:  # pragma: no cover
        logger.error(str(e))
        raise typer.Exit(code=1) from None


def _parse_uvicorn_argument(args: list[str]):
    if not args:
        return {}

    from uvicorn.main import main

    ctx = main.make_context("app", ["app"] + args)
    mapping = {opt: p.name for p in main.params for opt in p.opts}
    kwargs = {mapping[x]: ctx.params[mapping[x]] for x in args if x.startswith("--")}
    return kwargs


if __name__ == "__main__":
    app()
