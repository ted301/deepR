from __future__ import annotations
import typer
from ..logging.logger import configure_logging

app = typer.Typer(help="DeepR local deep research CLI")

@app.callback()
def _init() -> None:
    configure_logging()

@app.command()
def version() -> None:
    """Show version (placeholder)."""
    typer.echo("DeepR version 0.0.0-dev")

@app.command()
def research(query: str):
    """Start a research run (scaffold)."""
    typer.echo(f"[scaffold] Would start research for: {query}")

if __name__ == "__main__":  # pragma: no cover
    app()
