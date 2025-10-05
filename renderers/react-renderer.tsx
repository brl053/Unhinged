/**
 * @fileoverview React Component Renderer - DSL to React Bridge
 * 
 * @description
 * React renderer implementation that transforms Universal System DSL
 * component instances into live React components. Handles real-time
 * state updates, action execution, and component lifecycle management.
 * 
 * @design_principles
 * - DSL-driven rendering: All components generated from schema definitions
 * - Real-time updates: Reactive state changes and prop updates
 * - Action integration: Seamless action execution with DSL interpreter
 * - Component reuse: Efficient React component caching and updates
 * - Type safety: Full TypeScript integration with DSL interfaces
 * 
 * @llm_contract
 * This renderer serves as the visual manifestation of DSL components:
 * 1. Receives ComponentInstance objects from DSL Interpreter
 * 2. Transforms them into React components with proper styling
 * 3. Handles user interactions and forwards actions to interpreter
 * 4. Updates components reactively based on state changes
 * 5. Integrates with existing Unhinged component library
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import styled, { css } from 'styled-components';
import {
  DSLRenderer,
  ComponentInstance,
  ComponentContext,
  StateChangeEvent,
  ParsedAction,
  DSLInterpreter,
} from '../core/dsl-interpreter';

/**
 * React component props interface
 * 
 * @description
 * Props passed to rendered React components, including DSL data
 * and interaction handlers.
 */
interface ReactComponentProps {
  instance: ComponentInstance;
  context: ComponentContext;
  onAction: (actionString: string) => Promise<void>;
  onStateChange: (key: string, value: any) => void;
  children?: React.ReactNode;
}

/**
 * Component registry for React component mapping
 * 
 * @description
 * Maps DSL component names to React component implementations.
 * Allows for custom component registration and override.
 */
type ComponentRegistry = Map<string, React.ComponentType<ReactComponentProps>>;

/**
 * Rendered component tracking
 * 
 * @description
 * Tracks rendered React components for efficient updates and cleanup.
 */
interface RenderedComponent {
  id: string;
  instance: ComponentInstance;
  reactElement: React.ReactElement;
  mountTime: number;
}

/**
 * Styled components for DSL primitives
 * 
 * @description
 * Base styled components that implement the visual representation
 * of DSL primitive types with proper theming and responsive design.
 */

const StyledContainer = styled.div<{ $padding?: string; $background?: string; $maxWidth?: string }>`
  padding: ${props => {
    switch (props.$padding) {
      case 'small': return '8px';
      case 'medium': return '16px';
      case 'large': return '24px';
      case 'none': return '0';
      default: return props.$padding || '16px';
    }
  }};
  
  background: ${props => {
    switch (props.$background) {
      case 'sidebar': return '#2d2d2d';
      case 'message_bubble': return '#404040';
      case 'primary': return '#007acc';
      default: return props.$background || 'transparent';
    }
  }};
  
  max-width: ${props => props.$maxWidth || 'none'};
  border-radius: 8px;
  transition: all 0.2s ease-in-out;
`;

const StyledStack = styled.div<{ $spacing?: string; $alignment?: string; $direction?: string }>`
  display: flex;
  flex-direction: ${props => props.$direction === 'horizontal' ? 'row' : 'column'};
  
  gap: ${props => {
    switch (props.$spacing) {
      case 'small': return '8px';
      case 'medium': return '16px';
      case 'large': return '24px';
      default: return '16px';
    }
  }};
  
  align-items: ${props => {
    switch (props.$alignment) {
      case 'start': return 'flex-start';
      case 'center': return 'center';
      case 'end': return 'flex-end';
      case 'stretch': return 'stretch';
      default: return 'stretch';
    }
  }};
`;

const StyledInline = styled.div<{ $spacing?: string; $justification?: string; $wrap?: boolean }>`
  display: flex;
  flex-direction: row;
  
  gap: ${props => {
    switch (props.$spacing) {
      case 'small': return '8px';
      case 'medium': return '16px';
      case 'large': return '24px';
      default: return '16px';
    }
  }};
  
  justify-content: ${props => {
    switch (props.$justification) {
      case 'start': return 'flex-start';
      case 'center': return 'center';
      case 'end': return 'flex-end';
      case 'between': return 'space-between';
      case 'around': return 'space-around';
      default: return 'flex-start';
    }
  }};
  
  flex-wrap: ${props => props.$wrap ? 'wrap' : 'nowrap'};
`;

const StyledText = styled.span<{ 
  $variant?: string; 
  $size?: string; 
  $color?: string; 
  $weight?: string;
}>`
  color: ${props => {
    switch (props.$color) {
      case 'primary': return '#007acc';
      case 'secondary': return '#6c757d';
      case 'muted': return '#999999';
      case 'error': return '#dc3545';
      case 'success': return '#28a745';
      default: return props.$color || '#ffffff';
    }
  }};
  
  font-size: ${props => {
    switch (props.$size) {
      case 'caption': return '12px';
      case 'small': return '14px';
      case 'medium': return '16px';
      case 'large': return '18px';
      case 'xl': return '24px';
      default: return '16px';
    }
  }};
  
  font-weight: ${props => {
    switch (props.$weight) {
      case 'light': return '300';
      case 'normal': return '400';
      case 'medium': return '500';
      case 'bold': return '700';
      default: return props.$variant === 'body' ? '400' : '500';
    }
  }};
  
  line-height: 1.5;
`;

const StyledButton = styled.button<{ 
  $variant?: string; 
  $size?: string; 
  $loading?: boolean;
  $disabled?: boolean;
}>`
  padding: ${props => {
    switch (props.$size) {
      case 'small': return '6px 12px';
      case 'medium': return '8px 16px';
      case 'large': return '12px 24px';
      default: return '8px 16px';
    }
  }};
  
  border: none;
  border-radius: 6px;
  cursor: ${props => props.$disabled ? 'not-allowed' : 'pointer'};
  transition: all 0.2s ease-in-out;
  font-weight: 500;
  
  background: ${props => {
    if (props.$disabled) return '#404040';
    switch (props.$variant) {
      case 'primary': return '#007acc';
      case 'secondary': return '#6c757d';
      case 'ghost': return 'transparent';
      case 'danger': return '#dc3545';
      default: return '#007acc';
    }
  }};
  
  color: ${props => {
    if (props.$disabled) return '#999999';
    return props.$variant === 'ghost' ? '#007acc' : '#ffffff';
  }};
  
  border: ${props => props.$variant === 'ghost' ? '1px solid #007acc' : 'none'};
  
  opacity: ${props => props.$loading ? 0.7 : 1};
  
  &:hover:not(:disabled) {
    opacity: 0.8;
    transform: translateY(-1px);
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
  }
`;

const StyledVoiceInput = styled.div<{ $variant?: string; $size?: string; $isRecording?: boolean }>`
  padding: ${props => {
    switch (props.$size) {
      case 'small': return '12px';
      case 'medium': return '16px';
      case 'large': return '20px';
      default: return '16px';
    }
  }};
  
  border: 2px solid ${props => {
    if (props.$isRecording) return '#28a745';
    switch (props.$variant) {
      case 'primary': return '#007acc';
      case 'secondary': return '#6c757d';
      default: return '#007acc';
    }
  }};
  
  border-radius: 12px;
  background: ${props => props.$isRecording ? 'rgba(40, 167, 69, 0.1)' : '#2d2d2d'};
  transition: all 0.3s ease-in-out;
  
  ${props => props.$isRecording && css`
    box-shadow: 0 0 20px rgba(40, 167, 69, 0.3);
    animation: pulse 2s infinite;
  `}
  
  @keyframes pulse {
    0% { box-shadow: 0 0 20px rgba(40, 167, 69, 0.3); }
    50% { box-shadow: 0 0 30px rgba(40, 167, 69, 0.5); }
    100% { box-shadow: 0 0 20px rgba(40, 167, 69, 0.3); }
  }
`;

const VoiceInputContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const VoiceInputStatus = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #cccccc;
`;

const VoiceInputControls = styled.div`
  display: flex;
  gap: 8px;
  justify-content: center;
`;

const AudioLevelIndicator = styled.div<{ $level: number }>`
  width: 100px;
  height: 4px;
  background: #404040;
  border-radius: 2px;
  overflow: hidden;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    width: ${props => Math.min(props.$level * 100, 100)}%;
    background: linear-gradient(90deg, #28a745, #ffc107, #dc3545);
    transition: width 0.1s ease-out;
  }
`;

/**
 * DSL Component implementations
 * 
 * @description
 * React components that implement each DSL primitive type.
 * These components receive DSL instance data and render accordingly.
 */

const ContainerComponent: React.FC<ReactComponentProps> = ({ instance, children, onAction }) => {
  const { props = {} } = instance;
  
  return (
    <StyledContainer
      $padding={props.padding}
      $background={props.background}
      $maxWidth={props.maxWidth}
    >
      {children}
    </StyledContainer>
  );
};

const StackComponent: React.FC<ReactComponentProps> = ({ instance, children }) => {
  const { props = {} } = instance;
  
  return (
    <StyledStack
      $spacing={props.spacing}
      $alignment={props.alignment}
      $direction={props.direction}
    >
      {children}
    </StyledStack>
  );
};

const InlineComponent: React.FC<ReactComponentProps> = ({ instance, children }) => {
  const { props = {} } = instance;
  
  return (
    <StyledInline
      $spacing={props.spacing}
      $justification={props.justification}
      $wrap={props.wrap}
    >
      {children}
    </StyledInline>
  );
};

const TextComponent: React.FC<ReactComponentProps> = ({ instance }) => {
  const { props = {}, state = {} } = instance;
  
  return (
    <StyledText
      $variant={props.variant}
      $size={props.size}
      $color={props.color}
      $weight={props.weight}
    >
      {props.content}
    </StyledText>
  );
};

const ButtonComponent: React.FC<ReactComponentProps> = ({ instance, onAction }) => {
  const { props = {}, state = {}, actions = {} } = instance;

  const handleClick = useCallback(async () => {
    if (actions.onClick) {
      await onAction(actions.onClick);
    }
  }, [actions.onClick, onAction]);

  return (
    <StyledButton
      $variant={props.variant}
      $size={props.size}
      $loading={state.loading}
      $disabled={props.disabled || state.loading}
      onClick={handleClick}
    >
      {state.loading ? 'Loading...' : props.label}
    </StyledButton>
  );
};

const VoiceInputComponent: React.FC<ReactComponentProps> = ({ instance, onAction }) => {
  const { props = {}, state = {}, actions = {} } = instance;
  const [localAudioLevel, setLocalAudioLevel] = useState(0);

  const handleRecordStart = useCallback(async () => {
    if (actions.onRecordStart) {
      await onAction(actions.onRecordStart);
    }
  }, [actions.onRecordStart, onAction]);

  const handleRecordStop = useCallback(async () => {
    if (actions.onRecordStop) {
      await onAction(actions.onRecordStop);
    }
  }, [actions.onRecordStop, onAction]);

  const handleSubmit = useCallback(async () => {
    if (actions.onSubmit) {
      await onAction(actions.onSubmit);
    }
  }, [actions.onSubmit, onAction]);

  // Simulate audio level updates when recording
  useEffect(() => {
    if (state.isRecording) {
      const interval = setInterval(() => {
        setLocalAudioLevel(Math.random() * 0.8 + 0.1);
      }, 100);

      return () => clearInterval(interval);
    } else {
      setLocalAudioLevel(0);
    }
  }, [state.isRecording]);

  return (
    <StyledVoiceInput
      $variant={props.variant}
      $size={props.size}
      $isRecording={state.isRecording}
    >
      <VoiceInputContent>
        <VoiceInputStatus>
          <span>{props.placeholder || 'Voice Input'}</span>
          <span>{state.isRecording ? '🎤 Recording...' : '🎤 Ready'}</span>
        </VoiceInputStatus>

        {state.isRecording && (
          <AudioLevelIndicator $level={state.audioLevel || localAudioLevel} />
        )}

        {state.transcription && (
          <StyledText $size="small" $color="secondary">
            "{state.transcription}"
          </StyledText>
        )}

        <VoiceInputControls>
          <StyledButton
            $variant="primary"
            $size="small"
            $disabled={state.isRecording}
            onClick={handleRecordStart}
          >
            Start Recording
          </StyledButton>

          <StyledButton
            $variant="secondary"
            $size="small"
            $disabled={!state.isRecording}
            onClick={handleRecordStop}
          >
            Stop Recording
          </StyledButton>

          {state.transcription && (
            <StyledButton
              $variant="primary"
              $size="small"
              onClick={handleSubmit}
            >
              Submit
            </StyledButton>
          )}
        </VoiceInputControls>

        {state.error && (
          <StyledText $size="small" $color="error">
            Error: {state.error}
          </StyledText>
        )}
      </VoiceInputContent>
    </StyledVoiceInput>
  );
};

/**
 * Default component registry
 *
 * @description
 * Maps DSL component names to React component implementations.
 * Can be extended with custom components.
 */
const createDefaultComponentRegistry = (): ComponentRegistry => {
  const registry = new Map<string, React.ComponentType<ReactComponentProps>>();

  // Layout components
  registry.set('Container', ContainerComponent);
  registry.set('Stack', StackComponent);
  registry.set('Inline', InlineComponent);

  // Display components
  registry.set('Text', TextComponent);

  // Input components
  registry.set('Button', ButtonComponent);
  registry.set('VoiceInput', VoiceInputComponent);

  return registry;
};

/**
 * React DSL Renderer
 *
 * @description
 * Main renderer class that implements the DSLRenderer interface
 * and manages React component rendering, updates, and lifecycle.
 *
 * @example
 * ```typescript
 * const renderer = new ReactDSLRenderer();
 * interpreter.registerRenderer(renderer);
 *
 * const component = interpreter.createComponent('VoiceInput', {
 *   placeholder: 'Speak your command...'
 * });
 *
 * const reactElement = renderer.getRenderedComponent(component.id);
 * ```
 */
export class ReactDSLRenderer implements DSLRenderer {
  name = 'react';

  private componentRegistry: ComponentRegistry;
  private renderedComponents: Map<string, RenderedComponent> = new Map();
  private interpreter: DSLInterpreter | null = null;
  private updateCallbacks: Map<string, (element: React.ReactElement) => void> = new Map();

  constructor(customRegistry?: ComponentRegistry) {
    this.componentRegistry = customRegistry || createDefaultComponentRegistry();
    console.log(`📝 React DSL Renderer initialized with ${this.componentRegistry.size} component types`);
  }

  /**
   * Set the DSL interpreter instance
   *
   * @param interpreter - DSL interpreter to use for action execution
   */
  setInterpreter(interpreter: DSLInterpreter): void {
    this.interpreter = interpreter;
  }

  /**
   * Register a custom React component
   *
   * @param componentName - DSL component name
   * @param reactComponent - React component implementation
   */
  registerComponent(componentName: string, reactComponent: React.ComponentType<ReactComponentProps>): void {
    this.componentRegistry.set(componentName, reactComponent);
    console.log(`🔧 Registered custom component: ${componentName}`);
  }

  /**
   * Render a DSL component instance to React element
   *
   * @param instance - DSL component instance
   * @param context - Component context
   * @returns React element
   */
  renderComponent(instance: ComponentInstance, context: ComponentContext): React.ReactElement {
    const ComponentClass = this.componentRegistry.get(instance.component);

    if (!ComponentClass) {
      console.warn(`⚠️ Unknown component type: ${instance.component}`);
      return this.renderUnknownComponent(instance);
    }

    // Create action handler
    const handleAction = async (actionString: string) => {
      if (!this.interpreter) {
        console.error('❌ No interpreter available for action execution');
        return;
      }

      try {
        const action = this.interpreter.parseAction(actionString);
        await this.interpreter.executeAction(instance.id!, action);
      } catch (error) {
        console.error('❌ Action execution failed:', error);
      }
    };

    // Render children recursively
    const children = instance.children?.map((child, index) =>
      this.renderComponent(child, context)
    );

    // Create React element
    const reactElement = React.createElement(ComponentClass, {
      key: instance.id,
      instance,
      context,
      onAction: handleAction,
      children,
    });

    // Track rendered component
    if (instance.id) {
      this.renderedComponents.set(instance.id, {
        id: instance.id,
        instance,
        reactElement,
        mountTime: Date.now(),
      });
    }

    console.log(`🎨 Rendered component: ${instance.component} (${instance.id})`);
    return reactElement;
  }

  /**
   * Handle component state changes
   *
   * @param event - State change event
   */
  onStateChange(event: StateChangeEvent): void {
    const { componentId, key, newValue } = event;
    const renderedComponent = this.renderedComponents.get(componentId);

    if (!renderedComponent) {
      console.warn(`⚠️ State change for unknown component: ${componentId}`);
      return;
    }

    // Update the instance state
    if (renderedComponent.instance.state) {
      renderedComponent.instance.state[key] = newValue;
    } else {
      renderedComponent.instance.state = { [key]: newValue };
    }

    // Re-render the component with updated state
    const updatedElement = this.renderComponent(renderedComponent.instance, {
      scope: 'local',
      data: {},
    });

    // Update the tracked component
    this.renderedComponents.set(componentId, {
      ...renderedComponent,
      reactElement: updatedElement,
    });

    // Notify update callback if registered
    const updateCallback = this.updateCallbacks.get(componentId);
    if (updateCallback) {
      updateCallback(updatedElement);
    }

    console.log(`🔄 Component state updated: ${componentId}.${key} = ${newValue}`);
  }

  /**
   * Handle component actions
   *
   * @param componentId - Component ID
   * @param action - Parsed action
   */
  async onAction(componentId: string, action: ParsedAction): Promise<any> {
    console.log(`⚡ React renderer handling action: ${action.type} for ${componentId}`);

    // React renderer doesn't need to do anything special for actions
    // The action execution is handled by the DSL interpreter
    // This method is called after action execution for any renderer-specific updates

    return null;
  }

  /**
   * Update component props
   *
   * @param componentId - Component ID
   * @param props - New props
   */
  updateProps(componentId: string, props: Record<string, any>): void {
    const renderedComponent = this.renderedComponents.get(componentId);

    if (!renderedComponent) {
      console.warn(`⚠️ Props update for unknown component: ${componentId}`);
      return;
    }

    // Update the instance props
    renderedComponent.instance.props = { ...renderedComponent.instance.props, ...props };

    // Re-render the component with updated props
    const updatedElement = this.renderComponent(renderedComponent.instance, {
      scope: 'local',
      data: {},
    });

    // Update the tracked component
    this.renderedComponents.set(componentId, {
      ...renderedComponent,
      reactElement: updatedElement,
    });

    // Notify update callback if registered
    const updateCallback = this.updateCallbacks.get(componentId);
    if (updateCallback) {
      updateCallback(updatedElement);
    }

    console.log(`🔄 Component props updated: ${componentId}`);
  }

  /**
   * Destroy a component
   *
   * @param componentId - Component ID to destroy
   */
  destroyComponent(componentId: string): void {
    const renderedComponent = this.renderedComponents.get(componentId);

    if (!renderedComponent) {
      console.warn(`⚠️ Attempted to destroy unknown component: ${componentId}`);
      return;
    }

    // Clean up tracking
    this.renderedComponents.delete(componentId);
    this.updateCallbacks.delete(componentId);

    console.log(`🗑️ React component destroyed: ${componentId}`);
  }

  /**
   * Get rendered React element for a component
   *
   * @param componentId - Component ID
   * @returns React element or null if not found
   */
  getRenderedComponent(componentId: string): React.ReactElement | null {
    const renderedComponent = this.renderedComponents.get(componentId);
    return renderedComponent?.reactElement || null;
  }

  /**
   * Register update callback for a component
   *
   * @param componentId - Component ID
   * @param callback - Callback function called when component updates
   */
  onComponentUpdate(componentId: string, callback: (element: React.ReactElement) => void): void {
    this.updateCallbacks.set(componentId, callback);
  }

  /**
   * Remove update callback for a component
   *
   * @param componentId - Component ID
   */
  removeComponentUpdateCallback(componentId: string): void {
    this.updateCallbacks.delete(componentId);
  }

  /**
   * Render unknown component fallback
   *
   * @param instance - Component instance
   * @returns React element for unknown component
   */
  private renderUnknownComponent(instance: ComponentInstance): React.ReactElement {
    return React.createElement(
      'div',
      {
        key: instance.id,
        style: {
          padding: '8px',
          background: '#ff6b6b',
          color: 'white',
          borderRadius: '4px',
          fontSize: '14px',
        },
      },
      `Unknown component: ${instance.component}`
    );
  }

  /**
   * Get renderer statistics
   *
   * @returns Statistics object
   */
  getStats(): {
    name: string;
    renderedComponents: number;
    registeredComponents: number;
    updateCallbacks: number;
  } {
    return {
      name: this.name,
      renderedComponents: this.renderedComponents.size,
      registeredComponents: this.componentRegistry.size,
      updateCallbacks: this.updateCallbacks.size,
    };
  }
}

/**
 * React Hook for DSL Component Rendering
 *
 * @description
 * React hook that provides easy integration with the DSL renderer
 * for rendering DSL components within React applications.
 *
 * @param interpreter - DSL interpreter instance
 * @param componentId - Component ID to render
 * @returns React element and update functions
 */
export const useDSLComponent = (interpreter: DSLInterpreter, componentId: string) => {
  const [reactElement, setReactElement] = useState<React.ReactElement | null>(null);
  const [renderer] = useState(() => {
    const r = new ReactDSLRenderer();
    r.setInterpreter(interpreter);
    interpreter.registerRenderer(r);
    return r;
  });

  useEffect(() => {
    const component = interpreter.getComponent(componentId);
    if (component) {
      const element = renderer.renderComponent(component, { scope: 'local', data: {} });
      setReactElement(element);

      // Register update callback
      renderer.onComponentUpdate(componentId, setReactElement);

      return () => {
        renderer.removeComponentUpdateCallback(componentId);
      };
    }
  }, [interpreter, componentId, renderer]);

  return {
    reactElement,
    renderer,
    updateComponent: (props: Record<string, any>) => {
      renderer.updateProps(componentId, props);
    },
  };
};

/**
 * React Component for DSL Rendering
 *
 * @description
 * React component that renders a DSL component instance.
 * Handles automatic updates and lifecycle management.
 */
export const DSLComponentRenderer: React.FC<{
  interpreter: DSLInterpreter;
  componentId: string;
  className?: string;
  style?: React.CSSProperties;
}> = ({ interpreter, componentId, className, style }) => {
  const { reactElement } = useDSLComponent(interpreter, componentId);

  if (!reactElement) {
    return (
      <div className={className} style={style}>
        <StyledText $color="muted" $size="small">
          Loading component...
        </StyledText>
      </div>
    );
  }

  return (
    <div className={className} style={style}>
      {reactElement}
    </div>
  );
};

/**
 * React Hook for DSL Interpreter Integration
 *
 * @description
 * Hook that creates and manages a DSL interpreter with React renderer.
 * Provides easy integration for React applications.
 *
 * @param schema - Universal System DSL schema
 * @returns Interpreter instance and utility functions
 */
export const useDSLInterpreter = (schema: any) => {
  const [interpreter] = useState(() => new DSLInterpreter(schema));
  const [renderer] = useState(() => {
    const r = new ReactDSLRenderer();
    r.setInterpreter(interpreter);
    interpreter.registerRenderer(r);
    return r;
  });

  const createComponent = useCallback((
    componentName: string,
    props: Record<string, any> = {},
    initialState: Record<string, any> = {}
  ) => {
    return interpreter.createComponent(componentName, props, initialState);
  }, [interpreter]);

  const createFromExample = useCallback((exampleName: string) => {
    return interpreter.createFromExample(exampleName);
  }, [interpreter]);

  const generateFromPrompt = useCallback(async (prompt: string) => {
    return interpreter.generateFromPrompt(prompt);
  }, [interpreter]);

  const executeAction = useCallback(async (componentId: string, actionString: string) => {
    const action = interpreter.parseAction(actionString);
    return interpreter.executeAction(componentId, action);
  }, [interpreter]);

  return {
    interpreter,
    renderer,
    createComponent,
    createFromExample,
    generateFromPrompt,
    executeAction,
    getStats: () => ({
      interpreter: interpreter.getStats(),
      renderer: renderer.getStats(),
    }),
  };
};

/**
 * Export default component registry for external use
 */
export { createDefaultComponentRegistry };

/**
 * Export styled components for custom component development
 */
export {
  StyledContainer,
  StyledStack,
  StyledInline,
  StyledText,
  StyledButton,
  StyledVoiceInput,
};
