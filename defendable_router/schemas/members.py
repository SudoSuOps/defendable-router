from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class MemberCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1)


class MemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    name: str
    status: str
    annual_fee_paid: bool
    membership_started_at: datetime | None
    membership_expires_at: datetime | None
    created_at: datetime


class MemberStatusRead(BaseModel):
    member_id: str
    status: str
    active: bool
    annual_fee_paid: bool
    membership_expires_at: datetime | None
