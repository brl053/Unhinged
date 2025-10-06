// ============================================================================
// EventLog Module - Public API Exports
// ============================================================================
//
// @file index.ts
// @version 2.0.0
// @author Unhinged Design System Team
// @date 2025-10-06
// @description Public API for EventLog module with clean exports
//
// Etymology: Latin "index" = pointer, indicator
// Methodology: Barrel exports with organized public interface
// ============================================================================

// Main EventLog component
export { EventLog as default } from '../../EventLog';

// Type definitions
export type {
  Event,
  EventLogProps,
  EventLogState,
  ConnectionStatus,
  EventFilter,
  EventFormatOptions,
  WebSocketMessage,
  EventLogMetrics,
  UseEventLogReturn,
  EventLogContextType,
  EventTypeMetadata,
  EventLogConfig
} from './types';

// Utility functions
export {
  formatTimestamp,
  formatRelativeTime,
  formatJSON,
  filterEvents,
  filterEventsByText,
  getEventTypeMetadata,
  getEventKey,
  sortEventsByTimestamp,
  groupEventsByTimePeriod,
  calculateEventStats,
  truncateText,
  debounce,
  checkPerformanceThresholds,
  sanitizeEvent
} from './utils';

// React hooks
export {
  useEventLog,
  useAutoScroll,
  useEventLogPreferences
} from './hooks';

// Constants and configuration
export {
  DEFAULT_CONFIG,
  WEBSOCKET_CONFIG,
  EVENT_TYPE_METADATA,
  CONNECTION_STATUS_METADATA,
  FILTER_PRESETS,
  EVENT_LOG_CLASSES,
  EVENT_LOG_DATA_ATTRIBUTES,
  PERFORMANCE_THRESHOLDS,
  KEYBOARD_SHORTCUTS,
  STORAGE_KEYS
} from './constants';

// Styled components and styles
export {
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
  errorMessageStyles,
  eventLogDarkThemeStyles
} from './styles';
