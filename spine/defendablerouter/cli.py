from __future__ import annotations

from pathlib import Path
from typing import Optional

import orjson
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from defendablerouter.agents.kimi_review import review_receipt as kimi_review_receipt
from defendablerouter.config import RouterConfig
from defendablerouter.core.ddeed import create_ddeed_stub
from defendablerouter.core.export import (
    export_run,
    finalize_run,
    write_ddeed_stub,
    write_tribunal_stub,
)
from defendablerouter.core.hash import sha256_file
from defendablerouter.core.receipt import (
    build_receipt,
    finalize_receipt_hashes,
    write_event_input,
    write_receipt,
)
from defendablerouter.core.tribunal import create_tribunal_stub
from defendablerouter.core.verify import verify_run
from defendablerouter.schemas.router_event import RouterEvent
from defendablerouter.schemas.router_receipt import Provenance

app = typer.Typer(
    add_completion=False,
    help="DefendableRouter · deterministic receipt spine · ring ring · to the shed.",
)
receipt_app = typer.Typer(help="Receipt operations.")
agent_app = typer.Typer(help="Agent operations.")
app.add_typer(receipt_app, name="receipt")
app.add_typer(agent_app, name="agent")

console = Console()


def _load_event(event_path: Path) -> RouterEvent:
    data = orjson.loads(event_path.read_bytes())
    return RouterEvent.model_validate(data)


@receipt_app.command("create")
def receipt_create(
    event: Path = typer.Option(..., exists=True, readable=True, help="Path to event JSON."),
    out: Path = typer.Option(..., help="Run output directory."),
) -> None:
    """Create a deterministic router receipt + Tribunal/DDEED stubs + manifest."""
    config = RouterConfig.from_env()
    event_obj = _load_event(event)
    out.mkdir(parents=True, exist_ok=True)

    write_event_input(event_obj, out)
    receipt = build_receipt(event_obj)
    receipt.provenance = Provenance(host=config.host, gpu=config.gpu, cuda=config.cuda)

    tribunal_stub = create_tribunal_stub(receipt.assignment_id)
    receipt.tribunal.verdict_id = tribunal_stub.verdict_id
    write_tribunal_stub(tribunal_stub, out)

    ddeed_stub = create_ddeed_stub(receipt.receipt_id, receipt.assignment_id)
    receipt.ddeed.deed_id = ddeed_stub.deed_id
    write_ddeed_stub(ddeed_stub, out)

    finalize_receipt_hashes(receipt)
    write_receipt(receipt, out)
    finalize_run(receipt, out)

    table = Table(title="Router Receipt", show_header=False, box=None)
    table.add_row("receipt_id", receipt.receipt_id)
    table.add_row("assignment_id", receipt.assignment_id)
    table.add_row("verdict_id", tribunal_stub.verdict_id)
    table.add_row("deed_id", ddeed_stub.deed_id)
    table.add_row("canonical_sha256", receipt.hashes.canonical_receipt_sha256 or "")
    table.add_row("receipt_sha256", receipt.hashes.receipt_sha256 or "")
    table.add_row("object_storage", receipt.object_storage.uri)
    console.print(Panel.fit(table, title="DefendableRouter · receipts first", border_style="green"))


@receipt_app.command("verify")
def receipt_verify(
    run: Path = typer.Option(..., exists=True, file_okay=False, dir_okay=True),
) -> None:
    """Verify hashes in a run directory."""
    result = verify_run(run)
    status = "[green]PASS[/green]" if result.ok else "[red]FAIL[/red]"
    table = Table(title=f"Verify {run}", show_header=False, box=None)
    table.add_row("status", status)
    table.add_row("receipt_id", result.receipt_id)
    table.add_row("canonical_match", str(result.canonical_match))
    table.add_row("receipt_match", str(result.receipt_match))
    table.add_row("manifest_match", str(result.manifest_match))
    table.add_row("sha256sums_match", str(result.sha256sums_match))
    table.add_row("files_checked", str(len(result.checked_files)))
    if result.errors:
        table.add_row("errors", "\n".join(result.errors))
    console.print(Panel.fit(table, border_style="green" if result.ok else "red"))
    if not result.ok:
        raise typer.Exit(code=1)


@receipt_app.command("hash")
def receipt_hash(
    file: Path = typer.Option(..., exists=True, dir_okay=False, readable=True),
) -> None:
    """Print SHA256 of a file."""
    console.print(f"{sha256_file(file)}  {file}")


@receipt_app.command("export")
def receipt_export(
    run: Path = typer.Option(..., exists=True, file_okay=False, dir_okay=True),
    target: str = typer.Option("local"),
) -> None:
    """Export a run. Currently 'local' only."""
    out = export_run(run, target=target)  # type: ignore[arg-type]
    console.print(f"exported: {out}")


@agent_app.command("kimi-review")
def agent_kimi_review(
    run: Path = typer.Option(..., exists=True, file_okay=False, dir_okay=True),
) -> None:
    """Run Kimi (Moonshot) review over the receipt. Skips cleanly without MOONSHOT_API_KEY."""
    result = kimi_review_receipt(run)
    verdict = result.get("verdict", "UNKNOWN")
    style = {
        "PASS": "green",
        "WARN": "yellow",
        "FAIL": "red",
        "SKIPPED": "yellow",
    }.get(verdict, "white")
    table = Table(title="Kimi Router Review", show_header=False, box=None)
    table.add_row("verdict", f"[{style}]{verdict}[/{style}]")
    table.add_row("model", result.get("model", ""))
    table.add_row("findings", str(len(result.get("findings", []))))
    table.add_row("missing_fields", str(len(result.get("missing_fields", []))))
    table.add_row("schema_risks", str(len(result.get("schema_risks", []))))
    if "skip_reason" in result:
        table.add_row("skip_reason", result["skip_reason"])
    console.print(Panel.fit(table, border_style=style))


@app.command("serve")
def serve(
    host: str = typer.Option("0.0.0.0", help="Bind host."),
    port: int = typer.Option(8080, help="Bind port."),
    reload: bool = typer.Option(False, help="Auto-reload on code changes (dev only)."),
) -> None:
    """Run the StreetChat intake HTTP server."""
    import uvicorn

    uvicorn.run(
        "defendablerouter.api.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


def main() -> None:
    load_dotenv()
    app()


if __name__ == "__main__":
    main()
