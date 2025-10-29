# 🔐 Super Admin Guide
## DP Works - Bhadrak District Atlas

**Version:** 1.0  
**Last Updated:** October 29, 2025

---

## Table of Contents
1. [Admin Overview](#admin-overview)
2. [User Management](#user-management)
3. [Field Worker Approval](#field-worker-approval)
4. [Duplicate Exception Review](#duplicate-exception-review)
5. [Form Field Configuration](#form-field-configuration)
6. [Analytics Dashboard](#analytics-dashboard)
7. [Data Export](#data-export)
8. [Map Settings](#map-settings)
9. [Security & Best Practices](#security--best-practices)
10. [System Maintenance](#system-maintenance)

---

## Admin Overview

### Access Admin Panel
- **URL:** `/admin`
- **Login:** `/admin/login`
- **Credentials:** Configured in environment variables

### Admin Capabilities
✅ Full system control  
✅ User approval/rejection  
✅ Field Worker approval/rejection  
✅ Configure form fields (required/optional)  
✅ Review duplicate phone exceptions  
✅ Edit ALL entries (even approved ones)  
✅ Multi-block assignment for users  
✅ Data export (CSV)  
✅ Analytics & reporting  
✅ Map customization  

---

## User Management

### Pending User Approvals
**Location:** Dashboard → 👥 Users → Pending Users  
**URL:** `/admin/users`

#### Review Process
1. **View Pending Requests:**
   - Name, Email, Phone
   - Requested Primary Block
   - Registration Date

2. **Approve User:**
   - Click **"Approve"** button
   - Optionally assign additional blocks
   - User receives approval email
   - Account becomes active

3. **Reject User:**
   - Click **"Reject"** button
   - Provide clear rejection reason
   - User receives rejection email
   - Account remains inactive

### Multi-Block Assignment
**Purpose:** Assign coordinators to work across multiple blocks

**How to Assign:**
1. Go to `/admin/users`
2. Find approved user
3. Click **"Edit Blocks"**
4. Select additional blocks (comma-separated)
5. Primary block + assigned blocks = total access
6. Click **"Save"**

**Example:**
- Primary Block: **Bhadrak**
- Assigned Blocks: **Bhadrak, Tihidi, Basudevpur**
- Result: Coordinator can submit FW data for all 3 blocks

### User Actions
- 🔓 **Reactivate:** Restore deactivated accounts
- 🔒 **Deactivate:** Suspend user access (retains data)
- ✏️ **Edit Blocks:** Modify assigned blocks
- 👁️ **View Activity:** See user submission history

---

## Field Worker Approval

### Approval Queue
**Location:** Dashboard → 📋 Field Workers  
**URL:** `/admin/field-workers`

#### Submission Statuses
| Status | Icon | Meaning |
|--------|------|---------|
| Pending | ⏳ | Awaiting your review |
| Approved | ✅ | Accepted and public |
| Rejected | ❌ | Declined with reason |

### Approval Workflow
1. **Review Submission:**
   - Full Name, Phone, Village, Designation
   - Submitter Name
   - Submission Date
   - **Duplicate Flag:** ⚠️ if duplicate phone exists

2. **Verify Information:**
   - Check completeness
   - Validate phone format
   - Confirm village in correct block
   - Review duplicate reason (if applicable)

3. **Decision:**
   - **Approve:** Click ✅ **"Approve"** → Entry becomes public & locked
   - **Reject:** Click ❌ **"Reject"** → Provide reason → Coordinator can resubmit

### Bulk Actions
- Filter by: Block, Status, Submitter
- Sort by: Date, Village, Name
- Export filtered results to CSV

---

## Duplicate Exception Review

### Access
**Location:** Dashboard → ⚠️ Duplicates  
**URL:** `/admin/duplicates`

### What Are Duplicate Exceptions?
Coordinators request exceptions when they need to add a Field Worker with a phone number that already exists in the system.

### Review Interface
**Side-by-Side Comparison:**
- **Left:** New submission (pending)
- **Right:** Existing entry (approved)
- **Reason:** Coordinator's explanation

### Decision Process
1. **Read Coordinator's Reason**
   - Example: "Same person, multiple departments"
   - Example: "Shared office phone"

2. **Compare Entries:**
   - Same person? Different roles?
   - Different villages/blocks?
   - Legitimate duplicate?

3. **Action:**
   - **Approve Exception:** Both entries coexist with same phone
   - **Reject:** Coordinator must correct data or use different phone

### Statistics
- **Pending Exceptions:** Awaiting review
- **Approved Duplicates:** Legitimate cases
- **Rejected:** Declined requests

---

## Form Field Configuration

### Access
**Location:** Dashboard → ⚙️ Form Config  
**URL:** `/admin/form-config`

### Purpose
Control which fields are required/optional on the Field Worker submission form.

### Configuration Options
For each of 12 fields:
- ✅ **Required:** Must be filled by coordinator
- ⬜ **Optional:** Can be left blank
- 👁️ **Visible:** Shows on form
- 🙈 **Hidden:** Removed from form

### Field List
1. Full Name (★ core field - always required)
2. Phone (★ core field - always required)
3. Alternate Phone
4. Email
5. Village (★ core field - always required)
6. Address Line
7. Landmark
8. Designation (★ core field - always required)
9. Department
10. Employee ID
11. Preferred Contact Method
12. Available Days
13. Available Hours

### Reordering Fields
- **Drag & Drop:** Use ⋮⋮ handle to reorder
- **Display Order:** Controls form layout
- Click **"Save Changes"** to apply

### Live Preview
- See how form will appear to coordinators
- Updates in real-time as you configure

---

## Analytics Dashboard

### Access
**Location:** Dashboard → 📊 Analytics  
**URL:** `/admin/analytics`

### Key Metrics
1. **Total Field Workers:** All approved entries
2. **Pending Approvals:** Awaiting review
3. **Total Coordinators:** Active users
4. **Coverage:** Villages with FW data

### Charts & Visualizations
- **Block Distribution:** Field Workers per block (Bar Chart)
- **Designation Breakdown:** Pie chart of roles
- **Submission Timeline:** Daily/weekly trends (Line Chart)
- **Top Contributors:** Most active coordinators

### Data Insights
- Identify underserved blocks
- Monitor submission patterns
- Track coordinator activity
- Spot data quality issues

---

## Data Export

### CSV Export Options

#### 1. All Field Workers
**URL:** `/admin/field-workers?export=csv`  
**Contains:** All approved FW entries with complete details

#### 2. Filtered Export
1. Apply filters (block, status, date range)
2. Click **"Export CSV"**
3. Downloads filtered subset

#### 3. User Export
**URL:** `/admin/users?export=csv`  
**Contains:** All user accounts with roles and blocks

### CSV Format
```csv
ID,Full Name,Phone,Email,Village,Block,Designation,Department,Status,Submitted By,Created Date
1,John Doe,9876543210,john@example.com,Alanda,Bhadrak,ANM,Health,approved,coordinator@example.com,2025-10-15
```

### Use Cases
- Offline analysis
- Backup records
- Integration with other systems
- Reporting to higher authorities

---

## Map Settings

### Customization Options
**Location:** Dashboard → Map Settings

#### 1. Color Schemes
- Blues, Greens, Reds, Purples, Oranges, Viridis, Turbo
- Controls village polygon heatmap colors

#### 2. Pin Styles
- Choose from 7 dot styles: Neon Glow, Pulse, Crystal, Firefly, Laser, Halo Fade
- Visible when zoomed in

#### 3. Display Toggles
- Show/Hide Villages
- Show/Hide Blocks
- Show/Hide Pins
- Heat Map Layers

#### 4. Custom Labels
Change terminology:
- "Field Workers" → Your term
- "UK Centers" → Your term
- Icons and display names

---

## Security & Best Practices

### Password Security
- ✅ Bcrypt encryption (12 rounds)
- ✅ Minimum 8 characters required
- ✅ Session expiry: 7 days
- ✅ Automatic logout on inactivity

### SQL Injection Prevention
- ✅ Parameterized queries (SQLModel ORM)
- ✅ Input validation on all forms
- ✅ Type checking at API level

### XSS Protection
- ✅ HTML escaping in templates
- ✅ Content Security Policy headers
- ✅ No inline JavaScript in user content

### Access Control
- ✅ Role-based permissions (Super Admin, Block Coordinator)
- ✅ Block-level data isolation
- ✅ Approval workflows prevent unauthorized changes

### Audit Trail
- ✅ Track who submitted each FW entry
- ✅ Log approval/rejection actions
- ✅ Timestamp all modifications

### Best Practices
1. **Regular Backups:** Export CSV data weekly
2. **Monitor Duplicates:** Review exception requests promptly
3. **User Vetting:** Verify coordinator identities before approval
4. **Data Quality:** Reject incomplete/incorrect submissions
5. **Communication:** Email coordinators about rejections with clear reasons

---

## System Maintenance

### Database Management
**Location:** Replit Database Pane

#### Tables
- `users` - User accounts
- `field_workers` - FW entries
- `villages` - Geographic data
- `form_field_config` - Form settings
- `block_statistics` - Analytics cache

#### Maintenance Tasks
- ✅ Automatic backups (Replit managed)
- ✅ Index optimization (PostgreSQL)
- ✅ Session cleanup (auto-handled)

### Performance Monitoring
- Check server logs for errors
- Monitor API response times
- Review database query performance

### Troubleshooting

#### Users Can't Login
1. Check if account is active (`is_active = true`)
2. Verify email matches exactly
3. Reset password if needed

#### Submissions Not Appearing
1. Check submission status (pending/rejected?)
2. Verify coordinator has assigned blocks
3. Review server logs for errors

#### Map Not Loading
1. Check browser console for JavaScript errors
2. Verify GeoJSON files exist
3. Clear browser cache

#### Slow Performance
1. Check database size (>10,000 FW entries?)
2. Optimize village queries
3. Consider caching block statistics

### Support Contacts
**Technical Issues:**  
Replit Support: support@replit.com

**Database Issues:**  
Check Replit Database Pane → View SQL queries

**Deployment Issues:**  
Review workflow logs in Replit Console

---

## Quick Reference Commands

### Admin URLs
```
Dashboard:          /admin
User Management:    /admin/users
Field Workers:      /admin/field-workers
Duplicates:         /admin/duplicates
Form Config:        /admin/form-config
Analytics:          /admin/analytics
Map Settings:       /admin/settings/map
```

### Keyboard Shortcuts
- `ESC` - Close modals
- `Ctrl+F` - Search (in tables)

### Common Tasks Checklist
- [ ] Approve pending users daily
- [ ] Review FW submissions twice daily
- [ ] Check duplicate exceptions weekly
- [ ] Export data backups weekly
- [ ] Review analytics monthly
- [ ] Update form fields as needed

---

**© 2025 DP Works | Bhadrak District Atlas**  
**Super Admin Guide - Confidential**  
*Last Updated: October 29, 2025*
