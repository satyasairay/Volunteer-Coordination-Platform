# Priority 3: Admin Role Management System (Support 10+ Admins)

**Status:** Planning Phase  
**Created:** October 29, 2025  
**Estimated Effort:** 6-8 hours  
**Priority:** High

---

## 🎯 Objective

Build a Super Admin panel to manage multiple administrators with role-based access control:
1. Create new admin accounts (Block Coordinators and Super Admins)
2. Change roles (promote/demote between coordinator ↔ super_admin)
3. Deactivate/reactivate admin accounts
4. View all admins in a table
5. Support 10+ admins (scalable design)

---

## 📋 Requirements

### Functional Requirements

#### 1. Super Admin Dashboard Page (`/admin`)

**Existing Features (Keep):**
- View pending registrations
- Approve/reject Block Coordinator requests
- View system statistics

**New Features (Add):**
- **Admin Management Tab** - New section to manage existing admins
- **Create Admin Button** - Manually create admin accounts (bypass registration)
- **Role Change Action** - Promote coordinator to super_admin or demote super_admin to coordinator
- **Deactivate/Activate Action** - Disable login without deleting account
- **Admin List Table** - View all admins with filters

#### 2. Admin List Table

**Columns:**
- **#** - Row number
- **Name** - Full name
- **Email** - Email address
- **Role** - Badge (Super Admin 👑 / Block Coordinator 📊)
- **Status** - Badge (Active ✅ / Inactive ❌)
- **Assigned Block** - Block name(s) for coordinators
- **Created** - Date joined
- **Actions** - Dropdown menu

**Actions Dropdown:**
- Change Role → Opens modal
- Deactivate/Activate → Confirmation dialog
- Edit Details → Edit name, email, block assignment
- Delete (only if no data) → Hard delete with warning

**Filters:**
- Show All / Super Admins Only / Coordinators Only
- Active / Inactive
- Search by name or email

**Sorting:**
- By name (A-Z)
- By role
- By created date (newest first)

#### 3. Create Admin Modal

**Form Fields:**
- Full Name* (required)
- Email* (required, must be unique)
- Password* (required, min 8 chars)
- Role* (dropdown: Super Admin / Block Coordinator)
- Assigned Block (dropdown, only if coordinator role)
- Status (Active by default)

**Validation:**
- Email must be valid format
- Email must not already exist
- Password strength indicator
- Block required if coordinator role

**Success:**
- Show success toast: "Admin created successfully!"
- Add row to admin table
- Close modal

#### 4. Change Role Modal

**Display:**
- Current role badge
- Confirmation text: "Change role for [Name] from [Current Role] to [New Role]?"
- New role dropdown (exclude current role)

**Action:**
- Update admin role in database
- Update table row UI
- Show success toast

**Warning:**
- If demoting last super_admin → Show error: "Cannot demote. At least 1 super admin required."

#### 5. Deactivate/Activate Confirmation

**Deactivate:**
- Confirmation dialog: "Deactivate [Name]? They will lose access to the platform."
- On confirm: Set `is_active = false`, show toast, update table badge

**Activate:**
- Confirmation dialog: "Reactivate [Name]? They will regain access."
- On confirm: Set `is_active = true`, show toast, update table badge

---

## 🎨 Design Specification

### Admin Management Tab

**Layout:**
```
┌────────────────────────────────────────────────────┐
│  Admin Management                  [+ Create Admin]│
├────────────────────────────────────────────────────┤
│  Filters: [All ▼] [Active ▼]   🔍 Search...       │
├────────────────────────────────────────────────────┤
│  #  Name         Email        Role    Status  ...  │
│  1  Satya Sai    satya@...    👑       ✅      ⋮  │
│  2  John Doe     john@...     📊       ✅      ⋮  │
│  3  Jane Smith   jane@...     📊       ❌      ⋮  │
└────────────────────────────────────────────────────┘
```

**Styling:**
- Same purple gradient theme
- Cards with glassmorphism
- Badges: rounded pills
- Actions: 3-dot menu (⋮)

---

## 🛠️ Implementation Plan

### Step 1: Database Schema Review (30 minutes)

**Current `admins` table:**
```sql
CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL, -- 'super_admin' or 'block_coordinator'
    block VARCHAR(255), -- Block assigned (for coordinators)
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**No changes needed** - Schema already supports:
- Multiple admins (no limit)
- Role field (can be changed)
- is_active field (can toggle)
- block field (for coordinators)

### Step 2: Backend API Routes (3 hours)

Add new routes to `main.py`:

#### GET `/api/admins` - List all admins (Super Admin only)
```python
@app.get("/api/admins")
async def get_all_admins(admin: Admin = Depends(get_current_admin)):
    if admin.role != "super_admin":
        raise HTTPException(403, "Only super admins can view all admins")
    
    query = "SELECT id, full_name, email, role, block, is_active, created_at FROM admins ORDER BY created_at DESC"
    admins = db.fetch_all(query)
    return admins
```

#### POST `/api/admins` - Create new admin (Super Admin only)
```python
from pydantic import BaseModel, EmailStr

class CreateAdminRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str  # 'super_admin' or 'block_coordinator'
    block: str | None = None
    is_active: bool = True

@app.post("/api/admins")
async def create_admin(
    request: CreateAdminRequest, 
    admin: Admin = Depends(get_current_admin)
):
    if admin.role != "super_admin":
        raise HTTPException(403, "Only super admins can create admins")
    
    # Validate role
    if request.role not in ["super_admin", "block_coordinator"]:
        raise HTTPException(400, "Invalid role")
    
    # Validate block for coordinators
    if request.role == "block_coordinator" and not request.block:
        raise HTTPException(400, "Block required for coordinators")
    
    # Check email doesn't exist
    existing = db.fetch_one("SELECT id FROM admins WHERE email = %s", [request.email])
    if existing:
        raise HTTPException(400, "Email already exists")
    
    # Hash password
    password_hash = pwd_context.hash(request.password)
    
    # Insert admin
    query = """
        INSERT INTO admins (full_name, email, password_hash, role, block, is_active)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, full_name, email, role, block, is_active, created_at
    """
    new_admin = db.fetch_one(query, [
        request.full_name,
        request.email,
        password_hash,
        request.role,
        request.block,
        request.is_active
    ])
    
    return new_admin
```

#### PUT `/api/admins/{admin_id}/role` - Change admin role
```python
class ChangeRoleRequest(BaseModel):
    new_role: str  # 'super_admin' or 'block_coordinator'
    block: str | None = None

@app.put("/api/admins/{admin_id}/role")
async def change_admin_role(
    admin_id: int,
    request: ChangeRoleRequest,
    admin: Admin = Depends(get_current_admin)
):
    if admin.role != "super_admin":
        raise HTTPException(403, "Only super admins can change roles")
    
    # Validate role
    if request.new_role not in ["super_admin", "block_coordinator"]:
        raise HTTPException(400, "Invalid role")
    
    # Get target admin
    target = db.fetch_one("SELECT * FROM admins WHERE id = %s", [admin_id])
    if not target:
        raise HTTPException(404, "Admin not found")
    
    # Prevent demoting last super admin
    if target['role'] == "super_admin" and request.new_role != "super_admin":
        super_admin_count = db.fetch_one("SELECT COUNT(*) as count FROM admins WHERE role = 'super_admin' AND is_active = true")
        if super_admin_count['count'] <= 1:
            raise HTTPException(400, "Cannot demote last super admin")
    
    # Update role
    query = "UPDATE admins SET role = %s, block = %s WHERE id = %s RETURNING *"
    updated = db.fetch_one(query, [request.new_role, request.block, admin_id])
    
    return updated
```

#### PUT `/api/admins/{admin_id}/status` - Activate/Deactivate admin
```python
class ChangeStatusRequest(BaseModel):
    is_active: bool

@app.put("/api/admins/{admin_id}/status")
async def change_admin_status(
    admin_id: int,
    request: ChangeStatusRequest,
    admin: Admin = Depends(get_current_admin)
):
    if admin.role != "super_admin":
        raise HTTPException(403, "Only super admins can change status")
    
    # Get target admin
    target = db.fetch_one("SELECT * FROM admins WHERE id = %s", [admin_id])
    if not target:
        raise HTTPException(404, "Admin not found")
    
    # Prevent deactivating last super admin
    if target['role'] == "super_admin" and not request.is_active:
        active_super_admins = db.fetch_one(
            "SELECT COUNT(*) as count FROM admins WHERE role = 'super_admin' AND is_active = true AND id != %s",
            [admin_id]
        )
        if active_super_admins['count'] == 0:
            raise HTTPException(400, "Cannot deactivate last active super admin")
    
    # Update status
    query = "UPDATE admins SET is_active = %s WHERE id = %s RETURNING *"
    updated = db.fetch_one(query, [request.is_active, admin_id])
    
    return updated
```

#### DELETE `/api/admins/{admin_id}` - Delete admin (optional, dangerous)
```python
@app.delete("/api/admins/{admin_id}")
async def delete_admin(admin_id: int, admin: Admin = Depends(get_current_admin)):
    if admin.role != "super_admin":
        raise HTTPException(403, "Only super admins can delete admins")
    
    # Prevent deleting last super admin
    target = db.fetch_one("SELECT role FROM admins WHERE id = %s", [admin_id])
    if target['role'] == "super_admin":
        super_admin_count = db.fetch_one("SELECT COUNT(*) as count FROM admins WHERE role = 'super_admin'")
        if super_admin_count['count'] <= 1:
            raise HTTPException(400, "Cannot delete last super admin")
    
    db.execute("DELETE FROM admins WHERE id = %s", [admin_id])
    return {"message": "Admin deleted"}
```

### Step 3: Frontend - Admin Management UI (3-4 hours)

Create new template section in `/admin` page (update `templates/admin_dashboard.html` or similar):

**HTML Structure:**
```html
<!-- Admin Management Tab -->
<div class="admin-section">
    <div class="section-header">
        <h2>👥 Admin Management</h2>
        <button class="btn-primary" onclick="openCreateAdminModal()">
            + Create Admin
        </button>
    </div>
    
    <!-- Filters -->
    <div class="filters">
        <select id="roleFilter" onchange="filterAdmins()">
            <option value="all">All Roles</option>
            <option value="super_admin">Super Admins Only</option>
            <option value="block_coordinator">Coordinators Only</option>
        </select>
        
        <select id="statusFilter" onchange="filterAdmins()">
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
        </select>
        
        <input type="text" id="searchAdmins" placeholder="🔍 Search by name or email" oninput="filterAdmins()">
    </div>
    
    <!-- Admin Table -->
    <table id="adminTable">
        <thead>
            <tr>
                <th>#</th>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Block</th>
                <th>Created</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody id="adminTableBody">
            <!-- Populated by JavaScript -->
        </tbody>
    </table>
</div>

<!-- Create Admin Modal -->
<div class="modal" id="createAdminModal" style="display: none;">
    <div class="modal-content">
        <h3>Create New Admin</h3>
        <form id="createAdminForm">
            <label>Full Name *</label>
            <input type="text" id="adminName" required>
            
            <label>Email *</label>
            <input type="email" id="adminEmail" required>
            
            <label>Password *</label>
            <input type="password" id="adminPassword" required minlength="8">
            
            <label>Role *</label>
            <select id="adminRole" onchange="toggleBlockField()">
                <option value="super_admin">Super Admin</option>
                <option value="block_coordinator">Block Coordinator</option>
            </select>
            
            <label id="blockLabel" style="display: none;">Assigned Block *</label>
            <select id="adminBlock" style="display: none;">
                <!-- Populated from blocks API -->
            </select>
            
            <button type="submit" class="btn-primary">Create Admin</button>
            <button type="button" onclick="closeCreateAdminModal()">Cancel</button>
        </form>
    </div>
</div>

<!-- Change Role Modal -->
<div class="modal" id="changeRoleModal" style="display: none;">
    <!-- Similar structure -->
</div>
```

**JavaScript Logic:**
```javascript
let allAdmins = [];

async function loadAdmins() {
    const response = await fetch('/api/admins', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    allAdmins = await response.json();
    renderAdminTable(allAdmins);
}

function renderAdminTable(admins) {
    const tbody = document.getElementById('adminTableBody');
    tbody.innerHTML = admins.map((admin, index) => `
        <tr>
            <td>${index + 1}</td>
            <td>${admin.full_name}</td>
            <td>${admin.email}</td>
            <td>${getRoleBadge(admin.role)}</td>
            <td>${getStatusBadge(admin.is_active)}</td>
            <td>${admin.block || '-'}</td>
            <td>${new Date(admin.created_at).toLocaleDateString()}</td>
            <td>
                <button class="action-menu" onclick="openActionMenu(${admin.id})">⋮</button>
            </td>
        </tr>
    `).join('');
}

function getRoleBadge(role) {
    return role === 'super_admin' 
        ? '<span class="badge badge-admin">👑 Super Admin</span>'
        : '<span class="badge badge-coordinator">📊 Coordinator</span>';
}

function getStatusBadge(isActive) {
    return isActive
        ? '<span class="badge badge-active">✅ Active</span>'
        : '<span class="badge badge-inactive">❌ Inactive</span>';
}

async function createAdmin(formData) {
    const response = await fetch('/api/admins', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
    });
    
    if (response.ok) {
        showToast('Admin created successfully!');
        closeCreateAdminModal();
        loadAdmins(); // Refresh table
    } else {
        const error = await response.json();
        showToast(error.detail, 'error');
    }
}

async function changeAdminRole(adminId, newRole, block) {
    const response = await fetch(`/api/admins/${adminId}/role`, {
        method: 'PUT',
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ new_role: newRole, block })
    });
    
    if (response.ok) {
        showToast('Role changed successfully!');
        loadAdmins();
    } else {
        const error = await response.json();
        showToast(error.detail, 'error');
    }
}

async function toggleAdminStatus(adminId, isActive) {
    const response = await fetch(`/api/admins/${adminId}/status`, {
        method: 'PUT',
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ is_active: isActive })
    });
    
    if (response.ok) {
        showToast(`Admin ${isActive ? 'activated' : 'deactivated'} successfully!`);
        loadAdmins();
    } else {
        const error = await response.json();
        showToast(error.detail, 'error');
    }
}

function filterAdmins() {
    const roleFilter = document.getElementById('roleFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;
    const searchQuery = document.getElementById('searchAdmins').value.toLowerCase();
    
    let filtered = allAdmins;
    
    if (roleFilter !== 'all') {
        filtered = filtered.filter(a => a.role === roleFilter);
    }
    
    if (statusFilter === 'active') {
        filtered = filtered.filter(a => a.is_active);
    } else if (statusFilter === 'inactive') {
        filtered = filtered.filter(a => !a.is_active);
    }
    
    if (searchQuery) {
        filtered = filtered.filter(a => 
            a.full_name.toLowerCase().includes(searchQuery) ||
            a.email.toLowerCase().includes(searchQuery)
        );
    }
    
    renderAdminTable(filtered);
}
```

### Step 4: Security & Validation (1 hour)

1. **Backend validation:**
   - Only super_admin can access admin management routes
   - Prevent deleting/demoting last super admin
   - Validate email format
   - Enforce password strength
   - Sanitize inputs

2. **Frontend validation:**
   - Show role badge on action buttons
   - Confirm destructive actions (delete, deactivate)
   - Disable buttons during API calls

### Step 5: QA Testing (1 hour)

Test scenarios:
- [ ] Super admin can view all admins
- [ ] Block coordinator cannot access admin management
- [ ] Create new super admin → appears in table
- [ ] Create new coordinator → requires block
- [ ] Change coordinator to super admin
- [ ] Change super admin to coordinator
- [ ] Deactivate admin → cannot login
- [ ] Reactivate admin → can login again
- [ ] Cannot deactivate last super admin
- [ ] Cannot demote last super admin
- [ ] Search filters work correctly
- [ ] Mobile responsive

---

## 📊 Database / API Summary

### New API Routes
- `GET /api/admins` - List all admins
- `POST /api/admins` - Create admin
- `PUT /api/admins/{id}/role` - Change role
- `PUT /api/admins/{id}/status` - Activate/deactivate
- `DELETE /api/admins/{id}` - Delete admin (optional)

### Database Schema
**No changes needed** - existing `admins` table supports all features.

---

## 🚀 Future Enhancements (Optional)

1. **Audit Log** - Track who changed what (create, role change, deactivate)
2. **Bulk Actions** - Select multiple admins and deactivate/delete
3. **Email Notifications** - Notify admin when created or role changed
4. **Password Reset** - Allow super admin to reset passwords
5. **2FA Management** - Enforce 2FA for super admins
6. **Permissions Granularity** - Custom permissions beyond just role

---

## ✅ Definition of Done

- [ ] Super admin can view all admins in table
- [ ] Create new admin (super admin or coordinator)
- [ ] Change admin role (promote/demote)
- [ ] Activate/deactivate admin
- [ ] Cannot deactivate/demote last super admin
- [ ] Search and filters work
- [ ] Mobile responsive
- [ ] Security tested (only super admin access)
- [ ] User tested and approved
