# DP Works - Bhadrak 🗺️

## Overview
**DP Works - Bhadrak** is a professional village-level interactive map displaying all 1,315 villages of Bhadrak district, Odisha with actual geographic boundaries. The system features role-based authentication where Block Coordinators can register, get admin approval, and submit Field Worker contact details for their assigned blocks. Admins review and approve all submissions.

**Rebranded from:** Seva Atlas → DP Works - Bhadrak  
**Current Version:** 2.1.0  
**Status:** Phase 2 Complete - Field Worker Submission System Live!

---

## 📋 Version 2.1.0 - Field Worker Submission Interface (October 29, 2025)

### ✅ PHASE 2 COMPLETE: Field Worker Submission & Approval System

**NEW FEATURES:**
1. **Field Worker Submission Form** (`/field-workers/new`)
   - 4-section organized form (Personal, Contact, Location, Availability)
   - Village autocomplete search (1,315 villages)
   - Real-time duplicate phone number detection
   - Exception modal for valid duplicate entries
   - Mobile-responsive glassmorphism UI
   - 12 configurable fields loaded dynamically

2. **My Submissions Dashboard** (`/field-workers/my-submissions`)
   - View all submitted Field Workers
   - Real-time statistics (Total, Pending, Approved, Rejected)
   - Filter by status and search
   - Edit/delete pending submissions
   - Cannot modify approved/rejected entries (locked)
   - Mobile-responsive with cards

3. **Admin Approval Interface** (`/admin/field-workers`)
   - Review all Field Worker submissions
   - Approve/reject workflow with reasons
   - Filter by block, status, search
   - Statistics dashboard
   - Duplicate exception warnings
   - Bulk review capability

4. **Smart Duplicate Detection**
   - Phone number uniqueness check
   - Exception modal with reason requirement
   - Tracks duplicate_of_phone and exception_reason
   - Admin sees duplicate exceptions highlighted

5. **Approval Workflow**
   - Submissions start as 'pending'
   - Coordinators can edit/delete pending submissions
   - Admin approves → status='approved', entry locked
   - Admin rejects → status='rejected' with reason, entry locked
   - Approval tracking (approved_by, approved_at)

### API Endpoints (Version 2.1.0)

#### Field Worker Management
- `GET /field-workers/new` - Submission form page
- `POST /api/field-workers` - Submit new Field Worker
- `GET /field-workers/my-submissions` - Coordinator submissions page
- `GET /api/field-workers/my-submissions` - Get coordinator's submissions
- `DELETE /api/field-workers/{id}` - Delete pending submission

#### Form Configuration
- `GET /api/form-fields` - Get visible form field configuration
- `GET /api/villages` - Get all villages for autocomplete (lightweight)

#### Admin Field Worker Management
- `GET /admin/field-workers` - Admin approval interface
- `GET /api/admin/field-workers` - Get all submissions
- `POST /api/admin/field-workers/{id}/approve` - Approve submission
- `POST /api/admin/field-workers/{id}/reject` - Reject with reason

### Field Worker Submission Flow

```
Coordinator Login
  ↓
Navigate to /field-workers/new
  ↓
Fill Form (12 fields)
  ↓
Select Village (Autocomplete)
  ↓
Submit → Duplicate Check
  ↓
If Duplicate → Exception Modal
  ↓
If No Duplicate OR Exception Provided → field_workers table (status='pending')
  ↓
Admin Review at /admin/field-workers
  ↓
Approve → status='approved', locked
  OR
Reject → status='rejected', locked with reason
  ↓
Coordinator sees status in /field-workers/my-submissions
```

### Form Field Configuration (12 Fields)

All fields configurable via `form_field_config` table:

**Required Fields (3):**
1. full_name - Text input
2. phone - Tel input (10-digit validation)
3. designation - Select dropdown (6 options)

**Optional Fields (9):**
4. alternate_phone - Tel input
5. email - Email input
6. department - Text input
7. employee_id - Text input
8. address_line - Textarea
9. landmark - Text input
10. preferred_contact_method - Select (4 options: Phone, Email, WhatsApp, SMS)
11. available_days - Text input
12. available_hours - Text input

---

## 📋 Version 2.0.0 - Authentication System (October 29, 2025)

### ✅ PHASE 1 COMPLETE: Database & Auth Implementation

**FEATURES:**
1. **Role-Based Authentication System**
   - Super Admin: Full system control
   - Block Coordinator: Submit Field Workers for assigned blocks
   - Password hashing with bcrypt (12 rounds)
   - Session-based authentication (7-day expiry)

2. **User Registration & Approval**
   - Block Coordinators self-register at `/register`
   - Manual admin approval required
   - Multi-block assignment capability

3. **Database Schema Expansion**
   - `users` table: Authentication & role management
   - `field_workers` table: Field Worker submissions with approval workflow
   - `form_field_config` table: Admin-configurable form fields

### Database Tables (Current Version)

#### users (Phase 1)
```sql
- id, email, password_hash, full_name, phone
- role (super_admin | block_coordinator)
- primary_block, assigned_blocks (comma-separated)
- is_active (approval status)
- approved_by, approved_at, rejection_reason
- created_at, last_login, login_count
```

#### field_workers (Phase 2)
```sql
- id, full_name, phone, alternate_phone, email
- village_id (FK → villages.id)
- address_line, landmark
- designation, department, employee_id
- preferred_contact_method, available_days, available_hours
- status ('pending' | 'approved' | 'rejected')
- submitted_by_user_id (FK → users.id)
- approved_by, approved_at, rejection_reason
- duplicate_exception_reason, duplicate_of_phone
- is_active, created_at, updated_at, last_verified_at
```

#### form_field_config (Phase 1)
```sql
- id, field_name, field_label, field_type
- is_required, is_visible, display_order
- placeholder, help_text
- min_length, max_length, pattern
- options (JSON for select fields)
- created_at, updated_at
```

---

## Previous Features (Version 1.x)

### ✅ 3D Glowing Dot System
- 8 CSS-based dot styles (neon_glow, pulse_ring, double_halo, etc.)
- Pure CSS animations (box-shadow, radial-gradient)
- Performance optimized for mobile

### ✅ Pin System & Map Features
- Google Maps-style zoom-based visibility
- All 1,315 villages with geographic boundaries
- Choropleth heatmap with data-driven colors
- Block boundaries with customizable colors
- Smart tooltips and modals

### Database Schema (Legacy)
- `villages` table: 1,315 villages (loaded via API from GeoJSON)
- `village_pins` table: Field worker and UK center counts
- `block_settings` table: Administrative block visual settings
- `map_settings` table: Global map visualization settings
- `custom_labels` table: Customizable UI terminology

---

## Project Architecture

### Technology Stack
- **Backend:** FastAPI (Python), SQLModel, AsyncPG
- **Frontend:** D3.js for map, Pure CSS for UI
- **Database:** PostgreSQL (Neon) with async support
- **Authentication:** bcrypt + itsdangerous (session tokens)
- **Maps:** GeoJSON with Mercator projection

### Key Files
**Core Application:**
- `main.py` - FastAPI application (1,926 lines, 20+ endpoints)
- `models.py` - SQLModel models (429 lines, 18 tables)
- `auth.py` - Authentication system (140 lines)
- `db.py` - Database connection (asyncpg)

**Templates (5,532 total lines):**
- `index.html` - Main map interface with D3.js
- `admin.html` - Admin dashboard
- `admin_field_workers.html` - Field Worker approval interface (Phase 2)
- `register.html` - Block Coordinator registration
- `login.html` - Unified login with role detection
- `dashboard.html` - Block Coordinator dashboard
- `field_worker_new.html` - Field Worker submission form (Phase 2)
- `field_worker_submissions.html` - My Submissions page (Phase 2)

**GeoJSON Data:**
- `static/geojson/bhadrak_villages.geojson` - 1,315 village boundaries (13MB)
- `static/geojson/bhadrak_blocks.geojson` - 7 administrative blocks

### Critical Technical Decisions
1. **NEVER load bhadrak_villages.geojson in frontend** - Always use `/api/villages/pins`
2. **Password Security:** bcrypt (12 rounds), httponly cookies, samesite=lax
3. **Session Management:** 7-day expiry tokens
4. **Role Detection:** Login returns role and redirects accordingly
5. **Multi-Block Access:** assigned_blocks + primary_block
6. **Approval Workflow:** Manual admin approval prevents spam
7. **Duplicate Prevention:** Phone number check with exception modal
8. **Village Autocomplete:** Lightweight API returns only needed fields (id, name, block, population)
9. **Status Locking:** Approved/rejected entries cannot be edited or deleted

---

## Admin Credentials
- **Email:** admin@example.com
- **Password:** admin123
- **Role:** super_admin
- **Access:** Full system control

---

## Current Status (Version 2.1.0)

### ✅ Completed Features
- ✅ User authentication system (bcrypt + sessions)
- ✅ Role-based access control
- ✅ User registration with admin approval
- ✅ Login with automatic role detection
- ✅ Field Worker submission form with autocomplete
- ✅ Duplicate phone number detection with exception modal
- ✅ My Submissions dashboard for coordinators
- ✅ Admin Field Worker approval interface
- ✅ Approve/reject workflow with reasons
- ✅ Status locking (approved/rejected = locked)
- ✅ Mobile-responsive glassmorphism UI
- ✅ Database tables: users, field_workers, form_field_config
- ✅ 12 configurable form fields seeded
- ✅ All 1,315 villages rendering on map
- ✅ 3D glowing dots system
- ✅ API endpoints for full workflow

### 📊 Database Statistics
```
Total Tables: 16
Phase 1 Tables: 3 (users, field_workers, form_field_config)
Phase 2 Enhancements: field_workers fully utilized

Current Data:
- users: 0 (ready for registrations)
- field_workers: 0 (ready for submissions)
- form_field_config: 12 (seeded and configured)
- villages: 3 in DB (map loads 1,315 from GeoJSON API)
```

### 🎯 User Workflows

**Block Coordinator Workflow:**
1. Register at `/register` → pending approval
2. Admin approves → account activated
3. Login → redirected to `/dashboard`
4. Submit Field Worker → `/field-workers/new`
5. View submissions → `/field-workers/my-submissions`
6. Edit/delete pending entries
7. See approval status and rejection reasons

**Super Admin Workflow:**
1. Login → redirected to `/admin`
2. Approve user registrations → API endpoints ready
3. Review Field Workers → `/admin/field-workers`
4. Approve/reject submissions with reasons
5. View statistics and filter by block/status
6. Configure form fields (admin can toggle required/visible)

---

## Next Steps (Phase 3 - Future)

### Google OAuth Integration
- Add Google Sign-In as login option
- Keep existing email/password system
- User preference for login method
- **Cost:** FREE (Google OAuth is free)

### Enhanced Features
1. Edit approved Field Worker entries (admin only)
2. Bulk approve multiple submissions
3. Export Field Workers to CSV
4. Email notifications for approvals/rejections
5. Field Worker verification workflow
6. Activity logs and audit trail
7. Dashboard statistics and analytics
8. Block-wise Field Worker counts on map

---

## Deployment
- **Target:** Autoscale (stateless web app)
- **Command:** `uvicorn main:app --host 0.0.0.0 --port 5000`
- **Environment Secrets:**
  - `MAPBOX_ACCESS_TOKEN` - For map rendering
  - `SESSION_SECRET` - For session encryption
  - `DATABASE_URL` - PostgreSQL connection (auto-configured)

---

## User Preferences
- **Budget-conscious:** Efficient implementation, no unnecessary features
- **Professional appearance:** Glassmorphism UI, bright sunlit forest background
- **Full admin control:** All terminology and fields customizable
- **Mobile-first:** Responsive design, touch-friendly
- **Security:** Strong password hashing, role-based access
- **Real Bhadrak geography:** Actual village boundaries, no rectangles
- **Thorough testing:** Every feature must be verified before delivery

---

## Footer Branding
`© 2025 @dpworks Bhadrak Team. All rights reserved.`

---

**Last Updated:** October 29, 2025  
**Version:** 2.1.0  
**Phase 1 Status:** ✅ Complete and Verified  
**Phase 2 Status:** ✅ Complete and Verified  
**Next Phase:** Google OAuth Integration (Phase 3)
