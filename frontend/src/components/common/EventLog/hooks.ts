// ============================================================================
// EventLog Hooks - React Hooks for Event Log Functionality
// ============================================================================
//
// @file hooks.ts
// @version 2.0.0
// @author Unhinged Design System Team
// @date 2025-10-06
// @description Custom React hooks for event log state management
//
// Etymology: "Hook" = React pattern for stateful logic
// Methodology: Composable hooks following React patterns
// ============================================================================

import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { 
  Event, 
  EventLogState, 
  UseEventLogReturn, 
  ConnectionStatus,
  EventLogMetrics,
  WebSocketMessage 
} from './types';
import { 
  DEFAULT_CONFIG, 
  WEBSOCKET_CONFIG, 
  PERFORMANCE_THRESHOLDS,
  STORAGE_KEYS 
} from './constants';
import { 
  filterEventsByText, 
  calculateEventStats, 
  checkPerformanceThresholds,
  debounce 
} from './utils';

/**
 * Hook for managing event log state and WebSocket connection
 * Provides complete event log functionality with real-time updates
 * 
 * @param maxEvents - Maximum number of events to keep
 * @param wsUrl - WebSocket URL for real-time updates
 * @param apiEndpoint - API endpoint for initial events
 * @returns Event log state and actions
 */
export const useEventLog = (
  maxEvents: number = DEFAULT_CONFIG.defaultMaxEvents,
  wsUrl?: string,
  apiEndpoint: string = '/api/events'
): UseEventLogReturn => {
  const [state, setState] = useState<EventLogState>({
    events: [],
    connectionStatus: 'disconnected',
    filter: '',
    autoScroll: true,
    isLoading: false,
    error: null,
    filteredCount: 0,
    totalCount: 0,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const metricsRef = useRef<EventLogMetrics>({
    totalEvents: 0,
    eventsPerSecond: 0,
    connectionUptime: 0,
    reconnectionAttempts: 0,
    averageProcessingTime: 0,
    memoryUsage: 0,
  });

  /**
   * Load initial events from API
   */
  const loadInitialEvents = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const response = await fetch(apiEndpoint);
      if (!response.ok) {
        throw new Error(`Failed to load events: ${response.statusText}`);
      }
      
      const events: Event[] = await response.json();
      
      setState(prev => ({
        ...prev,
        events: events.slice(0, maxEvents),
        totalCount: events.length,
        isLoading: false,
      }));
      
      metricsRef.current.totalEvents = events.length;
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to load events',
        isLoading: false,
      }));
    }
  }, [apiEndpoint, maxEvents]);

  /**
   * Connect to WebSocket for real-time events
   */
  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setState(prev => ({ ...prev, connectionStatus: 'connecting' }));

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const url = wsUrl || `${protocol}//${window.location.host}${WEBSOCKET_CONFIG.DEFAULT_PATH}`;
    
    try {
      wsRef.current = new WebSocket(url);
      
      wsRef.current.onopen = () => {
        setState(prev => ({ ...prev, connectionStatus: 'connected', error: null }));
        reconnectAttemptsRef.current = 0;
        metricsRef.current.connectionUptime = Date.now();
      };

      wsRef.current.onmessage = (event) => {
        try {
          const startTime = performance.now();
          const message: WebSocketMessage = JSON.parse(event.data);
          
          if (message.type === 'event' && message.data) {
            const newEvent: Event = message.data;
            
            setState(prev => {
              const updatedEvents = [newEvent, ...prev.events].slice(0, maxEvents);
              return {
                ...prev,
                events: updatedEvents,
                totalCount: prev.totalCount + 1,
              };
            });
            
            metricsRef.current.totalEvents++;
            
            // Update processing time metric
            const processingTime = performance.now() - startTime;
            metricsRef.current.averageProcessingTime = 
              (metricsRef.current.averageProcessingTime + processingTime) / 2;
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      wsRef.current.onclose = () => {
        setState(prev => ({ ...prev, connectionStatus: 'disconnected' }));
        
        // Attempt reconnection with exponential backoff
        if (reconnectAttemptsRef.current < DEFAULT_CONFIG.reconnection.maxAttempts) {
          const delay = DEFAULT_CONFIG.reconnection.exponentialBackoff
            ? Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000)
            : DEFAULT_CONFIG.reconnection.delay;
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            metricsRef.current.reconnectionAttempts++;
            connectWebSocket();
          }, delay);
        }
      };

      wsRef.current.onerror = () => {
        setState(prev => ({ ...prev, connectionStatus: 'error' }));
      };
    } catch (error) {
      setState(prev => ({
        ...prev,
        connectionStatus: 'error',
        error: 'Failed to connect to WebSocket',
      }));
    }
  }, [wsUrl, maxEvents]);

  /**
   * Disconnect from WebSocket
   */
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setState(prev => ({ ...prev, connectionStatus: 'disconnected' }));
  }, []);

  /**
   * Set filter with debouncing for performance
   */
  const debouncedSetFilter = useMemo(
    () => debounce((filter: string) => {
      setState(prev => ({ ...prev, filter }));
    }, DEFAULT_CONFIG.performance.filterDebounce),
    []
  );

  /**
   * Actions object with all available operations
   */
  const actions = useMemo(() => ({
    setFilter: (filter: string) => {
      debouncedSetFilter(filter);
    },
    
    toggleAutoScroll: () => {
      setState(prev => {
        const newAutoScroll = !prev.autoScroll;
        localStorage.setItem(STORAGE_KEYS.autoScroll, JSON.stringify(newAutoScroll));
        return { ...prev, autoScroll: newAutoScroll };
      });
    },
    
    clearEvents: () => {
      setState(prev => ({
        ...prev,
        events: [],
        totalCount: 0,
        filteredCount: 0,
      }));
      metricsRef.current.totalEvents = 0;
    },
    
    refreshEvents: loadInitialEvents,
    
    connect: connectWebSocket,
    
    disconnect,
  }), [debouncedSetFilter, loadInitialEvents, connectWebSocket, disconnect]);

  /**
   * Filter events based on current filter
   */
  const filteredEvents = useMemo(() => {
    const filtered = filterEventsByText(state.events, state.filter, true);
    
    // Update filtered count
    setState(prev => ({ ...prev, filteredCount: filtered.length }));
    
    return filtered;
  }, [state.events, state.filter]);

  /**
   * Calculate current metrics
   */
  const metrics = useMemo(() => {
    const stats = calculateEventStats(state.events);
    const warnings = checkPerformanceThresholds(state.events);
    
    return {
      ...metricsRef.current,
      eventsPerSecond: stats.eventsPerSecond,
      memoryUsage: JSON.stringify(state.events).length / 1024 / 1024, // MB
      warnings,
    };
  }, [state.events]);

  /**
   * Load user preferences on mount
   */
  useEffect(() => {
    try {
      const savedAutoScroll = localStorage.getItem(STORAGE_KEYS.autoScroll);
      const savedFilter = localStorage.getItem(STORAGE_KEYS.filter);
      
      setState(prev => ({
        ...prev,
        autoScroll: savedAutoScroll ? JSON.parse(savedAutoScroll) : true,
        filter: savedFilter || '',
      }));
    } catch (error) {
      console.warn('Failed to load event log preferences:', error);
    }
  }, []);

  /**
   * Initialize connection and load events on mount
   */
  useEffect(() => {
    loadInitialEvents();
    connectWebSocket();
    
    return () => {
      disconnect();
    };
  }, [loadInitialEvents, connectWebSocket, disconnect]);

  /**
   * Save filter to localStorage when it changes
   */
  useEffect(() => {
    if (state.filter) {
      localStorage.setItem(STORAGE_KEYS.filter, state.filter);
    } else {
      localStorage.removeItem(STORAGE_KEYS.filter);
    }
  }, [state.filter]);

  return {
    state,
    actions,
    filteredEvents,
    metrics,
  };
};

/**
 * Hook for managing auto-scroll behavior
 * Handles automatic scrolling to new events
 * 
 * @param containerRef - Ref to scroll container
 * @param autoScroll - Whether auto-scroll is enabled
 * @param events - Events array to watch for changes
 */
export const useAutoScroll = (
  containerRef: React.RefObject<HTMLElement | null>,
  autoScroll: boolean,
  events: Event[]
) => {
  const prevEventsLengthRef = useRef(events.length);

  useEffect(() => {
    if (autoScroll && containerRef.current && events.length > prevEventsLengthRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
    
    prevEventsLengthRef.current = events.length;
  }, [autoScroll, events, containerRef]);

  /**
   * Handle scroll events to detect if user scrolled away from bottom
   */
  const handleScroll = useCallback(() => {
    if (!containerRef.current) return false;
    
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const isAtBottom = scrollTop + clientHeight >= scrollHeight - 10;
    
    return isAtBottom;
  }, [containerRef]);

  return { handleScroll };
};

/**
 * Hook for managing event log preferences
 * Handles user preferences and settings persistence
 */
export const useEventLogPreferences = () => {
  const [preferences, setPreferences] = useState({
    autoScroll: true,
    showMetadata: true,
    showPayload: true,
    timestampFormat: 'absolute' as const,
    maxEvents: DEFAULT_CONFIG.defaultMaxEvents,
    filter: '',
  });

  /**
   * Load preferences from localStorage
   */
  const loadPreferences = useCallback(() => {
    try {
      const keys = Object.keys(STORAGE_KEYS) as Array<keyof typeof STORAGE_KEYS>;
      const loaded = {} as typeof preferences;
      
      keys.forEach(key => {
        const stored = localStorage.getItem(STORAGE_KEYS[key]);
        if (stored) {
          try {
            (loaded as any)[key] = JSON.parse(stored);
          } catch {
            // Ignore invalid JSON
          }
        }
      });
      
      setPreferences(prev => ({ ...prev, ...loaded }));
    } catch (error) {
      console.warn('Failed to load event log preferences:', error);
    }
  }, []);

  /**
   * Save preferences to localStorage
   */
  const savePreferences = useCallback((newPreferences: Partial<typeof preferences>) => {
    try {
      const updated = { ...preferences, ...newPreferences };
      setPreferences(updated);
      
      Object.entries(newPreferences).forEach(([key, value]) => {
        const storageKey = STORAGE_KEYS[key as keyof typeof STORAGE_KEYS];
        if (storageKey) {
          localStorage.setItem(storageKey, JSON.stringify(value));
        }
      });
    } catch (error) {
      console.warn('Failed to save event log preferences:', error);
    }
  }, [preferences]);

  // Load preferences on mount
  useEffect(() => {
    loadPreferences();
  }, [loadPreferences]);

  return {
    preferences,
    savePreferences,
    loadPreferences,
  };
};
