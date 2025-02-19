import React from 'react';
import { createBrowserRouter, RouteObject, RouterProvider } from 'react-router-dom';
import { Chatroom } from '../pages/Chatroom/Chatroom';
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

];


//   {
//     path: "/about",
//     element: <About />,
//   },
//   {
//     path: "*", // Wildcard for not found routes
//     element: <NotFound />,
//   },