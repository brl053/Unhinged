/**
 * Unhinged Platform Text Editor Component
 * ======================================
 * 
 * Text editor component using Monaco Editor
 * Integrated with the Unhinged Platform design system
 */

import React, { forwardRef, useImperativeHandle, useState, useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { 
  TextEditorProps, 
  EditorInstance,
  DEFAULT_FEATURES,
  EditorLanguage,
  EditorTheme
} from './types';
import {
  EditorContainer,
  EditorMain,
  LoadingContainer,
  LoadingSpinner,
  ErrorContainer,
  ErrorTitle,
  ErrorMessage,
  PlaceholderContainer
} from './styles';

// ============================================================================
// Monaco Editor Theme Configuration
// ============================================================================

const configureMonacoThemes = (monaco: any) => {
  // Define Unhinged Dark Theme
  monaco.editor.defineTheme('unhinged-dark', {
    base: 'vs-dark',
    inherit: true,
    rules: [
      { token: 'comment', foreground: '6A737D', fontStyle: 'italic' },
      { token: 'keyword', foreground: 'F97583' },
      { token: 'string', foreground: '9ECBFF' },
      { token: 'number', foreground: '79B8FF' },
      { token: 'type', foreground: 'B392F0' },
      { token: 'class', foreground: 'FFAB70' },
      { token: 'function', foreground: 'B392F0' },
      { token: 'variable', foreground: 'E1E4E8' },
    ],
    colors: {
      'editor.background': '#0D1117',
      'editor.foreground': '#E1E4E8',
      'editor.lineHighlightBackground': '#161B22',
      'editor.selectionBackground': '#264F78',
      'editor.inactiveSelectionBackground': '#3A3D41',
      'editorLineNumber.foreground': '#6A737D',
      'editorLineNumber.activeForeground': '#E1E4E8',
      'editorCursor.foreground': '#E1E4E8',
    }
  });

  // Define Unhinged Light Theme
  monaco.editor.defineTheme('unhinged-light', {
    base: 'vs',
    inherit: true,
    rules: [
      { token: 'comment', foreground: '6A737D', fontStyle: 'italic' },
      { token: 'keyword', foreground: 'D73A49' },
      { token: 'string', foreground: '032F62' },
      { token: 'number', foreground: '005CC5' },
      { token: 'type', foreground: '6F42C1' },
      { token: 'class', foreground: 'E36209' },
      { token: 'function', foreground: '6F42C1' },
      { token: 'variable', foreground: '24292E' },
    ],
    colors: {
      'editor.background': '#FFFFFF',
      'editor.foreground': '#24292E',
      'editor.lineHighlightBackground': '#F6F8FA',
      'editor.selectionBackground': '#0366D6',
      'editorLineNumber.foreground': '#6A737D',
      'editorLineNumber.activeForeground': '#24292E',
      'editorCursor.foreground': '#24292E',
    }
  });
};

// ============================================================================
// Main TextEditor Component
// ============================================================================

export const TextEditor = forwardRef<EditorInstance, TextEditorProps>(({
  // Core props
  value,
  defaultValue,
  language = 'typescript',
  theme = 'unhinged-dark',
  size = 'medium',
  width,
  height,
  readOnly = false,
  placeholder,
  
  // Event handlers
  onChange,
  onMount,
  onSave,
  
  // Configuration
  features = {},
  
  // UI customization
  className,
  style,
  testId,
  
  ...props
}, ref) => {
  // State
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isReady, setIsReady] = useState(false);
  const editorRef = useRef<any>(null);
  
  // Merge with defaults
  const mergedFeatures = { ...DEFAULT_FEATURES, ...features };
  
  // Map our language types to Monaco language IDs
  const getMonacoLanguage = (lang: EditorLanguage): string => {
    const languageMap: Record<EditorLanguage, string> = {
      'typescript': 'typescript',
      'javascript': 'javascript',
      'tsx': 'typescript',
      'jsx': 'javascript',
      'json': 'json',
      'markdown': 'markdown',
      'html': 'html',
      'css': 'css',
      'scss': 'scss',
      'python': 'python',
      'java': 'java',
      'kotlin': 'kotlin',
      'go': 'go',
      'rust': 'rust',
      'sql': 'sql',
      'yaml': 'yaml',
      'xml': 'xml',
      'dockerfile': 'dockerfile',
      'plaintext': 'plaintext',
    };
    return languageMap[lang] || 'plaintext';
  };
  
  // Map our theme types to Monaco theme IDs
  const getMonacoTheme = (themeType: EditorTheme): string => {
    const themeMap: Record<EditorTheme, string> = {
      'unhinged-light': 'unhinged-light',
      'unhinged-dark': 'unhinged-dark',
      'vs-light': 'vs',
      'vs-dark': 'vs-dark',
    };
    return themeMap[themeType] || 'unhinged-dark';
  };
  
  // Handle Monaco mount
  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor;
    
    // Configure custom themes
    configureMonacoThemes(monaco);
    
    // Set up save shortcut
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      if (onSave) {
        onSave(editor.getValue());
      }
    });
    
    setIsReady(true);
    setIsLoading(false);
    setError(null);
    
    // Call onMount callback
    if (onMount) {
      onMount(editor);
    }
  };
  
  // Handle change events
  const handleEditorChange = (newValue: string | undefined) => {
    if (onChange && newValue !== undefined) {
      onChange({
        value: newValue,
        changes: [], // Monaco doesn't provide detailed changes in this callback
      });
    }
  };
  
  // Handle loading state
  const handleEditorLoading = () => {
    setIsLoading(true);
    setError(null);
  };
  
  // Handle validation errors
  const handleEditorValidation = (markers: any[]) => {
    const errors = markers.filter(marker => marker.severity === 8); // Error severity
    if (errors.length > 0) {
      setError(`Syntax error: ${errors[0].message}`);
    } else {
      setError(null);
    }
  };
  
  // Create editor instance API
  const editorInstance: EditorInstance = {
    getValue: () => editorRef.current?.getValue() || '',
    setValue: (newValue: string) => editorRef.current?.setValue(newValue),
    focus: () => editorRef.current?.focus(),
    blur: () => editorRef.current?.getContainerDomNode()?.blur(),
    dispose: () => editorRef.current?.dispose(),
  };
  
  // Expose editor instance through ref
  useImperativeHandle(ref, () => editorInstance, []);
  
  // Configure Monaco options
  const monacoOptions: any = {
    readOnly,
    lineNumbers: mergedFeatures.lineNumbers ? 'on' : 'off',
    minimap: { enabled: mergedFeatures.minimap },
    wordWrap: mergedFeatures.wordWrap ? 'on' : 'off',
    matchBrackets: mergedFeatures.bracketMatching ? 'always' : 'never',
    folding: mergedFeatures.codeFolding,
    find: { addExtraSpaceOnTop: false },
    automaticLayout: true,
    scrollBeyondLastLine: false,
    fontSize: 14,
    fontFamily: 'JetBrains Mono, Fira Code, Consolas, monospace',
    lineHeight: 21,
    renderWhitespace: 'selection',
    cursorBlinking: 'smooth',
    cursorSmoothCaretAnimation: 'on',
    smoothScrolling: true,
  };
  
  // Handle error state
  if (error && !isLoading) {
    return (
      <EditorContainer 
        $size={size} 
        $width={width} 
        $height={height} 
        $hasError={true}
        className={className}
        style={style}
        data-testid={testId}
      >
        <ErrorContainer>
          <ErrorTitle>Editor Error</ErrorTitle>
          <ErrorMessage>{error}</ErrorMessage>
        </ErrorContainer>
      </EditorContainer>
    );
  }
  
  return (
    <EditorContainer 
      $size={size} 
      $width={width} 
      $height={height} 
      $isLoading={isLoading}
      className={className}
      style={style}
      data-testid={testId}
    >
      <EditorMain>
        <Editor
          value={value}
          defaultValue={defaultValue}
          language={getMonacoLanguage(language)}
          theme={getMonacoTheme(theme)}
          options={monacoOptions}
          onChange={handleEditorChange}
          onMount={handleEditorDidMount}
          beforeMount={handleEditorLoading}
          onValidate={handleEditorValidation}
          loading={
            <LoadingContainer>
              <LoadingSpinner />
              <span>Loading editor...</span>
            </LoadingContainer>
          }
        />
      </EditorMain>
      
      {/* Placeholder when empty and not focused */}
      {placeholder && !value && !isReady && (
        <PlaceholderContainer>
          {placeholder}
        </PlaceholderContainer>
      )}
    </EditorContainer>
  );
});

TextEditor.displayName = 'TextEditor';

export default TextEditor;
