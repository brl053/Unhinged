/**
 * API Integration for Tab System
 * Connects generated proto clients with the tab-based control plane
 * 
 * @llm-type integration
 * @llm-legend API client integration layer for tab system service communication
 * @llm-key Provides seamless gRPC service access within tab-based browser interface
 * @llm-map Bridges generated proto clients with TabSystem for real service calls
 * @llm-axiom All service communication must be type-safe and error-handled
 * @llm-contract Provides unified API access through tab system integration
 * @llm-token api-tab-integration: Service client integration for tab-based control plane
 */

class APITabIntegration {
    constructor() {
        this.initialized = false;
        this.serviceClients = new Map();
        this.connectionStatus = new Map();
        this.retryAttempts = new Map();
        this.maxRetries = 3;
        
        // Service endpoint configuration
        this.endpoints = {
            chat: 'http://localhost:8080',
            llm: 'http://localhost:8080',
            vision: 'http://localhost:8080', 
            audio: 'http://localhost:8080',
            document_store: 'http://localhost:8080',
            cdc: 'http://localhost:8080'
        };
    }
    
    /**
     * Initialize API integration with tab system
     */
    async initialize() {
        if (this.initialized) return;
        
        try {
            // Wait for API registry to be available
            await this.waitForAPIRegistry();
            
            // Initialize service connections
            await this.initializeServiceConnections();
            
            // Integrate with tab system
            this.integrateWithTabSystem();
            
            // Start health monitoring
            this.startHealthMonitoring();
            
            this.initialized = true;
            console.log('✅ API Tab Integration initialized successfully');
            
        } catch (error) {
            console.error('❌ Failed to initialize API integration:', error);
            throw error;
        }
    }
    
    /**
     * Wait for API registry to be loaded
     */
    async waitForAPIRegistry() {
        return new Promise((resolve, reject) => {
            const checkRegistry = () => {
                if (window.UnhingedAPI) {
                    resolve();
                } else {
                    setTimeout(checkRegistry, 100);
                }
            };
            
            checkRegistry();
            
            // Timeout after 10 seconds
            setTimeout(() => {
                if (!window.UnhingedAPI) {
                    reject(new Error('API registry not loaded within timeout'));
                }
            }, 10000);
        });
    }
    
    /**
     * Initialize connections to all available services
     */
    async initializeServiceConnections() {
        const services = window.UnhingedAPI.getAvailableServices();
        
        for (const serviceName of services) {
            try {
                const client = window.UnhingedAPI.getClient(serviceName);
                this.serviceClients.set(serviceName, client);
                this.connectionStatus.set(serviceName, 'connected');
                this.retryAttempts.set(serviceName, 0);
                
                console.log(`✅ Connected to ${serviceName} service`);
                
            } catch (error) {
                console.warn(`⚠️ Failed to connect to ${serviceName}:`, error);
                this.connectionStatus.set(serviceName, 'disconnected');
            }
        }
    }
    
    /**
     * Integrate API clients with tab system
     */
    integrateWithTabSystem() {
        if (!window.UnhingedComponents || !window.UnhingedComponents.TabSystem) {
            console.warn('TabSystem not available for API integration');
            return;
        }
        
        // Extend TabSystem prototype with API methods
        const TabSystemProto = window.UnhingedComponents.TabSystem.prototype;
        
        // Add service client access method
        TabSystemProto.getServiceClient = (serviceName) => {
            return this.getServiceClient(serviceName);
        };
        
        // Add service call method with error handling
        TabSystemProto.callService = async (serviceName, methodName, request = {}) => {
            return await this.callService(serviceName, methodName, request);
        };
        
        // Add service health check method
        TabSystemProto.checkServiceHealth = (serviceName) => {
            return this.getServiceHealth(serviceName);
        };
        
        // Add batch service call method
        TabSystemProto.callServices = async (calls) => {
            return await this.batchServiceCalls(calls);
        };
        
        console.log('✅ TabSystem extended with API integration methods');
    }
    
    /**
     * Get service client with connection validation
     */
    getServiceClient(serviceName) {
        if (!this.serviceClients.has(serviceName)) {
            throw new Error(`Service '${serviceName}' not available`);
        }
        
        const status = this.connectionStatus.get(serviceName);
        if (status !== 'connected') {
            throw new Error(`Service '${serviceName}' is ${status}`);
        }
        
        return this.serviceClients.get(serviceName);
    }
    
    /**
     * Call service method with retry logic and error handling
     */
    async callService(serviceName, methodName, request = {}) {
        const maxRetries = this.maxRetries;
        let lastError;
        
        for (let attempt = 0; attempt <= maxRetries; attempt++) {
            try {
                const client = this.getServiceClient(serviceName);
                const response = await client.call(methodName, request);
                
                // Reset retry count on success
                this.retryAttempts.set(serviceName, 0);
                this.connectionStatus.set(serviceName, 'connected');
                
                return response;
                
            } catch (error) {
                lastError = error;
                
                if (attempt < maxRetries) {
                    console.warn(`Retry ${attempt + 1}/${maxRetries} for ${serviceName}.${methodName}:`, error);
                    
                    // Exponential backoff
                    const delay = Math.pow(2, attempt) * 1000;
                    await new Promise(resolve => setTimeout(resolve, delay));
                    
                    // Try to reconnect
                    await this.reconnectService(serviceName);
                } else {
                    this.connectionStatus.set(serviceName, 'error');
                    this.retryAttempts.set(serviceName, attempt);
                }
            }
        }
        
        throw new Error(`Service call failed after ${maxRetries} retries: ${lastError.message}`);
    }
    
    /**
     * Batch service calls with parallel execution
     */
    async batchServiceCalls(calls) {
        const promises = calls.map(async (call) => {
            try {
                const result = await this.callService(call.service, call.method, call.request);
                return { success: true, result, call };
            } catch (error) {
                return { success: false, error: error.message, call };
            }
        });
        
        return await Promise.all(promises);
    }
    
    /**
     * Get service health status
     */
    getServiceHealth(serviceName) {
        return {
            status: this.connectionStatus.get(serviceName) || 'unknown',
            retryAttempts: this.retryAttempts.get(serviceName) || 0,
            lastCheck: new Date().toISOString()
        };
    }
    
    /**
     * Attempt to reconnect to a service
     */
    async reconnectService(serviceName) {
        try {
            const client = window.UnhingedAPI.getClient(serviceName, { 
                endpoint: this.endpoints[serviceName] 
            });
            
            this.serviceClients.set(serviceName, client);
            this.connectionStatus.set(serviceName, 'connected');
            
            console.log(`✅ Reconnected to ${serviceName} service`);
            
        } catch (error) {
            console.warn(`Failed to reconnect to ${serviceName}:`, error);
            this.connectionStatus.set(serviceName, 'disconnected');
        }
    }
    
    /**
     * Start periodic health monitoring
     */
    startHealthMonitoring() {
        setInterval(async () => {
            for (const [serviceName, client] of this.serviceClients) {
                try {
                    // Try a simple health check call
                    await client.call('GetHealth', {});
                    this.connectionStatus.set(serviceName, 'connected');
                } catch (error) {
                    if (this.connectionStatus.get(serviceName) === 'connected') {
                        console.warn(`Service ${serviceName} health check failed:`, error);
                        this.connectionStatus.set(serviceName, 'degraded');
                    }
                }
            }
        }, 30000); // Check every 30 seconds
    }
    
    /**
     * Get overall system health
     */
    getSystemHealth() {
        const services = Array.from(this.connectionStatus.entries()).map(([name, status]) => ({
            name,
            status,
            retryAttempts: this.retryAttempts.get(name) || 0
        }));
        
        const healthyCount = services.filter(s => s.status === 'connected').length;
        const totalCount = services.length;
        
        return {
            overall: healthyCount === totalCount ? 'healthy' : 'degraded',
            healthyServices: healthyCount,
            totalServices: totalCount,
            services
        };
    }
}

// Global instance
window.APITabIntegration = new APITabIntegration();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.APITabIntegration.initialize().catch(console.error);
    });
} else {
    window.APITabIntegration.initialize().catch(console.error);
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APITabIntegration;
}
