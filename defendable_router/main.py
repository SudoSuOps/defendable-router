from fastapi import FastAPI
from defendable_router.api import admin, compute, datasets, health, jobs, members, receipts, workers
from defendable_router.db.init_db import init_db

app = FastAPI(title="DefendableRouter", version="0.1.0", description="Member-only DefendableCloud dataset and GPU compute router.")

app.include_router(health.router)
app.include_router(members.router)
app.include_router(datasets.router)
app.include_router(compute.router)
app.include_router(jobs.router)
app.include_router(admin.router)
app.include_router(workers.router)
app.include_router(receipts.router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
