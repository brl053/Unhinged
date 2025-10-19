/**
 * Unhinged AI Service Testing - Configuration
 * Centralized configuration for all service test pages
 * Eliminates hardcoded URLs and service metadata duplication
 */

const SERVICE_CONFIG = {
    'dag_control': {
        name: 'DAG Control Plane',
        icon: '🎛️',
        subtitle: 'Intelligent Build Orchestration with Human Oversight',
        baseUrl: 'http://localhost:9000',
        healthEndpoint: '/dag/health',
        testEndpoint: '/dag/status',
        port: 9000,
        description: 'Unified control plane for build orchestration, dependency management, and human-in-the-loop workflows.',
        capabilities: [
            'DAG-based build execution with cycle detection',
            'Parallel execution with dependency awareness',
            'Human approval workflows for critical operations',
            'Real-time performance monitoring and metrics',
            'LLM-powered error explanation and optimization',
            'Self-serve debugging and report generation'
        ]
    },
    'text': {
        name: 'GPU-Accelerated LLM Test',
        icon: '🚀',
        subtitle: 'Dual-Model Architecture: Specialized AI for Coding & Creative Tasks',
        baseUrl: 'http://localhost:11434',
        healthEndpoint: '/api/tags',
        testEndpoint: '/api/generate',
        port: 11434,
        description: 'Test our dual-model architecture with 5 specialized LLMs running on RTX 5070 Ti GPU.',
        capabilities: [
            'DeepSeek-Coder 6.7B for coding tasks',
            'Dolphin-Mixtral 8x7B for creative content',
            'GPU acceleration with RTX 5070 Ti',
            'Minimal to zero censorship',
            '3-80 second response times'
        ]
    },
    'vision': {
        name: 'Vision AI Analysis',
        icon: '👁️',
        subtitle: 'Advanced Image Analysis using BLIP Vision Transformer',
        baseUrl: 'http://localhost:8001',
        healthEndpoint: '/health',
        testEndpoint: '/analyze',
        port: 8001,
        description: 'Advanced image analysis and description using BLIP models with object detection.',
        capabilities: [
            'BLIP Vision Transformer model',
            'Image description and captioning',
            'Object detection and scene understanding',
            'Support for JPG, PNG, WebP formats',
            '2-5 second response times'
        ]
    },
    'audio': {
        name: 'Voice & Audio Processing',
        icon: '🎤',
        subtitle: 'High-Quality Speech-to-Text using OpenAI Whisper',
        baseUrl: 'http://localhost:8000',
        healthEndpoint: '/health',
        testEndpoint: '/transcribe',
        port: 8000,
        description: 'High-quality speech-to-text transcription using OpenAI Whisper with multi-language support.',
        capabilities: [
            'OpenAI Whisper model',
            '99+ languages supported',
            'MP3, WAV, M4A, WebM formats',
            '95%+ accuracy for clear audio',
            'Real-time recording support'
        ]
    }
};

/**
 * Common API endpoints used across services
 */
const COMMON_ENDPOINTS = {
    health: '/health',
    status: '/status',
    info: '/info'
};

/**
 * Common HTTP headers for API requests
 */
const COMMON_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
};

/**
 * CORS configuration for cross-origin requests
 */
const CORS_CONFIG = {
    mode: 'cors',
    credentials: 'omit'
};

/**
 * Timeout configurations (in milliseconds)
 */
const TIMEOUTS = {
    health_check: 5000,      // 5 seconds for health checks
    text_generation: 120000, // 2 minutes for text generation
    image_analysis: 30000,   // 30 seconds for image analysis
    audio_transcription: 60000 // 1 minute for audio transcription
};

/**
 * Status indicator configurations
 */
const STATUS_CONFIG = {
    healthy: {
        class: 'status healthy',
        icon: '✅',
        message: 'Service Healthy'
    },
    unhealthy: {
        class: 'status unhealthy',
        icon: '❌',
        message: 'Service Unavailable'
    },
    loading: {
        class: 'status loading',
        icon: '⏳',
        message: 'Checking service...'
    },
    testing: {
        class: 'status loading',
        icon: '🔄',
        message: 'Processing request...'
    }
};

/**
 * Navigation links for all service pages
 */
const NAVIGATION_LINKS = [
    { href: 'index.html', text: '🏠 Home', service: 'home' },
    { href: 'text-test.html', text: '🚀 Text Generation', service: 'text' },
    { href: 'image-test.html', text: '👁️ Vision AI', service: 'vision' },
    { href: 'voice-test.html', text: '🎤 Voice Processing', service: 'audio' }
];

/**
 * Get service configuration by service type
 * @param {string} serviceType - The service type ('text', 'vision', 'audio')
 * @returns {object} Service configuration object
 */
function getServiceConfig(serviceType) {
    return SERVICE_CONFIG[serviceType] || null;
}

/**
 * Get full API URL for a service endpoint
 * @param {string} serviceType - The service type
 * @param {string} endpoint - The endpoint path
 * @returns {string} Full URL
 */
function getApiUrl(serviceType, endpoint) {
    const config = getServiceConfig(serviceType);
    if (!config) return null;
    return config.baseUrl + endpoint;
}

/**
 * Get health check URL for a service
 * @param {string} serviceType - The service type
 * @returns {string} Health check URL
 */
function getHealthUrl(serviceType) {
    const config = getServiceConfig(serviceType);
    if (!config) return null;
    return config.baseUrl + config.healthEndpoint;
}

/**
 * Get test endpoint URL for a service
 * @param {string} serviceType - The service type
 * @returns {string} Test endpoint URL
 */
function getTestUrl(serviceType) {
    const config = getServiceConfig(serviceType);
    if (!config) return null;
    return config.baseUrl + config.testEndpoint;
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        SERVICE_CONFIG,
        COMMON_ENDPOINTS,
        COMMON_HEADERS,
        CORS_CONFIG,
        TIMEOUTS,
        STATUS_CONFIG,
        NAVIGATION_LINKS,
        getServiceConfig,
        getApiUrl,
        getHealthUrl,
        getTestUrl
    };
}
