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

            // Alt + D: Go to DAG control
            if (event.altKey && event.key === 'd') {
                event.preventDefault();
                window.location.href = 'dag-control.html';
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
                { id: 'dag', href: 'dag-control.html', icon: '🎯', label: 'DAG Control' },
                { id: 'orchestration', href: 'service-orchestration.html', icon: '🎛️', label: 'Service Orchestration' },
                { id: 'text', href: 'text-test.html', icon: '🚀', label: 'Text Generation' },
                { id: 'image', href: 'image-test.html', icon: '👁️', label: 'Vision AI' },
                { id: 'voice', href: 'voice-test.html', icon: '🎤', label: 'Voice Processing' },
                { id: 'chat', href: 'chat.html', icon: '💬', label: 'AI Chat' },
                { id: 'grpc', href: 'grpc-test.html', icon: '🔧', label: 'Service Testing' },
                { id: 'persistence', href: 'persistence-dev-tool.html', icon: '💾', label: 'Data Management' },
                { id: 'toc', href: 'table-of-contents.html', icon: '📚', label: 'Table of Contents' },
                { id: 'test', href: 'accessibility-test.html', icon: '🧪', label: 'Accessibility Test' },
                { id: 'validator', href: 'validate-standardization.html', icon: '🔍', label: 'Validator' }
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
        });
    }
}

// Auto-initialize when script loads
UnhingedComponents.init();

// Export for manual usage
window.UnhingedComponents = UnhingedComponents;
