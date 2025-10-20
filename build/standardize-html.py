#!/usr/bin/env python3
"""
HTML Standardization Tool

Standardizes all HTML files in control/static_html to use consistent:
- Navigation structure
- CSS imports
- Layout patterns
- Design tokens

This fixes the inconsistent mess of HTML files to follow a unified design system.
"""

import os
import re
from pathlib import Path
from typing import Dict, List

class HTMLStandardizer:
    """Standardizes HTML files to use consistent design system."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.html_dir = project_root / "control" / "static_html"
        
        # Standard HTML template structure
        self.standard_head = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="shared/theme.css">
    <link rel="stylesheet" href="shared/styles.css">
    <script src="shared/config.js"></script>
    <script src="../generated/static_html/registry.js"></script>
    <script src="shared/components.js"></script>
    <script src="../generated/static_html/api-clients.js"></script>
    <script src="shared/api-integration.js"></script>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>{icon}</text></svg>">
</head>
<body>
    <div class="container">
        <!-- Navigation - Standardized Component -->
        <div id="nav-container" data-component="navigation" data-active="{nav_active}"></div>
        
        <!-- Page Header - Standardized Component -->
        <div id="header-container" data-component="page-header"
             data-title="{page_title}"
             data-subtitle="{page_subtitle}"
             data-icon="{icon}"></div>
        
        <!-- Main Content -->
        <main class="main-content">
{content}
        </main>
        
        <!-- Footer - Standardized Component -->
        <div id="footer-container" data-component="footer"></div>
    </div>
</body>
</html>'''
    
    def get_page_config(self, filename: str) -> Dict[str, str]:
        """Get standardized configuration for each page."""
        configs = {
            'index.html': {
                'title': '🎛️ Unhinged Mission Control',
                'icon': '🎛️',
                'nav_active': 'control',
                'page_title': 'Mission Control',
                'page_subtitle': 'System Operations Center'
            },
            'table-of-contents.html': {
                'title': '📚 Table of Contents',
                'icon': '📚',
                'nav_active': 'toc',
                'page_title': 'Interface Directory',
                'page_subtitle': 'Complete Platform Navigation'
            },
            'blog-editor.html': {
                'title': '✍️ Blog Editor',
                'icon': '✍️',
                'nav_active': 'blog',
                'page_title': 'Blog Editor',
                'page_subtitle': 'Content Management System'
            },
            'blog-list.html': {
                'title': '📝 Blog Posts',
                'icon': '📝',
                'nav_active': 'blog',
                'page_title': 'Blog Posts',
                'page_subtitle': 'Content Library'
            },
            'persistence-platform.html': {
                'title': '🔍 Persistence Platform',
                'icon': '🔍',
                'nav_active': 'persistence',
                'page_title': 'Persistence Platform',
                'page_subtitle': 'Database Operations'
            },
            'validate-standardization.html': {
                'title': '✅ Validation',
                'icon': '✅',
                'nav_active': 'validation',
                'page_title': 'Design Validation',
                'page_subtitle': 'Component Standardization'
            },
            'test-blog-integration.html': {
                'title': '🧪 Blog Testing',
                'icon': '🧪',
                'nav_active': 'testing',
                'page_title': 'Blog Integration Test',
                'page_subtitle': 'End-to-End Testing'
            }
        }
        
        return configs.get(filename, {
            'title': f'🔧 {filename}',
            'icon': '🔧',
            'nav_active': 'other',
            'page_title': filename.replace('.html', '').replace('-', ' ').title(),
            'page_subtitle': 'Unhinged Platform'
        })
    
    def extract_main_content(self, html_content: str) -> str:
        """Extract the main content from existing HTML, removing head/nav/footer."""
        # Remove everything before <body> and after </body>
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL)
        if not body_match:
            return "<!-- No content found -->"
        
        body_content = body_match.group(1)
        
        # Remove common wrapper elements
        body_content = re.sub(r'<div[^>]*class="container"[^>]*>', '', body_content)
        body_content = re.sub(r'</div>\s*$', '', body_content.strip())
        
        # Remove navigation elements
        body_content = re.sub(r'<div[^>]*id="nav-container"[^>]*></div>', '', body_content)
        body_content = re.sub(r'<nav[^>]*>.*?</nav>', '', body_content, flags=re.DOTALL)
        
        # Remove header elements
        body_content = re.sub(r'<div[^>]*id="header-container"[^>]*[^>]*></div>', '', body_content)
        body_content = re.sub(r'<header[^>]*>.*?</header>', '', body_content, flags=re.DOTALL)
        
        # Remove footer elements
        body_content = re.sub(r'<div[^>]*id="footer-container"[^>]*></div>', '', body_content)
        body_content = re.sub(r'<footer[^>]*>.*?</footer>', '', body_content, flags=re.DOTALL)
        
        # Clean up whitespace
        body_content = re.sub(r'\n\s*\n\s*\n', '\n\n', body_content)
        body_content = body_content.strip()
        
        return body_content
    
    def standardize_file(self, file_path: Path) -> bool:
        """Standardize a single HTML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Get page configuration
            config = self.get_page_config(file_path.name)
            
            # Extract main content
            main_content = self.extract_main_content(original_content)
            
            # Generate standardized HTML
            standardized_html = self.standard_head.format(
                title=config['title'],
                icon=config['icon'],
                nav_active=config['nav_active'],
                page_title=config['page_title'],
                page_subtitle=config['page_subtitle'],
                content=main_content
            )
            
            # Write standardized file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(standardized_html)
            
            print(f"✅ Standardized: {file_path.name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to standardize {file_path.name}: {e}")
            return False
    
    def standardize_all(self) -> None:
        """Standardize all HTML files in the directory."""
        print("🔧 Starting HTML standardization...")
        print(f"📁 Directory: {self.html_dir}")
        
        html_files = list(self.html_dir.glob("*.html"))
        
        if not html_files:
            print("⚠️  No HTML files found")
            return
        
        success_count = 0
        for file_path in html_files:
            if self.standardize_file(file_path):
                success_count += 1
        
        print(f"\n📊 Standardization complete:")
        print(f"   ✅ Success: {success_count}/{len(html_files)} files")
        print(f"   ❌ Failed: {len(html_files) - success_count}/{len(html_files)} files")
        
        if success_count == len(html_files):
            print("🎉 All HTML files now follow consistent design system!")
        else:
            print("⚠️  Some files failed standardization - check errors above")

def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    standardizer = HTMLStandardizer(project_root)
    standardizer.standardize_all()

if __name__ == '__main__':
    main()
