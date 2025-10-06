import { useState, useEffect, useMemo } from 'react';
import { EventItem } from './types';
import { EVENT_FEED_CONSTANTS } from './constants';
import { sortEventsBySeverity, filterRecentEvents, limitEvents } from './utils';

export const useEventFeed = (
  initialEvents: EventItem[] = [],
  maxEvents: number = EVENT_FEED_CONSTANTS.DEFAULT_MAX_EVENTS
) => {
  const [events, setEvents] = useState<EventItem[]>(initialEvents);
  const [isCollapsed, setIsCollapsed] = useState(false);

  const processedEvents = useMemo(() => {
    const recentEvents = filterRecentEvents(events);
    const sortedEvents = sortEventsBySeverity(recentEvents);
    return limitEvents(sortedEvents, maxEvents);
  }, [events, maxEvents]);

  const addEvent = (event: EventItem) => {
    setEvents(prev => [event, ...prev]);
  };

  const clearEvents = () => {
    setEvents([]);
  };

  const toggleCollapsed = () => {
    setIsCollapsed(prev => !prev);
  };

  const eventCounts = useMemo(() => {
    return processedEvents.reduce((counts, event) => {
      const severity = event.severity || 'info';
      counts[severity] = (counts[severity] || 0) + 1;
      return counts;
    }, {} as Record<string, number>);
  }, [processedEvents]);

  return {
    events,
    processedEvents,
    addEvent,
    clearEvents,
    isCollapsed,
    toggleCollapsed,
    eventCounts,
  };
};
