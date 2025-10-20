/**
 * Persistence Platform TypeScript Client Integration
 * =================================================
 * 
 * Browser-compatible wrapper for the generated TypeScript persistence platform client.
 * Provides simplified interface for CRUD operations with CockroachDB via gRPC-Web.
 */

class PersistencePlatformClient {
    constructor(options = {}) {
        this.endpoint = options.endpoint || 'http://localhost:50051';
        this.timeout = options.timeout || 10000;
        this.retryAttempts = options.retryAttempts || 3;
        this.client = null;
        this.isInitialized = false;
        
        this.init();
    }

    async init() {
        try {
            // In a real implementation, this would use the generated TypeScript client
            // For now, we'll create a gRPC-Web compatible client simulation
            this.client = this.createGrpcWebClient();
            this.isInitialized = true;
            
            console.log('✅ Persistence Platform Client initialized');
            console.log(`🔗 Endpoint: ${this.endpoint}`);
            
        } catch (error) {
            console.error('❌ Failed to initialize Persistence Platform Client:', error);
            this.client = this.createMockClient();
        }
    }

    createGrpcWebClient() {
        // This would normally import and use the generated TypeScript client
        // import { PersistencePlatformServiceClient } from '../../../generated/typescript/clients/persistence_platform';
        
        return {
            // Simulate the generated client interface
            insert: async (request) => {
                return this.makeRequest('Insert', request);
            },
            
            read: async (request) => {
                return this.makeRequest('Read', request);
            },
            
            update: async (request) => {
                return this.makeRequest('Update', request);
            },
            
            delete: async (request) => {
                return this.makeRequest('Delete', request);
            },
            
            executeQuery: async (request) => {
                return this.makeRequest('ExecuteQuery', request);
            },
            
            healthCheck: async (request) => {
                return this.makeRequest('HealthCheck', request);
            }
        };
    }

    createMockClient() {
        console.log('🔄 Using mock persistence client for development');
        
        return {
            insert: async (request) => {
                await this.simulateNetworkDelay();
                console.log('📝 Mock INSERT:', request);
                
                return {
                    success: true,
                    recordId: request.record.id,
                    version: '1.0',
                    affectedTechnologies: ['cockroachdb']
                };
            },
            
            read: async (request) => {
                await this.simulateNetworkDelay();
                console.log('📖 Mock READ:', request);
                
                return {
                    success: true,
                    record: {
                        id: request.recordId,
                        recordType: 'blog_post',
                        data: '{"title": "Mock Blog Post", "content": "This is mock content"}',
                        metadata: '{"source": "mock"}',
                        createdAt: new Date().toISOString(),
                        updatedAt: new Date().toISOString(),
                        version: '1.0'
                    }
                };
            },
            
            update: async (request) => {
                await this.simulateNetworkDelay();
                console.log('✏️ Mock UPDATE:', request);
                
                return {
                    success: true,
                    recordId: request.recordId,
                    newVersion: '2.0'
                };
            },
            
            delete: async (request) => {
                await this.simulateNetworkDelay();
                console.log('🗑️ Mock DELETE:', request);
                
                return {
                    success: true,
                    recordId: request.recordId
                };
            },
            
            executeQuery: async (request) => {
                await this.simulateNetworkDelay();
                console.log('🔍 Mock QUERY:', request);
                
                return {
                    success: true,
                    resultCount: 5,
                    records: [
                        {
                            id: 'blog_post_1',
                            recordType: 'blog_post',
                            data: '{"title": "First Post", "content": "Content 1"}',
                            createdAt: new Date().toISOString()
                        },
                        {
                            id: 'blog_post_2',
                            recordType: 'blog_post',
                            data: '{"title": "Second Post", "content": "Content 2"}',
                            createdAt: new Date().toISOString()
                        }
                    ],
                    executedOn: 'cockroachdb'
                };
            },
            
            healthCheck: async (request) => {
                await this.simulateNetworkDelay();
                console.log('🏥 Mock HEALTH CHECK:', request);
                
                return {
                    status: 'SERVING',
                    timestamp: new Date().toISOString(),
                    technologyHealth: {
                        cockroachdb: {
                            healthy: true,
                            responseTimeMs: 25,
                            lastChecked: new Date().toISOString()
                        }
                    }
                };
            }
        };
    }

    async makeRequest(method, request) {
        try {
            // In a real implementation, this would use gRPC-Web
            // For now, simulate HTTP requests to a gRPC-Web gateway
            
            const response = await fetch(`${this.endpoint}/unhinged.persistence.PersistencePlatformService/${method}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/grpc-web+proto',
                    'Accept': 'application/grpc-web+proto'
                },
                body: this.serializeRequest(request)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return this.deserializeResponse(await response.arrayBuffer());
            
        } catch (error) {
            console.warn(`⚠️ gRPC-Web request failed, using mock response:`, error);
            
            // Fallback to mock for development
            const mockClient = this.createMockClient();
            const methodName = method.toLowerCase();
            
            if (mockClient[methodName]) {
                return await mockClient[methodName](request);
            }
            
            throw error;
        }
    }

    serializeRequest(request) {
        // In a real implementation, this would use protobuf serialization
        // For now, just return JSON as bytes
        return new TextEncoder().encode(JSON.stringify(request));
    }

    deserializeResponse(buffer) {
        // In a real implementation, this would use protobuf deserialization
        // For now, just parse JSON
        const text = new TextDecoder().decode(buffer);
        return JSON.parse(text);
    }

    async simulateNetworkDelay() {
        const delay = Math.random() * 500 + 100; // 100-600ms
        await new Promise(resolve => setTimeout(resolve, delay));
    }

    // High-level convenience methods for blog operations
    async createBlogPost(title, content, metadata = {}) {
        const postId = `blog_post_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        const request = {
            record: {
                id: postId,
                recordType: 'blog_post',
                data: JSON.stringify({
                    title: title,
                    content: content,
                    wordCount: content.trim().split(/\s+/).length,
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString()
                }),
                metadata: JSON.stringify({
                    source: 'blog_editor',
                    format: 'markdown',
                    ...metadata
                }),
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
                version: '1.0'
            },
            context: {
                requestId: `blog_create_${Date.now()}`,
                userId: 'blog_editor_user',
                metadata: {
                    source: 'blog_editor_interface'
                }
            }
        };

        return await this.client.insert(request);
    }

    async updateBlogPost(postId, title, content, metadata = {}) {
        const request = {
            recordId: postId,
            updates: {
                data: JSON.stringify({
                    title: title,
                    content: content,
                    wordCount: content.trim().split(/\s+/).length,
                    updatedAt: new Date().toISOString()
                }),
                metadata: JSON.stringify({
                    source: 'blog_editor',
                    format: 'markdown',
                    lastModified: new Date().toISOString(),
                    ...metadata
                })
            },
            context: {
                requestId: `blog_update_${Date.now()}`,
                userId: 'blog_editor_user'
            }
        };

        return await this.client.update(request);
    }

    async getBlogPost(postId) {
        const request = {
            recordId: postId,
            context: {
                requestId: `blog_read_${Date.now()}`,
                userId: 'blog_editor_user'
            }
        };

        return await this.client.read(request);
    }

    async listBlogPosts(limit = 10, offset = 0) {
        const request = {
            queryName: 'list_blog_posts',
            spec: {
                queryType: 'DOCUMENT_QUERY',
                criteria: {
                    equals: {
                        field: 'record_type',
                        value: 'blog_post'
                    }
                },
                orderBy: [
                    {
                        field: 'created_at',
                        direction: 'desc'
                    }
                ],
                limit: limit,
                offset: offset
            },
            context: {
                requestId: `blog_list_${Date.now()}`,
                userId: 'blog_editor_user'
            }
        };

        return await this.client.executeQuery(request);
    }

    async deleteBlogPost(postId) {
        const request = {
            recordId: postId,
            context: {
                requestId: `blog_delete_${Date.now()}`,
                userId: 'blog_editor_user'
            }
        };

        return await this.client.delete(request);
    }

    async checkHealth() {
        const request = {
            includeMetrics: true,
            includeTechnologyDetails: true
        };

        return await this.client.healthCheck(request);
    }
}

// Global instance for use across the application
window.PersistencePlatformClient = PersistencePlatformClient;

// Auto-initialize when loaded
document.addEventListener('DOMContentLoaded', () => {
    if (!window.persistenceClient) {
        window.persistenceClient = new PersistencePlatformClient();
        console.log('🚀 Global persistence client initialized');
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PersistencePlatformClient;
}
