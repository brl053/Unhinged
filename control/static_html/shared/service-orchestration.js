/**
 * Service Orchestration Logic
 * Manages service tiers, dependencies, and real-time status monitoring
 */

class ServiceOrchestrator {
    constructor() {
        this.dagEndpoint = 'http://localhost:9000';
        this.updateInterval = 3000; // 3 seconds
        this.serviceStatus = {};
        this.resourceUsage = {};
        this.isMonitoring = false;
    }

    /**
     * Initialize the orchestrator
     */
    async init() {
        await this.loadServiceStatus();
        this.renderServiceTiers();
        this.startMonitoring();
        this.bindEventHandlers();
    }

    /**
     * Load current service status from Docker
     */
    async loadServiceStatus() {
        try {
            const response = await fetch(`${this.dagEndpoint}/api/docker/status`);
            if (response.ok) {
                this.serviceStatus = await response.json();
            } else {
                // Fallback: check individual services
                await this.checkIndividualServices();
            }
        } catch (error) {
            console.warn('Failed to load service status from DAG, checking individually:', error);
            await this.checkIndividualServices();
        }
    }

    /**
     * Check individual service health
     */
    async checkIndividualServices() {
        for (const [serviceId, service] of Object.entries(SERVICE_DEFINITIONS)) {
            try {
                const url = `http://localhost:${service.port}${service.health_path || '/health'}`;
                const response = await fetch(url, { 
                    method: 'GET',
                    timeout: 2000 
                });
                this.serviceStatus[serviceId] = {
                    status: response.ok ? 'running' : 'unhealthy',
                    container: service.container,
                    port: service.port
                };
            } catch (error) {
                this.serviceStatus[serviceId] = {
                    status: 'stopped',
                    container: service.container,
                    port: service.port
                };
            }
        }
    }

    /**
     * Toggle an entire service tier
     */
    async toggleServiceTier(tierId) {
        const tier = SERVICE_TIERS[tierId];
        if (!tier) return;

        const isRunning = this.isTierRunning(tierId);
        const button = document.querySelector(`[data-tier="${tierId}"]`);
        
        if (button) {
            button.disabled = true;
            button.textContent = isRunning ? 'Stopping...' : 'Starting...';
        }

        try {
            if (isRunning) {
                await this.stopTier(tierId);
            } else {
                await this.startTier(tierId);
            }
        } catch (error) {
            console.error(`Failed to toggle tier ${tierId}:`, error);
            this.showNotification(`Failed to ${isRunning ? 'stop' : 'start'} ${tier.name}`, 'error');
        } finally {
            if (button) {
                button.disabled = false;
                this.updateTierButton(tierId);
            }
        }
    }

    /**
     * Start a service tier
     */
    async startTier(tierId) {
        const tier = SERVICE_TIERS[tierId];
        
        // Check dependencies first
        if (tier.depends_on) {
            for (const depTier of tier.depends_on) {
                if (!this.isTierRunning(depTier)) {
                    throw new Error(`Dependency ${SERVICE_TIERS[depTier].name} is not running`);
                }
            }
        }

        // Execute via DAG control plane
        const response = await fetch(`${this.dagEndpoint}/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                target: `start-${tierId}-services`,
                human_approval: false
            })
        });

        if (!response.ok) {
            throw new Error(`Failed to start ${tier.name}`);
        }

        this.showNotification(`${tier.name} services starting...`, 'info');
    }

    /**
     * Stop a service tier
     */
    async stopTier(tierId) {
        const tier = SERVICE_TIERS[tierId];
        
        // Check if other tiers depend on this one
        const dependentTiers = Object.entries(SERVICE_TIERS)
            .filter(([_, t]) => t.depends_on && t.depends_on.includes(tierId))
            .map(([id, _]) => id);

        if (dependentTiers.length > 0) {
            const runningDependents = dependentTiers.filter(id => this.isTierRunning(id));
            if (runningDependents.length > 0) {
                const names = runningDependents.map(id => SERVICE_TIERS[id].name).join(', ');
                throw new Error(`Cannot stop ${tier.name}: ${names} depend on it`);
            }
        }

        // Stop services
        const response = await fetch(`${this.dagEndpoint}/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                target: `stop-${tierId}-services`,
                human_approval: false
            })
        });

        if (!response.ok) {
            throw new Error(`Failed to stop ${tier.name}`);
        }

        this.showNotification(`${tier.name} services stopping...`, 'info');
    }

    /**
     * Check if a tier is running
     */
    isTierRunning(tierId) {
        const tier = SERVICE_TIERS[tierId];
        if (!tier) return false;

        return tier.services.some(serviceId => {
            const status = this.serviceStatus[serviceId];
            return status && status.status === 'running';
        });
    }

    /**
     * Get tier health status
     */
    getTierHealth(tierId) {
        const tier = SERVICE_TIERS[tierId];
        if (!tier) return 'unknown';

        const statuses = tier.services.map(serviceId => {
            const status = this.serviceStatus[serviceId];
            return status ? status.status : 'unknown';
        });

        if (statuses.every(s => s === 'running')) return 'healthy';
        if (statuses.every(s => s === 'stopped')) return 'stopped';
        if (statuses.some(s => s === 'unhealthy')) return 'unhealthy';
        return 'partial';
    }

    /**
     * Render service tiers UI
     */
    renderServiceTiers() {
        const container = document.getElementById('service-tiers');
        if (!container) return;

        container.innerHTML = '';

        Object.entries(SERVICE_TIERS).forEach(([tierId, tier]) => {
            const tierElement = this.createTierElement(tierId, tier);
            container.appendChild(tierElement);
        });
    }

    /**
     * Create a tier UI element
     */
    createTierElement(tierId, tier) {
        const tierDiv = document.createElement('div');
        tierDiv.className = `tier tier-${tierId}`;
        tierDiv.innerHTML = `
            <div class="tier-header">
                <div class="tier-info">
                    <h3>${tier.icon} ${tier.name}</h3>
                    <p class="tier-description">${tier.description}</p>
                </div>
                <div class="tier-controls">
                    <div class="tier-status" data-tier-status="${tierId}">
                        <span class="status-indicator"></span>
                        <span class="status-text">Checking...</span>
                    </div>
                    <button class="tier-toggle" data-tier="${tierId}">
                        Toggle
                    </button>
                </div>
            </div>
            <div class="services-grid" data-services="${tierId}">
                ${tier.services.map(serviceId => this.createServiceElement(serviceId)).join('')}
            </div>
        `;

        return tierDiv;
    }

    /**
     * Create a service UI element
     */
    createServiceElement(serviceId) {
        const service = SERVICE_DEFINITIONS[serviceId];
        if (!service) return '';

        return `
            <div class="service-card" data-service="${serviceId}">
                <div class="service-header">
                    <h4>${service.name}</h4>
                    <span class="service-status" data-service-status="${serviceId}">
                        <span class="status-indicator"></span>
                    </span>
                </div>
                <p class="service-description">${service.description}</p>
                <div class="service-details">
                    <span class="service-port">:${service.port}</span>
                    <span class="service-container">${service.container}</span>
                </div>
            </div>
        `;
    }

    /**
     * Update tier button state
     */
    updateTierButton(tierId) {
        const button = document.querySelector(`[data-tier="${tierId}"]`);
        const statusElement = document.querySelector(`[data-tier-status="${tierId}"]`);
        
        if (!button || !statusElement) return;

        const health = this.getTierHealth(tierId);
        const isRunning = this.isTierRunning(tierId);

        // Update button
        button.textContent = isRunning ? 'Stop' : 'Start';
        button.className = `tier-toggle ${isRunning ? 'stop' : 'start'}`;

        // Update status
        const statusText = statusElement.querySelector('.status-text');
        const statusIndicator = statusElement.querySelector('.status-indicator');
        
        statusText.textContent = this.getHealthText(health);
        statusIndicator.className = `status-indicator status-${health}`;
    }

    /**
     * Get human-readable health text
     */
    getHealthText(health) {
        const texts = {
            'healthy': 'All services running',
            'partial': 'Some services running',
            'unhealthy': 'Services unhealthy',
            'stopped': 'All services stopped',
            'unknown': 'Status unknown'
        };
        return texts[health] || 'Unknown';
    }

    /**
     * Update all UI elements
     */
    updateUI() {
        // Update tier buttons and status
        Object.keys(SERVICE_TIERS).forEach(tierId => {
            this.updateTierButton(tierId);
        });

        // Update individual service status
        Object.keys(SERVICE_DEFINITIONS).forEach(serviceId => {
            this.updateServiceStatus(serviceId);
        });
    }

    /**
     * Update individual service status
     */
    updateServiceStatus(serviceId) {
        const statusElement = document.querySelector(`[data-service-status="${serviceId}"]`);
        if (!statusElement) return;

        const status = this.serviceStatus[serviceId];
        const indicator = statusElement.querySelector('.status-indicator');
        
        if (status) {
            indicator.className = `status-indicator status-${status.status}`;
            indicator.title = `${status.status} (${status.container})`;
        } else {
            indicator.className = 'status-indicator status-unknown';
            indicator.title = 'Status unknown';
        }
    }

    /**
     * Start monitoring services
     */
    startMonitoring() {
        if (this.isMonitoring) return;
        
        this.isMonitoring = true;
        this.monitoringInterval = setInterval(async () => {
            await this.loadServiceStatus();
            this.updateUI();
        }, this.updateInterval);
    }

    /**
     * Stop monitoring services
     */
    stopMonitoring() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.isMonitoring = false;
        }
    }

    /**
     * Bind event handlers
     */
    bindEventHandlers() {
        // Tier toggle buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-tier]')) {
                const tierId = e.target.dataset.tier;
                this.toggleServiceTier(tierId);
            }
        });

        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            this.stopMonitoring();
        });
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        // Simple notification - could be enhanced with a proper notification system
        console.log(`[${type.toUpperCase()}] ${message}`);
        
        // You could add a toast notification here
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.serviceOrchestrator = new ServiceOrchestrator();
    window.serviceOrchestrator.init();
});
