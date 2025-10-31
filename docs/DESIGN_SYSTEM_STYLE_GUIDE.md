# Design System Style Guide
## DP Works - Bhadrak District Mapping System

**Version:** 1.0  
**Last Updated:** November 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Design Tokens](#design-tokens)
3. [Components](#components)
4. [Typography](#typography)
5. [Spacing](#spacing)
6. [Usage Guidelines](#usage-guidelines)
7. [Migration Guide](#migration-guide)

---

## Overview

This design system provides a unified visual language for the DP Works application. All UI components, colors, typography, and spacing should use the design tokens and components defined in this system.

### File Structure

```
static/
├── css/
│   ├── theme.css          # CSS variables and design tokens
│   ├── components.css     # Reusable UI components
│   ├── typography.css     # Font system and text styles
│   └── utilities.css      # Common utility classes
└── js/
    └── components.js      # Reusable JavaScript components
```

### Including the Design System

In your HTML templates, include all design system files in this order:

```html
<link rel="stylesheet" href="/static/css/theme.css">
<link rel="stylesheet" href="/static/css/typography.css">
<link rel="stylesheet" href="/static/css/components.css">
<link rel="stylesheet" href="/static/css/utilities.css">
<script src="/static/js/components.js"></script>
```

---

## Design Tokens

### Colors

#### Primary Brand Colors
- **Primary:** `#4338ca` (Indigo) - Main brand color
- **Primary Dark:** `#312e81` - Darker variant
- **Primary Light:** `#6366f1` - Lighter variant

**Usage:** Use for primary actions, links, and brand elements.

```css
background: var(--color-primary);
color: var(--color-primary-dark);
```

#### Semantic Colors

- **Success:** `#10b981` (Green) - Success states, confirmations
- **Warning:** `#f59e0b` (Amber) - Warnings, cautions
- **Error:** `#ef4444` (Red) - Errors, destructive actions
- **Info:** `#3b82f6` (Blue) - Informational messages

**Usage:** Use for status indicators, alerts, and feedback messages.

```css
/* Example */
.alert-success {
  background: var(--color-success-bg);
  color: var(--color-success-dark);
}
```

#### Neutral Colors (Gray Scale)

Use gray scale for text, backgrounds, and borders:
- `--color-gray-50` to `--color-gray-900`
- `--color-text-primary` - Main text color
- `--color-text-secondary` - Secondary text
- `--color-bg-primary` - Main background (white)
- `--color-bg-secondary` - Secondary background

---

## Components

### Buttons

#### Basic Usage

```html
<button class="btn btn-primary">Primary Button</button>
<button class="btn btn-secondary">Secondary Button</button>
<button class="btn btn-success">Success</button>
<button class="btn btn-danger">Delete</button>
```

#### Button Sizes

```html
<button class="btn btn-primary btn-sm">Small</button>
<button class="btn btn-primary">Default</button>
<button class="btn btn-primary btn-lg">Large</button>
```

#### Button Variants

- `btn-primary` - Primary action (gradient background)
- `btn-secondary` - Secondary action (outlined)
- `btn-success` - Success actions
- `btn-danger` - Destructive actions
- `btn-info` - Informational actions
- `btn-ghost` - Subtle, minimal style

**Guidelines:**
- Use primary buttons for main actions (max one per page/section)
- Use secondary buttons for alternative actions
- Use danger buttons for destructive actions
- All buttons have minimum 44px height for touch targets (WCAG)

---

### Cards

#### Basic Card

```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Card Title</h3>
  </div>
  <div class="card-body">
    <p>Card content goes here.</p>
  </div>
  <div class="card-footer">
    <button class="btn btn-primary">Action</button>
  </div>
</div>
```

#### Glassmorphic Card

Use for cards on gradient backgrounds:

```html
<div class="card card-glass">
  <div class="card-body">
    Glassmorphic content
  </div>
</div>
```

**Guidelines:**
- Use standard cards for white backgrounds
- Use glassmorphic cards for gradient/colored backgrounds
- Always include padding (handled by `.card` class)

---

### Form Inputs

#### Basic Input

```html
<label class="form-label required">Email</label>
<input type="email" class="form-input" placeholder="Enter email">
<span class="form-error">Error message</span>
```

#### Select

```html
<label class="form-label">Role</label>
<select class="form-select">
  <option>Select role</option>
</select>
```

#### Textarea

```html
<label class="form-label">Message</label>
<textarea class="form-textarea" rows="4"></textarea>
```

**Guidelines:**
- Always pair inputs with labels
- Use `.required` class on labels for required fields
- Show `.form-error` for validation errors
- Use `.form-help` for helpful hints

---

### Navigation

#### Standard Navigation

```html
<nav class="app-nav">
  <a href="/" class="app-nav-brand">DP Works</a>
  <div class="app-nav-menu">
    <a href="/dashboard" class="app-nav-link">Dashboard</a>
    <a href="/profile" class="app-nav-link active">Profile</a>
  </div>
  <button class="app-nav-toggle">☰</button>
</nav>
```

**Guidelines:**
- Fixed height: 72px (`--nav-height`)
- Use `.active` class for current page
- Hamburger menu appears on mobile automatically
- Mobile menu slides in from right

---

### Modals

#### Basic Modal

```html
<div class="modal-backdrop" id="example-modal" style="display: none;">
  <div class="modal">
    <div class="modal-header">
      <h2 class="modal-title">Modal Title</h2>
      <button class="modal-close">&times;</button>
    </div>
    <div class="modal-body">
      Modal content
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary">Cancel</button>
      <button class="btn btn-primary">Confirm</button>
    </div>
  </div>
</div>
```

#### JavaScript Usage

```javascript
const modal = new Modal('example-modal');
modal.open();
modal.close();
modal.toggle();
```

**Modal Sizes:**
- Default: max-width 500px
- `modal-lg`: max-width 800px
- `modal-xl`: max-width 1200px

---

## Typography

### Headings

```html
<h1>Heading 1</h1>
<h2>Heading 2</h2>
<h3>Heading 3</h3>
<h4>Heading 4</h4>
<h5>Heading 5</h5>
<h6>Heading 6</h6>
```

### Text Sizes

```html
<p class="text-xs">Extra Small</p>
<p class="text-sm">Small</p>
<p class="text-base">Base (default)</p>
<p class="text-lg">Large</p>
<p class="text-xl">Extra Large</p>
<p class="text-2xl">2X Large</p>
```

### Font Weights

```html
<p class="font-light">Light</p>
<p class="font-normal">Normal</p>
<p class="font-medium">Medium</p>
<p class="font-semibold">Semibold</p>
<p class="font-bold">Bold</p>
```

**Guidelines:**
- Use headings in order (h1 → h2 → h3)
- Only one h1 per page
- Use font weights consistently (semibold for headings, normal for body)

---

## Spacing

### Spacing Scale (8px grid)

The design system uses an 8px grid system:

- `--spacing-1` = 4px
- `--spacing-2` = 8px
- `--spacing-3` = 12px
- `--spacing-4` = 16px
- `--spacing-6` = 24px
- `--spacing-8` = 32px

### Usage

```html
<!-- Margin -->
<div class="m-4">Margin all sides</div>
<div class="mt-4 mb-6">Different top/bottom</div>
<div class="mx-4">Horizontal margin</div>

<!-- Padding -->
<div class="p-6">Padding all sides</div>
<div class="px-4 py-6">Horizontal/vertical padding</div>

<!-- Gap (for flex/grid) -->
<div class="flex gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
</div>
```

**Guidelines:**
- Use spacing utilities instead of hardcoded values
- Stick to the 8px grid (use spacing variables)
- Use consistent spacing within components

---

## Usage Guidelines

### DO ✅

- Use CSS variables for all colors, spacing, and sizes
- Use component classes (`.btn`, `.card`, `.form-input`, etc.)
- Follow the spacing scale (8px grid)
- Maintain consistent typography hierarchy
- Use semantic HTML elements
- Ensure 44px minimum touch targets
- Test responsive behavior at breakpoints

### DON'T ❌

- Don't use hardcoded color values (hex codes, rgb)
- Don't create custom button/card styles (use variants)
- Don't use arbitrary spacing values
- Don't mix multiple design systems
- Don't use inline styles (except for dynamic values)
- Don't skip labels on form inputs
- Don't use font sizes smaller than 12px (accessibility)

---

## Migration Guide

### Replacing Hardcoded Colors

**Before:**
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
color: #312e81;
```

**After:**
```css
background: var(--gradient-primary);
color: var(--color-primary-dark);
```

### Replacing Custom Buttons

**Before:**
```html
<button style="background: #3b82f6; padding: 12px 24px; border-radius: 10px;">
  Click Me
</button>
```

**After:**
```html
<button class="btn btn-primary">Click Me</button>
```

### Replacing Custom Cards

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

### Replacing Custom Form Inputs

**Before:**
```html
<input class="w-full px-4 py-2 border border-gray-300 rounded-lg">
```

**After:**
```html
<input class="form-input">
```

---

## Responsive Design

### Breakpoints

- **sm:** 640px (mobile landscape)
- **md:** 768px (tablet)
- **lg:** 1024px (desktop)
- **xl:** 1280px (large desktop)
- **2xl:** 1536px (extra large)

### Mobile-First Approach

Design for mobile first, then enhance for larger screens:

```css
/* Mobile first */
.container {
  padding: var(--spacing-4);
}

/* Tablet and up */
@media (min-width: 768px) {
  .container {
    padding: var(--spacing-8);
  }
}
```

---

## Accessibility

### WCAG Compliance

- **Color Contrast:** All text meets WCAG AA (4.5:1) minimum
- **Touch Targets:** Minimum 44x44px for interactive elements
- **Focus States:** Visible focus indicators on all interactive elements
- **Keyboard Navigation:** All interactive elements are keyboard accessible
- **Screen Readers:** Semantic HTML and ARIA labels where needed

### Best Practices

1. Always provide text alternatives for icons
2. Use proper heading hierarchy
3. Ensure form inputs have labels
4. Test with keyboard navigation
5. Test with screen readers

---

## Examples

### Complete Form Example

```html
<form>
  <div class="mb-4">
    <label class="form-label required">Full Name</label>
    <input type="text" class="form-input" required>
    <span class="form-error">Name is required</span>
  </div>
  
  <div class="mb-4">
    <label class="form-label">Email</label>
    <input type="email" class="form-input">
    <span class="form-help">We'll never share your email</span>
  </div>
  
  <div class="flex gap-4">
    <button type="submit" class="btn btn-primary">Submit</button>
    <button type="button" class="btn btn-secondary">Cancel</button>
  </div>
</form>
```

### Card Grid Example

```html
<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
  <div class="card">
    <div class="card-header">
      <h3 class="card-title">Card 1</h3>
    </div>
    <div class="card-body">
      Content
    </div>
  </div>
  <!-- Repeat for other cards -->
</div>
```

---

## Support & Updates

For questions or updates to the design system:
- Refer to this style guide
- Check component examples in templates
- All design tokens are defined in `static/css/theme.css`

**Last Updated:** November 2025  
**Version:** 1.0

