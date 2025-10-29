#!/usr/bin/env python3
"""
@llm-type util.tool
@llm-does llm context warming system for onboarding new
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
@llm-type config.build
@llm-does structured context summaries for new llm agents
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
@llm-type util.function
@llm-does comprehensive project overview from extracted comments
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
@llm-type util.function
@llm-does extract key system components with improved name
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
@llm-type util.function
@llm-does paginated access to all extracted comments for
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
@llm-type util.function
@llm-does improve element name detection from file paths
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
@llm-type util.function
@llm-does find related services through port references, api
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
@llm-type util.function
@llm-does validate that service and component comments have
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

    def _generate_getting_started_section(self) -> Dict[str, Any]:
        """
@llm-type util.function
@llm-does generate getting started section with setup commands
"""
        return {
            'quick_start_commands': [
                'make setup    # Initial project setup',
                'make dev      # Start development environment',
                'make test     # Run test suite',
                'make docs-context-overview  # Get project overview'
            ],
            'prerequisites': [
                'Docker and Docker Compose',
                'Node.js 18+ (for frontend)',
                'Python 3.12+ (for AI services)',
                'Java 17+ (for Kotlin backend)',
                'At least 16GB RAM (for AI models)'
            ],
            'first_steps': [
                '1. Clone the repository',
                '2. Run `make setup` to initialize',
                '3. Run `make dev` to start all services',
                '4. Open http://localhost:8081 for the main interface',
                '5. Use `make docs-context-paginate` to explore the codebase'
            ]
        }

    def _extract_dependency_information(self) -> Dict[str, Any]:
        """
@llm-type util.function
@llm-does extract dependency and build system information from
"""
        dependencies = {
            'frontend': {
                'language': 'TypeScript/React',
                'package_manager': 'npm',
                'config_file': 'package.json',
                'key_dependencies': ['React', 'TypeScript', 'Vite']
            },
            'backend': {
                'language': 'Kotlin',
                'build_system': 'Gradle',
                'config_file': 'build.gradle.kts',
                'key_dependencies': ['Ktor', 'Kotlin Coroutines']
            },
            'ai_services': {
                'language': 'Python',
                'package_manager': 'pip',
                'config_files': ['requirements.txt', 'pyproject.toml'],
                'key_dependencies': ['FastAPI', 'Transformers', 'PyTorch']
            },
            'infrastructure': {
                'containerization': 'Docker Compose',
                'config_file': 'docker-compose.yml',
                'services': ['PostgreSQL', 'Redis', 'Nginx']
            }
        }
        return dependencies

    def _validate_legend_completeness(self, comments: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
@llm-type util.function
@llm-does validate that
"""
        truncated_legends = []

        for comment in comments:
            legend = comment.get('llm_legend', '') or comment.get('legend', '')
            element_name = comment.get('element_name', 'unknown')

            # Check for signs of truncation or incompleteness
            if legend:
                # Too short (likely truncated)
                if len(legend) < 15:
                    truncated_legends.append({
                        'file_path': comment['file_path'],
                        'element_name': element_name,
                        'legend': legend,
                        'issue': 'Legend too short (likely truncated)',
                        'suggestion': 'Expand to provide more context'
                    })
                # Ends abruptly (common truncation patterns)
                elif legend.endswith(('...', 'Extracts all', 'Provides', 'Handles')):
                    truncated_legends.append({
                        'file_path': comment['file_path'],
                        'element_name': element_name,
                        'legend': legend,
                        'issue': 'Legend appears incomplete',
                        'suggestion': 'Complete the description'
                    })

        return truncated_legends

    def generate_enhanced_project_overview(self) -> Dict[str, Any]:
        """
@llm-type util.function
@llm-does generate enhanced project overview addressing all llm
"""
        base_overview = self.generate_project_overview()

        # Add the missing sections identified in LLM feedback
        enhanced_overview = {
            **base_overview,
            'getting_started': self._generate_getting_started_section(),
            'dependencies': self._extract_dependency_information(),
            'legend_quality_report': {
                'truncated_legends': self._validate_legend_completeness(self.comments),
                'total_legends': len([c for c in self.comments if c.get('llm_legend') or c.get('legend')]),
                'quality_score': self._calculate_legend_quality_score()
            }
        }

        return enhanced_overview

    def _calculate_legend_quality_score(self) -> float:
        """Calculate quality score for legend completeness"""
        total_legends = len([c for c in self.comments if c.get('llm_legend') or c.get('legend')])
        if total_legends == 0:
            return 0.0

        truncated = len(self._validate_legend_completeness(self.comments))
        return round((total_legends - truncated) / total_legends * 100, 1)

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
            data = warmer.generate_enhanced_project_overview()
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
