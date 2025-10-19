#!/usr/bin/env python3
"""
@llm-type tool
@llm-legend LLM context warming system for onboarding new AI agents to the Unhinged monorepo
@llm-context Provides paginated, structured summaries of codebase culture, vision, and architecture
"""

import json
import yaml
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class LLMContextWarmer:
    """
    @llm-type class
    @llm-legend Generates structured context summaries for new LLM agents joining the project
    @llm-context Converts extracted comments into digestible chunks with pagination support
    """
    
    def __init__(self, comments_file: str = "docs/architecture/extracted-comments.json"):
        self.comments_file = Path(comments_file)
        self.comments = self._load_comments()
        self.page_size = 10  # Comments per page
        
    def _load_comments(self) -> List[Dict]:
        """Load and parse the extracted comments JSON"""
        if not self.comments_file.exists():
            raise FileNotFoundError(f"Comments file not found: {self.comments_file}")
        
        with open(self.comments_file, 'r') as f:
            return json.load(f)
    
    def generate_project_overview(self) -> Dict[str, Any]:
        """
        @llm-type function
        @llm-legend Generates comprehensive project overview from extracted comments
        @llm-context Creates high-level summary perfect for LLM context warming
        """
        overview = {
            'project_name': 'Unhinged',
            'description': 'AI-powered multimodal conversation platform with vision, speech, and text capabilities',
            'generated_at': datetime.now().isoformat(),
            'total_comments': len(self.comments),
            'languages': self._get_language_stats(),
            'component_types': self._get_type_stats(),
            'architecture_principles': self._extract_axioms(),
            'key_components': self._extract_key_components(),
            'integration_patterns': self._extract_integration_patterns()
        }
        return overview
    
    def _get_language_stats(self) -> Dict[str, int]:
        """Get distribution of comments by programming language"""
        stats = {}
        for comment in self.comments:
            lang = comment.get('language', 'unknown')
            stats[lang] = stats.get(lang, 0) + 1
        return dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))
    
    def _get_type_stats(self) -> Dict[str, int]:
        """Get distribution of comments by component type"""
        stats = {}
        for comment in self.comments:
            comp_type = comment.get('llm_type', 'unknown')
            if comp_type:
                stats[comp_type] = stats.get(comp_type, 0) + 1
        return dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))
    
    def _extract_axioms(self) -> List[Dict[str, str]]:
        """Extract fundamental design principles"""
        axioms = []
        for comment in self.comments:
            if comment.get('llm_axiom'):
                axioms.append({
                    'file': comment['file_path'],
                    'component': comment.get('element_name', 'unknown'),
                    'principle': comment['llm_axiom'],
                    'context': comment.get('llm_legend', '')
                })
        return axioms
    
    def _extract_key_components(self) -> List[Dict[str, str]]:
        """
        @llm-type function
        @llm-legend Extract key system components with improved name resolution and cross-references
        @llm-context Addresses LLM feedback about unknown element names and missing navigation
        """
        components = []
        for comment in self.comments:
            if comment.get('llm_type') in ['service', 'component', 'config'] and comment.get('llm_legend'):
                # Use improved element name detection
                improved_name = self._improve_element_name(comment)

                components.append({
                    'name': improved_name,
                    'type': comment['llm_type'],
                    'file': comment['file_path'],
                    'purpose': comment['llm_legend'],
                    'implementation': comment.get('llm_key', ''),
                    'architecture_role': comment.get('llm_map', ''),
                    'context': comment.get('llm_context', ''),
                    'related_services': self._find_related_services(comment)
                })
        return components[:15]  # Top 15 components
    
    def _extract_integration_patterns(self) -> List[Dict[str, str]]:
        """Extract integration and communication patterns"""
        patterns = []
        for comment in self.comments:
            if comment.get('llm_map') and 'integrat' in comment['llm_map'].lower():
                patterns.append({
                    'component': comment.get('element_name', 'unknown'),
                    'file': comment['file_path'],
                    'pattern': comment['llm_map'],
                    'context': comment.get('llm_context', '')
                })
        return patterns
    
    def paginate_comments(self, page: int = 1) -> Dict[str, Any]:
        """
        @llm-type function
        @llm-legend Provides paginated access to all extracted comments for detailed review
        @llm-context Allows LLMs to scroll through codebase comments in digestible chunks
        """
        start_idx = (page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        
        total_pages = (len(self.comments) + self.page_size - 1) // self.page_size
        
        page_comments = self.comments[start_idx:end_idx]
        
        return {
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_comments': len(self.comments),
                'page_size': self.page_size,
                'has_next': page < total_pages,
                'has_previous': page > 1
            },
            'comments': page_comments
        }
    
    def output_yaml(self, data: Dict[str, Any]) -> str:
        """Convert data to YAML format"""
        return yaml.dump(data, default_flow_style=False, sort_keys=False, width=120)
    
    def output_json(self, data: Dict[str, Any]) -> str:
        """Convert data to JSON format"""
        return json.dumps(data, indent=2)

    def _improve_element_name(self, comment: Dict[str, Any]) -> str:
        """
        @llm-type function
        @llm-legend Improve element name detection from file paths when element_name is unknown
        @llm-context Addresses LLM feedback about unknown element names in service files
        """
        element_name = comment.get('element_name', 'unknown')
        if element_name == 'unknown':
            file_path = comment['file_path']
            if 'services/' in file_path:
                # Extract service name from services/service-name/file.py
                element_name = file_path.split('services/')[1].split('/')[0]
            elif file_path.endswith('.py'):
                # Extract from Python file name
                element_name = file_path.split('/')[-1].replace('.py', '')
            elif file_path.endswith('.ts') or file_path.endswith('.tsx'):
                # Extract from TypeScript file name
                element_name = file_path.split('/')[-1].replace('.ts', '').replace('.tsx', '')
            elif file_path.endswith('.yml') or file_path.endswith('.yaml'):
                # Extract from YAML file name
                element_name = file_path.split('/')[-1].replace('.yml', '').replace('.yaml', '')
        return element_name

    def _find_related_services(self, comment: Dict[str, Any]) -> List[str]:
        """
        @llm-type function
        @llm-legend Find related services through port references, API calls, and integration patterns
        @llm-context Addresses LLM feedback about lack of cross-reference navigation capabilities
        """
        related = []
        current_file = comment['file_path']
        current_text = ' '.join([
            comment.get('key', '') or '',
            comment.get('map', '') or '',
            comment.get('contract', '') or '',
            comment.get('llm_context', '') or '',
            comment.get('raw_comment', '') or ''
        ]).lower()

        # Look for port references, service names, and integration patterns
        for other_comment in self.comments:
            if other_comment['file_path'] == current_file:
                continue

            other_text = ' '.join([
                other_comment.get('key', '') or '',
                other_comment.get('map', '') or '',
                other_comment.get('contract', '') or '',
                other_comment.get('llm_context', '') or '',
                other_comment.get('raw_comment', '') or ''
            ]).lower()

            # Check for port number matches
            import re
            current_ports = re.findall(r'port\s+(\d+)|:(\d+)', current_text)
            other_ports = re.findall(r'port\s+(\d+)|:(\d+)', other_text)

            # Flatten port tuples and filter empty strings
            current_ports = [p for group in current_ports for p in group if p]
            other_ports = [p for group in other_ports for p in group if p]

            if any(port in other_ports for port in current_ports):
                element_name = self._improve_element_name(other_comment)
                if element_name not in related:
                    related.append(element_name)

            # Check for service name references
            current_element = self._improve_element_name(comment)
            other_element = self._improve_element_name(other_comment)

            if current_element.lower() in other_text or other_element.lower() in current_text:
                if other_element not in related:
                    related.append(other_element)

        return related[:5]  # Limit to top 5 related services

    def _validate_context_completeness(self, comments: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        @llm-type function
        @llm-legend Validate that service and component comments have proper context information
        @llm-context Addresses LLM feedback about null llm_context fields where context should exist
        """
        missing_context = []

        for comment in comments:
            # Services and components should have context
            if comment.get('type') in ['service', 'component', 'config']:
                llm_context = comment.get('llm_context')
                if not llm_context or llm_context.strip() == '':
                    missing_context.append({
                        'file_path': comment['file_path'],
                        'element_name': comment.get('element_name', 'unknown'),
                        'type': comment.get('type'),
                        'reason': 'Service/component missing integration context'
                    })

        return missing_context

def main():
    parser = argparse.ArgumentParser(description='LLM Context Warming System')
    parser.add_argument('command', choices=['overview', 'paginate'], 
                       help='Command to execute')
    parser.add_argument('--page', type=int, default=1,
                       help='Page number for pagination (default: 1)')
    parser.add_argument('--format', choices=['yaml', 'json'], default='yaml',
                       help='Output format (default: yaml)')
    parser.add_argument('--comments-file', default='docs/architecture/extracted-comments.json',
                       help='Path to extracted comments file')
    
    args = parser.parse_args()
    
    try:
        warmer = LLMContextWarmer(args.comments_file)
        
        if args.command == 'overview':
            data = warmer.generate_project_overview()
        elif args.command == 'paginate':
            data = warmer.paginate_comments(args.page)
        
        if args.format == 'yaml':
            output = warmer.output_yaml(data)
        else:
            output = warmer.output_json(data)
        
        print(output)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
