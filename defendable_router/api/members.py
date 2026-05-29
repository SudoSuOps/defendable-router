from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from defendable_router.db.session import get_db
from defendable_router.schemas.members import MemberCreate, MemberRead, MemberStatusRead
from defendable_router.services.members import activate_member, create_member, get_member, is_member_active

router = APIRouter(prefix="/members", tags=["members"])


@router.post("", response_model=MemberRead)
def create_member_endpoint(payload: MemberCreate, db: Session = Depends(get_db)):
    return create_member(db, payload.email, payload.name)


@router.get("/{member_id}", response_model=MemberRead)
def read_member(member_id: str, db: Session = Depends(get_db)):
    member = get_member(db, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="member not found")
    return member


@router.post("/{member_id}/activate", response_model=MemberRead)
def activate_member_endpoint(member_id: str, db: Session = Depends(get_db)):
    try:
        return activate_member(db, member_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{member_id}/status", response_model=MemberStatusRead)
def member_status(member_id: str, db: Session = Depends(get_db)):
    member = get_member(db, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="member not found")
    return MemberStatusRead(member_id=member.id, status=member.status, active=is_member_active(member), annual_fee_paid=member.annual_fee_paid, membership_expires_at=member.membership_expires_at)
