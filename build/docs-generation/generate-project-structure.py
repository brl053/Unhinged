#!/usr/bin/env python3
"""
@llm-type util.generator
@llm-does project structure documentation generation from filesystem analysis
@llm-rule structure documentation must be accurate and reflect current state
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

class ProjectAnalyzer:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.ignore_dirs = {
            '.git', 'node_modules', 'build', 'target', 'dist', 
            '.gradle', '__pycache__', '.pytest_cache', 'coverage',
            'test-results', '.next', '.nuxt'
        }
        self.ignore_files = {
            '.DS_Store', 'Thumbs.db', '*.log', '*.tmp'
        }
        
    def analyze_structure(self) -> Dict:
        """Analyze the complete project structure"""
        structure = {
            'root': str(self.root_path),
            'analysis_date': datetime.now().isoformat(),
            'directories': {},
            'file_counts': {},
            'key_files': [],
            'services': [],
            'components': {}
        }
        
        # Analyze directory structure
        structure['directories'] = self._analyze_directories()
        
        # Count files by type
        structure['file_counts'] = self._count_files()
        
        # Identify key files
        structure['key_files'] = self._identify_key_files()
        
        # Identify services
        structure['services'] = self._identify_services()
        
        # Analyze components
        structure['components'] = self._analyze_components()
        
        return structure
    
    def _analyze_directories(self) -> Dict:
        """Analyze directory structure and purposes"""
        directories = {}
        
        for root, dirs, files in os.walk(self.root_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            rel_path = os.path.relpath(root, self.root_path)
            if rel_path == '.':
                rel_path = 'root'
            
            # Determine directory purpose
            purpose = self._determine_directory_purpose(rel_path, files)
            
            directories[rel_path] = {
                'file_count': len(files),
                'subdirs': len(dirs),
                'purpose': purpose,
                'key_files': [f for f in files if self._is_key_file(f)]
            }
        
        return directories
    
    def _count_files(self) -> Dict:
        """Count files by extension"""
        counts = {}
        
        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            for file in files:
                if self._should_ignore_file(file):
                    continue
                
                ext = Path(file).suffix.lower()
                if not ext:
                    ext = 'no_extension'
                
                counts[ext] = counts.get(ext, 0) + 1
        
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))
    
    def _identify_key_files(self) -> List[Dict]:
        """Identify important files in the project"""
        key_files = []
        
        important_files = {
            'Makefile': 'Build automation and development commands',
            'README.md': 'Project overview and setup instructions',
            'docker-compose.yml': 'Service orchestration configuration',
            'package.json': 'Node.js dependencies and scripts',
            'build.gradle.kts': 'Kotlin/Java build configuration',
            'requirements.txt': 'Python dependencies',
            'Dockerfile': 'Container build instructions'
        }
        
        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            for file in files:
                if file in important_files:
                    rel_path = os.path.relpath(os.path.join(root, file), self.root_path)
                    key_files.append({
                        'path': rel_path,
                        'name': file,
                        'purpose': important_files[file]
                    })
        
        return key_files
    
    def _identify_services(self) -> List[Dict]:
        """Identify microservices in the project"""
        services = []
        
        # Check services directory
        services_dir = self.root_path / 'services'
        if services_dir.exists():
            for service_dir in services_dir.iterdir():
                if service_dir.is_dir() and service_dir.name not in self.ignore_dirs:
                    service_info = self._analyze_service(service_dir)
                    services.append(service_info)
        
        # Check for other service patterns
        for potential_service in ['backend', 'frontend', 'llm']:
            service_path = self.root_path / potential_service
            if service_path.exists() and service_path.is_dir():
                service_info = self._analyze_service(service_path)
                services.append(service_info)
        
        return services
    
    def _analyze_service(self, service_path: Path) -> Dict:
        """Analyze a single service directory"""
        service_info = {
            'name': service_path.name,
            'path': str(service_path.relative_to(self.root_path)),
            'type': 'unknown',
            'language': 'unknown',
            'has_dockerfile': False,
            'has_tests': False,
            'description': ''
        }
        
        # Check for language indicators
        if (service_path / 'package.json').exists():
            service_info['language'] = 'JavaScript/TypeScript'
            service_info['type'] = 'Node.js Service'
        elif (service_path / 'requirements.txt').exists():
            service_info['language'] = 'Python'
            service_info['type'] = 'Python Service'
        elif (service_path / 'build.gradle.kts').exists():
            service_info['language'] = 'Kotlin'
            service_info['type'] = 'Kotlin Service'
        elif (service_path / 'Cargo.toml').exists():
            service_info['language'] = 'Rust'
            service_info['type'] = 'Rust Service'
        
        # Check for Docker
        service_info['has_dockerfile'] = (service_path / 'Dockerfile').exists()
        
        # Check for tests
        test_indicators = ['test', 'tests', '__tests__', 'spec']
        service_info['has_tests'] = any(
            (service_path / test_dir).exists() for test_dir in test_indicators
        )
        
        # Try to get description from README
        readme_path = service_path / 'README.md'
        if readme_path.exists():
            try:
                with open(readme_path, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.strip() and not line.startswith('#'):
                            service_info['description'] = line.strip()[:100]
                            break
            except:
                pass
        
        return service_info
    
    def _analyze_components(self) -> Dict:
        """Analyze major project components"""
        components = {}
        
        component_dirs = {
            'backend': 'Backend API and business logic',
            'frontend': 'Frontend user interface',
            'services': 'Microservices and external integrations',
            'proto': 'Protocol buffer definitions',
            'docs': 'Project documentation',
            'scripts': 'Build and automation scripts',
            'infrastructure': 'Infrastructure as code',
            'monitoring': 'Monitoring and observability'
        }
        
        for comp_name, comp_desc in component_dirs.items():
            comp_path = self.root_path / comp_name
            if comp_path.exists():
                components[comp_name] = {
                    'description': comp_desc,
                    'exists': True,
                    'file_count': sum(1 for _ in comp_path.rglob('*') if _.is_file()),
                    'subdirs': len([d for d in comp_path.iterdir() if d.is_dir()])
                }
            else:
                components[comp_name] = {
                    'description': comp_desc,
                    'exists': False
                }
        
        return components
    
    def _determine_directory_purpose(self, path: str, files: List[str]) -> str:
        """Determine the purpose of a directory based on its contents"""
        if 'Dockerfile' in files:
            return 'Containerized service'
        elif 'package.json' in files:
            return 'Node.js project'
        elif 'requirements.txt' in files:
            return 'Python project'
        elif 'build.gradle.kts' in files or 'build.gradle' in files:
            return 'Gradle project'
        elif 'Cargo.toml' in files:
            return 'Rust project'
        elif any(f.endswith('.proto') for f in files):
            return 'Protocol buffer definitions'
        elif any(f.endswith('.md') for f in files):
            return 'Documentation'
        elif any(f.endswith('.sql') for f in files):
            return 'Database scripts'
        elif 'docker-compose.yml' in files:
            return 'Docker orchestration'
        else:
            return 'General files'
    
    def _is_key_file(self, filename: str) -> bool:
        """Check if a file is considered important"""
        key_files = {
            'Makefile', 'README.md', 'Dockerfile', 'docker-compose.yml',
            'package.json', 'requirements.txt', 'build.gradle.kts',
            'Cargo.toml', '.gitignore', 'LICENSE'
        }
        return filename in key_files
    
    def _should_ignore_file(self, filename: str) -> bool:
        """Check if a file should be ignored"""
        return filename.startswith('.') and filename not in {'.gitignore', '.dockerignore'}

class StructureDocumentationGenerator:
    def __init__(self, analysis_data: Dict):
        self.data = analysis_data
    
    def generate_structure_doc(self) -> str:
        """Generate project structure documentation"""
        doc = []
        
        # Header
        doc.append("# 🏗️ Project Structure - Unhinged Platform")
        doc.append("")
        doc.append("> **Purpose**: Comprehensive overview of project organization and components")
        doc.append("> **Audience**: Developers and AI assistants working on the platform")
        doc.append(f"> **Last Updated**: Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc.append("")
        
        # Overview
        doc.append("## 📊 Project Overview")
        doc.append("")
        doc.append(f"- **Total Files**: {sum(self.data['file_counts'].values())}")
        doc.append(f"- **Services**: {len(self.data['services'])}")
        doc.append(f"- **Key Files**: {len(self.data['key_files'])}")
        doc.append("")
        
        # File type breakdown
        doc.append("### File Type Distribution")
        doc.append("```")
        for ext, count in list(self.data['file_counts'].items())[:10]:
            doc.append(f"{ext:<15} {count:>5} files")
        doc.append("```")
        doc.append("")
        
        # Services
        if self.data['services']:
            doc.append("## 🚀 Services")
            doc.append("")
            for service in self.data['services']:
                doc.append(f"### {service['name']}")
                doc.append(f"- **Type**: {service['type']}")
                doc.append(f"- **Language**: {service['language']}")
                doc.append(f"- **Path**: `{service['path']}`")
                doc.append(f"- **Dockerized**: {'✅' if service['has_dockerfile'] else '❌'}")
                doc.append(f"- **Tests**: {'✅' if service['has_tests'] else '❌'}")
                if service['description']:
                    doc.append(f"- **Description**: {service['description']}")
                doc.append("")
        
        # Components
        doc.append("## 🧩 Components")
        doc.append("")
        for comp_name, comp_info in self.data['components'].items():
            if comp_info['exists']:
                doc.append(f"### {comp_name}")
                doc.append(f"- **Description**: {comp_info['description']}")
                doc.append(f"- **Files**: {comp_info['file_count']}")
                doc.append(f"- **Subdirectories**: {comp_info['subdirs']}")
                doc.append("")
        
        # Key files
        doc.append("## 📋 Key Files")
        doc.append("")
        for file_info in self.data['key_files']:
            doc.append(f"- **{file_info['name']}** (`{file_info['path']}`) - {file_info['purpose']}")
        doc.append("")
        
        # Footer
        doc.append("---")
        doc.append("")
        doc.append("**Note**: This documentation is automatically generated from project analysis.")
        doc.append("Run `make docs-update` to refresh after structural changes.")
        
        return '\n'.join(doc)

def main():
    """Main function"""
    # Analyze project
    analyzer = ProjectAnalyzer()
    analysis_data = analyzer.analyze_structure()
    
    # Generate documentation
    generator = StructureDocumentationGenerator(analysis_data)
    structure_doc = generator.generate_structure_doc()
    
    # Write to output file
    output_path = "docs/development/project-structure.md"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(structure_doc)
    
    print(f"✅ Generated project structure documentation: {output_path}")
    print(f"📊 Analyzed {len(analysis_data['directories'])} directories")
    print(f"📊 Found {len(analysis_data['services'])} services")

if __name__ == "__main__":
    main()
