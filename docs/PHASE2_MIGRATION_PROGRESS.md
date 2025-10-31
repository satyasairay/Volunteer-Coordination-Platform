# Phase 2 Migration Progress Tracker

**Status:** In Progress  
**Started:** November 2025

---

## Migration Status by Template

### ✅ Completed Templates

1. **login.html** ✅
   - ✅ Design system CSS files included
   - ✅ Colors migrated to CSS variables
   - ✅ Buttons migrated to `.btn` components
   - ✅ Form inputs migrated to `.form-input`
   - ✅ Navigation updated to `.app-nav`
   - ✅ Spacing updated to use spacing utilities
   - ✅ Typography updated to use typography scale
   - **Notes:** Hamburger menu styles customized for design system

2. **register.html** ✅
   - ✅ Design system CSS files included
   - ✅ Colors migrated to CSS variables (purple gradient → `--gradient-primary`)
   - ✅ Buttons migrated to `.btn .btn-primary`
   - ✅ Form inputs migrated to `.form-input` and `.form-select`
   - ✅ Navigation updated to `.app-nav`
   - ✅ Spacing updated to use spacing utilities (8px grid)
   - ✅ Typography updated to use typography scale
   - ✅ Alert components use design system colors
   - **Notes:** Similar structure to login.html, all form fields migrated

3. **dashboard.html** ✅
   - ✅ Design system CSS files included
   - ✅ Colors migrated to CSS variables (purple gradient → `--gradient-primary`)
   - ✅ Glassmorphic cards migrated to `.card .card-glass` components
   - ✅ Buttons migrated to `.btn .btn-primary` and `.btn-secondary`
   - ✅ Navigation updated to `.app-nav`
   - ✅ Spacing updated to use spacing utilities (`mb-6`, `mb-4`)
   - ✅ Typography updated to use typography scale (h1, h2, p)
   - **Notes:** All content cards now use card component, buttons standardized

---

### 🔄 In Progress Templates

None currently

---

### ⏳ Pending Templates (In Order)

2. **index.html** - Base template, CSS variable-based (already partially migrated)
3. **dashboard.html** - Purple gradient, glassmorphic cards
4. **register.html** - Similar to login.html
5. **admin.html** - Plain gray, white nav
6. **admin_users.html** - Blue gradient header
7. **admin_field_workers.html** - Blue gradient header
8. **profile.html** - Multi-color gradient
9. **field_worker_new.html** - Mixed styles
10. **field_worker_submissions.html** - Glassmorphic cards
11. **admin_about.html** - Admin content editor
12. **admin_blocks.html** - Glassmorphic dark theme
13. **admin_villages.html** - Admin village management
14. **admin_analytics.html** - Analytics dashboard
15. **admin_duplicates.html** - Duplicate management
16. **admin_form_config.html** - Form configuration
17. **admin_map_settings.html** - Map settings
18. **about.html** - Public about page
19. **doctors.html** - Public doctors page
20. **doctors_admin.html** - Admin doctors page
21. **members.html** - Members page
22. **sample_village_choropleth.html** - Sample visualization

---

## Migration Checklist Template

For each template:

- [ ] 1. Include design system CSS files in `<head>`
- [ ] 2. Replace all hardcoded colors with CSS variables
- [ ] 3. Replace custom buttons with `.btn` component classes
- [ ] 4. Replace custom cards with `.card` component classes
- [ ] 5. Replace custom form inputs with `.form-input` component classes
- [ ] 6. Replace custom navigation with `.app-nav` component
- [ ] 7. Update spacing to use spacing utilities (8px grid)
- [ ] 8. Update typography to use typography scale
- [ ] 9. Include `components.js` before `</body>`
- [ ] 10. Test responsive behavior
- [ ] 11. Verify accessibility (contrast, touch targets)
- [ ] 12. Remove unused custom CSS

---

## Common Patterns Identified

### Purple Gradient Backgrounds
**Pattern:** `background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);`
**Replace with:** `background: var(--gradient-primary);` or `var(--gradient-purple);`

### Blue Gradient Headers
**Pattern:** `background: linear-gradient(to right, #2563eb, #1e40af);`
**Replace with:** `background: var(--gradient-blue);`

### Glassmorphic Cards
**Pattern:** `background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(20px);`
**Replace with:** Use `.card-card-glass` component

### Custom Buttons
**Pattern:** Various custom button styles
**Replace with:** `.btn .btn-primary`, `.btn .btn-secondary`, etc.

### Form Inputs
**Pattern:** Custom styled inputs with glassmorphic or Tailwind styles
**Replace with:** `.form-input` component

---

## Issues & Solutions

### Issue: Navigation hamburger button styling
**Solution:** Added custom styles for hamburger button while using `.app-nav-toggle` class

### Issue: Slide menu custom styling
**Solution:** Kept custom slide menu styles but migrated colors to CSS variables

---

## Next Steps

1. Continue with index.html (base template)
2. Then dashboard.html, register.html
3. Then admin pages
4. Then field worker pages
5. Finally public pages

---

**Last Updated:** After login.html migration

