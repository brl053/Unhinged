/**
 * @fileoverview Event Payload Type Definitions
 * 
 * @description
 * TypeScript definitions for event-specific payloads that get serialized
 * into the event_data.payload field. Each event type has its own structure
 * with rich context and rationale for AI/ML analysis.
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

// ============================================================================
// LLM INFERENCE EVENTS
// ============================================================================

export interface LLMInferencePayload {
  model_name: string;
  model_version: string;
  prompt: {
    text: string;
    tokens: number;
    template_used?: string;
    context_window_size: number;
  };
  response: {
    text: string;
    tokens: number;
    finish_reason: 'stop' | 'length' | 'content_filter' | 'error';
    confidence_score?: number;
  };
  parameters: {
    temperature: number;
    max_tokens: number;
    top_p?: number;
    frequency_penalty?: number;
    presence_penalty?: number;
  };
  rationale: {
    intent: string;
    expected_outcome: string;
    reasoning_chain?: string[];
    decision_factors: string[];
  };
  performance: {
    latency_ms: number;
    tokens_per_second: number;
    cost_estimate_usd?: number;
  };
  context: {
    conversation_history_length: number;
    system_prompt_used: boolean;
    rag_context_used: boolean;
    tool_calling_enabled: boolean;
  };
}

// ============================================================================
// TOOL USAGE EVENTS
// ============================================================================

export interface ToolUsagePayload {
  tool_name: string;
  tool_version: string;
  tool_category: 'web_scraping' | 'api_call' | 'file_operation' | 'data_processing' | 'ui_generation' | 'voice_processing';
  
  input: {
    parameters: Record<string, any>;
    raw_input?: string;
    validation_passed: boolean;
  };
  
  output: {
    result: any;
    success: boolean;
    error_message?: string;
    data_size_bytes?: number;
  };
  
  rationale: {
    why_this_tool: string;
    expected_outcome: string;
    alternative_tools_considered: string[];
    risk_assessment: string;
    success_criteria: string[];
  };
  
  // Web scraping specific
  web_scraping?: {
    target_url: string;
    target_domain: string;
    scraping_strategy: string;
    data_extraction_rules: string[];
    what_looking_for: string;
    found_data_summary: string;
    robots_txt_compliant: boolean;
    rate_limiting_applied: boolean;
  };
  
  // API call specific
  api_call?: {
    endpoint: string;
    method: string;
    headers: Record<string, string>;
    response_status: number;
    response_time_ms: number;
    retry_count: number;
  };
  
  performance: {
    execution_time_ms: number;
    memory_peak_mb: number;
    network_bytes_transferred?: number;
  };
}

// ============================================================================
// VOICE PROCESSING EVENTS
// ============================================================================

export interface VoiceTranscriptionPayload {
  audio: {
    duration_seconds: number;
    sample_rate: number;
    channels: number;
    format: string;
    size_bytes: number;
    quality_score?: number;
  };
  
  transcription: {
    text: string;
    confidence_score: number;
    language_detected: string;
    word_timestamps?: Array<{
      word: string;
      start_time: number;
      end_time: number;
      confidence: number;
    }>;
  };
  
  processing: {
    model_used: string;
    preprocessing_applied: string[];
    post_processing_applied: string[];
    processing_time_ms: number;
  };
  
  context: {
    user_intent: string;
    expected_language: string;
    noise_level: 'low' | 'medium' | 'high';
    speaker_identification?: string;
  };
  
  rationale: {
    transcription_purpose: string;
    accuracy_requirements: string;
    downstream_usage: string[];
  };
}

export interface TTSSynthesisPayload {
  text: {
    content: string;
    length_chars: number;
    language: string;
    ssml_used: boolean;
  };
  
  audio_output: {
    duration_seconds: number;
    sample_rate: number;
    format: string;
    size_bytes: number;
    quality_setting: string;
  };
  
  voice_config: {
    voice_id: string;
    voice_name: string;
    gender: string;
    accent: string;
    speed: number;
    pitch: number;
    volume: number;
  };
  
  processing: {
    model_used: string;
    synthesis_time_ms: number;
    preprocessing_steps: string[];
  };
  
  rationale: {
    synthesis_purpose: string;
    voice_selection_reason: string;
    target_audience: string;
    emotional_tone_desired: string;
  };
}

// ============================================================================
// UI GENERATION EVENTS
// ============================================================================

export interface UIGenerationPayload {
  request: {
    user_prompt: string;
    ui_type: 'component' | 'page' | 'layout' | 'widget';
    target_platform: 'web' | 'mobile' | 'desktop';
    framework: string;
    style_preferences: Record<string, any>;
  };
  
  generated_ui: {
    component_name: string;
    component_type: string;
    code_generated: boolean;
    code_language: string;
    lines_of_code: number;
    dependencies: string[];
  };
  
  design_decisions: {
    layout_strategy: string;
    color_scheme: string;
    typography_choices: string[];
    accessibility_features: string[];
    responsive_breakpoints: string[];
  };
  
  rationale: {
    design_philosophy: string;
    user_experience_goals: string[];
    technical_constraints: string[];
    accessibility_considerations: string[];
    performance_optimizations: string[];
  };
  
  validation: {
    syntax_valid: boolean;
    accessibility_score?: number;
    performance_score?: number;
    best_practices_followed: string[];
  };
}

// ============================================================================
// USER INTERACTION EVENTS
// ============================================================================

export interface UserInteractionPayload {
  interaction_type: 'click' | 'voice_command' | 'text_input' | 'gesture' | 'navigation';
  
  ui_element: {
    element_type: string;
    element_id?: string;
    element_class?: string;
    page_url: string;
    viewport_size: { width: number; height: number };
  };
  
  user_input: {
    raw_input: string;
    processed_input: string;
    input_method: string;
    input_duration_ms?: number;
  };
  
  system_response: {
    response_type: string;
    response_data: any;
    response_time_ms: number;
    success: boolean;
  };
  
  context: {
    user_journey_step: string;
    previous_interactions: number;
    session_duration_ms: number;
    user_expertise_level: 'beginner' | 'intermediate' | 'expert';
  };
  
  intent_analysis: {
    detected_intent: string;
    confidence_score: number;
    alternative_intents: string[];
    context_clues_used: string[];
  };
  
  rationale: {
    interaction_purpose: string;
    expected_user_goal: string;
    system_interpretation: string;
    response_strategy: string;
  };
}

// ============================================================================
// WORKFLOW EXECUTION EVENTS
// ============================================================================

export interface WorkflowExecutionPayload {
  workflow: {
    workflow_id: string;
    workflow_name: string;
    workflow_version: string;
    workflow_type: 'linear' | 'dag' | 'conditional' | 'parallel';
  };
  
  execution: {
    execution_id: string;
    step_name: string;
    step_index: number;
    total_steps: number;
    step_type: string;
    step_status: 'started' | 'completed' | 'failed' | 'skipped';
  };
  
  step_data: {
    input_data: any;
    output_data: any;
    processing_time_ms: number;
    resources_used: Record<string, any>;
  };
  
  decision_tree: {
    decision_point: string;
    available_options: string[];
    chosen_option: string;
    decision_criteria: string[];
    confidence_score: number;
    historical_data_used: boolean;
  };
  
  rationale: {
    step_purpose: string;
    decision_reasoning: string;
    risk_mitigation: string[];
    success_metrics: string[];
    fallback_strategies: string[];
  };
  
  context: {
    trigger_event: string;
    business_context: string;
    user_context: Record<string, any>;
    system_state: Record<string, any>;
  };
}

// ============================================================================
// SYSTEM STATE CHANGE EVENTS
// ============================================================================

export interface SystemStateChangePayload {
  state_change: {
    entity_type: string;
    entity_id: string;
    change_type: 'create' | 'update' | 'delete' | 'archive';
    field_changes: Array<{
      field_name: string;
      old_value: any;
      new_value: any;
      change_reason: string;
    }>;
  };
  
  change_metadata: {
    change_source: string;
    change_method: string;
    batch_operation: boolean;
    transaction_id?: string;
  };
  
  impact_analysis: {
    affected_systems: string[];
    downstream_effects: string[];
    rollback_possible: boolean;
    data_consistency_maintained: boolean;
  };
  
  rationale: {
    change_justification: string;
    business_impact: string;
    technical_necessity: string;
    compliance_requirements: string[];
  };
  
  audit_trail: {
    approval_required: boolean;
    approver_id?: string;
    approval_timestamp?: number;
    compliance_tags: string[];
  };
}

// ============================================================================
// UNION TYPE FOR ALL PAYLOADS
// ============================================================================

export type EventPayload = 
  | LLMInferencePayload
  | ToolUsagePayload
  | VoiceTranscriptionPayload
  | TTSSynthesisPayload
  | UIGenerationPayload
  | UserInteractionPayload
  | WorkflowExecutionPayload
  | SystemStateChangePayload;

// ============================================================================
// EVENT FACTORY INTERFACES
// ============================================================================

export interface EventFactory {
  createLLMInferenceEvent(payload: LLMInferencePayload): UniversalEvent;
  createToolUsageEvent(payload: ToolUsagePayload): UniversalEvent;
  createVoiceTranscriptionEvent(payload: VoiceTranscriptionPayload): UniversalEvent;
  createTTSSynthesisEvent(payload: TTSSynthesisPayload): UniversalEvent;
  createUIGenerationEvent(payload: UIGenerationPayload): UniversalEvent;
  createUserInteractionEvent(payload: UserInteractionPayload): UniversalEvent;
  createWorkflowExecutionEvent(payload: WorkflowExecutionPayload): UniversalEvent;
  createSystemStateChangeEvent(payload: SystemStateChangePayload): UniversalEvent;
}

export interface UniversalEvent {
  event_id: string;
  event_type: string;
  event_version: string;
  timestamp: number;
  correlation_id?: string;
  causation_id?: string;
  session_id?: string;
  user_id?: string;
  source_service: string;
  source_component?: string;
  aggregate_id?: string;
  aggregate_type?: string;
  event_data: {
    payload: string; // JSON-encoded EventPayload
    metadata: Record<string, string>;
  };
  context: {
    environment: 'DEVELOPMENT' | 'STAGING' | 'PRODUCTION';
    region: string;
    instance_id?: string;
    request_id?: string;
  };
  performance: {
    duration_ms?: number;
    memory_usage_mb?: number;
    cpu_usage_percent?: number;
  };
  tags: string[];
  error_info?: {
    error_code: string;
    error_message: string;
    stack_trace?: string;
    recovery_action?: string;
  };
}
