/**
 * @fileoverview Enhanced Event Producer Service with Protocol Buffers
 *
 * @description
 * Production-ready event producer with protobuf serialization,
 * tenant-aware partitioning, and rich context capture.
 *
 * @author LLM Agent
 * @version 3.0.0
 * @since 2025-01-04
 */

import { Kafka, Producer, ProducerRecord } from 'kafkajs';
import { v4 as uuidv4 } from 'uuid';
import * as proto from '../types/proto/universal_event';

export interface EventProducerConfig {
  kafkaBrokers: string[];
  clientId: string;
  environment: 'DEVELOPMENT' | 'STAGING' | 'PRODUCTION';
  region: string;
  instanceId?: string;
  tenantId: string;
}

export interface EventContext {
  correlationId: string;
  causationId?: string;
  sessionId?: string;
  userId?: string;
  workflowId?: string;
  requestId?: string;
}

export interface EventMetadata {
  tags?: string[];
  piiFields?: string[];
  retentionPolicy?: proto.RetentionPolicy;
  customMetadata?: Record<string, string>;
}

export class EventProducerService {
  private kafka: Kafka;
  private producer: Producer;
  private config: EventProducerConfig;
  private isConnected: boolean = false;
  private sequenceCounter: number = 0;

  constructor(config: EventProducerConfig) {
    this.config = config;

    this.kafka = new Kafka({
      clientId: config.clientId,
      brokers: config.kafkaBrokers,
      retry: {
        initialRetryTime: 100,
        retries: 8,
      },
      connectionTimeout: 3000,
      requestTimeout: 30000,
    });

    this.producer = this.kafka.producer({
      maxInFlightRequests: 1,
      idempotent: true,
      transactionTimeout: 30000,
      retry: {
        initialRetryTime: 100,
        retries: 5,
      },
    });
  }

  /**
   * Initialize the producer
   */
  async initialize(): Promise<void> {
    try {
      await this.producer.connect();
      this.isConnected = true;
      console.log('✅ Event Producer Service connected to Kafka');
    } catch (error) {
      console.error('❌ Failed to initialize Event Producer Service:', error);
      throw error;
    }
  }

  /**
   * Create universal event with protobuf payload
   */
  private createUniversalEvent(
    eventType: string,
    sourceService: string,
    payload: any,
    context: EventContext,
    metadata: EventMetadata = {},
    sourceComponent?: string
  ): proto.UniversalEvent {
    return proto.UniversalEvent.create({
      eventId: uuidv4(),
      eventType: eventType,
      eventVersion: '1.0.0',
      timestampMs: Date.now(),
      sequenceNumber: ++this.sequenceCounter,
      correlationId: context.correlationId,
      causationId: context.causationId || '',
      tenantId: this.config.tenantId,
      userId: context.userId || '',
      sessionId: context.sessionId || '',
      workflowId: context.workflowId || '',
      sourceService: sourceService,
      sourceComponent: sourceComponent || '',
      environment: this.config.environment,
      region: this.config.region,
      instanceId: this.config.instanceId || '',
      requestId: context.requestId || '',
      payload: payload,
      tags: metadata.tags || [],
      metadata: metadata.customMetadata || {},
      piiFields: metadata.piiFields || [],
      retentionPolicy: metadata.retentionPolicy || proto.RetentionPolicy.OPERATIONAL,
    });
  }

  /**
   * Generate partition key for tenant-aware partitioning
   */
  private generatePartitionKey(tenantId: string, sessionId?: string, workflowId?: string): string {
    if (workflowId) {
      return `${tenantId}:workflow:${workflowId}`;
    }
    if (sessionId) {
      return `${tenantId}:session:${sessionId}`;
    }
    return `${tenantId}:${Math.floor(Math.random() * 1000)}`;
  }

  /**
   * Produce event to appropriate topic
   */
  private async produceEvent(
    topicName: string,
    event: proto.UniversalEvent
  ): Promise<void> {
    if (!this.isConnected) {
      throw new Error('Event Producer Service is not connected');
    }

    try {
      // Serialize with protobuf
      const encodedValue = proto.UniversalEvent.encode(event).finish();

      const partitionKey = this.generatePartitionKey(
        event.tenantId,
        event.sessionId || undefined,
        event.workflowId || undefined
      );

      const record: ProducerRecord = {
        topic: topicName,
        messages: [
          {
            key: partitionKey,
            value: Buffer.from(encodedValue),
            timestamp: event.timestampMs.toString(),
            headers: {
              'event-type': event.eventType,
              'source-service': event.sourceService,
              'correlation-id': event.correlationId,
              'tenant-id': event.tenantId,
              'event-version': event.eventVersion,
              'content-type': 'application/x-protobuf',
            },
          },
        ],
      };

      await this.producer.send(record);
      console.log(`📤 Event produced: ${event.eventType} (${event.eventId}) to ${topicName}`);
    } catch (error) {
      console.error(`❌ Failed to produce event ${event.eventId}:`, error);
      throw error;
    }
  }

  // ============================================================================
  // DOMAIN-SPECIFIC EVENT PRODUCERS
  // ============================================================================

  /**
   * Produce LLM inference event
   */
  async produceLLMInferenceEvent(
    eventType: 'llm.inference.started' | 'llm.inference.completed' | 'llm.inference.failed',
    payload: proto.LLMInferenceEvent,
    context: EventContext,
    metadata: EventMetadata = {}
  ): Promise<void> {
    const event = this.createUniversalEvent(
      eventType,
      'llm-service',
      { llmInference: payload },
      context,
      {
        ...metadata,
        tags: [...(metadata.tags || []), 'llm', 'inference', payload.model?.modelName || ''],
        retentionPolicy: proto.RetentionPolicy.TRAINING, // LLM events are valuable for training
      },
      'inference-engine'
    );

    await this.produceEvent('llm-events', event);
  }

  /**
   * Produce tool usage event
   */
  async produceToolUsageEvent(
    eventType: 'tool.execution.started' | 'tool.execution.completed' | 'tool.execution.failed',
    payload: proto.ToolUsageEvent,
    context: EventContext,
    metadata: EventMetadata = {}
  ): Promise<void> {
    const event = this.createUniversalEvent(
      eventType,
      'backend-service',
      { toolUsage: payload },
      context,
      {
        ...metadata,
        tags: [...(metadata.tags || []), 'tool', proto.ToolCategory[payload.tool?.toolCategory || 0], payload.tool?.toolName || ''],
        retentionPolicy: proto.RetentionPolicy.ANALYTICAL,
      },
      'tool-executor'
    );

    await this.produceEvent('tool-events', event);
  }

  /**
   * Produce workflow execution event
   */
  async produceWorkflowEvent(
    eventType: 'workflow.started' | 'workflow.step.completed' | 'workflow.completed' | 'workflow.failed',
    payload: any,
    context: EventContext,
    metadata: EventMetadata = {}
  ): Promise<void> {
    const envelope = this.createEventEnvelope(
      eventType,
      'backend-service',
      payload,
      'workflow-execution-payload',
      context,
      {
        ...metadata,
        tags: [...(metadata.tags || []), 'workflow', 'execution'],
        retentionPolicy: 'AUDIT', // Workflow events need long retention
      },
      'workflow-engine'
    );

    // Workflow events go to dedicated topic for strict ordering
    await this.produceEvent('workflow-events', envelope);
  }

  /**
   * Produce voice processing event
   */
  async produceVoiceEvent(
    eventType: 'voice.transcription.started' | 'voice.transcription.completed' | 'voice.synthesis.completed',
    payload: any,
    context: EventContext,
    metadata: EventMetadata = {}
  ): Promise<void> {
    const envelope = this.createEventEnvelope(
      eventType,
      'whisper-tts-service',
      payload,
      'voice-processing-payload',
      context,
      {
        ...metadata,
        tags: [...(metadata.tags || []), 'voice', eventType.includes('transcription') ? 'stt' : 'tts'],
        piiFields: ['transcription.text', 'synthesis.text'], // Voice content may contain PII
        retentionPolicy: 'OPERATIONAL',
      },
      eventType.includes('transcription') ? 'whisper-engine' : 'tts-engine'
    );

    await this.produceEvent('voice-events', envelope);
  }

  /**
   * Produce UI generation event
   */
  async produceUIEvent(
    eventType: 'ui.generation.started' | 'ui.generation.completed' | 'ui.interaction.recorded',
    payload: any,
    context: EventContext,
    metadata: EventMetadata = {}
  ): Promise<void> {
    const envelope = this.createEventEnvelope(
      eventType,
      eventType.includes('interaction') ? 'frontend-service' : 'backend-service',
      payload,
      'ui-event-payload',
      context,
      {
        ...metadata,
        tags: [...(metadata.tags || []), 'ui', eventType.includes('interaction') ? 'interaction' : 'generation'],
        retentionPolicy: 'ANALYTICAL',
      },
      eventType.includes('interaction') ? 'ui-component' : 'ui-generator'
    );

    await this.produceEvent('ui-events', envelope);
  }

  /**
   * Shutdown the producer
   */
  async shutdown(): Promise<void> {
    try {
      await this.producer.disconnect();
      this.isConnected = false;
      console.log('✅ Event Producer Service disconnected');
    } catch (error) {
      console.error('❌ Failed to disconnect Event Producer Service:', error);
      throw error;
    }
  }
}
