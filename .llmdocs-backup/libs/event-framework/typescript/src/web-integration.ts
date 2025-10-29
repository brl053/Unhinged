/**
 * Web Integration for the Event Framework
 * 
 * Provides specialized logging capabilities for web components and browser interactions,
 * enabling logging of user interactions, clicks, navigation, and web-specific events.
 */

import { EventLogger, createServiceLogger, LogLevel } from './event-logger';

/**
 * Represents a web interaction event
 */
export interface WebEvent {
    eventType: string; // click, navigation, form_submit, etc.
    elementId?: string;
    elementType?: string;
    elementText?: string;
    url?: string;
    coordinates?: { x: number; y: number };
    keyCode?: string;
    modifiers?: string[]; // Ctrl, Alt, Shift, etc.
    pageTitle?: string;
    userAgent?: string;
    additionalData?: Record<string, any>;
}

/**
 * Specialized logger for web events and user interactions
 */
export class WebEventLogger {
    private logger: EventLogger;
    private sessionId: string;
    private currentPage: string | null = null;
    
    constructor(appName: string = 'unhinged-web', version: string = '1.0.0') {
        this.logger = createServiceLogger(
            appName,
            version,
            this.getEnvironment(),
            LogLevel.INFO
        );
        
        // Web-specific context
        this.sessionId = `web_session_${Date.now()}`;
        this.currentPage = typeof window !== 'undefined' ? window.location.pathname : null;
        
        // Add web-specific context to logger
        this.logger = this.logger.withContext({
            component_type: 'web_ui',
            ui_framework: 'browser',
            session_id: this.sessionId,
            user_agent: typeof navigator !== 'undefined' ? navigator.userAgent : 'unknown',
            current_page: this.currentPage
        });
        
        // Set up automatic page tracking
        this.setupPageTracking();
    }
    
    /**
     * Log a user interaction event
     */
    logUserInteraction(webEvent: WebEvent, userId?: string): void {
        const metadata: Record<string, any> = {
            event_type: 'user_interaction',
            web_event_type: webEvent.eventType,
            interaction_timestamp: Date.now()
        };
        
        // Add web event details
        if (webEvent.elementId) metadata.element_id = webEvent.elementId;
        if (webEvent.elementType) metadata.element_type = webEvent.elementType;
        if (webEvent.elementText) metadata.element_text = webEvent.elementText;
        if (webEvent.url) metadata.url = webEvent.url;
        if (webEvent.coordinates) metadata.coordinates = webEvent.coordinates;
        if (webEvent.keyCode) metadata.key_code = webEvent.keyCode;
        if (webEvent.modifiers) metadata.modifiers = webEvent.modifiers;
        if (webEvent.pageTitle) metadata.page_title = webEvent.pageTitle;
        if (webEvent.userAgent) metadata.user_agent = webEvent.userAgent;
        if (webEvent.additionalData) metadata.additional_data = webEvent.additionalData;
        
        // Add user context if available
        if (userId) metadata.user_id = userId;
        
        // Create contextual logger if we have page info
        let contextualLogger = this.logger;
        if (webEvent.url || webEvent.pageTitle) {
            const context: Record<string, any> = {};
            if (webEvent.url) context.current_url = webEvent.url;
            if (webEvent.pageTitle) context.current_page_title = webEvent.pageTitle;
            contextualLogger = this.logger.withContext(context);
        }
        
        // Log the interaction
        let message = `User ${webEvent.eventType}`;
        if (webEvent.elementText) {
            message += ` on '${webEvent.elementText}'`;
        } else if (webEvent.elementType) {
            message += ` on ${webEvent.elementType}`;
        }
        
        contextualLogger.info(message, metadata);
    }
    
    /**
     * Log a button click event
     */
    logButtonClick(buttonText: string, elementId?: string, coordinates?: { x: number; y: number }, userId?: string): void {
        const webEvent: WebEvent = {
            eventType: 'button_click',
            elementType: 'button',
            elementText: buttonText,
            elementId,
            coordinates,
            pageTitle: typeof document !== 'undefined' ? document.title : undefined,
            url: typeof window !== 'undefined' ? window.location.href : undefined
        };
        this.logUserInteraction(webEvent, userId);
    }
    
    /**
     * Log a link click event
     */
    logLinkClick(linkText: string, href: string, elementId?: string, userId?: string): void {
        const webEvent: WebEvent = {
            eventType: 'link_click',
            elementType: 'link',
            elementText: linkText,
            elementId,
            url: href,
            pageTitle: typeof document !== 'undefined' ? document.title : undefined,
            additionalData: { target_url: href }
        };
        this.logUserInteraction(webEvent, userId);
    }
    
    /**
     * Log form submission
     */
    logFormSubmit(formId?: string, formAction?: string, fieldCount?: number, userId?: string): void {
        const webEvent: WebEvent = {
            eventType: 'form_submit',
            elementType: 'form',
            elementId: formId,
            url: typeof window !== 'undefined' ? window.location.href : undefined,
            additionalData: {
                form_action: formAction,
                field_count: fieldCount
            }
        };
        this.logUserInteraction(webEvent, userId);
    }
    
    /**
     * Log page navigation
     */
    logPageNavigation(fromUrl: string, toUrl: string, navigationType: string = 'unknown', userId?: string): void {
        const webEvent: WebEvent = {
            eventType: 'page_navigation',
            elementType: 'navigation',
            url: toUrl,
            additionalData: {
                from_url: fromUrl,
                to_url: toUrl,
                navigation_type: navigationType
            }
        };
        this.currentPage = new URL(toUrl).pathname;
        this.logUserInteraction(webEvent, userId);
    }
    
    /**
     * Log keyboard shortcut usage
     */
    logKeyboardShortcut(shortcut: string, action: string, userId?: string): void {
        const webEvent: WebEvent = {
            eventType: 'keyboard_shortcut',
            elementType: 'shortcut',
            keyCode: shortcut,
            url: typeof window !== 'undefined' ? window.location.href : undefined,
            additionalData: { action }
        };
        this.logUserInteraction(webEvent, userId);
    }
    
    /**
     * Log scroll events
     */
    logScroll(scrollPosition: number, scrollDirection: 'up' | 'down', userId?: string): void {
        const webEvent: WebEvent = {
            eventType: 'scroll',
            elementType: 'page',
            url: typeof window !== 'undefined' ? window.location.href : undefined,
            additionalData: {
                scroll_position: scrollPosition,
                scroll_direction: scrollDirection
            }
        };
        this.logUserInteraction(webEvent, userId);
    }
    
    /**
     * Log web-specific errors
     */
    logError(errorMessage: string, errorType: string = 'web_error', url?: string, exception?: Error): void {
        const metadata: Record<string, any> = {
            error_type: errorType,
            web_component: 'browser'
        };
        
        if (url) metadata.url = url;
        
        this.logger.error(errorMessage, exception, metadata);
    }
    
    /**
     * Log performance metrics
     */
    logPerformanceMetric(metricName: string, value: number, unit: string = 'ms'): void {
        const metadata: Record<string, any> = {
            metric_type: 'web_performance',
            metric_name: metricName,
            metric_value: value,
            metric_unit: unit,
            url: typeof window !== 'undefined' ? window.location.href : undefined
        };
        
        this.logger.info(`Performance metric: ${metricName} = ${value}${unit}`, metadata);
    }
    
    /**
     * Set up automatic page tracking
     */
    private setupPageTracking(): void {
        if (typeof window === 'undefined') return;
        
        // Track initial page load
        window.addEventListener('load', () => {
            this.logPageNavigation('', window.location.href, 'initial_load');
        });
        
        // Track page visibility changes
        document.addEventListener('visibilitychange', () => {
            const webEvent: WebEvent = {
                eventType: document.hidden ? 'page_hidden' : 'page_visible',
                elementType: 'page',
                url: window.location.href,
                additionalData: { visibility_state: document.visibilityState }
            };
            this.logUserInteraction(webEvent);
        });
        
        // Track beforeunload (page leaving)
        window.addEventListener('beforeunload', () => {
            const webEvent: WebEvent = {
                eventType: 'page_unload',
                elementType: 'page',
                url: window.location.href
            };
            this.logUserInteraction(webEvent);
        });
    }
    
    private getEnvironment(): string {
        if (typeof process !== 'undefined' && process.env) {
            return process.env.NODE_ENV || process.env.ENVIRONMENT || 'development';
        }
        return 'development';
    }
}

/**
 * Factory function to create a web event logger
 */
export function createWebLogger(appName: string = 'unhinged-web', version: string = '1.0.0'): WebEventLogger {
    return new WebEventLogger(appName, version);
}

/**
 * Auto-attach event listeners to common elements
 */
export function autoTrackWebEvents(logger: WebEventLogger, userId?: string): void {
    if (typeof document === 'undefined') return;
    
    // Track all button clicks
    document.addEventListener('click', (event) => {
        const target = event.target as HTMLElement;
        if (target.tagName === 'BUTTON') {
            logger.logButtonClick(
                target.textContent || target.getAttribute('aria-label') || 'Unknown Button',
                target.id,
                { x: event.clientX, y: event.clientY },
                userId
            );
        } else if (target.tagName === 'A') {
            const link = target as HTMLAnchorElement;
            logger.logLinkClick(
                link.textContent || link.getAttribute('aria-label') || 'Unknown Link',
                link.href,
                link.id,
                userId
            );
        }
    });
    
    // Track form submissions
    document.addEventListener('submit', (event) => {
        const form = event.target as HTMLFormElement;
        const fieldCount = form.querySelectorAll('input, select, textarea').length;
        logger.logFormSubmit(form.id, form.action, fieldCount, userId);
    });
    
    // Track keyboard shortcuts (common ones)
    document.addEventListener('keydown', (event) => {
        if (event.ctrlKey || event.metaKey) {
            const key = event.key.toLowerCase();
            const shortcut = `${event.ctrlKey ? 'Ctrl+' : 'Cmd+'}${key}`;
            
            // Only log common shortcuts to avoid noise
            const commonShortcuts = ['s', 'c', 'v', 'x', 'z', 'y', 'f', 'n', 't', 'w'];
            if (commonShortcuts.includes(key)) {
                logger.logKeyboardShortcut(shortcut, `shortcut_${key}`, userId);
            }
        }
    });
}
