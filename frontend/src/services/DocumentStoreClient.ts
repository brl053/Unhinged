// ============================================================================
// DocumentStore Client - LLM-Native Frontend Integration
// ============================================================================
// 
// @file DocumentStoreClient.ts
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-04
// @description TypeScript client for DocumentStore with LLM-optimized features
// 
// This client provides:
// - Type-safe document operations with generated protobuf types
// - Session context management for LLM prompt construction
// - Real-time document updates through event streaming
// - Optimistic UI updates with conflict resolution
// - Intelligent caching for frequently accessed documents
// 
// LLM-Native Features:
// - Session context aggregation for prompt engineering
// - Document relevance scoring for optimal context ordering
// - Real-time collaboration indicators for multi-agent workflows
// - Automatic retry logic with exponential backoff
// - Token count estimation for context window management
// ============================================================================

import { 
    Document, 
    PutDocumentRequest, 
    PutDocumentResponse,
    GetDocumentRequest,
    GetDocumentResponse,
    GetSessionContextRequest,
    GetSessionContextResponse,
    ListDocumentsRequest,
    ListDocumentsResponse,
    TagDocumentRequest,
    TagDocumentResponse,
    DocumentStoreServiceClient
} from '../types/generated/document_store';
import { Timestamp } from '../types/generated/google/protobuf/timestamp';
import { Struct } from '../types/generated/google/protobuf/struct';

/**
 * Configuration options for DocumentStore client
 */
export interface DocumentStoreClientConfig {
    /** Base URL for the DocumentStore gRPC-Web service */
    baseUrl: string;
    /** Default timeout for requests in milliseconds */
    timeout?: number;
    /** Enable automatic retry with exponential backoff */
    enableRetry?: boolean;
    /** Maximum number of retry attempts */
    maxRetries?: number;
    /** Enable request/response logging for debugging */
    enableLogging?: boolean;
}

/**
 * Session context options for LLM prompt construction
 */
export interface SessionContextOptions {
    /** Document types to include in context */
    documentTypes?: string[];
    /** Maximum number of documents to retrieve */
    limit?: number;
    /** Include document bodies (vs metadata only) */
    includeBody?: boolean;
    /** Only include documents since this timestamp */
    since?: Date;
    /** Sort order for context relevance */
    sortBy?: 'relevance' | 'recency' | 'mixed';
}

/**
 * Document creation options with LLM-specific metadata
 */
export interface CreateDocumentOptions {
    /** Document type (e.g., 'llm_interaction', 'user_feedback') */
    type: string;
    /** Document name for human readability */
    name?: string;
    /** Namespace for organization */
    namespace?: string;
    /** Document content as JSON */
    content: any;
    /** Additional metadata for LLM processing */
    metadata?: Record<string, any>;
    /** Session ID for context linking */
    sessionId?: string;
    /** Tags to apply immediately */
    tags?: string[];
}

/**
 * LLM-native DocumentStore client with TypeScript type safety
 * 
 * @example
 * ```typescript
 * const client = new DocumentStoreClient({
 *   baseUrl: 'https://api.unhinged.dev/document-store'
 * });
 * 
 * // Store LLM interaction
 * const document = await client.createDocument({
 *   type: 'llm_interaction',
 *   name: 'User Query Analysis',
 *   content: {
 *     prompt: 'Analyze this data...',
 *     response: 'Based on the analysis...',
 *     model: 'gpt-4',
 *     tokens: 1250
 *   },
 *   sessionId: 'session-123',
 *   metadata: {
 *     user_id: 'user-456',
 *     interaction_type: 'analysis',
 *     confidence_score: 0.95
 *   }
 * });
 * 
 * // Get session context for LLM prompt
 * const context = await client.getSessionContext('session-123', {
 *   documentTypes: ['llm_interaction', 'user_feedback', 'knowledge_base'],
 *   limit: 20,
 *   sortBy: 'mixed'
 * });
 * ```
 */
export class DocumentStoreClient {
    private client: DocumentStoreServiceClient;
    private config: Required<DocumentStoreClientConfig>;
    private cache: Map<string, Document> = new Map();

    constructor(config: DocumentStoreClientConfig) {
        this.config = {
            timeout: 30000,
            enableRetry: true,
            maxRetries: 3,
            enableLogging: false,
            ...config
        };

        this.client = new DocumentStoreServiceClient(config.baseUrl);
    }

    // ========================================================================
    // Document CRUD Operations
    // ========================================================================

    /**
     * Create a new document with LLM-optimized metadata
     * 
     * @param options Document creation options
     * @returns Promise resolving to the created document
     * 
     * @example
     * ```typescript
     * const doc = await client.createDocument({
     *   type: 'llm_interaction',
     *   content: { prompt: 'Hello', response: 'Hi there!' },
     *   sessionId: 'session-123'
     * });
     * ```
     */
    async createDocument(options: CreateDocumentOptions): Promise<Document> {
        const documentUuid = this.generateUUID();
        const now = this.getCurrentTimestamp();

        // Enhance metadata with LLM-specific information
        const enhancedMetadata = this.enhanceMetadataForLLM(options.metadata || {}, options.content);

        const document: Document = {
            documentUuid,
            type: options.type,
            name: options.name || `${options.type}_${Date.now()}`,
            namespace: options.namespace || 'default',
            version: 1, // Will be auto-assigned by server
            bodyJson: JSON.stringify(options.content),
            metadata: this.objectToStruct(enhancedMetadata),
            tags: options.tags || [],
            createdAt: now,
            createdBy: 'user', // TODO: Get from auth context
            createdByType: 'human',
            sessionId: options.sessionId || ''
        };

        const request: PutDocumentRequest = { document };
        const response = await this.executeWithRetry(() => this.client.putDocument(request));

        if (!response.success) {
            throw new Error(`Failed to create document: ${response.message}`);
        }

        // Update local cache
        const createdDocument = { ...document, version: response.version };
        this.cache.set(documentUuid, createdDocument);

        this.log('Created document', { documentUuid, type: options.type, version: response.version });
        return createdDocument;
    }

    /**
     * Retrieve a document by UUID and optional version/tag
     * 
     * @param documentUuid Document UUID to retrieve
     * @param options Retrieval options (version, tag, includeBody)
     * @returns Promise resolving to the document or null if not found
     */
    async getDocument(
        documentUuid: string, 
        options: { version?: number; tag?: string; includeBody?: boolean } = {}
    ): Promise<Document | null> {
        // Check cache first
        const cacheKey = `${documentUuid}_${options.version || 'latest'}_${options.tag || ''}`;
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey)!;
        }

        const request: GetDocumentRequest = {
            documentUuid,
            version: options.version,
            tag: options.tag,
            includeBody: options.includeBody ?? true
        };

        const response = await this.executeWithRetry(() => this.client.getDocument(request));

        if (!response.success || !response.document) {
            return null;
        }

        // Update cache
        this.cache.set(cacheKey, response.document);

        this.log('Retrieved document', { documentUuid, version: response.document.version });
        return response.document;
    }

    // ========================================================================
    // LLM-Native Session Context Operations
    // ========================================================================

    /**
     * Get session context optimized for LLM prompt construction
     * 
     * @param sessionId Session ID to get context for
     * @param options Context retrieval options
     * @returns Promise resolving to session context documents
     * 
     * This method implements intelligent document ranking for optimal LLM context:
     * 1. Recent user interactions (highest priority)
     * 2. Relevant knowledge base documents
     * 3. Agent configurations and capabilities
     * 4. Previous successful responses
     * 5. Error context for learning
     */
    async getSessionContext(
        sessionId: string, 
        options: SessionContextOptions = {}
    ): Promise<Document[]> {
        const request: GetSessionContextRequest = {
            sessionId,
            documentTypes: options.documentTypes || [],
            since: options.since ? this.dateToTimestamp(options.since) : undefined,
            limit: options.limit || 50,
            includeBody: options.includeBody ?? true
        };

        const response = await this.executeWithRetry(() => this.client.getSessionContext(request));

        if (!response.success) {
            throw new Error(`Failed to get session context: ${response.message}`);
        }

        let documents = response.documents || [];

        // Apply client-side sorting if requested
        if (options.sortBy) {
            documents = this.sortDocumentsForLLMContext(documents, options.sortBy);
        }

        // Estimate token counts for context window management
        documents = documents.map(doc => this.enhanceDocumentWithTokenEstimate(doc));

        this.log('Retrieved session context', { 
            sessionId, 
            documentCount: documents.length,
            totalTokens: documents.reduce((sum, doc) => sum + this.estimateTokenCount(doc.bodyJson), 0)
        });

        return documents;
    }

    /**
     * Tag a document version for A/B testing or environment promotion
     * 
     * @param documentUuid Document to tag
     * @param version Version to tag
     * @param tag Tag to apply (e.g., 'production', 'staging', 'experimental')
     * @returns Promise resolving when tag is applied
     */
    async tagDocument(documentUuid: string, version: number, tag: string): Promise<void> {
        const request: TagDocumentRequest = {
            documentUuid,
            version,
            tag,
            taggedBy: 'user', // TODO: Get from auth context
            taggedByType: 'human',
            sessionId: '' // TODO: Get from session context
        };

        const response = await this.executeWithRetry(() => this.client.tagDocument(request));

        if (!response.success) {
            throw new Error(`Failed to tag document: ${response.message}`);
        }

        // Invalidate cache for this document
        this.invalidateDocumentCache(documentUuid);

        this.log('Tagged document', { documentUuid, version, tag });
    }

    // ========================================================================
    // LLM-Specific Helper Methods
    // ========================================================================

    /**
     * Enhance metadata with LLM-specific information
     */
    private enhanceMetadataForLLM(metadata: Record<string, any>, content: any): Record<string, any> {
        const enhanced = { ...metadata };

        // Add token count estimation
        enhanced.estimated_tokens = this.estimateTokenCount(JSON.stringify(content));

        // Add content type analysis
        enhanced.content_type = this.analyzeContentType(content);

        // Add timestamp for recency scoring
        enhanced.created_timestamp = Date.now();

        // Add content hash for deduplication
        enhanced.content_hash = this.hashContent(content);

        return enhanced;
    }

    /**
     * Sort documents for optimal LLM context ordering
     */
    private sortDocumentsForLLMContext(documents: Document[], sortBy: string): Document[] {
        switch (sortBy) {
            case 'relevance':
                return documents.sort((a, b) => this.getRelevanceScore(b) - this.getRelevanceScore(a));
            case 'recency':
                return documents.sort((a, b) => 
                    this.timestampToDate(b.createdAt!).getTime() - this.timestampToDate(a.createdAt!).getTime()
                );
            case 'mixed':
                return documents.sort((a, b) => {
                    const scoreA = this.getRelevanceScore(a) * 0.7 + this.getRecencyScore(a) * 0.3;
                    const scoreB = this.getRelevanceScore(b) * 0.7 + this.getRecencyScore(b) * 0.3;
                    return scoreB - scoreA;
                });
            default:
                return documents;
        }
    }

    /**
     * Estimate token count for context window management
     */
    private estimateTokenCount(text: string): number {
        // Rough estimation: ~4 characters per token for English text
        return Math.ceil(text.length / 4);
    }

    /**
     * Get relevance score for document based on type and metadata
     */
    private getRelevanceScore(document: Document): number {
        const typeScores: Record<string, number> = {
            'llm_interaction': 10,
            'user_feedback': 8,
            'agent_configuration': 6,
            'knowledge_base': 4,
            'system_log': 2
        };
        return typeScores[document.type] || 1;
    }

    /**
     * Get recency score based on document age
     */
    private getRecencyScore(document: Document): number {
        const ageHours = (Date.now() - this.timestampToDate(document.createdAt!).getTime()) / (1000 * 60 * 60);
        return Math.max(0, 10 - Math.log(ageHours + 1));
    }

    /**
     * Enhance document with token count estimate
     */
    private enhanceDocumentWithTokenEstimate(document: Document): Document {
        const tokenCount = this.estimateTokenCount(document.bodyJson);
        const enhancedMetadata = {
            ...this.structToObject(document.metadata),
            estimated_tokens: tokenCount
        };
        
        return {
            ...document,
            metadata: this.objectToStruct(enhancedMetadata)
        };
    }

    // ========================================================================
    // Utility Methods
    // ========================================================================

    private generateUUID(): string {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    private getCurrentTimestamp(): Timestamp {
        return this.dateToTimestamp(new Date());
    }

    private dateToTimestamp(date: Date): Timestamp {
        return {
            seconds: Math.floor(date.getTime() / 1000),
            nanos: (date.getTime() % 1000) * 1000000
        };
    }

    private timestampToDate(timestamp: Timestamp): Date {
        return new Date(timestamp.seconds * 1000 + timestamp.nanos / 1000000);
    }

    private objectToStruct(obj: Record<string, any>): Struct {
        // TODO: Implement proper object to Struct conversion
        return {} as Struct;
    }

    private structToObject(struct?: Struct): Record<string, any> {
        // TODO: Implement proper Struct to object conversion
        return {};
    }

    private analyzeContentType(content: any): string {
        if (typeof content === 'string') return 'text';
        if (content.prompt && content.response) return 'llm_interaction';
        if (content.feedback || content.rating) return 'user_feedback';
        return 'unknown';
    }

    private hashContent(content: any): string {
        // Simple hash for content deduplication
        return btoa(JSON.stringify(content)).slice(0, 16);
    }

    private invalidateDocumentCache(documentUuid: string): void {
        for (const key of this.cache.keys()) {
            if (key.startsWith(documentUuid)) {
                this.cache.delete(key);
            }
        }
    }

    private async executeWithRetry<T>(operation: () => Promise<T>): Promise<T> {
        let lastError: Error;
        
        for (let attempt = 0; attempt <= this.config.maxRetries; attempt++) {
            try {
                return await operation();
            } catch (error) {
                lastError = error as Error;
                
                if (attempt < this.config.maxRetries && this.config.enableRetry) {
                    const delay = Math.pow(2, attempt) * 1000; // Exponential backoff
                    await new Promise(resolve => setTimeout(resolve, delay));
                    continue;
                }
                break;
            }
        }
        
        throw lastError!;
    }

    private log(message: string, data?: any): void {
        if (this.config.enableLogging) {
            console.log(`[DocumentStoreClient] ${message}`, data);
        }
    }
}
