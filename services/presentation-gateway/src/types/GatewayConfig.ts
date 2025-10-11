// ============================================================================
// Gateway Configuration Types
// ============================================================================
//
// @file GatewayConfig.ts
// @version 1.0.0
// @author Unhinged Team
// @date 2025-10-06
// @description TypeScript interfaces for gateway configuration
// ============================================================================

/**
 * Complete gateway configuration interface
 */
export interface GatewayConfig {
  server: ServerConfig;
  grpc: GrpcConfig;
  auth: AuthConfig;
  rateLimit: RateLimitConfig;
  cache: CacheConfig;
  websocket: WebSocketConfig;
  sse: SSEConfig;
  development: DevelopmentConfig;
}

/**
 * HTTP server configuration
 */
export interface ServerConfig {
  port: number;
  host: string;
  cors: {
    origins: string[];
    credentials: boolean;
  };
}

/**
 * gRPC backend services configuration
 */
export interface GrpcConfig {
  services: GrpcServiceConfig[];
  options: {
    keepalive: {
      keepaliveTimeMs: number;
      keepaliveTimeoutMs: number;
      keepalivePermitWithoutCalls: boolean;
    };
    retry: {
      maxAttempts: number;
      initialDelay: number;
      maxDelay: number;
      backoffMultiplier: number;
    };
  };
}

/**
 * Individual gRPC service configuration
 */
export interface GrpcServiceConfig {
  name: string;
  address: string;
  protoPath: string;
  packageName: string;
}

/**
 * Authentication configuration
 */
export interface AuthConfig {
  jwt: {
    secret: string;
    issuer: string;
    audience: string;
  };
  apiKey: {
    header: string;
    enabled: boolean;
  };
}

/**
 * Rate limiting configuration
 */
export interface RateLimitConfig {
  windowMs: number;
  max: number;
  standardHeaders: boolean;
  legacyHeaders: boolean;
}

/**
 * Caching configuration
 */
export interface CacheConfig {
  redis: {
    url: string;
    keyPrefix: string;
  };
  defaultTtl: number;
}

/**
 * WebSocket configuration
 */
export interface WebSocketConfig {
  maxConnections: number;
  pingInterval: number;
  pongTimeout: number;
  maxMessageSize: number;
}

/**
 * Server-Sent Events configuration
 */
export interface SSEConfig {
  keepaliveInterval: number;
  maxStreamDuration: number;
  maxClients: number;
}

/**
 * Development and debugging configuration
 */
export interface DevelopmentConfig {
  enableSwagger: boolean;
  enableMetrics: boolean;
  logLevel: string;
}