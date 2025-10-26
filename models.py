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
    
    # Pin details for map display
    population: Optional[int] = None
    pin_description: Optional[str] = None
    pin_contact_name: Optional[str] = None
    pin_contact_phone: Optional[str] = None
    pin_notes: Optional[str] = None
    show_pin: bool = Field(default=True)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
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
    
    # SEVA enhancements
    available: bool = Field(default=True, index=True)
    seva_types: str = Field(default="")  # Comma-separated: medical,electrical,spiritual,emergency
    total_seva_count: int = Field(default=0)
    last_seva_date: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    village: Optional[Village] = Relationship(back_populates="members")
    seva_responses: List["SevaResponse"] = Relationship(back_populates="volunteer")


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


class SevaRequest(SQLModel, table=True):
    """Service requests from community members"""
    __tablename__ = "seva_requests"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Request details
    seva_type: str = Field(index=True)  # medical, electrical, plumbing, spiritual, emergency, other
    urgency: str = Field(index=True)    # low, medium, high, critical
    status: str = Field(default="open", index=True)  # open, assigned, in_progress, fulfilled, closed
    
    # Location
    village_id: int = Field(foreign_key="villages.id", index=True)
    location_details: Optional[str] = None
    
    # Description
    title: str
    description: str
    contact_phone: str
    
    # Tracking
    requested_by: str  # Name of person requesting
    assigned_to_id: Optional[int] = Field(default=None, foreign_key="members.id")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    fulfilled_at: Optional[datetime] = None
    
    # Relationships
    village: Optional[Village] = Relationship()
    assigned_volunteer: Optional[Member] = Relationship()
    responses: List["SevaResponse"] = Relationship(back_populates="request")
    testimonials: List["Testimonial"] = Relationship(back_populates="seva_request")


class SevaResponse(SQLModel, table=True):
    """Volunteer responses to seva requests"""
    __tablename__ = "seva_responses"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Links
    request_id: int = Field(foreign_key="seva_requests.id", index=True)
    volunteer_id: int = Field(foreign_key="members.id", index=True)
    
    # Response
    status: str = Field(default="offered")  # offered, accepted, declined, completed
    notes: Optional[str] = None
    estimated_time: Optional[str] = None  # "30 minutes", "1 hour", etc.
    
    # Timestamps
    responded_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Relationships
    request: Optional[SevaRequest] = Relationship(back_populates="responses")
    volunteer: Optional[Member] = Relationship(back_populates="seva_responses")


class Testimonial(SQLModel, table=True):
    """Gratitude messages and seva impact stories"""
    __tablename__ = "testimonials"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Story details
    author_name: str
    author_phone: Optional[str] = None
    content: str  # The gratitude message or story
    
    # Context
    village_id: Optional[int] = Field(default=None, foreign_key="villages.id")
    seva_request_id: Optional[int] = Field(default=None, foreign_key="seva_requests.id")
    seva_type: Optional[str] = None  # medical, electrical, etc.
    volunteer_name: Optional[str] = None  # Name of volunteer being thanked
    
    # Moderation
    verified: bool = Field(default=False, index=True)
    featured: bool = Field(default=False)  # Highlight special stories
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Relationships
    village: Optional[Village] = Relationship()
    seva_request: Optional[SevaRequest] = Relationship(back_populates="testimonials")


class BlockSettings(SQLModel, table=True):
    """Administrative block visual settings for map display"""
    __tablename__ = "block_settings"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    block_name: str = Field(unique=True, index=True)
    
    # Visual properties
    color: str = Field(default="#00FFFF")  # Hex color
    fill_opacity: float = Field(default=0.15)  # 0.0 to 1.0
    border_width: int = Field(default=2)  # pixels
    glow_intensity: int = Field(default=80)  # 0-100
    show_boundary: bool = Field(default=True)
    
    # Timestamps
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MapSettings(SQLModel, table=True):
    """Global map visualization settings (admin-controlled)"""
    __tablename__ = "map_settings"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Choropleth settings
    metric_name: str = Field(default="population")  # population, seva_count, literacy_rate, development_index
    color_scheme: str = Field(default="Blues")  # Blues, Greens, Reds, Purples, Oranges, Viridis, Turbo
    
    # Display options
    show_villages: bool = Field(default=True)
    show_blocks: bool = Field(default=True)
    village_point_color: str = Field(default="#e63946")  # Red dots
    
    # Timestamps
    updated_at: datetime = Field(default_factory=datetime.utcnow)
