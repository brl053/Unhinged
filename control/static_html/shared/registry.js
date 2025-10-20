// Auto-generated registry - DO NOT EDIT MANUALLY
// Generated at: 2025-10-19T21:30:10.946154
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
  "/control/static_html/table-of-contents.html": {
    "title": "\ud83d\udcda Table of Contents",
    "description": "",
    "category": "other",
    "capabilities": [],
    "exists": true,
    "lastModified": 1760919867.4941573,
    "size": 16656
  },
  "/control/static_html/index2.html": {
    "title": "\ud83c\udf9b\ufe0f Unhinged Mission Control v2 - Tab-Based Operations Center",
    "description": "",
    "category": "other",
    "capabilities": [],
    "exists": true,
    "lastModified": 1760928152.1506603,
    "size": 40578
  },
  "/control/static_html/validate-standardization.html": {
    "title": "\ud83d\udd0d Standardization Validator - Unhinged Control Plane",
    "description": "",
    "category": "other",
    "capabilities": [],
    "exists": true,
    "lastModified": 1760919948.2730174,
    "size": 23978
  },
  "/control/static_html/persistence-platform.html": {
    "title": "\ud83d\udcbe Persistence Platform - Unified Database Management",
    "description": "",
    "category": "other",
    "capabilities": [],
    "exists": true,
    "lastModified": 1760929148.0366623,
    "size": 24686
  },
  "/control/static_html/legacy/grpc-test.html": {
    "title": "\ud83d\udd27 gRPC Direct Client Test - Unhinged Control Plane",
    "description": "",
    "category": "other",
    "capabilities": [],
    "exists": true,
    "lastModified": 1760919860.7174625,
    "size": 15390
  },
  "/control/static_html/legacy/chat.html": {
    "title": "\ud83d\udcac Chat Interface - Unhinged Control Plane",
    "description": "",
    "category": "other",
    "capabilities": [],
    "exists": true,
    "lastModified": 1760918328.320376,
    "size": 21138
  },
  "/control/static_html/legacy/accessibility-test.html": {
    "title": "\ud83e\uddea Accessibility & Responsive Design Test - Unhinged Control Plane",
    "description": "",
    "category": "other",
    "capabilities": [],
    "exists": true,
    "lastModified": 1760919587.920255,
    "size": 16102
  },
  "/control/static_html/legacy/image-test.html": {
    "title": "\ud83d\udc41\ufe0f Vision AI Test - Unhinged Multi-Modal Platform",
    "description": "",
    "category": "ai-services",
    "capabilities": [],
    "exists": true,
    "lastModified": 1760918296.8305762,
    "size": 24050
  },
  "/control/static_html/legacy/dag-control.html": {
    "title": "\ud83c\udf9b\ufe0f DAG Control Plane - Unhinged AI",
    "description": "",
    "category": "control",
    "capabilities": [],
    "exists": true,
    "lastModified": 1760918328.3154469,
    "size": 16190
  }
};

/**
 * @llm-type config
 * @llm-legend Hierarchical file structure for table-of-contents navigation
 * @llm-key Auto-generated directory tree with file metadata for browser navigation
 * @llm-map Used by table-of-contents.html for dynamic file structure display
 * @llm-axiom File structure regenerated on every make start to reflect current filesystem
 * @llm-contract Provides nested directory structure with file metadata
 * @llm-token unhinged-file-structure: Complete directory tree for navigation
 */
window.UNHINGED_FILE_STRUCTURE = {
  "control/static_html": {
    "type": "directory",
    "children": {
      "index2.html": {
        "type": "file",
        "title": "\ud83c\udf9b\ufe0f Unhinged Mission Control v2 - Tab-Based Operations Center",
        "description": "",
        "category": "other",
        "size": 40578,
        "lastModified": 1760928152.1506603,
        "exists": true
      },
      "legacy": {
        "type": "directory",
        "children": {
          "accessibility-test.html": {
            "type": "file",
            "title": "\ud83e\uddea Accessibility & Responsive Design Test - Unhinged Control Plane",
            "description": "",
            "category": "other",
            "size": 16102,
            "lastModified": 1760919587.920255,
            "exists": true
          },
          "chat.html": {
            "type": "file",
            "title": "\ud83d\udcac Chat Interface - Unhinged Control Plane",
            "description": "",
            "category": "other",
            "size": 21138,
            "lastModified": 1760918328.320376,
            "exists": true
          },
          "dag-control.html": {
            "type": "file",
            "title": "\ud83c\udf9b\ufe0f DAG Control Plane - Unhinged AI",
            "description": "",
            "category": "control",
            "size": 16190,
            "lastModified": 1760918328.3154469,
            "exists": true
          },
          "grpc-test.html": {
            "type": "file",
            "title": "\ud83d\udd27 gRPC Direct Client Test - Unhinged Control Plane",
            "description": "",
            "category": "other",
            "size": 15390,
            "lastModified": 1760919860.7174625,
            "exists": true
          },
          "image-test.html": {
            "type": "file",
            "title": "\ud83d\udc41\ufe0f Vision AI Test - Unhinged Multi-Modal Platform",
            "description": "",
            "category": "ai-services",
            "size": 24050,
            "lastModified": 1760918296.8305762,
            "exists": true
          }
        }
      },
      "network": {
        "type": "directory",
        "children": {
          "clients": {
            "type": "directory",
            "children": {
              "audio-client.js": {
                "type": "file",
                "title": "audio-client.js",
                "description": ".JS file",
                "category": "resource",
                "size": 1767,
                "lastModified": 1760865373.3976326,
                "exists": true
              },
              "chat-client.js": {
                "type": "file",
                "title": "chat-client.js",
                "description": ".JS file",
                "category": "resource",
                "size": 2508,
                "lastModified": 1760865373.3966327,
                "exists": true
              },
              "tts-client.js": {
                "type": "file",
                "title": "tts-client.js",
                "description": ".JS file",
                "category": "resource",
                "size": 2101,
                "lastModified": 1760865373.3976326,
                "exists": true
              },
              "vision-client.js": {
                "type": "file",
                "title": "vision-client.js",
                "description": ".JS file",
                "category": "resource",
                "size": 1938,
                "lastModified": 1760865373.3976326,
                "exists": true
              }
            }
          },
          "generate-clients.js": {
            "type": "file",
            "title": "generate-clients.js",
            "description": ".JS file",
            "category": "resource",
            "size": 6930,
            "lastModified": 1760865367.8506877,
            "exists": true
          },
          "grpc-client.js": {
            "type": "file",
            "title": "grpc-client.js",
            "description": ".JS file",
            "category": "resource",
            "size": 7218,
            "lastModified": 1760866104.3634655,
            "exists": true
          },
          "queries": {
            "type": "directory",
            "children": {
              "audio.js": {
                "type": "file",
                "title": "audio.js",
                "description": ".JS file",
                "category": "resource",
                "size": 705,
                "lastModified": 1760865373.3976326,
                "exists": true
              },
              "chat.js": {
                "type": "file",
                "title": "chat.js",
                "description": ".JS file",
                "category": "resource",
                "size": 1921,
                "lastModified": 1760865373.3966327,
                "exists": true
              },
              "tts.js": {
                "type": "file",
                "title": "tts.js",
                "description": ".JS file",
                "category": "resource",
                "size": 1391,
                "lastModified": 1760865373.3976326,
                "exists": true
              },
              "vision.js": {
                "type": "file",
                "title": "vision.js",
                "description": ".JS file",
                "category": "resource",
                "size": 1054,
                "lastModified": 1760865373.3976326,
                "exists": true
              }
            }
          }
        }
      },
      "persistence-platform.html": {
        "type": "file",
        "title": "\ud83d\udcbe Persistence Platform - Unified Database Management",
        "description": "",
        "category": "other",
        "size": 24686,
        "lastModified": 1760929148.0366623,
        "exists": true
      },
      "shared": {
        "type": "directory",
        "children": {
          "README.md": {
            "type": "file",
            "title": "README.md",
            "description": ".MD file",
            "category": "resource",
            "size": 4076,
            "lastModified": 1760830716.0698452,
            "exists": true
          },
          "TOKEN_MAPPINGS.md": {
            "type": "file",
            "title": "TOKEN_MAPPINGS.md",
            "description": ".MD file",
            "category": "resource",
            "size": 5980,
            "lastModified": 1760915038.0957146,
            "exists": true
          },
          "api-clients.js": {
            "type": "file",
            "title": "api-clients.js",
            "description": ".JS file",
            "category": "resource",
            "size": 1749,
            "lastModified": 1760934609.8521924,
            "exists": true
          },
          "api-integration.js": {
            "type": "file",
            "title": "api-integration.js",
            "description": ".JS file",
            "category": "resource",
            "size": 10409,
            "lastModified": 1760928139.2517772,
            "exists": true
          },
          "components.js": {
            "type": "file",
            "title": "components.js",
            "description": ".JS file",
            "category": "resource",
            "size": 29254,
            "lastModified": 1760926065.953242,
            "exists": true
          },
          "config.js": {
            "type": "file",
            "title": "config.js",
            "description": ".JS file",
            "category": "resource",
            "size": 9950,
            "lastModified": 1760864062.955377,
            "exists": true
          },
          "registry.js": {
            "type": "file",
            "title": "registry.js",
            "description": ".JS file",
            "category": "resource",
            "size": 17316,
            "lastModified": 1760934540.5332897,
            "exists": true
          },
          "service-orchestration.js": {
            "type": "file",
            "title": "service-orchestration.js",
            "description": ".JS file",
            "category": "resource",
            "size": 12747,
            "lastModified": 1760860400.1203165,
            "exists": true
          },
          "styles.css": {
            "type": "file",
            "title": "styles.css",
            "description": ".CSS file",
            "category": "resource",
            "size": 23229,
            "lastModified": 1760925622.0519125,
            "exists": true
          },
          "theme.css": {
            "type": "file",
            "title": "theme.css",
            "description": ".CSS file",
            "category": "resource",
            "size": 11888,
            "lastModified": 1760918272.611923,
            "exists": true
          }
        }
      },
      "standardize-components.sh": {
        "type": "file",
        "title": "standardize-components.sh",
        "description": ".SH file",
        "category": "resource",
        "size": 2860,
        "lastModified": 1760918317.9457228,
        "exists": true
      },
      "table-of-contents.html": {
        "type": "file",
        "title": "\ud83d\udcda Table of Contents",
        "description": "",
        "category": "other",
        "size": 16656,
        "lastModified": 1760919867.4941573,
        "exists": true
      },
      "update-navigation.sh": {
        "type": "file",
        "title": "update-navigation.sh",
        "description": ".SH file",
        "category": "resource",
        "size": 1945,
        "lastModified": 1760918175.328715,
        "exists": true
      },
      "validate-design-tokens.js": {
        "type": "file",
        "title": "validate-design-tokens.js",
        "description": ".JS file",
        "category": "resource",
        "size": 4354,
        "lastModified": 1760916818.356188,
        "exists": true
      },
      "validate-standardization.html": {
        "type": "file",
        "title": "\ud83d\udd0d Standardization Validator - Unhinged Control Plane",
        "description": "",
        "category": "other",
        "size": 23978,
        "lastModified": 1760919948.2730174,
        "exists": true
      }
    }
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

// Helper functions for file structure access
window.getFileStructure = function() {
    return window.UNHINGED_FILE_STRUCTURE;
};

window.getDirectoryContents = function(path) {
    const parts = path.split('/').filter(p => p);
    let current = window.UNHINGED_FILE_STRUCTURE;

    for (const part of parts) {
        if (current && current[part] && current[part].children) {
            current = current[part].children;
        } else {
            return null;
        }
    }

    return current;
};

window.findFilesByPattern = function(pattern) {
    const regex = new RegExp(pattern, 'i');
    const results = [];

    function searchTree(node, path = '') {
        if (!node || typeof node !== 'object') return;

        Object.entries(node).forEach(([name, item]) => {
            const fullPath = path ? `${path}/${name}` : name;

            if (item.type === 'file' && regex.test(name)) {
                results.push({
                    path: fullPath,
                    name: name,
                    ...item
                });
            } else if (item.type === 'directory' && item.children) {
                searchTree(item.children, fullPath);
            }
        });
    }

    searchTree(window.UNHINGED_FILE_STRUCTURE);
    return results;
};

console.log('📋 Unhinged Registry loaded with', Object.keys(window.UNHINGED_REGISTRY).length, 'files');
console.log('🗂️ File structure loaded with', Object.keys(window.UNHINGED_FILE_STRUCTURE).length, 'root directories');
