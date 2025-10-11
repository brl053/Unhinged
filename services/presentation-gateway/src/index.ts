// ============================================================================
// Presentation Gateway Service - Main Entry Point
// ============================================================================
//
// @file index.ts
// @version 1.0.0
// @author Unhinged Team
// @date 2025-10-06
// @description Main entry point for the Presentation Gateway Service
//
// This service provides protocol translation between web clients and gRPC
// backend services, automatically generating REST endpoints, WebSocket handlers,
// and Server-Sent Events from Protocol Buffer annotations.
//
// Features:
// - Auto-generated REST endpoints from gRPC services
// - WebSocket support for bidirectional streaming
// - Server-Sent Events for server-to-client streaming
// - Long polling fallback for legacy clients
// - OpenAPI documentation generation
// - Rate limiting, caching, and authentication
// ============================================================================

import 'dotenv/config';
import { PresentationGateway } from './core/PresentationGateway';
import { GatewayConfig } from './types/GatewayConfig';
import { logger } from './utils/logger';

/**
 * Gateway configuration from environment variables
 */
const config: GatewayConfig = {
  // Server configuration
  server: {
    port: parseInt(process.env.GATEWAY_PORT || '8082'),
    host: process.env.GATEWAY_HOST || '0.0.0.0',
    cors: {
      origins: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:3000'],
      credentials: true,
    },
  },

  // gRPC backend configuration
  grpc: {
    services: [
      {
        name: 'ChatService',
        address: process.env.CHAT_SERVICE_ADDRESS || 'localhost:9090',
        protoPath: '../../proto/chat.proto',
        packageName: 'unhinged.chat.v1',
      },
      {
        name: 'AudioService',
        address: process.env.AUDIO_SERVICE_ADDRESS || 'localhost:8000',
        protoPath: '../../proto/audio.proto',
        packageName: 'unhinged.audio.v1',
      },
      {
        name: 'VisionService',
        address: process.env.VISION_SERVICE_ADDRESS || 'localhost:8001',
        protoPath: '../../proto/vision_service.proto',
        packageName: 'multimodal',
      },
    ],
    options: {
      keepalive: {
        keepaliveTimeMs: 30000,
        keepaliveTimeoutMs: 5000,
        keepalivePermitWithoutCalls: true,
      },
      retry: {
        maxAttempts: 3,
        initialDelay: 1000,
        maxDelay: 5000,
        backoffMultiplier: 2,
      },
    },
  },

  // Authentication configuration
  auth: {
    jwt: {
      secret: process.env.JWT_SECRET || 'your-secret-key',
      issuer: process.env.JWT_ISSUER || 'unhinged-gateway',
      audience: process.env.JWT_AUDIENCE || 'unhinged-api',
    },
    apiKey: {
      header: 'X-API-Key',
      enabled: process.env.API_KEY_AUTH === 'true',
    },
  },

  // Rate limiting configuration
  rateLimit: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 1000, // requests per window
    standardHeaders: true,
    legacyHeaders: false,
  },

  // Caching configuration
  cache: {
    redis: {
      url: process.env.REDIS_URL || 'redis://localhost:6379',
      keyPrefix: 'gateway:',
    },
    defaultTtl: 300, // 5 minutes
  },

  // WebSocket configuration
  websocket: {
    maxConnections: 1000,
    pingInterval: 30000,
    pongTimeout: 5000,
    maxMessageSize: 1024 * 1024, // 1MB
  },

  // Server-Sent Events configuration
  sse: {
    keepaliveInterval: 30000,
    maxStreamDuration: 3600000, // 1 hour
    maxClients: 500,
  },

  // Development and debugging
  development: {
    enableSwagger: process.env.NODE_ENV !== 'production',
    enableMetrics: true,
    logLevel: process.env.LOG_LEVEL || 'info',
  },
};

/**
 * Start the Presentation Gateway Service
 */
async function startGateway(): Promise<void> {
  try {
    logger.info('🚀 Starting Presentation Gateway Service...');
    logger.info(`📋 Configuration:`, {
      port: config.server.port,
      host: config.server.host,
      grpcServices: config.grpc.services.length,
      environment: process.env.NODE_ENV || 'development',
    });

    // Create and initialize the gateway
    const gateway = new PresentationGateway(config);
    await gateway.initialize();

    // Start the server
    await gateway.start();

    logger.info(`✅ Presentation Gateway Service started successfully`);
    logger.info(`🌐 Server running at http://${config.server.host}:${config.server.port}`);
    logger.info(`📚 API Documentation: http://${config.server.host}:${config.server.port}/docs`);
    logger.info(`🔍 Health Check: http://${config.server.host}:${config.server.port}/health`);

    // Graceful shutdown handling
    const shutdown = async (signal: string) => {
      logger.info(`📡 Received ${signal}, shutting down gracefully...`);
      try {
        await gateway.stop();
        logger.info('✅ Gateway stopped successfully');
        process.exit(0);
      } catch (error) {
        logger.error('❌ Error during shutdown:', error);
        process.exit(1);
      }
    };

    process.on('SIGTERM', () => shutdown('SIGTERM'));
    process.on('SIGINT', () => shutdown('SIGINT'));

  } catch (error) {
    logger.error('❌ Failed to start Presentation Gateway Service:', error);
    process.exit(1);
  }
}

// Start the service
if (require.main === module) {
  startGateway().catch((error) => {
    logger.error('💥 Unhandled error during startup:', error);
    process.exit(1);
  });
}

export { PresentationGateway, GatewayConfig };