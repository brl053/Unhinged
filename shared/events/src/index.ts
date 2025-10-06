// ============================================================================
// Unhinged Event Library - Main Export
// ============================================================================
//
// @file index.ts
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Main export file for the Unhinged event library
//
// Usage:
//   import { EventLogger, createEventLogger, EventSource } from '@unhinged/events';
//
// ============================================================================

// Core types and interfaces
export * from './types';

// Event logger implementation
export * from './EventLogger';

// Utility functions
export { createEventLogger } from './EventLogger';

// Re-export commonly used types for convenience
export type {
  BaseEvent,
  UnhingedEvent,
  EventMetadata,
  VoiceRecordingEvent,
  TranscriptionEvent,
  ChatEvent,
  LLMEvent,
  SystemEvent,
  ErrorEvent,
  UserActionEvent,
  EventHandler,
  EventFilter
} from './types';

export {
  EventSource,
  EventSeverity,
  EventCategory
} from './types';
