import typer
from rich import print
from sqlalchemy import func, select
from defendable_router.api.admin import admin_summary as admin_summary_service
from defendable_router.core.pricing import GPU_PRICING
from defendable_router.core.security import require_active_member
from defendable_router.db.init_db import init_db, seed_demo as seed_demo_data
from defendable_router.db.models import ComputeNode, Dataset, JobLease, JobLeaseStatus, Member, Worker
from defendable_router.db.session import SessionLocal
from defendable_router.services.billing import quote_compute
from defendable_router.core.receipts import write_receipt
from defendable_router.services.leases import expire_stale_leases
from defendable_router.services.workers import mark_stale_workers

app = typer.Typer(help="DefendableRouter admin and dev commands.")


@app.command("init-db")
def init_db_command():
    init_db()
    print("DefendableRouter database initialized")


@app.command("seed-demo")
def seed_demo_command():
    with SessionLocal() as db:
        seed_demo_data(db)
    print("DefendableRouter demo data seeded")


@app.command("list-members")
def list_members():
    with SessionLocal() as db:
        for member in db.scalars(select(Member)).all():
            print({"id": member.id, "email": member.email, "status": member.status})


@app.command("list-datasets")
def list_datasets():
    with SessionLocal() as db:
        for dataset in db.scalars(select(Dataset)).all():
            print({"id": dataset.id, "title": dataset.title, "quality_tier": dataset.quality_tier})


@app.command("list-compute")
def list_compute():
    with SessionLocal() as db:
        for node in db.scalars(select(ComputeNode)).all():
            print({"id": node.id, "hostname": node.hostname, "gpu_type": node.gpu_type, "status": node.status})


@app.command("list-workers")
def list_workers():
    with SessionLocal() as db:
        for worker in db.scalars(select(Worker)).all():
            print({"id": worker.id, "node_id": worker.node_id, "hostname": worker.hostname, "status": worker.status, "last_heartbeat_at": worker.last_heartbeat_at})


@app.command("worker-summary")
def worker_summary():
    with SessionLocal() as db:
        print({"workers_total": db.scalar(select(func.count()).select_from(Worker)) or 0, "active_leases": db.scalar(select(func.count()).select_from(JobLease).where(JobLease.status == JobLeaseStatus.active.value)) or 0, "expired_leases": db.scalar(select(func.count()).select_from(JobLease).where(JobLease.status == JobLeaseStatus.expired.value)) or 0})


@app.command("expire-leases")
def expire_leases():
    with SessionLocal() as db:
        count = expire_stale_leases(db)
        print({"expired_leases": count})


@app.command("mark-stale-workers")
def mark_stale_workers_command():
    with SessionLocal() as db:
        count = mark_stale_workers(db)
        print({"stale_workers_marked_offline": count})


@app.command("admin-summary")
def admin_summary_command():
    with SessionLocal() as db:
        print(admin_summary_service(db))


@app.command("quote")
def quote(member_id: str = typer.Option(...), gpu: str = typer.Option(...), hours: float = typer.Option(...), job_type: str = typer.Option("fine_tune")):
    with SessionLocal() as db:
        require_active_member(db, member_id)
        hourly_rate, estimated_cost = quote_compute(gpu, hours)
        receipt = write_receipt("compute_quote", member_id, estimated_cost, {"gpu_sku": gpu, "estimated_hours": hours, "job_type": job_type})
        print({"member_id": member_id, "gpu": gpu, "gpu_display_name": GPU_PRICING[gpu]["display_name"], "hourly_rate_usd": float(hourly_rate), "estimated_hours": hours, "estimated_cost_usd": float(estimated_cost), "receipt_id": receipt["receipt_id"]})


if __name__ == "__main__":
    app()
