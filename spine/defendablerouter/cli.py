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
from defendablerouter.core.ledger import (
    append_payload_file,
    read_records,
    verify_ledger as verify_ledger_chain,
)
from defendablerouter.core.receipt import (
    build_receipt,
    finalize_receipt_hashes,
    write_event_input,
    write_receipt,
)
from defendablerouter.core.swarmjelly import build_pair, corpus_stats, write_pair
from defendablerouter.core.tribunal import create_tribunal_stub
from defendablerouter.core.tribunal_grade import grade_receipt, write_verdict
from defendablerouter.core.verify import verify_run
from defendablerouter.publisher.publish import publish as publish_records
from defendablerouter.schemas.router_event import RouterEvent
from defendablerouter.schemas.router_receipt import Provenance, RouterReceipt

app = typer.Typer(
    add_completion=False,
    help="DefendableRouter · deterministic receipt spine · ring ring · to the shed.",
)
receipt_app = typer.Typer(help="Receipt operations.")
agent_app = typer.Typer(help="Agent operations.")
tribunal_app = typer.Typer(help="Tribunal grading.")
ledger_app = typer.Typer(help="DefendableLedger operations.")
jelly_app = typer.Typer(help="SwarmJelly corpus operations.")
app.add_typer(receipt_app, name="receipt")
app.add_typer(agent_app, name="agent")
app.add_typer(tribunal_app, name="tribunal")
app.add_typer(ledger_app, name="ledger")
app.add_typer(jelly_app, name="jelly")

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


@tribunal_app.command("grade")
def tribunal_grade(
    run: Path = typer.Option(..., exists=True, file_okay=False, dir_okay=True),
) -> None:
    """Grade an existing run via SwarmCurator-9B · writes verdict.json · appends to ledger · routes pair."""
    receipt_path = run / "router_receipt.json"
    event_path = run / "input.json"
    if not receipt_path.exists() or not event_path.exists():
        console.print(f"[red]missing receipt or input in {run}[/red]")
        raise typer.Exit(code=1)

    receipt = RouterReceipt.model_validate(orjson.loads(receipt_path.read_bytes()))
    event = RouterEvent.model_validate(orjson.loads(event_path.read_bytes()))

    verdict = grade_receipt(receipt, event=event)
    write_verdict(verdict, run)
    append_payload_file(
        record_type="VERDICT",
        payload_path=run / "verdict.json",
        issued_by="Tribunal",
        host=RouterConfig.from_env().host,
        base_dir=run.parent.parent,
    )

    pair = build_pair(event, verdict)
    pair_status = "n/a"
    if pair is not None:
        pair_path = write_pair(pair)
        append_payload_file(
            record_type="PAIR",
            payload_path=pair_path,
            issued_by="SwarmJelly",
            host=RouterConfig.from_env().host,
            base_dir=run.parent.parent,
        )
        pair_status = f"{pair.pair_id} → {pair.tier}"

    style = {"GRADED": "green", "SKIPPED": "yellow", "FAILED": "red"}.get(verdict.status, "white")
    table = Table(title=f"Tribunal · {verdict.verdict_id}", show_header=False, box=None)
    table.add_row("status", f"[{style}]{verdict.status}[/{style}]")
    table.add_row("verdict_id", verdict.verdict_id)
    table.add_row("tier", verdict.tier or "—")
    if verdict.rubric_scores is not None:
        s = verdict.rubric_scores
        table.add_row("scores", f"acc={s.accuracy} cre={s.cre_judgment} fmt={s.format} score={s.score}")
        table.add_row("mean", f"{s.mean:.2f}")
    if verdict.notes:
        table.add_row("notes", verdict.notes[:200])
    if verdict.skip_reason:
        table.add_row("skip_reason", verdict.skip_reason[:200])
    table.add_row("pair", pair_status)
    console.print(Panel.fit(table, border_style=style))


@ledger_app.command("verify")
def ledger_verify() -> None:
    """Walk the DefendableLedger chain and verify every record_sha256 + parent_hash link."""
    result = verify_ledger_chain()
    style = "green" if result.ok else "red"
    table = Table(title="DefendableLedger · verify", show_header=False, box=None)
    table.add_row("status", f"[{style}]{'PASS' if result.ok else 'FAIL'}[/{style}]")
    table.add_row("records_checked", str(result.records_checked))
    if result.first_break_seq is not None:
        table.add_row("first_break_seq", str(result.first_break_seq))
    if result.errors:
        table.add_row("errors", "\n".join(result.errors[:5]))
    console.print(Panel.fit(table, border_style=style))
    if not result.ok:
        raise typer.Exit(code=1)


@ledger_app.command("show")
def ledger_show(
    last: int = typer.Option(10, help="Show last N records."),
) -> None:
    """Show recent DefendableLedger records."""
    records = read_records()
    tail = records[-last:]
    table = Table(title=f"DefendableLedger · last {len(tail)} of {len(records)}", show_lines=False)
    table.add_column("seq", justify="right")
    table.add_column("type")
    table.add_column("record_id")
    table.add_column("payload_ref")
    table.add_column("issued_by")
    for r in tail:
        table.add_row(str(r.ledger_seq), r.record_type, r.record_id, r.payload_ref[:50], r.issued_by)
    console.print(table)


@ledger_app.command("publish")
def ledger_publish(
    repo: Path = typer.Option(..., exists=True, file_okay=False, dir_okay=True,
                              help="Path to the defendable-ledger clone."),
    since: Optional[int] = typer.Option(None, help="Override cursor · republish records with ledger_seq > since."),
    commit: bool = typer.Option(False, "--commit", help="git commit new files."),
    push: bool = typer.Option(False, "--push", help="git push origin main (implies --commit)."),
) -> None:
    """Publish DefendableLedger records into the defendable-ledger repo · /public/records/*."""
    if push and not commit:
        commit = True
    result = publish_records(repo=repo, since=since, commit=commit, push=push)
    style = "green" if result.ok else "red"
    table = Table(title="DefendableLedger · publish", show_header=False, box=None)
    table.add_row("status", f"[{style}]{'OK' if result.ok else 'ERROR'}[/{style}]")
    table.add_row("repo", str(result.repo))
    table.add_row("cursor", f"{result.cursor_before} → {result.cursor_after}")
    table.add_row("new_records", str(result.new_records))
    if result.commit_sha:
        table.add_row("commit", result.commit_sha[:12])
    if result.pushed:
        table.add_row("pushed", "yes")
    if result.skipped:
        table.add_row("skipped", "\n".join(result.skipped[:5]))
    if result.errors:
        table.add_row("errors", "\n".join(result.errors[:5]))
    console.print(Panel.fit(table, border_style=style))
    if not result.ok:
        raise typer.Exit(code=1)


@jelly_app.command("stats")
def jelly_stats() -> None:
    """Show SwarmJelly corpus counts by Royal Jelly tier."""
    s = corpus_stats()
    table = Table(title="SwarmJelly · corpus by tier", show_header=False, box=None)
    for t in ["apex", "honey", "jelly", "pollen", "propolis"]:
        table.add_row(t, str(s.get(t, 0)))
    table.add_row("total", str(s.get("total", 0)))
    console.print(Panel.fit(table, border_style="green"))


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
