# 📋 Block Coordinator Manual
## DP Works - Bhadrak District Atlas

**Version:** 1.0  
**Last Updated:** October 29, 2025

---

## Table of Contents
1. [Getting Started](#getting-started)
2. [Registration & Approval](#registration--approval)
3. [Dashboard Overview](#dashboard-overview)
4. [Adding Field Workers](#adding-field-workers)
5. [Managing Submissions](#managing-submissions)
6. [Duplicate Phone Handling](#duplicate-phone-handling)
7. [My Profile](#my-profile)
8. [Mobile Usage](#mobile-usage)
9. [FAQs](#faqs)

---

## Getting Started

### What is DP Works?
DP Works is an interactive village-level map system for Bhadrak district, Odisha, allowing Block Coordinators to register and manage Field Worker information across 1,315 villages in 7 blocks.

### Your Role as Block Coordinator
- Submit Field Worker information for your assigned block(s)
- Track your submissions (pending/approved/rejected)
- Request duplicate phone exceptions when necessary
- View all Field Workers across the district (read-only)

---

## Registration & Approval

### Step 1: Register Your Account
1. Visit the registration page: `/register`
2. Fill in your details:
   - **Full Name:** Your complete name
   - **Email:** Your official email (used for login)
   - **Phone:** Your contact number
   - **Password:** Minimum 8 characters
   - **Primary Block:** Select your main block from dropdown
3. Click **"Register"**

### Step 2: Wait for Admin Approval
- Your account status: **Pending Approval** ⏳
- Admin will review your request within 24-48 hours
- You'll receive an email once approved
- Admin can assign you additional blocks beyond your primary block

### Step 3: First Login
1. Once approved, visit: `/dashboard`
2. Login with your **email** and **password**
3. You'll see your personalized coordinator dashboard

---

## Dashboard Overview

### Main Statistics
- **My Pending Submissions:** Field Workers awaiting admin approval
- **Total Approved:** Your successfully approved submissions
- **My Assigned Blocks:** Blocks you can submit data for

### Quick Actions
- 📋 **Add Field Worker** → Submit new FW entry
- 📊 **My Submissions** → View/edit your pending entries
- ⚙️ **My Profile** → Update account information
- 🗺️ **View Map** → Explore district map with FW data

---

## Adding Field Workers

### Navigation
Click **"Add Field Worker"** from dashboard or visit `/field-workers/new`

### Required Fields (★)
The form shows 12 fields. Admin configures which are required:
- ★ **Full Name:** Field Worker's complete name
- ★ **Phone Number:** Primary contact (checked for duplicates)
- ★ **Village:** Select from dropdown (only your assigned blocks visible)
- ★ **Designation:** Role/position

### Optional Fields
- **Alternate Phone:** Secondary contact number
- **Email:** Email address
- **Address Line:** Physical address
- **Landmark:** Nearby reference point
- **Department:** Government department/organization
- **Employee ID:** Official identification number
- **Preferred Contact Method:** Phone/Email/SMS
- **Available Days:** Working days
- **Available Hours:** Working hours

### Submission Process
1. Fill all required (★) fields
2. Phone number is validated in real-time
3. If duplicate detected → See [Duplicate Phone Handling](#duplicate-phone-handling)
4. Click **"Submit for Approval"**
5. Status: **Pending** ⏳ (visible in "My Submissions")

### After Submission
- ✅ **If Approved:** Entry becomes public and locked (you cannot edit)
- ❌ **If Rejected:** Admin provides reason; you can resubmit with corrections
- ⏳ **While Pending:** You can edit or delete

---

## Managing Submissions

### View Your Submissions
Visit **"My Submissions"** or `/field-workers/my-submissions`

### Submission Statuses
| Status | Icon | Meaning | Actions Available |
|--------|------|---------|-------------------|
| Pending | ⏳ | Awaiting admin review | Edit, Delete |
| Approved | ✅ | Accepted and public | View only |
| Rejected | ❌ | Not accepted | View reason, Resubmit |

### Editing Pending Submissions
1. Go to "My Submissions"
2. Find the entry with **Pending** status
3. Click **"Edit"**
4. Make changes
5. Click **"Update"**

> **Note:** You can only edit your own pending submissions. Once approved by admin, entries are locked.

### Deleting Submissions
1. Go to "My Submissions"
2. Click **"Delete"** on pending entry
3. Confirm deletion
4. Entry is permanently removed

---

## Duplicate Phone Handling

### When Does This Occur?
When you enter a phone number that already exists in the system for another Field Worker.

### Exception Request Process
1. **System Detects Duplicate:**
   ```
   ⚠️ Phone XXX-XXX-XXXX already exists
   Existing: [Name] in [Village], [Block]
   ```

2. **Click "Request Exception"** (orange button)

3. **Modal Opens:**
   - **Left Side:** Shows your new submission details
   - **Right Side:** Shows existing entry with same phone
   - **Reason Field (Required):** Explain why duplicate is legitimate

4. **Example Valid Reasons:**
   - "Same person works in multiple departments"
   - "Person transferred from Village A to Village B"
   - "Shared office phone for department"
   - "Person has dual roles"

5. **Submit for Admin Review:**
   - Your entry goes to **Pending** status
   - Tagged as "Duplicate Exception Request"
   - Admin reviews both entries side-by-side
   - Admin decides: Approve or Reject

### Best Practices
✅ **DO:**
- Provide clear, specific reasons
- Verify the person is truly the same/different
- Contact existing submitter if possible

❌ **DON'T:**
- Submit without valid reason
- Request exceptions for data entry errors
- Abuse the system

---

## My Profile

### Access
Click **"My Profile"** or visit `/profile`

### What You Can Update
- ✏️ **Full Name:** Change your display name
- ✏️ **Phone Number:** Update contact
- 🔒 **Password:** Change login password
- 👁️ **View-Only Fields:**
  - Email (cannot change - used for login)
  - Role (Block Coordinator)
  - Primary Block
  - Assigned Blocks (contact admin to modify)
  - Account Status
  - Member Since date
  - Last Login

### Changing Password
1. Scroll to "Change Password" section
2. Enter **Current Password**
3. Enter **New Password** (minimum 8 characters)
4. Confirm **New Password**
5. Click **"Update Password"**
6. Success message appears

---

## Mobile Usage

### Hamburger Menu (≡)
On mobile devices (phones/tablets), tap the **hamburger icon (≡)** in top-left to access:
- 🔍 **Search Villages** - Find villages/blocks
- 🏞️ **Blocks (7)** - Navigate to specific blocks
- 🌿 **Heat Map Overlays** - Toggle data layers
- 👤 **Account Menu:**
  - My Dashboard
  - Add Field Worker
  - My Profile
  - Admin Panel (if applicable)

### Responsive Features
- **Phone Portrait (< 480px):** Single-column layout, large touch targets
- **Phone Landscape (481-767px):** Optimized horizontal layout
- **Tablet (768-1023px):** Two-column forms, collapsible sidebars
- **Desktop (1024px+):** Full sidebar, multi-column layouts

### Touch Gestures on Map
- **Pinch:** Zoom in/out
- **Double Tap:** Zoom to location
- **Drag:** Pan around map
- **Tap Village:** View Field Workers with click-to-call contacts

---

## FAQs

### Q1: How long does approval take?
**A:** Typically 24-48 hours. Admin reviews all submissions manually.

### Q2: Can I edit approved entries?
**A:** No. Once approved, only admins can edit. Contact admin for corrections.

### Q3: What if I forget my password?
**A:** Contact system administrator at admin@dpworks.in for password reset.

### Q4: Can I submit for multiple blocks?
**A:** Yes, if admin assigns you multiple blocks. Check "My Profile" → "Assigned Blocks"

### Q5: Why was my submission rejected?
**A:** Check rejection reason in "My Submissions". Common reasons:
- Incorrect/incomplete data
- Duplicate without valid reason
- Village not in your assigned blocks
- Invalid phone format

### Q6: Can I export Field Worker data?
**A:** Admins can export CSV data. Coordinators can view all FW data on the map.

### Q7: How do I contact support?
**A:** Email: admin@dpworks.in | Include your email and block name in request

### Q8: What browsers are supported?
**A:** Modern browsers: Chrome, Firefox, Safari, Edge (latest 2 versions)

### Q9: Is my data secure?
**A:** Yes. All passwords are encrypted (bcrypt), sessions expire after 7 days, SQL injection protection enabled.

### Q10: Can I delete approved entries?
**A:** No. Only admins can delete. Contact admin if absolutely necessary.

---

## Contact & Support

**System Administrator:**  
📧 Email: admin@dpworks.in  
📞 Phone: [Contact admin for phone number]

**Office Hours:**  
Monday - Friday: 9:00 AM - 5:00 PM IST

**For Technical Issues:**  
Include in your email:
- Your registered email
- Block name
- Screenshot of error (if applicable)
- Browser and device type

---

**© 2025 DP Works | Bhadrak District Atlas**  
*Last Updated: October 29, 2025*
