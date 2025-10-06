// ============================================================================
// EventLog Utils - Utility Functions for Event Processing
// ============================================================================
//
// @file utils.ts
// @version 2.0.0
// @author Unhinged Design System Team
// @date 2025-10-06
// @description Utility functions for event processing and formatting
//
// Etymology: Latin "utilitas" = usefulness, practical value
// Methodology: Pure functions with clear inputs and outputs
// ============================================================================

import { Event, EventFilter, EventFormatOptions, EventTypeMetadata } from './types';
import { EVENT_TYPE_METADATA, PERFORMANCE_THRESHOLDS } from './constants';

/**
 * Format timestamp for display
 * Converts timestamp to human-readable format
 * 
 * @param timestampMs - Timestamp in milliseconds
 * @param format - Format type ('relative', 'absolute', 'iso')
 * @param showMilliseconds - Whether to include milliseconds
 * @returns Formatted timestamp string
 */
export const formatTimestamp = (
  timestampMs: number,
  format: EventFormatOptions['timestampFormat'] = 'absolute',
  showMilliseconds: boolean = false
): string => {
  const date = new Date(timestampMs);
  
  switch (format) {
    case 'relative':
      return formatRelativeTime(timestampMs);
    
    case 'iso':
      return showMilliseconds ? date.toISOString() : date.toISOString().slice(0, -5) + 'Z';
    
    case 'absolute':
    default:
      const options: Intl.DateTimeFormatOptions = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
      };
      
      if (showMilliseconds) {
        return date.toLocaleString('en-US', options) + `.${date.getMilliseconds().toString().padStart(3, '0')}`;
      }
      
      return date.toLocaleString('en-US', options);
  }
};

/**
 * Format relative time (e.g., "2 minutes ago")
 * Creates human-readable relative timestamps
 * 
 * @param timestampMs - Timestamp in milliseconds
 * @returns Relative time string
 */
export const formatRelativeTime = (timestampMs: number): string => {
  const now = Date.now();
  const diffMs = now - timestampMs;
  const diffSeconds = Math.floor(diffMs / 1000);
  const diffMinutes = Math.floor(diffSeconds / 60);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);
  
  if (diffSeconds < 60) {
    return diffSeconds <= 1 ? 'just now' : `${diffSeconds}s ago`;
  } else if (diffMinutes < 60) {
    return `${diffMinutes}m ago`;
  } else if (diffHours < 24) {
    return `${diffHours}h ago`;
  } else {
    return `${diffDays}d ago`;
  }
};

/**
 * Format JSON payload for display
 * Pretty-prints JSON with syntax highlighting
 * 
 * @param obj - Object to format
 * @param indentation - Number of spaces for indentation
 * @param maxLength - Maximum length before truncation
 * @returns Formatted JSON string
 */
export const formatJSON = (
  obj: any,
  indentation: number = 2,
  maxLength?: number
): string => {
  try {
    const jsonString = JSON.stringify(obj, null, indentation);
    
    if (maxLength && jsonString.length > maxLength) {
      return jsonString.slice(0, maxLength) + '...';
    }
    
    return jsonString;
  } catch (error) {
    return `[Invalid JSON: ${error instanceof Error ? error.message : 'Unknown error'}]`;
  }
};

/**
 * Filter events based on criteria
 * Applies multiple filter criteria to event array
 * 
 * @param events - Array of events to filter
 * @param filter - Filter criteria
 * @returns Filtered events array
 */
export const filterEvents = (events: Event[], filter: EventFilter): Event[] => {
  return events.filter(event => {
    // Text search
    if (filter.searchTerm) {
      const searchTerm = filter.searchTerm.toLowerCase();
      const searchableText = [
        event.event_type,
        event.user_id,
        event.session_id,
        event.event_id,
      ].join(' ').toLowerCase();
      
      const payloadText = filter.includePayload 
        ? JSON.stringify(event.payload).toLowerCase()
        : '';
      
      if (!searchableText.includes(searchTerm) && !payloadText.includes(searchTerm)) {
        return false;
      }
    }
    
    // Event type filter
    if (filter.eventTypes && filter.eventTypes.length > 0) {
      if (!filter.eventTypes.includes(event.event_type)) {
        return false;
      }
    }
    
    // User ID filter
    if (filter.userIds && filter.userIds.length > 0) {
      if (!filter.userIds.includes(event.user_id)) {
        return false;
      }
    }
    
    // Session ID filter
    if (filter.sessionIds && filter.sessionIds.length > 0) {
      if (!filter.sessionIds.includes(event.session_id)) {
        return false;
      }
    }
    
    // Date range filter
    if (filter.dateRange) {
      const eventDate = new Date(event.timestamp_ms);
      if (eventDate < filter.dateRange.start || eventDate > filter.dateRange.end) {
        return false;
      }
    }
    
    return true;
  });
};

/**
 * Simple text-based event filtering
 * Quick filter for search term across event fields
 * 
 * @param events - Array of events to filter
 * @param searchTerm - Text to search for
 * @param includePayload - Whether to search in payload
 * @returns Filtered events array
 */
export const filterEventsByText = (
  events: Event[],
  searchTerm: string,
  includePayload: boolean = true
): Event[] => {
  if (!searchTerm.trim()) {
    return events;
  }
  
  const term = searchTerm.toLowerCase();
  
  return events.filter(event => {
    const searchableFields = [
      event.event_type,
      event.user_id,
      event.session_id,
      event.event_id,
    ];
    
    // Search in basic fields
    const basicMatch = searchableFields.some(field => 
      field.toLowerCase().includes(term)
    );
    
    if (basicMatch) {
      return true;
    }
    
    // Search in payload if enabled
    if (includePayload) {
      try {
        const payloadString = JSON.stringify(event.payload).toLowerCase();
        return payloadString.includes(term);
      } catch {
        return false;
      }
    }
    
    return false;
  });
};

/**
 * Get event type metadata
 * Retrieves styling and display information for event type
 * 
 * @param eventType - Event type string
 * @returns Event type metadata
 */
export const getEventTypeMetadata = (eventType: string): EventTypeMetadata => {
  return EVENT_TYPE_METADATA[eventType] || EVENT_TYPE_METADATA.unknown;
};

/**
 * Generate unique event key for React rendering
 * Creates stable key for event list rendering
 * 
 * @param event - Event object
 * @returns Unique key string
 */
export const getEventKey = (event: Event): string => {
  return `${event.event_id}-${event.timestamp_ms}`;
};

/**
 * Sort events by timestamp
 * Sorts events in chronological order
 * 
 * @param events - Array of events to sort
 * @param ascending - Whether to sort in ascending order
 * @returns Sorted events array
 */
export const sortEventsByTimestamp = (events: Event[], ascending: boolean = false): Event[] => {
  return [...events].sort((a, b) => {
    const diff = a.timestamp_ms - b.timestamp_ms;
    return ascending ? diff : -diff;
  });
};

/**
 * Group events by time period
 * Groups events into time buckets for analysis
 * 
 * @param events - Array of events to group
 * @param periodMs - Time period in milliseconds
 * @returns Grouped events by time period
 */
export const groupEventsByTimePeriod = (
  events: Event[],
  periodMs: number
): Record<string, Event[]> => {
  const groups: Record<string, Event[]> = {};
  
  events.forEach(event => {
    const periodStart = Math.floor(event.timestamp_ms / periodMs) * periodMs;
    const key = new Date(periodStart).toISOString();
    
    if (!groups[key]) {
      groups[key] = [];
    }
    
    groups[key].push(event);
  });
  
  return groups;
};

/**
 * Calculate event statistics
 * Computes metrics about event distribution
 * 
 * @param events - Array of events to analyze
 * @returns Event statistics
 */
export const calculateEventStats = (events: Event[]) => {
  const stats = {
    total: events.length,
    byType: {} as Record<string, number>,
    byUser: {} as Record<string, number>,
    bySession: {} as Record<string, number>,
    timeRange: {
      earliest: 0,
      latest: 0,
      span: 0,
    },
    eventsPerSecond: 0,
  };
  
  if (events.length === 0) {
    return stats;
  }
  
  // Count by type, user, and session
  events.forEach(event => {
    stats.byType[event.event_type] = (stats.byType[event.event_type] || 0) + 1;
    stats.byUser[event.user_id] = (stats.byUser[event.user_id] || 0) + 1;
    stats.bySession[event.session_id] = (stats.bySession[event.session_id] || 0) + 1;
  });
  
  // Calculate time range
  const timestamps = events.map(e => e.timestamp_ms);
  stats.timeRange.earliest = Math.min(...timestamps);
  stats.timeRange.latest = Math.max(...timestamps);
  stats.timeRange.span = stats.timeRange.latest - stats.timeRange.earliest;
  
  // Calculate events per second
  if (stats.timeRange.span > 0) {
    stats.eventsPerSecond = (events.length / stats.timeRange.span) * 1000;
  }
  
  return stats;
};

/**
 * Truncate text with ellipsis
 * Safely truncates text to specified length
 * 
 * @param text - Text to truncate
 * @param maxLength - Maximum length
 * @param ellipsis - Ellipsis string
 * @returns Truncated text
 */
export const truncateText = (
  text: string,
  maxLength: number,
  ellipsis: string = '...'
): string => {
  if (text.length <= maxLength) {
    return text;
  }
  
  return text.slice(0, maxLength - ellipsis.length) + ellipsis;
};

/**
 * Debounce function for performance optimization
 * Creates debounced version of function
 * 
 * @param func - Function to debounce
 * @param delay - Delay in milliseconds
 * @returns Debounced function
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

/**
 * Check if events array exceeds performance thresholds
 * Monitors performance and suggests optimizations
 * 
 * @param events - Array of events to check
 * @returns Performance warnings
 */
export const checkPerformanceThresholds = (events: Event[]) => {
  const warnings: string[] = [];
  
  if (events.length > PERFORMANCE_THRESHOLDS.maxEventsWarning) {
    warnings.push(`High event count: ${events.length} events may impact performance`);
  }
  
  if (events.length > PERFORMANCE_THRESHOLDS.maxEventsLimit) {
    warnings.push(`Event limit exceeded: ${events.length} events, consider cleanup`);
  }
  
  // Estimate memory usage (rough calculation)
  const estimatedMemoryMB = (JSON.stringify(events).length / 1024 / 1024);
  if (estimatedMemoryMB > PERFORMANCE_THRESHOLDS.maxMemoryUsage) {
    warnings.push(`High memory usage: ~${estimatedMemoryMB.toFixed(1)}MB`);
  }
  
  return warnings;
};

/**
 * Sanitize event data for display
 * Removes sensitive information from events
 * 
 * @param event - Event to sanitize
 * @returns Sanitized event
 */
export const sanitizeEvent = (event: Event): Event => {
  const sanitized = { ...event };
  
  // Remove potentially sensitive payload fields
  if (sanitized.payload && typeof sanitized.payload === 'object') {
    const { password, token, apiKey, secret, ...safePayload } = sanitized.payload;
    sanitized.payload = safePayload;
  }
  
  return sanitized;
};
