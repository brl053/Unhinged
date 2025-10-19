# Design Token Mappings - The Floor Foundation

## Overview
This document maps all hardcoded values found in the 11 HTML files to their corresponding design tokens. Use this as a reference during systematic remediation.

## Color Mappings

### Text Colors
- `color: #6c757d` → `color: var(--color-text-secondary)`
- `color: #495057` → `color: var(--color-text-primary)`
- `color: #212529` → `color: var(--color-text-primary)`
- `color: #1f2937` → `color: var(--color-text-primary)`

### Background Colors
- `background: #f8f9fa` → `background: var(--color-surface)`
- `background: #ffffff` → `background: var(--color-background)`
- `background: #f8fafc` → `background: var(--color-surface)`

### Status Colors (Bootstrap → Design Tokens)
- `background: #d4edda; color: #155724` → `background: rgba(var(--color-success-rgb), 0.1); color: var(--color-success)`
- `background: #f8d7da; color: #721c24` → `background: rgba(var(--color-danger-rgb), 0.1); color: var(--color-danger)`
- `background: #fff3cd; color: #856404` → `background: rgba(var(--color-warning-rgb), 0.1); color: var(--color-warning)`

### Primary Colors
- `#007bff` → `var(--color-primary)`
- `#2563eb` → `var(--color-primary)`
- `#3b82f6` → `var(--color-primary)`

### Success Colors
- `#28a745` → `var(--color-success)`
- `#10b981` → `var(--color-success)`

### Danger Colors
- `#dc3545` → `var(--color-danger)`
- `#ef4444` → `var(--color-danger)`

### Border Colors
- `border: 1px solid #c3e6cb` → `border: 1px solid rgba(var(--color-success-rgb), 0.2)`
- `border: 1px solid #f5c6cb` → `border: 1px solid rgba(var(--color-danger-rgb), 0.2)`
- `border: 1px solid #e5e7eb` → `border: 1px solid var(--color-border)`

## Spacing Mappings

### Padding
- `padding: 4px 8px` → `padding: var(--spacing-xs) var(--spacing-sm)`
- `padding: 8px 12px` → `padding: var(--spacing-sm) var(--spacing-md)`
- `padding: 12px` → `padding: var(--spacing-md)`
- `padding: 12px 24px` → `padding: var(--spacing-md) var(--spacing-xl)`
- `padding: 15px` → `padding: var(--spacing-lg)`
- `padding: 16px` → `padding: var(--spacing-md)`
- `padding: 20px` → `padding: var(--spacing-lg)`
- `padding: 30px` → `padding: var(--spacing-2xl)`

### Margin
- `margin: 2px 0` → `margin: var(--spacing-xs) 0`
- `margin: 4px` → `margin: var(--spacing-xs)`
- `margin: 8px 0` → `margin: var(--spacing-sm) 0`
- `margin: 10px 5px` → `margin: var(--spacing-sm)`
- `margin: 16px 0` → `margin: var(--spacing-md) 0`
- `margin: 20px 0` → `margin: var(--spacing-lg) 0`
- `margin: 20px auto` → `margin: var(--spacing-lg) auto`
- `margin-bottom: 8px` → `margin-bottom: var(--spacing-sm)`
- `margin-bottom: 16px` → `margin-bottom: var(--spacing-md)`
- `margin-bottom: 20px` → `margin-bottom: var(--spacing-lg)`
- `margin-bottom: 30px` → `margin-bottom: var(--spacing-2xl)`

### Gap
- `gap: 8px` → `gap: var(--spacing-sm)` ✅ (already correct)

## Typography Mappings

### Font Sizes
- `font-size: 12px` → `font-size: var(--font-size-xs)`
- `font-size: 14px` → `font-size: var(--font-size-sm)`
- `font-size: 16px` → `font-size: var(--font-size-base)`
- `font-size: 18px` → `font-size: var(--font-size-lg)`
- `font-size: 40px` → `font-size: var(--font-size-3xl)`
- `font-size: 48px` → `font-size: var(--font-size-3xl)`

### Font Weights
- `font-weight: bold` → `font-weight: 700`
- `font-weight: 500` → `font-weight: 500` ✅ (already correct)
- `font-weight: 600` → `font-weight: 600` ✅ (already correct)

## Layout Mappings

### Border Radius
- `border-radius: 4px` → `border-radius: var(--border-radius)`
- `border-radius: 6px` → `border-radius: var(--border-radius)`
- `border-radius: 8px` → `border-radius: var(--border-radius)`
- `border-radius: 12px` → `border-radius: var(--border-radius-lg)`

## File-Specific Violation Counts

### High Priority (Most Violations)
1. **image-test.html**: 25 violations
2. **voice-test.html**: 15 violations
3. **index.html**: 12 violations
4. **grpc-test.html**: 8 violations

### Medium Priority
5. **dag-control.html**: 6 violations
6. **table-of-contents.html**: 5 violations
7. **chat.html**: 4 violations

### Low Priority
8. **text-test.html**: 3 violations
9. **service-orchestration.html**: 2 violations
10. **persistence-dev-tool.html**: 1 violation
11. **test-mission-control.html**: 7 violations

## Implementation Notes

### Status Indicator Pattern
Replace all instances of hardcoded status colors with this pattern:
```css
.status.healthy {
  background: rgba(var(--color-success-rgb), 0.1);
  color: var(--color-success);
  border: 1px solid rgba(var(--color-success-rgb), 0.2);
}
```

### Button Pattern
Replace all instances of hardcoded button styles with this pattern:
```css
.button-primary {
  background: var(--color-primary);
  color: white;
  padding: var(--spacing-md) var(--spacing-xl);
  border-radius: var(--border-radius);
  font-size: var(--font-size-base);
}
```

### Container Pattern
Replace all instances of hardcoded container styles with this pattern:
```css
.container {
  padding: var(--spacing-2xl);
  margin-bottom: var(--spacing-lg);
  background: var(--color-background);
  border-radius: var(--border-radius-lg);
}
```

## Validation Commands

### Check for remaining violations:
```bash
# Colors
grep -r "color: #" control/static_html/ --include="*.html"
grep -r "background: #" control/static_html/ --include="*.html"

# Spacing
grep -r "padding: [0-9]" control/static_html/ --include="*.html"
grep -r "margin: [0-9]" control/static_html/ --include="*.html"

# Typography
grep -r "font-size: [0-9]" control/static_html/ --include="*.html"
```

### Success Criteria
- All grep commands return zero results
- All 11 HTML files load correctly
- Visual appearance remains consistent
- No CSS errors in browser console

---

**THE FLOOR FOUNDATION - DETERMINISTIC IMPLEMENTATION GUIDE**
*Every hardcoded value mapped. Every violation catalogued. Every replacement specified.*
