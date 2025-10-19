// Auto-generated registry - DO NOT EDIT MANUALLY
// Generated at: 2025-10-18T22:44:01.060371
// Run 'make start' to regenerate

/**
 * @llm-type config
 * @llm-legend Global registry of static HTML files for browser navigation
 * @llm-key Auto-generated from filesystem scan, provides metadata for each HTML file
 * @llm-map Used by index.html and navigation components for file discovery
 * @llm-axiom Registry must be regenerated whenever HTML files are added/removed/modified
 * @llm-contract Provides consistent interface for file metadata and navigation
 * @llm-token unhinged-registry: Complete file registry for static HTML interface
 */
window.UNHINGED_REGISTRY = {
  "/control/static_html/text-test.html": {
    "title": "\ud83d\ude80 GPU-Accelerated LLM Test - Unhinged AI",
    "description": "",
    "category": "ai-services",
    "capabilities": [],
    "exists": true,
    "lastModified": 1760830716.070069,
    "size": 30808
  },
  "/control/static_html/index.html": {
    "title": "\ud83d\ude80 Unhinged AI - GPU-Accelerated Multi-Modal Platform",
    "description": "",
    "category": "root",
    "capabilities": [],
    "exists": true,
    "lastModified": 1760830716.0698452,
    "size": 13548
  },
  "/control/static_html/image-test.html": {
    "title": "\ud83d\udc41\ufe0f Vision AI Test - Unhinged Multi-Modal Platform",
    "description": "",
    "category": "ai-services",
    "capabilities": [],
    "exists": true,
    "lastModified": 1760830716.0698452,
    "size": 23318
  },
  "/control/static_html/dag-control.html": {
    "title": "\ud83c\udf9b\ufe0f DAG Control Plane - Unhinged AI",
    "description": "",
    "category": "control",
    "capabilities": [],
    "exists": true,
    "lastModified": 1760850680.5197256,
    "size": 15918
  },
  "/control/static_html/voice-test.html": {
    "title": "\ud83c\udfa4 Voice & Audio Processing - Unhinged Multi-Modal Platform",
    "description": "",
    "category": "ai-services",
    "capabilities": [],
    "exists": true,
    "lastModified": 1760830716.070069,
    "size": 14162
  },
  "/control/static_html/html-links/index.html": {
    "title": "\ud83e\udde0 Unhinged HTML Files",
    "description": "",
    "category": "root",
    "capabilities": [],
    "exists": true,
    "lastModified": 1760830716.0698452,
    "size": 8295
  },
  "/control/static_html/html-links/static-dashboard.html": {
    "title": "static-dashboard.html",
    "description": "Error reading file: [Errno 2] No such file or directory: '/home/e-bliss-station-1/Projects/Unhinged/control/static_html/html-links/static-dashboard.html'",
    "category": "error",
    "capabilities": [],
    "exists": false,
    "lastModified": 0,
    "size": 0
  },
  "/control/static_html/html-links/audio.html": {
    "title": "audio.html",
    "description": "Error reading file: [Errno 2] No such file or directory: '/home/e-bliss-station-1/Projects/Unhinged/control/static_html/html-links/audio.html'",
    "category": "error",
    "capabilities": [],
    "exists": false,
    "lastModified": 0,
    "size": 0
  },
  "/control/static_html/html-links/context.html": {
    "title": "context.html",
    "description": "Error reading file: [Errno 2] No such file or directory: '/home/e-bliss-station-1/Projects/Unhinged/control/static_html/html-links/context.html'",
    "category": "error",
    "capabilities": [],
    "exists": false,
    "lastModified": 0,
    "size": 0
  },
  "/control/static_html/html-links/static-main.html": {
    "title": "static-main.html",
    "description": "Error reading file: [Errno 2] No such file or directory: '/home/e-bliss-station-1/Projects/Unhinged/control/static_html/html-links/static-main.html'",
    "category": "error",
    "capabilities": [],
    "exists": false,
    "lastModified": 0,
    "size": 0
  },
  "/control/static_html/html-links/dashboard.html": {
    "title": "dashboard.html",
    "description": "Error reading file: [Errno 2] No such file or directory: '/home/e-bliss-station-1/Projects/Unhinged/control/static_html/html-links/dashboard.html'",
    "category": "error",
    "capabilities": [],
    "exists": false,
    "lastModified": 0,
    "size": 0
  },
  "/control/static_html/html-links/vision.html": {
    "title": "vision.html",
    "description": "Error reading file: [Errno 2] No such file or directory: '/home/e-bliss-station-1/Projects/Unhinged/control/static_html/html-links/vision.html'",
    "category": "error",
    "capabilities": [],
    "exists": false,
    "lastModified": 0,
    "size": 0
  }
};

// Helper functions for registry access
window.getRegistryEntry = function(path) {
    return window.UNHINGED_REGISTRY[path] || null;
};

window.getAllFiles = function() {
    return Object.keys(window.UNHINGED_REGISTRY);
};

window.getFilesByCategory = function(category) {
    return Object.entries(window.UNHINGED_REGISTRY)
        .filter(([path, meta]) => meta.category === category)
        .map(([path, meta]) => ({path, ...meta}));
};

window.getExistingFiles = function() {
    return Object.entries(window.UNHINGED_REGISTRY)
        .filter(([path, meta]) => meta.exists)
        .map(([path, meta]) => ({path, ...meta}));
};

window.getMissingFiles = function() {
    return Object.entries(window.UNHINGED_REGISTRY)
        .filter(([path, meta]) => !meta.exists)
        .map(([path, meta]) => ({path, ...meta}));
};

// Kawaii ASCII TOC generator
window.generateKawaiiTOC = function() {
    const existing = window.getExistingFiles();
    const missing = window.getMissingFiles();
    
    let toc = `
╭─────────────────────────────────────╮
│  🌸 Unhinged Static HTML Files 🌸  │
╰─────────────────────────────────────╯

📁 control/static_html/
`;
    
    existing.forEach(file => {
        toc += `  ✅ ${file.title}\n`;
        toc += `     📄 ${file.path.split('/').pop()}\n`;
        if (file.description) {
            toc += `     💭 ${file.description}\n`;
        }
        toc += `\n`;
    });
    
    if (missing.length > 0) {
        toc += `\n🚨 Missing Files:\n`;
        missing.forEach(file => {
            toc += `  ❌ ${file.title}\n`;
            toc += `     📄 ${file.path.split('/').pop()}\n`;
            toc += `     💭 File not found - please create!\n\n`;
        });
    }
    
    return toc;
};

console.log('📋 Unhinged Registry loaded with', Object.keys(window.UNHINGED_REGISTRY).length, 'files');
