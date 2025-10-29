# 🏥 Emergency Services Inventory - Implementation Plan
## DP Works - Bhadrak | Replacing "Doctors" Page

**Date:** October 29, 2025  
**Status:** Planning Phase  
**Target:** Replace current `/doctors` page with comprehensive emergency services directory

---

## 🎯 VISION

Transform the basic "doctors" page into a **comprehensive emergency services inventory** covering all critical services across Bhadrak district's 1,315 villages.

**Key Principle:** When someone needs help, they should find it instantly.

---

## 📋 SERVICE CATEGORIES

### 1. 🏥 Medical Services
- **Hospitals** (Government & Private)
- **Primary Health Centers (PHCs)**
- **Community Health Centers (CHCs)**
- **Sub-Centers**
- **Private Clinics**
- **Ambulance Services** (108, private)
- **Blood Banks**
- **Pharmacies** (24x7 marked separately)
- **Diagnostic Labs**

### 2. 👨‍⚕️ Medical Specialists
- **Doctors by Specialization:**
  - General Physicians
  - Pediatricians
  - Gynecologists
  - Orthopedics
  - Cardiologists
  - Dermatologists
  - Ophthalmologists
  - Dentists
  - ENT Specialists
  - Surgeons
  
- **Availability Tracking:**
  - Regular hours
  - Emergency availability
  - On-call services
  - Hospital affiliations

### 3. 🚨 Emergency Responders
- **Police Stations**
  - Station House (SHO contact)
  - Control room numbers
  - Women's helpline
  - Cyber crime cell
  
- **Fire Services**
  - Fire stations
  - Fire officer contacts
  - Equipment availability
  
- **Disaster Management**
  - Block Disaster Management Officers
  - Emergency response teams
  - Flood rescue teams
  - Cyclone shelters

### 4. 🔧 Essential Utilities
- **Electricity**
  - TPCODL emergency (Bhadrak division)
  - Section office contacts
  - Lineman numbers
  
- **Water Supply**
  - PHE emergency numbers
  - Water tanker services
  - Pump house contacts
  
- **Road Maintenance**
  - PWD emergency
  - Block roads contacts
  
- **Telecommunications**
  - BSNL fault reporting
  - Airtel/Jio/Vi service centers

### 5. 🏛️ Government Services
- **Block Development Offices**
- **Tehsil Offices**
- **Revenue Inspector Offices**
- **Village Resource Centers (VRCs)**
- **Ration Shops (PDS)**

### 6. 🆘 Helplines
- **National Helplines:**
  - 108 - Ambulance
  - 102 - Medical helpline
  - 112 - All emergencies
  - 1091 - Women's helpline
  - 1098 - Child helpline
  - 1800-180-1111 - Senior citizen helpline
  
- **State Helplines:**
  - Odisha COVID helpline
  - Odisha Disaster helpline
  - CM's grievance cell

---

## 💾 DATABASE SCHEMA

### Main Table: `emergency_services`
```sql
CREATE TABLE emergency_services (
    id SERIAL PRIMARY KEY,
    
    -- Basic Info
    service_name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL, -- medical, police, fire, utilities, govt
    service_type VARCHAR(100) NOT NULL, -- hospital, phc, police_station, etc
    
    -- Location
    village_id INT REFERENCES villages(id),
    block_name VARCHAR(100),
    address TEXT,
    landmark TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Contact
    primary_contact VARCHAR(15) NOT NULL,
    alternate_contact VARCHAR(15),
    emergency_contact VARCHAR(15),
    email VARCHAR(100),
    website VARCHAR(200),
    
    -- Operating Details
    operating_hours VARCHAR(100), -- "24x7", "9AM-6PM Mon-Sat", etc
    emergency_available BOOLEAN DEFAULT false,
    days_closed TEXT, -- "Sundays", "2nd Saturday", etc
    
    -- Medical Specific
    has_ambulance BOOLEAN DEFAULT false,
    ambulance_contact VARCHAR(15),
    has_emergency_ward BOOLEAN DEFAULT false,
    has_icu BOOLEAN DEFAULT false,
    bed_capacity INT,
    specializations TEXT[], -- Array: ["Cardiology", "Orthopedics"]
    
    -- Utilities Specific
    service_area TEXT, -- Which villages covered
    response_time_minutes INT, -- Average response time
    
    -- Metadata
    verified_at TIMESTAMP,
    verified_by INT REFERENCES users(id),
    last_updated TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    created_by INT REFERENCES users(id)
);

CREATE INDEX idx_emergency_category ON emergency_services(category);
CREATE INDEX idx_emergency_village ON emergency_services(village_id);
CREATE INDEX idx_emergency_block ON emergency_services(block_name);
CREATE INDEX idx_emergency_type ON emergency_services(service_type);
CREATE INDEX idx_emergency_available ON emergency_services(emergency_available);
```

### Doctors/Specialists Table: `service_specialists`
```sql
CREATE TABLE service_specialists (
    id SERIAL PRIMARY KEY,
    service_id INT REFERENCES emergency_services(id) ON DELETE CASCADE,
    
    -- Doctor Info
    doctor_name VARCHAR(200) NOT NULL,
    specialization VARCHAR(100),
    qualification VARCHAR(200), -- "MBBS, MD", "BDS", etc
    registration_number VARCHAR(50), -- Medical council registration
    
    -- Availability
    available_days VARCHAR(100), -- "Mon-Fri", "Mon,Wed,Fri", "Daily"
    available_hours VARCHAR(100), -- "10AM-2PM, 6PM-9PM"
    emergency_available BOOLEAN DEFAULT false,
    on_call BOOLEAN DEFAULT false,
    
    -- Contact
    phone VARCHAR(15),
    emergency_phone VARCHAR(15),
    
    -- Languages
    languages_spoken TEXT[], -- ["Odia", "English", "Hindi"]
    
    -- Metadata
    years_experience INT,
    consultation_fee INT,
    accepts_emergency_cases BOOLEAN DEFAULT false,
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_specialist_service ON service_specialists(service_id);
CREATE INDEX idx_specialist_specialization ON service_specialists(specialization);
```

### Service Reviews/Ratings (Future)
```sql
CREATE TABLE service_reviews (
    id SERIAL PRIMARY KEY,
    service_id INT REFERENCES emergency_services(id),
    user_id INT REFERENCES users(id),
    rating INT CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    response_time_rating INT,
    quality_rating INT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🎨 UI/UX DESIGN

### Page: `/emergency-services`

#### Layout Structure:
```
┌─────────────────────────────────────────────────────────────┐
│  DP Works 📍 Bhadrak        [Map] [Doctors] [🔐 Login]       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  🆘 EMERGENCY SERVICES DIRECTORY                             │
│  Find critical services across 1,315 villages                │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 🔍 Search services, locations, doctors...             │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────┬─────────────────────────────────────┐  │
│  │  FILTERS        │  RESULTS (Map/List View Toggle)      │  │
│  │  ───────────    │  ──────────────────────────────      │  │
│  │  □ Medical      │  ┌───────────────────────────────┐  │  │
│  │  □ Police       │  │ 🏥 District Headquarters       │  │  │
│  │  □ Fire         │  │    Hospital                    │  │  │
│  │  □ Utilities    │  │    Bhandaripokhari             │  │  │
│  │  □ Govt         │  │    📞 06784-251600 (Emergency) │  │  │
│  │                 │  │    ⏰ 24x7  🚑 Ambulance       │  │  │
│  │  ── BY BLOCK    │  │    [📍 Navigate] [☎️ Call]     │  │  │
│  │  □ Bhadrak      │  └───────────────────────────────┘  │  │
│  │  □ Basudevpur   │                                      │  │
│  │  □ Bonth        │  ┌───────────────────────────────┐  │  │
│  │  □ Chandbali    │  │ 👮 Bhadrak Town Police        │  │  │
│  │  □ Dhamnagar    │  │    Station                     │  │  │
│  │  □ Tihidi       │  │    Bhadrak Municipality        │  │  │
│  │  □ Bhandaripokhari│ │    📞 06784-250100            │  │  │
│  │                 │  │    ⏰ 24x7                      │  │  │
│  │  ── QUICK       │  │    [📍 Navigate] [☎️ Call]     │  │  │
│  │  ☑ 24x7 Only    │  └───────────────────────────────┘  │  │
│  │  □ Has Ambulance│                                      │  │
│  │  □ Emergency    │  [Load More...]                      │  │
│  │    Ward         │                                      │  │
│  └─────────────────┴─────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

#### Service Card Design:
```html
<div class="service-card">
  <!-- Header with Icon -->
  <div class="service-header">
    <span class="service-icon">🏥</span>
    <div>
      <h3>District Headquarters Hospital</h3>
      <p class="location">📍 Bhandaripokhari, Bhadrak</p>
    </div>
    <span class="category-badge medical">Medical</span>
  </div>
  
  <!-- Quick Stats -->
  <div class="service-stats">
    <span class="stat">⏰ 24x7</span>
    <span class="stat">🚑 Ambulance</span>
    <span class="stat">🏥 ICU: 10 beds</span>
    <span class="stat">🩺 10 Specialists</span>
  </div>
  
  <!-- Contact Actions -->
  <div class="service-actions">
    <a href="tel:06784251600" class="btn-primary">
      ☎️ Call Emergency: 06784-251600
    </a>
    <a href="https://maps.google.com/?q=21.054,86.493" class="btn-secondary">
      📍 Get Directions
    </a>
    <button onclick="showDetails(123)" class="btn-secondary">
      ℹ️ More Details
    </button>
  </div>
</div>
```

#### Map View:
- **Color-coded pins:**
  - 🏥 Red - Medical
  - 👮 Blue - Police
  - 🚒 Orange - Fire
  - 🔧 Green - Utilities
  - 🏛️ Gray - Government
  
- **Pin Clusters:** Group nearby services
- **Info Window:** Click pin → Show service card
- **Route:** Click "Navigate" → Open Google Maps with directions

---

## 🔍 SEARCH FUNCTIONALITY

### Search Features:
1. **Fuzzy Search:** Typo-tolerant (Levenshtein distance)
2. **Multi-field:** Name, location, specialization, doctor name
3. **Autocomplete:** Suggest as user types
4. **Voice Search:** (Future) Use Web Speech API

### Search Query Examples:
- "cardiology bhadrak" → All cardiologists in Bhadrak
- "24x7 ambulance" → All 24x7 ambulance services
- "police chandbali" → Police stations in Chandbali
- "Dr. Mishra" → All doctors named Mishra
- "electricity emergency" → Power utility contacts

### Implementation (PostgreSQL Full-Text Search):
```sql
-- Add search vector column
ALTER TABLE emergency_services 
ADD COLUMN search_vector tsvector;

-- Update search vector
UPDATE emergency_services 
SET search_vector = to_tsvector('english',
    coalesce(service_name, '') || ' ' ||
    coalesce(address, '') || ' ' ||
    coalesce(category, '') || ' ' ||
    coalesce(service_type, '')
);

-- Create GIN index
CREATE INDEX idx_search_vector 
ON emergency_services 
USING GIN(search_vector);

-- Search query
SELECT * FROM emergency_services
WHERE search_vector @@ plainto_tsquery('english', 'cardiology bhadrak')
ORDER BY ts_rank(search_vector, plainto_tsquery('english', 'cardiology bhadrak')) DESC;
```

---

## 📱 MOBILE-FIRST FEATURES

### Quick Actions (Mobile):
1. **Emergency Banner:** 
   - Red sticky banner at top
   - "🆘 IN EMERGENCY? TAP HERE"
   - Quick links: 108, 112, Blood Bank, Nearest Hospital

2. **One-Tap Calling:**
   - All phone numbers are `tel:` links
   - Long-press to copy number
   
3. **Location-Based:**
   - "Find services near me" (Geolocation API)
   - Sort by distance
   - Show distance in km

4. **Offline Access:**
   - Service Worker caches critical contacts
   - Works without internet
   - "Last updated: X hours ago" indicator

### Responsive Breakpoints:
```css
/* Mobile First */
.service-grid {
    display: grid;
    grid-template-columns: 1fr; /* 320px+ */
}

@media (min-width: 640px) {
    .service-grid {
        grid-template-columns: repeat(2, 1fr); /* Tablet */
    }
}

@media (min-width: 1024px) {
    .service-grid {
        grid-template-columns: repeat(3, 1fr); /* Desktop */
    }
}
```

---

## 🔐 ADMIN FEATURES

### Admin Panel: `/admin/emergency-services`

#### Actions:
1. **Add New Service**
   - Multi-step form
   - Auto-geocode address
   - Upload photos (facility images)
   
2. **Edit Service**
   - Update contact numbers
   - Change operating hours
   - Mark inactive if closed

3. **Add Specialist**
   - Link doctor to service
   - Set availability schedule
   - Upload qualification certificates

4. **Bulk Import**
   - CSV upload
   - Template: Download sample CSV
   - Validate before import
   
5. **Verification**
   - Call service to verify
   - Mark "Verified" with date
   - Re-verify every 6 months

6. **Analytics**
   - Most searched services
   - Popular specializations
   - Coverage gaps (villages without services)

---

## 📊 DATA COLLECTION STRATEGY

### Phase 1: Government Data (Week 1)
- **Sources:**
  - District Health Department
  - Police Headquarters
  - Fire Services Office
  - TPCODL/Electricity Board
  - PWD Department
  
- **Method:**
  - Official RTI requests
  - District administration data
  - Public directories

### Phase 2: Field Verification (Weeks 2-3)
- **Coordinators:**
  - Each block coordinator verifies services in their block
  - Call and confirm phone numbers
  - Note operating hours
  - Check ambulance availability
  
- **Form:** `/verify-service/:id`
  - Checkbox: Service is active
  - Update contact if changed
  - Note any closures
  - Upload photos

### Phase 3: Community Contributions (Ongoing)
- **Public Form:** `/suggest-service`
  - Anyone can suggest missing service
  - Admin reviews and approves
  - Gamification: Credits for verified suggestions

---

## 🚀 IMPLEMENTATION ROADMAP

### Week 1: Database & API
- [ ] Create database tables
- [ ] Build API endpoints:
  - `GET /api/emergency-services` (search, filter)
  - `POST /api/emergency-services` (admin only)
  - `PUT /api/emergency-services/:id` (admin only)
  - `DELETE /api/emergency-services/:id` (admin only)
  - `GET /api/emergency-services/nearby` (geolocation)
  - `GET /api/specialists` (filter by specialization)

### Week 2: Frontend
- [ ] Design UI components
- [ ] Build search interface
- [ ] Implement map view
- [ ] Create service cards
- [ ] Mobile responsiveness

### Week 3: Admin Panel
- [ ] Add/edit service forms
- [ ] Bulk import functionality
- [ ] Specialist management
- [ ] Verification workflow

### Week 4: Data Collection
- [ ] Collect government data
- [ ] Field verification
- [ ] Import into database
- [ ] Quality assurance

### Week 5: Testing & Launch
- [ ] End-to-end testing
- [ ] Load testing (1000+ services)
- [ ] User acceptance testing
- [ ] Public launch
- [ ] Training for coordinators

---

## 🎯 SUCCESS METRICS

### Quantitative:
- **Coverage:** All 7 blocks have >90% critical services listed
- **Accuracy:** <5% incorrect phone numbers
- **Response:** Page loads in <2 seconds
- **Mobile:** 80%+ users on mobile
- **Usage:** 100+ searches per day

### Qualitative:
- **User Feedback:** 4+ stars average rating
- **Emergency Cases:** Stories of lives saved
- **Community Impact:** Reduced emergency response time

---

## 💡 INNOVATIVE FEATURES (Future)

### 1. Emergency Alert System
- Push notifications for:
  - Natural disasters (cyclones, floods)
  - Disease outbreaks
  - Blood donation camps
  - Health camps

### 2. Telemedicine Integration
- Video consultation links
- E-prescription support
- Follow-up reminders

### 3. Ambulance Tracking
- Real-time GPS tracking
- ETA to patient location
- Route optimization

### 4. Blood Donor Network
- Voluntary donor database
- Blood group search
- Emergency blood requests
- Donation history

### 5. Multilingual Support
- Odia (primary)
- Hindi
- English
- Voice navigation in local language

---

## 📞 SAMPLE DATA STRUCTURE

### Example Entry:
```json
{
  "id": 1,
  "service_name": "District Headquarters Hospital",
  "category": "medical",
  "service_type": "government_hospital",
  "village_id": 523,
  "block_name": "Bhadrak",
  "address": "Station Road, Bhandaripokhari",
  "landmark": "Near Railway Station",
  "latitude": 21.0545,
  "longitude": 86.4930,
  "primary_contact": "06784251600",
  "alternate_contact": "06784251601",
  "emergency_contact": "06784251602",
  "email": "dhh.bhadrak@nic.in",
  "operating_hours": "24x7",
  "emergency_available": true,
  "has_ambulance": true,
  "ambulance_contact": "108",
  "has_emergency_ward": true,
  "has_icu": true,
  "bed_capacity": 150,
  "specializations": [
    "Cardiology",
    "Orthopedics",
    "Gynecology",
    "Pediatrics",
    "General Surgery",
    "ENT",
    "Ophthalmology",
    "Dermatology"
  ],
  "verified_at": "2025-10-15T10:30:00Z",
  "verified_by": 2,
  "is_active": true,
  "notes": "Main referral hospital for Bhadrak district"
}
```

---

## 🎓 USER TRAINING

### For Coordinators:
- **Module 1:** Adding new services
- **Module 2:** Verifying existing data
- **Module 3:** Handling community suggestions
- **Module 4:** Emergency protocols

### For Public:
- **Tutorial:** "How to find emergency services"
- **Video:** 2-minute walkthrough
- **FAQs:** Common questions
- **Helpline:** Support number for assistance

---

## 📋 CONCLUSION

This Emergency Services Inventory will transform DP Works from a simple village map into a **life-saving platform** that connects people to critical services in emergencies.

**Core Philosophy:** When someone is in trouble, finding help should be the easiest thing in the world.

---

**Next Steps:**
1. Get user approval for this plan
2. Start with database schema
3. Begin data collection
4. Iterative development with user feedback

**Questions to Resolve:**
- Should we include private services or only government?
- What's the verification protocol for doctor credentials?
- Should we integrate with 108 ambulance tracking system?
- How often should data be refreshed?

---

**Document Prepared By:** Development Team  
**Date:** October 29, 2025  
**Status:** Awaiting Approval
