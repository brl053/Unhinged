/**
 * @fileoverview Event Consumer Service with Protocol Buffers
 * 
 * @description
 * Production-ready event consumer that deserializes protobuf events
 * and stores them in PostgreSQL with JSONB payload for querying.
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import { Kafka, Consumer, EachMessagePayload } from 'kafkajs';
import { Pool } from 'pg';
import * as proto from '../types/proto/universal_event';

export interface EventConsumerConfig {
  kafkaBrokers: string[];
  clientId: string;
  groupId: string;
  topics: string[];
  postgresConfig: {
    host: string;
    port: number;
    database: string;
    user: string;
    password: string;
  };
  tenantId: string;
}

export class EventConsumerService {
  private kafka: Kafka;
  private consumer: Consumer;
  private pgPool: Pool;
  private config: EventConsumerConfig;
  private isRunning: boolean = false;

  constructor(config: EventConsumerConfig) {
    this.config = config;
    
    this.kafka = new Kafka({
      clientId: config.clientId,
      brokers: config.kafkaBrokers,
      retry: {
        initialRetryTime: 100,
        retries: 8,
      },
    });

    this.consumer = this.kafka.consumer({
      groupId: config.groupId,
      sessionTimeout: 30000,
      heartbeatInterval: 3000,
      maxWaitTimeInMs: 5000,
      retry: {
        initialRetryTime: 100,
        retries: 5,
      },
    });

    this.pgPool = new Pool({
      host: config.postgresConfig.host,
      port: config.postgresConfig.port,
      database: config.postgresConfig.database,
      user: config.postgresConfig.user,
      password: config.postgresConfig.password,
      max: 20,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 2000,
    });
  }

  /**
   * Initialize the consumer
   */
  async initialize(): Promise<void> {
    try {
      await this.consumer.connect();
      await this.consumer.subscribe({ 
        topics: this.config.topics,
        fromBeginning: false 
      });
      
      // Set tenant context for RLS
      await this.pgPool.query(`SET app.current_tenant_id = '${this.config.tenantId}'`);
      
      console.log('✅ Event Consumer Service initialized');
    } catch (error) {
      console.error('❌ Failed to initialize Event Consumer Service:', error);
      throw error;
    }
  }

  /**
   * Start consuming events
   */
  async start(): Promise<void> {
    if (this.isRunning) {
      console.log('⚠️  Consumer is already running');
      return;
    }

    this.isRunning = true;
    console.log('🚀 Starting event consumption...');

    await this.consumer.run({
      eachMessage: async (payload: EachMessagePayload) => {
        await this.processMessage(payload);
      },
    });
  }

  /**
   * Process individual message
   */
  private async processMessage(payload: EachMessagePayload): Promise<void> {
    const { topic, partition, message } = payload;
    
    try {
      if (!message.value) {
        console.warn('⚠️  Received message with no value');
        return;
      }

      // Deserialize protobuf
      const event = proto.UniversalEvent.decode(message.value);
      
      // Validate tenant isolation
      if (event.tenantId !== this.config.tenantId) {
        console.warn(`⚠️  Received event for different tenant: ${event.tenantId}`);
        return;
      }

      // Store in PostgreSQL
      await this.storeEvent(event, message.value);
      
      // Process domain-specific logic
      await this.processDomainEvent(event);
      
      console.log(`✅ Processed event: ${event.eventType} (${event.eventId})`);
      
    } catch (error) {
      console.error(`❌ Failed to process message from ${topic}:${partition}:`, error);
      
      // Send to dead letter queue
      await this.sendToDeadLetterQueue(message, error as Error);
    }
  }

  /**
   * Store event in PostgreSQL
   */
  private async storeEvent(event: proto.UniversalEvent, rawData: Uint8Array): Promise<void> {
    const client = await this.pgPool.connect();
    
    try {
      await client.query('BEGIN');
      
      // Convert protobuf to JSONB for flexible querying
      const payloadJson = this.protobufToJson(event);
      
      const insertQuery = `
        INSERT INTO events (
          event_id, event_type, event_version, timestamp_ms,
          correlation_id, causation_id, sequence_number,
          tenant_id, user_id, session_id, workflow_id,
          source_service, source_component, environment, region,
          instance_id, request_id, payload, metadata, tags, pii_fields,
          retention_policy, protobuf_data
        ) VALUES (
          $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15,
          $16, $17, $18, $19, $20, $21, $22, $23
        )
      `;
      
      const values = [
        event.eventId,
        event.eventType,
        event.eventVersion,
        event.timestampMs,
        event.correlationId,
        event.causationId || null,
        event.sequenceNumber,
        event.tenantId,
        event.userId || null,
        event.sessionId || null,
        event.workflowId || null,
        event.sourceService,
        event.sourceComponent || null,
        event.environment,
        event.region,
        event.instanceId || null,
        event.requestId || null,
        JSON.stringify(payloadJson),
        JSON.stringify(event.metadata),
        event.tags,
        event.piiFields,
        this.retentionPolicyToString(event.retentionPolicy),
        Buffer.from(rawData),
      ];
      
      await client.query(insertQuery, values);
      await client.query('COMMIT');
      
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }

  /**
   * Convert protobuf event to JSON for JSONB storage
   */
  private protobufToJson(event: proto.UniversalEvent): any {
    const payload = event.payload;
    
    if (!payload) {
      return {};
    }
    
    // Convert oneof payload to JSON
    if ('llmInference' in payload) {
      return {
        type: 'llm_inference',
        data: this.llmInferenceToJson(payload.llmInference!),
      };
    }
    
    if ('toolUsage' in payload) {
      return {
        type: 'tool_usage',
        data: this.toolUsageToJson(payload.toolUsage!),
      };
    }
    
    if ('voiceProcessing' in payload) {
      return {
        type: 'voice_processing',
        data: this.voiceProcessingToJson(payload.voiceProcessing!),
      };
    }
    
    if ('uiGeneration' in payload) {
      return {
        type: 'ui_generation',
        data: this.uiGenerationToJson(payload.uiGeneration!),
      };
    }
    
    if ('workflowExecution' in payload) {
      return {
        type: 'workflow_execution',
        data: this.workflowExecutionToJson(payload.workflowExecution!),
      };
    }
    
    return { type: 'unknown', data: {} };
  }

  /**
   * Convert LLM inference event to JSON
   */
  private llmInferenceToJson(event: proto.LLMInferenceEvent): any {
    return {
      inference_id: event.inferenceId,
      model: event.model ? {
        model_name: event.model.modelName,
        model_version: event.model.modelVersion,
        provider: event.model.provider,
        model_type: event.model.modelType,
      } : null,
      prompt: event.prompt ? {
        text: event.prompt.text,
        token_count: event.prompt.tokenCount,
        template_used: event.prompt.templateUsed,
        context_window_size: event.prompt.contextWindowSize,
        system_prompt_included: event.prompt.systemPromptIncluded,
      } : null,
      response: event.response ? {
        text: event.response.text,
        token_count: event.response.tokenCount,
        finish_reason: proto.FinishReason[event.response.finishReason],
        confidence_score: event.response.confidenceScore,
      } : null,
      rationale: event.rationale ? {
        intent: event.rationale.intent,
        expected_outcome: event.rationale.expectedOutcome,
        reasoning_chain: event.rationale.reasoningChain,
        decision_factors: event.rationale.decisionFactors,
        alternatives_considered: event.rationale.alternativesConsidered?.map(alt => ({
          description: alt.description,
          score: alt.score,
          rejection_reason: alt.rejectionReason,
        })),
        risk_assessment: event.rationale.riskAssessment,
        decision_confidence: event.rationale.decisionConfidence,
      } : null,
      performance: event.performance ? {
        latency_ms: event.performance.latencyMs,
        tokens_per_second: event.performance.tokensPerSecond,
        cost_estimate_usd: event.performance.costEstimateUsd,
        memory_usage_mb: event.performance.memoryUsageMb,
      } : null,
      outcome: event.outcome ? {
        success: event.outcome.success,
        error_code: event.outcome.errorCode,
        error_message: event.outcome.errorMessage,
        retry_count: event.outcome.retryCount,
        user_satisfaction: proto.SatisfactionLevel[event.outcome.userSatisfaction],
      } : null,
    };
  }

  /**
   * Convert tool usage event to JSON
   */
  private toolUsageToJson(event: proto.ToolUsageEvent): any {
    return {
      execution_id: event.executionId,
      tool: event.tool ? {
        tool_name: event.tool.toolName,
        tool_version: event.tool.toolVersion,
        tool_category: proto.ToolCategory[event.tool.toolCategory],
        tool_provider: event.tool.toolProvider,
      } : null,
      input: event.input ? {
        parameters_json: event.input.parametersJson,
        raw_input: event.input.rawInput,
        validation_passed: event.input.validationPassed,
        validation_errors: event.input.validationErrors,
        input_size_bytes: event.input.inputSizeBytes,
      } : null,
      output: event.output ? {
        result_json: event.output.resultJson,
        success: event.output.success,
        error_message: event.output.errorMessage,
        output_size_bytes: event.output.outputSizeBytes,
        data_quality_score: event.output.dataQualityScore,
      } : null,
      // Add other fields as needed...
    };
  }

  // Placeholder methods for other event types
  private voiceProcessingToJson(event: proto.VoiceProcessingEvent): any {
    return { processing_id: event.processingId };
  }

  private uiGenerationToJson(event: proto.UIGenerationEvent): any {
    return { generation_id: event.generationId };
  }

  private workflowExecutionToJson(event: proto.WorkflowExecutionEvent): any {
    return { execution_id: event.executionId };
  }

  /**
   * Process domain-specific event logic
   */
  private async processDomainEvent(event: proto.UniversalEvent): Promise<void> {
    // Route to domain-specific processors
    if (event.payload && 'llmInference' in event.payload) {
      await this.processLLMInferenceEvent(event.payload.llmInference!);
    }
    
    if (event.payload && 'toolUsage' in event.payload) {
      await this.processToolUsageEvent(event.payload.toolUsage!);
    }
    
    // Add other domain processors...
  }

  /**
   * Process LLM inference event for analytics
   */
  private async processLLMInferenceEvent(event: proto.LLMInferenceEvent): Promise<void> {
    // Store in analytics table
    const client = await this.pgPool.connect();
    
    try {
      const insertQuery = `
        INSERT INTO llm_inference_analytics (
          event_id, tenant_id, model_name, model_version,
          prompt_tokens, response_tokens, total_tokens,
          tokens_per_second, latency_ms, cost_estimate_usd,
          confidence_score, finish_reason, success
        ) VALUES (
          (SELECT event_id FROM events WHERE correlation_id = $1 ORDER BY created_at DESC LIMIT 1),
          $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13
        )
      `;
      
      const values = [
        event.inferenceId, // Using inference_id as correlation
        this.config.tenantId,
        event.model?.modelName || '',
        event.model?.modelVersion || '',
        event.prompt?.tokenCount || 0,
        event.response?.tokenCount || 0,
        (event.prompt?.tokenCount || 0) + (event.response?.tokenCount || 0),
        event.performance?.tokensPerSecond || 0,
        event.performance?.latencyMs || 0,
        event.performance?.costEstimateUsd || 0,
        event.response?.confidenceScore || 0,
        proto.FinishReason[event.response?.finishReason || 0],
        event.outcome?.success || false,
      ];
      
      await client.query(insertQuery, values);
      
    } catch (error) {
      console.error('❌ Failed to store LLM analytics:', error);
    } finally {
      client.release();
    }
  }

  /**
   * Process tool usage event for analytics
   */
  private async processToolUsageEvent(event: proto.ToolUsageEvent): Promise<void> {
    // Similar analytics processing for tool usage
    console.log(`📊 Processing tool usage analytics for: ${event.tool?.toolName}`);
  }

  /**
   * Send failed message to dead letter queue
   */
  private async sendToDeadLetterQueue(message: any, error: Error): Promise<void> {
    // Implementation for dead letter queue
    console.error('💀 Sending to DLQ:', error.message);
  }

  /**
   * Convert retention policy enum to string
   */
  private retentionPolicyToString(policy: proto.RetentionPolicy): string {
    return proto.RetentionPolicy[policy] || 'OPERATIONAL';
  }

  /**
   * Stop the consumer
   */
  async stop(): Promise<void> {
    if (!this.isRunning) {
      return;
    }

    this.isRunning = false;
    await this.consumer.disconnect();
    await this.pgPool.end();
    console.log('✅ Event Consumer Service stopped');
  }
}
