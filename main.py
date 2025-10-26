from fastapi import FastAPI, Request, Depends, HTTPException, Form, UploadFile, File, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import csv
import io
import json
import os
from datetime import datetime
from contextlib import asynccontextmanager

from db import init_db, get_session
from models import Village, Member, Doctor, Audit, Report, SevaRequest, SevaResponse, Testimonial, BlockSettings, MapSettings, VillagePin, CustomLabel
from auth import create_session_token, get_current_admin, ADMIN_EMAIL, ADMIN_PASSWORD


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
    
    print("\n" + "="*60)
    print("🕉️  SATSANGEE SEVA ATLAS - Ready to Serve")
    print("="*60)
    print("📍 Public URLs:")
    print("   Seva Map:    http://0.0.0.0:5000/")
    print("   Doctors:     http://0.0.0.0:5000/doctors")
    print("\n🔐 Admin URLs:")
    print("   Login:       http://0.0.0.0:5000/admin/login")
    print("   Dashboard:   http://0.0.0.0:5000/admin")
    print("="*60 + "\n")
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    mapbox_token = os.getenv("MAPBOX_ACCESS_TOKEN", "")
    return templates.TemplateResponse("index.html", {
        "request": request,
        "mapbox_token": mapbox_token
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
    """Get pin data for all villages with field workers and UK centers"""
    # Load full village data with geometries
    with open('static/geojson/bhadrak_villages.geojson', 'r') as f:
        villages_data = json.load(f)
    
    # Get all village pins from database
    result = await session.execute(select(VillagePin))
    pins_dict = {pin.village_id: pin for pin in result.scalars().all()}
    
    # Get custom labels for display
    labels_result = await session.execute(
        select(CustomLabel).order_by(CustomLabel.display_order)
    )
    labels = {label.label_key: label for label in labels_result.scalars().all()}
    
    # Enrich village data with pin information
    features = []
    for i, feature in enumerate(villages_data['features']):
        props = feature['properties']
        village_name = props.get('NAME', f'Village_{i}')
        
        # Get or create default pin data
        pin_data = pins_dict.get(i + 1, None)  # village_id starts at 1
        
        features.append({
            "type": "Feature",
            "properties": {
                "id": i + 1,
                "name": village_name,
                "block": props.get('SUB_DIST', 'Unknown'),
                "population": props.get('population', props.get('POP', 1000 + (i * 10))),
                "field_worker_count": pin_data.field_worker_count if pin_data else 0,
                "uk_center_count": pin_data.uk_center_count if pin_data else 0,
                "custom_data": json.loads(pin_data.custom_data) if pin_data and pin_data.custom_data else {},
                "pin_color": pin_data.pin_color if pin_data else None,
                "is_active": pin_data.is_active if pin_data else True,
            },
            "geometry": feature['geometry']
        })
    
    return {
        "type": "FeatureCollection",
        "features": features,
        "labels": {
            key: {
                "value": label.label_value,
                "singular": label.label_singular,
                "icon": label.label_icon
            }
            for key, label in labels.items()
        }
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
    return templates.TemplateResponse("login.html", {"request": request})


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
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session")
    return response


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
            "village_point_color": "#e63946"
        }
    
    return {
        "metric_name": settings.metric_name,
        "color_scheme": settings.color_scheme,
        "show_villages": settings.show_villages,
        "show_blocks": settings.show_blocks,
        "village_point_color": settings.village_point_color
    }


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
