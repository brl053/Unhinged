/**
 * @fileoverview Main Layout Styled Components
 * @purpose Styled components for the main application layout with responsive sidebar
 * @editable true - LLM should update styles when adding new layout features
 * @deprecated false
 * 
 * @remarks
 * All styles use the enhanced theme system with proper color/spacing/typography tokens.
 * Includes responsive design patterns, smooth animations, and accessibility features.
 * The layout supports both desktop and mobile navigation patterns.
 */

import { styled, css } from 'styled-components';

// ============================================================================
// Layout Container
// ============================================================================

export const LayoutContainer = styled.div`
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: ${({ theme }) => theme.color.background.primary};
  color: ${({ theme }) => theme.color.text.primary};
`;

// ============================================================================
// Mobile Menu Button
// ============================================================================

export const MobileMenuButton = styled.button<{ $menuOpen: boolean }>`
  position: fixed;
  top: ${({ theme }) => theme.spacing.md};
  left: ${({ theme }) => theme.spacing.md};
  z-index: 1001;
  width: 44px;
  height: 44px;
  border: none;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  background: ${({ theme }) => theme.color.background.secondary};
  color: ${({ theme }) => theme.color.text.primary};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px ${({ theme }) => theme.color.shadow.primary};
  transition: all 0.2s ease;

  &:hover {
    background: ${({ theme }) => theme.color.background.hovered};
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }

  @media (min-width: 768px) {
    display: none;
  }
`;

// ============================================================================
// Sidebar Overlay (Mobile)
// ============================================================================

export const SidebarOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  
  @media (min-width: 768px) {
    display: none;
  }
`;

// ============================================================================
// Sidebar
// ============================================================================

export const Sidebar = styled.aside<{ 
  $collapsed: boolean; 
  $mobileOpen: boolean; 
  $isMobile: boolean; 
}>`
  display: flex;
  flex-direction: column;
  background: ${({ theme }) => theme.color.background.secondary};
  border-right: 1px solid ${({ theme }) => theme.color.border.primary};
  transition: all 0.3s ease;
  z-index: 1000;

  ${({ $collapsed, $isMobile, $mobileOpen }) => {
    if ($isMobile) {
      return css`
        position: fixed;
        top: 0;
        left: 0;
        height: 100vh;
        width: 280px;
        transform: translateX(${$mobileOpen ? '0' : '-100%'});
        box-shadow: ${$mobileOpen ? '4px 0 12px rgba(0, 0, 0, 0.15)' : 'none'};
      `;
    } else {
      return css`
        position: relative;
        height: 100vh;
        width: ${$collapsed ? '64px' : '280px'};
        min-width: ${$collapsed ? '64px' : '280px'};
      `;
    }
  }}
`;

// ============================================================================
// Sidebar Header
// ============================================================================

export const SidebarHeader = styled.div<{ $collapsed: boolean }>`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${({ theme }) => theme.spacing.lg};
  border-bottom: 1px solid ${({ theme }) => theme.color.border.primary};
  min-height: 64px;

  h2 {
    margin: 0;
    font-size: ${({ theme }) => theme.typography.fontSize.lg};
    font-weight: ${({ theme }) => theme.typography.fontWeight.bold};
    color: ${({ theme }) => theme.color.text.primary};
    opacity: ${({ $collapsed }) => $collapsed ? 0 : 1};
    transition: opacity 0.2s ease;
  }

  button {
    background: none;
    border: none;
    color: ${({ theme }) => theme.color.text.secondary};
    cursor: pointer;
    padding: ${({ theme }) => theme.spacing.sm};
    border-radius: ${({ theme }) => theme.borderRadius.sm};
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;

    &:hover {
      background: ${({ theme }) => theme.color.background.hovered};
      color: ${({ theme }) => theme.color.text.primary};
    }
  }

  ${({ $collapsed }) => $collapsed && css`
    justify-content: center;
    
    button {
      margin: 0;
    }
  `}
`;

// ============================================================================
// Sidebar Navigation
// ============================================================================

export const SidebarNav = styled.nav`
  flex: 1;
  padding: ${({ theme }) => theme.spacing.md} 0;
  overflow-y: auto;
  overflow-x: hidden;

  /* Custom scrollbar */
  &::-webkit-scrollbar {
    width: 4px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: ${({ theme }) => theme.color.border.primary};
    border-radius: 2px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: ${({ theme }) => theme.color.border.secondary};
  }
`;

// ============================================================================
// Navigation Item
// ============================================================================

export const NavItem = styled.div<{ $active: boolean; $collapsed: boolean }>`
  display: flex;
  align-items: center;
  padding: ${({ theme }) => theme.spacing.md} ${({ theme }) => theme.spacing.lg};
  margin: 0 ${({ theme }) => theme.spacing.sm};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  min-height: 48px;

  ${({ $collapsed }) => $collapsed && css`
    justify-content: center;
    margin: 0 ${({ theme }) => theme.spacing.sm};
    padding: ${({ theme }) => theme.spacing.md};
  `}

  ${({ $active, theme }) => $active ? css`
    background: ${theme.color.primary.main}20;
    color: ${theme.color.primary.main};
    
    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 50%;
      transform: translateY(-50%);
      width: 3px;
      height: 24px;
      background: ${theme.color.primary.main};
      border-radius: 0 2px 2px 0;
    }
  ` : css`
    color: ${theme.color.text.secondary};
    
    &:hover {
      background: ${theme.color.background.hovered};
      color: ${theme.color.text.primary};
    }
  `}

  &:active {
    transform: translateX(2px);
  }
`;

export const NavIcon = styled.div<{ $active: boolean }>`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  
  svg {
    width: 20px;
    height: 20px;
    transition: all 0.2s ease;
  }
`;

export const NavLabel = styled.span<{ $active: boolean }>`
  margin-left: ${({ theme }) => theme.spacing.md};
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
  font-weight: ${({ $active, theme }) => 
    $active ? theme.typography.fontWeight.semibold : theme.typography.fontWeight.medium
  };
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

// ============================================================================
// Main Content Area
// ============================================================================

export const MainContent = styled.main<{ $sidebarCollapsed: boolean }>`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: margin-left 0.3s ease;

  @media (max-width: 767px) {
    margin-left: 0;
  }
`;

export const ContentArea = styled.div`
  flex: 1;
  overflow: auto;
  background: ${({ theme }) => theme.color.background.primary};

  /* Custom scrollbar */
  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: ${({ theme }) => theme.color.background.secondary};
  }

  &::-webkit-scrollbar-thumb {
    background: ${({ theme }) => theme.color.border.primary};
    border-radius: 4px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: ${({ theme }) => theme.color.border.secondary};
  }
`;
