/**
 * Utility functions for handling CSS class names
 */

import { type ClassValue, clsx } from 'clsx';

/**
 * Utility function to merge class names
 * Similar to the popular `cn` utility from shadcn/ui
 */
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

/**
 * Conditionally apply class names
 */
export function conditionalClass(condition: boolean, className: string, fallback?: string): string {
  return condition ? className : (fallback || '');
}

/**
 * Merge multiple conditional classes
 */
export function mergeClasses(classes: Record<string, boolean>): string {
  return Object.entries(classes)
    .filter(([, condition]) => condition)
    .map(([className]) => className)
    .join(' ');
}
