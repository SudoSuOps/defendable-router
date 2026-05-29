from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from defendable_router.core.security import require_active_member
from defendable_router.db.session import get_db
from defendable_router.schemas.datasets import DatasetAccessRequest, DatasetAccessResponse, DatasetCreate, DatasetRead
from defendable_router.services.datasets import create_access_receipt, create_dataset, get_dataset, list_datasets

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("", response_model=DatasetRead)
def create_dataset_endpoint(payload: DatasetCreate, db: Session = Depends(get_db)):
    return create_dataset(db, payload)


@router.get("", response_model=list[DatasetRead])
def list_dataset_endpoint(domain: str | None = None, quality_tier: str | None = None, limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    return list_datasets(db, domain=domain, quality_tier=quality_tier, limit=limit, offset=offset)


@router.get("/{dataset_id}", response_model=DatasetRead)
def read_dataset(dataset_id: str, db: Session = Depends(get_db)):
    dataset = get_dataset(db, dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="dataset not found")
    return dataset


@router.post("/{dataset_id}/access", response_model=DatasetAccessResponse)
def access_dataset(dataset_id: str, payload: DatasetAccessRequest, db: Session = Depends(get_db)):
    require_active_member(db, payload.member_id)
    dataset = get_dataset(db, dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="dataset not found")
    receipt = create_access_receipt(payload.member_id, dataset)
    return DatasetAccessResponse(access_granted=True, dataset_id=dataset.id, member_id=payload.member_id, receipt_id=receipt["receipt_id"], object_uri=dataset.object_uri)
