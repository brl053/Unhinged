// ============================================================================
// Unhinged Health Dashboard JavaScript
// ============================================================================

class UnhingedDashboard {
    constructor() {
        this.services = {
            backend: { url: 'http://localhost:8080/health', port: 8080 },
            'vision-ai': { url: 'http://localhost:8001/health', port: 8001 },
            'whisper-tts': { url: 'http://localhost:8000/health', port: 8000 },
            'context-llm': { url: 'http://localhost:8002/health', port: 8002 },
            grafana: { url: 'http://localhost:3001/api/health', port: 3001 },
            prometheus: { url: 'http://localhost:9090/-/healthy', port: 9090 },
            loki: { url: 'http://localhost:3100/ready', port: 3100 }
        };
        
        this.autoRefreshInterval = null;
        this.init();
    }

    init() {
        this.updateTimestamp();
        this.setupAutoRefresh();
        this.refreshAll();
        
        // Setup event listeners
        document.getElementById('autoRefresh').addEventListener('change', (e) => {
            if (e.target.checked) {
                this.setupAutoRefresh();
            } else {
                this.clearAutoRefresh();
            }
        });
    }

    updateTimestamp() {
        const now = new Date().toLocaleString();
        document.getElementById('lastUpdate').textContent = `Last Update: ${now}`;
        document.getElementById('footerTimestamp').textContent = now;
    }

    setupAutoRefresh() {
        this.clearAutoRefresh();
        this.autoRefreshInterval = setInterval(() => {
            this.refreshAll();
        }, 30000); // 30 seconds
    }

    clearAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }

    async refreshAll() {
        this.updateTimestamp();
        
        // Check all services
        const servicePromises = Object.keys(this.services).map(service => 
            this.checkService(service)
        );
        
        await Promise.allSettled(servicePromises);
        
        // Update overall status
        this.updateOverallStatus();
    }

    async checkService(serviceName) {
        const service = this.services[serviceName];
        if (!service) return;

        const statusElement = document.getElementById(`${serviceName}-status`);
        
        if (statusElement) {
            statusElement.textContent = 'Checking...';
            statusElement.className = 'status-badge checking';
        }

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
            
            const response = await fetch(service.url, {
                method: 'GET',
                signal: controller.signal,
                mode: 'cors'
            });
            
            clearTimeout(timeoutId);
            
            if (response.ok) {
                const data = await response.json().catch(() => ({}));
                this.updateServiceStatus(serviceName, 'online', data);
            } else {
                this.updateServiceStatus(serviceName, 'degraded', { error: `HTTP ${response.status}` });
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                this.updateServiceStatus(serviceName, 'offline', { error: 'Timeout' });
            } else {
                this.updateServiceStatus(serviceName, 'offline', { error: error.message });
            }
        }
    }

    updateServiceStatus(serviceName, status, data = {}) {
        const statusElement = document.getElementById(`${serviceName}-status`);
        
        if (statusElement) {
            statusElement.className = `status-badge ${status}`;
            statusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        }

        // Update service-specific details
        this.updateServiceDetails(serviceName, status, data);
    }

    updateServiceDetails(serviceName, status, data) {
        switch (serviceName) {
            case 'backend':
                this.updateElement(`${serviceName}-health`, data.status || 'Unknown');
                this.updateElement(`${serviceName}-response`, status === 'online' ? 'OK' : 'Failed');
                break;
                
            case 'vision-ai':
                this.updateElement(`${serviceName}-gpu`, data.gpu_available || 'Unknown');
                this.updateElement(`${serviceName}-model`, data.model_status || 'Unknown');
                break;
                
            case 'whisper-tts':
                this.updateElement(`${serviceName}-model`, data.model_status || 'Unknown');
                this.updateElement(`${serviceName}-audio`, data.audio_capabilities || 'Unknown');
                break;
                
            case 'context-llm':
                this.updateElement(`${serviceName}-health`, data.status || 'Unknown');
                this.updateElement(`${serviceName}-context`, data.context_status || 'Unknown');
                break;
                
            case 'grafana':
                this.updateElement(`${serviceName}-version`, data.version || 'Unknown');
                this.updateElement(`${serviceName}-db`, data.database || 'Unknown');
                break;
                
            case 'prometheus':
                this.updatePrometheusDetails();
                break;
                
            case 'loki':
                this.updateElement(`${serviceName}-ready`, status === 'online' ? 'Ready' : 'Not Ready');
                this.updateElement(`${serviceName}-logs`, 'Available');
                break;
        }
    }

    async updatePrometheusDetails() {
        try {
            const targetsResponse = await fetch('http://localhost:9090/api/v1/targets');
            if (targetsResponse.ok) {
                const targetsData = await targetsResponse.json();
                const activeTargets = targetsData.data?.activeTargets || [];
                const healthyTargets = activeTargets.filter(t => t.health === 'up').length;
                this.updateElement('prometheus-targets', `${healthyTargets}/${activeTargets.length}`);
            }
        } catch (error) {
            this.updateElement('prometheus-targets', 'Unknown');
        }
        
        this.updateElement('prometheus-metrics', 'Collecting');
    }

    updateElement(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    updateOverallStatus() {
        const statusElements = document.querySelectorAll('.status-badge');
        let totalServices = 0;
        let healthyServices = 0;
        let degradedServices = 0;
        
        statusElements.forEach(element => {
            if (element.id.endsWith('-status')) {
                totalServices++;
                if (element.classList.contains('online')) {
                    healthyServices++;
                } else if (element.classList.contains('degraded')) {
                    degradedServices++;
                }
            }
        });
        
        const overallIndicator = document.getElementById('overallIndicator');
        const statusSummary = document.getElementById('statusSummary');
        
        let overallStatus = 'healthy';
        if (healthyServices === 0) {
            overallStatus = 'unhealthy';
        } else if (degradedServices > 0 || healthyServices < totalServices) {
            overallStatus = 'degraded';
        }
        
        if (overallIndicator) {
            const statusText = overallIndicator.querySelector('.status-text');
            if (statusText) {
                statusText.textContent = overallStatus.charAt(0).toUpperCase() + overallStatus.slice(1);
                statusText.className = `status-text status-${overallStatus}`;
            }
        }
        
        if (statusSummary) {
            statusSummary.innerHTML = `
                <span class="services-count">Services: ${healthyServices}/${totalServices} healthy</span>
            `;
        }
    }

    async testChatEndpoint() {
        try {
            const response = await fetch('http://localhost:8080/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: 'Dashboard health test'
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                alert(`✅ Chat endpoint test successful!\n\nResponse: ${data.response?.substring(0, 100)}...`);
            } else {
                alert(`❌ Chat endpoint test failed!\n\nStatus: ${response.status}`);
            }
        } catch (error) {
            alert(`❌ Chat endpoint test failed!\n\nError: ${error.message}`);
        }
    }

    async checkMetrics() {
        try {
            const response = await fetch('http://localhost:8080/metrics');
            if (response.ok) {
                const metrics = await response.text();
                const lines = metrics.split('\n').length;
                alert(`✅ Metrics endpoint accessible!\n\nTotal metrics lines: ${lines}\n\nSample metrics available for Prometheus collection.`);
            } else {
                alert(`❌ Metrics endpoint failed!\n\nStatus: ${response.status}`);
            }
        } catch (error) {
            alert(`❌ Metrics endpoint failed!\n\nError: ${error.message}`);
        }
    }

    runHealthScript() {
        alert(`🏥 Health Check Script\n\nTo run the comprehensive health check script, execute:\n\n./scripts/health-check.sh\n\nOr for specific services:\n./scripts/health-check.sh --service backend\n./scripts/health-check.sh --service observability`);
    }

    viewLogs() {
        const logCommands = `
📋 View Recent Logs

Backend Logs:
docker logs unhinged-backend --tail 50

Vision AI Logs:
docker logs vision-ai-service --tail 50

Whisper TTS Logs:
docker logs whisper-tts-service --tail 50

Grafana Logs:
docker logs unhinged-grafana --tail 50

All Container Status:
docker ps --format "table {{.Names}}\\t{{.Status}}"
        `;
        alert(logCommands);
    }
}

// Global functions for HTML onclick handlers
function refreshAll() {
    dashboard.refreshAll();
}

function checkService(serviceName) {
    dashboard.checkService(serviceName);
}

function testChatEndpoint() {
    dashboard.testChatEndpoint();
}

function checkMetrics() {
    dashboard.checkMetrics();
}

function runHealthScript() {
    dashboard.runHealthScript();
}

function viewLogs() {
    dashboard.viewLogs();
}

// Initialize dashboard when page loads
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new UnhingedDashboard();
});
