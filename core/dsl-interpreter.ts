/**
 * @fileoverview DSL Interpreter Engine - Universal System Core
 * 
 * @description
 * Core engine that interprets Universal System DSL schemas and transforms
 * them into executable component instances. Handles state management,
 * action processing, context resolution, and provides abstract interfaces
 * for different renderers (React, LLM, etc.).
 * 
 * @design_principles
 * - Schema-driven: All behavior derived from YAML schema definitions
 * - Renderer-agnostic: Abstract interface supports multiple output targets
 * - State-aware: Comprehensive state management with reactive updates
 * - Action-oriented: Declarative action syntax with secure execution
 * - Context-conscious: Hierarchical context and data binding support
 * 
 * @llm_contract
 * This interpreter serves as the universal translator between:
 * 1. YAML DSL schema definitions (human/LLM readable)
 * 2. Executable component instances (runtime objects)
 * 3. Renderer-specific implementations (React, natural language, etc.)
 * 4. Backend service integrations (LLM, TTS, database)
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import { EventEmitter } from 'events';

/**
 * Universal System DSL Schema interface
 * 
 * @description
 * TypeScript representation of the YAML schema structure for
 * compile-time validation and IDE support.
 */
export interface UniversalSystemSchema {
  version: string;
  description: string;
  principles: Record<string, string>;
  primitives: {
    layout: { types: ComponentDefinition[] };
    input: { types: ComponentDefinition[] };
    display: { types: ComponentDefinition[] };
    action: { types: ComponentDefinition[] };
  };
  binding: {
    state_flow: { type: string; pattern: string };
    context_scope: { type: string; levels: string[] };
    update_strategy: { type: string; triggers: string[] };
  };
  events: {
    syntax: { format: string; examples: string[] };
    action_types: Record<string, ActionTypeDefinition>;
  };
  examples: Record<string, ComponentInstance>;
  llm_guidelines: {
    understanding_patterns: string[];
    generation_principles: string[];
    voice_command_mapping: Record<string, string>;
  };
}

/**
 * Component definition from DSL schema
 */
export interface ComponentDefinition {
  name: string;
  purpose: string;
  props: string[];
  state?: string[];
  actions?: string[];
}

/**
 * Action type definition from DSL schema
 */
export interface ActionTypeDefinition {
  description: string;
  syntax: string;
  examples: string[];
}

/**
 * Component instance definition
 */
export interface ComponentInstance {
  component: string;
  props?: Record<string, any>;
  state?: Record<string, any>;
  actions?: Record<string, string>;
  children?: ComponentInstance[];
  context?: {
    scope: string;
    [key: string]: any;
  };
}

/**
 * Parsed action result
 */
export interface ParsedAction {
  type: 'setState' | 'emit' | 'navigate' | 'command' | 'custom';
  target?: string;
  parameters: Record<string, any>;
  raw: string;
}

/**
 * Component state change event
 */
export interface StateChangeEvent {
  componentId: string;
  key: string;
  oldValue: any;
  newValue: any;
  timestamp: number;
}

/**
 * Component context interface
 */
export interface ComponentContext {
  scope: 'local' | 'parent' | 'global';
  data: Record<string, any>;
  parent?: ComponentContext;
}

/**
 * Renderer interface for different output targets
 * 
 * @description
 * Abstract interface that different renderers (React, LLM, etc.)
 * must implement to receive interpreted component data.
 */
export interface DSLRenderer {
  /** Renderer identifier */
  name: string;
  
  /** Render a component instance */
  renderComponent(instance: ComponentInstance, context: ComponentContext): any;
  
  /** Handle component state changes */
  onStateChange(event: StateChangeEvent): void;
  
  /** Handle component actions */
  onAction(componentId: string, action: ParsedAction): Promise<any>;
  
  /** Update component props */
  updateProps(componentId: string, props: Record<string, any>): void;
  
  /** Destroy component */
  destroyComponent(componentId: string): void;
}

/**
 * DSL Interpreter Engine
 * 
 * @description
 * Core engine that interprets Universal System DSL schemas and manages
 * component lifecycle, state, actions, and renderer communication.
 * 
 * @example
 * ```typescript
 * const interpreter = new DSLInterpreter(schema);
 * const reactRenderer = new ReactDSLRenderer();
 * interpreter.registerRenderer(reactRenderer);
 * 
 * const component = interpreter.createComponent('VoiceInput', {
 *   placeholder: 'Speak your command...'
 * });
 * ```
 */
export class DSLInterpreter extends EventEmitter {
  private schema: UniversalSystemSchema;
  private renderers: Map<string, DSLRenderer> = new Map();
  private components: Map<string, ComponentInstance> = new Map();
  private componentStates: Map<string, Record<string, any>> = new Map();
  private contexts: Map<string, ComponentContext> = new Map();
  private nextComponentId = 1;
  
  /**
   * Create DSL interpreter instance
   * 
   * @param schema - Universal System DSL schema
   */
  constructor(schema: UniversalSystemSchema) {
    super();
    this.schema = schema;
    this.validateSchema();
    
    console.log(`🧠 DSL Interpreter initialized with schema v${schema.version}`);
  }
  
  /**
   * Validate DSL schema structure
   * 
   * @description
   * Ensures the schema has all required fields and valid structure
   * for safe interpretation.
   */
  private validateSchema(): void {
    if (!this.schema.version) {
      throw new Error('Schema missing version field');
    }
    
    if (!this.schema.primitives) {
      throw new Error('Schema missing primitives definition');
    }
    
    const requiredPrimitives = ['layout', 'input', 'display', 'action'];
    for (const primitive of requiredPrimitives) {
      if (!this.schema.primitives[primitive as keyof typeof this.schema.primitives]) {
        throw new Error(`Schema missing primitive category: ${primitive}`);
      }
    }
    
    if (!this.schema.events?.action_types) {
      throw new Error('Schema missing action types definition');
    }
    
    console.log('✅ DSL Schema validation passed');
  }
  
  /**
   * Register a renderer for component output
   * 
   * @param renderer - Renderer implementation
   */
  registerRenderer(renderer: DSLRenderer): void {
    this.renderers.set(renderer.name, renderer);
    console.log(`📝 Registered renderer: ${renderer.name}`);
  }
  
  /**
   * Unregister a renderer
   * 
   * @param rendererName - Name of renderer to remove
   */
  unregisterRenderer(rendererName: string): void {
    this.renderers.delete(rendererName);
    console.log(`🗑️ Unregistered renderer: ${rendererName}`);
  }
  
  /**
   * Get component definition from schema
   * 
   * @param componentName - Name of component to find
   * @returns Component definition or null if not found
   */
  getComponentDefinition(componentName: string): ComponentDefinition | null {
    const allPrimitives = [
      ...this.schema.primitives.layout.types,
      ...this.schema.primitives.input.types,
      ...this.schema.primitives.display.types,
      ...this.schema.primitives.action.types,
    ];
    
    return allPrimitives.find(def => def.name === componentName) || null;
  }
  
  /**
   * Create a component instance from definition
   * 
   * @param componentName - Name of component to create
   * @param props - Component properties
   * @param initialState - Initial component state
   * @param context - Component context
   * @returns Created component instance with unique ID
   */
  createComponent(
    componentName: string,
    props: Record<string, any> = {},
    initialState: Record<string, any> = {},
    context: ComponentContext | null = null
  ): ComponentInstance & { id: string } {
    const definition = this.getComponentDefinition(componentName);
    if (!definition) {
      throw new Error(`Unknown component: ${componentName}`);
    }
    
    const componentId = `${componentName}_${this.nextComponentId++}`;
    
    // Validate props against definition
    const validProps = this.validateProps(definition, props);
    
    // Initialize state with defaults
    const defaultState = this.getDefaultState(definition);
    const componentState = { ...defaultState, ...initialState };
    
    // Create component instance
    const instance: ComponentInstance & { id: string } = {
      id: componentId,
      component: componentName,
      props: validProps,
      state: componentState,
      actions: {},
      children: [],
    };
    
    // Store component and state
    this.components.set(componentId, instance);
    this.componentStates.set(componentId, componentState);
    
    // Set up context
    if (context) {
      this.contexts.set(componentId, context);
    }
    
    // Notify renderers
    this.renderers.forEach(renderer => {
      try {
        renderer.renderComponent(instance, context || this.createDefaultContext());
      } catch (error) {
        console.error(`❌ Renderer ${renderer.name} failed to render component:`, error);
      }
    });
    
    console.log(`🎨 Created component: ${componentName} (${componentId})`);
    this.emit('componentCreated', { componentId, instance });
    
    return instance;
  }
  
  /**
   * Validate component props against definition
   * 
   * @param definition - Component definition
   * @param props - Props to validate
   * @returns Validated props object
   */
  private validateProps(definition: ComponentDefinition, props: Record<string, any>): Record<string, any> {
    const validProps: Record<string, any> = {};
    
    // Only include props that are defined in the schema
    for (const propName of definition.props) {
      if (props.hasOwnProperty(propName)) {
        validProps[propName] = props[propName];
      }
    }
    
    // Warn about unknown props
    for (const propName in props) {
      if (!definition.props.includes(propName)) {
        console.warn(`⚠️ Unknown prop '${propName}' for component '${definition.name}'`);
      }
    }
    
    return validProps;
  }
  
  /**
   * Get default state for component definition
   * 
   * @param definition - Component definition
   * @returns Default state object
   */
  private getDefaultState(definition: ComponentDefinition): Record<string, any> {
    const defaultState: Record<string, any> = {};
    
    if (definition.state) {
      for (const stateKey of definition.state) {
        // Set sensible defaults based on common patterns
        switch (stateKey) {
          case 'isRecording':
          case 'loading':
          case 'disabled':
          case 'checked':
          case 'expanded':
          case 'selected':
            defaultState[stateKey] = false;
            break;
          case 'value':
          case 'transcription':
          case 'content':
          case 'error':
            defaultState[stateKey] = '';
            break;
          case 'audioLevel':
          case 'progress':
          case 'count':
            defaultState[stateKey] = 0;
            break;
          default:
            defaultState[stateKey] = null;
        }
      }
    }
    
    return defaultState;
  }
  
  /**
   * Create default context for components
   * 
   * @returns Default component context
   */
  private createDefaultContext(): ComponentContext {
    return {
      scope: 'local',
      data: {},
    };
  }
  
  /**
   * Parse action syntax into structured action object
   * 
   * @param actionString - Action string (e.g., "setState:key=value")
   * @returns Parsed action object
   */
  parseAction(actionString: string): ParsedAction {
    const [actionType, parametersString] = actionString.split(':', 2);
    
    if (!actionType) {
      throw new Error(`Invalid action syntax: ${actionString}`);
    }
    
    const parameters: Record<string, any> = {};
    
    if (parametersString) {
      // Parse parameters based on action type
      switch (actionType) {
        case 'setState':
          const [key, value] = parametersString.split('=', 2);
          if (key && value !== undefined) {
            // Type conversion for common values
            let parsedValue: any = value;
            if (value === 'true') parsedValue = true;
            else if (value === 'false') parsedValue = false;
            else if (!isNaN(Number(value))) parsedValue = Number(value);
            
            parameters.key = key;
            parameters.value = parsedValue;
          }
          break;
          
        case 'emit':
          const [eventName, eventData] = parametersString.split('=', 2);
          parameters.eventName = eventName;
          parameters.eventData = eventData || null;
          break;
          
        case 'navigate':
          parameters.route = parametersString.replace('route=', '');
          break;
          
        case 'command':
          parameters.command = parametersString.replace('execute=', '');
          break;
          
        default:
          // Custom action - parse as key=value pairs
          const pairs = parametersString.split('&');
          for (const pair of pairs) {
            const [key, value] = pair.split('=', 2);
            if (key) {
              parameters[key] = value || '';
            }
          }
      }
    }
    
    return {
      type: actionType as ParsedAction['type'],
      parameters,
      raw: actionString,
    };
  }

  /**
   * Execute a parsed action on a component
   *
   * @param componentId - ID of component to execute action on
   * @param action - Parsed action to execute
   * @returns Promise resolving to action result
   */
  async executeAction(componentId: string, action: ParsedAction): Promise<any> {
    const component = this.components.get(componentId);
    if (!component) {
      throw new Error(`Component not found: ${componentId}`);
    }

    console.log(`⚡ Executing action: ${action.raw} on ${componentId}`);

    let result: any = null;

    switch (action.type) {
      case 'setState':
        result = await this.handleSetState(componentId, action.parameters);
        break;

      case 'emit':
        result = await this.handleEmit(componentId, action.parameters);
        break;

      case 'navigate':
        result = await this.handleNavigate(componentId, action.parameters);
        break;

      case 'command':
        result = await this.handleCommand(componentId, action.parameters);
        break;

      default:
        result = await this.handleCustomAction(componentId, action);
    }

    // Notify renderers of action execution
    this.renderers.forEach(renderer => {
      try {
        renderer.onAction(componentId, action);
      } catch (error) {
        console.error(`❌ Renderer ${renderer.name} failed to handle action:`, error);
      }
    });

    this.emit('actionExecuted', { componentId, action, result });
    return result;
  }

  /**
   * Handle setState action
   */
  private async handleSetState(componentId: string, parameters: Record<string, any>): Promise<void> {
    const { key, value } = parameters;
    if (!key) {
      throw new Error('setState action missing key parameter');
    }

    const currentState = this.componentStates.get(componentId) || {};
    const oldValue = currentState[key];

    // Update state
    currentState[key] = value;
    this.componentStates.set(componentId, currentState);

    // Update component instance
    const component = this.components.get(componentId);
    if (component) {
      component.state = { ...currentState };
    }

    // Create state change event
    const stateChangeEvent: StateChangeEvent = {
      componentId,
      key,
      oldValue,
      newValue: value,
      timestamp: Date.now(),
    };

    // Notify renderers of state change
    this.renderers.forEach(renderer => {
      try {
        renderer.onStateChange(stateChangeEvent);
      } catch (error) {
        console.error(`❌ Renderer ${renderer.name} failed to handle state change:`, error);
      }
    });

    console.log(`🔄 State updated: ${componentId}.${key} = ${value}`);
    this.emit('stateChanged', stateChangeEvent);
  }

  /**
   * Handle emit action
   */
  private async handleEmit(componentId: string, parameters: Record<string, any>): Promise<void> {
    const { eventName, eventData } = parameters;
    if (!eventName) {
      throw new Error('emit action missing eventName parameter');
    }

    const eventPayload = {
      componentId,
      eventName,
      eventData,
      timestamp: Date.now(),
    };

    console.log(`📡 Event emitted: ${eventName} from ${componentId}`);
    this.emit('componentEvent', eventPayload);
  }

  /**
   * Handle navigate action
   */
  private async handleNavigate(componentId: string, parameters: Record<string, any>): Promise<void> {
    const { route } = parameters;
    if (!route) {
      throw new Error('navigate action missing route parameter');
    }

    console.log(`🧭 Navigation requested: ${route} from ${componentId}`);
    this.emit('navigationRequested', { componentId, route });
  }

  /**
   * Handle command action
   */
  private async handleCommand(componentId: string, parameters: Record<string, any>): Promise<string> {
    const { command } = parameters;
    if (!command) {
      throw new Error('command action missing command parameter');
    }

    console.log(`💻 Command execution requested: ${command} from ${componentId}`);
    this.emit('commandRequested', { componentId, command });

    return `Command executed: ${command}`;
  }

  /**
   * Handle custom action
   */
  private async handleCustomAction(componentId: string, action: ParsedAction): Promise<any> {
    console.log(`🔧 Custom action: ${action.type} from ${componentId}`);
    this.emit('customAction', { componentId, action });
    return null;
  }

  /**
   * Update component props
   *
   * @param componentId - Component ID
   * @param newProps - New props to merge
   */
  updateComponentProps(componentId: string, newProps: Record<string, any>): void {
    const component = this.components.get(componentId);
    if (!component) {
      throw new Error(`Component not found: ${componentId}`);
    }

    const definition = this.getComponentDefinition(component.component);
    if (!definition) {
      throw new Error(`Component definition not found: ${component.component}`);
    }

    // Validate and merge props
    const validatedProps = this.validateProps(definition, newProps);
    component.props = { ...component.props, ...validatedProps };

    // Notify renderers
    this.renderers.forEach(renderer => {
      try {
        renderer.updateProps(componentId, component.props!);
      } catch (error) {
        console.error(`❌ Renderer ${renderer.name} failed to update props:`, error);
      }
    });

    console.log(`🔄 Props updated: ${componentId}`);
    this.emit('propsUpdated', { componentId, props: component.props });
  }

  /**
   * Destroy a component instance
   *
   * @param componentId - Component ID to destroy
   */
  destroyComponent(componentId: string): void {
    const component = this.components.get(componentId);
    if (!component) {
      console.warn(`⚠️ Attempted to destroy non-existent component: ${componentId}`);
      return;
    }

    // Notify renderers
    this.renderers.forEach(renderer => {
      try {
        renderer.destroyComponent(componentId);
      } catch (error) {
        console.error(`❌ Renderer ${renderer.name} failed to destroy component:`, error);
      }
    });

    // Clean up internal state
    this.components.delete(componentId);
    this.componentStates.delete(componentId);
    this.contexts.delete(componentId);

    console.log(`🗑️ Component destroyed: ${componentId}`);
    this.emit('componentDestroyed', { componentId });
  }

  /**
   * Get component state
   *
   * @param componentId - Component ID
   * @returns Component state or null if not found
   */
  getComponentState(componentId: string): Record<string, any> | null {
    return this.componentStates.get(componentId) || null;
  }

  /**
   * Get component instance
   *
   * @param componentId - Component ID
   * @returns Component instance or null if not found
   */
  getComponent(componentId: string): ComponentInstance | null {
    return this.components.get(componentId) || null;
  }

  /**
   * Get all component instances
   *
   * @returns Map of all component instances
   */
  getAllComponents(): Map<string, ComponentInstance> {
    return new Map(this.components);
  }

  /**
   * Create component from schema example
   *
   * @param exampleName - Name of example in schema
   * @returns Created component instance
   */
  createFromExample(exampleName: string): ComponentInstance & { id: string } {
    const example = this.schema.examples[exampleName];
    if (!example) {
      throw new Error(`Example not found: ${exampleName}`);
    }

    return this.createComponent(
      example.component,
      example.props || {},
      example.state || {},
      example.context ? {
        scope: example.context.scope as 'local' | 'parent' | 'global',
        data: example.context,
      } : null
    );
  }

  /**
   * Generate component from LLM prompt
   *
   * @param prompt - Natural language description
   * @returns Promise resolving to created component
   */
  async generateFromPrompt(prompt: string): Promise<ComponentInstance & { id: string }> {
    console.log(`🤖 Generating component from prompt: "${prompt}"`);

    // Use LLM guidelines to map prompt to component
    const mapping = this.schema.llm_guidelines.voice_command_mapping;

    // Simple keyword matching (TODO: Implement proper LLM integration)
    let componentName = 'Container'; // Default fallback
    let props: Record<string, any> = {};

    for (const [command, description] of Object.entries(mapping)) {
      if (prompt.toLowerCase().includes(command.toLowerCase())) {
        // Extract component name from description
        const match = description.match(/component: (\w+)/);
        if (match) {
          componentName = match[1];
        }
        break;
      }
    }

    // Set props based on prompt context
    if (prompt.includes('voice') || prompt.includes('speak')) {
      props.placeholder = 'Speak your command...';
      props.variant = 'primary';
    } else if (prompt.includes('text') || prompt.includes('type')) {
      props.placeholder = 'Type your message...';
    }

    const component = this.createComponent(componentName, props);

    console.log(`✨ Generated component: ${componentName} from prompt`);
    this.emit('componentGenerated', { prompt, component });

    return component;
  }

  /**
   * Get schema information
   *
   * @returns Schema object
   */
  getSchema(): UniversalSystemSchema {
    return this.schema;
  }

  /**
   * Get interpreter statistics
   *
   * @returns Statistics object
   */
  getStats(): {
    schemaVersion: string;
    componentCount: number;
    rendererCount: number;
    primitiveTypes: number;
    exampleCount: number;
  } {
    const allPrimitives = [
      ...this.schema.primitives.layout.types,
      ...this.schema.primitives.input.types,
      ...this.schema.primitives.display.types,
      ...this.schema.primitives.action.types,
    ];

    return {
      schemaVersion: this.schema.version,
      componentCount: this.components.size,
      rendererCount: this.renderers.size,
      primitiveTypes: allPrimitives.length,
      exampleCount: Object.keys(this.schema.examples).length,
    };
  }
}
