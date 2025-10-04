/**
 * @fileoverview Minimal Routing Types - Day 1 Implementation
 * @purpose Core type definitions to get sidebar navigation working
 * @editable true - LLM should expand these types in future phases
 * @deprecated false
 * 
 * @remarks
 * This is the minimal viable type system for functional navigation.
 * Contains only the essential types needed for:
 * - Route definitions with icons
 * - Type-safe navigation
 * - Active route detection
 * - Basic navigation state
 * 
 * Future phases will add: guards, metadata, advanced state management, etc.
 * 
 * @phase Day 1 - Core Navigation
 * @bundle_size ~0kb (compile-time only)
 */

import { ComponentType, ReactNode } from 'react';
import { IconType } from '../../lib/components/Icon/types';

/**
 * Core route path definitions
 * @public
 */
export type RoutePath = '/' | '/showcase' | '/settings' | '/tools' | '/docs';

/**
 * Basic route definition for sidebar navigation
 * @public
 */
export interface RouteDefinition {
  /** Route path */
  path: RoutePath;
  /** Component to render */
  component: ComponentType<any>;
  /** Display title */
  title: string;
  /** Icon for sidebar */
  icon: IconType;
  /** Show in sidebar navigation */
  showInSidebar: boolean;
}

/**
 * Navigation target for type-safe navigation
 * @public
 */
export interface NavigationTarget {
  /** Target route path */
  path: RoutePath;
  /** Replace current history entry instead of pushing */
  replace?: boolean;
}

/**
 * Current route context
 * @public
 */
export interface RouteContext {
  /** Current path */
  path: RoutePath;
  /** Route definition */
  route: RouteDefinition;
  /** Whether route is loading */
  loading: boolean;
}

/**
 * Basic navigation state
 * @public
 */
export interface NavigationState {
  /** Current route context */
  current: RouteContext;
  /** Whether navigation is in progress */
  navigating: boolean;
  /** Sidebar collapsed state */
  sidebarCollapsed: boolean;
  /** Mobile menu open state */
  mobileMenuOpen: boolean;
}

/**
 * Navigation actions
 * @public
 */
export interface NavigationActions {
  /** Navigate to a route */
  navigate: (target: NavigationTarget) => void;
  /** Toggle sidebar collapsed state */
  toggleSidebar: () => void;
  /** Set mobile menu state */
  setMobileMenuOpen: (open: boolean) => void;
}

/**
 * Complete navigation hook return type
 * @public
 */
export interface UseNavigationReturn extends NavigationState, NavigationActions {}

/**
 * Active route detection result
 * @public
 */
export interface RouteMatch {
  /** Whether route is active */
  isActive: boolean;
  /** Whether route is exact match */
  isExact: boolean;
}
