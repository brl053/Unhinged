// ============================================================================
// Event Feed Component - Real-time Event Visualization in Chat
// ============================================================================
//
// @file EventFeed.tsx
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Live event feed showing system events in the chat interface
//
// This component provides:
// - Real-time event display in chat window
// - Audio processing event visualization
// - System event debugging in UI
// - Event filtering and categorization
// - Collapsible event details
// ============================================================================

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

// Event display types
interface EventDisplayProps {
  events: EventItem[];
  maxEvents?: number;
  showTimestamps?: boolean;
  collapsible?: boolean;
}

interface EventItem {
  id: string;
  type: string;
  source: string;
  data: any;
  metadata?: any;
  timestamp: string;
  severity?: 'info' | 'warn' | 'error' | 'success';
}

// Styled components
const EventFeedContainer = styled.div`
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  padding: 12px;
  margin: 8px 0;
  border-left: 3px solid #007bff;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  max-height: 300px;
  overflow-y: auto;
`;

const EventFeedHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-weight: bold;
  color: #333;
  cursor: pointer;
  user-select: none;
  
  &:hover {
    color: #007bff;
  }
`;

const EventItem = styled.div<{ severity?: string }>`
  padding: 6px 8px;
  margin: 4px 0;
  border-radius: 4px;
  background: ${props => {
    switch (props.severity) {
      case 'error': return 'rgba(220, 53, 69, 0.1)';
      case 'warn': return 'rgba(255, 193, 7, 0.1)';
      case 'success': return 'rgba(40, 167, 69, 0.1)';
      default: return 'rgba(108, 117, 125, 0.1)';
    }
  }};
  border-left: 2px solid ${props => {
    switch (props.severity) {
      case 'error': return '#dc3545';
      case 'warn': return '#ffc107';
      case 'success': return '#28a745';
      default: return '#6c757d';
    }
  }};
`;

const EventType = styled.span<{ severity?: string }>`
  font-weight: bold;
  color: ${props => {
    switch (props.severity) {
      case 'error': return '#dc3545';
      case 'warn': return '#856404';
      case 'success': return '#155724';
      default: return '#495057';
    }
  }};
`;

const EventSource = styled.span`
  color: #6c757d;
  font-size: 10px;
  margin-left: 8px;
`;

const EventTimestamp = styled.span`
  color: #6c757d;
  font-size: 10px;
  float: right;
`;

const EventData = styled.div`
  margin-top: 4px;
  padding-left: 8px;
  color: #495057;
  font-size: 11px;
`;

const EventToggle = styled.span`
  font-size: 14px;
  color: #6c757d;
`;

const ClearButton = styled.button`
  background: none;
  border: none;
  color: #6c757d;
  font-size: 10px;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 3px;
  
  &:hover {
    background: rgba(108, 117, 125, 0.1);
    color: #495057;
  }
`;

/**
 * Event Feed Component
 */
export const EventFeed: React.FC<EventDisplayProps> = ({
  events,
  maxEvents = 20,
  showTimestamps = true,
  collapsible = true
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [displayEvents, setDisplayEvents] = useState<EventItem[]>([]);

  useEffect(() => {
    // Keep only the most recent events
    const recentEvents = events.slice(-maxEvents).reverse();
    setDisplayEvents(recentEvents);
  }, [events, maxEvents]);

  const formatEventType = (type: string): string => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getEventSeverity = (event: EventItem): 'info' | 'warn' | 'error' | 'success' => {
    if (event.type.includes('error') || event.type.includes('failed')) return 'error';
    if (event.type.includes('warn') || event.type.includes('timeout')) return 'warn';
    if (event.type.includes('completed') || event.type.includes('success') || event.type.includes('started')) return 'success';
    return 'info';
  };

  const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }) + '.' + date.getMilliseconds().toString().padStart(3, '0');
  };

  const formatEventData = (data: any): string => {
    if (!data || Object.keys(data).length === 0) return '';
    
    // Show key information for different event types
    const keyInfo: string[] = [];
    
    if (data.sessionId) keyInfo.push(`session: ${data.sessionId.slice(-8)}`);
    if (data.duration) keyInfo.push(`duration: ${data.duration}ms`);
    if (data.audioSize) keyInfo.push(`size: ${(data.audioSize / 1024).toFixed(1)}KB`);
    if (data.transcriptionText) keyInfo.push(`text: "${data.transcriptionText.slice(0, 30)}${data.transcriptionText.length > 30 ? '...' : ''}"`);
    if (data.language) keyInfo.push(`lang: ${data.language}`);
    if (data.processingTimeMs) keyInfo.push(`processed: ${data.processingTimeMs}ms`);
    if (data.confidence) keyInfo.push(`confidence: ${(data.confidence * 100).toFixed(1)}%`);
    if (data.error) keyInfo.push(`error: ${data.error}`);
    if (data.messageContent) keyInfo.push(`content: "${data.messageContent.slice(0, 30)}${data.messageContent.length > 30 ? '...' : ''}"`);
    if (data.messageRole) keyInfo.push(`role: ${data.messageRole}`);
    if (data.messageSource) keyInfo.push(`source: ${data.messageSource}`);
    
    return keyInfo.join(', ');
  };

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    setDisplayEvents([]);
  };

  if (displayEvents.length === 0) {
    return null;
  }

  return (
    <EventFeedContainer>
      <EventFeedHeader onClick={() => collapsible && setIsCollapsed(!isCollapsed)}>
        <div>
          {collapsible && (
            <EventToggle>{isCollapsed ? '▶' : '▼'}</EventToggle>
          )}
          <span style={{ marginLeft: collapsible ? '8px' : '0' }}>
            🔍 Live Events ({displayEvents.length})
          </span>
        </div>
        <ClearButton onClick={handleClear}>clear</ClearButton>
      </EventFeedHeader>
      
      {!isCollapsed && (
        <div>
          {displayEvents.map((event) => {
            const severity = getEventSeverity(event);
            const eventData = formatEventData(event.data);
            
            return (
              <EventItem key={event.id} severity={severity}>
                <div>
                  <EventType severity={severity}>
                    {formatEventType(event.type)}
                  </EventType>
                  <EventSource>({event.source})</EventSource>
                  {showTimestamps && (
                    <EventTimestamp>
                      {formatTimestamp(event.timestamp)}
                    </EventTimestamp>
                  )}
                </div>
                {eventData && (
                  <EventData>{eventData}</EventData>
                )}
              </EventItem>
            );
          })}
        </div>
      )}
    </EventFeedContainer>
  );
};

/**
 * Hook for managing event feed state
 */
export const useEventFeed = () => {
  const [events, setEvents] = useState<EventItem[]>([]);

  const addEvent = (event: Omit<EventItem, 'id' | 'timestamp'>) => {
    const newEvent: EventItem = {
      ...event,
      id: `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString()
    };
    
    setEvents(prev => [...prev, newEvent]);
  };

  const clearEvents = () => {
    setEvents([]);
  };

  return {
    events,
    addEvent,
    clearEvents
  };
};

export default EventFeed;
