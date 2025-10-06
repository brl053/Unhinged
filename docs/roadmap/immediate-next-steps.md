# Immediate Next Steps: Component Migration
## Week 1 Action Plan for Design System Integration

**Date**: 2025-10-06  
**Priority**: Critical  
**Timeline**: 7 days  
**Goal**: Begin component structure cleanup and design token integration

---

## **Day 1-2: Component Audit and Planning**

### **Component Inventory**

**Current Components Requiring Migration:**

```
HIGH PRIORITY (Hard-coded values, large LOC):
├── ✅ frontend/src/components/common/PromptSurgeryPanel/ (COMPLETE - 800+ LOC, 7 files)
├── frontend/src/components/common/EventFeed.tsx (283 LOC) [NEXT]
├── frontend/src/components/common/VoiceRecorder.tsx (340 LOC)
├── frontend/src/components/common/ErrorBoundary.tsx (150+ LOC)

MEDIUM PRIORITY (Existing structure, needs tokens):
├── frontend/lib/components/Layout/ (Grid system)
├── frontend/lib/components/Icon/ (SVG system)
├── frontend/lib/components/InlineChildren/ (Layout utility)
├── frontend/lib/components/SideNav/ (Navigation)

LOW PRIORITY (Simple components):
├── frontend/src/components/EventLog.tsx
├── frontend/src/components/chat/ (if exists)
```

### **Migration Strategy Decision**

**Approach**: Start with PromptSurgeryPanel as it's the most complex and will establish patterns for others.

**Tasks for Day 1-2:**
- [x] **Audit PromptSurgeryPanel.tsx** - Document all hard-coded values ✅ COMPLETE
- [x] **Create migration plan** - Map hard-coded values to design tokens ✅ COMPLETE
- [x] **Set up development environment** - Ensure design system is importable ✅ COMPLETE
- [x] **Create component folder structure** - Establish the recursive pattern ✅ COMPLETE

---

## **Day 3-4: PromptSurgeryPanel Migration**

### **Step 1: Structure Setup**

**Create new folder structure:**
```
frontend/src/components/common/PromptSurgeryPanel/
├── index.ts
├── PromptSurgeryPanel.tsx
├── styles.ts
├── types.ts
├── utils.ts
├── hooks.ts
└── constants.ts
```

**Tasks:**
- [x] **Create folder structure** following recursive pattern ✅ COMPLETE
- [x] **Move existing component** to `PromptSurgeryPanel.tsx` ✅ COMPLETE
- [x] **Extract hard-coded values** to constants ✅ COMPLETE
- [x] **Create proper exports** in `index.ts` ✅ COMPLETE

### **Step 2: Design Token Integration**

**Current Hard-Coded Values to Replace:**
```typescript
// BEFORE (hard-coded)
background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
border: 2px solid #007bff;
border-radius: 12px;
padding: 20px;
margin: 16px 0;

// AFTER (design tokens)
background: linear-gradient(135deg, 
  ${({ theme }) => theme.colors.semantic.context.background.primary} 0%, 
  ${({ theme }) => theme.colors.semantic.context.background.secondary} 100%
);
border: ${({ theme }) => theme.spatial.border.medium}px solid 
  ${({ theme }) => theme.colors.semantic.intent.primary};
border-radius: ${({ theme }) => theme.spatial.radius.md}px;
padding: ${({ theme }) => theme.spatial.spacing.lg}px;
margin: ${({ theme }) => theme.spatial.spacing.md}px 0;
```

**Tasks:**
- [x] **Replace all colors** with semantic color tokens ✅ COMPLETE
- [x] **Replace all spacing** with spatial tokens ✅ COMPLETE
- [x] **Replace all typography** with typography tokens ✅ COMPLETE
- [x] **Add responsive breakpoints** using design system ✅ COMPLETE
- [x] **Test component rendering** with new tokens ✅ COMPLETE

**✅ MIGRATION COMPLETE**: PromptSurgeryPanel successfully migrated to design system architecture with:
- 7 files in recursive structure (800+ LOC)
- 100% design token integration (zero hard-coded values)
- Complete TypeScript safety with design system types
- Cross-platform virtual DOM abstraction ready
- Python automation tooling established

---

## **Day 5: EventFeed Migration**

### **Apply Learned Patterns**

**EventFeed has similar patterns to PromptSurgeryPanel:**
- Hard-coded colors for severity states
- Fixed spacing and typography
- No responsive design

**Tasks:**
- [ ] **Create EventFeed folder structure**
- [ ] **Extract component logic** to separate files
- [ ] **Replace hard-coded severity colors** with semantic tokens:
  ```typescript
  // BEFORE
  case 'error': return 'rgba(220, 53, 69, 0.1)';
  case 'warn': return 'rgba(255, 193, 7, 0.1)';
  case 'success': return 'rgba(40, 167, 69, 0.1)';
  
  // AFTER
  case 'error': return theme.colors.alpha.danger.alpha10;
  case 'warn': return theme.colors.alpha.warning.alpha10;
  case 'success': return theme.colors.alpha.success.alpha10;
  ```
- [ ] **Add responsive typography** for different screen sizes
- [ ] **Test event rendering** with design tokens

---

## **Day 6: VoiceRecorder Migration**

### **Audio Component Complexity**

**VoiceRecorder has unique challenges:**
- Audio state management
- Recording UI states
- Microphone permissions
- Real-time audio visualization

**Tasks:**
- [ ] **Create VoiceRecorder folder structure**
- [ ] **Extract audio logic** to custom hooks (`hooks.ts`)
- [ ] **Replace UI styling** with design tokens
- [ ] **Add recording state variants** using semantic colors
- [ ] **Implement responsive audio controls**
- [ ] **Test audio functionality** with new structure

---

## **Day 7: Testing and Validation**

### **Integration Testing**

**Ensure all migrated components work together:**

**Tasks:**
- [ ] **Update import statements** throughout application
- [ ] **Test component rendering** in actual application context
- [ ] **Validate design token usage** - no hard-coded values remaining
- [ ] **Check responsive behavior** across breakpoints
- [ ] **Test theme switching** (if implemented)
- [ ] **Performance testing** - ensure no regression
- [ ] **Document migration patterns** for next components

### **Create Migration Template**

**Based on learnings from first three components:**

**Tasks:**
- [ ] **Document migration process** - step-by-step guide
- [ ] **Create component template** - boilerplate for new components
- [ ] **Update development guidelines** - design token usage rules
- [ ] **Plan next week's components** - ErrorBoundary, Layout, etc.

---

## **Success Criteria for Week 1**

### **Technical Deliverables**
- [ ] 3 components migrated to recursive folder structure
- [ ] 100% design token usage in migrated components (zero hard-coded values)
- [ ] Proper TypeScript interfaces with design system integration
- [ ] Responsive design implementation using breakpoint tokens
- [ ] Working application with migrated components

### **Process Deliverables**
- [ ] Component migration template and guidelines
- [ ] Documentation of migration patterns and best practices
- [ ] Updated import statements and dependency management
- [ ] Testing strategy for component migrations

### **Quality Metrics**
- [ ] No visual regression in migrated components
- [ ] Performance maintained or improved
- [ ] TypeScript compilation with no errors
- [ ] All components render correctly across breakpoints

---

## **Week 2 Preview**

### **Next Components to Migrate**
1. **ErrorBoundary** - Error state styling with design tokens
2. **Layout** - Grid system with responsive breakpoints
3. **Icon** - SVG system with consistent sizing
4. **SideNav** - Navigation with semantic colors

### **Advanced Features to Implement**
- [ ] Component variant system (size, intent, density)
- [ ] Motion tokens for transitions and animations
- [ ] Platform-specific adaptations
- [ ] Storybook integration for component documentation

---

## **Development Environment Setup**

### **Required Tools**
- [ ] Design system properly imported and accessible
- [ ] TypeScript strict mode enabled
- [ ] ESLint rules for design token usage
- [ ] Hot reload working for component development
- [ ] Browser dev tools for design token inspection

### **Validation Scripts**
```bash
# Check for hard-coded values (should return empty)
grep -r "#[0-9a-fA-F]\{6\}" frontend/src/components/

# Check for hard-coded pixel values (should be minimal)
grep -r "[0-9]\+px" frontend/src/components/

# Validate TypeScript compilation
npm run type-check

# Run component tests
npm run test:components
```

---

## **Communication Plan**

### **Daily Standups**
- Progress on component migration
- Blockers or design token gaps discovered
- Patterns learned for future components

### **End of Week Review**
- Demo migrated components
- Review migration template and guidelines
- Plan next week's component priorities
- Identify any design system improvements needed

---

**Ready to begin**: Component structure cleanup and design system integration starts now! 🚀
