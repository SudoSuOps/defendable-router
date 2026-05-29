from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from defendable_router import __version__
from defendable_router.core.time import utc_now
from defendable_router.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("select 1"))
    return {"status": "healthy", "service": "DefendableRouter", "version": __version__, "db_status": "ok", "timestamp": utc_now().isoformat()}
