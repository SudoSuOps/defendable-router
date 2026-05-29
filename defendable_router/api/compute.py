from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from defendable_router.core.pricing import GPU_PRICING
from defendable_router.core.receipts import write_receipt
from defendable_router.core.security import require_active_member
from defendable_router.db.session import get_db
from defendable_router.schemas.compute import ComputeNodeCreate, ComputeNodeRead, ComputeQuoteRequest, ComputeQuoteResponse
from defendable_router.services.billing import quote_compute
from defendable_router.services.compute_inventory import list_nodes, register_node

router = APIRouter(prefix="/compute", tags=["compute"])


@router.get("/inventory", response_model=list[ComputeNodeRead])
def inventory(db: Session = Depends(get_db)):
    return list_nodes(db)


@router.post("/register-node", response_model=ComputeNodeRead)
def register_node_endpoint(payload: ComputeNodeCreate, db: Session = Depends(get_db)):
    try:
        return register_node(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/quote", response_model=ComputeQuoteResponse)
def quote(payload: ComputeQuoteRequest, db: Session = Depends(get_db)):
    require_active_member(db, payload.member_id)
    try:
        hourly_rate, estimated_cost = quote_compute(payload.requested_gpu_sku, payload.estimated_hours)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    gpu = GPU_PRICING[payload.requested_gpu_sku]
    receipt = write_receipt("compute_quote", payload.member_id, estimated_cost, {"gpu_sku": payload.requested_gpu_sku, "estimated_hours": payload.estimated_hours, "job_type": payload.job_type})
    return ComputeQuoteResponse(member_id=payload.member_id, requested_gpu_sku=payload.requested_gpu_sku, gpu_display_name=gpu["display_name"], hourly_rate_usd=float(hourly_rate), estimated_hours=payload.estimated_hours, estimated_cost_usd=float(estimated_cost), job_type=payload.job_type, receipt_id=receipt["receipt_id"])
