/**
 * @fileoverview Electron Renderer Process - DSL UI Generation
 * 
 * @description
 * Renderer process for the Universal System that interprets DSL schemas
 * and generates React components. Handles real-time UI generation from
 * voice commands and LLM-generated schemas.
 * 
 * @design_principles
 * - DSL-driven rendering: All UI generated from schema definitions
 * - Real-time updates: Hot-swap components based on voice commands
 * - Backend integration: Seamless communication with Unhinged services
 * - Development-friendly: Hot reload and debugging support
 * 
 * @llm_contract
 * This renderer serves as the UI generation engine that:
 * 1. Loads Universal System DSL schema from main process
 * 2. Interprets component definitions into React components
 * 3. Handles voice commands and real-time UI updates
 * 4. Communicates with backend services for AI functionality
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import React, { useState, useEffect, useCallback } from 'react';
import { createRoot } from 'react-dom/client';
import styled, { ThemeProvider, createGlobalStyle } from 'styled-components';

/**
 * Universal System API interface for IPC communication
 * 
 * @description
 * TypeScript interface for the exposed API from the preload script.
 * Provides type-safe communication with the main process.
 */
interface UniversalSystemAPI {
  getSchema(): Promise<any>;
  getConfig(): Promise<any>;
  executeCommand(command: string): Promise<{ success: boolean; result: string }>;
  backendRequest(endpoint: string, data?: any): Promise<any>;
  onSchemaUpdate(callback: (schema: any) => void): void;
}

/**
 * Extend window interface to include Universal System API
 */
declare global {
  interface Window {
    universalSystem: UniversalSystemAPI;
  }
}

/**
 * Component instance interface matching DSL schema
 */
interface ComponentInstance {
  component: string;
  props?: Record<string, any>;
  state?: Record<string, any>;
  actions?: Record<string, string>;
  children?: ComponentInstance[];
}

/**
 * Application state interface
 */
interface AppState {
  schema: any | null;
  config: any | null;
  currentUI: ComponentInstance | null;
  voiceActive: boolean;
  loading: boolean;
  error: string | null;
}

/**
 * Global styles for the Universal System application
 */
const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    background: #1a1a1a;
    color: #ffffff;
    overflow: hidden;
  }
  
  #root {
    width: 100vw;
    height: 100vh;
    display: flex;
    flex-direction: column;
  }
`;

/**
 * Theme configuration for styled-components
 */
const theme = {
  colors: {
    primary: '#007acc',
    secondary: '#6c757d',
    success: '#28a745',
    warning: '#ffc107',
    error: '#dc3545',
    background: {
      primary: '#1a1a1a',
      secondary: '#2d2d2d',
      tertiary: '#404040',
    },
    text: {
      primary: '#ffffff',
      secondary: '#cccccc',
      muted: '#999999',
    },
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
  },
  borderRadius: '8px',
  transition: '0.2s ease-in-out',
};

/**
 * Main application container
 */
const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: ${props => props.theme.colors.background.primary};
`;

/**
 * Header with Universal System branding and status
 */
const Header = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.background.secondary};
  border-bottom: 1px solid ${props => props.theme.colors.background.tertiary};
`;

/**
 * Main content area where DSL components are rendered
 */
const MainContent = styled.main`
  flex: 1;
  padding: ${props => props.theme.spacing.lg};
  overflow-y: auto;
`;

/**
 * Status indicator component
 */
const StatusIndicator = styled.div<{ status: 'loading' | 'ready' | 'error' }>`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  color: ${props => {
    switch (props.status) {
      case 'loading': return props.theme.colors.warning;
      case 'ready': return props.theme.colors.success;
      case 'error': return props.theme.colors.error;
      default: return props.theme.colors.text.secondary;
    }
  }};
`;

/**
 * Voice activation button
 */
const VoiceButton = styled.button<{ active: boolean }>`
  padding: ${props => props.theme.spacing.md};
  border: none;
  border-radius: ${props => props.theme.borderRadius};
  background: ${props => props.active ? props.theme.colors.primary : props.theme.colors.background.tertiary};
  color: ${props => props.theme.colors.text.primary};
  cursor: pointer;
  transition: ${props => props.theme.transition};
  
  &:hover {
    opacity: 0.8;
  }
  
  &:active {
    transform: scale(0.95);
  }
`;

/**
 * DSL Component Renderer
 * 
 * @description
 * Recursively renders DSL component definitions into React components.
 * This is the core of the Universal System's UI generation capability.
 */
const DSLComponentRenderer: React.FC<{ definition: ComponentInstance }> = ({ definition }) => {
  const [localState, setLocalState] = useState(definition.state || {});
  
  /**
   * Handle component actions
   */
  const handleAction = useCallback(async (actionName: string, actionValue: string) => {
    console.log(`🎯 Action triggered: ${actionName} = ${actionValue}`);
    
    // Parse action syntax: "actionType:parameters"
    const [actionType, parameters] = actionValue.split(':');
    
    switch (actionType) {
      case 'setState':
        const [key, value] = parameters.split('=');
        setLocalState(prev => ({ ...prev, [key]: value === 'true' ? true : value === 'false' ? false : value }));
        break;
        
      case 'emit':
        console.log(`📡 Emitting event: ${parameters}`);
        // TODO: Implement event emission to parent components
        break;
        
      case 'navigate':
        const route = parameters.replace('route=', '');
        console.log(`🧭 Navigating to: ${route}`);
        // TODO: Implement navigation
        break;
        
      case 'command':
        const command = parameters.replace('execute=', '');
        const result = await window.universalSystem.executeCommand(command);
        console.log(`⚡ Command result:`, result);
        break;
        
      default:
        console.warn(`❓ Unknown action type: ${actionType}`);
    }
  }, []);
  
  /**
   * Render component based on type
   */
  const renderComponent = () => {
    const { component, props = {}, children = [] } = definition;
    const mergedProps = { ...props, ...localState };
    
    switch (component) {
      case 'Container':
        return (
          <div style={{ 
            padding: mergedProps.padding === 'medium' ? '16px' : mergedProps.padding,
            background: mergedProps.background,
            maxWidth: mergedProps.maxWidth,
          }}>
            {children.map((child, index) => (
              <DSLComponentRenderer key={index} definition={child} />
            ))}
          </div>
        );
        
      case 'Stack':
        return (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: mergedProps.spacing === 'small' ? '8px' : '16px',
            alignItems: mergedProps.alignment || 'stretch',
          }}>
            {children.map((child, index) => (
              <DSLComponentRenderer key={index} definition={child} />
            ))}
          </div>
        );
        
      case 'Text':
        return (
          <span style={{
            color: mergedProps.color,
            fontSize: mergedProps.size === 'caption' ? '12px' : '16px',
            fontWeight: mergedProps.variant === 'body' ? 'normal' : 'bold',
          }}>
            {mergedProps.content}
          </span>
        );
        
      case 'Button':
        return (
          <button
            onClick={() => definition.actions?.onClick && handleAction('onClick', definition.actions.onClick)}
            style={{
              padding: '8px 16px',
              border: 'none',
              borderRadius: '4px',
              background: mergedProps.variant === 'ghost' ? 'transparent' : '#007acc',
              color: '#ffffff',
              cursor: 'pointer',
            }}
          >
            {mergedProps.label}
          </button>
        );
        
      case 'VoiceInput':
        return (
          <div style={{ 
            padding: '16px',
            border: '2px solid #007acc',
            borderRadius: '8px',
            background: '#2d2d2d',
          }}>
            <div>🎤 Voice Input: {mergedProps.placeholder}</div>
            <div>Recording: {localState.isRecording ? 'Yes' : 'No'}</div>
            <div>Transcription: {localState.transcription || 'None'}</div>
            <button
              onClick={() => handleAction('onRecordStart', 'setState:isRecording=true')}
              disabled={localState.isRecording}
            >
              Start Recording
            </button>
            <button
              onClick={() => handleAction('onRecordStop', 'setState:isRecording=false')}
              disabled={!localState.isRecording}
            >
              Stop Recording
            </button>
          </div>
        );
        
      default:
        return (
          <div style={{ 
            padding: '8px',
            background: '#ff6b6b',
            color: 'white',
            borderRadius: '4px',
          }}>
            Unknown component: {component}
          </div>
        );
    }
  };
  
  return renderComponent();
};

/**
 * Main Universal System Application Component
 */
const UniversalSystemApp: React.FC = () => {
  const [appState, setAppState] = useState<AppState>({
    schema: null,
    config: null,
    currentUI: null,
    voiceActive: false,
    loading: true,
    error: null,
  });
  
  /**
   * Initialize application
   */
  useEffect(() => {
    const initializeApp = async () => {
      try {
        console.log('🚀 Initializing Universal System...');
        
        // Load schema and configuration
        const [schema, config] = await Promise.all([
          window.universalSystem.getSchema(),
          window.universalSystem.getConfig(),
        ]);
        
        console.log('✅ Schema loaded:', schema?.version);
        console.log('⚙️ Config loaded:', config);
        
        // Load default UI from schema examples
        const defaultUI = schema?.examples?.voice_input_component || null;
        
        setAppState({
          schema,
          config,
          currentUI: defaultUI,
          voiceActive: false,
          loading: false,
          error: null,
        });
        
      } catch (error) {
        console.error('❌ Failed to initialize app:', error);
        setAppState(prev => ({
          ...prev,
          loading: false,
          error: error instanceof Error ? error.message : 'Unknown error',
        }));
      }
    };
    
    initializeApp();
  }, []);
  
  /**
   * Toggle voice activation
   */
  const toggleVoice = useCallback(() => {
    setAppState(prev => ({
      ...prev,
      voiceActive: !prev.voiceActive,
    }));
  }, []);
  
  /**
   * Render loading state
   */
  if (appState.loading) {
    return (
      <AppContainer>
        <MainContent>
          <div style={{ textAlign: 'center', padding: '64px' }}>
            <h2>🚀 Loading Universal System...</h2>
            <p>Initializing DSL schema and backend services...</p>
          </div>
        </MainContent>
      </AppContainer>
    );
  }
  
  /**
   * Render error state
   */
  if (appState.error) {
    return (
      <AppContainer>
        <MainContent>
          <div style={{ textAlign: 'center', padding: '64px', color: '#dc3545' }}>
            <h2>❌ Error</h2>
            <p>{appState.error}</p>
          </div>
        </MainContent>
      </AppContainer>
    );
  }
  
  return (
    <AppContainer>
      <Header>
        <div>
          <h1>🌟 Universal System</h1>
          <small>DSL Schema v{appState.schema?.version}</small>
        </div>
        
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <StatusIndicator status="ready">
            <span>●</span>
            <span>Ready</span>
          </StatusIndicator>
          
          <VoiceButton active={appState.voiceActive} onClick={toggleVoice}>
            🎤 {appState.voiceActive ? 'Listening...' : 'Voice'}
          </VoiceButton>
        </div>
      </Header>
      
      <MainContent>
        {appState.currentUI ? (
          <DSLComponentRenderer definition={appState.currentUI} />
        ) : (
          <div style={{ textAlign: 'center', padding: '64px' }}>
            <h2>🎨 Universal System Ready</h2>
            <p>Use voice commands to generate UI components</p>
            <p>Try: "Create a voice input" or "Add a text field"</p>
          </div>
        )}
      </MainContent>
    </AppContainer>
  );
};

/**
 * Initialize the React application
 */
const container = document.getElementById('root');
if (container) {
  const root = createRoot(container);
  root.render(
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <UniversalSystemApp />
    </ThemeProvider>
  );
} else {
  console.error('❌ Root container not found');
}
