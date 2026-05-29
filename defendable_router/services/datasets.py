import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from defendable_router.core.receipts import write_receipt
from defendable_router.db.models import Dataset
from defendable_router.schemas.datasets import DatasetCreate


def create_dataset(db: Session, payload: DatasetCreate) -> Dataset:
    """Create a dataset registry entry for member-access metadata."""
    dataset = Dataset(id=payload.id or f"ds_{uuid.uuid4().hex}", **payload.model_dump(exclude={"id"}))
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


def list_datasets(db: Session, domain: str | None = None, quality_tier: str | None = None, limit: int = 50, offset: int = 0) -> list[Dataset]:
    """List dataset registry entries with optional domain and quality filters."""
    stmt = select(Dataset)
    if domain:
        stmt = stmt.where(Dataset.domain == domain)
    if quality_tier:
        stmt = stmt.where(Dataset.quality_tier == quality_tier)
    return list(db.scalars(stmt.offset(offset).limit(limit)).all())


def get_dataset(db: Session, dataset_id: str) -> Dataset | None:
    """Return dataset metadata by ID, or None when it is not registered."""
    return db.get(Dataset, dataset_id)


def create_access_receipt(member_id: str, dataset: Dataset) -> dict:
    """Emit a zero-dollar dataset access receipt for an active member."""
    return write_receipt("dataset_access", member_id, "0.00", {"dataset_title": dataset.title, "object_uri": dataset.object_uri}, dataset_ids=[dataset.id])
