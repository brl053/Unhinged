import { EventItem, EventSeverity } from './types';
import { EVENT_FEED_CONSTANTS, EVENT_SEVERITY_ORDER } from './constants';

export const formatTimestamp = (timestamp: string): string => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('en-US', { 
    hour12: false, 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit' 
  });
};

export const formatEventData = (data: any): string => {
  if (typeof data === 'string') {
    return data;
  }
  
  if (typeof data === 'object' && data !== null) {
    try {
      return JSON.stringify(data, null, 2);
    } catch {
      return String(data);
    }
  }
  
  return String(data);
};

export const sortEventsBySeverity = (events: EventItem[]): EventItem[] => {
  return [...events].sort((a, b) => {
    const severityA = a.severity || 'info';
    const severityB = b.severity || 'info';
    
    const orderA = EVENT_SEVERITY_ORDER[severityA];
    const orderB = EVENT_SEVERITY_ORDER[severityB];
    
    if (orderA !== orderB) {
      return orderA - orderB;
    }
    
    // If same severity, sort by timestamp (newest first)
    return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
  });
};

export const filterRecentEvents = (events: EventItem[]): EventItem[] => {
  const now = Date.now();
  const cutoff = now - EVENT_FEED_CONSTANTS.EVENT_RETENTION_TIME;
  
  return events.filter(event => {
    const eventTime = new Date(event.timestamp).getTime();
    return eventTime > cutoff;
  });
};

export const limitEvents = (events: EventItem[], maxEvents: number): EventItem[] => {
  return events.slice(0, maxEvents);
};

export const createEventItem = (
  type: string,
  source: string,
  data: any,
  severity?: EventSeverity,
  metadata?: any
): EventItem => {
  return {
    id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    type,
    source,
    data,
    metadata,
    timestamp: new Date().toISOString(),
    severity,
  };
};
