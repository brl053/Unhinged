export const EVENT_FEED_CONSTANTS = {
  DEFAULT_MAX_EVENTS: 50,
  MAX_HEIGHT_PX: 300,
  COLLAPSE_ANIMATION_DURATION: 200,
  EVENT_RETENTION_TIME: 5 * 60 * 1000, // 5 minutes
} as const;

export const EVENT_SEVERITY_ORDER = {
  error: 0,
  warn: 1,
  info: 2,
  success: 3,
} as const;
