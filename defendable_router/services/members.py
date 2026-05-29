import uuid
from datetime import UTC, timedelta
from sqlalchemy.orm import Session
from defendable_router.core.receipts import write_receipt
from defendable_router.core.time import utc_now
from defendable_router.db.models import Member, MemberStatus


def create_member(db: Session, email: str, name: str) -> Member:
    """Create an inactive member record pending annual membership activation."""
    member = Member(id=f"mem_{uuid.uuid4().hex}", email=email, name=name, status=MemberStatus.inactive.value)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def get_member(db: Session, member_id: str) -> Member | None:
    """Return a member by ID, or None when the member does not exist."""
    return db.get(Member, member_id)


def _as_aware_utc(value):
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def is_member_active(member: Member) -> bool:
    """Return True when a member is paid, active, and not expired."""
    expires_at = _as_aware_utc(member.membership_expires_at)
    return bool(
        member.status == MemberStatus.active.value
        and member.annual_fee_paid
        and expires_at
        and expires_at > utc_now()
    )


def activate_member(db: Session, member_id: str) -> Member:
    """Mark a member active for one year and emit a membership receipt."""
    member = db.get(Member, member_id)
    if member is None:
        raise ValueError("member not found")
    now = utc_now()
    member.status = MemberStatus.active.value
    member.annual_fee_paid = True
    member.membership_started_at = now
    member.membership_expires_at = now + timedelta(days=365)
    db.commit()
    db.refresh(member)
    write_receipt("membership", member.id, "100.00", {"action": "activate", "annual_fee_paid": True})
    return member
