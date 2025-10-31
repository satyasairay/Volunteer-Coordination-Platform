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

4. **index.html** ✅
   - ✅ Design system CSS files included
   - ✅ Navigation updated to `.app-nav` with `.app-nav-brand` and `.app-nav-toggle`
   - ✅ Colors migrated to CSS variables (footer gradient → `--gradient-primary`, map background → `--color-gray-*`)
   - ✅ Menu links migrated to use CSS variables (`--color-gray-50`, `--color-primary`, etc.)
   - ✅ Spacing updated to use spacing utilities (`var(--spacing-*)`)
   - ✅ Typography updated to use typography scale (`var(--text-*)`, `var(--font-weight-*)`)
   - ✅ Hamburger button migrated to `.app-nav-toggle` with custom styling
   - ✅ Reload button migrated to `.btn .btn-secondary`
   - ✅ Footer migrated to use design system variables
   - ✅ Components.js included
   - **Notes:** Complex map template with D3.js visualization. Theme switching preserved. Navigation and UI elements migrated while maintaining map functionality.

5. **admin.html** ✅
   - ✅ Design system CSS files included
   - ✅ Navigation migrated to custom `.admin-nav` (horizontal nav for admin panel)
   - ✅ Tailwind cards replaced with `.card` components
   - ✅ Tailwind buttons replaced with `.btn .btn-primary` and `.btn-success`
   - ✅ Tailwind form inputs replaced with `.form-input`
   - ✅ Colors migrated to CSS variables (`var(--color-primary)`, `var(--color-success)`, etc.)
   - ✅ Spacing updated to use spacing utilities (`var(--spacing-*)`)
   - ✅ Typography updated to use typography scale
   - ✅ Components.js included
   - **Notes:** Admin dashboard with bulk upload forms. All Tailwind utility classes replaced with design system components. Inline styles for dynamic content use CSS variables.

6. **admin_users.html** ✅
   - ✅ Design system CSS files included
   - ✅ Blue gradient header migrated to `var(--gradient-blue)`
   - ✅ Tailwind cards replaced with `.card` components and custom stats cards
   - ✅ Tailwind buttons replaced with `.btn` components (success, danger, primary, secondary, warning)
   - ✅ Tailwind form inputs replaced with `.form-input`, `.form-select`, `.form-textarea`
   - ✅ Modals migrated to `.modal`, `.modal-backdrop`, `.modal-header`, `.modal-body`, `.modal-footer`
   - ✅ Colors migrated to CSS variables (status badges, alert boxes, stats cards)
   - ✅ Spacing updated to use spacing utilities
   - ✅ Typography updated to use typography scale
   - ✅ Status badges use design system color variables
   - ✅ Components.js included
   - **Notes:** Complex admin user management page with dynamic user cards, modals, and filtering. All Tailwind classes replaced with design system components. JavaScript-generated HTML uses CSS variables.

7. **admin_field_workers.html** ✅
   - ✅ Design system CSS files included
   - ✅ Blue gradient header migrated to `var(--gradient-blue)`
   - ✅ Tailwind cards replaced with `.card` components and custom stats cards
   - ✅ Tailwind buttons replaced with `.btn` components (success, danger, secondary)
   - ✅ Tailwind form inputs replaced with `.form-input`, `.form-select`, `.form-textarea`
   - ✅ Modals migrated to `.modal` component structure
   - ✅ Colors migrated to CSS variables (status badges, alert boxes, stats cards)
   - ✅ Spacing updated to use spacing utilities
   - ✅ Typography updated to use typography scale
   - ✅ Status badges and alert boxes use design system color variables
   - ✅ Components.js included
   - **Notes:** Field worker approval page with similar structure to admin_users.html. Dynamic submission cards use CSS variables. All Tailwind replaced with design system.

8. **profile.html** ✅
   - ✅ Design system CSS files included
   - ✅ Multi-color gradient background migrated to CSS variables (`var(--color-success-light)`, `var(--color-info-light)`, `var(--color-purple-light)`)
   - ✅ Profile card header gradient migrated to `var(--color-indigo)`, `var(--color-purple)`
   - ✅ Tailwind cards replaced with `.card` component
   - ✅ Tailwind buttons replaced with `.btn .btn-primary`, `.btn-success`
   - ✅ Tailwind form inputs replaced with `.form-input` component
   - ✅ Colors migrated to CSS variables (disabled inputs, status badges, block tags)
   - ✅ Spacing updated to use spacing utilities
   - ✅ Typography updated to use typography scale
   - ✅ Danger zone uses design system danger colors
   - ✅ Components.js included
   - **Notes:** User profile page with form inputs, password change, and danger zone. Multi-color gradient preserved using design system variables. All Tailwind replaced.

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

