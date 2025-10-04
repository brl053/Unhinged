import React from 'react';
import { createBrowserRouter, RouteObject, RouterProvider } from 'react-router-dom';
import { Chatroom } from '../pages/Chatroom/Chatroom';
import { ComponentShowcase } from '../pages/ComponentShowcase/ComponentShowcase';
import { IconType } from '../../lib/components/Icon/types';

export type AthenaRoute = RouteObject & {
  icon: IconType;
  showOnSideNav: boolean;
}

export const routes: AthenaRoute[] = [
  {
    path: "/",
    element: <Chatroom />,
    icon: IconType.ChatBubbleFill,
    showOnSideNav: true,
  },
  {
    path: "/showcase",
    element: <ComponentShowcase />,
    icon: IconType.DemonEmoji,
    showOnSideNav: true,
  },

];


//   {
//     path: "/about",
//     element: <About />,
//   },
//   {
//     path: "*", // Wildcard for not found routes
//     element: <NotFound />,
//   },