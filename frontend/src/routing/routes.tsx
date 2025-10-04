/**
 * @fileoverview Route Definitions - Day 1 Implementation
 * @purpose Define all application routes with minimal configuration
 * @editable true - LLM should add new routes and enhance existing ones
 * @deprecated false
 *
 * @remarks
 * Minimal route definitions to get navigation working.
 * Each route includes component, title, icon, and sidebar visibility.
 *
 * @phase Day 1 - Core Navigation
 */

import React from 'react';
import { createBrowserRouter } from 'react-router-dom';
import { MainLayout } from '../layouts/MainLayout';
import { NavigationProvider } from './NavigationContext';
import { Chatroom } from '../pages/Chatroom/Chatroom';
import { ComponentShowcase } from '../pages/ComponentShowcase/ComponentShowcase';
import { IconType } from '../../lib/components/Icon/types';
import { RouteDefinition, RoutePath } from './types';

/**
 * Application route definitions
 * @public
 */
export const routes: RouteDefinition[] = [
  {
    path: '/' as RoutePath,
    component: Chatroom,
    title: 'Chat',
    icon: IconType.ChatBubbleFill,
    showInSidebar: true,
  },
  {
    path: '/showcase' as RoutePath,
    component: ComponentShowcase,
    title: 'Components',
    icon: IconType.DemonEmoji,
    showInSidebar: true,
  },
  // Future routes will be added here
  // {
  //   path: '/settings' as RoutePath,
  //   component: Settings,
  //   title: 'Settings',
  //   icon: IconType.Settings,
  //   showInSidebar: true,
  // },
];

/**
 * Layout Wrapper Component
 *
 * Wraps MainLayout with NavigationProvider to provide global navigation state.
 * This fixes the context provider ordering issue.
 *
 * @returns Layout wrapper with navigation context
 * @private
 */
const LayoutWrapper: React.FC = () => (
  <NavigationProvider>
    <MainLayout />
  </NavigationProvider>
);

/**
 * Create the main application router
 *
 * Sets up React Router with proper context provider wrapping.
 * NavigationProvider must be inside Router but outside MainLayout.
 *
 * @returns Configured browser router
 * @public
 */
export const createAppRouter = () => {
  return createBrowserRouter([
    {
      path: "/",
      element: <LayoutWrapper />,
      children: [
        {
          index: true, // This makes it the default route for "/"
          element: <Chatroom />,
        },
        {
          path: "showcase",
          element: <ComponentShowcase />,
        },
        // Future routes will be added here
      ],
    },
  ]);
};


//   {
//     path: "/about",
//     element: <About />,
//   },
//   {
//     path: "*", // Wildcard for not found routes
//     element: <NotFound />,
//   },