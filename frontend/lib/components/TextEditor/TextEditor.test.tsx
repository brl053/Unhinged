/**
 * TextEditor Component Tests
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from 'styled-components';
import { TextEditor } from './TextEditor';
import { theme } from '../../theme/theme';

// Mock Monaco Editor since it requires DOM APIs
jest.mock('@monaco-editor/react', () => {
  return {
    __esModule: true,
    default: ({ value, onChange, loading }: any) => (
      <div data-testid="monaco-editor">
        {loading}
        <textarea
          data-testid="editor-textarea"
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
        />
      </div>
    ),
  };
});

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('TextEditor', () => {
  it('renders without crashing', () => {
    renderWithTheme(
      <TextEditor
        value="console.log('Hello World');"
        language="typescript"
        testId="test-editor"
      />
    );
    
    expect(screen.getByTestId('test-editor')).toBeInTheDocument();
  });

  it('displays loading state initially', () => {
    renderWithTheme(
      <TextEditor
        value=""
        language="typescript"
        testId="test-editor"
      />
    );
    
    expect(screen.getByText('Loading editor...')).toBeInTheDocument();
  });

  it('handles different languages', () => {
    const { rerender } = renderWithTheme(
      <TextEditor
        value="const x = 1;"
        language="javascript"
        testId="test-editor"
      />
    );
    
    expect(screen.getByTestId('test-editor')).toBeInTheDocument();
    
    rerender(
      <ThemeProvider theme={theme}>
        <TextEditor
          value="print('Hello')"
          language="python"
          testId="test-editor"
        />
      </ThemeProvider>
    );
    
    expect(screen.getByTestId('test-editor')).toBeInTheDocument();
  });

  it('handles different themes', () => {
    const { rerender } = renderWithTheme(
      <TextEditor
        value="const x = 1;"
        language="typescript"
        theme="unhinged-dark"
        testId="test-editor"
      />
    );
    
    expect(screen.getByTestId('test-editor')).toBeInTheDocument();
    
    rerender(
      <ThemeProvider theme={theme}>
        <TextEditor
          value="const x = 1;"
          language="typescript"
          theme="unhinged-light"
          testId="test-editor"
        />
      </ThemeProvider>
    );
    
    expect(screen.getByTestId('test-editor')).toBeInTheDocument();
  });

  it('handles read-only mode', () => {
    renderWithTheme(
      <TextEditor
        value="const x = 1;"
        language="typescript"
        readOnly={true}
        testId="test-editor"
      />
    );
    
    expect(screen.getByTestId('test-editor')).toBeInTheDocument();
  });

  it('displays error state', () => {
    renderWithTheme(
      <TextEditor
        value=""
        language="typescript"
        error="Test error message"
        testId="test-editor"
      />
    );
    
    expect(screen.getByText('Editor Error')).toBeInTheDocument();
    expect(screen.getByText('Test error message')).toBeInTheDocument();
  });
});
