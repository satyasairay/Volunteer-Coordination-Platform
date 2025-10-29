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
    field_workers: List["FieldWorker"] = Relationship(back_populates="village")


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
    
    # Pin settings (DEPRECATED - use dot_style instead)
    pin_style: str = Field(default="mappin")  # mappin, diamond, star, triangle, hexagon, pentagon, marker
    pin_color_scheme: str = Field(default="Blues")  # Blues, Oranges, Greens
    pin_color_metric: str = Field(default="field_workers")  # field_workers, uk_centers, population, custom
    show_pins: bool = Field(default=True)
    
    # NEW: 3D Glowing Dot settings
    dot_style: str = Field(default="neon_glow")  # neon_glow, pulse_ring, double_halo, soft_blur, sharp_core, plasma, crystal
    
    # Timestamps
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class VillagePin(SQLModel, table=True):
    """Village pin data - field workers, UK centers, custom metrics"""
    __tablename__ = "village_pins"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    village_id: int = Field(index=True, unique=True)
    
    # Core metrics
    field_worker_count: int = Field(default=0)
    uk_center_count: int = Field(default=0)
    
    # Custom fields (flexible JSON storage)
    custom_data: Optional[str] = Field(default="{}")  # JSON string for custom fields
    
    # Pin appearance
    pin_color: Optional[str] = None  # Override color for this specific village
    is_active: bool = Field(default=True)
    
    # Modal quick links (JSON array of {label, url, icon})
    quick_links: Optional[str] = Field(default="[]")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CustomLabel(SQLModel, table=True):
    """Customizable labels for UI elements (admin can change anytime)"""
    __tablename__ = "custom_labels"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    label_key: str = Field(unique=True, index=True)  # field_workers, uk_centers, etc.
    label_value: str  # "Field Workers", "Upayojana Kendra", etc.
    label_singular: Optional[str] = None  # "Field Worker", "UK"
    label_icon: Optional[str] = Field(default="👥")  # Emoji or icon class
    
    # Display settings
    show_in_tooltip: bool = Field(default=True)
    show_in_modal: bool = Field(default=True)
    display_order: int = Field(default=0)
    
    # Timestamps
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BlockStatistics(SQLModel, table=True):
    """Real-time block-level statistics for Phase 2 & 3"""
    __tablename__ = "block_statistics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    block_name: str = Field(unique=True, index=True)
    block_code: str = Field(index=True)
    
    # Core metrics
    total_villages: int = Field(default=0)
    population: int = Field(default=0)
    
    # Seva activity (Phase 2)
    active_seva_requests: int = Field(default=0)
    total_seva_requests: int = Field(default=0)
    fulfilled_seva_count: int = Field(default=0)
    avg_response_time_hours: Optional[float] = None
    testimonial_count: int = Field(default=0)
    
    # Coverage metrics
    villages_with_members: int = Field(default=0)
    total_volunteers: int = Field(default=0)
    coverage_percentage: float = Field(default=0.0)  # % villages with active members
    
    # Activity level (for color coding)
    activity_level: str = Field(default="none")  # none, low, medium, high
    activity_color: str = Field(default="#9ca3af")  # gray, orange, yellow, green
    
    # Heat map data (Phase 3)
    seva_density: float = Field(default=0.0)  # Requests per 1000 people
    population_density: float = Field(default=0.0)  # People per sq km
    
    # Timestamps
    last_calculated: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class User(SQLModel, table=True):
    """User authentication and role management - Version 2.0.0"""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Authentication
    email: str = Field(unique=True, index=True)
    password_hash: str
    
    # Profile
    full_name: str
    phone: str
    
    # Role & Multi-Block Access
    role: str = Field(index=True)  # 'super_admin', 'block_coordinator'
    primary_block: str = Field(index=True)  # Default block from registration
    assigned_blocks: str = Field(default="")  # Comma-separated: "Bhadrak,Tihidi,Basudevpur"
    
    # Approval Status
    is_active: bool = Field(default=False, index=True)
    approved_by: Optional[str] = None  # Admin email who approved
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    # Tracking
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    login_count: int = Field(default=0)
    
    # Relationships
    field_worker_entries: List["FieldWorker"] = Relationship(back_populates="submitted_by_user")


class FieldWorker(SQLModel, table=True):
    """Field Worker contact information with approval workflow - Version 2.0.0"""
    __tablename__ = "field_workers"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Core Data
    full_name: str = Field(index=True)
    phone: str = Field(index=True)  # For duplicate checking
    alternate_phone: Optional[str] = None
    email: Optional[str] = None
    village_id: int = Field(foreign_key="villages.id", index=True)
    address_line: Optional[str] = None
    landmark: Optional[str] = None
    designation: str
    department: Optional[str] = None
    employee_id: Optional[str] = None
    
    # Contact Preferences
    preferred_contact_method: str = Field(default="phone")  # phone, email, whatsapp
    available_days: Optional[str] = None  # "Mon-Fri", "All days", etc.
    available_hours: Optional[str] = None  # "9AM-5PM", "24/7", etc.
    
    # Approval Workflow
    status: str = Field(default="pending", index=True)  # 'pending', 'approved', 'rejected'
    submitted_by_user_id: int = Field(foreign_key="users.id", index=True)
    approved_by: Optional[str] = None  # Admin email
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    # Duplicate Exception Handling
    duplicate_exception_reason: Optional[str] = None  # Submitter's reason for exception
    duplicate_of_phone: Optional[str] = None  # Which phone number is duplicate
    
    # Status
    is_active: bool = Field(default=True, index=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_verified_at: Optional[datetime] = None
    
    # Relationships
    village: Optional[Village] = Relationship(back_populates="field_workers")
    submitted_by_user: Optional[User] = Relationship(back_populates="field_worker_entries")


class FormFieldConfig(SQLModel, table=True):
    """Admin-configurable Field Worker form fields - Version 2.0.0"""
    __tablename__ = "form_field_config"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    field_name: str = Field(unique=True, index=True)  # 'full_name', 'phone', 'email', etc.
    
    # Configuration
    is_required: bool = Field(default=False)
    is_visible: bool = Field(default=True)
    display_order: int = Field(default=0, index=True)
    
    # Display Properties
    field_label: str  # "Full Name", "Phone Number", etc.
    field_type: str  # 'text', 'tel', 'email', 'textarea', 'select'
    placeholder: Optional[str] = None
    help_text: Optional[str] = None  # Helper text shown below field
    
    # Validation
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None  # Regex pattern for validation
    
    # For select fields
    options: Optional[str] = None  # JSON array of options
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
