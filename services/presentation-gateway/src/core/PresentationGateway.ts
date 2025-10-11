// ============================================================================
// Presentation Gateway - Core Service Implementation
// ============================================================================
//
// @file PresentationGateway.ts
// @version 1.0.0
// @author Unhinged Team
// @date 2025-10-06
// @description Core presentation gateway service that orchestrates protocol translation
// ============================================================================

import express, { Express } from 'express';
import { createServer, Server } from 'http';
import { WebSocketServer } from 'ws';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import rateLimit from 'express-rate-limit';

import { GatewayConfig } from '../types/GatewayConfig';
import { GrpcClientManager } from './GrpcClientManager';
import { HttpProtocolHandler } from '../protocols/HttpProtocolHandler';
import { WebSocketProtocolHandler } from '../protocols/WebSocketProtocolHandler';
import { SSEProtocolHandler } from '../protocols/SSEProtocolHandler';
import { AuthenticationMiddleware } from '../middleware/AuthenticationMiddleware';
import { CacheMiddleware } from '../middleware/CacheMiddleware';
import { logger } from '../utils/logger';

/**
 * Main Presentation Gateway Service
 *
 * Orchestrates protocol translation between web clients and gRPC backend services.
 * Automatically generates REST endpoints, WebSocket handlers, and SSE streams
 * from Protocol Buffer annotations.
 */
export class PresentationGateway {
  private app: Express;
  private server: Server;
  private wsServer: WebSocketServer;
  private grpcManager: GrpcClientManager;
  private httpHandler: HttpProtocolHandler;
  private wsHandler: WebSocketProtocolHandler;
  private sseHandler: SSEProtocolHandler;
  private authMiddleware: AuthenticationMiddleware;
  private cacheMiddleware: CacheMiddleware;

  constructor(private config: GatewayConfig) {
    this.app = express();
    this.server = createServer(this.app);
    this.wsServer = new WebSocketServer({ server: this.server });

    // Initialize core components
    this.grpcManager = new GrpcClientManager(config.grpc);
    this.authMiddleware = new AuthenticationMiddleware(config.auth);
    this.cacheMiddleware = new CacheMiddleware(config.cache);

    // Initialize protocol handlers
    this.httpHandler = new HttpProtocolHandler(this.grpcManager, config);
    this.wsHandler = new WebSocketProtocolHandler(this.grpcManager, config);
    this.sseHandler = new SSEProtocolHandler(this.grpcManager, config);
  }

  /**
   * Initialize the gateway service
   */
  async initialize(): Promise<void> {
    logger.info('🔧 Initializing Presentation Gateway...');

    try {
      // Initialize gRPC connections
      await this.grpcManager.initialize();
      logger.info('✅ gRPC client manager initialized');

      // Initialize middleware
      await this.authMiddleware.initialize();
      await this.cacheMiddleware.initialize();
      logger.info('✅ Middleware initialized');

      // Setup Express middleware
      this.setupMiddleware();
      logger.info('✅ Express middleware configured');

      // Initialize protocol handlers
      await this.httpHandler.initialize();
      await this.wsHandler.initialize();
      await this.sseHandler.initialize();
      logger.info('✅ Protocol handlers initialized');

      // Setup routes and handlers
      this.setupRoutes();
      this.setupWebSocketHandlers();
      logger.info('✅ Routes and handlers configured');

      logger.info('🎉 Presentation Gateway initialized successfully');

    } catch (error) {
      logger.error('❌ Failed to initialize Presentation Gateway:', error);
      throw error;
    }
  }

  /**
   * Start the gateway server
   */
  async start(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.server.listen(this.config.server.port, this.config.server.host, () => {
          logger.info(`🌐 Gateway server listening on ${this.config.server.host}:${this.config.server.port}`);
          resolve();
        });

        this.server.on('error', (error) => {
          logger.error('❌ Server error:', error);
          reject(error);
        });

      } catch (error) {
        logger.error('❌ Failed to start gateway server:', error);
        reject(error);
      }
    });
  }

  /**
   * Stop the gateway server gracefully
   */
  async stop(): Promise<void> {
    logger.info('🛑 Stopping Presentation Gateway...');

    try {
      // Close WebSocket server
      this.wsServer.close();
      logger.info('✅ WebSocket server closed');

      // Close HTTP server
      await new Promise<void>((resolve) => {
        this.server.close(() => {
          logger.info('✅ HTTP server closed');
          resolve();
        });
      });

      // Close gRPC connections
      await this.grpcManager.close();
      logger.info('✅ gRPC connections closed');

      // Close middleware connections
      await this.cacheMiddleware.close();
      logger.info('✅ Middleware connections closed');

      logger.info('🎉 Presentation Gateway stopped successfully');

    } catch (error) {
      logger.error('❌ Error during gateway shutdown:', error);
      throw error;
    }
  }

  /**
   * Setup Express middleware
   */
  private setupMiddleware(): void {
    // Security middleware
    this.app.use(helmet({
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          styleSrc: ["'self'", "'unsafe-inline'"],
          scriptSrc: ["'self'"],
          imgSrc: ["'self'", "data:", "https:"],
        },
      },
    }));

    // CORS middleware
    this.app.use(cors({
      origin: this.config.server.cors.origins,
      credentials: this.config.server.cors.credentials,
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
      allowedHeaders: ['Content-Type', 'Authorization', 'X-API-Key', 'X-Request-ID'],
    }));

    // Compression middleware
    this.app.use(compression());

    // Body parsing middleware
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

    // Rate limiting middleware
    this.app.use(rateLimit(this.config.rateLimit));

    // Request logging middleware
    this.app.use((req, res, next) => {
      const requestId = req.headers['x-request-id'] || `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      req.headers['x-request-id'] = requestId;

      logger.info(`📨 ${req.method} ${req.path}`, {
        requestId,
        userAgent: req.headers['user-agent'],
        ip: req.ip,
      });

      next();
    });
  }

  /**
   * Setup HTTP routes and handlers
   */
  private setupRoutes(): void {
    // Health check endpoint
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        services: this.grpcManager.getServiceStatus(),
      });
    });

    // Metrics endpoint (development only)
    if (this.config.development.enableMetrics) {
      this.app.get('/metrics', (req, res) => {
        res.json({
          uptime: process.uptime(),
          memory: process.memoryUsage(),
          connections: {
            grpc: this.grpcManager.getConnectionCount(),
            websocket: this.wsServer.clients.size,
          },
        });
      });
    }

    // Register HTTP protocol handlers (auto-generated from proto annotations)
    this.httpHandler.registerRoutes(this.app);

    // Register SSE protocol handlers
    this.sseHandler.registerRoutes(this.app);

    // Swagger documentation (development only)
    if (this.config.development.enableSwagger) {
      this.setupSwaggerDocs();
    }

    // 404 handler
    this.app.use('*', (req, res) => {
      res.status(404).json({
        error: 'Not Found',
        message: `Route ${req.method} ${req.originalUrl} not found`,
        timestamp: new Date().toISOString(),
      });
    });

    // Error handler
    this.app.use((error: any, req: any, res: any, next: any) => {
      logger.error('❌ Unhandled error:', error);

      res.status(error.status || 500).json({
        error: error.name || 'Internal Server Error',
        message: error.message || 'An unexpected error occurred',
        timestamp: new Date().toISOString(),
        requestId: req.headers['x-request-id'],
      });
    });
  }

  /**
   * Setup WebSocket handlers
   */
  private setupWebSocketHandlers(): void {
    this.wsServer.on('connection', (ws, request) => {
      logger.info('🔌 New WebSocket connection', {
        url: request.url,
        origin: request.headers.origin,
        userAgent: request.headers['user-agent'],
      });

      // Delegate to WebSocket protocol handler
      this.wsHandler.handleConnection(ws, request);
    });

    this.wsServer.on('error', (error) => {
      logger.error('❌ WebSocket server error:', error);
    });
  }

  /**
   * Setup Swagger documentation
   */
  private setupSwaggerDocs(): void {
    try {
      const swaggerUi = require('swagger-ui-express');
      const YAML = require('yaml');
      const fs = require('fs');
      const path = require('path');

      const swaggerPath = path.join(__dirname, '../../docs/openapi.yaml');

      if (fs.existsSync(swaggerPath)) {
        const swaggerDocument = YAML.parse(fs.readFileSync(swaggerPath, 'utf8'));

        this.app.use('/docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument, {
          customCss: '.swagger-ui .topbar { display: none }',
          customSiteTitle: 'Unhinged API Documentation',
        }));

        logger.info('📚 Swagger documentation available at /docs');
      } else {
        logger.warn('⚠️  OpenAPI specification not found, Swagger docs unavailable');
      }
    } catch (error) {
      logger.error('❌ Failed to setup Swagger documentation:', error);
    }
  }

  /**
   * Get the Express app instance (for testing)
   */
  getApp(): Express {
    return this.app;
  }

  /**
   * Get the HTTP server instance (for testing)
   */
  getServer(): Server {
    return this.server;
  }

  /**
   * Get the WebSocket server instance (for testing)
   */
  getWebSocketServer(): WebSocketServer {
    return this.wsServer;
  }
}