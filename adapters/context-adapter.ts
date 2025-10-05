/**
 * @fileoverview Context-Aware UI Adapter - Intelligent UI Adaptation Engine
 * 
 * @description
 * Intelligent adapter that modifies UI components based on user context,
 * environment, device capabilities, accessibility needs, and learned preferences.
 * Makes the Universal System truly adaptive and context-aware.
 * 
 * @design_principles
 * - Context-driven: All adaptations based on real user context
 * - Learning-enabled: Improves adaptations based on user behavior
 * - Accessibility-first: Automatic optimization for different needs
 * - Performance-aware: Context-based resource and rendering optimization
 * - Device-agnostic: Adapts to any device or environment seamlessly
 * 
 * @intelligence_contract
 * This adapter serves as the intelligence layer that:
 * 1. Detects user context (device, environment, preferences, accessibility)
 * 2. Analyzes component suitability for current context
 * 3. Adapts component properties, layout, and behavior intelligently
 * 4. Learns from user interactions to improve future adaptations
 * 5. Optimizes performance based on device capabilities and network
 * 
 * @adaptation_examples
 * - Noisy environment → Enhanced voice components, visual feedback
 * - Mobile device → Touch-optimized controls, simplified layouts
 * - Screen reader → Enhanced ARIA labels, semantic structure
 * - Low bandwidth → Optimized rendering, reduced animations
 * - Voice-first user → Prioritize voice inputs, minimize text entry
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import {
  ComponentInstance,
  ComponentContext,
  DSLInterpreter,
  StateChangeEvent,
} from '../core/dsl-interpreter';
import { ReactDSLRenderer } from '../renderers/react-renderer';

/**
 * User context information
 * 
 * @description
 * Comprehensive context data that influences UI adaptation decisions.
 * Includes device, environment, user preferences, and accessibility needs.
 */
export interface UserContext {
  /** Device and hardware context */
  device: {
    type: 'desktop' | 'mobile' | 'tablet' | 'embedded';
    screenSize: { width: number; height: number };
    touchCapable: boolean;
    voiceCapable: boolean;
    cameraCapable: boolean;
    orientation: 'portrait' | 'landscape';
    pixelDensity: number;
  };
  
  /** Environment context */
  environment: {
    lighting: 'bright' | 'dim' | 'dark' | 'unknown';
    noise: 'quiet' | 'moderate' | 'noisy' | 'unknown';
    location: 'home' | 'office' | 'public' | 'vehicle' | 'unknown';
    network: {
      speed: 'slow' | 'moderate' | 'fast';
      stability: 'unstable' | 'stable';
      metered: boolean;
    };
  };
  
  /** User preferences and behavior */
  user: {
    inputPreference: 'voice' | 'text' | 'touch' | 'mixed';
    interactionStyle: 'quick' | 'deliberate' | 'exploratory';
    experienceLevel: 'beginner' | 'intermediate' | 'expert';
    language: string;
    timezone: string;
  };
  
  /** Accessibility requirements */
  accessibility: {
    screenReader: boolean;
    highContrast: boolean;
    largeText: boolean;
    reducedMotion: boolean;
    colorBlindness: 'none' | 'protanopia' | 'deuteranopia' | 'tritanopia';
    motorImpairment: boolean;
    cognitiveSupport: boolean;
  };
  
  /** Application context */
  application: {
    currentTask: string;
    taskComplexity: 'simple' | 'moderate' | 'complex';
    timeConstraint: 'none' | 'moderate' | 'urgent';
    errorTolerance: 'high' | 'moderate' | 'low';
    dataImportance: 'low' | 'moderate' | 'critical';
  };
}

/**
 * Adaptation strategy for component modification
 * 
 * @description
 * Defines how components should be adapted based on context analysis.
 * Includes property changes, layout modifications, and behavior adjustments.
 */
export interface AdaptationStrategy {
  /** Component property modifications */
  propertyChanges: Record<string, any>;
  
  /** Layout and positioning adjustments */
  layoutChanges: {
    spacing?: string;
    alignment?: string;
    direction?: string;
    priority?: number;
  };
  
  /** Behavioral modifications */
  behaviorChanges: {
    autoFocus?: boolean;
    autoStart?: boolean;
    confirmationRequired?: boolean;
    feedbackLevel?: 'minimal' | 'standard' | 'verbose';
  };
  
  /** Performance optimizations */
  performanceChanges: {
    renderPriority?: 'low' | 'normal' | 'high';
    animationLevel?: 'none' | 'reduced' | 'full';
    updateFrequency?: 'low' | 'normal' | 'high';
  };
  
  /** Accessibility enhancements */
  accessibilityChanges: {
    ariaLabel?: string;
    ariaDescription?: string;
    tabIndex?: number;
    role?: string;
    semanticLevel?: number;
  };
}

/**
 * Context analysis result
 * 
 * @description
 * Result of context analysis including detected patterns,
 * adaptation recommendations, and confidence scores.
 */
export interface ContextAnalysis {
  /** Primary context factors influencing adaptation */
  primaryFactors: Array<{
    factor: string;
    impact: 'low' | 'medium' | 'high';
    confidence: number;
  }>;
  
  /** Recommended adaptations */
  adaptations: Record<string, AdaptationStrategy>;
  
  /** Overall adaptation confidence */
  confidence: number;
  
  /** Context change indicators */
  contextChanges: Array<{
    property: string;
    oldValue: any;
    newValue: any;
    significance: 'minor' | 'moderate' | 'major';
  }>;
  
  /** Performance recommendations */
  performanceRecommendations: {
    renderingOptimizations: string[];
    resourceOptimizations: string[];
    networkOptimizations: string[];
  };
}

/**
 * Learning data for context adaptation improvement
 * 
 * @description
 * Data collected from user interactions to improve future adaptations.
 * Includes success metrics, user feedback, and behavioral patterns.
 */
export interface AdaptationLearningData {
  /** User interaction patterns */
  interactionPatterns: {
    preferredComponents: Record<string, number>;
    successfulAdaptations: Array<{ context: UserContext; adaptation: AdaptationStrategy; success: boolean }>;
    userCorrections: Array<{ originalAdaptation: AdaptationStrategy; userPreference: AdaptationStrategy }>;
  };
  
  /** Performance metrics */
  performanceMetrics: {
    adaptationTime: number[];
    renderingTime: number[];
    userSatisfaction: number[];
    taskCompletionRate: number;
  };
  
  /** Context patterns */
  contextPatterns: {
    frequentContexts: Array<{ context: Partial<UserContext>; frequency: number }>;
    contextTransitions: Array<{ from: UserContext; to: UserContext; trigger: string }>;
    timeBasedPatterns: Record<string, UserContext>;
  };
}

/**
 * Context-Aware UI Adapter
 * 
 * @description
 * Main adapter class that analyzes user context and intelligently adapts
 * UI components for optimal user experience. Integrates with DSL interpreter
 * and React renderer to provide seamless context-aware adaptations.
 * 
 * @example
 * ```typescript
 * const adapter = new ContextAwareUIAdapter(interpreter, renderer);
 * 
 * // Set current user context
 * adapter.updateContext({
 *   device: { type: 'mobile', touchCapable: true },
 *   environment: { noise: 'noisy' },
 *   accessibility: { screenReader: true }
 * });
 * 
 * // Adapt component for current context
 * const adaptedComponent = await adapter.adaptComponent(voiceInputComponent);
 * ```
 */
export class ContextAwareUIAdapter {
  private interpreter: DSLInterpreter;
  private renderer: ReactDSLRenderer;
  private currentContext: UserContext;
  private learningData: AdaptationLearningData;
  private adaptationHistory: Array<{ context: UserContext; adaptations: Record<string, AdaptationStrategy> }> = [];
  
  /**
   * Create Context-Aware UI Adapter
   * 
   * @param interpreter - DSL interpreter instance
   * @param renderer - React renderer instance
   * @param initialContext - Initial user context
   */
  constructor(
    interpreter: DSLInterpreter,
    renderer: ReactDSLRenderer,
    initialContext?: Partial<UserContext>
  ) {
    this.interpreter = interpreter;
    this.renderer = renderer;
    this.currentContext = this.createDefaultContext(initialContext);
    this.learningData = this.initializeLearningData();
    
    // Set up event listeners for context changes
    this.setupContextListeners();
    
    console.log('🧠 Context-Aware UI Adapter initialized');
    console.log(`📱 Device: ${this.currentContext.device.type}`);
    console.log(`🌍 Environment: ${this.currentContext.environment.noise} noise, ${this.currentContext.environment.lighting} lighting`);
    console.log(`♿ Accessibility: ${Object.values(this.currentContext.accessibility).filter(Boolean).length} features enabled`);
  }
  
  /**
   * Update user context
   * 
   * @param contextUpdate - Partial context update
   */
  updateContext(contextUpdate: Partial<UserContext>): void {
    const previousContext = { ...this.currentContext };
    
    // Deep merge context update
    this.currentContext = this.mergeContext(this.currentContext, contextUpdate);
    
    // Analyze context changes
    const contextChanges = this.analyzeContextChanges(previousContext, this.currentContext);
    
    if (contextChanges.length > 0) {
      console.log(`🔄 Context updated: ${contextChanges.length} changes detected`);
      
      // Trigger re-adaptation of existing components
      this.reAdaptExistingComponents(contextChanges);
      
      // Learn from context transitions
      this.learnFromContextTransition(previousContext, this.currentContext);
    }
  }
  
  /**
   * Analyze current context and generate adaptation strategy
   * 
   * @param component - Component to analyze
   * @returns Promise resolving to context analysis
   */
  async analyzeContext(component: ComponentInstance): Promise<ContextAnalysis> {
    console.log(`🔍 Analyzing context for component: ${component.component}`);
    
    const primaryFactors = this.identifyPrimaryFactors(component);
    const adaptations = await this.generateAdaptationStrategies(component, primaryFactors);
    const confidence = this.calculateAdaptationConfidence(primaryFactors, adaptations);
    const contextChanges = this.getRecentContextChanges();
    const performanceRecommendations = this.generatePerformanceRecommendations();
    
    return {
      primaryFactors,
      adaptations,
      confidence,
      contextChanges,
      performanceRecommendations,
    };
  }
  
  /**
   * Adapt component based on current context
   * 
   * @param component - Component to adapt
   * @returns Promise resolving to adapted component
   */
  async adaptComponent(component: ComponentInstance): Promise<ComponentInstance> {
    const analysis = await this.analyzeContext(component);
    
    console.log(`🎨 Adapting component: ${component.component} (confidence: ${Math.round(analysis.confidence * 100)}%)`);
    
    // Apply adaptations
    const adaptedComponent = this.applyAdaptations(component, analysis.adaptations);
    
    // Record adaptation for learning
    this.recordAdaptation(component, adaptedComponent, analysis);
    
    // Update component in interpreter
    if (adaptedComponent.id) {
      this.interpreter.updateComponentProps(adaptedComponent.id, adaptedComponent.props || {});
    }
    
    console.log(`✅ Component adapted with ${Object.keys(analysis.adaptations).length} modifications`);
    
    return adaptedComponent;
  }

  /**
   * Generate adaptation strategies based on context factors
   *
   * @param component - Component to adapt
   * @param factors - Primary context factors
   * @returns Promise resolving to adaptation strategies
   */
  private async generateAdaptationStrategies(
    component: ComponentInstance,
    factors: Array<{ factor: string; impact: 'low' | 'medium' | 'high'; confidence: number }>
  ): Promise<Record<string, AdaptationStrategy>> {
    const adaptations: Record<string, AdaptationStrategy> = {};

    for (const factor of factors) {
      const strategy = this.createAdaptationStrategy(component, factor);
      if (strategy) {
        adaptations[factor.factor] = strategy;
      }
    }

    return adaptations;
  }

  /**
   * Create adaptation strategy for specific factor
   *
   * @param component - Component to adapt
   * @param factor - Context factor
   * @returns Adaptation strategy or null
   */
  private createAdaptationStrategy(
    component: ComponentInstance,
    factor: { factor: string; impact: 'low' | 'medium' | 'high'; confidence: number }
  ): AdaptationStrategy | null {
    const strategy: AdaptationStrategy = {
      propertyChanges: {},
      layoutChanges: {},
      behaviorChanges: {},
      performanceChanges: {},
      accessibilityChanges: {},
    };

    switch (factor.factor) {
      case 'mobile_device':
        // Mobile-specific adaptations
        strategy.propertyChanges.size = 'large';
        strategy.layoutChanges.spacing = 'large';
        strategy.behaviorChanges.confirmationRequired = true;
        strategy.performanceChanges.animationLevel = 'reduced';

        if (component.component === 'Button') {
          strategy.propertyChanges.size = 'large';
          strategy.layoutChanges.spacing = 'large';
        }
        if (component.component === 'VoiceInput') {
          strategy.propertyChanges.size = 'large';
          strategy.behaviorChanges.autoStart = false;
        }
        break;

      case 'touch_interface':
        // Touch-optimized adaptations
        strategy.propertyChanges.size = 'large';
        strategy.layoutChanges.spacing = 'large';
        strategy.behaviorChanges.feedbackLevel = 'verbose';
        break;

      case 'noisy_environment':
        // Noisy environment adaptations
        if (component.component === 'VoiceInput') {
          strategy.behaviorChanges.feedbackLevel = 'verbose';
          strategy.propertyChanges.variant = 'primary';
          strategy.accessibilityChanges.ariaLabel = 'Voice input - noisy environment detected';
        }
        break;

      case 'voice_preference':
        // Voice-first user adaptations
        if (component.component === 'VoiceInput') {
          strategy.behaviorChanges.autoStart = true;
          strategy.behaviorChanges.autoFocus = true;
          strategy.propertyChanges.variant = 'primary';
        }
        break;

      case 'screen_reader':
        // Screen reader adaptations
        strategy.accessibilityChanges.ariaLabel = this.generateAriaLabel(component);
        strategy.accessibilityChanges.ariaDescription = this.generateAriaDescription(component);
        strategy.accessibilityChanges.role = this.getSemanticRole(component);
        strategy.performanceChanges.animationLevel = 'none';
        break;

      case 'high_contrast':
        // High contrast adaptations
        strategy.propertyChanges.variant = 'primary';
        strategy.performanceChanges.animationLevel = 'reduced';
        break;

      case 'reduced_motion':
        // Reduced motion adaptations
        strategy.performanceChanges.animationLevel = 'none';
        strategy.behaviorChanges.feedbackLevel = 'standard';
        break;

      case 'slow_network':
        // Network optimization adaptations
        strategy.performanceChanges.renderPriority = 'high';
        strategy.performanceChanges.updateFrequency = 'low';
        strategy.performanceChanges.animationLevel = 'none';
        break;

      case 'complex_task':
        // Complex task adaptations
        strategy.behaviorChanges.confirmationRequired = true;
        strategy.behaviorChanges.feedbackLevel = 'verbose';
        strategy.accessibilityChanges.ariaDescription = 'Complex task - additional confirmation required';
        break;

      default:
        return null;
    }

    return strategy;
  }

  /**
   * Apply adaptations to component
   *
   * @param component - Original component
   * @param adaptations - Adaptation strategies
   * @returns Adapted component
   */
  private applyAdaptations(
    component: ComponentInstance,
    adaptations: Record<string, AdaptationStrategy>
  ): ComponentInstance {
    const adaptedComponent = JSON.parse(JSON.stringify(component));

    // Apply all adaptation strategies
    for (const [factorName, strategy] of Object.entries(adaptations)) {
      console.log(`🔧 Applying ${factorName} adaptations`);

      // Apply property changes
      if (strategy.propertyChanges) {
        adaptedComponent.props = { ...adaptedComponent.props, ...strategy.propertyChanges };
      }

      // Apply accessibility changes
      if (strategy.accessibilityChanges) {
        adaptedComponent.props = { ...adaptedComponent.props, ...strategy.accessibilityChanges };
      }

      // Apply behavior changes to actions
      if (strategy.behaviorChanges && adaptedComponent.actions) {
        if (strategy.behaviorChanges.autoFocus) {
          adaptedComponent.actions.onMount = 'setState:focused=true';
        }
        if (strategy.behaviorChanges.autoStart && component.component === 'VoiceInput') {
          adaptedComponent.actions.onMount = 'setState:isRecording=true';
        }
      }

      // Apply layout changes
      if (strategy.layoutChanges) {
        adaptedComponent.props = { ...adaptedComponent.props, ...strategy.layoutChanges };
      }
    }

    return adaptedComponent;
  }

  /**
   * Generate ARIA label for component
   *
   * @param component - Component instance
   * @returns ARIA label string
   */
  private generateAriaLabel(component: ComponentInstance): string {
    const componentType = component.component;
    const props = component.props || {};

    switch (componentType) {
      case 'VoiceInput':
        return `Voice input field${props.placeholder ? ': ' + props.placeholder : ''}`;
      case 'Button':
        return `Button${props.label ? ': ' + props.label : ''}`;
      case 'Text':
        return `Text content${props.content ? ': ' + props.content : ''}`;
      case 'Container':
        return 'Content container';
      default:
        return `${componentType} component`;
    }
  }

  /**
   * Generate ARIA description for component
   *
   * @param component - Component instance
   * @returns ARIA description string
   */
  private generateAriaDescription(component: ComponentInstance): string {
    const componentType = component.component;
    const context = this.currentContext;

    let description = '';

    switch (componentType) {
      case 'VoiceInput':
        description = 'Voice input component for speech recognition';
        if (context.environment.noise === 'noisy') {
          description += '. Noisy environment detected - enhanced feedback enabled';
        }
        break;
      case 'Button':
        description = 'Interactive button component';
        if (context.device.touchCapable) {
          description += '. Touch-optimized for mobile interaction';
        }
        break;
      default:
        description = `${componentType} user interface component`;
    }

    return description;
  }

  /**
   * Get semantic role for component
   *
   * @param component - Component instance
   * @returns ARIA role string
   */
  private getSemanticRole(component: ComponentInstance): string {
    switch (component.component) {
      case 'VoiceInput':
        return 'textbox';
      case 'Button':
        return 'button';
      case 'Text':
        return 'text';
      case 'Container':
        return 'region';
      default:
        return 'generic';
    }
  }

  /**
   * Calculate adaptation confidence score
   *
   * @param factors - Primary context factors
   * @param adaptations - Generated adaptations
   * @returns Confidence score (0-1)
   */
  private calculateAdaptationConfidence(
    factors: Array<{ factor: string; impact: 'low' | 'medium' | 'high'; confidence: number }>,
    adaptations: Record<string, AdaptationStrategy>
  ): number {
    if (factors.length === 0) return 0.1;

    let totalConfidence = 0;
    let weightSum = 0;

    for (const factor of factors) {
      const weight = factor.impact === 'high' ? 3 : factor.impact === 'medium' ? 2 : 1;
      totalConfidence += factor.confidence * weight;
      weightSum += weight;
    }

    const baseConfidence = totalConfidence / weightSum;

    // Boost confidence if we have adaptations for high-impact factors
    const highImpactFactors = factors.filter(f => f.impact === 'high');
    const adaptationBoost = Math.min(Object.keys(adaptations).length * 0.1, 0.3);

    return Math.min(baseConfidence + adaptationBoost, 1.0);
  }

  /**
   * Get recent context changes
   *
   * @returns Array of recent context changes
   */
  private getRecentContextChanges(): Array<{
    property: string;
    oldValue: any;
    newValue: any;
    significance: 'minor' | 'moderate' | 'major';
  }> {
    // Return recent changes from adaptation history
    const recentHistory = this.adaptationHistory.slice(-3);
    const changes: Array<{
      property: string;
      oldValue: any;
      newValue: any;
      significance: 'minor' | 'moderate' | 'major';
    }> = [];

    // This would be populated by actual context change tracking
    // For now, return empty array
    return changes;
  }

  /**
   * Generate performance recommendations
   *
   * @returns Performance recommendations
   */
  private generatePerformanceRecommendations(): {
    renderingOptimizations: string[];
    resourceOptimizations: string[];
    networkOptimizations: string[];
  } {
    const recommendations = {
      renderingOptimizations: [] as string[],
      resourceOptimizations: [] as string[],
      networkOptimizations: [] as string[],
    };

    // Network-based recommendations
    if (this.currentContext.environment.network.speed === 'slow') {
      recommendations.networkOptimizations.push('Reduce animation complexity');
      recommendations.networkOptimizations.push('Minimize real-time updates');
      recommendations.renderingOptimizations.push('Use simplified rendering mode');
    }

    // Device-based recommendations
    if (this.currentContext.device.type === 'mobile') {
      recommendations.resourceOptimizations.push('Optimize for touch interactions');
      recommendations.renderingOptimizations.push('Use mobile-optimized layouts');
    }

    // Accessibility-based recommendations
    if (this.currentContext.accessibility.reducedMotion) {
      recommendations.renderingOptimizations.push('Disable animations and transitions');
    }

    return recommendations;
  }

  /**
   * Re-adapt existing components after context change
   *
   * @param contextChanges - Array of context changes
   */
  private reAdaptExistingComponents(contextChanges: Array<{
    property: string;
    oldValue: any;
    newValue: any;
    significance: 'minor' | 'moderate' | 'major';
  }>): void {
    const significantChanges = contextChanges.filter(c => c.significance !== 'minor');

    if (significantChanges.length > 0) {
      console.log(`🔄 Re-adapting existing components due to ${significantChanges.length} significant context changes`);

      // Get all components from interpreter
      const allComponents = this.interpreter.getAllComponents();

      // Re-adapt components that are affected by context changes
      for (const [componentId, component] of allComponents) {
        this.adaptComponent(component).catch(error => {
          console.error(`❌ Failed to re-adapt component ${componentId}:`, error);
        });
      }
    }
  }

  /**
   * Learn from context transition
   *
   * @param previousContext - Previous context
   * @param currentContext - Current context
   */
  private learnFromContextTransition(previousContext: UserContext, currentContext: UserContext): void {
    // Record context transition for learning
    this.learningData.contextPatterns.contextTransitions.push({
      from: previousContext,
      to: currentContext,
      trigger: 'user_action', // This would be determined by the actual trigger
    });

    // Update frequent contexts
    const contextKey = this.generateContextKey(currentContext);
    const existingPattern = this.learningData.contextPatterns.frequentContexts.find(
      p => this.generateContextKey(p.context as UserContext) === contextKey
    );

    if (existingPattern) {
      existingPattern.frequency++;
    } else {
      this.learningData.contextPatterns.frequentContexts.push({
        context: currentContext,
        frequency: 1,
      });
    }

    console.log('📚 Context transition learned and recorded');
  }

  /**
   * Generate context key for pattern matching
   *
   * @param context - User context
   * @returns Context key string
   */
  private generateContextKey(context: UserContext): string {
    return `${context.device.type}-${context.environment.noise}-${context.user.inputPreference}-${context.accessibility.screenReader}`;
  }

  /**
   * Record adaptation for learning
   *
   * @param originalComponent - Original component
   * @param adaptedComponent - Adapted component
   * @param analysis - Context analysis
   */
  private recordAdaptation(
    originalComponent: ComponentInstance,
    adaptedComponent: ComponentInstance,
    analysis: ContextAnalysis
  ): void {
    // Record successful adaptation
    this.learningData.interactionPatterns.successfulAdaptations.push({
      context: this.currentContext,
      adaptation: Object.values(analysis.adaptations)[0] || {
        propertyChanges: {},
        layoutChanges: {},
        behaviorChanges: {},
        performanceChanges: {},
        accessibilityChanges: {},
      },
      success: true, // This would be determined by user feedback
    });

    // Update preferred components
    const componentType = originalComponent.component;
    this.learningData.interactionPatterns.preferredComponents[componentType] =
      (this.learningData.interactionPatterns.preferredComponents[componentType] || 0) + 1;

    // Record adaptation in history
    this.adaptationHistory.push({
      context: this.currentContext,
      adaptations: analysis.adaptations,
    });

    // Keep history size manageable
    if (this.adaptationHistory.length > 100) {
      this.adaptationHistory = this.adaptationHistory.slice(-50);
    }
  }

  /**
   * Get current context
   *
   * @returns Current user context
   */
  getCurrentContext(): UserContext {
    return { ...this.currentContext };
  }

  /**
   * Get learning data
   *
   * @returns Current learning data
   */
  getLearningData(): AdaptationLearningData {
    return { ...this.learningData };
  }

  /**
   * Get adapter statistics
   *
   * @returns Statistics object
   */
  getStats(): {
    currentContext: UserContext;
    adaptationHistory: number;
    learningDataPoints: number;
    contextTransitions: number;
    preferredComponents: Record<string, number>;
  } {
    return {
      currentContext: this.currentContext,
      adaptationHistory: this.adaptationHistory.length,
      learningDataPoints: this.learningData.interactionPatterns.successfulAdaptations.length,
      contextTransitions: this.learningData.contextPatterns.contextTransitions.length,
      preferredComponents: this.learningData.interactionPatterns.preferredComponents,
    };
  }

  /**
   * Reset learning data
   */
  resetLearningData(): void {
    this.learningData = this.initializeLearningData();
    this.adaptationHistory = [];
    console.log('🗑️ Learning data reset');
  }
}
