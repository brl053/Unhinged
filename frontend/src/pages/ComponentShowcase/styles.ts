/**
 * @fileoverview Component Showcase Page Styles
 * @purpose Styled components for the TextEditor component showcase page
 * @editable true - LLM should update styles when adding new showcase features
 * @deprecated false
 *
 * @remarks
 * All styles use the enhanced theme system with proper color/spacing/typography tokens.
 * When adding new styled components, ensure they follow the theme system patterns.
 *
 * @example
 * ```typescript
 * // Good - uses theme tokens
 * color: ${({ theme }) => theme.color.text.primary};
 * font-size: ${({ theme }) => theme.typography.fontSize.md};
 *
 * // Bad - hardcoded values
 * color: '#e1e4e8';
 * font-size: '1rem';
 * ```
 */

import { styled } from 'styled-components';

export const ShowcaseContainer = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: ${({ theme }) => theme.spacing.xl};

  @media (max-width: 768px) {
    padding: ${({ theme }) => theme.spacing.md};
  }
`;

export const ShowcaseSection = styled.section`
  margin-bottom: ${({ theme }) => theme.spacing['3xl']};
  padding: ${({ theme }) => theme.spacing.xl};
  background: ${({ theme }) => theme.color.background.secondary};
  border: 1px solid ${({ theme }) => theme.color.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.lg};

  h2 {
    color: ${({ theme }) => theme.color.text.primary};
    font-size: ${({ theme }) => theme.typography.fontSize.xl};
    margin-bottom: ${({ theme }) => theme.spacing.md};
    font-weight: ${({ theme }) => theme.typography.fontWeight.semibold};
  }

  h3 {
    color: ${({ theme }) => theme.color.text.primary};
    font-size: ${({ theme }) => theme.typography.fontSize.lg};
    margin: ${({ theme }) => theme.spacing.xl} 0 ${({ theme }) => theme.spacing.md} 0;
    font-weight: ${({ theme }) => theme.typography.fontWeight.medium};
  }

  p {
    color: ${({ theme }) => theme.color.text.secondary};
    line-height: ${({ theme }) => theme.typography.lineHeight.normal};
    margin-bottom: ${({ theme }) => theme.spacing.lg};
  }
`;

export const SectionTitle = styled.h1`
  color: ${({ theme }) => theme.color.text.primary};
  font-size: ${({ theme }) => theme.typography.fontSize['3xl']};
  font-weight: ${({ theme }) => theme.typography.fontWeight.bold};
  text-align: center;
  margin-bottom: ${({ theme }) => theme.spacing.md};

  background: linear-gradient(135deg, ${({ theme }) => theme.color.primary.main}, ${({ theme }) => theme.color.secondary.main});
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

export const SectionDescription = styled.p`
  color: ${({ theme }) => theme.color.text.secondary};
  font-size: ${({ theme }) => theme.typography.fontSize.lg};
  text-align: center;
  max-width: 800px;
  margin: 0 auto ${({ theme }) => theme.spacing['3xl']} auto;
  line-height: ${({ theme }) => theme.typography.lineHeight.normal};
`;

export const ControlsContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${({ theme }) => theme.spacing.md};
  margin: ${({ theme }) => theme.spacing.lg} 0;
  padding: ${({ theme }) => theme.spacing.lg};
  background: ${({ theme }) => theme.color.background.primary};
  border: 1px solid ${({ theme }) => theme.color.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.md};

  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

export const ControlGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${({ theme }) => theme.spacing.sm};
  min-width: 150px;

  @media (max-width: 768px) {
    min-width: auto;
  }
`;

export const ControlLabel = styled.label`
  color: ${({ theme }) => theme.color.text.primary};
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
  font-weight: ${({ theme }) => theme.typography.fontWeight.medium};
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

export const Select = styled.select`
  padding: ${({ theme }) => theme.spacing.sm};
  background: ${({ theme }) => theme.color.background.secondary};
  color: ${({ theme }) => theme.color.text.primary};
  border: 1px solid ${({ theme }) => theme.color.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
  cursor: pointer;

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.color.border.focus};
    box-shadow: 0 0 0 2px ${({ theme }) => theme.color.primary.main}20;
  }

  option {
    background: ${({ theme }) => theme.color.background.secondary};
    color: ${({ theme }) => theme.color.text.primary};
  }
`;

export const Button = styled.button`
  padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.lg};
  background: ${({ theme }) => theme.color.primary.main};
  color: ${({ theme }) => theme.color.primary.contrastText};
  border: none;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
  font-weight: ${({ theme }) => theme.typography.fontWeight.medium};
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${({ theme }) => theme.color.primary.dark};
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px ${({ theme }) => theme.color.primary.main}40;
  }
`;

export const CodeOutput = styled.div`
  background: ${({ theme }) => theme.color.background.primary};
  border: 1px solid ${({ theme }) => theme.color.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  padding: ${({ theme }) => theme.spacing.md};
  margin: ${({ theme }) => theme.spacing.md} 0;
  overflow-x: auto;

  pre {
    margin: 0;
    font-family: ${({ theme }) => theme.typography.fontFamily.mono};
    font-size: ${({ theme }) => theme.typography.fontSize.sm};
    color: ${({ theme }) => theme.color.text.primary};
    line-height: ${({ theme }) => theme.typography.lineHeight.normal};
    white-space: pre-wrap;
    word-break: break-word;
  }
`;

export const EditorContainer = styled.div`
  margin: ${({ theme }) => theme.spacing.xl} 0;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  overflow: hidden;
  box-shadow: ${({ theme }) => theme.shadows.md};
`;

export const FeatureToggle = styled.div`
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.sm};

  input[type="checkbox"] {
    width: 16px;
    height: 16px;
    accent-color: ${({ theme }) => theme.color.primary.main};
    cursor: pointer;
  }
`;

export const FeatureLabel = styled.label`
  color: ${({ theme }) => theme.color.text.primary};
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
  cursor: pointer;
  user-select: none;

  &:hover {
    color: ${({ theme }) => theme.color.primary.main};
  }
`;
