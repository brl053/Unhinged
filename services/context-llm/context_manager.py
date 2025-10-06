#!/usr/bin/env python3
"""
Context Manager for Project Documentation and Codebase Analysis
Provides contextual information to enhance vision analysis prompts
"""

import os
import logging
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import hashlib

# Document processing
import markdown
from pathlib import Path
import git

logger = logging.getLogger(__name__)

class ContextType(Enum):
    DOCUMENTATION = "documentation"
    CODEBASE = "codebase"
    UI_COMPONENTS = "ui_components"
    API_ENDPOINTS = "api_endpoints"
    ARCHITECTURE = "architecture"

@dataclass
class ContextItem:
    id: str
    type: ContextType
    title: str
    content: str
    file_path: str
    last_modified: float
    tags: List[str]
    relevance_score: float = 0.0

@dataclass
class ContextQuery:
    query: str
    context_types: List[ContextType]
    max_results: int = 10
    min_relevance: float = 0.3

class ProjectContextManager:
    """
    Manages project context including documentation, codebase, and UI components
    """
    
    def __init__(self, project_root: str = "/workspace"):
        self.project_root = Path(project_root)
        self.context_cache: Dict[str, ContextItem] = {}
        self.last_scan_time = 0
        self.scan_interval = 300  # 5 minutes
        
        # Initialize context sources
        self.docs_path = self.project_root / "docs"
        self.frontend_path = self.project_root / "frontend"
        self.backend_path = self.project_root / "backend"
        
        logger.info(f"Initialized ProjectContextManager for {project_root}")
    
    def scan_project_context(self, force_refresh: bool = False) -> Dict[str, int]:
        """
        Scan the project for contextual information
        """
        current_time = time.time()
        
        if not force_refresh and (current_time - self.last_scan_time) < self.scan_interval:
            logger.debug("Using cached context data")
            return self._get_context_stats()
        
        logger.info("Scanning project context...")
        start_time = time.time()
        
        # Clear old cache
        self.context_cache.clear()
        
        # Scan different context sources
        stats = {
            'documentation': self._scan_documentation(),
            'ui_components': self._scan_ui_components(),
            'api_endpoints': self._scan_api_endpoints(),
            'architecture': self._scan_architecture_docs()
        }
        
        self.last_scan_time = current_time
        scan_time = time.time() - start_time
        
        logger.info(f"Context scan completed in {scan_time:.2f}s: {sum(stats.values())} items")
        return stats
    
    def _scan_documentation(self) -> int:
        """Scan documentation files"""
        count = 0
        
        if not self.docs_path.exists():
            logger.warning(f"Documentation path not found: {self.docs_path}")
            return count
        
        # Scan markdown files
        for md_file in self.docs_path.rglob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                
                # Extract title from first heading or filename
                title = self._extract_title_from_markdown(content) or md_file.stem
                
                # Generate tags from path and content
                tags = self._generate_tags_from_path(md_file) + self._extract_tags_from_content(content)
                
                context_item = ContextItem(
                    id=self._generate_id(str(md_file)),
                    type=ContextType.DOCUMENTATION,
                    title=title,
                    content=content[:2000],  # Limit content size
                    file_path=str(md_file.relative_to(self.project_root)),
                    last_modified=md_file.stat().st_mtime,
                    tags=tags
                )
                
                self.context_cache[context_item.id] = context_item
                count += 1
                
            except Exception as e:
                logger.warning(f"Failed to process {md_file}: {e}")
        
        return count
    
    def _scan_ui_components(self) -> int:
        """Scan UI components for context"""
        count = 0
        
        if not self.frontend_path.exists():
            logger.warning(f"Frontend path not found: {self.frontend_path}")
            return count
        
        # Scan React/TypeScript components
        component_patterns = ["*.tsx", "*.jsx", "*.ts", "*.js"]
        
        for pattern in component_patterns:
            for component_file in (self.frontend_path / "src").rglob(pattern):
                try:
                    content = component_file.read_text(encoding='utf-8')
                    
                    # Skip if not a component file
                    if not self._is_component_file(content):
                        continue
                    
                    # Extract component info
                    component_name = self._extract_component_name(component_file, content)
                    component_props = self._extract_component_props(content)
                    
                    # Create context item
                    context_item = ContextItem(
                        id=self._generate_id(str(component_file)),
                        type=ContextType.UI_COMPONENTS,
                        title=f"Component: {component_name}",
                        content=self._summarize_component(content, component_props),
                        file_path=str(component_file.relative_to(self.project_root)),
                        last_modified=component_file.stat().st_mtime,
                        tags=['ui', 'component', component_name.lower()] + self._extract_ui_tags(content)
                    )
                    
                    self.context_cache[context_item.id] = context_item
                    count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to process component {component_file}: {e}")
        
        return count
    
    def _scan_api_endpoints(self) -> int:
        """Scan API endpoints for context"""
        count = 0
        
        # Scan Kotlin controllers
        if self.backend_path.exists():
            for controller_file in (self.backend_path / "src").rglob("*Controller.kt"):
                try:
                    content = controller_file.read_text(encoding='utf-8')
                    endpoints = self._extract_kotlin_endpoints(content)
                    
                    for endpoint in endpoints:
                        context_item = ContextItem(
                            id=self._generate_id(f"{controller_file}_{endpoint['path']}"),
                            type=ContextType.API_ENDPOINTS,
                            title=f"API: {endpoint['method']} {endpoint['path']}",
                            content=endpoint['description'],
                            file_path=str(controller_file.relative_to(self.project_root)),
                            last_modified=controller_file.stat().st_mtime,
                            tags=['api', 'endpoint', endpoint['method'].lower()]
                        )
                        
                        self.context_cache[context_item.id] = context_item
                        count += 1
                        
                except Exception as e:
                    logger.warning(f"Failed to process controller {controller_file}: {e}")
        
        return count
    
    def _scan_architecture_docs(self) -> int:
        """Scan architecture documentation"""
        count = 0
        
        architecture_files = [
            "architecture/*.md",
            "README.md",
            "ARCHITECTURE.md",
            "docs/architecture/*.md"
        ]
        
        for pattern in architecture_files:
            for arch_file in self.project_root.rglob(pattern):
                try:
                    content = arch_file.read_text(encoding='utf-8')
                    
                    context_item = ContextItem(
                        id=self._generate_id(str(arch_file)),
                        type=ContextType.ARCHITECTURE,
                        title=f"Architecture: {arch_file.stem}",
                        content=content[:3000],  # Larger content for architecture docs
                        file_path=str(arch_file.relative_to(self.project_root)),
                        last_modified=arch_file.stat().st_mtime,
                        tags=['architecture', 'design'] + self._extract_architecture_tags(content)
                    )
                    
                    self.context_cache[context_item.id] = context_item
                    count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to process architecture doc {arch_file}: {e}")
        
        return count
    
    def query_context(self, query: ContextQuery) -> List[ContextItem]:
        """
        Query context based on search criteria
        """
        # Ensure context is up to date
        self.scan_project_context()
        
        # Filter by context types
        filtered_items = [
            item for item in self.context_cache.values()
            if item.type in query.context_types
        ]
        
        # Calculate relevance scores
        for item in filtered_items:
            item.relevance_score = self._calculate_relevance(query.query, item)
        
        # Filter by minimum relevance and sort
        relevant_items = [
            item for item in filtered_items
            if item.relevance_score >= query.min_relevance
        ]
        
        relevant_items.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return relevant_items[:query.max_results]
    
    def get_ui_context_for_screenshot(self, image_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get UI-specific context for screenshot analysis
        """
        ui_query = ContextQuery(
            query="ui components forms buttons interface",
            context_types=[ContextType.UI_COMPONENTS, ContextType.DOCUMENTATION],
            max_results=5
        )
        
        ui_context = self.query_context(ui_query)
        
        return {
            'ui_framework': 'React + TypeScript',
            'component_library': 'Custom Design System',
            'common_patterns': [item.title for item in ui_context[:3]],
            'ui_components': [
                {
                    'name': item.title,
                    'description': item.content[:200],
                    'tags': item.tags
                }
                for item in ui_context if item.type == ContextType.UI_COMPONENTS
            ]
        }
    
    def get_project_context_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the project context
        """
        self.scan_project_context()
        
        return {
            'project_type': 'Full-stack web application',
            'frontend_framework': 'React 19 + TypeScript',
            'backend_framework': 'Kotlin + Ktor',
            'architecture': 'Microservices with Clean Architecture',
            'total_context_items': len(self.context_cache),
            'context_breakdown': self._get_context_stats(),
            'last_updated': self.last_scan_time
        }
    
    def _generate_id(self, content: str) -> str:
        """Generate unique ID for content"""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _extract_title_from_markdown(self, content: str) -> Optional[str]:
        """Extract title from markdown content"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return None
    
    def _generate_tags_from_path(self, file_path: Path) -> List[str]:
        """Generate tags from file path"""
        parts = file_path.parts
        tags = []
        
        for part in parts:
            if part not in ['docs', 'src', 'components']:
                tags.append(part.lower().replace('-', '_'))
        
        return tags[:3]  # Limit tags
    
    def _extract_tags_from_content(self, content: str) -> List[str]:
        """Extract tags from content"""
        # Simple keyword extraction
        keywords = ['api', 'component', 'service', 'database', 'frontend', 'backend', 'ui', 'ux']
        content_lower = content.lower()
        
        return [keyword for keyword in keywords if keyword in content_lower]
    
    def _is_component_file(self, content: str) -> bool:
        """Check if file is a React component"""
        return any(pattern in content for pattern in [
            'export default', 'export const', 'function ', 'const ', 'React.FC'
        ])
    
    def _extract_component_name(self, file_path: Path, content: str) -> str:
        """Extract component name"""
        return file_path.stem
    
    def _extract_component_props(self, content: str) -> List[str]:
        """Extract component props"""
        # Simplified prop extraction
        props = []
        lines = content.split('\n')
        
        for line in lines:
            if 'interface' in line and 'Props' in line:
                # Found props interface, could parse further
                props.append('props_interface_found')
                break
        
        return props
    
    def _summarize_component(self, content: str, props: List[str]) -> str:
        """Create component summary"""
        lines = content.split('\n')[:20]  # First 20 lines
        return '\n'.join(lines)
    
    def _extract_ui_tags(self, content: str) -> List[str]:
        """Extract UI-specific tags"""
        ui_keywords = ['button', 'form', 'input', 'modal', 'dialog', 'menu', 'nav']
        content_lower = content.lower()
        
        return [keyword for keyword in ui_keywords if keyword in content_lower]
    
    def _extract_kotlin_endpoints(self, content: str) -> List[Dict[str, str]]:
        """Extract Kotlin API endpoints"""
        endpoints = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if any(method in line for method in ['@GET', '@POST', '@PUT', '@DELETE']):
                method = line.strip().replace('@', '').split('(')[0]
                path = "/"  # Simplified path extraction
                
                endpoints.append({
                    'method': method,
                    'path': path,
                    'description': f"{method} endpoint"
                })
        
        return endpoints
    
    def _extract_architecture_tags(self, content: str) -> List[str]:
        """Extract architecture-specific tags"""
        arch_keywords = ['microservice', 'api', 'database', 'kafka', 'docker', 'kubernetes']
        content_lower = content.lower()
        
        return [keyword for keyword in arch_keywords if keyword in content_lower]
    
    def _calculate_relevance(self, query: str, item: ContextItem) -> float:
        """Calculate relevance score for query and context item"""
        query_words = set(query.lower().split())
        
        # Check title relevance
        title_words = set(item.title.lower().split())
        title_score = len(query_words.intersection(title_words)) / len(query_words) if query_words else 0
        
        # Check content relevance
        content_words = set(item.content.lower().split())
        content_score = len(query_words.intersection(content_words)) / len(query_words) if query_words else 0
        
        # Check tag relevance
        tag_words = set(' '.join(item.tags).lower().split())
        tag_score = len(query_words.intersection(tag_words)) / len(query_words) if query_words else 0
        
        # Weighted combination
        return (title_score * 0.5) + (content_score * 0.3) + (tag_score * 0.2)
    
    def _get_context_stats(self) -> Dict[str, int]:
        """Get context statistics"""
        stats = {}
        for context_type in ContextType:
            stats[context_type.value] = sum(
                1 for item in self.context_cache.values()
                if item.type == context_type
            )
        return stats

# Global context manager instance
context_manager = ProjectContextManager()
