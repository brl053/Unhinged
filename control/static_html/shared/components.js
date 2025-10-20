/**
 * Unhinged Component Library - DRY Reusable Components
 * Provides consistent UI components across all static HTML interfaces
 * Enhanced with accessibility and keyboard navigation
 */

class UnhingedComponents {

    /**
     * Keyboard Navigation Manager
     * Provides consistent keyboard navigation across all interfaces
     */
    static KeyboardManager = class {
        static init() {
            // Global keyboard shortcuts
            document.addEventListener('keydown', this.handleGlobalShortcuts.bind(this));

            // Enhanced focus management
            this.setupFocusTrapping();
            this.setupSkipLinks();

            // Escape key handling for modals/overlays
            this.setupEscapeHandling();
        }

        static handleGlobalShortcuts(event) {
            // Alt + H: Go to home/mission control
            if (event.altKey && event.key === 'h') {
                event.preventDefault();
                window.location.href = 'index.html';
            }



            // Alt + S: Go to service orchestration
            if (event.altKey && event.key === 's') {
                event.preventDefault();
                window.location.href = 'service-orchestration.html';
            }
        }

        static setupSkipLinks() {
            // Add skip to main content link
            const skipLink = document.createElement('a');
            skipLink.href = '#main-content';
            skipLink.textContent = 'Skip to main content';
            skipLink.className = 'skip-link';
            skipLink.style.cssText = `
                position: absolute;
                top: -40px;
                left: 6px;
                background: var(--color-primary, #007bff);
                color: white;
                padding: 8px;
                text-decoration: none;
                border-radius: 4px;
                z-index: 1000;
                transition: top 0.3s;
            `;

            skipLink.addEventListener('focus', () => {
                skipLink.style.top = '6px';
            });

            skipLink.addEventListener('blur', () => {
                skipLink.style.top = '-40px';
            });

            document.body.insertBefore(skipLink, document.body.firstChild);
        }

        static setupEscapeHandling() {
            document.addEventListener('keydown', (event) => {
                if (event.key === 'Escape') {
                    const activeElement = document.activeElement;
                    if (activeElement && activeElement.blur) {
                        activeElement.blur();
                    }
                }
            });
        }

        static enhanceButtonAccessibility(button) {
            // Ensure proper ARIA attributes
            if (!button.getAttribute('role') && button.tagName !== 'BUTTON') {
                button.setAttribute('role', 'button');
            }

            // Add keyboard support for non-button elements
            if (button.tagName !== 'BUTTON' && button.tagName !== 'INPUT') {
                button.setAttribute('tabindex', '0');
                button.addEventListener('keydown', (event) => {
                    if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault();
                        button.click();
                    }
                });
            }

            // Ensure minimum touch target size
            const computedStyle = window.getComputedStyle(button);
            const minSize = 44; // pixels
            if (parseInt(computedStyle.height) < minSize) {
                button.style.minHeight = `${minSize}px`;
            }
        }
    };
    
    /**
     * Navigation Component - Consistent navigation across all interfaces
     */
    static NavigationComponent = class {
        static render(activePage = '') {
            const navItems = [
                { id: 'index', href: 'index.html', icon: '🎛️', label: 'Mission Control' },
                { id: 'blog-list', href: 'blog-list.html', icon: '📚', label: 'Blog Posts' },
                { id: 'blog-editor', href: 'blog-editor.html', icon: '✍️', label: 'Blog Editor' },
                { id: 'persistence', href: 'persistence-platform.html', icon: '💾', label: 'Persistence Platform' },
                { id: 'toc', href: 'table-of-contents.html', icon: '📚', label: 'Table of Contents' },
                { id: 'validator', href: 'validate-standardization.html', icon: '🔍', label: 'Validator' },
                { id: 'test', href: 'test-blog-integration.html', icon: '🧪', label: 'Blog Integration Test' }
            ];

            const navHTML = navItems.map(item => {
                const isActive = activePage === item.id;
                return `<a href="${item.href}" class="nav-link ${isActive ? 'active' : ''}">${item.icon} ${item.label}</a>`;
            }).join('');

            return `
            <div class="navigation">
                ${navHTML}
            </div>`;
        }

        static inject(containerId, activePage = '') {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = this.render(activePage);
            } else {
                console.warn(`Navigation container '${containerId}' not found`);
            }
        }
    };

    /**
     * Page Header Component - Standardized page headers
     */
    static PageHeaderComponent = class {
        static render(title, subtitle = '', icon = '') {
            return `
            <div class="page-header">
                <div class="header-content">
                    <h1>${icon} ${title}</h1>
                    ${subtitle ? `<p class="subtitle">${subtitle}</p>` : ''}
                </div>
            </div>`;
        }

        static inject(containerId, title, subtitle = '', icon = '') {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = this.render(title, subtitle, icon);
            } else {
                console.warn(`Header container '${containerId}' not found`);
            }
        }
    };

    /**
     * Status Indicator Component - Consistent status displays
     */
    static StatusComponent = class {
        static render(status, label, details = '') {
            const statusClass = status.toLowerCase();
            return `
            <div class="status ${statusClass}">
                <span class="status-indicator">●</span>
                <span class="status-label">${label}</span>
                ${details ? `<span class="status-details">${details}</span>` : ''}
            </div>`;
        }

        static inject(containerId, status, label, details = '') {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = this.render(status, label, details);
            } else {
                console.warn(`Status container '${containerId}' not found`);
            }
        }
    };

    /**
     * Breadcrumb Component - Navigation breadcrumbs
     */
    static BreadcrumbComponent = class {
        static render(breadcrumbs) {
            const breadcrumbHTML = breadcrumbs.map((crumb, index) => {
                const isLast = index === breadcrumbs.length - 1;
                if (isLast) {
                    return `<span class="breadcrumb-current">${crumb.label}</span>`;
                } else {
                    return `<a href="${crumb.href}" class="breadcrumb-link">${crumb.label}</a>`;
                }
            }).join('<span class="breadcrumb-separator">›</span>');

            return `
            <div class="breadcrumbs">
                ${breadcrumbHTML}
            </div>`;
        }

        static inject(containerId, breadcrumbs) {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = this.render(breadcrumbs);
            } else {
                console.warn(`Breadcrumb container '${containerId}' not found`);
            }
        }
    };

    /**
     * Footer Component - Consistent footer across all interfaces
     */
    static FooterComponent = class {
        static render() {
            return `
            <div class="page-footer">
                <div class="footer-content">
                    <div class="footer-section">
                        <h4>🎛️ Unhinged Platform</h4>
                        <p>AI-powered control interfaces</p>
                    </div>
                    <div class="footer-section">
                        <h4>🔗 Quick Links</h4>
                        <a href="index.html">Mission Control</a>
                        <a href="table-of-contents.html">All Interfaces</a>
                    </div>
                    <div class="footer-section">
                        <h4>📊 System</h4>
                        <span class="footer-status">Status: <span id="footer-system-status">●</span></span>
                    </div>
                </div>
                <div class="footer-bottom">
                    <p>&copy; 2024 Unhinged Platform - The Floor Foundation</p>
                </div>
            </div>`;
        }

        static inject(containerId) {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = this.render();
                this.updateSystemStatus();
            } else {
                console.warn(`Footer container '${containerId}' not found`);
            }
        }

        static updateSystemStatus() {
            const statusElement = document.getElementById('footer-system-status');
            if (statusElement) {
                statusElement.textContent = '🟢';
                statusElement.style.color = 'var(--color-success)';
            }
        }
    };

    /**
     * Layout Component - Standard page layouts
     */
    static LayoutComponent = class {
        static renderStandardLayout(content = '') {
            return `
            <div class="standard-layout">
                <div id="nav-container" data-component="navigation"></div>
                <div id="header-container" data-component="page-header"></div>
                <main class="main-content">
                    ${content}
                </main>
                <div id="footer-container" data-component="footer"></div>
            </div>`;
        }

        static renderTestLayout(content = '') {
            return `
            <div class="test-layout">
                <div id="nav-container" data-component="navigation"></div>
                <div class="test-container">
                    <div id="header-container" data-component="page-header"></div>
                    <div class="test-content">
                        ${content}
                    </div>
                </div>
                <div id="footer-container" data-component="footer"></div>
            </div>`;
        }

        static inject(containerId, layoutType = 'standard', content = '') {
            const container = document.getElementById(containerId);
            if (container) {
                if (layoutType === 'test') {
                    container.innerHTML = this.renderTestLayout(content);
                } else {
                    container.innerHTML = this.renderStandardLayout(content);
                }
            } else {
                console.warn(`Layout container '${containerId}' not found`);
            }
        }
    };

    /**
     * Auto-inject components based on data attributes
     */
    static autoInject() {
        document.addEventListener('DOMContentLoaded', () => {
            // Auto-inject navigation
            const navContainers = document.querySelectorAll('[data-component="navigation"]');
            navContainers.forEach(container => {
                const activePage = container.getAttribute('data-active') || '';
                this.NavigationComponent.inject(container.id, activePage);
            });

            // Auto-inject headers
            const headerContainers = document.querySelectorAll('[data-component="page-header"]');
            headerContainers.forEach(container => {
                const title = container.getAttribute('data-title') || '';
                const subtitle = container.getAttribute('data-subtitle') || '';
                const icon = container.getAttribute('data-icon') || '';
                this.PageHeaderComponent.inject(container.id, title, subtitle, icon);
            });

            // Auto-inject footers
            const footerContainers = document.querySelectorAll('[data-component="footer"]');
            footerContainers.forEach(container => {
                this.FooterComponent.inject(container.id);
            });

            // Auto-inject status indicators
            const statusContainers = document.querySelectorAll('[data-component="status"]');
            statusContainers.forEach(container => {
                const status = container.getAttribute('data-status') || 'unknown';
                const label = container.getAttribute('data-label') || '';
                const details = container.getAttribute('data-details') || '';
                this.StatusComponent.inject(container.id, status, label, details);
            });

            // Auto-inject layouts
            const layoutContainers = document.querySelectorAll('[data-component="layout"]');
            layoutContainers.forEach(container => {
                const layoutType = container.getAttribute('data-layout-type') || 'standard';
                const content = container.innerHTML; // Preserve existing content
                this.LayoutComponent.inject(container.id, layoutType, content);
            });
        });
    }

    /**
     * Tab System Component
     * Provides browser-within-browser tab functionality
     */
    static TabSystem = class {
        constructor(container) {
            this.container = container;
            this.tabs = [];
            this.activeTab = null;
            this.init();
        }

        init() {
            this.render();
            this.setupEventListeners();
        }

        render() {
            this.container.innerHTML = `
                <div class="tab-container ${this.tabs.length === 0 ? 'empty-state' : ''}">
                    <div class="tab-navigation">
                        ${this.renderTabs()}
                        <button class="tab-add-button" data-action="add-tab">
                            <span>+</span>
                            <span>Add Tab</span>
                        </button>
                    </div>
                    <div class="tab-content">
                        ${this.renderContent()}
                    </div>
                </div>
            `;
        }

        renderTabs() {
            return this.tabs.map((tab, index) => `
                <button class="tab-link ${tab.active ? 'active' : ''}"
                        data-tab-id="${tab.id}"
                        data-action="switch-tab">
                    <span class="tab-icon">${tab.icon}</span>
                    <span class="tab-label">${tab.label}</span>
                    ${this.tabs.length > 1 ? `<button class="tab-close" data-action="close-tab" data-tab-id="${tab.id}">×</button>` : ''}
                </button>
            `).join('');
        }

        renderContent() {
            if (this.tabs.length === 0) {
                return `
                    <div class="tab-empty-icon">📚</div>
                    <div class="tab-empty-title">No tabs open</div>
                    <div class="tab-empty-subtitle">Add a tab to get started, or browse the table of contents below</div>
                    <div class="tab-default-content">
                        ${this.getTableOfContents()}
                    </div>
                `;
            }

            const activeTab = this.tabs.find(tab => tab.active);
            return activeTab ? activeTab.content : '';
        }

        getTableOfContents() {
            return `
                <div class="toc-container">
                    <h3>🎛️ Control Plane Interfaces</h3>
                    <div class="toc-grid">
                        <div class="toc-section">
                            <h4>Core Interfaces</h4>
                            <ul class="toc-list">
                                <li><a href="index.html">🎛️ Mission Control</a></li>
                                <li><a href="persistence-platform.html">💾 Persistence Platform</a></li>
                                <li><a href="table-of-contents.html">📚 Table of Contents</a></li>
                            </ul>
                        </div>
                        <div class="toc-section">
                            <h4>Blog System</h4>
                            <ul class="toc-list">
                                <li><a href="blog-list.html">📚 Blog Posts</a></li>
                                <li><a href="blog-editor.html">✍️ Blog Editor</a></li>
                                <li><a href="test-blog-integration.html">🧪 Blog Integration Test</a></li>
                            </ul>
                        </div>
                        <div class="toc-section">
                            <h4>Development Tools</h4>
                            <ul class="toc-list">
                                <li><a href="validate-standardization.html">🔍 Validator</a></li>
                            </ul>
                        </div>
                    </div>
                </div>
            `;
        }

        setupEventListeners() {
            this.container.addEventListener('click', (event) => {
                const action = event.target.dataset.action;
                const tabId = event.target.dataset.tabId;
                const tabContent = event.target.dataset.tabContent;

                switch (action) {
                    case 'add-tab':
                        this.addTab();
                        break;
                    case 'switch-tab':
                        this.switchTab(tabId);
                        break;
                    case 'close-tab':
                        event.stopPropagation();
                        this.closeTab(tabId);
                        break;
                }

                if (tabContent) {
                    event.preventDefault();
                    this.addTabFromContent(tabContent);
                }
            });
        }

        addTab(options = {}) {
            const defaultOptions = {
                id: `tab-${Date.now()}`,
                icon: '📄',
                label: 'New Tab',
                content: '<div class="tab-placeholder">Tab content goes here</div>',
                active: true
            };

            const tab = { ...defaultOptions, ...options };

            // Deactivate other tabs
            this.tabs.forEach(t => t.active = false);

            this.tabs.push(tab);
            this.activeTab = tab.id;
            this.render();
        }

        addTabFromContent(contentType) {
            const contentMap = {
                'mission-control': { icon: '🎛️', label: 'Mission Control', content: this.getMissionControlContent() },

                'service-orchestration': { icon: '🎛️', label: 'Service Orchestration', content: this.getServiceOrchestrationContent() },
                'text-test': { icon: '🚀', label: 'Text Generation', content: this.getTextTestContent() },
                'image-test': { icon: '👁️', label: 'Vision AI', content: this.getImageTestContent() },
                'voice-test': { icon: '🎤', label: 'Voice Processing', content: this.getVoiceTestContent() },
                'chat': { icon: '💬', label: 'AI Chat', content: this.getChatContent() },
                'grpc-test': { icon: '🔧', label: 'gRPC Testing', content: this.getGRPCTestContent() },
                'persistence-dev-tool': { icon: '💾', label: 'Data Management', content: this.getPersistenceContent() }
            };

            const config = contentMap[contentType];
            if (config) {
                this.addTab({
                    id: contentType,
                    ...config
                });
            }
        }

        switchTab(tabId) {
            this.tabs.forEach(tab => {
                tab.active = tab.id === tabId;
            });
            this.activeTab = tabId;
            this.render();
        }

        closeTab(tabId) {
            const tabIndex = this.tabs.findIndex(tab => tab.id === tabId);
            if (tabIndex === -1) return;

            const wasActive = this.tabs[tabIndex].active;
            this.tabs.splice(tabIndex, 1);

            if (wasActive && this.tabs.length > 0) {
                // Activate the tab to the left, or the first tab if we closed the first one
                const newActiveIndex = Math.max(0, tabIndex - 1);
                this.tabs[newActiveIndex].active = true;
                this.activeTab = this.tabs[newActiveIndex].id;
            } else if (this.tabs.length === 0) {
                this.activeTab = null;
            }

            this.render();
        }

        // Content generators for different tab types
        getMissionControlContent() {
            return `
                <div class="mission-control-tab">
                    <h2>🎛️ Mission Control</h2>
                    <p>System operations center for the Unhinged platform.</p>
                    <div class="quick-actions">
                        <button class="action-button">🚀 Start All Services</button>
                        <button class="action-button">🛑 Stop All Services</button>
                        <button class="action-button">📊 View Metrics</button>
                    </div>
                </div>
            `;
        }



        getServiceOrchestrationContent() {
            return `
                <div class="service-orchestration-tab">
                    <h2>🎛️ Service Orchestration</h2>
                    <p>Docker service management and orchestration.</p>
                    <div class="service-actions">
                        <button class="action-button">🐳 Start Containers</button>
                        <button class="action-button">📋 View Logs</button>
                        <button class="action-button">🔧 Configure Services</button>
                    </div>
                </div>
            `;
        }

        getTextTestContent() {
            return `
                <div class="text-test-tab">
                    <h2>🚀 Text Generation</h2>
                    <p>GPU-accelerated language model testing interface.</p>
                    <textarea placeholder="Enter your prompt here..." rows="4" style="width: 100%; margin: 16px 0;"></textarea>
                    <button class="generate-button">Generate Text</button>
                </div>
            `;
        }

        getImageTestContent() {
            return `
                <div class="image-test-tab">
                    <h2>👁️ Vision AI</h2>
                    <p>Image analysis and processing capabilities.</p>
                    <div class="upload-area" style="border: 2px dashed #ccc; padding: 40px; text-align: center; margin: 16px 0;">
                        <div>📁 Drop image here or click to upload</div>
                    </div>
                    <button class="action-button">Analyze Image</button>
                </div>
            `;
        }

        getVoiceTestContent() {
            return `
                <div class="voice-test-tab">
                    <h2>🎤 Voice Processing</h2>
                    <p>Speech-to-text and audio analysis tools.</p>
                    <div class="voice-controls" style="text-align: center; margin: 24px 0;">
                        <button class="action-button">🎤 Start Recording</button>
                        <button class="action-button">⏹️ Stop Recording</button>
                        <button class="action-button">▶️ Play Audio</button>
                    </div>
                </div>
            `;
        }

        getChatContent() {
            return `
                <div class="chat-tab">
                    <h2>💬 AI Chat</h2>
                    <div class="chat-messages" style="height: 300px; border: 1px solid #ddd; padding: 16px; margin: 16px 0; overflow-y: auto;">
                        <div class="chat-message">Welcome to AI Chat!</div>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <input type="text" placeholder="Type your message..." style="flex: 1; padding: 8px;">
                        <button class="action-button">Send</button>
                    </div>
                </div>
            `;
        }

        getGRPCTestContent() {
            return `
                <div class="grpc-test-tab">
                    <h2>🔧 gRPC Testing</h2>
                    <p>Direct service communication testing.</p>
                    <div class="grpc-controls">
                        <select style="width: 100%; margin: 8px 0; padding: 8px;">
                            <option>Select Service</option>
                            <option>Text Generation Service</option>
                            <option>Vision AI Service</option>
                            <option>Voice Processing Service</option>
                        </select>
                        <button class="action-button">Test Connection</button>
                    </div>
                </div>
            `;
        }

        getPersistenceContent() {
            return `
                <div class="persistence-tab">
                    <h2>💾 Data Management</h2>
                    <p>Database and storage management tools.</p>
                    <div class="persistence-actions">
                        <button class="action-button">📊 View Database</button>
                        <button class="action-button">🔄 Backup Data</button>
                        <button class="action-button">🗑️ Clear Cache</button>
                    </div>
                </div>
            `;
        }
    };

    /**
     * Initialize all components
     */
    static init() {
        this.autoInject();
        this.KeyboardManager.init();

        // Enhance all existing buttons with accessibility
        document.addEventListener('DOMContentLoaded', () => {
            const buttons = document.querySelectorAll('button, .generate-button, .action-button, .nav-link');
            buttons.forEach(button => {
                this.KeyboardManager.enhanceButtonAccessibility?.(button);
            });

            // Initialize tab systems
            const tabContainers = document.querySelectorAll('[data-component="tab-system"]');
            tabContainers.forEach(container => {
                container.tabSystem = new this.TabSystem(container);
            });
        });
    }
}

// Auto-initialize when script loads
UnhingedComponents.init();

// Export for manual usage
window.UnhingedComponents = UnhingedComponents;
