import { UnhingedTheme } from '../../../design_system';

export interface EventItem {
  id: string;
  type: string;
  source: string;
  data: any;
  metadata?: any;
  timestamp: string;
  severity?: EventSeverity;
}

export type EventSeverity = 'info' | 'warn' | 'error' | 'success';

export interface EventFeedProps {
  events: EventItem[];
  maxEvents?: number;
  showTimestamps?: boolean;
  collapsible?: boolean;
  className?: string;
}

export interface StyledEventFeedProps {
  theme: UnhingedTheme;
  collapsible?: boolean;
  isCollapsed?: boolean;
}

export interface StyledEventItemProps {
  theme: UnhingedTheme;
  severity?: EventSeverity;
}

export interface StyledEventTypeProps {
  theme: UnhingedTheme;
  severity?: EventSeverity;
}
