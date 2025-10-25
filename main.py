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
from datetime import datetime
from contextlib import asynccontextmanager

from db import init_db, get_session
from models import Village, Member, Doctor, Audit, Report, SevaRequest, SevaResponse, Testimonial
from auth import create_session_token, get_current_admin, ADMIN_EMAIL, ADMIN_PASSWORD


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
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
    return templates.TemplateResponse("index.html", {"request": request})


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
        "bbox": [v.south, v.west, v.north, v.east]
    } for v in villages]


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
