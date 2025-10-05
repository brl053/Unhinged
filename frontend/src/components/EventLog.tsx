/**
 * @fileoverview Event Log Component
 * 
 * @description
 * Real-time event log viewer for CDC events. Shows raw JSON events
 * with WebSocket updates and basic filtering.
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import React, { useState, useEffect, useRef } from 'react';
import './EventLog.css';

interface Event {
  event_id: string;
  event_type: string;
  timestamp_ms: number;
  user_id: string;
  session_id: string;
  payload: any;
  created_at: string;
}

export const EventLog: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [filter, setFilter] = useState('');
  const [autoScroll, setAutoScroll] = useState(true);
  const wsRef = useRef<WebSocket | null>(null);
  const logContainerRef = useRef<HTMLDivElement>(null);

  // Connect to WebSocket and load initial events
  useEffect(() => {
    loadInitialEvents();
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Auto-scroll to bottom when new events arrive
  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [events, autoScroll]);

  /**
   * Load initial events from API
   */
  const loadInitialEvents = async () => {
    try {
      const response = await fetch('/api/events');
      if (response.ok) {
        const initialEvents = await response.json();
        setEvents(initialEvents);
      }
    } catch (error) {
      console.error('Failed to load initial events:', error);
    }
  };

  /**
   * Connect to WebSocket for real-time events
   */
  const connectWebSocket = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/events/stream`;
    
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      console.log('📡 WebSocket connected');
      setIsConnected(true);
    };

    wsRef.current.onmessage = (event) => {
      try {
        const newEvent = JSON.parse(event.data);
        setEvents(prev => [newEvent, ...prev].slice(0, 1000)); // Keep last 1000 events
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    wsRef.current.onclose = () => {
      console.log('📡 WebSocket disconnected');
      setIsConnected(false);
      
      // Reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000);
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };
  };

  /**
   * Clear all events
   */
  const clearEvents = () => {
    setEvents([]);
  };

  /**
   * Format timestamp for display
   */
  const formatTimestamp = (timestampMs: number): string => {
    return new Date(timestampMs).toLocaleString();
  };

  /**
   * Format JSON for display
   */
  const formatJSON = (obj: any): string => {
    return JSON.stringify(obj, null, 2);
  };

  /**
   * Filter events based on search term
   */
  const filteredEvents = events.filter(event => {
    if (!filter) return true;
    
    const searchTerm = filter.toLowerCase();
    return (
      event.event_type.toLowerCase().includes(searchTerm) ||
      event.user_id.toLowerCase().includes(searchTerm) ||
      event.session_id.toLowerCase().includes(searchTerm) ||
      JSON.stringify(event.payload).toLowerCase().includes(searchTerm)
    );
  });

  return (
    <div className="event-log">
      {/* Header */}
      <div className="event-log-header">
        <h2>🔍 Event Log</h2>
        <div className="event-log-controls">
          <div className="connection-status">
            <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
              {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
            </span>
          </div>
          
          <input
            type="text"
            placeholder="Filter events..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="filter-input"
          />
          
          <label className="auto-scroll-toggle">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
            />
            Auto-scroll
          </label>
          
          <button onClick={clearEvents} className="clear-button">
            Clear
          </button>
        </div>
      </div>

      {/* Event count */}
      <div className="event-count">
        Showing {filteredEvents.length} of {events.length} events
      </div>

      {/* Event list */}
      <div 
        className="event-log-container" 
        ref={logContainerRef}
        onScroll={() => {
          if (logContainerRef.current) {
            const { scrollTop, scrollHeight, clientHeight } = logContainerRef.current;
            const isAtBottom = scrollTop + clientHeight >= scrollHeight - 10;
            setAutoScroll(isAtBottom);
          }
        }}
      >
        {filteredEvents.length === 0 ? (
          <div className="no-events">
            {events.length === 0 ? (
              <p>No events yet. Try making an LLM inference request.</p>
            ) : (
              <p>No events match the current filter.</p>
            )}
          </div>
        ) : (
          filteredEvents.map((event) => (
            <div key={event.event_id} className="event-item">
              <div className="event-header">
                <span className="event-type">{event.event_type}</span>
                <span className="event-timestamp">
                  {formatTimestamp(event.timestamp_ms)}
                </span>
                <span className="event-id">{event.event_id}</span>
              </div>
              
              <div className="event-metadata">
                <span>User: {event.user_id}</span>
                <span>Session: {event.session_id}</span>
              </div>
              
              <div className="event-payload">
                <details>
                  <summary>Payload</summary>
                  <pre className="json-payload">
                    {formatJSON(event.payload)}
                  </pre>
                </details>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
