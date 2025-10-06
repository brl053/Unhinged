# Component Migration Template

**Component**: `[ComponentName]`  
**Original LOC**: `[XXX]`  
**Estimated Time**: `[X hours]` (based on PromptSurgeryPanel: 507 LOC = 6 hours)  
**Migration Date**: `[YYYY-MM-DD]`  

---

## **Pre-Migration Checklist**

### **📋 Analysis Phase (30 min)**
- [ ] **Audit current component structure**
  - [ ] Count lines of code: `wc -l ComponentName.tsx`
  - [ ] Identify hard-coded values: `grep -E "#[0-9a-fA-F]{6}|[0-9]+px" ComponentName.tsx`
  - [ ] Document current dependencies and imports
  - [ ] Screenshot current visual state for regression testing

- [ ] **Design token mapping**
  - [ ] List all colors → map to `theme.colors.semantic.*`
  - [ ] List all spacing → map to `theme.spatial.base.spacing.*`
  - [ ] List all typography → map to `theme.typography.*`
  - [ ] List all motion → map to `theme.motion.*`

### **📁 Structure Setup (15 min)**
- [ ] **Create component directory**: `frontend/src/components/common/ComponentName/`
- [ ] **Create file structure**:
  ```
  ComponentName/
  ├── index.ts              # Clean exports
  ├── ComponentName.tsx     # Main component
  ├── types.ts             # TypeScript interfaces
  ├── styles.ts            # Design system styling
  ├── utils.ts             # Component utilities
  ├── hooks.ts             # Custom React hooks (if needed)
  └── constants.ts         # Component constants
  ```

---

## **Migration Implementation**

### **🔧 Step 1: Extract Component Logic (45 min)**
- [ ] **Move component to `ComponentName.tsx`**
- [ ] **Extract types to `types.ts`**
  ```typescript
  import { UnhingedTheme } from '../../design_system';
  
  export interface ComponentNameProps {
    // Define props with design system variants
  }
  
  export interface StyledComponentNameProps {
    theme: UnhingedTheme;
    // Only styling-related props
  }
  ```

- [ ] **Extract constants to `constants.ts`**
  ```typescript
  export const COMPONENT_NAME_CONSTANTS = {
    // Replace magic numbers/strings
  } as const;
  ```

### **🎨 Step 2: Design System Integration (90 min)**
- [ ] **Create `styles.ts` with design tokens**
  ```typescript
  import styled from 'styled-components';
  import { StyledComponentNameProps } from './types';
  
  export const StyledComponentName = styled.div<StyledComponentNameProps>`
    // Replace ALL hard-coded values with theme tokens
    color: ${({ theme }) => theme.colors.semantic.context.text.primary};
    padding: ${({ theme }) => theme.spatial.base.spacing.md}px;
    // etc.
  `;
  ```

- [ ] **Replace hard-coded values systematically**:
  - [ ] Colors: `#ffffff` → `theme.colors.primitive.achromatic.white`
  - [ ] Spacing: `16px` → `theme.spatial.base.spacing.md`
  - [ ] Typography: `font-size: 14px` → `theme.typography.scale.sm`
  - [ ] Borders: `1px solid #ccc` → `theme.spatial.base.border.thin solid theme.colors.semantic.context.border.primary`

### **🔗 Step 3: Utilities & Hooks (30 min)**
- [ ] **Extract utility functions to `utils.ts`**
- [ ] **Extract custom hooks to `hooks.ts`** (if component has state logic)
- [ ] **Create clean exports in `index.ts`**
  ```typescript
  export { ComponentName } from './ComponentName';
  export type { ComponentNameProps } from './types';
  export * from './constants';
  ```

---

## **Verification & Testing**

### **🧪 Technical Verification (30 min)**
- [ ] **TypeScript compilation**: `npm run type-check`
- [ ] **Build success**: `npm run build`
- [ ] **Hard-coded value check**: `python scripts/python/fix_theme_properties.py --dry-run`
- [ ] **Bundle size impact**: Compare before/after bundle sizes

### **👀 Visual Verification (15 min)**
- [ ] **Component renders correctly** in application
- [ ] **No visual regression** compared to pre-migration screenshots
- [ ] **Responsive behavior** works across breakpoints
- [ ] **Theme switching** works (if implemented)

### **📊 Metrics Collection (10 min)**
- [ ] **LOC comparison**: 
  - Original: `[XXX]` LOC
  - Migrated: `[XXX]` LOC  
  - Net change: `[+/-XXX]` LOC (`[XX]%` change)
- [ ] **Design token coverage**: `100%` (zero hard-coded values)
- [ ] **TypeScript safety**: Complete with design system types
- [ ] **File count**: `[X]` files in recursive structure

---

## **Documentation Updates**

### **📝 Required Updates (15 min)**
- [ ] **Update import statements** throughout application
- [ ] **Update `docs/roadmap/immediate-next-steps.md`**
  - Mark component tasks as complete
  - Update component inventory status
- [ ] **Update `CHECKPOINT-STATUS.md`**
  - Add component to completed list
  - Update migration statistics
  - Update confidence metrics

### **🎯 Optional Documentation**
- [ ] **Add component to Storybook** (if available)
- [ ] **Update component architecture docs**
- [ ] **Document any new patterns discovered**

---

## **Success Criteria**

### **✅ Technical Requirements**
- [ ] Zero TypeScript compilation errors
- [ ] Zero hard-coded values (100% design token coverage)
- [ ] Successful build with no warnings
- [ ] All imports updated and working
- [ ] Component renders identically to original

### **✅ Quality Requirements**
- [ ] Proper file separation (concerns properly separated)
- [ ] Clean TypeScript interfaces with design system integration
- [ ] Consistent naming conventions
- [ ] Proper error handling maintained

### **✅ Process Requirements**
- [ ] Migration time tracked for future estimates
- [ ] Documentation updated
- [ ] Patterns documented for future components
- [ ] Any blockers or learnings noted

---

## **Time Tracking**

**Estimated Time**: `[X]` hours  
**Actual Time**: `[X]` hours  
**Variance**: `[+/-X]` hours (`[XX]%`)

**Time Breakdown**:
- Analysis: `[X]` min
- Structure Setup: `[X]` min  
- Implementation: `[X]` min
- Verification: `[X]` min
- Documentation: `[X]` min

---

## **Lessons Learned**

### **✅ What Went Well**
- [Document successes and smooth processes]

### **⚠️ Challenges Encountered**
- [Document blockers, unexpected complexity, design token gaps]

### **💡 Improvements for Next Migration**
- [Process improvements, tooling needs, pattern refinements]

---

## **Rollback Plan**

If migration reveals architectural issues:

1. **Immediate rollback**: `git revert [commit-hash]`
2. **Restore original component**: Keep backup of original file
3. **Update imports**: Revert import statement changes
4. **Document issues**: Record problems for future resolution

---

## **Next Component Preparation**

Based on this migration:
- [ ] **Update migration template** with new learnings
- [ ] **Refine time estimates** for similar components
- [ ] **Identify reusable patterns** for component category
- [ ] **Plan next component** in migration queue

---

**Template Version**: 1.0  
**Based on**: PromptSurgeryPanel migration (507→847 LOC, 6 hours)  
**Next Update**: After EventFeed migration
