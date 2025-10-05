/**
 * @fileoverview LLM UI Schema Generator - Natural Language to DSL Bridge
 * 
 * @description
 * Intelligent UI schema generator that transforms natural language descriptions
 * into valid Universal System DSL component definitions. Uses LLM integration
 * for intent recognition, context awareness, and intelligent schema generation.
 * 
 * @design_principles
 * - Intent-driven: Understand user goals, not just keywords
 * - Context-aware: Use existing patterns and component relationships
 * - Validation-first: Generate only valid, renderable schemas
 * - Learning-enabled: Improve generation based on usage patterns
 * - Composable: Build complex UIs from simple component combinations
 * 
 * @llm_contract
 * This generator serves as the intelligent bridge between:
 * 1. Natural language user input ("Create a voice input with submit button")
 * 2. Structured DSL component definitions (YAML schema format)
 * 3. Visual UI components (via React renderer integration)
 * 4. Backend LLM services (for advanced natural language processing)
 * 
 * @pipeline_flow
 * Voice Input → Intent Recognition → Schema Generation → Component Creation → UI Rendering
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import {
  UniversalSystemSchema,
  ComponentInstance,
  ComponentDefinition,
  DSLInterpreter,
} from '../core/dsl-interpreter';

/**
 * Intent classification for UI generation
 * 
 * @description
 * Categorizes user intents for appropriate UI component selection
 * and schema generation strategies.
 */
export enum UIIntent {
  CREATE_INPUT = 'create_input',
  CREATE_DISPLAY = 'create_display',
  CREATE_LAYOUT = 'create_layout',
  CREATE_ACTION = 'create_action',
  MODIFY_EXISTING = 'modify_existing',
  CREATE_FORM = 'create_form',
  CREATE_NAVIGATION = 'create_navigation',
  CREATE_COMPLEX = 'create_complex',
  UNKNOWN = 'unknown',
}

/**
 * UI generation context
 * 
 * @description
 * Context information that influences schema generation decisions,
 * including existing components, user preferences, and usage patterns.
 */
export interface UIGenerationContext {
  /** Existing components in the current interface */
  existingComponents: ComponentInstance[];
  
  /** User preferences and patterns */
  userPreferences: {
    preferredVariants: Record<string, string>;
    commonProps: Record<string, any>;
    stylePreferences: Record<string, any>;
  };
  
  /** Current application context */
  applicationContext: {
    currentRoute: string;
    activeFeatures: string[];
    userRole: string;
  };
  
  /** Usage patterns and learning data */
  usagePatterns: {
    frequentCombinations: Array<{ components: string[]; frequency: number }>;
    successfulGenerations: Array<{ prompt: string; schema: ComponentInstance }>;
    userFeedback: Array<{ prompt: string; rating: number; improvements: string[] }>;
  };
}

/**
 * Generated schema result
 * 
 * @description
 * Result of schema generation including the generated components,
 * confidence scores, and metadata for validation and improvement.
 */
export interface GeneratedSchemaResult {
  /** Generated component instances */
  components: ComponentInstance[];
  
  /** Confidence score (0-1) for generation quality */
  confidence: number;
  
  /** Recognized intent from the prompt */
  intent: UIIntent;
  
  /** Extracted keywords and entities */
  entities: {
    componentTypes: string[];
    properties: Record<string, any>;
    relationships: Array<{ parent: string; child: string }>;
  };
  
  /** Generation metadata */
  metadata: {
    processingTime: number;
    llmTokensUsed?: number;
    fallbacksUsed: string[];
    validationErrors: string[];
  };
  
  /** Suggestions for improvement */
  suggestions: string[];
}

/**
 * LLM service interface for natural language processing
 * 
 * @description
 * Abstract interface for LLM integration, allowing different
 * LLM providers (Ollama, OpenAI, Claude, etc.) to be used.
 */
export interface LLMService {
  /** Generate text completion from prompt */
  generateCompletion(prompt: string, options?: any): Promise<string>;
  
  /** Extract structured data from text */
  extractStructuredData(text: string, schema: any): Promise<any>;
  
  /** Classify intent from user input */
  classifyIntent(input: string, intents: string[]): Promise<{ intent: string; confidence: number }>;
  
  /** Generate embeddings for semantic similarity */
  generateEmbeddings(text: string): Promise<number[]>;
}

/**
 * Intent recognition patterns
 * 
 * @description
 * Patterns and keywords for recognizing different UI generation intents
 * from natural language input.
 */
const INTENT_PATTERNS: Record<UIIntent, {
  keywords: string[];
  patterns: RegExp[];
  examples: string[];
}> = {
  [UIIntent.CREATE_INPUT]: {
    keywords: ['input', 'voice', 'text', 'field', 'form', 'enter', 'type', 'speak'],
    patterns: [
      /create.*(?:input|field)/i,
      /(?:voice|text).*input/i,
      /add.*(?:input|field)/i,
      /need.*(?:input|field)/i,
    ],
    examples: ['create a voice input', 'add text field', 'I need an input for messages'],
  },
  
  [UIIntent.CREATE_DISPLAY]: {
    keywords: ['show', 'display', 'text', 'label', 'message', 'content', 'information'],
    patterns: [
      /show.*(?:text|message|content)/i,
      /display.*(?:information|data)/i,
      /add.*(?:label|text)/i,
    ],
    examples: ['show a message', 'display user information', 'add a title'],
  },
  
  [UIIntent.CREATE_LAYOUT]: {
    keywords: ['layout', 'container', 'stack', 'arrange', 'organize', 'structure'],
    patterns: [
      /create.*(?:layout|container)/i,
      /arrange.*(?:components|elements)/i,
      /organize.*(?:ui|interface)/i,
    ],
    examples: ['create a container', 'arrange components vertically', 'organize the layout'],
  },
  
  [UIIntent.CREATE_ACTION]: {
    keywords: ['button', 'click', 'action', 'submit', 'send', 'execute', 'trigger'],
    patterns: [
      /create.*button/i,
      /add.*(?:button|action)/i,
      /need.*(?:button|action)/i,
    ],
    examples: ['create a submit button', 'add action button', 'need a send button'],
  },
  
  [UIIntent.CREATE_FORM]: {
    keywords: ['form', 'submit', 'fields', 'inputs', 'validation', 'data entry'],
    patterns: [
      /create.*form/i,
      /build.*form/i,
      /form.*(?:with|containing)/i,
    ],
    examples: ['create a contact form', 'build a registration form', 'form with name and email'],
  },
  
  [UIIntent.CREATE_NAVIGATION]: {
    keywords: ['navigation', 'menu', 'nav', 'sidebar', 'links', 'routes'],
    patterns: [
      /create.*(?:navigation|menu|nav)/i,
      /add.*(?:navigation|menu)/i,
      /build.*(?:sidebar|menu)/i,
    ],
    examples: ['create navigation menu', 'add sidebar navigation', 'build main menu'],
  },
  
  [UIIntent.CREATE_COMPLEX]: {
    keywords: ['dashboard', 'interface', 'application', 'system', 'complete', 'full'],
    patterns: [
      /create.*(?:dashboard|interface|app)/i,
      /build.*(?:complete|full).*(?:ui|interface)/i,
      /design.*(?:system|application)/i,
    ],
    examples: ['create a dashboard', 'build complete interface', 'design chat application'],
  },
  
  [UIIntent.MODIFY_EXISTING]: {
    keywords: ['modify', 'change', 'update', 'edit', 'alter', 'adjust'],
    patterns: [
      /(?:modify|change|update).*(?:component|element)/i,
      /edit.*(?:existing|current)/i,
      /alter.*(?:layout|design)/i,
    ],
    examples: ['modify the button color', 'change input placeholder', 'update layout spacing'],
  },
  
  [UIIntent.UNKNOWN]: {
    keywords: [],
    patterns: [],
    examples: [],
  },
};

/**
 * Component generation templates
 * 
 * @description
 * Templates for generating common component patterns based on recognized intents.
 * These templates provide starting points that can be customized based on context.
 */
const COMPONENT_TEMPLATES: Record<string, ComponentInstance> = {
  voice_input_basic: {
    component: 'VoiceInput',
    props: {
      placeholder: 'Speak your message...',
      variant: 'primary',
      size: 'medium',
      autoStart: false,
    },
    state: {
      isRecording: false,
      transcription: '',
      audioLevel: 0,
      error: null,
    },
    actions: {
      onRecordStart: 'setState:isRecording=true',
      onRecordStop: 'setState:isRecording=false',
      onTranscribe: 'setState:transcription=$result',
      onSubmit: 'emit:messageSubmit',
      onError: 'setState:error=$message',
    },
  },
  
  text_input_basic: {
    component: 'TextInput',
    props: {
      placeholder: 'Enter text...',
      type: 'text',
      variant: 'primary',
      disabled: false,
    },
    state: {
      value: '',
      focused: false,
      error: null,
    },
    actions: {
      onChange: 'setState:value=$event.target.value',
      onFocus: 'setState:focused=true',
      onBlur: 'setState:focused=false',
      onSubmit: 'emit:textSubmit',
    },
  },
  
  submit_button_basic: {
    component: 'Button',
    props: {
      label: 'Submit',
      variant: 'primary',
      size: 'medium',
      disabled: false,
    },
    state: {
      loading: false,
      pressed: false,
    },
    actions: {
      onClick: 'emit:submitClicked',
      onPress: 'setState:pressed=true',
      onRelease: 'setState:pressed=false',
    },
  },
  
  container_basic: {
    component: 'Container',
    props: {
      padding: 'medium',
      background: 'transparent',
      maxWidth: 'none',
    },
    children: [],
  },
  
  vertical_stack: {
    component: 'Stack',
    props: {
      spacing: 'medium',
      alignment: 'stretch',
      direction: 'vertical',
    },
    children: [],
  },
  
  horizontal_inline: {
    component: 'Inline',
    props: {
      spacing: 'medium',
      justification: 'start',
      wrap: false,
    },
    children: [],
  },
};

/**
 * LLM UI Schema Generator
 * 
 * @description
 * Main class that orchestrates natural language to DSL schema generation.
 * Combines intent recognition, template matching, LLM integration, and
 * context awareness to produce high-quality UI schemas.
 * 
 * @example
 * ```typescript
 * const generator = new LLMUISchemaGenerator(schema, llmService);
 * const result = await generator.generateFromPrompt(
 *   "Create a voice input with a submit button",
 *   context
 * );
 * 
 * // Result contains generated components ready for rendering
 * const components = result.components;
 * ```
 */
export class LLMUISchemaGenerator {
  private schema: UniversalSystemSchema;
  private llmService: LLMService | null;
  private generationHistory: Array<{ prompt: string; result: GeneratedSchemaResult }> = [];
  
  /**
   * Create LLM UI Schema Generator
   * 
   * @param schema - Universal System DSL schema
   * @param llmService - Optional LLM service for advanced processing
   */
  constructor(schema: UniversalSystemSchema, llmService?: LLMService) {
    this.schema = schema;
    this.llmService = llmService || null;
    
    console.log(`🤖 LLM UI Schema Generator initialized`);
    console.log(`📊 Available primitives: ${this.getAvailablePrimitives().length}`);
    console.log(`🎯 Intent patterns: ${Object.keys(INTENT_PATTERNS).length}`);
    console.log(`📋 Component templates: ${Object.keys(COMPONENT_TEMPLATES).length}`);
  }
  
  /**
   * Generate UI schema from natural language prompt
   * 
   * @param prompt - Natural language description of desired UI
   * @param context - Optional generation context
   * @returns Promise resolving to generated schema result
   */
  async generateFromPrompt(
    prompt: string,
    context?: UIGenerationContext
  ): Promise<GeneratedSchemaResult> {
    const startTime = Date.now();
    
    console.log(`🎯 Generating UI schema from prompt: "${prompt}"`);
    
    try {
      // Step 1: Recognize intent from prompt
      const intent = await this.recognizeIntent(prompt);
      console.log(`🧠 Recognized intent: ${intent}`);
      
      // Step 2: Extract entities and requirements
      const entities = await this.extractEntities(prompt, intent);
      console.log(`📊 Extracted entities:`, entities);
      
      // Step 3: Generate component schema
      const components = await this.generateComponents(prompt, intent, entities, context);
      console.log(`🎨 Generated ${components.length} component(s)`);
      
      // Step 4: Validate generated schema
      const validationErrors = this.validateGeneratedSchema(components);
      
      // Step 5: Calculate confidence score
      const confidence = this.calculateConfidence(prompt, intent, components, validationErrors);
      
      // Step 6: Generate improvement suggestions
      const suggestions = this.generateSuggestions(prompt, components, context);
      
      const result: GeneratedSchemaResult = {
        components,
        confidence,
        intent,
        entities,
        metadata: {
          processingTime: Date.now() - startTime,
          fallbacksUsed: [],
          validationErrors,
        },
        suggestions,
      };
      
      // Store in generation history for learning
      this.generationHistory.push({ prompt, result });
      
      console.log(`✅ Schema generation complete (${result.metadata.processingTime}ms, confidence: ${Math.round(confidence * 100)}%)`);
      
      return result;
      
    } catch (error) {
      console.error('❌ Schema generation failed:', error);
      
      // Return fallback result
      return this.createFallbackResult(prompt, startTime, error as Error);
    }
  }

  /**
   * Recognize intent from natural language prompt
   *
   * @param prompt - User input prompt
   * @returns Promise resolving to recognized intent
   */
  private async recognizeIntent(prompt: string): Promise<UIIntent> {
    const normalizedPrompt = prompt.toLowerCase().trim();

    // Try LLM-based intent recognition first
    if (this.llmService) {
      try {
        const intents = Object.values(UIIntent).filter(intent => intent !== UIIntent.UNKNOWN);
        const result = await this.llmService.classifyIntent(prompt, intents);

        if (result.confidence > 0.7) {
          return result.intent as UIIntent;
        }
      } catch (error) {
        console.warn('⚠️ LLM intent recognition failed, falling back to pattern matching');
      }
    }

    // Fallback to pattern-based intent recognition
    let bestMatch: { intent: UIIntent; score: number } = { intent: UIIntent.UNKNOWN, score: 0 };

    for (const [intent, patterns] of Object.entries(INTENT_PATTERNS)) {
      if (intent === UIIntent.UNKNOWN) continue;

      let score = 0;

      // Check keyword matches
      for (const keyword of patterns.keywords) {
        if (normalizedPrompt.includes(keyword)) {
          score += 1;
        }
      }

      // Check regex pattern matches
      for (const pattern of patterns.patterns) {
        if (pattern.test(prompt)) {
          score += 2; // Regex matches are weighted higher
        }
      }

      if (score > bestMatch.score) {
        bestMatch = { intent: intent as UIIntent, score };
      }
    }

    return bestMatch.score > 0 ? bestMatch.intent : UIIntent.UNKNOWN;
  }

  /**
   * Extract entities and requirements from prompt
   *
   * @param prompt - User input prompt
   * @param intent - Recognized intent
   * @returns Promise resolving to extracted entities
   */
  private async extractEntities(prompt: string, intent: UIIntent): Promise<GeneratedSchemaResult['entities']> {
    const entities: GeneratedSchemaResult['entities'] = {
      componentTypes: [],
      properties: {},
      relationships: [],
    };

    // Extract component types mentioned in prompt
    const availablePrimitives = this.getAvailablePrimitives();
    for (const primitive of availablePrimitives) {
      const primitiveName = primitive.name.toLowerCase();
      if (prompt.toLowerCase().includes(primitiveName)) {
        entities.componentTypes.push(primitive.name);
      }
    }

    // Extract properties based on common patterns
    const propertyPatterns = {
      placeholder: /placeholder[:\s]+"([^"]+)"/i,
      label: /label[:\s]+"([^"]+)"/i,
      variant: /(?:variant|style|type)[:\s]+(\w+)/i,
      size: /size[:\s]+(\w+)/i,
      color: /color[:\s]+(\w+)/i,
    };

    for (const [property, pattern] of Object.entries(propertyPatterns)) {
      const match = prompt.match(pattern);
      if (match) {
        entities.properties[property] = match[1];
      }
    }

    // Extract relationships (parent-child, layout)
    if (prompt.includes('with') || prompt.includes('containing')) {
      // Simple relationship extraction
      // TODO: Implement more sophisticated relationship parsing
      entities.relationships.push({ parent: 'Container', child: 'detected_component' });
    }

    return entities;
  }

  /**
   * Generate component instances based on intent and entities
   *
   * @param prompt - Original prompt
   * @param intent - Recognized intent
   * @param entities - Extracted entities
   * @param context - Generation context
   * @returns Promise resolving to generated components
   */
  private async generateComponents(
    prompt: string,
    intent: UIIntent,
    entities: GeneratedSchemaResult['entities'],
    context?: UIGenerationContext
  ): Promise<ComponentInstance[]> {
    const components: ComponentInstance[] = [];

    switch (intent) {
      case UIIntent.CREATE_INPUT:
        components.push(...this.generateInputComponents(prompt, entities, context));
        break;

      case UIIntent.CREATE_DISPLAY:
        components.push(...this.generateDisplayComponents(prompt, entities, context));
        break;

      case UIIntent.CREATE_LAYOUT:
        components.push(...this.generateLayoutComponents(prompt, entities, context));
        break;

      case UIIntent.CREATE_ACTION:
        components.push(...this.generateActionComponents(prompt, entities, context));
        break;

      case UIIntent.CREATE_FORM:
        components.push(...this.generateFormComponents(prompt, entities, context));
        break;

      case UIIntent.CREATE_NAVIGATION:
        components.push(...this.generateNavigationComponents(prompt, entities, context));
        break;

      case UIIntent.CREATE_COMPLEX:
        components.push(...this.generateComplexComponents(prompt, entities, context));
        break;

      case UIIntent.MODIFY_EXISTING:
        components.push(...this.generateModificationComponents(prompt, entities, context));
        break;

      default:
        // Fallback: try to generate based on detected component types
        components.push(...this.generateFallbackComponents(prompt, entities, context));
    }

    return components;
  }

  /**
   * Generate input components (VoiceInput, TextInput, etc.)
   */
  private generateInputComponents(
    prompt: string,
    entities: GeneratedSchemaResult['entities'],
    context?: UIGenerationContext
  ): ComponentInstance[] {
    const components: ComponentInstance[] = [];

    // Determine input type based on prompt
    if (prompt.toLowerCase().includes('voice') || prompt.toLowerCase().includes('speak')) {
      const voiceInput = JSON.parse(JSON.stringify(COMPONENT_TEMPLATES.voice_input_basic));

      // Customize based on extracted properties
      if (entities.properties.placeholder) {
        voiceInput.props!.placeholder = entities.properties.placeholder;
      }
      if (entities.properties.variant) {
        voiceInput.props!.variant = entities.properties.variant;
      }
      if (entities.properties.size) {
        voiceInput.props!.size = entities.properties.size;
      }

      components.push(voiceInput);
    } else {
      const textInput = JSON.parse(JSON.stringify(COMPONENT_TEMPLATES.text_input_basic));

      // Customize based on extracted properties
      if (entities.properties.placeholder) {
        textInput.props!.placeholder = entities.properties.placeholder;
      }
      if (entities.properties.variant) {
        textInput.props!.variant = entities.properties.variant;
      }

      components.push(textInput);
    }

    // Add submit button if mentioned
    if (prompt.toLowerCase().includes('submit') || prompt.toLowerCase().includes('send')) {
      const submitButton = JSON.parse(JSON.stringify(COMPONENT_TEMPLATES.submit_button_basic));

      if (entities.properties.label) {
        submitButton.props!.label = entities.properties.label;
      } else if (prompt.toLowerCase().includes('send')) {
        submitButton.props!.label = 'Send';
      }

      components.push(submitButton);
    }

    return components;
  }

  /**
   * Generate display components (Text, Image, etc.)
   */
  private generateDisplayComponents(
    prompt: string,
    entities: GeneratedSchemaResult['entities'],
    context?: UIGenerationContext
  ): ComponentInstance[] {
    const components: ComponentInstance[] = [];

    // Generate text component
    const textComponent: ComponentInstance = {
      component: 'Text',
      props: {
        content: entities.properties.label || 'Sample text',
        variant: entities.properties.variant || 'body',
        size: entities.properties.size || 'medium',
        color: entities.properties.color || 'primary',
      },
    };

    components.push(textComponent);
    return components;
  }

  /**
   * Generate layout components (Container, Stack, Inline)
   */
  private generateLayoutComponents(
    prompt: string,
    entities: GeneratedSchemaResult['entities'],
    context?: UIGenerationContext
  ): ComponentInstance[] {
    const components: ComponentInstance[] = [];

    if (prompt.toLowerCase().includes('vertical') || prompt.toLowerCase().includes('stack')) {
      components.push(JSON.parse(JSON.stringify(COMPONENT_TEMPLATES.vertical_stack)));
    } else if (prompt.toLowerCase().includes('horizontal') || prompt.toLowerCase().includes('inline')) {
      components.push(JSON.parse(JSON.stringify(COMPONENT_TEMPLATES.horizontal_inline)));
    } else {
      components.push(JSON.parse(JSON.stringify(COMPONENT_TEMPLATES.container_basic)));
    }

    return components;
  }

  /**
   * Generate action components (Button, etc.)
   */
  private generateActionComponents(
    prompt: string,
    entities: GeneratedSchemaResult['entities'],
    context?: UIGenerationContext
  ): ComponentInstance[] {
    const components: ComponentInstance[] = [];

    const button = JSON.parse(JSON.stringify(COMPONENT_TEMPLATES.submit_button_basic));

    // Customize button based on prompt
    if (entities.properties.label) {
      button.props!.label = entities.properties.label;
    } else if (prompt.toLowerCase().includes('send')) {
      button.props!.label = 'Send';
    } else if (prompt.toLowerCase().includes('save')) {
      button.props!.label = 'Save';
    } else if (prompt.toLowerCase().includes('cancel')) {
      button.props!.label = 'Cancel';
      button.props!.variant = 'secondary';
    }

    components.push(button);
    return components;
  }

  /**
   * Generate form components
   */
  private generateFormComponents(
    prompt: string,
    entities: GeneratedSchemaResult['entities'],
    context?: UIGenerationContext
  ): ComponentInstance[] {
    const components: ComponentInstance[] = [];

    // Create form container
    const formContainer = JSON.parse(JSON.stringify(COMPONENT_TEMPLATES.vertical_stack));
    formContainer.props!.spacing = 'large';

    // Add form fields based on prompt
    if (prompt.toLowerCase().includes('name')) {
      const nameInput = JSON.parse(JSON.stringify(COMPONENT_TEMPLATES.text_input_basic));
      nameInput.props!.placeholder = 'Enter your name...';
      components.push(nameInput);
    }

    if (prompt.toLowerCase().includes('email')) {
      const emailInput = JSON.parse(JSON.stringify(COMPONENT_TEMPLATES.text_input_basic));
      emailInput.props!.placeholder = 'Enter your email...';
      emailInput.props!.type = 'email';
      components.push(emailInput);
    }

    // Add submit button
    const submitButton = JSON.parse(JSON.stringify(COMPONENT_TEMPLATES.submit_button_basic));
    components.push(submitButton);

    // Wrap in container if multiple components
    if (components.length > 1) {
      formContainer.children = components;
      return [formContainer];
    }

    return components;
  }

  /**
   * Generate navigation components
   */
  private generateNavigationComponents(
    prompt: string,
    entities: GeneratedSchemaResult['entities'],
    context?: UIGenerationContext
  ): ComponentInstance[] {
    const components: ComponentInstance[] = [];

    // Create navigation container
    const navContainer = JSON.parse(JSON.stringify(COMPONENT_TEMPLATES.vertical_stack));
    navContainer.props!.spacing = 'small';

    // Add navigation items
    const navItems = ['Home', 'About', 'Contact'];
    for (const item of navItems) {
      const navButton = JSON.parse(JSON.stringify(COMPONENT_TEMPLATES.submit_button_basic));
      navButton.props!.label = item;
      navButton.props!.variant = 'ghost';
      navButton.actions!.onClick = `navigate:route=/${item.toLowerCase()}`;
      navContainer.children!.push(navButton);
    }

    components.push(navContainer);
    return components;
  }

  /**
   * Generate complex components (dashboard, etc.)
   */
  private generateComplexComponents(
    prompt: string,
    entities: GeneratedSchemaResult['entities'],
    context?: UIGenerationContext
  ): ComponentInstance[] {
    const components: ComponentInstance[] = [];

    // Create main container
    const mainContainer = JSON.parse(JSON.stringify(COMPONENT_TEMPLATES.container_basic));
    mainContainer.props!.padding = 'large';

    // Add header
    const header: ComponentInstance = {
      component: 'Text',
      props: {
        content: 'Dashboard',
        variant: 'heading',
        size: 'large',
        color: 'primary',
      },
    };

    // Add content area
    const contentStack = JSON.parse(JSON.stringify(COMPONENT_TEMPLATES.vertical_stack));
    contentStack.children = [header];

    // Add voice input if mentioned
    if (prompt.toLowerCase().includes('voice') || prompt.toLowerCase().includes('chat')) {
      const voiceInput = JSON.parse(JSON.stringify(COMPONENT_TEMPLATES.voice_input_basic));
      contentStack.children!.push(voiceInput);
    }

    mainContainer.children = [contentStack];
    components.push(mainContainer);

    return components;
  }

  /**
   * Generate modification components
   */
  private generateModificationComponents(
    prompt: string,
    entities: GeneratedSchemaResult['entities'],
    context?: UIGenerationContext
  ): ComponentInstance[] {
    // For modifications, we would typically update existing components
    // For now, return empty array as this requires more complex logic
    console.log('🔧 Modification intent detected - would update existing components');
    return [];
  }

  /**
   * Generate fallback components when intent is unknown
   */
  private generateFallbackComponents(
    prompt: string,
    entities: GeneratedSchemaResult['entities'],
    context?: UIGenerationContext
  ): ComponentInstance[] {
    const components: ComponentInstance[] = [];

    // If specific component types were detected, create those
    if (entities.componentTypes.length > 0) {
      for (const componentType of entities.componentTypes) {
        const template = Object.values(COMPONENT_TEMPLATES).find(
          t => t.component === componentType
        );
        if (template) {
          components.push(JSON.parse(JSON.stringify(template)));
        }
      }
    } else {
      // Default fallback: create a simple container with text
      const container = JSON.parse(JSON.stringify(COMPONENT_TEMPLATES.container_basic));
      const text: ComponentInstance = {
        component: 'Text',
        props: {
          content: 'Generated component from: ' + prompt,
          variant: 'body',
          size: 'medium',
          color: 'secondary',
        },
      };
      container.children = [text];
      components.push(container);
    }

    return components;
  }

  /**
   * Validate generated schema components
   *
   * @param components - Generated components to validate
   * @returns Array of validation errors
   */
  private validateGeneratedSchema(components: ComponentInstance[]): string[] {
    const errors: string[] = [];

    for (const component of components) {
      // Check if component type exists in schema
      const definition = this.getComponentDefinition(component.component);
      if (!definition) {
        errors.push(`Unknown component type: ${component.component}`);
        continue;
      }

      // Validate props against definition
      if (component.props) {
        for (const propName in component.props) {
          if (!definition.props.includes(propName)) {
            errors.push(`Invalid prop '${propName}' for component '${component.component}'`);
          }
        }
      }

      // Validate state against definition
      if (component.state && definition.state) {
        for (const stateKey in component.state) {
          if (!definition.state.includes(stateKey)) {
            errors.push(`Invalid state '${stateKey}' for component '${component.component}'`);
          }
        }
      }

      // Validate actions against definition
      if (component.actions && definition.actions) {
        for (const actionName in component.actions) {
          if (!definition.actions.includes(actionName)) {
            errors.push(`Invalid action '${actionName}' for component '${component.component}'`);
          }
        }
      }
    }

    return errors;
  }

  /**
   * Calculate confidence score for generated schema
   *
   * @param prompt - Original prompt
   * @param intent - Recognized intent
   * @param components - Generated components
   * @param validationErrors - Validation errors
   * @returns Confidence score (0-1)
   */
  private calculateConfidence(
    prompt: string,
    intent: UIIntent,
    components: ComponentInstance[],
    validationErrors: string[]
  ): number {
    let confidence = 0.5; // Base confidence

    // Boost confidence for recognized intent
    if (intent !== UIIntent.UNKNOWN) {
      confidence += 0.2;
    }

    // Boost confidence for generated components
    if (components.length > 0) {
      confidence += 0.2;
    }

    // Reduce confidence for validation errors
    confidence -= validationErrors.length * 0.1;

    // Boost confidence for specific component matches
    const promptLower = prompt.toLowerCase();
    for (const component of components) {
      if (promptLower.includes(component.component.toLowerCase())) {
        confidence += 0.1;
      }
    }

    return Math.max(0, Math.min(1, confidence));
  }

  /**
   * Generate improvement suggestions
   *
   * @param prompt - Original prompt
   * @param components - Generated components
   * @param context - Generation context
   * @returns Array of suggestions
   */
  private generateSuggestions(
    prompt: string,
    components: ComponentInstance[],
    context?: UIGenerationContext
  ): string[] {
    const suggestions: string[] = [];

    if (components.length === 0) {
      suggestions.push('Try being more specific about the UI components you want');
    }

    if (components.length === 1) {
      suggestions.push('Consider adding layout components to organize your UI');
    }

    if (!prompt.toLowerCase().includes('voice') && !prompt.toLowerCase().includes('text')) {
      suggestions.push('Specify input type: voice input or text input');
    }

    return suggestions;
  }

  /**
   * Create fallback result for failed generation
   *
   * @param prompt - Original prompt
   * @param startTime - Generation start time
   * @param error - Error that occurred
   * @returns Fallback result
   */
  private createFallbackResult(prompt: string, startTime: number, error: Error): GeneratedSchemaResult {
    return {
      components: [{
        component: 'Text',
        props: {
          content: `Failed to generate UI from: "${prompt}"`,
          variant: 'body',
          size: 'medium',
          color: 'error',
        },
      }],
      confidence: 0.1,
      intent: UIIntent.UNKNOWN,
      entities: {
        componentTypes: [],
        properties: {},
        relationships: [],
      },
      metadata: {
        processingTime: Date.now() - startTime,
        fallbacksUsed: ['error_fallback'],
        validationErrors: [error.message],
      },
      suggestions: [
        'Try rephrasing your request',
        'Be more specific about the UI components you want',
        'Check if all required services are available',
      ],
    };
  }

  /**
   * Get component definition from schema
   *
   * @param componentName - Name of component
   * @returns Component definition or null
   */
  private getComponentDefinition(componentName: string): ComponentDefinition | null {
    const allPrimitives = [
      ...this.schema.primitives.layout.types,
      ...this.schema.primitives.input.types,
      ...this.schema.primitives.display.types,
      ...this.schema.primitives.action.types,
    ];

    return allPrimitives.find(def => def.name === componentName) || null;
  }

  /**
   * Get all available primitive components
   *
   * @returns Array of all component definitions
   */
  private getAvailablePrimitives(): ComponentDefinition[] {
    return [
      ...this.schema.primitives.layout.types,
      ...this.schema.primitives.input.types,
      ...this.schema.primitives.display.types,
      ...this.schema.primitives.action.types,
    ];
  }

  /**
   * Get generation history for learning and improvement
   *
   * @returns Array of generation history entries
   */
  getGenerationHistory(): Array<{ prompt: string; result: GeneratedSchemaResult }> {
    return [...this.generationHistory];
  }

  /**
   * Clear generation history
   */
  clearGenerationHistory(): void {
    this.generationHistory = [];
    console.log('🗑️ Generation history cleared');
  }

  /**
   * Get generator statistics
   *
   * @returns Statistics object
   */
  getStats(): {
    schemaVersion: string;
    availablePrimitives: number;
    intentPatterns: number;
    componentTemplates: number;
    generationHistory: number;
    hasLLMService: boolean;
  } {
    return {
      schemaVersion: this.schema.version,
      availablePrimitives: this.getAvailablePrimitives().length,
      intentPatterns: Object.keys(INTENT_PATTERNS).length,
      componentTemplates: Object.keys(COMPONENT_TEMPLATES).length,
      generationHistory: this.generationHistory.length,
      hasLLMService: this.llmService !== null,
    };
  }

  /**
   * Set LLM service for advanced processing
   *
   * @param llmService - LLM service implementation
   */
  setLLMService(llmService: LLMService): void {
    this.llmService = llmService;
    console.log('🤖 LLM service configured for advanced processing');
  }

  /**
   * Generate multiple variations of a prompt
   *
   * @param prompt - Original prompt
   * @param count - Number of variations to generate
   * @param context - Generation context
   * @returns Promise resolving to array of generated results
   */
  async generateVariations(
    prompt: string,
    count: number = 3,
    context?: UIGenerationContext
  ): Promise<GeneratedSchemaResult[]> {
    const variations: GeneratedSchemaResult[] = [];

    console.log(`🎨 Generating ${count} variations for prompt: "${prompt}"`);

    for (let i = 0; i < count; i++) {
      // Add slight variations to the prompt for different results
      const variationPrompt = i === 0 ? prompt : `${prompt} (variation ${i + 1})`;
      const result = await this.generateFromPrompt(variationPrompt, context);
      variations.push(result);
    }

    console.log(`✅ Generated ${variations.length} variations`);
    return variations;
  }

  /**
   * Learn from user feedback to improve future generations
   *
   * @param prompt - Original prompt
   * @param result - Generated result
   * @param feedback - User feedback (rating and improvements)
   */
  learnFromFeedback(
    prompt: string,
    result: GeneratedSchemaResult,
    feedback: { rating: number; improvements: string[] }
  ): void {
    console.log(`📚 Learning from feedback for prompt: "${prompt}"`);
    console.log(`⭐ Rating: ${feedback.rating}/5`);
    console.log(`💡 Improvements: ${feedback.improvements.join(', ')}`);

    // TODO: Implement machine learning integration
    // This would update generation patterns based on user feedback

    // For now, just log the feedback for manual analysis
    const learningEntry = {
      prompt,
      result,
      feedback,
      timestamp: Date.now(),
    };

    console.log('📊 Feedback logged for future improvements');
  }
}
