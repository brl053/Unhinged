import styled from 'styled-components';
import { StyledEventFeedProps, StyledEventItemProps, StyledEventTypeProps, EventSeverity } from './types';

const getSeverityColors = (theme: any, severity?: EventSeverity) => {
  switch (severity) {
    case 'error':
      return {
        background: theme.colors.semantic.intent.danger + '1A', // 10% opacity
        border: theme.colors.semantic.intent.danger,
        text: theme.colors.semantic.intent.danger,
      };
    case 'warn':
      return {
        background: theme.colors.semantic.intent.warning + '1A',
        border: theme.colors.semantic.intent.warning,
        text: theme.colors.primitive.chromatic.orange,
      };
    case 'success':
      return {
        background: theme.colors.semantic.intent.success + '1A',
        border: theme.colors.semantic.intent.success,
        text: theme.colors.semantic.intent.success,
      };
    default:
      return {
        background: theme.colors.semantic.context.background.tertiary,
        border: theme.colors.semantic.context.border.secondary,
        text: theme.colors.semantic.context.text.secondary,
      };
  }
};

export const StyledEventFeedContainer = styled.div<StyledEventFeedProps>`
  background: ${({ theme }) => theme.colors.semantic.context.background.secondary};
  border-radius: ${({ theme }) => theme.spatial.base.radius.md}px;
  padding: ${({ theme }) => theme.spatial.base.spacing.md}px;
  margin: ${({ theme }) => theme.spatial.base.spacing.sm}px 0;
  border-left: ${({ theme }) => theme.spatial.base.border.thick}px solid ${({ theme }) => theme.colors.semantic.intent.primary};
  font-family: ${({ theme }) => theme.typography.families.monospace};
  font-size: ${({ theme }) => theme.typography.scale.small * 16}px;
  max-height: ${({ theme }) => theme.spatial.base.spacing.xxxl * 6}px;
  overflow-y: auto;
  transition: all ${({ theme }) => theme.motion.duration.fast}ms ${({ theme }) => theme.motion.easing.easeOut};
`;

export const StyledEventFeedHeader = styled.div<StyledEventFeedProps>`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${({ theme }) => theme.spatial.base.spacing.sm}px;
  font-weight: ${({ theme }) => theme.typography.weights.semibold};
  color: ${({ theme }) => theme.colors.semantic.context.text.primary};
  cursor: ${({ collapsible }) => collapsible ? 'pointer' : 'default'};
  user-select: none;
  
  &:hover {
    color: ${({ theme, collapsible }) => 
      collapsible ? theme.colors.semantic.intent.primary : theme.colors.semantic.context.text.primary};
  }
`;

export const StyledEventItem = styled.div<StyledEventItemProps>`
  padding: ${({ theme }) => theme.spatial.base.spacing.xs}px ${({ theme }) => theme.spatial.base.spacing.sm}px;
  margin: ${({ theme }) => theme.spatial.base.spacing.xs}px 0;
  border-radius: ${({ theme }) => theme.spatial.base.radius.sm}px;
  background: ${({ theme, severity }) => getSeverityColors(theme, severity).background};
  border-left: ${({ theme }) => theme.spatial.base.border.thin}px solid ${({ theme, severity }) => getSeverityColors(theme, severity).border};
  transition: all ${({ theme }) => theme.motion.duration.fast}ms ${({ theme }) => theme.motion.easing.easeOut};
  
  &:hover {
    transform: translateX(${({ theme }) => theme.spatial.base.spacing.xs / 2}px);
  }
`;

export const StyledEventType = styled.span<StyledEventTypeProps>`
  font-weight: ${({ theme }) => theme.typography.weights.semibold};
  color: ${({ theme, severity }) => getSeverityColors(theme, severity).text};
`;

export const StyledEventTimestamp = styled.span<{ theme: any }>`
  color: ${({ theme }) => theme.colors.semantic.context.text.tertiary};
  font-size: ${({ theme }) => theme.typography.scale.micro * 16}px;
  margin-left: ${({ theme }) => theme.spatial.base.spacing.sm}px;
`;

export const StyledEventData = styled.div<{ theme: any }>`
  margin-top: ${({ theme }) => theme.spatial.base.spacing.xs}px;
  color: ${({ theme }) => theme.colors.semantic.context.text.secondary};
  font-family: ${({ theme }) => theme.typography.families.monospace};
  white-space: pre-wrap;
  word-break: break-word;
`;

export const StyledCollapseIcon = styled.span<{ isCollapsed: boolean; theme: any }>`
  transform: rotate(${({ isCollapsed }) => isCollapsed ? '0deg' : '90deg'});
  transition: transform ${({ theme }) => theme.motion.duration.fast}ms ${({ theme }) => theme.motion.easing.easeOut};
  display: inline-block;
  margin-right: ${({ theme }) => theme.spatial.base.spacing.xs}px;
`;
