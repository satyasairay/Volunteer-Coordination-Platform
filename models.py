from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


class Village(SQLModel, table=True):
    __tablename__ = "villages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    block: str
    district: str = Field(default="Bhadrak")
    state: str = Field(default="Odisha")
    lat: float
    lng: float
    south: float
    west: float
    north: float
    east: float
    code_2011: Optional[str] = None
    
    members: List["Member"] = Relationship(back_populates="village")


class Member(SQLModel, table=True):
    __tablename__ = "members"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str = Field(index=True)
    role: str
    phone: str
    languages: str = Field(default="")
    verified: bool = Field(default=False, index=True)
    notes: Optional[str] = None
    village_id: int = Field(foreign_key="villages.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    village: Optional[Village] = Relationship(back_populates="members")


class Doctor(SQLModel, table=True):
    __tablename__ = "doctors"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str = Field(index=True)
    specialty: str = Field(index=True)
    city: str = Field(index=True)
    hospital: str
    phone: str
    languages: str = Field(default="")
    referral_reason: Optional[str] = None
    referred_by: Optional[str] = None
    rank: int = Field(default=0)
    verified: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Audit(SQLModel, table=True):
    __tablename__ = "audit"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    table_name: str
    row_id: int
    action: str
    changed_by: str
    changed_at: datetime = Field(default_factory=datetime.utcnow)
    diff: Optional[str] = None


class Report(SQLModel, table=True):
    __tablename__ = "reports"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    table_name: str
    row_id: int
    reason: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by_ip: str
