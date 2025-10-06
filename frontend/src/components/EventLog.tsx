// ============================================================================
// Event Log - Real-time Event Viewer
// ============================================================================
//
// @file EventLog.tsx
// @version 2.0.0
// @author Unhinged Design System Team
// @date 2025-10-06
// @description Real-time event log viewer with WebSocket integration
//
// This component provides:
// - Real-time event streaming via WebSocket
// - Event filtering and search
// - Auto-scroll functionality
// - Connection status monitoring
// - Event type categorization
// ============================================================================

import React, { useRef } from 'react';
import styled from 'styled-components';
import { EventLogProps } from './common/EventLog/types';
import { useEventLog, useAutoScroll } from './common/EventLog/hooks';
import { 
  formatTimestamp, 
  formatJSON, 
  getEventTypeMetadata, 
  getEventKey,
  truncateText 
} from './common/EventLog/utils';
import { CONNECTION_STATUS_METADATA } from './common/EventLog/constants';
import {
  eventLogContainerStyles,
  eventLogHeaderStyles,
  eventLogTitleStyles,
  eventLogControlsStyles,
  connectionStatusStyles,
  filterInputStyles,
  autoScrollToggleStyles,
  clearButtonStyles,
  eventCountStyles,
  eventListContainerStyles,
  noEventsStyles,
  eventItemStyles,
  eventHeaderStyles,
  eventTypeStyles,
  eventTimestampStyles,
  eventIdStyles,
  eventMetadataStyles,
  eventPayloadStyles,
  jsonPayloadStyles,
  loadingSpinnerStyles,
  errorMessageStyles
} from './common/EventLog/styles';

// ============================================================================
// Styled Components
// ============================================================================

const EventLogContainer = styled.div`
  ${eventLogContainerStyles}
`;

const EventLogHeader = styled.div`
  ${eventLogHeaderStyles}
`;

const EventLogTitle = styled.h2`
  ${eventLogTitleStyles}
`;

const EventLogControls = styled.div`
  ${eventLogControlsStyles}
`;

const ConnectionStatus = styled.div`
  ${connectionStatusStyles}
`;

const FilterInput = styled.input`
  ${filterInputStyles}
`;

const AutoScrollToggle = styled.label`
  ${autoScrollToggleStyles}
`;

const ClearButton = styled.button`
  ${clearButtonStyles}
`;

const EventCount = styled.div`
  ${eventCountStyles}
`;

const EventListContainer = styled.div`
  ${eventListContainerStyles}
`;

const NoEvents = styled.div`
  ${noEventsStyles}
`;

const EventItem = styled.div`
  ${eventItemStyles}
`;

const EventHeader = styled.div`
  ${eventHeaderStyles}
`;

const EventType = styled.span`
  ${eventTypeStyles}
`;

const EventTimestamp = styled.span`
  ${eventTimestampStyles}
`;

const EventId = styled.span`
  ${eventIdStyles}
`;

const EventMetadata = styled.div`
  ${eventMetadataStyles}
`;

const EventPayload = styled.div`
  ${eventPayloadStyles}
`;

const JsonPayload = styled.pre`
  ${jsonPayloadStyles}
`;

const LoadingSpinner = styled.div`
  ${loadingSpinnerStyles}
`;

const ErrorMessage = styled.div`
  ${errorMessageStyles}
`;

// ============================================================================
// Event Log Component
// ============================================================================

export const EventLog: React.FC<EventLogProps> = ({
  maxEvents = 1000,
  autoScroll: initialAutoScroll = true,
  initialFilter = '',
  wsUrl,
  apiEndpoint = '/api/events',
  showMetadata = true,
  showPayload = true,
  eventTypeColors = {},
  onEventsUpdate,
  onConnectionChange,
}) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  
  // Use event log hook for state management
  const { state, actions, filteredEvents, metrics } = useEventLog(
    maxEvents,
    wsUrl,
    apiEndpoint
  );
  
  // Use auto-scroll hook
  useAutoScroll(containerRef, state.autoScroll, state.events);
  
  // Notify parent components of changes
  React.useEffect(() => {
    onEventsUpdate?.(state.events);
  }, [state.events, onEventsUpdate]);
  
  React.useEffect(() => {
    onConnectionChange?.(state.connectionStatus);
  }, [state.connectionStatus, onConnectionChange]);
  
  // Get connection status metadata
  const connectionMeta = CONNECTION_STATUS_METADATA[state.connectionStatus];
  
  return (
    <EventLogContainer>
      {/* Header with title and controls */}
      <EventLogHeader>
        <EventLogTitle>
          📊 Event Log
          <ConnectionStatus 
            data-status={state.connectionStatus}
            title={`Connection: ${connectionMeta.label}`}
          >
            {connectionMeta.icon} {connectionMeta.label}
          </ConnectionStatus>
        </EventLogTitle>
        
        <EventLogControls>
          <FilterInput
            type="text"
            placeholder="Filter events..."
            value={state.filter}
            onChange={(e) => actions.setFilter(e.target.value)}
          />
          
          <AutoScrollToggle>
            <input
              type="checkbox"
              checked={state.autoScroll}
              onChange={actions.toggleAutoScroll}
            />
            Auto-scroll
          </AutoScrollToggle>
          
          <ClearButton
            onClick={actions.clearEvents}
            disabled={state.events.length === 0}
          >
            Clear
          </ClearButton>
        </EventLogControls>
      </EventLogHeader>
      
      {/* Event count information */}
      <EventCount>
        Showing {state.filteredCount} of {state.totalCount} events
        {state.filter && ` (filtered by "${state.filter}")`}
        {metrics.warnings && metrics.warnings.length > 0 && (
          <span style={{ color: '#f59e0b', marginLeft: '16px' }}>
            ⚠️ {metrics.warnings[0]}
          </span>
        )}
      </EventCount>
      
      {/* Event list */}
      <EventListContainer ref={containerRef}>
        {state.isLoading && (
          <LoadingSpinner>
            Loading events...
          </LoadingSpinner>
        )}
        
        {state.error && (
          <ErrorMessage>
            {state.error}
          </ErrorMessage>
        )}
        
        {!state.isLoading && !state.error && filteredEvents.length === 0 && (
          <NoEvents>
            {state.filter ? 'No events match your filter' : 'No events to display'}
          </NoEvents>
        )}
        
        {filteredEvents.map((event) => {
          const eventMeta = getEventTypeMetadata(event.event_type);
          const customColor = eventTypeColors[event.event_type];
          
          return (
            <EventItem key={getEventKey(event)}>
              <EventHeader>
                <EventType
                  data-event-type={event.event_type}
                  style={customColor ? { backgroundColor: customColor } : {}}
                >
                  {eventMeta.icon} {eventMeta.displayName || event.event_type}
                </EventType>
                
                <EventTimestamp>
                  {formatTimestamp(event.timestamp_ms, 'absolute', true)}
                </EventTimestamp>
                
                <EventId>
                  {truncateText(event.event_id, 12)}
                </EventId>
              </EventHeader>
              
              {showMetadata && (
                <EventMetadata>
                  <span>User: {event.user_id}</span>
                  <span>Session: {truncateText(event.session_id, 16)}</span>
                </EventMetadata>
              )}
              
              {showPayload && event.payload && (
                <EventPayload>
                  <details>
                    <summary>Payload</summary>
                    <JsonPayload>
                      {formatJSON(event.payload, 2, 2000)}
                    </JsonPayload>
                  </details>
                </EventPayload>
              )}
            </EventItem>
          );
        })}
      </EventListContainer>
    </EventLogContainer>
  );
};

// Default export for convenience
export default EventLog;
