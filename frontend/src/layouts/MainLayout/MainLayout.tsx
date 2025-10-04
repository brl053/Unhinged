/**
 * @fileoverview Main Layout Component
 * @purpose Primary layout wrapper with sidebar navigation and main content area
 * @editable true - LLM should update when adding new layout features or navigation patterns
 * @deprecated false
 * 
 * @remarks
 * This component provides the main application layout including:
 * - Responsive sidebar navigation with route-based active states
 * - Main content area with proper routing integration
 * - Mobile-responsive navigation patterns
 * - Theme integration and consistent spacing
 * 
 * The layout automatically integrates with React Router to show active navigation
 * states and handle route transitions. It supports both desktop and mobile
 * navigation patterns with collapsible sidebar functionality.
 * 
 * @example
 * ```tsx
 * <MainLayout>
 *   <Outlet /> // React Router outlet for page content
 * </MainLayout>
 * ```
 */

import React, { useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Icon, IconType } from '../../../lib/components/Icon';
import { useNavigation } from '../../routing/NavigationContext';
import { RouteDefinition } from '../../routing/types';
import { routes } from '../../routing/routes';
import {
  LayoutContainer,
  Sidebar,
  SidebarHeader,
  SidebarNav,
  NavItem,
  NavIcon,
  NavLabel,
  MainContent,
  ContentArea,
  MobileMenuButton,
  SidebarOverlay
} from './styles';

/**
 * Main Layout Component Props
 * @public
 */
export interface MainLayoutProps {
  /** Additional CSS class name */
  className?: string;
  /** Test ID for testing */
  testId?: string;
}

/**
 * Main Layout Component
 * 
 * Provides the primary application layout with sidebar navigation and main content area.
 * Automatically handles route-based active states and responsive navigation patterns.
 * 
 * @public
 */
export const MainLayout: React.FC<MainLayoutProps> = ({
  className,
  testId
}) => {
  // ========== Hooks ==========
  const navigation = useNavigation();
  const location = useLocation();

  // ========== Local State ==========
  const [isMobile, setIsMobile] = React.useState(false);

  // ========== Sidebar Routes ==========
  const sidebarRoutes = routes.filter(route => route.showInSidebar);

  // ========== Effects ==========

  // Handle responsive behavior
  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);

      // Auto-collapse sidebar on mobile
      if (mobile && !navigation.sidebarCollapsed) {
        navigation.toggleSidebar();
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [navigation]);

  // Close mobile menu on route change
  useEffect(() => {
    if (navigation.mobileMenuOpen) {
      navigation.setMobileMenuOpen(false);
    }
  }, [navigation.currentPath, navigation]);

  // ========== Event Handlers ==========

  const handleNavItemClick = (route: RouteDefinition) => {
    navigation.navigate(route.path);
  };

  const toggleSidebar = () => {
    if (isMobile) {
      navigation.setMobileMenuOpen(!navigation.mobileMenuOpen);
    } else {
      navigation.toggleSidebar();
    }
  };

  const closeMobileMenu = () => {
    navigation.setMobileMenuOpen(false);
  };

  // ========== Helper Functions ==========

  const isRouteActive = (routePath: string): boolean => {
    if (routePath === '/') {
      return location.pathname === '/';
    }
    return location.pathname === routePath || location.pathname.startsWith(routePath + '/');
  };

  const NavigationItem: React.FC<{ route: RouteDefinition }> = ({ route }) => {
    const isActive = isRouteActive(route.path);

    return (
      <NavItem
        data-testid="nav-item"
        data-route={route.path}
        $active={isActive}
        $collapsed={navigation.sidebarCollapsed}
        onClick={() => handleNavItemClick(route)}
        title={navigation.sidebarCollapsed ? route.title : undefined}
      >
        <NavIcon $active={isActive}>
          <Icon type={route.icon} size="md" />
        </NavIcon>

        {!navigation.sidebarCollapsed && (
          <NavLabel data-testid="nav-label" $active={isActive}>
            {route.title}
          </NavLabel>
        )}
      </NavItem>
    );
  };

  // ========== Render ==========
  
  return (
    <LayoutContainer className={className} data-testid={testId}>
      {/* Mobile Menu Button */}
      {isMobile && (
        <MobileMenuButton
          onClick={toggleSidebar}
          $menuOpen={navigation.mobileMenuOpen}
        >
          <Icon
            type={navigation.mobileMenuOpen ? IconType.Stop : IconType.DemonEmoji}
            size="md"
          />
        </MobileMenuButton>
      )}

      {/* Mobile Overlay */}
      {isMobile && navigation.mobileMenuOpen && (
        <SidebarOverlay onClick={closeMobileMenu} />
      )}

      {/* Sidebar */}
      <Sidebar
        data-testid="sidebar"
        $collapsed={navigation.sidebarCollapsed}
        $mobileOpen={navigation.mobileMenuOpen}
        $isMobile={isMobile}
      >
        <SidebarHeader $collapsed={navigation.sidebarCollapsed}>
          {!navigation.sidebarCollapsed && (
            <h2>Unhinged</h2>
          )}

          {!isMobile && (
            <button
              onClick={toggleSidebar}
              title={navigation.sidebarCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
            >
              <Icon
                type={navigation.sidebarCollapsed ? IconType.ChatBubbleFill : IconType.Stop}
                size="sm"
              />
            </button>
          )}
        </SidebarHeader>

        <SidebarNav>
          {sidebarRoutes.map(route => (
            <NavigationItem key={route.path} route={route} />
          ))}
        </SidebarNav>
      </Sidebar>

      {/* Main Content */}
      <MainContent $sidebarCollapsed={navigation.sidebarCollapsed}>
        <ContentArea>
          <Outlet />
        </ContentArea>
      </MainContent>
    </LayoutContainer>
  );
};

export default MainLayout;
