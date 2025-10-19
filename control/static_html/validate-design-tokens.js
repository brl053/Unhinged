#!/usr/bin/env node

/**
 * Design Token Validation Script
 * Scans all HTML files for hardcoded values that should use design tokens
 * Part of "The Floor" foundation implementation
 */

const fs = require('fs');
const path = require('path');

// Violation patterns to detect
const violations = [
    {
        name: 'Hardcoded Colors',
        pattern: /color:\s*#[0-9a-fA-F]{3,6}/g,
        description: 'Use var(--color-*) tokens instead'
    },
    {
        name: 'Hardcoded Backgrounds',
        pattern: /background:\s*#[0-9a-fA-F]{3,6}/g,
        description: 'Use var(--color-*) tokens instead'
    },
    {
        name: 'Hardcoded Font Sizes (px)',
        pattern: /font-size:\s*\d+px/g,
        description: 'Use var(--font-size-*) tokens instead'
    },
    {
        name: 'Hardcoded Padding (px)',
        pattern: /padding:\s*\d+px/g,
        description: 'Use var(--spacing-*) tokens instead'
    },
    {
        name: 'Hardcoded Margin (px)',
        pattern: /margin:\s*\d+px/g,
        description: 'Use var(--spacing-*) tokens instead'
    },
    {
        name: 'Hardcoded Border Radius (px)',
        pattern: /border-radius:\s*\d+px/g,
        description: 'Use var(--border-radius*) tokens instead'
    }
];

// Files to scan (excluding html-links subdirectory and test files)
const htmlFiles = [
    'persistence-dev-tool.html',
    'text-test.html',
    'grpc-test.html',
    'table-of-contents.html',
    'chat.html',
    'index.html',
    'image-test.html',
    'service-orchestration.html',
    'dag-control.html',
    'voice-test.html'
];

function scanFile(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf8');
        const results = [];
        
        violations.forEach(violation => {
            const matches = content.match(violation.pattern);
            if (matches) {
                results.push({
                    type: violation.name,
                    count: matches.length,
                    matches: matches,
                    description: violation.description
                });
            }
        });
        
        return results;
    } catch (error) {
        console.error(`Error reading file ${filePath}:`, error.message);
        return [];
    }
}

function main() {
    console.log('🔍 Design Token Validation - The Floor Foundation');
    console.log('================================================\n');
    
    let totalViolations = 0;
    let filesWithViolations = 0;
    
    htmlFiles.forEach(fileName => {
        const filePath = path.join(__dirname, fileName);
        const violations = scanFile(filePath);
        
        if (violations.length > 0) {
            filesWithViolations++;
            console.log(`❌ ${fileName}:`);
            
            violations.forEach(violation => {
                totalViolations += violation.count;
                console.log(`   ${violation.type}: ${violation.count} violations`);
                console.log(`   → ${violation.description}`);
                
                // Show first few examples
                const examples = violation.matches.slice(0, 3);
                examples.forEach(example => {
                    console.log(`     Example: ${example}`);
                });
                if (violation.matches.length > 3) {
                    console.log(`     ... and ${violation.matches.length - 3} more`);
                }
                console.log('');
            });
        } else {
            console.log(`✅ ${fileName}: No violations found`);
        }
    });
    
    console.log('\n📊 SUMMARY');
    console.log('===========');
    console.log(`Files scanned: ${htmlFiles.length}`);
    console.log(`Files with violations: ${filesWithViolations}`);
    console.log(`Total violations: ${totalViolations}`);
    
    if (totalViolations === 0) {
        console.log('\n🎉 THE FLOOR IS COMPLETE!');
        console.log('All files are using design tokens correctly.');
        process.exit(0);
    } else {
        console.log('\n🚧 FOUNDATION WORK NEEDED');
        console.log('Some files still contain hardcoded values.');
        console.log('Refer to TOKEN_MAPPINGS.md for remediation guidance.');
        process.exit(1);
    }
}

// Run validation
if (require.main === module) {
    main();
}

module.exports = { scanFile, violations };
