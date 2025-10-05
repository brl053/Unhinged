// ============================================================================
// Generated TypeScript Proto Definitions - Common Types
// ============================================================================
//
// @file common.ts
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description TypeScript definitions for common.proto messages and types
//
// This file contains shared TypeScript interfaces and types used across
// all services in the Unhinged platform.
// ============================================================================

// ============================================================================
// Enums
// ============================================================================

export enum ChunkType {
  CHUNK_TYPE_UNSPECIFIED = 0,
  CHUNK_TYPE_DATA = 1,
  CHUNK_TYPE_METADATA = 2,
  CHUNK_TYPE_ERROR = 3,
  CHUNK_TYPE_HEARTBEAT = 4,
}

export enum ChunkStatus {
  CHUNK_STATUS_UNSPECIFIED = 0,
  CHUNK_STATUS_PROCESSING = 1,
  CHUNK_STATUS_COMPLETE = 2,
  CHUNK_STATUS_ERROR = 3,
  CHUNK_STATUS_CANCELLED = 4,
}

// ============================================================================
// Core Message Interfaces
// ============================================================================

export interface StreamChunk {
  streamId?: string;
  sequenceNumber?: number;
  type?: ChunkType;
  data?: Uint8Array;
  text?: string;
  isFinal?: boolean;
  status?: ChunkStatus;
  timestamp?: string;
  structured?: { [key: string]: any };
}

export interface StandardResponse {
  success?: boolean;
  message?: string;
  timestamp?: string;
  requestId?: string;
}

export interface ResourceMetadata {
  resourceId?: string;
  createdAt?: string;
  updatedAt?: string;
  version?: string;
  tags?: { [key: string]: string };
}

export interface PaginationRequest {
  pageSize?: number;
  pageToken?: string;
  orderBy?: string;
  filter?: string;
}

export interface PaginationResponse {
  hasMore?: boolean;
  nextPageToken?: string;
  pageSize?: number;
  totalCount?: number;
}

// ============================================================================
// Usage and Metrics
// ============================================================================

export interface AudioUsage {
  duration?: {
    seconds?: number;
    nanos?: number;
  };
  bytesProcessed?: number;
  sampleRate?: number;
  channels?: number;
  format?: string;
}

export interface TokenUsage {
  promptTokens?: number;
  completionTokens?: number;
  totalTokens?: number;
  cost?: number;
}

export interface Usage {
  audio?: AudioUsage;
  tokens?: TokenUsage;
  requestCount?: number;
  timestamp?: string;
}

// ============================================================================
// Health Check
// ============================================================================

export interface HealthCheckRequest {
  service?: string;
}

export interface HealthCheckResponse {
  status?: string;
  timestamp?: string;
  details?: { [key: string]: string };
}

// ============================================================================
// Error Handling
// ============================================================================

export interface ErrorDetail {
  code?: string;
  message?: string;
  field?: string;
  value?: string;
}

export interface ErrorResponse {
  error?: string;
  details?: ErrorDetail[];
  timestamp?: string;
  requestId?: string;
}

// ============================================================================
// Attachment and File Handling
// ============================================================================

export interface Attachment {
  id?: string;
  filename?: string;
  contentType?: string;
  size?: number;
  data?: Uint8Array;
  url?: string;
  metadata?: { [key: string]: string };
}

export interface FileUpload {
  filename?: string;
  contentType?: string;
  data?: Uint8Array;
  checksum?: string;
}

// ============================================================================
// Utility Types
// ============================================================================

export interface KeyValue {
  key?: string;
  value?: string;
}

export interface Duration {
  seconds?: number;
  nanos?: number;
}

export interface Timestamp {
  seconds?: number;
  nanos?: number;
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Creates a new StreamChunk with default values
 */
export function createStreamChunk(data: Partial<StreamChunk>): StreamChunk {
  return {
    streamId: data.streamId || '',
    sequenceNumber: data.sequenceNumber || 0,
    type: data.type || ChunkType.CHUNK_TYPE_DATA,
    data: data.data || new Uint8Array(),
    text: data.text || '',
    isFinal: data.isFinal || false,
    status: data.status || ChunkStatus.CHUNK_STATUS_PROCESSING,
    timestamp: data.timestamp || new Date().toISOString(),
    structured: data.structured || {},
  };
}

/**
 * Creates a new StandardResponse with default values
 */
export function createStandardResponse(data: Partial<StandardResponse>): StandardResponse {
  return {
    success: data.success || false,
    message: data.message || '',
    timestamp: data.timestamp || new Date().toISOString(),
    requestId: data.requestId || generateRequestId(),
  };
}

/**
 * Creates a new PaginationRequest with default values
 */
export function createPaginationRequest(data: Partial<PaginationRequest>): PaginationRequest {
  return {
    pageSize: data.pageSize || 50,
    pageToken: data.pageToken || '',
    orderBy: data.orderBy || '',
    filter: data.filter || '',
  };
}

/**
 * Creates a new Duration from seconds
 */
export function createDuration(seconds: number): Duration {
  return {
    seconds: Math.floor(seconds),
    nanos: Math.floor((seconds % 1) * 1e9),
  };
}

/**
 * Converts Duration to seconds
 */
export function durationToSeconds(duration: Duration): number {
  return (duration.seconds || 0) + (duration.nanos || 0) / 1e9;
}

/**
 * Creates a new Timestamp from Date
 */
export function createTimestamp(date: Date = new Date()): Timestamp {
  const seconds = Math.floor(date.getTime() / 1000);
  const nanos = (date.getTime() % 1000) * 1e6;
  return { seconds, nanos };
}

/**
 * Converts Timestamp to Date
 */
export function timestampToDate(timestamp: Timestamp): Date {
  const milliseconds = (timestamp.seconds || 0) * 1000 + (timestamp.nanos || 0) / 1e6;
  return new Date(milliseconds);
}

/**
 * Generates a unique request ID
 */
export function generateRequestId(): string {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Checks if a response indicates success
 */
export function isSuccessResponse(response: StandardResponse): boolean {
  return response.success === true;
}

/**
 * Extracts error message from response
 */
export function getErrorMessage(response: StandardResponse): string {
  return response.message || 'Unknown error occurred';
}

// ============================================================================
// Type Guards
// ============================================================================

/**
 * Type guard for StreamChunk
 */
export function isStreamChunk(obj: any): obj is StreamChunk {
  return obj && typeof obj === 'object' && 'streamId' in obj;
}

/**
 * Type guard for StandardResponse
 */
export function isStandardResponse(obj: any): obj is StandardResponse {
  return obj && typeof obj === 'object' && 'success' in obj;
}

/**
 * Type guard for ErrorResponse
 */
export function isErrorResponse(obj: any): obj is ErrorResponse {
  return obj && typeof obj === 'object' && 'error' in obj;
}

// ============================================================================
// Constants
// ============================================================================

export const DEFAULT_PAGE_SIZE = 50;
export const MAX_PAGE_SIZE = 1000;
export const DEFAULT_TIMEOUT_MS = 30000;
export const MAX_CHUNK_SIZE = 1024 * 1024; // 1MB
export const HEARTBEAT_INTERVAL_MS = 30000; // 30 seconds
