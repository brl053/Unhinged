/**
 * Unhinged Platform Text Editor Types
 * ===================================
 * 
 * Type definitions for the text editor component
 * Designed to work with MonacoEditor but implementation-agnostic
 */

import { ReactNode } from 'react';

// ============================================================================
// Core Editor Types
// ============================================================================

export type EditorLanguage = 
  | 'typescript' | 'javascript' | 'tsx' | 'jsx'
  | 'json' | 'markdown' | 'html' | 'css' | 'scss'
  | 'python' | 'java' | 'kotlin' | 'go' | 'rust'
  | 'sql' | 'yaml' | 'xml' | 'dockerfile'
  | 'plaintext';

export type EditorTheme = 
  | 'unhinged-light' 
  | 'unhinged-dark' 
  | 'vs-light'
  | 'vs-dark';

export type EditorSize = 'small' | 'medium' | 'large' | 'full';

export interface EditorPosition {
  line: number;
  column: number;
}

export interface EditorRange {
  startLine: number;
  startColumn: number;
  endLine: number;
  endColumn: number;
}

// ============================================================================
// Editor Configuration
// ============================================================================

export interface EditorFeatures {
  syntaxHighlighting: boolean;
  autoComplete: boolean;
  lineNumbers: boolean;
  minimap: boolean;
  wordWrap: boolean;
  bracketMatching: boolean;
  codeFolding: boolean;
  findReplace: boolean;
  multiCursor: boolean;
}

// ============================================================================
// Editor Events
// ============================================================================

export interface EditorChangeEvent {
  value: string;
  changes: Array<{
    range: EditorRange;
    text: string;
    rangeLength: number;
  }>;
}

// ============================================================================
// Main Editor Props
// ============================================================================

export interface TextEditorProps {
  // Core content
  value?: string;
  defaultValue?: string;
  language?: EditorLanguage;
  theme?: EditorTheme;
  size?: EditorSize;
  width?: string | number;
  height?: string | number;
  readOnly?: boolean;
  placeholder?: string;
  
  // Event handlers
  onChange?: (event: EditorChangeEvent) => void;
  onMount?: (editor: any) => void;
  onSave?: (value: string) => void;
  
  // Configuration
  features?: Partial<EditorFeatures>;
  
  // UI customization
  className?: string;
  style?: React.CSSProperties;
  
  // Test ID
  testId?: string;
}

// ============================================================================
// Editor Instance API
// ============================================================================

export interface EditorInstance {
  getValue(): string;
  setValue(value: string): void;
  focus(): void;
  blur(): void;
  dispose(): void;
}

// ============================================================================
// Default configurations
// ============================================================================

export const DEFAULT_FEATURES: EditorFeatures = {
  syntaxHighlighting: true,
  autoComplete: true,
  lineNumbers: true,
  minimap: false,
  wordWrap: false,
  bracketMatching: true,
  codeFolding: true,
  findReplace: true,
  multiCursor: true,
};
