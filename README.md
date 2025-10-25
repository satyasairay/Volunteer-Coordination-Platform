# Satsangee District Map

A FastAPI-based web application for mapping villages, volunteers, and doctors in Bhadrak district, Odisha.

## Features

- 🗺️ Interactive Leaflet map with village markers and clustering
- 📍 Search villages by name with smooth fly-to animation
- 👥 Village-based volunteer/professional listings
- 👨‍⚕️ Verified doctors directory with filters
- 🔐 Admin panel for data management
- 📤 Bulk CSV import for villages and members
- 📱 Mobile-responsive design

## Quick Start

### 1. Setup Environment Variables

Add these secrets in Replit:

```
ADMIN_EMAIL=your-email@example.com
ADMIN_PASSWORD=your-secure-password
SESSION_SECRET=your-random-secret-key
```

Optional:
```
DATABASE_URL=postgresql://user:pass@host/dbname  # For PostgreSQL instead of SQLite
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Load Sample Data

Import the sample villages and members:

1. Start the server: `uvicorn main:app --host 0.0.0.0 --port 8000`
2. Navigate to `/admin/login` and login with your credentials
3. Go to `/admin` dashboard
4. Upload `sample_villages.csv` in the "Bulk Upload Villages" section
5. Upload `sample_members.csv` in the "Bulk Upload Members" section (check "Verify all on import")

### 4. Process Real GeoJSON Data (Optional)

If you have Bhadrak 2011 census GeoJSON:

```bash
python scripts/geo_to_centroids.py bhadrak_2011.geojson villages.csv
```

Then upload the generated `villages.csv` via the admin panel.

## CSV Formats

### Villages CSV
```csv
name,block,lat,lng,south,west,north,east,code_2011
Bhadrak Town,Bhadrak,21.054239,86.517891,21.045,86.510,21.063,86.525,021001
```

### Members CSV
```csv
full_name,role,phone,languages,village
Rajesh Kumar,Volunteer,9876543210,"Odia, Hindi",Bhadrak Town
```

**Valid Roles:** Volunteer, Electrician, Plumber, Technician, Lawyer, Engineer

## API Endpoints

### Public APIs
- `GET /` - Map page
- `GET /doctors` - Doctors list page
- `GET /api/villages` - Get all villages
- `GET /api/members?village_id=&role=&verified=&q=` - Get members
- `GET /api/village/{id}/volunteers` - Get verified members for a village
- `POST /report` - Report a profile

### Admin APIs
- `GET /admin/login` - Admin login
- `GET /admin` - Dashboard
- `GET /admin/members` - Manage members
- `GET /admin/doctors` - Manage doctors
- `POST /admin/bulk/villages` - Bulk upload villages
- `POST /admin/bulk/members` - Bulk upload members

## Database

The app uses SQLite by default (`satsangee.db`). To switch to PostgreSQL, set the `DATABASE_URL` environment variable.

Tables are auto-created on first run.

## Development

Run locally:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Tech Stack

- **Backend:** FastAPI, SQLModel, SQLAlchemy
- **Frontend:** Jinja2 templates, Tailwind CSS
- **Map:** Leaflet.js + MarkerCluster
- **Database:** SQLite (PostgreSQL-ready)

## Map Controls

- **Search:** Type village name and press Enter to fly to location
- **Bhadrak Button:** Recenter map on Bhadrak district
- **Markers:** Click village markers to see verified volunteers
- **Doctors Link:** Navigate to verified doctors directory

## License

MIT
