from fastapi import FastAPI, Request, Depends, HTTPException, Form, UploadFile, File, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import csv
import io
import json
import os
from datetime import datetime
from contextlib import asynccontextmanager

STATIC_VILLAGE_FEATURES: list[dict] | None = None
STATIC_BLOCK_FEATURE_MAP: dict[str, list[dict]] = {}
STATIC_BLOCK_CACHE: dict[str, dict | None] = {}


def _normalize_block(name: str) -> str:
    return ''.join(ch for ch in name.lower() if ch.isalnum())


async def ensure_static_village_features() -> list[dict]:
    global STATIC_VILLAGE_FEATURES, STATIC_BLOCK_FEATURE_MAP
    if STATIC_VILLAGE_FEATURES is None:
        with open('static/geojson/bhadrak_villages.geojson', 'r', encoding='utf-8') as f:
            data = json.load(f)
            STATIC_VILLAGE_FEATURES = data.get('features', [])

        block_map: dict[str, list[dict]] = {}
        for feature in STATIC_VILLAGE_FEATURES:
            props = feature.get('properties', {})
            block = (props.get('SUB_DIST') or props.get('block') or '').strip()
            if not block:
                continue
            normalized = _normalize_block(block)
            block_map.setdefault(normalized, []).append(feature)
        STATIC_BLOCK_FEATURE_MAP = block_map
    return STATIC_VILLAGE_FEATURES


async def get_block_bounds_from_static(block_name: str) -> dict | None:
    if not block_name:
        return None

    await ensure_static_village_features()
    normalized = _normalize_block(block_name)

    if normalized in STATIC_BLOCK_CACHE:
        return STATIC_BLOCK_CACHE[normalized]

    block_features = STATIC_BLOCK_FEATURE_MAP.get(normalized)
    if not block_features:
        from difflib import get_close_matches
        matches = get_close_matches(normalized, list(STATIC_BLOCK_FEATURE_MAP.keys()), n=1, cutoff=0.72)
        if matches:
            normalized = matches[0]
            block_features = STATIC_BLOCK_FEATURE_MAP.get(normalized)
        else:
            STATIC_BLOCK_CACHE[normalized] = None
            return None

    lats: list[float] = []
    lngs: list[float] = []
    south = north = west = east = None

    for feature in block_features:
        geometry = feature.get('geometry', {})
        coords = geometry.get('coordinates', [])
        if geometry.get('type') == 'Polygon':
            polygons = [coords]
        elif geometry.get('type') == 'MultiPolygon':
            polygons = coords
        else:
            polygons = []

        for polygon in polygons:
            for ring in polygon:
                for lng, lat in ring:
                    lats.append(lat)
                    lngs.append(lng)
                    south = lat if south is None else min(south, lat)
                    north = lat if north is None else max(north, lat)
                    west = lng if west is None else min(west, lng)
                    east = lng if east is None else max(east, lng)

    if not lats or not lngs:
        STATIC_BLOCK_CACHE[normalized] = None
        return None

    stats = {
        'lat': sum(lats) / len(lats),
        'lng': sum(lngs) / len(lngs),
        'south': south,
        'west': west,
        'north': north,
        'east': east
    }
    STATIC_BLOCK_CACHE[normalized] = stats
    return stats


from db import init_db, get_session
from models import Village, Member, Doctor, Audit, Report, SevaRequest, SevaResponse, Testimonial, BlockSettings, MapSettings, VillagePin, CustomLabel, BlockStatistics, User, FieldWorker, FormFieldConfig, AboutPage
from auth import create_session_token, get_current_admin, get_current_user, get_optional_user, require_super_admin, require_block_coordinator, ADMIN_EMAIL, ADMIN_PASSWORD, pwd_context, hash_password


async def seed_default_labels(session: AsyncSession):
    """Initialize default custom labels if they don't exist"""
    default_labels = [
        {
            "label_key": "field_workers",
            "label_value": "Field Workers",
            "label_singular": "Field Worker",
            "label_icon": "👥",
            "show_in_tooltip": True,
            "show_in_modal": True,
            "display_order": 1
        },
        {
            "label_key": "uk_centers",
            "label_value": "Upayojana Kendras",
            "label_singular": "UK",
            "label_icon": "🏢",
            "show_in_tooltip": True,
            "show_in_modal": True,
            "display_order": 2
        },
        {
            "label_key": "population",
            "label_value": "Population",
            "label_singular": "Population",
            "label_icon": "📊",
            "show_in_tooltip": True,
            "show_in_modal": True,
            "display_order": 3
        }
    ]
    
    for label_data in default_labels:
        result = await session.execute(
            select(CustomLabel).where(CustomLabel.label_key == label_data["label_key"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            label = CustomLabel(**label_data)
            session.add(label)
    
    await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    
    # Seed default labels
    from db import async_session_maker
    async with async_session_maker() as session:
        await seed_default_labels(session)
    
    print("\n" + "=" * 60)
    print("SATSANGEE SEVA ATLAS - Ready to Serve")
    print("=" * 60)
    print("Public URLs:")
    print("   Seva Map:    http://0.0.0.0:5000/")
    print("   Doctors:     http://0.0.0.0:5000/doctors")
    print("\nAdmin URLs:")
    print("   Login:       http://0.0.0.0:5000/admin/login")
    print("   Dashboard:   http://0.0.0.0:5000/admin")
    print("=" * 60 + "\n")
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    mapbox_token = os.getenv("MAPBOX_ACCESS_TOKEN", "")
    user = get_optional_user(request)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "mapbox_token": mapbox_token,
        "user": user
    })


@app.get("/sample", response_class=HTMLResponse)
async def sample_choropleth(request: Request):
    """Sample village-level choropleth demonstration"""
    return templates.TemplateResponse("sample_village_choropleth.html", {"request": request})


@app.get("/doctors", response_class=HTMLResponse)
async def doctors_page(
    request: Request,
    city: Optional[str] = None,
    specialty: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    query = select(Doctor).where(Doctor.verified == True)
    
    if city:
        query = query.where(Doctor.city == city)
    if specialty:
        query = query.where(Doctor.specialty.contains(specialty))
    
    query = query.order_by(Doctor.city, Doctor.specialty, Doctor.rank)
    result = await session.execute(query)
    doctors = result.scalars().all()
    
    all_cities = await session.execute(select(Doctor.city).distinct().where(Doctor.verified == True))
    cities = [c for c in all_cities.scalars().all()]
    
    all_specialties = await session.execute(select(Doctor.specialty).distinct().where(Doctor.verified == True))
    specialties = [s for s in all_specialties.scalars().all()]
    
    return templates.TemplateResponse("doctors.html", {
        "request": request,
        "doctors": doctors,
        "cities": cities,
        "specialties": specialties,
        "selected_city": city,
        "selected_specialty": specialty
    })


@app.get("/api/villages")
async def get_villages(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Village))
    villages = result.scalars().all()
    
    return [{
        "id": v.id,
        "name": v.name,
        "block": v.block,
        "lat": v.lat,
        "lng": v.lng,
        "bbox": [v.south, v.west, v.north, v.east],
        "show_pin": v.show_pin
    } for v in villages]


@app.get("/api/villages/choropleth")
async def get_villages_choropleth():
    """Return ALL 1,315 village geometries for choropleth with real data"""
    import json
    
    # Load full village data (cached in memory after first load)
    if not hasattr(get_villages_choropleth, '_cache'):
        with open('static/geojson/bhadrak_villages.geojson', 'r') as f:
            villages_data = json.load(f)
        
        # Process all villages with real data
        features = []
        for i, feature in enumerate(villages_data['features']):
            props = feature['properties']
            features.append({
                "type": "Feature",
                "properties": {
                    "name": props.get('NAME', props.get('name', f'Village_{i}')),
                    "block": props.get('SUB_DIST', props.get('block', 'Unknown')),
                    "population": props.get('population', props.get('POP', 1000 + (i * 10))),
                },
                "geometry": feature['geometry']
            })
        
        get_villages_choropleth._cache = {
            "type": "FeatureCollection",
            "features": features
        }
    
    return get_villages_choropleth._cache


@app.get("/api/village/{village_name}")
async def get_village_details(village_name: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Village).where(Village.name == village_name))
    village = result.scalar_one_or_none()
    
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    
    return {
        "id": village.id,
        "name": village.name,
        "block": village.block,
        "lat": village.lat,
        "lng": village.lng,
        "population": village.population,
        "pin_description": village.pin_description,
        "pin_contact_name": village.pin_contact_name,
        "pin_contact_phone": village.pin_contact_phone,
        "pin_notes": village.pin_notes,
        "show_pin": village.show_pin
    }


@app.get("/api/villages/pins")
async def get_village_pins(session: AsyncSession = Depends(get_session)):
    """FAST LOAD: Return enriched pin data - frontend loads geojson directly"""
    # Only return pin data enrichment - frontend loads static geojson file
    
    # Get all village pins from database
    pins_result = await session.execute(select(VillagePin))
    pins_list = pins_result.scalars().all()
    
    # Get custom labels for display
    labels_result = await session.execute(
        select(CustomLabel).order_by(CustomLabel.display_order)
    )
    labels = {label.label_key: label for label in labels_result.scalars().all()}
    
    # Return pin enrichment data only (frontend merges with static geojson)
    pin_data = {}
    for pin in pins_list:
        pin_data[pin.village_id] = {
            "field_worker_count": pin.field_worker_count,
            "uk_center_count": pin.uk_center_count,
            "custom_data": json.loads(pin.custom_data) if pin.custom_data else {},
            "pin_color": pin.pin_color,
            "is_active": pin.is_active,
        }
    
    return {
        "pin_data": pin_data,
        "labels": {
            key: {
                "value": label.label_value,
                "singular": label.label_singular,
                "icon": label.label_icon
            }
            for key, label in labels.items()
        },
        "geojson_url": "/static/geojson/bhadrak_villages.geojson"  # Tell frontend where to load
    }


@app.get("/api/villages/{village_id}/details")
async def get_village_pin_details(village_id: int, session: AsyncSession = Depends(get_session)):
    """Get detailed village info for modal"""
    # Get village basic info
    result = await session.execute(select(Village).where(Village.id == village_id))
    village = result.scalar_one_or_none()
    
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    
    # Get pin data
    pin_result = await session.execute(
        select(VillagePin).where(VillagePin.village_id == village_id)
    )
    pin = pin_result.scalar_one_or_none()
    
    # Get custom labels
    labels_result = await session.execute(
        select(CustomLabel).order_by(CustomLabel.display_order)
    )
    labels = {label.label_key: label for label in labels_result.scalars().all()}
    
    return {
        "id": village.id,
        "name": village.name,
        "block": village.block,
        "population": village.population,
        "field_worker_count": pin.field_worker_count if pin else 0,
        "uk_center_count": pin.uk_center_count if pin else 0,
        "custom_data": json.loads(pin.custom_data) if pin and pin.custom_data else {},
        "quick_links": json.loads(pin.quick_links) if pin and pin.quick_links else [],
        "labels": {
            key: {
                "value": label.label_value,
                "singular": label.label_singular,
                "icon": label.label_icon
            }
            for key, label in labels.items() if label.show_in_modal
        }
    }


@app.get("/api/custom-labels")
async def get_custom_labels(session: AsyncSession = Depends(get_session)):
    """Get all customizable labels for UI"""
    result = await session.execute(select(CustomLabel).order_by(CustomLabel.display_order))
    labels = result.scalars().all()
    
    return [{
        "key": label.label_key,
        "value": label.label_value,
        "singular": label.label_singular,
        "icon": label.label_icon,
        "show_in_tooltip": label.show_in_tooltip,
        "show_in_modal": label.show_in_modal
    } for label in labels]


@app.get("/api/blocks/colors")
async def get_block_colors(session: AsyncSession = Depends(get_session)):
    """Get visual settings for all blocks"""
    result = await session.execute(select(BlockSettings))
    blocks = result.scalars().all()
    
    colors = {}
    for block in blocks:
        colors[block.block_name] = {
            "color": block.color,
            "fillOpacity": block.fill_opacity,
            "borderWidth": block.border_width,
            "glowIntensity": block.glow_intensity,
            "showBoundary": block.show_boundary
        }
    
    return colors


@app.get("/api/members")
async def get_members(
    village_id: Optional[int] = None,
    role: Optional[str] = None,
    verified: Optional[bool] = True,
    q: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    query = select(Member)
    
    if verified is not None:
        query = query.where(Member.verified == verified)
    if village_id:
        query = query.where(Member.village_id == village_id)
    if role:
        query = query.where(Member.role == role)
    if q:
        query = query.where(or_(
            Member.full_name.contains(q),
            Member.phone.contains(q)
        ))
    
    result = await session.execute(query)
    members = result.scalars().all()
    
    return [{
        "id": m.id,
        "full_name": m.full_name,
        "role": m.role,
        "phone": m.phone,
        "languages": m.languages,
        "verified": m.verified,
        "village_id": m.village_id
    } for m in members]


@app.get("/api/village/{village_id}/volunteers")
async def get_village_volunteers(
    village_id: int,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Member).where(
            Member.village_id == village_id,
            Member.verified == True
        )
    )
    members = result.scalars().all()
    
    return [{
        "id": m.id,
        "full_name": m.full_name,
        "role": m.role,
        "phone": m.phone,
        "languages": m.languages
    } for m in members]


@app.post("/report")
async def create_report(
    request: Request,
    table_name: str = Form(...),
    row_id: int = Form(...),
    reason: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    client_ip = request.client.host
    
    report = Report(
        table_name=table_name,
        row_id=row_id,
        reason=reason,
        created_by_ip=client_ip
    )
    session.add(report)
    await session.commit()
    
    return {"status": "success", "message": "Report submitted"}


# ============================================================
# SEVA API ENDPOINTS
# ============================================================

@app.get("/api/seva/feed")
async def get_seva_feed(
    limit: int = 20,
    session: AsyncSession = Depends(get_session)
):
    """Get real-time seva activity feed - requests, responses, testimonials"""
    
    # Get recent requests
    requests_query = select(SevaRequest).order_by(SevaRequest.created_at.desc()).limit(limit)
    result = await session.execute(requests_query)
    requests = result.scalars().all()
    
    # Get recent responses
    responses_query = select(SevaResponse).order_by(SevaResponse.responded_at.desc()).limit(limit)
    result = await session.execute(responses_query)
    responses = result.scalars().all()
    
    # Get recent testimonials
    testimonials_query = select(Testimonial).where(Testimonial.verified == True).order_by(Testimonial.created_at.desc()).limit(limit)
    result = await session.execute(testimonials_query)
    testimonials = result.scalars().all()
    
    # Build unified feed
    feed_items = []
    
    for req in requests:
        village = await session.get(Village, req.village_id)
        feed_items.append({
            "type": "request",
            "id": req.id,
            "seva_type": req.seva_type,
            "urgency": req.urgency,
            "status": req.status,
            "title": req.title,
            "village_name": village.name if village else "Unknown",
            "requested_by": req.requested_by,
            "created_at": req.created_at.isoformat()
        })
    
    for resp in responses:
        volunteer = await session.get(Member, resp.volunteer_id)
        request_obj = await session.get(SevaRequest, resp.request_id)
        feed_items.append({
            "type": "response",
            "id": resp.id,
            "volunteer_name": volunteer.full_name if volunteer else "Unknown",
            "seva_type": request_obj.seva_type if request_obj else "Unknown",
            "status": resp.status,
            "responded_at": resp.responded_at.isoformat()
        })
    
    for test in testimonials:
        village = await session.get(Village, test.village_id) if test.village_id else None
        feed_items.append({
            "type": "testimonial",
            "id": test.id,
            "author_name": test.author_name,
            "content": test.content[:200],  # Truncate for feed
            "seva_type": test.seva_type,
            "village_name": village.name if village else None,
            "created_at": test.created_at.isoformat()
        })
    
    # Sort all by timestamp
    feed_items.sort(key=lambda x: x.get("created_at") or x.get("responded_at"), reverse=True)
    
    return {"feed": feed_items[:limit]}


@app.get("/api/seva/requests")
async def get_seva_requests(
    status: Optional[str] = None,
    seva_type: Optional[str] = None,
    urgency: Optional[str] = None,
    village_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session)
):
    """Get seva requests with filters"""
    query = select(SevaRequest)
    
    if status:
        query = query.where(SevaRequest.status == status)
    if seva_type:
        query = query.where(SevaRequest.seva_type == seva_type)
    if urgency:
        query = query.where(SevaRequest.urgency == urgency)
    if village_id:
        query = query.where(SevaRequest.village_id == village_id)
    
    query = query.order_by(SevaRequest.created_at.desc())
    result = await session.execute(query)
    requests = result.scalars().all()
    
    items = []
    for req in requests:
        village = await session.get(Village, req.village_id)
        assigned_volunteer = await session.get(Member, req.assigned_to_id) if req.assigned_to_id else None
        
        items.append({
            "id": req.id,
            "seva_type": req.seva_type,
            "urgency": req.urgency,
            "status": req.status,
            "title": req.title,
            "description": req.description,
            "contact_phone": req.contact_phone,
            "requested_by": req.requested_by,
            "village_name": village.name if village else "Unknown",
            "village_id": req.village_id,
            "assigned_volunteer": assigned_volunteer.full_name if assigned_volunteer else None,
            "created_at": req.created_at.isoformat()
        })
    
    return {"requests": items}


@app.post("/api/seva/request")
async def create_seva_request(
    seva_type: str = Form(...),
    urgency: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    village_id: int = Form(...),
    requested_by: str = Form(...),
    contact_phone: str = Form(...),
    location_details: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session)
):
    """Create a new seva request"""
    seva_request = SevaRequest(
        seva_type=seva_type,
        urgency=urgency,
        title=title,
        description=description,
        village_id=village_id,
        requested_by=requested_by,
        contact_phone=contact_phone,
        location_details=location_details,
        status="open"
    )
    
    session.add(seva_request)
    await session.commit()
    await session.refresh(seva_request)
    
    return {
        "status": "success",
        "message": "Seva request created",
        "request_id": seva_request.id
    }


@app.post("/api/seva/respond")
async def respond_to_seva(
    request_id: int = Form(...),
    volunteer_id: int = Form(...),
    notes: Optional[str] = Form(None),
    estimated_time: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session)
):
    """Volunteer responds to a seva request"""
    seva_response = SevaResponse(
        request_id=request_id,
        volunteer_id=volunteer_id,
        status="offered",
        notes=notes,
        estimated_time=estimated_time
    )
    
    session.add(seva_response)
    
    # Update request status to assigned
    seva_request = await session.get(SevaRequest, request_id)
    if seva_request:
        seva_request.status = "assigned"
        seva_request.assigned_to_id = volunteer_id
        seva_request.updated_at = datetime.utcnow()
    
    await session.commit()
    
    return {
        "status": "success",
        "message": "Response recorded"
    }


@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    user = get_optional_user(request)
    return templates.TemplateResponse("login.html", {"request": request, "user": user})


@app.post("/admin/login")
async def admin_login(
    email: str = Form(...),
    password: str = Form(...),
):
    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        token = create_session_token(email)
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie(key="session", value=token, httponly=True, max_age=86400*7)
        return response
    
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/admin/logout")
async def admin_logout():
    response = RedirectResponse(url="/admin/login?logout=success", status_code=303)
    response.delete_cookie("session")
    return response

@app.get("/login", response_class=HTMLResponse)
async def login_redirect():
    """User-friendly login redirect"""
    return RedirectResponse(url="/admin/login", status_code=303)


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    admin=Depends(get_current_admin),
    session: AsyncSession = Depends(get_session)
):
    villages_count = await session.execute(select(Village))
    members_count = await session.execute(select(Member))
    doctors_count = await session.execute(select(Doctor))
    
    stats = {
        "villages": len(villages_count.scalars().all()),
        "members": len(members_count.scalars().all()),
        "doctors": len(doctors_count.scalars().all())
    }
    
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "stats": stats,
        "admin": admin
    })


@app.get("/admin/members", response_class=HTMLResponse)
async def admin_members_page(
    request: Request,
    q: Optional[str] = None,
    admin=Depends(get_current_admin),
    session: AsyncSession = Depends(get_session)
):
    query = select(Member).join(Village)
    
    if q:
        query = query.where(or_(
            Member.full_name.contains(q),
            Member.phone.contains(q),
            Village.name.contains(q)
        ))
    
    result = await session.execute(query)
    members = result.scalars().all()
    
    villages_result = await session.execute(select(Village))
    villages = villages_result.scalars().all()
    
    return templates.TemplateResponse("members.html", {
        "request": request,
        "members": members,
        "villages": villages,
        "admin": admin,
        "search_query": q
    })


@app.post("/admin/members/new")
async def create_member(
    full_name: str = Form(...),
    role: str = Form(...),
    phone: str = Form(...),
    languages: str = Form(""),
    notes: str = Form(""),
    village_id: int = Form(...),
    verified: bool = Form(False),
    admin=Depends(get_current_admin),
    session: AsyncSession = Depends(get_session)
):
    member = Member(
        full_name=full_name,
        role=role,
        phone=phone,
        languages=languages,
        notes=notes,
        village_id=village_id,
        verified=verified
    )
    session.add(member)
    await session.commit()
    
    audit = Audit(
        table_name="members",
        row_id=member.id,
        action="create",
        changed_by=admin["email"]
    )
    session.add(audit)
    await session.commit()
    
    return RedirectResponse(url="/admin/members", status_code=303)


@app.post("/admin/members/{member_id}/verify")
async def verify_member(
    member_id: int,
    admin=Depends(get_current_admin),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(Member).where(Member.id == member_id))
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    member.verified = True
    member.updated_at = datetime.utcnow()
    await session.commit()
    
    audit = Audit(
        table_name="members",
        row_id=member_id,
        action="verify",
        changed_by=admin["email"]
    )
    session.add(audit)
    await session.commit()
    
    return {"status": "success"}


@app.get("/admin/villages", response_class=HTMLResponse)
async def admin_villages_page(
    request: Request,
    admin=Depends(get_current_admin),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(Village))
    villages = result.scalars().all()
    
    villages_data = [{
        "id": v.id,
        "name": v.name,
        "block": v.block,
        "lat": v.lat,
        "lng": v.lng
    } for v in villages]
    
    return templates.TemplateResponse("admin_villages.html", {
        "request": request,
        "villages": villages_data,
        "admin": admin
    })


@app.post("/admin/api/villages/update")
async def update_village_coords(
    request: Request,
    admin=Depends(get_current_admin),
    session: AsyncSession = Depends(get_session)
):
    data = await request.json()
    village_id = data.get('id')
    name = data.get('name')
    block = data.get('block')
    lat = data.get('lat')
    lng = data.get('lng')
    
    # Pin details
    pin_description = data.get('pin_description')
    pin_contact_name = data.get('pin_contact_name')
    pin_contact_phone = data.get('pin_contact_phone')
    pin_notes = data.get('pin_notes')
    show_pin = data.get('show_pin', True)
    population = data.get('population')
    
    # Find or create village
    if village_id:
        result = await session.execute(select(Village).where(Village.id == int(village_id)))
        village = result.scalar_one_or_none()
    else:
        result = await session.execute(select(Village).where(Village.name == name))
        village = result.scalar_one_or_none()
    
    if not village:
        village = Village(name=name, block=block)
        session.add(village)
    
    village.lat = lat
    village.lng = lng
    village.block = block
    village.pin_description = pin_description
    village.pin_contact_name = pin_contact_name
    village.pin_contact_phone = pin_contact_phone
    village.pin_notes = pin_notes
    village.show_pin = show_pin
    if population:
        village.population = int(population)
    village.updated_at = datetime.utcnow()
    
    await session.commit()
    
    audit = Audit(
        table_name="villages",
        row_id=village.id,
        action="update_village_details",
        changed_by=admin["email"]
    )
    session.add(audit)
    await session.commit()
    
    return {"status": "success", "village_id": village.id}


@app.get("/admin/api/villages/export")
async def export_villages(
    admin=Depends(get_current_admin),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(Village))
    villages = result.scalars().all()
    
    data = [{
        "id": v.id,
        "name": v.name,
        "block": v.block,
        "lat": v.lat,
        "lng": v.lng,
        "population": v.population
    } for v in villages]
    
    return JSONResponse(content=data)


@app.post("/admin/api/blocks/update")
async def update_block_settings(
    request: Request,
    admin=Depends(get_current_admin),
    session: AsyncSession = Depends(get_session)
):
    """Update block visual settings"""
    data = await request.json()
    block_name = data.get('block_name')
    
    # Find block
    result = await session.execute(select(BlockSettings).where(BlockSettings.block_name == block_name))
    block = result.scalar_one_or_none()
    
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    
    # Update fields
    if 'color' in data:
        block.color = data['color']
    if 'fill_opacity' in data:
        block.fill_opacity = float(data['fill_opacity'])
    if 'border_width' in data:
        block.border_width = int(data['border_width'])
    if 'glow_intensity' in data:
        block.glow_intensity = int(data['glow_intensity'])
    if 'show_boundary' in data:
        block.show_boundary = bool(data['show_boundary'])
    
    block.updated_at = datetime.utcnow()
    await session.commit()
    
    # Audit log
    audit = Audit(
        table_name="block_settings",
        row_id=block.id,
        action="update_block_visual_settings",
        changed_by=admin["email"]
    )
    session.add(audit)
    await session.commit()
    
    return {"status": "success", "block_name": block_name}


@app.get("/admin/settings/blocks", response_class=HTMLResponse)
async def admin_blocks_page(
    request: Request,
    admin=Depends(get_current_admin)
):
    """Admin page for managing block color settings"""
    return templates.TemplateResponse("admin_blocks.html", {
        "request": request,
        "admin": admin
    })


@app.get("/api/map-settings")
async def get_map_settings(session: AsyncSession = Depends(get_session)):
    """Get current map visualization settings"""
    result = await session.execute(select(MapSettings))
    settings = result.scalar_one_or_none()
    
    # Return defaults if no settings exist
    if not settings:
        return {
            "metric_name": "population",
            "color_scheme": "Blues",
            "show_villages": True,
            "show_blocks": True,
            "village_point_color": "#e63946",
            "pin_style": "mappin",
            "pin_color_scheme": "Blues",
            "pin_color_metric": "field_workers",
            "show_pins": True,
            "dot_style": "neon_glow"
        }
    
    return {
        "metric_name": settings.metric_name,
        "color_scheme": settings.color_scheme,
        "show_villages": settings.show_villages,
        "show_blocks": settings.show_blocks,
        "village_point_color": settings.village_point_color,
        "pin_style": settings.pin_style,
        "pin_color_scheme": settings.pin_color_scheme,
        "pin_color_metric": settings.pin_color_metric,
        "show_pins": settings.show_pins,
        "dot_style": settings.dot_style
    }


@app.put("/api/map-settings")
async def update_map_settings(
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """Update map visualization settings (used by admin panel)"""
    data = await request.json()
    
    # Get or create settings
    result = await session.execute(select(MapSettings))
    settings = result.scalar_one_or_none()
    
    if not settings:
        settings = MapSettings()
        session.add(settings)
    
    # Update fields if provided
    if "metric_name" in data:
        settings.metric_name = data["metric_name"]
    if "color_scheme" in data:
        settings.color_scheme = data["color_scheme"]
    if "show_villages" in data:
        settings.show_villages = data["show_villages"]
    if "show_blocks" in data:
        settings.show_blocks = data["show_blocks"]
    if "village_point_color" in data:
        settings.village_point_color = data["village_point_color"]
    if "pin_style" in data:
        settings.pin_style = data["pin_style"]
    if "pin_color_scheme" in data:
        settings.pin_color_scheme = data["pin_color_scheme"]
    if "pin_color_metric" in data:
        settings.pin_color_metric = data["pin_color_metric"]
    if "show_pins" in data:
        settings.show_pins = data["show_pins"]
    if "dot_style" in data:
        settings.dot_style = data["dot_style"]
    
    settings.updated_at = datetime.utcnow()
    
    await session.commit()
    
    return {"status": "success", "message": "Settings updated successfully"}


# ============================================================
# PHASE 2 & 3: BLOCK STATISTICS & HEAT MAP APIs
# ============================================================

@app.get("/api/blocks")
async def get_blocks():
    """Get all block boundaries (GeoJSON) for Phase 2"""
    with open('static/geojson/bhadrak_blocks.geojson', 'r') as f:
        blocks_data = json.load(f)
    return blocks_data


@app.get("/api/blocks/statistics")
async def get_block_statistics(session: AsyncSession = Depends(get_session)):
    """Get real-time statistics for all blocks (Phase 2)"""
    result = await session.execute(select(BlockStatistics))
    stats = result.scalars().all()
    
    # If no stats exist, create default ones from blocks GeoJSON
    if not stats:
        with open('static/geojson/bhadrak_blocks.geojson', 'r') as f:
            blocks_data = json.load(f)
        
        for feature in blocks_data['features']:
            props = feature['properties']
            block_stat = BlockStatistics(
                block_name=props['name'],
                block_code=props.get('block_code', props['name'][:3].upper()),
                total_villages=props.get('villages', 0),
                population=props.get('population', 0),
                activity_level="medium",
                activity_color="#f59e0b"
            )
            session.add(block_stat)
        
        await session.commit()
        result = await session.execute(select(BlockStatistics))
        stats = result.scalars().all()
    
    return [{
        "block_name": s.block_name,
        "block_code": s.block_code,
        "total_villages": s.total_villages,
        "population": s.population,
        "active_seva_requests": s.active_seva_requests,
        "total_seva_requests": s.total_seva_requests,
        "fulfilled_seva_count": s.fulfilled_seva_count,
        "avg_response_time_hours": s.avg_response_time_hours,
        "testimonial_count": s.testimonial_count,
        "villages_with_members": s.villages_with_members,
        "total_volunteers": s.total_volunteers,
        "coverage_percentage": s.coverage_percentage,
        "activity_level": s.activity_level,
        "activity_color": s.activity_color,
        "seva_density": s.seva_density,
        "population_density": s.population_density,
        "last_calculated": s.last_calculated.isoformat() if s.last_calculated else None
    } for s in stats]


@app.post("/admin/api/blocks/statistics/refresh")
async def refresh_block_statistics(
    admin=Depends(get_current_admin),
    session: AsyncSession = Depends(get_session)
):
    """Refresh block statistics by calculating from live data (Phase 2)"""
    from sqlalchemy import func
    
    # Get all blocks
    with open('static/geojson/bhadrak_blocks.geojson', 'r') as f:
        blocks_data = json.load(f)
    
    for feature in blocks_data['features']:
        block_name = feature['properties']['name']
        
        # Get or create block statistics
        result = await session.execute(
            select(BlockStatistics).where(BlockStatistics.block_name == block_name)
        )
        block_stat = result.scalar_one_or_none()
        
        if not block_stat:
            block_stat = BlockStatistics(
                block_name=block_name,
                block_code=feature['properties'].get('block_code', block_name[:3].upper())
            )
            session.add(block_stat)
        
        # Calculate statistics
        # Total villages in this block
        village_count = await session.execute(
            select(func.count(Village.id)).where(Village.block == block_name)
        )
        block_stat.total_villages = village_count.scalar() or 0
        
        # Population
        pop_sum = await session.execute(
            select(func.sum(Village.population)).where(Village.block == block_name)
        )
        block_stat.population = int(pop_sum.scalar() or 0)
        
        # Seva requests (active and total)
        active_count = await session.execute(
            select(func.count(SevaRequest.id))
            .join(Village, SevaRequest.village_id == Village.id)
            .where(Village.block == block_name)
            .where(SevaRequest.status.in_(["open", "assigned", "in_progress"]))
        )
        block_stat.active_seva_requests = active_count.scalar() or 0
        
        total_count = await session.execute(
            select(func.count(SevaRequest.id))
            .join(Village, SevaRequest.village_id == Village.id)
            .where(Village.block == block_name)
        )
        block_stat.total_seva_requests = total_count.scalar() or 0
        
        fulfilled_count = await session.execute(
            select(func.count(SevaRequest.id))
            .join(Village, SevaRequest.village_id == Village.id)
            .where(Village.block == block_name)
            .where(SevaRequest.status == "fulfilled")
        )
        block_stat.fulfilled_seva_count = fulfilled_count.scalar() or 0
        
        # Coverage
        volunteers_count = await session.execute(
            select(func.count(Member.id))
            .join(Village, Member.village_id == Village.id)
            .where(Village.block == block_name)
            .where(Member.verified == True)
        )
        block_stat.total_volunteers = volunteers_count.scalar() or 0
        
        # Calculate activity level
        active_reqs = block_stat.active_seva_requests
        if active_reqs >= 10:
            block_stat.activity_level = "high"
            block_stat.activity_color = "#10b981"  # Green
        elif active_reqs >= 5:
            block_stat.activity_level = "medium"
            block_stat.activity_color = "#f59e0b"  # Yellow
        elif active_reqs >= 1:
            block_stat.activity_level = "low"
            block_stat.activity_color = "#f97316"  # Orange
        else:
            block_stat.activity_level = "none"
            block_stat.activity_color = "#9ca3af"  # Gray
        
        # Heat map metrics (Phase 3)
        if block_stat.population > 0:
            block_stat.seva_density = (block_stat.total_seva_requests / block_stat.population) * 1000
        
        block_stat.last_calculated = datetime.utcnow()
    
    await session.commit()
    return {"status": "success", "message": "Block statistics refreshed"}


@app.post("/admin/settings/map")
async def save_map_settings(
    request: Request,
    admin=Depends(get_current_admin),
    session: AsyncSession = Depends(get_session)
):
    """Save map visualization settings"""
    data = await request.json()
    
    # Get or create settings
    result = await session.execute(select(MapSettings))
    settings = result.scalar_one_or_none()
    
    if not settings:
        settings = MapSettings(
            metric_name=data.get("metric_name", "population"),
            color_scheme=data.get("color_scheme", "Blues"),
            show_villages=data.get("show_villages", True),
            show_blocks=data.get("show_blocks", True),
            village_point_color=data.get("village_point_color", "#e63946")
        )
        session.add(settings)
    else:
        settings.metric_name = data.get("metric_name", settings.metric_name)
        settings.color_scheme = data.get("color_scheme", settings.color_scheme)
        settings.show_villages = data.get("show_villages", settings.show_villages)
        settings.show_blocks = data.get("show_blocks", settings.show_blocks)
        settings.village_point_color = data.get("village_point_color", settings.village_point_color)
        settings.updated_at = datetime.utcnow()
    
    await session.commit()
    
    # Audit log
    audit = Audit(
        table_name="map_settings",
        row_id=settings.id,
        action="update_map_settings",
        changed_by=admin["email"]
    )
    session.add(audit)
    await session.commit()
    
    return {"status": "success"}


@app.get("/admin/settings/map", response_class=HTMLResponse)
async def admin_map_settings_page(
    request: Request,
    admin=Depends(get_current_admin)
):
    """Admin page for map visualization settings"""
    return templates.TemplateResponse("admin_map_settings.html", {
        "request": request,
        "admin": admin
    })


@app.get("/admin/doctors", response_class=HTMLResponse)
async def admin_doctors_page(
    request: Request,
    admin=Depends(get_current_admin),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(Doctor))
    doctors = result.scalars().all()
    
    return templates.TemplateResponse("doctors_admin.html", {
        "request": request,
        "doctors": doctors,
        "admin": admin
    })


@app.post("/admin/doctors/new")
async def create_doctor(
    full_name: str = Form(...),
    specialty: str = Form(...),
    city: str = Form(...),
    hospital: str = Form(...),
    phone: str = Form(...),
    languages: str = Form(""),
    referral_reason: str = Form(""),
    referred_by: str = Form(""),
    rank: int = Form(0),
    verified: bool = Form(False),
    admin=Depends(get_current_admin),
    session: AsyncSession = Depends(get_session)
):
    doctor = Doctor(
        full_name=full_name,
        specialty=specialty,
        city=city,
        hospital=hospital,
        phone=phone,
        languages=languages,
        referral_reason=referral_reason,
        referred_by=referred_by,
        rank=rank,
        verified=verified
    )
    session.add(doctor)
    await session.commit()
    
    audit = Audit(
        table_name="doctors",
        row_id=doctor.id,
        action="create",
        changed_by=admin["email"]
    )
    session.add(audit)
    await session.commit()
    
    return RedirectResponse(url="/admin/doctors", status_code=303)


@app.post("/admin/bulk/villages")
async def bulk_upload_villages(
    file: UploadFile = File(...),
    admin=Depends(get_current_admin),
    session: AsyncSession = Depends(get_session)
):
    content = await file.read()
    csv_file = io.StringIO(content.decode('utf-8'))
    reader = csv.DictReader(csv_file)
    
    inserted = 0
    errors = []
    
    for row in reader:
        try:
            result = await session.execute(
                select(Village).where(Village.name == row['name'], Village.block == row['block'])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                existing.lat = float(row['lat'])
                existing.lng = float(row['lng'])
                existing.south = float(row['south'])
                existing.west = float(row['west'])
                existing.north = float(row['north'])
                existing.east = float(row['east'])
                existing.code_2011 = row.get('code_2011', '')
            else:
                village = Village(
                    name=row['name'],
                    block=row['block'],
                    lat=float(row['lat']),
                    lng=float(row['lng']),
                    south=float(row['south']),
                    west=float(row['west']),
                    north=float(row['north']),
                    east=float(row['east']),
                    code_2011=row.get('code_2011', '')
                )
                session.add(village)
            
            inserted += 1
        except Exception as e:
            errors.append(f"Row {row.get('name', '?')}: {str(e)}")
    
    await session.commit()
    
    return {"inserted": inserted, "errors": errors}


@app.post("/admin/bulk/members")
async def bulk_upload_members(
    file: UploadFile = File(...),
    verify_on_import: bool = Form(False),
    admin=Depends(get_current_admin),
    session: AsyncSession = Depends(get_session)
):
    content = await file.read()
    csv_file = io.StringIO(content.decode('utf-8'))
    reader = csv.DictReader(csv_file)
    
    inserted = 0
    errors = []
    
    for row in reader:
        try:
            result = await session.execute(
                select(Village).where(Village.name == row['village'])
            )
            village = result.scalar_one_or_none()
            
            if not village:
                errors.append(f"{row['full_name']}: Village '{row['village']}' not found")
                continue
            
            member = Member(
                full_name=row['full_name'],
                role=row['role'],
                phone=row['phone'],
                languages=row.get('languages', ''),
                village_id=village.id,
                verified=verify_on_import
            )
            session.add(member)
            inserted += 1
        except Exception as e:
            errors.append(f"{row.get('full_name', '?')}: {str(e)}")
    
    await session.commit()
    
    return {"inserted": inserted, "errors": errors}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Block Coordinator registration page"""
    user = get_optional_user(request)
    return templates.TemplateResponse("register.html", {"request": request, "user": user})


@app.post("/api/auth/register")
async def register_user(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    primary_block: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    """Register a new Block Coordinator (pending approval)"""
    from auth import hash_password
    
    result = await session.execute(
        select(User).where(User.email == email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    password_hash = hash_password(password)
    
    new_user = User(
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        phone=phone,
        role="block_coordinator",
        primary_block=primary_block,
        is_active=False
    )
    
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    return {
        "success": True,
        "message": "Registration successful! Your account is pending admin approval.",
        "user_id": new_user.id
    }


@app.post("/api/auth/login")
async def login_user(
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    """Login with role detection and redirect"""
    from auth import verify_password, hash_password
    
    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        token = create_session_token(email, "super_admin")
        response = JSONResponse({
            "success": True,
            "role": "super_admin",
            "redirect": "/admin"
        })
        response.set_cookie(
            "session",
            token,
            httponly=True,
            max_age=86400 * 7,
            samesite="lax"
        )
        return response
    
    result = await session.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Your account is pending admin approval. Please contact the administrator."
        )
    
    user.last_login = datetime.utcnow()
    user.login_count += 1
    await session.commit()
    
    token = create_session_token(user.email, user.role)
    
    redirect_url = "/admin" if user.role == "super_admin" else "/dashboard"
    
    response = JSONResponse({
        "success": True,
        "role": user.role,
        "redirect": redirect_url,
        "blocks": user.assigned_blocks or user.primary_block
    })
    response.set_cookie(
        "session",
        token,
        httponly=True,
        max_age=86400 * 7,
        samesite="lax"
    )
    
    return response


@app.get("/dashboard", response_class=HTMLResponse)
async def coordinator_dashboard(
    request: Request,
    user_data: dict = Depends(get_current_user)
):
    """Block Coordinator Dashboard"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user_data
    })


@app.get("/api/admin/pending-users")
async def get_pending_users(
    user_data: dict = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session)
):
    """Get all pending user registrations (admin only)"""
    result = await session.execute(
        select(User)
        .where(User.is_active == False)
        .where(User.role == "block_coordinator")
        .order_by(User.created_at.desc())
    )
    pending_users = result.scalars().all()
    
    return [{
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "primary_block": user.primary_block,
        "created_at": user.created_at.isoformat()
    } for user in pending_users]


@app.post("/api/admin/approve-user/{user_id}")
async def approve_user(
    user_id: int,
    assigned_blocks: str = Form(""),
    admin_data: dict = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session)
):
    """Approve a pending user registration (admin only)"""
    try:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": "User not found"}
            )
        
        user.is_active = True
        user.approved_by = admin_data.get("email")
        user.approved_at = datetime.utcnow()
        user.assigned_blocks = assigned_blocks if assigned_blocks else user.primary_block
        
        await session.commit()
        
        return {"success": True, "message": f"✅ User {user.full_name} ({user.email}) approved successfully!"}
    
    except Exception as e:
        await session.rollback()
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Failed to approve user: {str(e)}"}
        )


@app.post("/api/admin/reject-user/{user_id}")
async def reject_user(
    user_id: int,
    rejection_reason: str = Form(...),
    admin_data: dict = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session)
):
    """Reject a pending user registration (admin only)"""
    try:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": "User not found"}
            )
        
        user.rejection_reason = rejection_reason
        
        await session.delete(user)
        await session.commit()
        
        return {"success": True, "message": f"❌ User registration for {user.full_name} rejected"}
    
    except Exception as e:
        await session.rollback()
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Failed to reject user: {str(e)}"}
        )


@app.get("/field-workers/new", response_class=HTMLResponse)
async def field_worker_new_page(
    request: Request,
    user_data: dict = Depends(require_block_coordinator),
    session: AsyncSession = Depends(get_session)
):
    """Field Worker submission form"""
    user_profile = None
    coordinator_blocks: list[str] = []

    if user_data:
        result = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        user_profile = result.scalar_one_or_none()

        if user_profile:
            if getattr(user_profile, "primary_block", None):
                coordinator_blocks.append(user_profile.primary_block.strip())
            if getattr(user_profile, "assigned_blocks", None):
                coordinator_blocks.extend([
                    blk.strip()
                    for blk in user_profile.assigned_blocks.split(",")
                    if blk.strip()
                ])

    unique_blocks = sorted({blk for blk in coordinator_blocks if blk})
    default_block = ""

    if unique_blocks:
        default_block = unique_blocks[0]
    elif user_profile and getattr(user_profile, "primary_block", None):
        default_block = user_profile.primary_block.strip()

    return templates.TemplateResponse("field_worker_new.html", {
        "request": request,
        "user": user_data,
        "user_profile": user_profile,
        "user_blocks": unique_blocks,
        "default_block": default_block
    })


@app.get("/api/form-fields")
async def get_form_fields(
    user_data: dict = Depends(require_block_coordinator),
    session: AsyncSession = Depends(get_session)
):
    """Get form field configuration for Field Worker form"""
    result = await session.execute(
        select(FormFieldConfig)
        .where(FormFieldConfig.is_visible == True)
        .order_by(FormFieldConfig.display_order)
    )
    fields = result.scalars().all()
    
    return [{
        "field_name": f.field_name,
        "field_label": f.field_label,
        "field_type": f.field_type,
        "is_required": f.is_required,
        "placeholder": f.placeholder,
        "help_text": f.help_text,
        "options": f.options
    } for f in fields]


@app.get("/api/villages")
async def get_villages_list(
    session: AsyncSession = Depends(get_session)
):
    """Get all villages for autocomplete (lightweight version)"""
    result = await session.execute(
        select(
            Village.id,
            Village.name.label("village_name"),
            Village.block.label("block_name"),
            Village.population
        ).order_by(Village.name)
    )
    villages = result.all()
    
    return {
        "villages": [{
            "id": v.id,
            "village_name": v.village_name,
            "block_name": v.block_name,
            "population": v.population
        } for v in villages]
    }


@app.post("/api/field-workers")
async def submit_field_worker(
    request: Request,
    user_data: dict = Depends(require_block_coordinator),
    session: AsyncSession = Depends(get_session)
):
    """Submit a new Field Worker entry"""
    from auth import check_block_access
    
    data = await request.json()

    village_name = (data.get('village_name') or "").strip()
    if not village_name:
        raise HTTPException(status_code=400, detail="Village name is required")

    village_id_raw = (data.get('village_id') or "").strip()
    incoming_block = (data.get('village_block') or "").strip()

    user_result = await session.execute(
        select(User).where(User.email == user_data.get('email'))
    )
    user = user_result.scalar_one_or_none()

    def resolve_user_block(user_obj: User | None, payload: dict) -> str:
        if user_obj:
            block_hints: list[str] = []
            if getattr(user_obj, "primary_block", None):
                block_hints.append(user_obj.primary_block.strip())
            if getattr(user_obj, "assigned_blocks", None):
                block_hints.extend([
                    blk.strip()
                    for blk in user_obj.assigned_blocks.split(",")
                    if blk.strip()
                ])
            for hint in block_hints:
                if hint:
                    return hint
        session_blocks = (payload.get("blocks") or "").split(",")
        for blk in session_blocks:
            blk = blk.strip()
            if blk:
                return blk
        return ""

    block_name = incoming_block or resolve_user_block(user, user_data)

    village: Village | None = None
    if village_id_raw:
        try:
            village_id = int(village_id_raw)
        except ValueError:
            village_id = None

        if village_id is not None:
            village_result = await session.execute(
                select(Village).where(Village.id == village_id)
            )
            village = village_result.scalar_one_or_none()
            if village:
                block_name = village.block

    if not village:
        if not block_name:
            raise HTTPException(
                status_code=400,
                detail="Block selection is required for village submissions"
            )

        existing_village = await session.execute(
            select(Village)
            .where(func.lower(Village.name) == village_name.lower())
            .where(func.lower(Village.block) == block_name.lower())
        )
        village = existing_village.scalar_one_or_none()

        if not village:
            block_lookup = await session.execute(
                select(Village).where(func.lower(Village.block) == block_name.lower())
            )
            block_villages = block_lookup.scalars().all()

            if block_villages:
                lat = sum(v.lat for v in block_villages) / len(block_villages)
                lng = sum(v.lng for v in block_villages) / len(block_villages)
                south = min(v.south for v in block_villages)
                west = min(v.west for v in block_villages)
                north = max(v.north for v in block_villages)
                east = max(v.east for v in block_villages)
            else:
                static_bounds = await get_block_bounds_from_static(block_name)
                if static_bounds:
                    lat = static_bounds['lat']
                    lng = static_bounds['lng']
                    south = static_bounds['south']
                    west = static_bounds['west']
                    north = static_bounds['north']
                    east = static_bounds['east']
                else:
                    # Fallback to Bhadrak centroid if no data at all
                    lat = 21.054
                    lng = 86.52
                    south = lat - 0.02
                    west = lng - 0.02
                    north = lat + 0.02
                    east = lng + 0.02

            village = Village(
                name=village_name,
                block=block_name,
                lat=lat,
                lng=lng,
                south=south,
                west=west,
                north=north,
                east=east,
                population=0,
                show_pin=False,
                pin_description="Pending geo-verification",
                pin_notes="Auto-created from Field Worker submission"
            )
            session.add(village)
            await session.flush()

            session.add(VillagePin(
                village_id=village.id,
                field_worker_count=0,
                uk_center_count=0,
                is_active=False
            ))


    static_bounds = await get_block_bounds_from_static(block_name)
    if static_bounds and abs(village.lat - 21.054) < 0.0005 and abs(village.lng - 86.52) < 0.0005:
        village.lat = static_bounds['lat']
        village.lng = static_bounds['lng']
        village.south = static_bounds['south']
        village.west = static_bounds['west']
        village.north = static_bounds['north']
        village.east = static_bounds['east']
        session.add(village)

    village_id = village.id

    try:
        check_block_access(user_data, village.block, user)
    except HTTPException:
        raise HTTPException(
            status_code=403,
            detail=f"You do not have access to submit Field Workers for {village.block} block"
        )
    
    # Check for duplicate phone number (unless exception provided)
    if not data.get('duplicate_exception_reason'):
        duplicate_check = await session.execute(
            select(FieldWorker)
            .where(FieldWorker.phone == data['phone'])
            .where(FieldWorker.is_active == True)
        )
        existing = duplicate_check.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Phone number {data['phone']} already exists in the system. If this is a valid duplicate, please provide a reason."
            )
    
    # Create Field Worker entry
    field_worker = FieldWorker(
        full_name=data['full_name'],
        phone=data['phone'],
        alternate_phone=data.get('alternate_phone'),
        email=data.get('email'),
        village_id=village_id,
        address_line=data.get('address_line'),
        landmark=data.get('landmark'),
        designation=data['designation'],
        department=data.get('department'),
        employee_id=data.get('employee_id'),
        preferred_contact_method=data.get('preferred_contact_method', 'phone'),
        available_days=data.get('available_days'),
        available_hours=data.get('available_hours'),
        status='pending',
        submitted_by_user_id=user.id,
        duplicate_exception_reason=data.get('duplicate_exception_reason'),
        duplicate_of_phone=data.get('duplicate_of_phone')
    )
    
    session.add(field_worker)
    await session.commit()
    await session.refresh(field_worker)
    
    return {
        "success": True,
        "message": "Field Worker submitted successfully. Pending admin approval.",
        "id": field_worker.id
    }


@app.get("/field-workers/my-submissions", response_class=HTMLResponse)
async def my_submissions_page(
    request: Request,
    user_data: dict = Depends(require_block_coordinator)
):
    """My submissions page"""
    return templates.TemplateResponse("field_worker_submissions.html", {
        "request": request,
        "user": user_data
    })


@app.get("/api/field-workers/my-submissions")
async def get_my_submissions(
    user_data: dict = Depends(require_block_coordinator),
    session: AsyncSession = Depends(get_session)
):
    """Get all submissions by current user"""
    # Get user ID
    user_result = await session.execute(
        select(User).where(User.email == user_data.get('email'))
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get submissions with village info
    result = await session.execute(
        select(FieldWorker, Village.name.label('village_name'), Village.block.label('block_name'))
        .join(Village, FieldWorker.village_id == Village.id)
        .where(FieldWorker.submitted_by_user_id == user.id)
        .order_by(FieldWorker.created_at.desc())
    )
    
    submissions = []
    for fw, village_name, block_name in result.all():
        submissions.append({
            "id": fw.id,
            "full_name": fw.full_name,
            "phone": fw.phone,
            "alternate_phone": fw.alternate_phone,
            "email": fw.email,
            "village_id": fw.village_id,
            "village_name": village_name,
            "block_name": block_name,
            "designation": fw.designation,
            "department": fw.department,
            "employee_id": fw.employee_id,
            "status": fw.status,
            "created_at": fw.created_at.isoformat(),
            "approved_at": fw.approved_at.isoformat() if fw.approved_at else None,
            "approved_by": fw.approved_by,
            "rejection_reason": fw.rejection_reason
        })
    
    return submissions


@app.delete("/api/field-workers/{field_worker_id}")
async def delete_field_worker(
    field_worker_id: int,
    user_data: dict = Depends(require_block_coordinator),
    session: AsyncSession = Depends(get_session)
):
    """Delete a pending Field Worker submission"""
    # Get user
    user_result = await session.execute(
        select(User).where(User.email == user_data.get('email'))
    )
    user = user_result.scalar_one_or_none()
    
    # Get field worker
    fw_result = await session.execute(
        select(FieldWorker).where(FieldWorker.id == field_worker_id)
    )
    fw = fw_result.scalar_one_or_none()
    
    if not fw:
        raise HTTPException(status_code=404, detail="Field Worker not found")
    
    # Check ownership
    if fw.submitted_by_user_id != user.id and user_data.get('role') != 'super_admin':
        raise HTTPException(status_code=403, detail="You can only delete your own submissions")
    
    # Can only delete pending submissions
    if fw.status != 'pending':
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete {fw.status} submissions. Only pending submissions can be deleted."
        )
    
    await session.delete(fw)
    await session.commit()
    
    return {"success": True, "message": "Submission deleted successfully"}


@app.get("/admin/field-workers", response_class=HTMLResponse)
async def admin_field_workers_page(
    request: Request,
    admin_data: dict = Depends(require_super_admin)
):
    """Admin Field Worker approval interface"""
    return templates.TemplateResponse("admin_field_workers.html", {
        "request": request,
        "admin": admin_data
    })


@app.get("/api/admin/field-workers")
async def get_all_field_workers(
    admin_data: dict = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session)
):
    """Get all Field Worker submissions (admin only)"""
    result = await session.execute(
        select(
            FieldWorker,
            Village.name.label('village_name'),
            Village.block.label('block_name'),
            User.full_name.label('submitted_by_name')
        )
        .join(Village, FieldWorker.village_id == Village.id)
        .join(User, FieldWorker.submitted_by_user_id == User.id)
        .order_by(FieldWorker.created_at.desc())
    )
    
    field_workers = []
    for fw, village_name, block_name, submitted_by_name in result.all():
        field_workers.append({
            "id": fw.id,
            "full_name": fw.full_name,
            "phone": fw.phone,
            "alternate_phone": fw.alternate_phone,
            "email": fw.email,
            "village_id": fw.village_id,
            "village_name": village_name,
            "block_name": block_name,
            "designation": fw.designation,
            "department": fw.department,
            "employee_id": fw.employee_id,
            "status": fw.status,
            "submitted_by_name": submitted_by_name,
            "duplicate_exception_reason": fw.duplicate_exception_reason,
            "created_at": fw.created_at.isoformat(),
            "approved_at": fw.approved_at.isoformat() if fw.approved_at else None,
            "approved_by": fw.approved_by,
            "rejection_reason": fw.rejection_reason
        })
    
    return field_workers


@app.post("/api/admin/field-workers/{field_worker_id}/approve")
async def approve_field_worker(
    field_worker_id: int,
    admin_data: dict = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session)
):
    """Approve a Field Worker submission (admin only)"""
    result = await session.execute(
        select(FieldWorker).where(FieldWorker.id == field_worker_id)
    )
    fw = result.scalar_one_or_none()
    
    if not fw:
        raise HTTPException(status_code=404, detail="Field Worker not found")
    
    if fw.status != 'pending':
        raise HTTPException(
            status_code=400,
            detail=f"Cannot approve {fw.status} submission. Only pending submissions can be approved."
        )
    
    fw.status = 'approved'
    fw.approved_by = admin_data.get('email')
    fw.approved_at = datetime.utcnow()
    
    await session.commit()
    
    return {"success": True, "message": "Field Worker approved successfully"}


@app.post("/api/admin/field-workers/{field_worker_id}/reject")
async def reject_field_worker(
    field_worker_id: int,
    rejection_reason: str = Form(...),
    admin_data: dict = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session)
):
    """Reject a Field Worker submission (admin only)"""
    result = await session.execute(
        select(FieldWorker).where(FieldWorker.id == field_worker_id)
    )
    fw = result.scalar_one_or_none()
    
    if not fw:
        raise HTTPException(status_code=404, detail="Field Worker not found")
    
    if fw.status != 'pending':
        raise HTTPException(
            status_code=400,
            detail=f"Cannot reject {fw.status} submission. Only pending submissions can be rejected."
        )
    
    fw.status = 'rejected'
    fw.rejection_reason = rejection_reason
    fw.approved_by = admin_data.get('email')
    fw.approved_at = datetime.utcnow()
    
    await session.commit()
    
    return {"success": True, "message": "Field Worker rejected"}


# ============================================================
# PHASE 3: ADMIN USER MANAGEMENT
# ============================================================

@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users_page(
    request: Request,
    admin_data: dict = Depends(require_super_admin)
):
    """Admin user management interface"""
    return templates.TemplateResponse("admin_users.html", {
        "request": request,
        "admin": admin_data
    })


@app.get("/api/admin/users")
async def get_all_users(
    admin_data: dict = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session)
):
    """Get all users with submission counts"""
    # Get all users
    users_result = await session.execute(select(User).order_by(User.created_at.desc()))
    users = users_result.scalars().all()
    
    # Get submission counts for each user
    user_list = []
    for user in users:
        # Count submissions
        count_result = await session.execute(
            select(FieldWorker).where(FieldWorker.submitted_by_user_id == user.id)
        )
        submission_count = len(count_result.scalars().all())
        
        user_list.append({
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "role": user.role,
            "primary_block": user.primary_block,
            "assigned_blocks": user.assigned_blocks,
            "is_active": user.is_active,
            "approved_by": user.approved_by,
            "approved_at": user.approved_at.isoformat() if user.approved_at else None,
            "rejection_reason": user.rejection_reason,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "login_count": user.login_count,
            "submission_count": submission_count
        })
    
    return user_list


@app.put("/api/admin/users/{user_id}/blocks")
async def update_user_blocks(
    user_id: int,
    assigned_blocks: str = Form(...),
    admin_data: dict = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session)
):
    """Update user's assigned blocks"""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.assigned_blocks = assigned_blocks
    user.profile_updated_at = datetime.utcnow()
    
    await session.commit()
    
    return {"success": True, "message": "Blocks updated successfully"}


@app.post("/api/admin/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    admin_data: dict = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session)
):
    """Deactivate a user"""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    user.profile_updated_at = datetime.utcnow()
    
    await session.commit()
    
    return {"success": True, "message": "User deactivated successfully"}


@app.post("/api/admin/users/{user_id}/reactivate")
async def reactivate_user(
    user_id: int,
    admin_data: dict = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session)
):
    """Reactivate a user"""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = True
    user.rejection_reason = None
    user.profile_updated_at = datetime.utcnow()
    
    await session.commit()
    
    return {"success": True, "message": "User reactivated successfully"}


@app.post("/api/admin/users")
async def create_admin_user(
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    primary_block: str = Form(""),
    assigned_blocks: str = Form(""),
    admin_data: dict = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session)
):
    """Create new admin user (super admin only)"""
    # Validate role
    if role not in ["super_admin", "block_coordinator"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be super_admin or block_coordinator")
    
    # Validate block for coordinators
    if role == "block_coordinator" and not primary_block:
        raise HTTPException(status_code=400, detail="Block coordinators must have a primary block assigned")
    
    # Check if email already exists
    result = await session.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Validate password strength
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    # Create new admin user
    new_user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        phone="",  # Optional, can be updated later
        role=role,
        primary_block=primary_block or "",
        assigned_blocks=assigned_blocks,
        is_active=True,  # Auto-activate admin-created users
        approved_by=admin_data.get('email'),
        approved_at=datetime.utcnow(),
        oauth_provider="email"
    )
    
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    return {
        "success": True,
        "message": "Admin user created successfully",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role,
            "primary_block": new_user.primary_block,
            "is_active": new_user.is_active
        }
    }


@app.put("/api/admin/users/{user_id}/role")
async def change_user_role(
    user_id: int,
    new_role: str = Form(...),
    primary_block: str = Form(""),
    assigned_blocks: str = Form(""),
    admin_data: dict = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session)
):
    """Change user role (super admin only)"""
    # Validate new role
    if new_role not in ["super_admin", "block_coordinator"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # Get target user
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if this is the last super admin being demoted
    if user.role == "super_admin" and new_role != "super_admin":
        # Count active super admins
        count_result = await session.execute(
            select(func.count(User.id)).where(
                User.role == "super_admin",
                User.is_active == True
            )
        )
        super_admin_count = count_result.scalar()
        
        if super_admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot change role. At least one active super admin must remain."
            )
    
    # Update user role
    user.role = new_role
    user.primary_block = primary_block if new_role == "block_coordinator" else ""
    user.assigned_blocks = assigned_blocks if new_role == "block_coordinator" else ""
    user.profile_updated_at = datetime.utcnow()
    
    await session.commit()
    
    return {
        "success": True,
        "message": f"Role changed to {new_role} successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "primary_block": user.primary_block,
            "assigned_blocks": user.assigned_blocks
        }
    }


@app.delete("/api/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    admin_data: dict = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session)
):
    """Delete user (super admin only) - Use with caution"""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent deleting last super admin
    if user.role == "super_admin":
        count_result = await session.execute(
            select(func.count(User.id)).where(User.role == "super_admin")
        )
        super_admin_count = count_result.scalar()
        
        if super_admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete last super admin"
            )
    
    await session.delete(user)
    await session.commit()
    
    return {"success": True, "message": "User deleted successfully"}


# ============================================================
# PHASE 4: DATA EXPORT SYSTEM
# ============================================================

@app.get("/api/export/field-workers")
async def export_field_workers(
    user_data: dict = Depends(require_block_coordinator),
    session: AsyncSession = Depends(get_session)
):
    """Export Field Workers to CSV"""
    from fastapi.responses import StreamingResponse
    import csv
    from io import StringIO
    
    # Get user
    user_result = await session.execute(select(User).where(User.email == user_data.get('email')))
    user = user_result.scalar_one_or_none()
    
    # Query based on role
    if user.role == 'super_admin':
        # Admin: All Field Workers
        result = await session.execute(
            select(FieldWorker, Village.name.label('village_name'), Village.block.label('block_name'), User.full_name.label('submitted_by'))
            .join(Village, FieldWorker.village_id == Village.id)
            .join(User, FieldWorker.submitted_by_user_id == User.id)
            .order_by(FieldWorker.created_at.desc())
        )
    else:
        # Coordinator: Own submissions only
        result = await session.execute(
            select(FieldWorker, Village.name.label('village_name'), Village.block.label('block_name'))
            .join(Village, FieldWorker.village_id == Village.id)
            .where(FieldWorker.submitted_by_user_id == user.id)
            .order_by(FieldWorker.created_at.desc())
        )
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    if user.role == 'super_admin':
        writer.writerow([
            'ID', 'Full Name', 'Phone', 'Alternate Phone', 'Email',
            'Village', 'Block', 'Designation', 'Department', 'Employee ID',
            'Status', 'Submitted By', 'Submitted Date', 'Approved By', 'Approved Date'
        ])
        
        for fw, village_name, block_name, submitted_by in result.all():
            writer.writerow([
                fw.id, fw.full_name, fw.phone, fw.alternate_phone or '', fw.email or '',
                village_name, block_name, fw.designation, fw.department or '', fw.employee_id or '',
                fw.status, submitted_by, fw.created_at.strftime('%Y-%m-%d'),
                fw.approved_by or '', fw.approved_at.strftime('%Y-%m-%d') if fw.approved_at else ''
            ])
    else:
        writer.writerow([
            'ID', 'Full Name', 'Phone', 'Alternate Phone', 'Email',
            'Village', 'Block', 'Designation', 'Department', 'Employee ID',
            'Status', 'Submitted Date', 'Approved Date'
        ])
        
        for fw, village_name, block_name in result.all():
            writer.writerow([
                fw.id, fw.full_name, fw.phone, fw.alternate_phone or '', fw.email or '',
                village_name, block_name, fw.designation, fw.department or '', fw.employee_id or '',
                fw.status, fw.created_at.strftime('%Y-%m-%d'),
                fw.approved_at.strftime('%Y-%m-%d') if fw.approved_at else ''
            ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=field_workers_export.csv"}
    )


@app.get("/api/export/users")
async def export_users(
    admin_data: dict = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session)
):
    """Export users to CSV (admin only)"""
    from fastapi.responses import StreamingResponse
    import csv
    from io import StringIO
    
    result = await session.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'ID', 'Full Name', 'Email', 'Phone', 'Role', 'Primary Block',
        'Assigned Blocks', 'Status', 'Registered Date', 'Last Login', 'Login Count'
    ])
    
    for user in users:
        status = 'Active' if user.is_active else ('Rejected' if user.rejection_reason else 'Pending')
        writer.writerow([
            user.id, user.full_name, user.email, user.phone, user.role,
            user.primary_block, user.assigned_blocks or '',
            status, user.created_at.strftime('%Y-%m-%d'),
            user.last_login.strftime('%Y-%m-%d') if user.last_login else 'Never',
            user.login_count
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users_export.csv"}
    )


# ============================================================
# PHASE 3/4: COORDINATOR DASHBOARD STATISTICS
# ============================================================

@app.get("/api/dashboard/statistics")
async def get_dashboard_statistics(
    user_data: dict = Depends(require_block_coordinator),
    session: AsyncSession = Depends(get_session)
):
    """Get coordinator dashboard statistics"""
    # Get user
    user_result = await session.execute(select(User).where(User.email == user_data.get('email')))
    user = user_result.scalar_one_or_none()
    
    # Get all submissions
    fw_result = await session.execute(
        select(FieldWorker).where(FieldWorker.submitted_by_user_id == user.id)
    )
    field_workers = fw_result.scalars().all()
    
    total = len(field_workers)
    pending = len([fw for fw in field_workers if fw.status == 'pending'])
    approved = len([fw for fw in field_workers if fw.status == 'approved'])
    rejected = len([fw for fw in field_workers if fw.status == 'rejected'])
    
    # Recent submissions (last 5)
    recent_result = await session.execute(
        select(FieldWorker, Village.name.label('village_name'), Village.block.label('block_name'))
        .join(Village, FieldWorker.village_id == Village.id)
        .where(FieldWorker.submitted_by_user_id == user.id)
        .order_by(FieldWorker.created_at.desc())
        .limit(5)
    )
    
    recent_submissions = []
    for fw, village_name, block_name in recent_result.all():
        recent_submissions.append({
            "id": fw.id,
            "full_name": fw.full_name,
            "village_name": village_name,
            "block_name": block_name,
            "status": fw.status,
            "created_at": fw.created_at.isoformat()
        })
    
    return {
        "total_submissions": total,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "recent_submissions": recent_submissions
    }


# Update dashboard route to use enhanced version
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    user_data: dict = Depends(require_block_coordinator)
):
    """Enhanced coordinator dashboard with statistics"""
    return templates.TemplateResponse("dashboard_enhanced.html", {
        "request": request,
        "user": user_data
    })


# ============================================================
# PHASE 4: ANALYTICS DASHBOARD
# ============================================================

@app.get("/admin/analytics", response_class=HTMLResponse)
async def admin_analytics_page(
    request: Request,
    admin_data: dict = Depends(require_super_admin)
):
    """Admin analytics dashboard"""
    return templates.TemplateResponse("admin_analytics.html", {
        "request": request,
        "admin": admin_data
    })


@app.get("/api/analytics/overview")
async def get_analytics_overview(
    admin_data: dict = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session)
):
    """Get comprehensive analytics data"""
    from collections import defaultdict
    
    # Users statistics
    users_result = await session.execute(select(User))
    users = users_result.scalars().all()
    total_users = len(users)
    active_users = len([u for u in users if u.is_active])
    
    # Field Workers statistics
    fw_result = await session.execute(select(FieldWorker))
    field_workers = fw_result.scalars().all()
    total_field_workers = len(field_workers)
    approved_field_workers = len([fw for fw in field_workers if fw.status == 'approved'])
    pending_reviews = len([fw for fw in field_workers if fw.status == 'pending'])
    
    # Village coverage
    villages_result = await session.execute(select(Village))
    all_villages = villages_result.scalars().all()
    villages_with_fw = set(fw.village_id for fw in field_workers if fw.status == 'approved')
    villages_covered = len(villages_with_fw)
    coverage_percent = round((villages_covered / 1315) * 100, 1) if villages_covered > 0 else 0
    
    # By Block
    by_block = defaultdict(int)
    for fw in field_workers:
        for village in all_villages:
            if village.id == fw.village_id:
                by_block[village.block_name] += 1
                break
    
    # By Status
    by_status = {
        "approved": len([fw for fw in field_workers if fw.status == 'approved']),
        "pending": len([fw for fw in field_workers if fw.status == 'pending']),
        "rejected": len([fw for fw in field_workers if fw.status == 'rejected'])
    }
    
    # Timeline (last 30 days)
    from datetime import timedelta
    timeline = defaultdict(int)
    today = datetime.utcnow().date()
    for i in range(30):
        date = today - timedelta(days=29-i)
        timeline[date.strftime('%Y-%m-%d')] = 0
    
    for fw in field_workers:
        date_str = fw.created_at.date().strftime('%Y-%m-%d')
        if date_str in timeline:
            timeline[date_str] += 1
    
    # Top Contributors
    contributor_counts = defaultdict(int)
    contributor_data = {}
    for fw in field_workers:
        contributor_counts[fw.submitted_by_user_id] += 1
    
    for user in users:
        if user.id in contributor_counts:
            contributor_data[user.id] = {
                "name": user.full_name,
                "email": user.email,
                "count": contributor_counts[user.id]
            }
    
    top_contributors = sorted(contributor_data.values(), key=lambda x: x['count'], reverse=True)[:10]
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_field_workers": total_field_workers,
        "approved_field_workers": approved_field_workers,
        "pending_reviews": pending_reviews,
        "villages_covered": villages_covered,
        "coverage_percent": coverage_percent,
        "by_block": [{"block": k, "count": v} for k, v in sorted(by_block.items())],
        "by_status": by_status,
        "timeline": [{"date": k, "count": v} for k, v in sorted(timeline.items())],
        "top_contributors": top_contributors
    }


# ============================================================
# PHASE 2: ADMIN FORM FIELD CONFIGURATION
# ============================================================

@app.get("/admin/form-config", response_class=HTMLResponse)
async def admin_form_config_page(
    request: Request,
    admin_data: dict = Depends(require_super_admin)
):
    """Admin form field configuration interface"""
    return templates.TemplateResponse("admin_form_config.html", {
        "request": request,
        "admin": admin_data
    })


@app.get("/api/admin/form-config")
async def get_form_config(
    admin_data: dict = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session)
):
    """Get all form field configurations"""
    result = await session.execute(
        select(FormFieldConfig).order_by(FormFieldConfig.display_order)
    )
    configs = result.scalars().all()
    
    return [{
        "id": c.id,
        "field_name": c.field_name,
        "field_label": c.field_label,
        "field_type": c.field_type,
        "is_required": c.is_required,
        "is_visible": c.is_visible,
        "display_order": c.display_order,
        "placeholder": c.placeholder
    } for c in configs]


@app.put("/api/admin/form-config")
async def update_form_config(
    request: Request,
    admin_data: dict = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session)
):
    """Update all form field configurations"""
    data = await request.json()
    
    for field_data in data:
        result = await session.execute(
            select(FormFieldConfig).where(FormFieldConfig.id == field_data['id'])
        )
        config = result.scalar_one_or_none()
        
        if config:
            config.is_required = field_data['is_required']
            config.is_visible = field_data['is_visible']
            config.display_order = field_data['display_order']
            config.updated_at = datetime.utcnow()
    
    await session.commit()
    
    return {"success": True, "message": "Form configuration updated successfully"}


# ============================================================
# PHASE 2: DUPLICATE EXCEPTIONS REVIEW
# ============================================================

@app.get("/admin/duplicates", response_class=HTMLResponse)
async def admin_duplicates_page(
    request: Request,
    admin_data: dict = Depends(require_super_admin)
):
    """Admin duplicate exceptions review interface"""
    return templates.TemplateResponse("admin_duplicates.html", {
        "request": request,
        "admin": admin_data
    })


@app.get("/api/admin/duplicates")
async def get_duplicate_exceptions(
    admin_data: dict = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session)
):
    """Get all Field Workers with duplicate exception reasons"""
    # Get all Field Workers with duplicate exceptions
    result = await session.execute(
        select(FieldWorker, Village, User.full_name.label('submitted_by_name'))
        .join(Village, FieldWorker.village_id == Village.id)
        .join(User, FieldWorker.submitted_by_user_id == User.id)
        .where(FieldWorker.duplicate_exception_reason.isnot(None))
        .order_by(FieldWorker.created_at.desc())
    )
    
    duplicates = []
    for fw, village, submitted_by_name in result.all():
        # Get the existing entry if duplicate_of_phone is set
        existing_entry = None
        if fw.duplicate_of_phone:
            existing_result = await session.execute(
                select(FieldWorker, Village)
                .join(Village, FieldWorker.village_id == Village.id)
                .where(FieldWorker.phone == fw.duplicate_of_phone)
                .where(FieldWorker.id != fw.id)
                .where(FieldWorker.status == 'approved')
                .limit(1)
            )
            existing_row = existing_result.first()
            if existing_row:
                existing_fw, existing_village = existing_row
                existing_entry = {
                    "id": existing_fw.id,
                    "full_name": existing_fw.full_name,
                    "phone": existing_fw.phone,
                    "village_name": existing_village.village_name,
                    "block_name": existing_village.block_name,
                    "designation": existing_fw.designation,
                    "department": existing_fw.department,
                    "status": existing_fw.status
                }
        
        duplicates.append({
            "id": fw.id,
            "full_name": fw.full_name,
            "phone": fw.phone,
            "alternate_phone": fw.alternate_phone,
            "email": fw.email,
            "village_name": village.village_name,
            "block_name": village.block_name,
            "designation": fw.designation,
            "department": fw.department,
            "status": fw.status,
            "duplicate_exception_reason": fw.duplicate_exception_reason,
            "duplicate_of_phone": fw.duplicate_of_phone,
            "existing_entry": existing_entry,
            "submitted_by_name": submitted_by_name,
            "created_at": fw.created_at.isoformat()
        })
    
    return duplicates


# ============================================================
# PHASE 3: USER PROFILE PAGE
# ============================================================

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    user_data: dict = Depends(get_current_user)
):
    """User profile page"""
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user_data['user']
    })


@app.put("/api/profile/update")
async def update_profile(
    request: Request,
    user_data: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Update user profile information"""
    data = await request.json()
    
    result = await session.execute(
        select(User).where(User.id == user_data['user'].id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update allowed fields
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'phone' in data:
        user.phone = data['phone']
    
    user.profile_updated_at = datetime.utcnow()
    
    await session.commit()
    
    return {"success": True, "message": "Profile updated successfully"}


@app.put("/api/profile/change-password")
async def change_password(
    request: Request,
    user_data: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Change user password"""
    data = await request.json()
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    result = await session.execute(
        select(User).where(User.id == user_data['user'].id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify current password
    if not pwd_context.verify(current_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    
    # Hash new password
    user.password_hash = pwd_context.hash(new_password)
    user.profile_updated_at = datetime.utcnow()
    
    await session.commit()
    
    return {"success": True, "message": "Password changed successfully"}


# ============================================================
# PHASE 5: MAP INTEGRATION WITH FIELD WORKERS
# ============================================================

@app.get("/api/villages/field-worker-counts")
async def get_village_field_worker_counts(session: AsyncSession = Depends(get_session)):
    """Get Field Worker counts per village for map display"""
    result = await session.execute(
        select(
            FieldWorker.village_id,
            func.count(FieldWorker.id).label('fw_count')
        )
        .where(FieldWorker.status == 'approved')
        .group_by(FieldWorker.village_id)
    )
    
    counts = {row.village_id: row.fw_count for row in result.all()}
    return counts


@app.get("/api/villages/{village_id}/field-workers")
async def get_village_field_workers(
    village_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get all Field Workers for a specific village"""
    # Get village details
    village_result = await session.execute(
        select(Village).where(Village.id == village_id)
    )
    village = village_result.scalar_one_or_none()
    
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    
    # Get all approved Field Workers for this village
    fw_result = await session.execute(
        select(FieldWorker, User.full_name.label('submitted_by_name'))
        .join(User, FieldWorker.submitted_by_user_id == User.id)
        .where(FieldWorker.village_id == village_id)
        .where(FieldWorker.status == 'approved')
        .order_by(FieldWorker.full_name)
    )
    
    field_workers = []
    for fw, submitted_by_name in fw_result.all():
        field_workers.append({
            "id": fw.id,
            "full_name": fw.full_name,
            "phone": fw.phone,
            "alternate_phone": fw.alternate_phone,
            "email": fw.email,
            "designation": fw.designation,
            "department": fw.department,
            "address_line": fw.address_line,
            "preferred_contact_method": fw.preferred_contact_method,
            "submitted_by": submitted_by_name,
            "created_at": fw.created_at.isoformat()
        })
    
    return {
        "village": {
            "id": village.id,
            "village_name": village.village_name,
            "block_name": village.block_name,
            "population": village.population
        },
        "field_workers": field_workers,
        "total_count": len(field_workers)
    }


@app.get("/api/field-workers/search")
async def search_field_workers(
    q: str = "",
    session: AsyncSession = Depends(get_session)
):
    """Global search for Field Workers across all villages"""
    if not q or len(q) < 2:
        return {"results": [], "total": 0}
    
    search_term = f"%{q.lower()}%"
    
    result = await session.execute(
        select(FieldWorker, Village, User.full_name.label('submitted_by_name'))
        .join(Village, FieldWorker.village_id == Village.id)
        .join(User, FieldWorker.submitted_by_user_id == User.id)
        .where(FieldWorker.status == 'approved')
        .where(
            or_(
                func.lower(FieldWorker.full_name).like(search_term),
                func.lower(FieldWorker.phone).like(search_term),
                func.lower(FieldWorker.email).like(search_term),
                func.lower(FieldWorker.designation).like(search_term),
                func.lower(FieldWorker.department).like(search_term),
                func.lower(Village.name).like(search_term),
                func.lower(Village.block).like(search_term)
            )
        )
        .order_by(FieldWorker.full_name)
        .limit(50)
    )
    
    results = []
    for fw, village, submitted_by_name in result.all():
        results.append({
            "id": fw.id,
            "full_name": fw.full_name,
            "phone": fw.phone,
            "email": fw.email,
            "designation": fw.designation,
            "department": fw.department,
            "village_id": village.id,
            "village_name": village.village_name,
            "block_name": village.block_name,
            "submitted_by": submitted_by_name
        })
    
    return {"results": results, "total": len(results), "query": q}


@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request, session: AsyncSession = Depends(get_session)):
    """Public about page"""
    result = await session.execute(select(AboutPage))
    about = result.scalar_one_or_none()
    
    if not about:
        about = AboutPage(
            title="About Us",
            subtitle="Serving with Devotion",
            main_content="We have not named anything yet, awaiting blessings from Param Pujyapad Sree Sree Acharya Dev"
        )
        session.add(about)
        await session.commit()
        await session.refresh(about)
    
    user = get_optional_user(request)
    return templates.TemplateResponse("about.html", {
        "request": request,
        "about": about,
        "user": user
    })


@app.get("/api/about")
async def get_about_api(session: AsyncSession = Depends(get_session)):
    """API endpoint to fetch about page content"""
    result = await session.execute(select(AboutPage))
    about = result.scalar_one_or_none()
    
    if not about:
        about = AboutPage(
            title="About Us",
            subtitle="Serving with Devotion",
            main_content="We have not named anything yet, awaiting blessings from Param Pujyapad Sree Sree Acharya Dev"
        )
        session.add(about)
        await session.commit()
        await session.refresh(about)
    
    return {
        "id": about.id,
        "title": about.title,
        "subtitle": about.subtitle,
        "main_content": about.main_content,
        "mission_statement": about.mission_statement,
        "vision_statement": about.vision_statement,
        "contact_info": about.contact_info,
        "last_edited_by": about.last_edited_by,
        "updated_at": about.updated_at.isoformat() if about.updated_at else None
    }


@app.put("/api/admin/about")
async def update_about(
    request: Request,
    title: str = Form(...),
    subtitle: Optional[str] = Form(None),
    main_content: str = Form(...),
    mission_statement: Optional[str] = Form(None),
    vision_statement: Optional[str] = Form(None),
    contact_info: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(require_super_admin)
):
    """Admin endpoint to update about page content (requires super_admin)"""
    result = await session.execute(select(AboutPage))
    about = result.scalar_one_or_none()
    
    if not about:
        about = AboutPage()
        session.add(about)
    
    about.title = title
    about.subtitle = subtitle
    about.main_content = main_content
    about.mission_statement = mission_statement
    about.vision_statement = vision_statement
    about.contact_info = contact_info
    about.last_edited_by = admin.email
    about.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(about)
    
    return {
        "success": True,
        "message": "About page updated successfully",
        "about": {
            "id": about.id,
            "title": about.title,
            "subtitle": about.subtitle,
            "main_content": about.main_content,
            "mission_statement": about.mission_statement,
            "vision_statement": about.vision_statement,
            "contact_info": about.contact_info,
            "last_edited_by": about.last_edited_by,
            "updated_at": about.updated_at.isoformat() if about.updated_at else None
        }
    }


@app.get("/admin/about", response_class=HTMLResponse)
async def admin_about_page(
    request: Request,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin)
):
    """Admin page for editing about content"""
    result = await session.execute(select(AboutPage))
    about = result.scalar_one_or_none()
    
    if not about:
        about = AboutPage(
            title="About Us",
            subtitle="Serving with Devotion",
            main_content="We have not named anything yet, awaiting blessings from Param Pujyapad Sree Sree Acharya Dev"
        )
        session.add(about)
        await session.commit()
        await session.refresh(about)
    
    return templates.TemplateResponse("admin_about.html", {
        "request": request,
        "about": about,
        "admin": admin
    })
