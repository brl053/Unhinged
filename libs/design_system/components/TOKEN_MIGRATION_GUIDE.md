# Component Token Reference Migration Guide

## Overview

This guide documents the systematic approach to fix token references in component specifications to match the actual design token structure.

## Token Reference Mapping

### Spacing Tokens
```yaml
# ❌ Incorrect
sp.1, sp.2, sp.3, sp.4, sp.5, sp.6, sp.8, sp.12
sp.1_5, sp.2_5

# ✅ Correct  
spacing.scale.sp_1, spacing.scale.sp_2, spacing.scale.sp_3, spacing.scale.sp_4
spacing.scale.sp_5, spacing.scale.sp_6, spacing.scale.sp_8, spacing.scale.sp_12
spacing.scale.sp_1_5, spacing.scale.sp_2_5
```

### Color Tokens
```yaml
# ❌ Incorrect
text.primary, text.secondary, text.tertiary, text.inverse, text.disabled
surface.default, surface.elevated, surface.overlay, surface.inverse
action.primary, action.secondary, action.tertiary, action.disabled
feedback.success, feedback.warning, feedback.error, feedback.info
border.default, border.subtle, border.strong
interactive.hover, interactive.active, interactive.focus

# ✅ Correct
colors.text.primary, colors.text.secondary, colors.text.tertiary, colors.text.inverse, colors.text.disabled
colors.surface.default, colors.surface.elevated, colors.surface.overlay, colors.surface.inverse
colors.action.primary, colors.action.secondary, colors.action.tertiary, colors.action.disabled
colors.feedback.success, colors.feedback.warning, colors.feedback.error, colors.feedback.info
colors.border.default, colors.border.subtle, colors.border.strong
colors.interactive.hover, colors.interactive.active, colors.interactive.focus
```

### Typography Tokens
```yaml
# ❌ Incorrect
type.display, type.heading, type.body, type.caption, type.code

# ✅ Correct
typography.scale.display, typography.scale.heading, typography.scale.body, typography.scale.caption, typography.scale.code
```

### Border and Size Values
```yaml
# ❌ Incorrect (these aren't tokens)
border.thin, border.medium, border.thick
radius.sm, radius.md, radius.lg, radius.full

# ✅ Correct (use actual values)
"1px", "2px", "3px"
"4px", "8px", "16px", "50%"
```

### Elevation Tokens
```yaml
# ❌ Incorrect
elevation.1, elevation.2, elevation.3, elevation.4

# ✅ Correct
elevation.shadows.1, elevation.shadows.2, elevation.shadows.3, elevation.shadows.4
```

## Migration Script Approach

### Find and Replace Patterns

1. **Spacing References:**
   ```bash
   find libs/design_system/components -name "*.yaml" -exec sed -i 's/"sp\.\([0-9_]*\)"/"spacing.scale.sp_\1"/g' {} \;
   ```

2. **Color References:**
   ```bash
   find libs/design_system/components -name "*.yaml" -exec sed -i 's/"text\.\([a-z]*\)"/"colors.text.\1"/g' {} \;
   find libs/design_system/components -name "*.yaml" -exec sed -i 's/"surface\.\([a-z]*\)"/"colors.surface.\1"/g' {} \;
   find libs/design_system/components -name "*.yaml" -exec sed -i 's/"action\.\([a-z]*\)"/"colors.action.\1"/g' {} \;
   find libs/design_system/components -name "*.yaml" -exec sed -i 's/"feedback\.\([a-z]*\)"/"colors.feedback.\1"/g' {} \;
   find libs/design_system/components -name "*.yaml" -exec sed -i 's/"border\.\([a-z]*\)"/"colors.border.\1"/g' {} \;
   find libs/design_system/components -name "*.yaml" -exec sed -i 's/"interactive\.\([a-z]*\)"/"colors.interactive.\1"/g' {} \;
   ```

3. **Typography References:**
   ```bash
   find libs/design_system/components -name "*.yaml" -exec sed -i 's/"type\.\([a-z]*\)"/"typography.scale.\1"/g' {} \;
   ```

## Validation Workflow

1. **Before Migration:**
   ```bash
   python3 libs/design_system/build/component_validator.py --components-dir libs/design_system/components
   ```

2. **Run Migration Script**

3. **After Migration:**
   ```bash
   python3 libs/design_system/build/component_validator.py --components-dir libs/design_system/components
   ```

4. **Manual Fixes for Non-Token Values:**
   - Replace `border.thin` with `"1px"`
   - Replace `border.medium` with `"2px"`
   - Replace `radius.sm` with `"4px"`
   - Replace `radius.md` with `"8px"`
   - Replace `radius.lg` with `"16px"`
   - Replace `radius.full` with `"50%"`

## Expected Results

After migration, all component specifications should:
- ✅ Pass schema validation
- ✅ Have correct token references
- ✅ Be ready for component generation
- ✅ Support the specification-first development approach

## Next Steps

1. Run the migration script
2. Validate all components pass
3. Test component generation pipeline
4. Create additional primitive component specifications
5. Develop container and complex component specifications
