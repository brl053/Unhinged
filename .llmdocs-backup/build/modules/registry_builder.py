#!/usr/bin/env python3

"""
@llm-type build-module
@llm-legend Static HTML registry generation module for control plane browser interface
@llm-key Scans control/static_html directory and generates JavaScript registry following BuildModule interface
@llm-map Integrates with existing build orchestrator as specialized module for static asset management
@llm-axiom Must follow BuildModule contract and provide caching, validation, and artifact management
@llm-contract Implements BuildModule interface with build(), cache_key(), and validate() methods
@llm-token registry-builder: Build module for static HTML file registry generation

Registry Builder Module

Specialized build module that scans the control/static_html directory and generates
a JavaScript registry file for browser consumption. Integrates with the existing
build orchestrator to provide caching, dependency tracking, and performance monitoring.

Features:
- Recursive HTML file discovery
- Metadata extraction from HTML files
- JavaScript registry generation
- Content-based caching
- Build artifact management

Author: Unhinged Team
Version: 1.0.0
Date: 2025-10-19
"""

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

try:
    from . import BuildModule, BuildContext, BuildModuleResult, BuildArtifact
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from __init__ import BuildModule, BuildContext, BuildModuleResult, BuildArtifact

class RegistryBuilder(BuildModule):
    """
    @llm-type build-module
    @llm-legend Generates JavaScript registry of static HTML files for browser navigation
    @llm-key Scans filesystem, extracts HTML metadata, generates registry.js with kawaii ASCII TOC
    @llm-map Integrates with build orchestrator for caching and dependency management
    @llm-axiom Registry must be generated before browser access to ensure accurate file discovery
    @llm-contract Returns BuildResult with registry.js artifact or error details
    @llm-token static-html-registry: Browser-consumable file registry for navigation
    """
    
    def __init__(self):
        self.name = "registry_builder"
        self.description = "Static HTML registry generator"
        
    def can_handle(self, context: BuildContext) -> bool:
        """
        @llm-type function
        @llm-legend Determines if this module can handle the given build context
        @llm-key Checks for registry-related target names and static_html directory existence
        @llm-map Called by build orchestrator during module selection phase
        @llm-contract Returns True for registry targets, False otherwise
        """
        registry_targets = ["generate-registry", "registry", "static-html-registry"]
        return (
            context.target_name in registry_targets or
            "registry" in context.target_name.lower()
        )
    
    def get_dependencies(self, context: BuildContext) -> List[str]:
        """
        @llm-type function
        @llm-legend Returns list of files that affect registry generation
        @llm-key Scans control/static_html for all HTML files to establish dependencies
        @llm-map Used by build orchestrator for cache invalidation and dependency tracking
        @llm-contract Returns list of file paths that trigger registry regeneration when changed
        """
        static_html_dir = context.project_root / "control" / "static_html"
        dependencies = []
        
        if static_html_dir.exists():
            # Include all HTML files as dependencies
            for html_file in static_html_dir.rglob("*.html"):
                dependencies.append(str(html_file.relative_to(context.project_root)))
        
        return dependencies
    
    def calculate_cache_key(self, context: BuildContext) -> str:
        """
        @llm-type function
        @llm-legend Generates content-based cache key for registry generation
        @llm-key Combines file modification times and content hashes of all HTML files
        @llm-map Used by build orchestrator for intelligent cache invalidation
        @llm-contract Returns stable cache key that changes only when HTML files change
        """
        static_html_dir = context.project_root / "control" / "static_html"
        
        if not static_html_dir.exists():
            return "no-static-html-dir"
        
        # Collect file modification times and sizes
        file_info = []
        for html_file in sorted(static_html_dir.rglob("*.html")):
            try:
                stat = html_file.stat()
                file_info.append(f"{html_file.name}:{stat.st_mtime}:{stat.st_size}")
            except OSError:
                file_info.append(f"{html_file.name}:missing")
        
        # Create hash of all file information
        import hashlib
        content = "|".join(file_info)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def extract_html_metadata(self, file_path: Path) -> Dict[str, any]:
        """
        @llm-type function
        @llm-legend Extracts title, description, and metadata from HTML file
        @llm-key Parses HTML content using regex to find title and meta tags
        @llm-map Helper function for registry generation process
        @llm-contract Returns metadata dict with title, description, category, and file info
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else file_path.name
            
            # Extract description from meta tag
            desc_match = re.search(
                r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']', 
                content, 
                re.IGNORECASE
            )
            description = desc_match.group(1) if desc_match else ""
            
            # Determine category from filename and content
            filename = file_path.name.lower()
            if 'dag' in filename or 'control' in filename:
                category = 'control'
            elif any(x in filename for x in ['text', 'image', 'voice', 'ai']):
                category = 'ai-services'
            elif filename == 'index.html':
                category = 'root'
            else:
                category = 'other'
            
            # Extract capabilities from content (look for service config or capabilities)
            capabilities = []
            if 'capabilities' in content:
                cap_match = re.search(r'capabilities["\']?\s*:\s*\[(.*?)\]', content, re.DOTALL)
                if cap_match:
                    caps_text = cap_match.group(1)
                    capabilities = [
                        cap.strip().strip('\'"') 
                        for cap in caps_text.split(',') 
                        if cap.strip()
                    ]
            
            return {
                'title': title,
                'description': description,
                'category': category,
                'capabilities': capabilities,
                'exists': True,
                'lastModified': file_path.stat().st_mtime,
                'size': file_path.stat().st_size
            }
            
        except Exception as e:
            return {
                'title': file_path.name,
                'description': f"Error reading file: {e}",
                'category': 'error',
                'capabilities': [],
                'exists': False,
                'lastModified': 0,
                'size': 0
            }
    
    def scan_static_html_directory(self, project_root: Path) -> Dict[str, Dict]:
        """
        @llm-type function
        @llm-legend Recursively scans control/static_html for HTML files and extracts metadata
        @llm-key Walks filesystem tree, processes each HTML file, builds registry dictionary
        @llm-map Core scanning function that builds the complete file registry
        @llm-contract Returns registry dict with absolute paths as keys and metadata as values
        """
        static_html_dir = project_root / "control" / "static_html"
        registry = {}

        if not static_html_dir.exists():
            print(f"❌ Directory not found: {static_html_dir}")
            return registry

        # Scan for all HTML files
        for html_file in static_html_dir.rglob("*.html"):
            # Convert to absolute path from monorepo root
            abs_path = f"/{html_file.relative_to(project_root).as_posix()}"

            # Extract metadata
            metadata = self.extract_html_metadata(html_file)

            registry[abs_path] = metadata
            print(f"✅ Registered: {abs_path}")

        return registry

    def build_file_structure(self, project_root: Path) -> Dict:
        """
        @llm-type function
        @llm-legend Builds hierarchical file structure for table-of-contents navigation
        @llm-key Scans control/static_html directory and creates nested structure with metadata
        @llm-map Generates browser-consumable file tree for navigation components
        @llm-contract Returns nested dict with directories and files organized hierarchically
        """
        static_html_dir = project_root / "control" / "static_html"

        if not static_html_dir.exists():
            return {}

        def build_tree(directory: Path, relative_to: Path) -> Dict:
            """Recursively build directory tree structure"""
            tree = {
                'type': 'directory',
                'children': {}
            }

            try:
                # Process all items in directory
                for item in sorted(directory.iterdir()):
                    if item.name.startswith('.'):
                        continue  # Skip hidden files

                    relative_path = item.relative_to(relative_to)

                    if item.is_dir():
                        # Recursively process subdirectory
                        tree['children'][item.name] = build_tree(item, relative_to)
                    elif item.is_file() and item.suffix.lower() == '.html':
                        # Extract metadata for HTML files
                        metadata = self.extract_html_metadata(item)
                        tree['children'][item.name] = {
                            'type': 'file',
                            'title': metadata.get('title', item.name),
                            'description': metadata.get('description', ''),
                            'category': metadata.get('category', 'general'),
                            'size': metadata.get('size', 0),
                            'lastModified': metadata.get('lastModified', 0),
                            'exists': metadata.get('exists', True)
                        }
                    elif item.is_file():
                        # Non-HTML files
                        stat = item.stat()
                        tree['children'][item.name] = {
                            'type': 'file',
                            'title': item.name,
                            'description': f'{item.suffix.upper()} file',
                            'category': 'resource',
                            'size': stat.st_size,
                            'lastModified': stat.st_mtime,
                            'exists': True
                        }
            except PermissionError:
                print(f"⚠️ Permission denied accessing: {directory}")

            return tree

        # Build the complete file structure
        root_structure = {
            'control/static_html': build_tree(static_html_dir, project_root)
        }

        return root_structure
    
    def generate_registry_js(self, registry: Dict[str, Dict], file_structure: Dict = None) -> str:
        """
        @llm-type function
        @llm-legend Generates JavaScript registry file with helper functions and kawaii ASCII TOC
        @llm-key Creates JavaScript module with registry object and utility functions
        @llm-map Converts Python registry dict to browser-consumable JavaScript
        @llm-contract Returns valid JavaScript code with UNHINGED_REGISTRY global
        """
        js_content = f'''// Auto-generated registry - DO NOT EDIT MANUALLY
// Generated at: {datetime.now().isoformat()}
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
window.UNHINGED_REGISTRY = {json.dumps(registry, indent=2)};

/**
 * @llm-type config
 * @llm-legend Hierarchical file structure for table-of-contents navigation
 * @llm-key Auto-generated directory tree with file metadata for browser navigation
 * @llm-map Used by table-of-contents.html for dynamic file structure display
 * @llm-axiom File structure regenerated on every make start to reflect current filesystem
 * @llm-contract Provides nested directory structure with file metadata
 * @llm-token unhinged-file-structure: Complete directory tree for navigation
 */
window.UNHINGED_FILE_STRUCTURE = {json.dumps(file_structure or {}, indent=2)};

// Helper functions for registry access
window.getRegistryEntry = function(path) {{
    return window.UNHINGED_REGISTRY[path] || null;
}};

window.getAllFiles = function() {{
    return Object.keys(window.UNHINGED_REGISTRY);
}};

window.getFilesByCategory = function(category) {{
    return Object.entries(window.UNHINGED_REGISTRY)
        .filter(([path, meta]) => meta.category === category)
        .map(([path, meta]) => ({{path, ...meta}}));
}};

window.getExistingFiles = function() {{
    return Object.entries(window.UNHINGED_REGISTRY)
        .filter(([path, meta]) => meta.exists)
        .map(([path, meta]) => ({{path, ...meta}}));
}};

window.getMissingFiles = function() {{
    return Object.entries(window.UNHINGED_REGISTRY)
        .filter(([path, meta]) => !meta.exists)
        .map(([path, meta]) => ({{path, ...meta}}));
}};

// Kawaii ASCII TOC generator
window.generateKawaiiTOC = function() {{
    const existing = window.getExistingFiles();
    const missing = window.getMissingFiles();
    
    let toc = `
╭─────────────────────────────────────╮
│  🌸 Unhinged Static HTML Files 🌸  │
╰─────────────────────────────────────╯

📁 control/static_html/
`;
    
    existing.forEach(file => {{
        toc += `  ✅ ${{file.title}}\\n`;
        toc += `     📄 ${{file.path.split('/').pop()}}\\n`;
        if (file.description) {{
            toc += `     💭 ${{file.description}}\\n`;
        }}
        toc += `\\n`;
    }});
    
    if (missing.length > 0) {{
        toc += `\\n🚨 Missing Files:\\n`;
        missing.forEach(file => {{
            toc += `  ❌ ${{file.title}}\\n`;
            toc += `     📄 ${{file.path.split('/').pop()}}\\n`;
            toc += `     💭 File not found - please create!\\n\\n`;
        }});
    }}
    
    return toc;
}};

// Helper functions for file structure access
window.getFileStructure = function() {{
    return window.UNHINGED_FILE_STRUCTURE;
}};

window.getDirectoryContents = function(path) {{
    const parts = path.split('/').filter(p => p);
    let current = window.UNHINGED_FILE_STRUCTURE;

    for (const part of parts) {{
        if (current && current[part] && current[part].children) {{
            current = current[part].children;
        }} else {{
            return null;
        }}
    }}

    return current;
}};

window.findFilesByPattern = function(pattern) {{
    const regex = new RegExp(pattern, 'i');
    const results = [];

    function searchTree(node, path = '') {{
        if (!node || typeof node !== 'object') return;

        Object.entries(node).forEach(([name, item]) => {{
            const fullPath = path ? `${{path}}/${{name}}` : name;

            if (item.type === 'file' && regex.test(name)) {{
                results.push({{
                    path: fullPath,
                    name: name,
                    ...item
                }});
            }} else if (item.type === 'directory' && item.children) {{
                searchTree(item.children, fullPath);
            }}
        }});
    }}

    searchTree(window.UNHINGED_FILE_STRUCTURE);
    return results;
}};

console.log('📋 Unhinged Registry loaded with', Object.keys(window.UNHINGED_REGISTRY).length, 'files');
console.log('🗂️ File structure loaded with', Object.keys(window.UNHINGED_FILE_STRUCTURE).length, 'root directories');
'''
        
        return js_content
    
    def build(self, context: BuildContext) -> BuildModuleResult:
        """
        @llm-type function
        @llm-legend Main build function that generates the static HTML registry
        @llm-key Scans filesystem, generates JavaScript registry, writes output file
        @llm-map Called by build orchestrator to execute registry generation
        @llm-contract Returns BuildModuleResult with success status and generated artifacts
        """
        start_time = time.time()
        
        try:
            print("🔍 Scanning control/static_html directory...")
            registry = self.scan_static_html_directory(context.project_root)

            print(f"📊 Found {len(registry)} HTML files")

            print("🗂️ Building file structure...")
            file_structure = self.build_file_structure(context.project_root)

            print(f"📁 Built structure for {len(file_structure)} root directories")

            # Generate JavaScript content
            js_content = self.generate_registry_js(registry, file_structure)
            
            # Write to output file in /generated directory
            output_path = context.project_root / "generated" / "static_html" / "registry.js"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(js_content)
            
            # Create build artifact
            artifact = BuildArtifact(
                path=output_path,
                type="javascript",
                size=len(js_content.encode('utf-8')),
                checksum=self.calculate_cache_key(context),
                metadata={
                    'files_scanned': len(registry),
                    'output_format': 'javascript',
                    'generator': 'registry_builder'
                }
            )
            
            duration = time.time() - start_time
            
            print(f"✅ Registry generated: {output_path}")
            print(f"🎉 Registry build completed in {duration:.2f}s")
            
            return BuildModuleResult(
                success=True,
                duration=duration,
                artifacts=[artifact],
                cache_hit=False,
                metrics={
                    'files_scanned': len(registry),
                    'output_size': len(js_content),
                    'categories': list(set(meta.get('category', 'unknown') for meta in registry.values()))
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            
            return BuildModuleResult(
                success=False,
                duration=duration,
                error_message=f"Registry generation failed: {e}",
                artifacts=[],
                cache_hit=False
            )
    
    def clean(self, context: BuildContext) -> bool:
        """
        @llm-type function
        @llm-legend Removes generated registry.js file
        @llm-key Deletes output file to force regeneration on next build
        @llm-map Called by build orchestrator during clean operations
        @llm-contract Returns True if cleanup successful, False otherwise
        """
        try:
            output_path = context.project_root / "generated" / "static_html" / "registry.js"
            if output_path.exists():
                output_path.unlink()
                print(f"🗑️ Removed: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to clean registry: {e}")
            return False
