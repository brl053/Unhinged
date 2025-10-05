/**
 * @fileoverview Navigation Context Provider - Day 1 Implementation
 * @purpose Global navigation state management with React Context
 * @editable true - LLM should extend with additional navigation features
 * @deprecated false
 * 
 * @remarks
 * Provides shared navigation state across the entire application.
 * Fixes the issue where useState in custom hooks creates separate state per component.
 * 
 * @phase Day 1 - Core Navigation Context
 */

import React, { createContext, useContext, useState, ReactNode, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { RoutePath } from './types';

/**
 * Navigation Context Value Interface
 * @public
 */
export interface NavigationContextValue {
  /** Current route path */
  currentPath: string;
  /** Navigate to a new path */
  navigate: (path: string) => void;
  /** Whether sidebar is collapsed */
  sidebarCollapsed: boolean;
  /** Toggle sidebar collapsed state */
  toggleSidebar: () => void;
  /** Whether mobile menu is open */
  mobileMenuOpen: boolean;
  /** Set mobile menu open state */
  setMobileMenuOpen: (open: boolean) => void;
}

/**
 * Navigation Context
 * @private
 */
const NavigationContext = createContext<NavigationContextValue | null>(null);

/**
 * Navigation Provider Props
 * @public
 */
export interface NavigationProviderProps {
  children: ReactNode;
}

/**
 * Navigation Provider Component
 * 
 * Provides global navigation state management using React Context.
 * Must be placed inside React Router but outside of components that use navigation.
 * 
 * @param props - Provider props
 * @returns Navigation provider component
 * @public
 */
export const NavigationProvider: React.FC<NavigationProviderProps> = ({ children }) => {
  // ========== React Router Hooks ==========
  const navigate = useNavigate();
  const location = useLocation();

  // ========== Global Navigation State ==========
  // This state is shared across ALL components that use useNavigation
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // ========== Navigation Actions ==========
  const handleNavigate = (path: string) => {
    navigate(path);
    // Auto-close mobile menu on navigation
    if (mobileMenuOpen) {
      setMobileMenuOpen(false);
    }
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(prev => !prev);
  };

  const handleSetMobileMenuOpen = (open: boolean) => {
    setMobileMenuOpen(open);
  };

  // ========== Context Value ==========
  const value = useMemo(() => ({
    currentPath: location.pathname,
    navigate: handleNavigate,
    sidebarCollapsed,
    toggleSidebar,
    mobileMenuOpen,
    setMobileMenuOpen: handleSetMobileMenuOpen,
  }), [location.pathname, sidebarCollapsed, mobileMenuOpen]);

  return (
    <NavigationContext.Provider value={value}>
      {children}
    </NavigationContext.Provider>
  );
};

/**
 * Use Navigation Hook
 * 
 * Provides access to global navigation state and actions.
 * Must be used within NavigationProvider.
 * 
 * @returns Navigation context value
 * @throws Error if used outside NavigationProvider
 * @public
 */
export const useNavigation = (): NavigationContextValue => {
  const context = useContext(NavigationContext);
  
  if (!context) {
    throw new Error('useNavigation must be used within NavigationProvider');
  }
  
  return context;
};

/**
 * Use Active Route Hook
 * 
 * Determines if a given route path is currently active.
 * Uses React Router's location directly to avoid hook violations.
 * 
 * @param routePath - Route path to check
 * @returns Whether the route is active
 * @public
 */
export const useActiveRoute = (routePath: string): boolean => {
  const location = useLocation();
  
  // Exact match for root route
  if (routePath === '/') {
    return location.pathname === '/';
  }
  
  // For other routes, check if current path starts with route path
  return location.pathname === routePath || location.pathname.startsWith(routePath + '/');
};
