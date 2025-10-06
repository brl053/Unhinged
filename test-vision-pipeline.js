#!/usr/bin/env node

/**
 * Vision Pipeline Test Script
 * 
 * Tests the complete image processing pipeline:
 * 1. Vision AI service health
 * 2. Backend vision endpoints
 * 3. End-to-end image analysis
 */

const fs = require('fs');
const path = require('path');

// Test configuration
const VISION_SERVICE_URL = 'http://localhost:8001';
const BACKEND_URL = 'http://localhost:8080';

// ANSI color codes for pretty output
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

function logSection(title) {
    log(`\n${'='.repeat(60)}`, 'cyan');
    log(`${title}`, 'bright');
    log(`${'='.repeat(60)}`, 'cyan');
}

function logTest(name, status, details = '') {
    const statusColor = status === 'PASS' ? 'green' : status === 'FAIL' ? 'red' : 'yellow';
    const statusIcon = status === 'PASS' ? '✅' : status === 'FAIL' ? '❌' : '⏳';
    log(`${statusIcon} ${name}: ${status}`, statusColor);
    if (details) {
        log(`   ${details}`, 'reset');
    }
}

async function makeRequest(url, options = {}) {
    try {
        const response = await fetch(url, options);
        return {
            ok: response.ok,
            status: response.status,
            statusText: response.statusText,
            data: response.ok ? await response.json() : null,
            error: response.ok ? null : `HTTP ${response.status}: ${response.statusText}`
        };
    } catch (error) {
        return {
            ok: false,
            status: 0,
            statusText: 'Network Error',
            data: null,
            error: error.message
        };
    }
}

async function testVisionServiceHealth() {
    logSection('🔍 Vision AI Service Health Check');
    
    const result = await makeRequest(`${VISION_SERVICE_URL}/health`);
    
    if (result.ok && result.data) {
        logTest('Vision Service Health', 'PASS', `Status: ${result.data.status}`);
        logTest('Vision Model Loaded', result.data.vision_model_loaded ? 'PASS' : 'FAIL');
        logTest('CUDA Available', result.data.cuda_available ? 'PASS' : 'WARN', 'GPU acceleration');
        log(`   Service: ${result.data.service} v${result.data.version}`);
        log(`   Capabilities: ${result.data.capabilities.join(', ')}`);
        return true;
    } else {
        logTest('Vision Service Health', 'FAIL', result.error);
        return false;
    }
}

async function testBackendVisionHealth() {
    logSection('🏗️ Backend Vision Endpoints Health');
    
    const result = await makeRequest(`${BACKEND_URL}/api/v1/vision/health`);
    
    if (result.ok && result.data) {
        logTest('Backend Vision Health', 'PASS', `Status: ${result.data.status}`);
        logTest('Vision Model Loaded', result.data.visionModelLoaded ? 'PASS' : 'FAIL');
        logTest('CUDA Available', result.data.cudaAvailable ? 'PASS' : 'WARN');
        log(`   Service: ${result.data.service} v${result.data.version}`);
        log(`   Capabilities: ${result.data.capabilities.join(', ')}`);
        return true;
    } else {
        logTest('Backend Vision Health', 'FAIL', result.error);
        return false;
    }
}

async function createTestImage() {
    // Create a simple test image using Canvas API (if available) or return a placeholder
    // For now, we'll create a simple colored rectangle as base64
    const canvas = `
    <svg width="200" height="100" xmlns="http://www.w3.org/2000/svg">
        <rect width="200" height="100" fill="#4CAF50"/>
        <text x="100" y="55" font-family="Arial" font-size="16" fill="white" text-anchor="middle">Test Image</text>
    </svg>`;
    
    return Buffer.from(canvas);
}

async function testImageAnalysis() {
    logSection('🖼️ Image Analysis Pipeline Test');
    
    try {
        // Create test image
        const imageBuffer = await createTestImage();
        logTest('Test Image Creation', 'PASS', `Size: ${imageBuffer.length} bytes`);
        
        // Test image analysis endpoint
        const formData = new FormData();
        formData.append('image', new Blob([imageBuffer], { type: 'image/svg+xml' }), 'test.svg');
        formData.append('generateTags', 'true');
        formData.append('detectObjects', 'false');
        formData.append('maxDescriptionLength', '100');
        
        const result = await makeRequest(`${BACKEND_URL}/api/v1/vision/analyze`, {
            method: 'POST',
            body: formData
        });
        
        if (result.ok && result.data) {
            logTest('Image Analysis', 'PASS');
            log(`   Description: ${result.data.description}`);
            log(`   Confidence: ${result.data.confidence}`);
            log(`   Tags: ${result.data.tags.join(', ')}`);
            log(`   Processing Time: ${result.data.processingTimeMs}ms`);
            return true;
        } else {
            logTest('Image Analysis', 'FAIL', result.error);
            return false;
        }
        
    } catch (error) {
        logTest('Image Analysis', 'FAIL', error.message);
        return false;
    }
}

async function testImageDescription() {
    logSection('📝 Image Description Test');
    
    try {
        const imageBuffer = await createTestImage();
        
        const formData = new FormData();
        formData.append('image', new Blob([imageBuffer], { type: 'image/svg+xml' }), 'test.svg');
        formData.append('prompt', 'What colors do you see in this image?');
        formData.append('maxDescriptionLength', '150');
        
        const result = await makeRequest(`${BACKEND_URL}/api/v1/vision/describe`, {
            method: 'POST',
            body: formData
        });
        
        if (result.ok && result.data) {
            logTest('Image Description', 'PASS');
            log(`   Description: ${result.data.description}`);
            log(`   Prompt Used: ${result.data.promptUsed}`);
            return true;
        } else {
            logTest('Image Description', 'FAIL', result.error);
            return false;
        }
        
    } catch (error) {
        logTest('Image Description', 'FAIL', error.message);
        return false;
    }
}

async function testObjectDetection() {
    logSection('🎯 Object Detection Test');
    
    try {
        const imageBuffer = await createTestImage();
        
        const formData = new FormData();
        formData.append('image', new Blob([imageBuffer], { type: 'image/svg+xml' }), 'test.svg');
        
        const result = await makeRequest(`${BACKEND_URL}/api/v1/vision/detect`, {
            method: 'POST',
            body: formData
        });
        
        if (result.ok && result.data) {
            logTest('Object Detection', 'PASS');
            log(`   Objects Found: ${result.data.objects.length}`);
            result.data.objects.forEach((obj, i) => {
                log(`   Object ${i + 1}: ${obj.label} (${(obj.confidence * 100).toFixed(1)}%)`);
            });
            return true;
        } else {
            logTest('Object Detection', 'FAIL', result.error);
            return false;
        }
        
    } catch (error) {
        logTest('Object Detection', 'FAIL', error.message);
        return false;
    }
}

async function runTests() {
    log('🚀 Starting Vision Pipeline Tests...', 'bright');
    
    const results = {
        visionHealth: false,
        backendHealth: false,
        imageAnalysis: false,
        imageDescription: false,
        objectDetection: false
    };
    
    // Test vision service health
    results.visionHealth = await testVisionServiceHealth();
    
    // Test backend health
    results.backendHealth = await testBackendVisionHealth();
    
    // Only run pipeline tests if services are healthy
    if (results.visionHealth && results.backendHealth) {
        results.imageAnalysis = await testImageAnalysis();
        results.imageDescription = await testImageDescription();
        results.objectDetection = await testObjectDetection();
    } else {
        log('\n⚠️ Skipping pipeline tests due to service health issues', 'yellow');
    }
    
    // Summary
    logSection('📊 Test Summary');
    
    const passed = Object.values(results).filter(Boolean).length;
    const total = Object.keys(results).length;
    
    log(`Tests Passed: ${passed}/${total}`, passed === total ? 'green' : 'yellow');
    
    Object.entries(results).forEach(([test, passed]) => {
        logTest(test.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase()), passed ? 'PASS' : 'FAIL');
    });
    
    if (passed === total) {
        log('\n🎉 All tests passed! Vision pipeline is ready.', 'green');
    } else {
        log('\n⚠️ Some tests failed. Check the services and try again.', 'yellow');
    }
    
    return passed === total;
}

// Run tests if this script is executed directly
if (require.main === module) {
    runTests().then(success => {
        process.exit(success ? 0 : 1);
    }).catch(error => {
        log(`\n💥 Test runner failed: ${error.message}`, 'red');
        process.exit(1);
    });
}

module.exports = { runTests };
