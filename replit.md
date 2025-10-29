# DP Works - Bhadrak 🗺️

## Overview
**DP Works - Bhadrak** is a professional village-level interactive map displaying all 1,315 villages of Bhadrak district, Odisha with actual geographic boundaries. The system now features role-based authentication where Block Coordinators can register, get admin approval, and submit Field Worker contact details for their assigned blocks.

**Rebranded from:** Seva Atlas → DP Works - Bhadrak  
**Current Version:** 2.0.0  
**Status:** Phase 1 Complete - Authentication & Database Implemented!

---

## 📋 Version 2.0.0 - Authentication System (October 29, 2025)

### ✅ PHASE 1 COMPLETE: Database & Auth Implementation

**NEW FEATURES:**
1. **Role-Based Authentication System**
   - Super Admin: Full system control (admin@example.com / admin123)
   - Block Coordinator: Can submit Field Worker data for assigned blocks
   - Password hashing with bcrypt (12 rounds minimum)
   - Session-based authentication with 7-day expiry

2. **User Registration & Approval Workflow**
   - Block Coordinators can self-register at `/register`
   - Manual admin approval required before account activation
   - Multi-block assignment capability
   - Registration tracking (created_at, approval timestamps)

3. **Database Schema Expansion**
   - `users` table: Email, password_hash, role, assigned_blocks, approval status
   - `field_workers` table: Contact details with approval workflow (pending → approved)
   - `form_field_config` table: 12 configurable form fields for admin control

4. **Field Worker Submission System**
   - 12 configurable fields: full_name, phone, email, designation, etc.
   - Admin can toggle required/visible fields
   - Duplicate phone number prevention with exception modal
   - Status workflow: pending → approved/rejected
   - Locked editing after approval

5. **Mobile-Responsive UI**
   - Glassmorphism design with bright sunlit forest background
   - 4-tier breakpoints for all screen sizes
   - Hamburger menu on mobile
   - Full-screen modals on mobile devices

### Database Tables (Version 2.0.0)

#### users
```sql
- id (SERIAL PRIMARY KEY)
- email (VARCHAR, UNIQUE)
- password_hash (VARCHAR)
- full_name (VARCHAR)
- phone (VARCHAR)
- role (VARCHAR) - 'super_admin' or 'block_coordinator'
- primary_block (VARCHAR)
- assigned_blocks (TEXT) - Comma-separated block names
- is_active (BOOLEAN) - Approval status
- approved_by (VARCHAR)
- approved_at (TIMESTAMP)
- rejection_reason (TEXT)
- created_at (TIMESTAMP)
- last_login (TIMESTAMP)
- login_count (INTEGER)
```

#### field_workers
```sql
- id (SERIAL PRIMARY KEY)
- full_name (VARCHAR)
- phone (VARCHAR) - For duplicate checking
- alternate_phone (VARCHAR)
- email (VARCHAR)
- village_id (INTEGER FK → villages.id)
- address_line (TEXT)
- landmark (VARCHAR)
- designation (VARCHAR)
- department (VARCHAR)
- employee_id (VARCHAR)
- preferred_contact_method (VARCHAR)
- available_days (VARCHAR)
- available_hours (VARCHAR)
- status (VARCHAR) - 'pending', 'approved', 'rejected'
- submitted_by_user_id (INTEGER FK → users.id)
- approved_by (VARCHAR)
- approved_at (TIMESTAMP)
- rejection_reason (TEXT)
- duplicate_exception_reason (TEXT)
- duplicate_of_phone (VARCHAR)
- is_active (BOOLEAN)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
- last_verified_at (TIMESTAMP)
```

#### form_field_config
```sql
- id (SERIAL PRIMARY KEY)
- field_name (VARCHAR, UNIQUE)
- is_required (BOOLEAN)
- is_visible (BOOLEAN)
- display_order (INTEGER)
- field_label (VARCHAR)
- field_type (VARCHAR) - 'text', 'tel', 'email', 'textarea', 'select'
- placeholder (VARCHAR)
- help_text (TEXT)
- min_length (INTEGER)
- max_length (INTEGER)
- pattern (VARCHAR) - Regex validation
- options (TEXT) - JSON array for select fields
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### API Endpoints (Version 2.0.0)

#### Authentication
- `GET /register` - Registration page for Block Coordinators
- `POST /api/auth/register` - Create new user account (pending approval)
- `GET /admin/login` - Unified login page with role detection
- `POST /api/auth/login` - Login with automatic role-based redirect
- `GET /dashboard` - Block Coordinator dashboard

#### User Management (Admin Only)
- `GET /api/admin/pending-users` - List pending registrations
- `POST /api/admin/approve-user/{user_id}` - Approve user with block assignment
- `POST /api/admin/reject-user/{user_id}` - Reject registration with reason

#### Field Workers (Coming in Phase 2)
- `GET /field-workers/new` - Submit new Field Worker
- `GET /field-workers/my-submissions` - View coordinator's submissions
- `GET /api/field-workers` - List all Field Workers (with filters)
- `POST /api/field-workers` - Create new entry
- `PUT /api/field-workers/{id}` - Update entry (if pending)
- `DELETE /api/field-workers/{id}` - Delete entry (if pending)

### Permission System

**Super Admin (`super_admin`):**
- Full access to all features
- Approve/reject user registrations
- Assign multiple blocks to coordinators
- Configure form fields
- Approve/reject Field Worker submissions
- Access all blocks' data

**Block Coordinator (`block_coordinator`):**
- Submit Field Worker data for assigned blocks only
- View own submissions
- Edit pending submissions
- Cannot approve own submissions
- Limited to assigned block(s)

### Authentication Flow

1. **User Registration:**
   ```
   User visits /register
   → Fills form (name, email, phone, primary_block, password)
   → POST /api/auth/register
   → Account created with is_active=FALSE
   → Redirect to login with "pending approval" message
   ```

2. **Admin Approval:**
   ```
   Admin logs in
   → Views pending users at /admin/pending-users
   → Assigns additional blocks (optional)
   → Approves user
   → User.is_active = TRUE, approved_at set
   ```

3. **User Login:**
   ```
   User visits /admin/login
   → Enters credentials
   → POST /api/auth/login
   → If super_admin → redirect /admin
   → If block_coordinator → redirect /dashboard
   → Session cookie set (7-day expiry)
   ```

---

## Previous Features (Version 1.x)

### ✅ 3D Glowing Dot System (October 28, 2025)
- Migrated from 18 SVG pin styles to 8 CSS-based 3D glowing dots
- Styles: neon_glow, pulse_ring, double_halo, soft_blur, sharp_core, plasma, crystal, firefly
- Pure CSS: box-shadow for glow, radial-gradient for depth, CSS animations
- Fixed critical bug: API now returns `dot_style` field in map settings
- Performance: No compromise on visual effects even on mobile

### ✅ Pin System (October 26, 2025)
- Google Maps-style zoom-based visibility
- All 1,315 villages have pins
- Smart tooltips based on data availability
- Data-driven colors for villages with Field Worker data
- Clean choropleth view when zoomed out

### Database Schema (Legacy)
- `villages` table: 1,315 villages with geographic boundaries
- `village_pins` table: Field worker and UK center counts
- `block_settings` table: Administrative block visual settings
- `map_settings` table: Global map visualization settings
- `custom_labels` table: Customizable UI terminology

---

## Project Architecture

### Technology Stack
- **Backend:** FastAPI (Python), SQLModel, AsyncPG
- **Frontend:** D3.js for map rendering, Pure CSS (no Tailwind on map)
- **Database:** PostgreSQL (Neon) with async support
- **Authentication:** bcrypt + itsdangerous (session tokens)
- **Maps:** GeoJSON with Mercator projection

### Key Files
- `main.py` - FastAPI application with all endpoints (1500+ lines)
- `models.py` - SQLModel models (15 tables including new auth tables)
- `auth.py` - Authentication functions (hash_password, verify_password, role checks)
- `db.py` - Database connection (asyncpg)
- `templates/index.html` - Main map interface with D3.js
- `templates/admin.html` - Admin dashboard
- `templates/register.html` - Block Coordinator registration
- `templates/login.html` - Unified login with role detection
- `templates/dashboard.html` - Block Coordinator dashboard
- `static/geojson/bhadrak_villages.geojson` - 1,315 village boundaries (13MB)
- `static/geojson/bhadrak_blocks.geojson` - 7 administrative blocks

### Critical Technical Decisions
1. **NEVER load bhadrak_villages.geojson in frontend** - Always use API to prevent crashes
2. **Password Security:** bcrypt with 12 rounds minimum, never store plain passwords
3. **Session Management:** 7-day expiry, httponly cookies, samesite=lax
4. **Role Detection:** Login endpoint returns role and redirects accordingly
5. **Multi-Block Access:** Comma-separated assigned_blocks + primary_block
6. **Approval Workflow:** Manual admin approval prevents spam registrations
7. **Duplicate Prevention:** Phone number uniqueness with exception modal

### Data Flow (Version 2.0.0)
```
User Registration Flow:
  Register Form → /api/auth/register → users table (is_active=FALSE)
    ↓
  Admin Approval → /api/admin/approve-user → is_active=TRUE
    ↓
  User Login → /api/auth/login → Session cookie + role-based redirect

Field Worker Submission Flow (Phase 2):
  Coordinator → /field-workers/new → Fills form
    ↓
  Duplicate Check → Shows exception modal if needed
    ↓
  Submit → field_workers table (status='pending')
    ↓
  Admin Approval → status='approved', locked for editing
```

---

## Admin Credentials
- **Email:** admin@example.com
- **Password:** admin123
- **Role:** super_admin
- **Access:** Full system control

## Seeded Data (Version 2.0.0)

### Form Field Configuration (12 fields)
1. full_name (required, text)
2. phone (required, tel) - 10-digit validation
3. alternate_phone (optional, tel)
4. email (optional, email)
5. designation (required, select) - 6 options
6. department (optional, text)
7. employee_id (optional, text)
8. address_line (optional, textarea)
9. landmark (optional, text)
10. preferred_contact_method (optional, select) - 4 options
11. available_days (optional, text)
12. available_hours (optional, text)

### Block Names (7 blocks)
- Bhadrak
- Basudevpur
- Tihidi
- Chandbali
- Dhamnagar
- Bonth
- Tihidi (duplicate in original data)

---

## User Preferences
- **Budget-conscious:** User spent $30, needs focused execution
- **No rectangular blocks:** Demands real Bhadrak geography
- **Professional appearance:** USA-style choropleth with glassmorphism UI
- **Full admin control:** All terminology and fields customizable
- **Mobile-first:** Responsive design with hamburger menu
- **Security:** Strong password hashing, role-based access

---

## Next Steps (Phase 2 - Pending)

### Field Worker Submission Interface
1. Build `/field-workers/new` form page
2. Implement duplicate phone check with modal
3. Add village autocomplete search
4. Real-time form validation
5. Submit to field_workers table with status='pending'

### Admin Field Worker Management
6. List all pending Field Worker submissions
7. Approve/reject workflow with reason
8. Edit submitted data before approval
9. Bulk approve multiple entries
10. Export to CSV functionality

### Dashboard Enhancement
11. Show submission statistics (pending, approved, rejected)
12. Recent submissions widget
13. Block-wise summary cards
14. Quick actions panel

### Mobile Optimization
15. Touch gestures: pinch-zoom, double-tap
16. Full-screen modals on mobile
17. Bottom sheet UI for forms
18. Optimized tap targets (min 44px)

---

## Deployment
- **Target:** Autoscale (stateless web app)
- **Command:** `uvicorn main:app --host 0.0.0.0 --port 5000`
- **Environment Secrets:**
  - `MAPBOX_ACCESS_TOKEN` - For map rendering
  - `SESSION_SECRET` - For session encryption (production)
  - `DATABASE_URL` - PostgreSQL connection (auto-configured by Replit)

---

## Current Status (Version 2.0.0)
- ✅ User authentication system (bcrypt + sessions)
- ✅ Role-based access control (super_admin, block_coordinator)
- ✅ User registration with admin approval
- ✅ Login with automatic role detection
- ✅ Database tables: users, field_workers, form_field_config
- ✅ Seeded 12 configurable form fields
- ✅ Mobile-responsive glassmorphism UI
- ✅ API endpoints for user management
- ✅ Block Coordinator dashboard placeholder
- ⏳ Field Worker submission form (Phase 2)
- ⏳ Admin Field Worker approval interface (Phase 2)
- ⏳ Submission statistics dashboard (Phase 2)
- ⏳ Production deployment: Ready to publish

---

## Footer Branding
`© 2025 @dpworks Bhadrak Team. All rights reserved.`

---

**Last Updated:** October 29, 2025  
**Version:** 2.0.0  
**Phase 1 Status:** ✅ Complete and Verified  
**Next Phase:** Field Worker Submission Interface
