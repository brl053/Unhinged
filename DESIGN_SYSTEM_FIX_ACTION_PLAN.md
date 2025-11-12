# DESIGN SYSTEM FIX - ONE-PAGE ACTION PLAN

## Problem Statement
The GTK4 CSS generator (`libs/design_system/build/generators/gtk4_generator.py`) outputs CSS custom properties (CSS variables like `--color-action-primary: #0066CC`), but GTK4's CSS parser **does not support CSS custom properties**. This causes 50+ parser errors and leaves widgets unstyled, triggering the TextView assertion crash.

## Root Cause
**File**: `libs/design_system/build/generators/gtk4_generator.py` lines 88-150
- `_generate_base_css()` outputs `:root { --color-action-primary: #0066CC; }`
- `_generate_theme_css()` outputs `.theme-light { --color-action-primary: #0066CC; }`
- `_generate_component_css()` outputs `.button { background-color: var(--color-action-primary); }`

GTK4 rejects all of this because it doesn't understand CSS variables.

## Solution: Replace CSS Variables with Hardcoded Values

The generator must resolve design tokens **at generation time**, not at runtime.

### Implementation (50 lines of code)

**File**: `libs/design_system/build/generators/gtk4_generator.py`

**Change**: Modify `_generate_base_css()`, `_generate_theme_css()`, and `_generate_component_css()` to:

1. Load design tokens from YAML files (already done in `load_tokens()`)
2. For each CSS rule that uses `var(--color-action-primary)`, replace it with the actual value `#0066CC`
3. Output pure GTK4 CSS with **zero CSS variables**

**Example transformation**:
```
BEFORE (invalid for GTK4):
.button { background-color: var(--color-action-primary); }

AFTER (valid for GTK4):
.button { background-color: #0066CC; }
```

### Code Changes Required

1. **In `_generate_base_css()`**: Don't output CSS variable definitions. Instead, output nothing (or comments only).

2. **In `_generate_theme_css()`**: When generating component styles, resolve tokens immediately:
   ```python
   # Instead of: background-color: var(--color-action-primary);
   # Output: background-color: #0066CC;  (for light theme)
   # Output: background-color: #4D94FF;  (for dark theme)
   ```

3. **In `_generate_component_css()`**: Replace all `var(--token-name)` with actual values from `self.tokens`.

### Validation

After changes, run:
```bash
make design-tokens-gtk4
grep "var(" generated/design_system/gtk4/*.css
# Should output: (nothing - no CSS variables)
```

## Timeline
- **Estimated effort**: 4-6 hours
- **Complexity**: Medium (token resolution logic already exists in GTK4ComponentGenerator)
- **Risk**: Low (only affects CSS generation, not component logic)
- **Blocker**: Yes—FormInput cannot work until this is fixed

## Immediate Workaround
```bash
export SKIP_DESIGN_SYSTEM=1
make start-gui
```

## Success Criteria
1. ✅ No CSS parser errors in startup output
2. ✅ `grep "var(" generated/design_system/gtk4/*.css` returns nothing
3. ✅ FormInput renders without assertion crash
4. ✅ All colors and spacing apply correctly to components

## Owner Assignment
[Assign to engineer responsible for design system]

## Related Files
- `libs/design_system/build/generators/gtk4_generator.py` (main fix)
- `libs/design_system/tokens/colors.yaml` (token source)
- `libs/design_system/tokens/spacing.yaml` (token source)
- `libs/design_system/tokens/typography.yaml` (token source)

