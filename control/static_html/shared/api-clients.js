/**
 * Unhinged Proto Client Registry
 * Auto-generated client registry for browser consumption
 * Generated at: 1760935426.8367877
 */

class UnhingedProtoClientRegistry {
    constructor() {
        this.clients = new Map();
        this.serviceEndpoints = {
            'persistence': 'http://localhost:8090',
            'audio': 'http://localhost:8000',
            'vision': 'http://localhost:8001',
            'context': 'http://localhost:8002'
        };
    }

    /**
     * Get or create a service client
     */
    getClient(serviceName, options = {}) {
        if (this.clients.has(serviceName)) {
            return this.clients.get(serviceName);
        }

        const client = this._createServiceClient(serviceName, options);
        this.clients.set(serviceName, client);
        return client;
    }

    /**
     * Create service client instance
     */
    _createServiceClient(serviceName, options) {
        const endpoint = options.endpoint || this.serviceEndpoints[serviceName];
        
        return {
            serviceName,
            endpoint,
            
            async call(method, request) {
                const response = await fetch(`${endpoint}/${method}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(request)
                });
                
                return await response.json();
            }
        };
    }
}

// Global registry instance
window.UnhingedClients = new UnhingedProtoClientRegistry();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UnhingedProtoClientRegistry;
}
