# Priority 2b: Village Search Feature (Google-like)

**Status:** Planning Phase  
**Created:** October 29, 2025  
**Estimated Effort:** 4-6 hours  
**Priority:** High

---

## 🎯 Objective

Add a Google-like search box that allows users to:
1. Search for villages by name
2. Auto-complete suggestions as they type
3. Click a result to zoom/focus on that village on the map
4. Works on mobile and desktop
5. Matches the modern 2025 purple gradient aesthetic

---

## 📋 Requirements

### Functional Requirements

1. **Search Input**
   - Floating search box positioned at top-center of map (below navigation)
   - Placeholder text: "Search 1,315 villages..." 
   - Icon: 🔍 magnifying glass
   - Minimum 3 characters to trigger search
   - Clear button (×) when text is present

2. **Auto-Complete Dropdown**
   - Shows up to 10 matching villages
   - Displays: Village name, Block name, Population
   - Highlights matching text
   - Keyboard navigation (↑↓ arrows, Enter to select, Esc to close)
   - Click outside to close

3. **Search Results Action**
   - When user selects a village:
     - Zoom to village on map
     - Highlight village polygon
     - Show village modal with details
     - Close search dropdown

4. **Responsive Design**
   - Desktop: 500px wide search box
   - Mobile: Full width minus padding (16px each side)
   - Touch-friendly (44px min height)

### Technical Requirements

1. **Data Source**
   - Use existing `/api/villages/pins` endpoint (contains all village names, blocks, lat/lon)
   - Client-side filtering (faster than server calls)
   - Cache data on first load

2. **Search Algorithm**
   - Case-insensitive
   - Match village name OR block name
   - Fuzzy matching (optional: use Fuse.js library)
   - Sort by relevance: exact match > starts with > contains

3. **Performance**
   - Search results appear within 50ms
   - Debounce input (300ms)
   - No lag on mobile devices

---

## 🎨 Design Specification

### Search Box Style
```css
- Position: fixed, top: 80px (below nav), left: 50%, transform: translateX(-50%)
- Width: 500px (desktop), calc(100% - 32px) (mobile)
- Height: 56px
- Background: rgba(255, 255, 255, 0.95)
- Backdrop-filter: blur(12px)
- Border-radius: 28px
- Box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2)
- Border: 2px solid transparent
- Focus: border-color: #667eea
- Z-index: 1000
```

### Dropdown Style
```css
- Position: absolute, top: 64px
- Width: 100% (match search box)
- Max-height: 400px
- Background: white
- Border-radius: 16px
- Box-shadow: 0 12px 48px rgba(0,0,0,0.15)
- Overflow-y: auto
```

### Result Item Style
```css
- Padding: 12px 16px
- Border-bottom: 1px solid #f0f0f0
- Hover: background: linear-gradient(135deg, #f8f9ff 0%, #fff 100%)
- Cursor: pointer
- Font: 15px / 1.5
- Village name: font-weight: 600, color: #1a1a1a
- Block name: font-size: 13px, color: #666
- Population: font-size: 13px, color: #999
```

---

## 🛠️ Implementation Plan

### Step 1: HTML Structure (30 minutes)

Add search component to `templates/index.html` after navigation:

```html
<div id="search-container" class="search-container">
    <div class="search-box">
        <span class="search-icon">🔍</span>
        <input 
            type="text" 
            id="villageSearch" 
            placeholder="Search 1,315 villages..."
            autocomplete="off"
        />
        <button id="clearSearch" class="clear-btn" style="display: none;">×</button>
    </div>
    <div id="searchResults" class="search-results" style="display: none;">
        <!-- Results populated by JavaScript -->
    </div>
</div>
```

### Step 2: CSS Styling (45 minutes)

Add styles to `<style>` section in `index.html`:
- `.search-container` - positioning and z-index
- `.search-box` - glassmorphism effect
- `.search-results` - dropdown styling
- `.search-result-item` - individual result styling
- Media queries for mobile responsiveness
- Hover and focus states

### Step 3: JavaScript Logic (2-3 hours)

Add to `<script>` section:

```javascript
// 1. Load and cache village data
let villagesData = [];

async function loadVillagesData() {
    const response = await fetch('/api/villages/pins');
    villagesData = await response.json();
}

// 2. Search function with debouncing
let searchTimeout;
function handleSearch(query) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        if (query.length < 3) {
            hideSearchResults();
            return;
        }
        
        const results = searchVillages(query);
        displaySearchResults(results);
    }, 300);
}

// 3. Search algorithm
function searchVillages(query) {
    const lowerQuery = query.toLowerCase();
    
    return villagesData
        .filter(v => 
            v.name.toLowerCase().includes(lowerQuery) ||
            v.block.toLowerCase().includes(lowerQuery)
        )
        .sort((a, b) => {
            // Exact match first
            const aExact = a.name.toLowerCase() === lowerQuery;
            const bExact = b.name.toLowerCase() === lowerQuery;
            if (aExact && !bExact) return -1;
            if (!aExact && bExact) return 1;
            
            // Starts with second
            const aStarts = a.name.toLowerCase().startsWith(lowerQuery);
            const bStarts = b.name.toLowerCase().startsWith(lowerQuery);
            if (aStarts && !bStarts) return -1;
            if (!aStarts && bStarts) return 1;
            
            // Alphabetical
            return a.name.localeCompare(b.name);
        })
        .slice(0, 10); // Top 10 results
}

// 4. Display results
function displaySearchResults(results) {
    const container = document.getElementById('searchResults');
    
    if (results.length === 0) {
        container.innerHTML = '<div class="no-results">No villages found</div>';
        container.style.display = 'block';
        return;
    }
    
    container.innerHTML = results.map(v => `
        <div class="search-result-item" onclick="selectVillage('${v.name}')">
            <div class="result-name">${highlightMatch(v.name, query)}</div>
            <div class="result-meta">
                <span>📍 ${v.block}</span>
                ${v.population ? `<span>👥 ${v.population.toLocaleString()}</span>` : ''}
            </div>
        </div>
    `).join('');
    
    container.style.display = 'block';
}

// 5. Highlight matching text
function highlightMatch(text, query) {
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
}

// 6. Select village and zoom
function selectVillage(villageName) {
    hideSearchResults();
    
    // Find village polygon on map
    const villageElement = d3.selectAll('.village-polygon')
        .filter(d => d.properties.name === villageName);
    
    if (!villageElement.empty()) {
        // Zoom to village
        const bounds = villageElement.node().getBBox();
        const dx = bounds.width;
        const dy = bounds.height;
        const x = bounds.x + dx / 2;
        const y = bounds.y + dy / 2;
        const scale = 0.9 / Math.max(dx / width, dy / height);
        const translate = [width / 2 - scale * x, height / 2 - scale * y];
        
        svg.transition()
            .duration(750)
            .call(zoom.transform, d3.zoomIdentity
                .translate(translate[0], translate[1])
                .scale(scale));
        
        // Show village modal
        setTimeout(() => {
            showVillageDetails(villageElement.datum());
        }, 800);
    }
}

// 7. Event listeners
document.getElementById('villageSearch').addEventListener('input', (e) => {
    const query = e.target.value.trim();
    document.getElementById('clearSearch').style.display = query ? 'block' : 'none';
    handleSearch(query);
});

document.getElementById('clearSearch').addEventListener('click', () => {
    document.getElementById('villageSearch').value = '';
    document.getElementById('clearSearch').style.display = 'none';
    hideSearchResults();
});

// Hide results when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-container')) {
        hideSearchResults();
    }
});

// Keyboard navigation (↑↓ Enter Esc)
document.getElementById('villageSearch').addEventListener('keydown', (e) => {
    // TODO: Implement keyboard navigation
});
```

### Step 4: Integration (30 minutes)

1. Call `loadVillagesData()` on page load
2. Test search on desktop and mobile
3. Verify zoom and modal functionality
4. Check performance with 1,315 villages

### Step 5: QA Testing (1 hour)

Test scenarios:
- [ ] Search for "Bhadrak" (common name)
- [ ] Search for "xyz" (no results)
- [ ] Search with 1 character (no results shown)
- [ ] Search with 3+ characters (results appear)
- [ ] Click result → map zooms → modal opens
- [ ] Clear button works
- [ ] Click outside closes dropdown
- [ ] Mobile responsive (test on phone)
- [ ] Keyboard navigation works
- [ ] No performance lag

---

## 📊 Database / API Changes

**None required** - Uses existing `/api/villages/pins` endpoint.

---

## 🚀 Future Enhancements (Optional)

1. **Advanced Fuzzy Search** - Use Fuse.js library for better typo tolerance
2. **Recent Searches** - Remember last 5 searches in localStorage
3. **Popular Villages** - Show trending/most searched villages
4. **Block Filter** - Dropdown to filter by block
5. **Voice Search** - Add microphone icon for speech input
6. **Search History** - Track searches in database for analytics

---

## ✅ Definition of Done

- [ ] Search box visible on map page
- [ ] Auto-complete works with 3+ characters
- [ ] Top 10 results displayed
- [ ] Click result zooms to village and opens modal
- [ ] Mobile responsive
- [ ] No performance issues
- [ ] Matches purple gradient theme
- [ ] User tested and approved
