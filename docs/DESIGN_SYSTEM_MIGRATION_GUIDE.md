# Design System Migration Guide
## Template-by-Template Color System Unification

**Version:** 1.0  
**Date:** November 2025  
**Purpose:** Systematic guide for migrating all templates to the unified design system

---

## Migration Overview

This guide provides step-by-step instructions for migrating each template from hardcoded styles to the unified design system using CSS variables and component classes.

### Migration Checklist Per Template

For each template, complete these steps:

- [ ] 1. Include design system CSS files
- [ ] 2. Replace hardcoded colors with CSS variables
- [ ] 3. Replace custom buttons with `.btn` component classes
- [ ] 4. Replace custom cards with `.card` component classes
- [ ] 5. Replace custom form inputs with `.form-input` component classes
- [ ] 6. Replace custom navigation with `.app-nav` component
- [ ] 7. Update spacing to use spacing utilities
- [ ] 8. Update typography to use typography utilities
- [ ] 9. Test responsive behavior
- [ ] 10. Verify accessibility (contrast, touch targets)

---

## Step 1: Include Design System Files

At the top of each template's `<head>` section, add:

```html
<!-- Design System -->
<link rel="stylesheet" href="/static/css/theme.css">
<link rel="stylesheet" href="/static/css/typography.css">
<link rel="stylesheet" href="/static/css/components.css">
<link rel="stylesheet" href="/static/css/utilities.css">
```

Before the closing `</body>` tag, add:

```html
<!-- Design System Components -->
<script src="/static/js/components.js"></script>
```

---

## Step 2: Color Migration Patterns

### Purple Gradient → Primary Gradient

**Before:**
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

**After:**
```css
background: var(--gradient-primary);
/* OR for legacy purple if needed */
background: var(--gradient-purple);
```

### Blue Gradient → Info/Blue Gradient

**Before:**
```css
background: linear-gradient(to right, #2563eb, #1e40af);
```

**After:**
```css
background: var(--gradient-blue);
```

### Hardcoded Colors → CSS Variables

**Before:**
```css
color: #4338ca;
background: #f3f4f6;
border: 1px solid #d1d5db;
```

**After:**
```css
color: var(--color-primary);
background: var(--color-gray-100);
border: 1px solid var(--color-border-medium);
```

---

## Step 3: Button Migration

### Custom CSS Buttons

**Before:**
```html
<button class="btn-primary" style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); border-radius: 10px; padding: 0.75rem 1.5rem;">
  Click Me
</button>
```

**After:**
```html
<button class="btn btn-primary">Click Me</button>
```

### Tailwind Utility Buttons

**Before:**
```html
<button class="bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
  Click Me
</button>
```

**After:**
```html
<button class="btn btn-primary">Click Me</button>
```

### Inline Style Buttons

**Before:**
```html
<button style="cursor: pointer; border: 3px solid #3b82f6; padding: 8px 16px;">
  Click Me
</button>
```

**After:**
```html
<button class="btn btn-secondary">Click Me</button>
```

### Button Variants Mapping

- Primary actions → `btn btn-primary`
- Secondary actions → `btn btn-secondary`
- Success actions → `btn btn-success`
- Delete/danger → `btn btn-danger`
- Info/informational → `btn btn-info`
- Subtle/ghost → `btn btn-ghost`

---

## Step 4: Card Migration

### Glassmorphic Cards

**Before:**
```html
<div style="background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 20px; padding: 24px;">
  Content
</div>
```

**After:**
```html
<div class="card card-glass">
  <div class="card-body">Content</div>
</div>
```

### Plain White Cards

**Before:**
```html
<div class="bg-white rounded-xl shadow-md p-6">
  Content
</div>
```

**After:**
```html
<div class="card">
  <div class="card-body">Content</div>
</div>
```

### Tailwind Cards

**Before:**
```html
<div class="bg-white rounded-2xl shadow-xl p-8">
  <h2 class="text-2xl font-bold mb-4">Title</h2>
  <p>Content</p>
</div>
```

**After:**
```html
<div class="card">
  <div class="card-header">
    <h2 class="card-title">Title</h2>
  </div>
  <div class="card-body">
    <p>Content</p>
  </div>
</div>
```

---

## Step 5: Form Input Migration

### Glassmorphic Inputs

**Before:**
```html
<input style="background: rgba(255, 255, 255, 0.8); border: 1px solid rgba(30, 41, 59, 0.2); border-radius: 10px; padding: 0.75rem 1rem;">
```

**After:**
```html
<input class="form-input">
```

### Tailwind Inputs

**Before:**
```html
<input class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
```

**After:**
```html
<input class="form-input">
```

### Form Structure

**Before:**
```html
<div>
  <label>Email</label>
  <input type="email">
</div>
```

**After:**
```html
<div class="mb-4">
  <label class="form-label required">Email</label>
  <input type="email" class="form-input">
</div>
```

---

## Step 6: Navigation Migration

### Glassmorphic Purple Nav

**Before:**
```html
<nav style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 68px;">
  <div>Brand</div>
  <div>Menu Items</div>
  <button>☰</button>
</nav>
```

**After:**
```html
<nav class="app-nav">
  <a href="/" class="app-nav-brand">Brand</a>
  <div class="app-nav-menu">
    <a href="/link1" class="app-nav-link">Item 1</a>
    <a href="/link2" class="app-nav-link">Item 2</a>
  </div>
  <button class="app-nav-toggle">☰</button>
</nav>
```

### Plain White Nav

**Before:**
```html
<nav class="bg-white shadow-sm h-16">
  <div>Brand</div>
  <div>Links</div>
</nav>
```

**After:**
```html
<nav class="app-nav">
  <a href="/" class="app-nav-brand">Brand</a>
  <div class="app-nav-menu">
    <a href="/link1" class="app-nav-link">Item 1</a>
  </div>
</nav>
```

---

## Step 7: Spacing Migration

### Hardcoded Padding/Margin

**Before:**
```html
<div style="padding: 24px; margin-bottom: 16px;">
```

**After:**
```html
<div class="p-6 mb-4">
```

### Spacing Mapping

- `padding: 24px` → `p-6`
- `margin-bottom: 16px` → `mb-4`
- `gap: 12px` → `gap-3`
- `padding: 0.75rem 1.5rem` → `py-3 px-6`

---

## Step 8: Typography Migration

### Font Families

**Before:**
```css
font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
```

**After:**
```css
/* Already handled by body in typography.css */
/* Or use: */
font-family: var(--font-family-primary);
```

### Font Sizes

**Before:**
```html
<h1 style="font-size: 2rem;">Title</h1>
<p style="font-size: 0.95rem;">Text</p>
```

**After:**
```html
<h1>Title</h1>
<p class="text-sm">Text</p>
```

### Font Weights

**Before:**
```css
font-weight: 600;
```

**After:**
```css
font-weight: var(--font-weight-semibold);
/* OR use class: */
.font-semibold
```

---

## Template-Specific Migration Notes

### 1. index.html
- **Current:** CSS variable-based theme system (already good base)
- **Changes:** Ensure all colors use variables, update buttons/cards

### 2. login.html
- **Current:** Purple gradient background, glassmorphic inputs
- **Changes:** Replace gradient with `--gradient-primary`, use `.form-input`, use `.btn` buttons

### 3. dashboard.html
- **Current:** Purple gradient, glassmorphic cards
- **Changes:** Use `.card-glass` for cards, update navigation

### 4. register.html
- **Current:** Similar to login.html
- **Changes:** Same as login.html

### 5. admin.html
- **Current:** Plain gray background, white nav
- **Changes:** Use `.app-nav`, update cards to `.card`, update buttons

### 6. admin_users.html
- **Current:** Blue gradient header
- **Changes:** Use `.app-nav`, replace blue gradient with CSS variables, update cards/buttons

### 7. admin_field_workers.html
- **Current:** Blue gradient header (similar to admin_users.html)
- **Changes:** Same as admin_users.html

### 8. profile.html
- **Current:** Multi-color gradient background
- **Changes:** Use CSS variables for gradients, update cards/forms

### 9. field_worker_new.html
- **Current:** Mixed styles
- **Changes:** Use `.form-input`, `.btn`, `.card` components

### 10. field_worker_submissions.html
- **Current:** Glassmorphic cards
- **Changes:** Use `.card-glass` component

---

## Testing Checklist

After migrating each template:

- [ ] Visual appearance matches original (or improved)
- [ ] Colors are consistent with design system
- [ ] Buttons work correctly
- [ ] Forms are accessible and styled correctly
- [ ] Navigation works on mobile (hamburger menu)
- [ ] Cards display properly
- [ ] No console errors
- [ ] Responsive breakpoints work
- [ ] Touch targets are 44px minimum
- [ ] Focus states visible

---

## Common Issues & Solutions

### Issue: Colors look different
**Solution:** Check that CSS variables are loaded before custom styles

### Issue: Buttons not styled
**Solution:** Ensure `.btn` class is applied, check CSS file order

### Issue: Navigation hamburger not working
**Solution:** Ensure `components.js` is loaded, check console for errors

### Issue: Cards not showing glassmorphic effect
**Solution:** Ensure `.card-glass` is used on gradient backgrounds only

### Issue: Form inputs not styled
**Solution:** Use `.form-input` class, ensure CSS files are loaded

---

## Migration Order (Recommended)

1. **Phase 1: Core Pages**
   - index.html (base template)
   - login.html
   - dashboard.html

2. **Phase 2: Registration & Profile**
   - register.html
   - profile.html

3. **Phase 3: Admin Pages**
   - admin.html (admin dashboard)
   - admin_users.html
   - admin_field_workers.html
   - admin_about.html
   - admin_blocks.html
   - admin_villages.html
   - admin_analytics.html
   - admin_duplicates.html
   - admin_form_config.html
   - admin_map_settings.html

4. **Phase 4: Field Worker Pages**
   - field_worker_new.html
   - field_worker_submissions.html

5. **Phase 5: Public Pages**
   - about.html
   - doctors.html
   - doctors_admin.html
   - members.html
   - sample_village_choropleth.html

---

## Post-Migration

After all templates are migrated:

1. Remove unused custom CSS from templates
2. Verify all pages load design system CSS
3. Run accessibility audit
4. Test on multiple browsers
5. Update documentation
6. Mark migration as complete

---

**Last Updated:** November 2025  
**Version:** 1.0

