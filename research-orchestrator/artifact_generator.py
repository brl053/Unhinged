"""
Artifact Generator - Creates code files, documentation, and configurations
"""
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, Template

from config import settings


class ArtifactGenerator:
    """Generates code artifacts based on research results"""
    
    def __init__(self):
        self.templates_dir = settings.templates_dir
        self.output_dir = settings.output_dir
        self.project_root = settings.project_root
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Ensure templates directory exists
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._create_default_templates()
    
    def generate_from_research(self, research_response: Any, context: Dict[str, Any]) -> List[Path]:
        """Generate artifacts based on research response and context"""
        
        artifacts = []
        
        # Determine what artifacts to generate based on context
        if context.get("integration_type") == "React component wrapper":
            artifacts.extend(self._generate_react_wrapper(research_response, context))
        
        elif context.get("integration_type") == "API client/wrapper":
            artifacts.extend(self._generate_api_client(research_response, context))
        
        elif context.get("integration_type") == "Backend service integration":
            artifacts.extend(self._generate_backend_service(research_response, context))
        
        elif context.get("integration_type") == "Full-stack implementation":
            artifacts.extend(self._generate_fullstack(research_response, context))
        
        # Always generate documentation
        artifacts.extend(self._generate_documentation(research_response, context))
        
        return artifacts
    
    def _generate_react_wrapper(self, research_response: Any, context: Dict[str, Any]) -> List[Path]:
        """Generate React component wrapper artifacts"""
        
        artifacts = []
        technology = context.get("technology", "Unknown")
        
        # Extract component name
        component_name = self._to_pascal_case(technology)
        
        # Generate main component
        component_path = self._generate_from_template(
            "react-wrapper.tsx.j2",
            f"{component_name}Wrapper.tsx",
            {
                "component_name": component_name,
                "technology": technology,
                "research_content": research_response.content,
                "platform_features": context.get("platform_features", []),
                "use_case": context.get("use_case", ""),
                "timestamp": datetime.now().isoformat()
            }
        )
        artifacts.append(component_path)
        
        # Generate TypeScript types
        types_path = self._generate_from_template(
            "types.ts.j2",
            f"{component_name}Types.ts",
            {
                "component_name": component_name,
                "technology": technology,
                "research_content": research_response.content
            }
        )
        artifacts.append(types_path)
        
        # Generate hooks (if applicable)
        hooks_path = self._generate_from_template(
            "hooks.ts.j2", 
            f"use{component_name}.ts",
            {
                "component_name": component_name,
                "technology": technology,
                "research_content": research_response.content
            }
        )
        artifacts.append(hooks_path)
        
        # Generate tests
        test_path = self._generate_from_template(
            "component.test.tsx.j2",
            f"{component_name}Wrapper.test.tsx",
            {
                "component_name": component_name,
                "technology": technology
            }
        )
        artifacts.append(test_path)
        
        # Generate stories (Storybook)
        stories_path = self._generate_from_template(
            "component.stories.tsx.j2",
            f"{component_name}Wrapper.stories.tsx", 
            {
                "component_name": component_name,
                "technology": technology
            }
        )
        artifacts.append(stories_path)
        
        return artifacts
    
    def _generate_api_client(self, research_response: Any, context: Dict[str, Any]) -> List[Path]:
        """Generate API client artifacts"""
        
        artifacts = []
        technology = context.get("technology", "Unknown")
        client_name = self._to_pascal_case(technology)
        
        # Generate main client
        client_path = self._generate_from_template(
            "api-client.ts.j2",
            f"{client_name}Client.ts",
            {
                "client_name": client_name,
                "technology": technology,
                "research_content": research_response.content,
                "platform_features": context.get("platform_features", [])
            }
        )
        artifacts.append(client_path)
        
        # Generate types
        types_path = self._generate_from_template(
            "api-types.ts.j2",
            f"{client_name}Types.ts",
            {
                "client_name": client_name,
                "technology": technology,
                "research_content": research_response.content
            }
        )
        artifacts.append(types_path)
        
        return artifacts
    
    def _generate_backend_service(self, research_response: Any, context: Dict[str, Any]) -> List[Path]:
        """Generate backend service artifacts"""
        
        artifacts = []
        technology = context.get("technology", "Unknown")
        service_name = self._to_pascal_case(technology)
        
        # Generate Kotlin service
        service_path = self._generate_from_template(
            "kotlin-service.kt.j2",
            f"{service_name}Service.kt",
            {
                "service_name": service_name,
                "technology": technology,
                "research_content": research_response.content,
                "platform_features": context.get("platform_features", [])
            }
        )
        artifacts.append(service_path)
        
        return artifacts
    
    def _generate_fullstack(self, research_response: Any, context: Dict[str, Any]) -> List[Path]:
        """Generate full-stack implementation artifacts"""
        
        artifacts = []
        
        # Generate both frontend and backend artifacts
        artifacts.extend(self._generate_react_wrapper(research_response, context))
        artifacts.extend(self._generate_backend_service(research_response, context))
        
        return artifacts
    
    def _generate_documentation(self, research_response: Any, context: Dict[str, Any]) -> List[Path]:
        """Generate documentation artifacts"""
        
        artifacts = []
        technology = context.get("technology", "Unknown")
        
        # Generate README
        readme_path = self._generate_from_template(
            "README.md.j2",
            f"{technology}_README.md",
            {
                "technology": technology,
                "integration_type": context.get("integration_type", ""),
                "research_content": research_response.content,
                "use_case": context.get("use_case", ""),
                "platform_features": context.get("platform_features", []),
                "citations": research_response.citations,
                "related_questions": research_response.related_questions,
                "timestamp": datetime.now().isoformat()
            }
        )
        artifacts.append(readme_path)
        
        # Generate implementation guide
        guide_path = self._generate_from_template(
            "implementation-guide.md.j2",
            f"{technology}_Implementation_Guide.md",
            {
                "technology": technology,
                "integration_type": context.get("integration_type", ""),
                "research_content": research_response.content,
                "depth": context.get("depth", ""),
                "platform_features": context.get("platform_features", [])
            }
        )
        artifacts.append(guide_path)
        
        return artifacts
    
    def _generate_from_template(self, template_name: str, output_name: str, context: Dict[str, Any]) -> Path:
        """Generate a file from a Jinja2 template"""
        
        try:
            template = self.jinja_env.get_template(template_name)
        except Exception:
            # If template doesn't exist, create a basic one
            template = self._create_basic_template(template_name, context)
        
        # Render template
        content = template.render(**context)
        
        # Write to output file
        output_path = self.output_dir / output_name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(content)
        
        return output_path
    
    def _create_basic_template(self, template_name: str, context: Dict[str, Any]) -> Template:
        """Create a basic template if the specific one doesn't exist"""
        
        if template_name.endswith('.tsx.j2'):
            template_content = """// {{ component_name }} - Generated from research
// Technology: {{ technology }}
// Generated: {{ timestamp }}

import React from 'react';

interface {{ component_name }}Props {
  // TODO: Define props based on research
}

export const {{ component_name }}: React.FC<{{ component_name }}Props> = (props) => {
  // TODO: Implement based on research findings
  return (
    <div>
      <h1>{{ component_name }}</h1>
      <p>Implementation needed based on research</p>
    </div>
  );
};

export default {{ component_name }};
"""
        elif template_name.endswith('.ts.j2'):
            template_content = """// {{ technology }} Types - Generated from research
// Generated: {{ timestamp }}

// TODO: Define types based on research findings

export interface {{ component_name }}Config {
  // Configuration options
}

export interface {{ component_name }}Options {
  // Runtime options
}
"""
        elif template_name.endswith('.md.j2'):
            template_content = """# {{ technology }} Integration

**Generated:** {{ timestamp }}
**Integration Type:** {{ integration_type }}

## Overview

{{ research_content[:500] }}...

## Implementation

TODO: Add implementation details based on research.

## Usage

TODO: Add usage examples.

## Sources

{% for citation in citations %}
- {{ citation }}
{% endfor %}
"""
        else:
            template_content = """// {{ technology }} - Generated from research
// TODO: Implement based on research findings
"""
        
        return Template(template_content)
    
    def _create_default_templates(self):
        """Create default templates if they don't exist"""
        
        # This would create comprehensive Jinja2 templates
        # For now, we'll rely on the basic template creation
        pass
    
    def _to_pascal_case(self, text: str) -> str:
        """Convert text to PascalCase"""
        # Remove non-alphanumeric characters and split
        words = re.findall(r'[a-zA-Z0-9]+', text)
        return ''.join(word.capitalize() for word in words)
    
    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case"""
        # Remove non-alphanumeric characters and split
        words = re.findall(r'[a-zA-Z0-9]+', text)
        return '_'.join(word.lower() for word in words)
