from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from defendable_router.db.session import get_db
from defendable_router.services.members import get_member, is_member_active
from defendable_router.services.workers import authenticate_worker

worker_bearer = HTTPBearer(auto_error=False)


def require_active_member(db: Session, member_id: str):
    member = get_member(db, member_id)
    if member is None or not is_member_active(member):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Active membership required")
    return member


def require_worker(db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials | None = Depends(worker_bearer)):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Worker bearer token required")
    worker = authenticate_worker(db, credentials.credentials)
    if worker is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid worker token")
    if worker.status == "banned":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Worker banned")
    return worker
