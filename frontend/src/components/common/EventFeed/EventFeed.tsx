import React from 'react';
import { EventFeedProps } from './types';
import { useEventFeed } from './hooks';
import { formatTimestamp, formatEventData } from './utils';
import {
  StyledEventFeedContainer,
  StyledEventFeedHeader,
  StyledEventItem,
  StyledEventType,
  StyledEventTimestamp,
  StyledEventData,
  StyledCollapseIcon,
} from './styles';

export const EventFeed: React.FC<EventFeedProps> = ({
  events,
  maxEvents,
  showTimestamps = true,
  collapsible = true,
  className,
}) => {
  const { processedEvents, isCollapsed, toggleCollapsed, eventCounts } = useEventFeed(events, maxEvents);

  const renderEventCounts = () => {
    const counts = Object.entries(eventCounts)
      .filter(([, count]) => count > 0)
      .map(([severity, count]) => `${severity}: ${count}`)
      .join(', ');
    
    return counts ? ` (${counts})` : '';
  };

  return (
    <StyledEventFeedContainer className={className} collapsible={collapsible}>
      {collapsible && (
        <StyledEventFeedHeader collapsible={collapsible} onClick={toggleCollapsed}>
          <span>
            <StyledCollapseIcon isCollapsed={isCollapsed}>▶</StyledCollapseIcon>
            Event Feed{renderEventCounts()}
          </span>
          <span>{processedEvents.length} events</span>
        </StyledEventFeedHeader>
      )}
      
      {!isCollapsed && (
        <>
          {processedEvents.length === 0 ? (
            <StyledEventItem severity="info">
              <StyledEventType severity="info">INFO</StyledEventType>
              {showTimestamps && (
                <StyledEventTimestamp>
                  {formatTimestamp(new Date().toISOString())}
                </StyledEventTimestamp>
              )}
              <StyledEventData>No events to display</StyledEventData>
            </StyledEventItem>
          ) : (
            processedEvents.map((event) => (
              <StyledEventItem key={event.id} severity={event.severity}>
                <div>
                  <StyledEventType severity={event.severity}>
                    {event.type.toUpperCase()}
                  </StyledEventType>
                  {showTimestamps && (
                    <StyledEventTimestamp>
                      {formatTimestamp(event.timestamp)}
                    </StyledEventTimestamp>
                  )}
                </div>
                <StyledEventData>
                  {formatEventData(event.data)}
                </StyledEventData>
                {event.metadata && (
                  <StyledEventData>
                    Metadata: {formatEventData(event.metadata)}
                  </StyledEventData>
                )}
              </StyledEventItem>
            ))
          )}
        </>
      )}
    </StyledEventFeedContainer>
  );
};
