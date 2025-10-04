/**
 * @fileoverview TextEditor Component Styles
 * @purpose Styled components for the Monaco Editor wrapper component
 * @editable true - LLM should update styles when adding new editor features
 * @deprecated false
 *
 * @remarks
 * All styles use the enhanced theme system with proper color/spacing/typography tokens.
 * Monaco Editor specific styling is handled through CSS classes that integrate with the theme.
 *
 * @example
 * ```typescript
 * // Good - uses theme tokens
 * background: ${({ theme }) => theme.color.background.primary};
 * border-radius: ${({ theme }) => theme.borderRadius.md};
 *
 * // Bad - hardcoded values
 * background: '#0d1117';
 * border-radius: '8px';
 * ```
 */

import { styled } from 'styled-components';
import { EditorSize } from './types';

interface EditorContainerProps {
  $size: EditorSize;
  $width?: string | number;
  $height?: string | number;
  $hasError?: boolean;
  $isLoading?: boolean;
}

const getSizeDimensions = (size: EditorSize) => {
  switch (size) {
    case 'small':
      return { width: '400px', height: '200px' };
    case 'medium':
      return { width: '600px', height: '400px' };
    case 'large':
      return { width: '800px', height: '600px' };
    case 'full':
      return { width: '100%', height: '100%' };
    default:
      return { width: '600px', height: '400px' };
  }
};

export const EditorContainer = styled.div<EditorContainerProps>`
  position: relative;
  border: 1px solid ${({ theme, $hasError }) =>
    $hasError ? theme.color.error.main : theme.color.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  background: ${({ theme }) => theme.color.background.primary};
  overflow: hidden;

  ${({ $size, $width, $height }) => {
    const dimensions = getSizeDimensions($size);
    return `
      width: ${$width ? (typeof $width === 'number' ? `${$width}px` : $width) : dimensions.width};
      height: ${$height ? (typeof $height === 'number' ? `${$height}px` : $height) : dimensions.height};
    `;
  }}

  ${({ $isLoading }) => $isLoading && `
    display: flex;
    align-items: center;
    justify-content: center;
  `}
`;

export const EditorMain = styled.div`
  width: 100%;
  height: 100%;

  .monaco-editor {
    font-family: ${({ theme }) => theme.typography.fontFamily.mono};
  }

  .monaco-editor .margin {
    background: ${({ theme }) => theme.color.background.secondary};
  }

  .monaco-editor .monaco-editor-background {
    background: ${({ theme }) => theme.color.background.primary};
  }

  .monaco-editor .mtk1 {
    color: ${({ theme }) => theme.color.text.primary};
  }
`;

export const LoadingContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${({ theme }) => theme.spacing.sm};
  color: ${({ theme }) => theme.color.text.secondary};
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
`;

export const LoadingSpinner = styled.div`
  width: 16px;
  height: 16px;
  border: 2px solid ${({ theme }) => theme.color.border.primary};
  border-top: 2px solid ${({ theme }) => theme.color.primary.main};
  border-radius: ${({ theme }) => theme.borderRadius.full};
  animation: spin 1s linear infinite;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

export const ErrorContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: ${({ theme }) => theme.spacing.xl};
  text-align: center;
  color: ${({ theme }) => theme.color.error.main};
`;

export const ErrorTitle = styled.div`
  font-weight: ${({ theme }) => theme.typography.fontWeight.semibold};
  margin-bottom: ${({ theme }) => theme.spacing.sm};
  font-size: ${({ theme }) => theme.typography.fontSize.md};
`;

export const ErrorMessage = styled.div`
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
  color: ${({ theme }) => theme.color.text.secondary};
`;

export const PlaceholderContainer = styled.div`
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  color: ${({ theme }) => theme.color.text.tertiary};
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
  font-style: italic;
`;
