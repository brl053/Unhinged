#!/usr/bin/env python3
"""
Automated Makefile Documentation Generator

This script analyzes the Makefile and generates/updates documentation automatically.
It extracts targets, descriptions, dependencies, and usage patterns.
"""

import os
import re
import sys
from datetime import datetime


class MakefileAnalyzer:
    def __init__(self, makefile_path: str):
        self.makefile_path = makefile_path
        self.targets = {}
        self.variables = {}
        self.functions = {}

    def analyze(self) -> dict:
        """Analyze the Makefile and extract all information"""
        with open(self.makefile_path) as f:
            content = f.read()

        # Extract targets with descriptions
        self._extract_targets(content)

        # Extract variables
        self._extract_variables(content)

        # Extract functions
        self._extract_functions(content)

        return {
            "targets": self.targets,
            "variables": self.variables,
            "functions": self.functions,
            "analysis_date": datetime.now().isoformat(),
        }

    def _extract_targets(self, content: str):
        """Extract Make targets and their descriptions"""
        lines = content.split("\n")
        current_target = None

        for i, line in enumerate(lines):
            # Look for target definitions with descriptions
            if "##" in line and ":" in line:
                match = re.match(r"^([a-zA-Z_-]+):\s*.*##\s*(.+)$", line.strip())
                if match:
                    target_name = match.group(1)
                    description = match.group(2)

                    # Look for dependencies
                    deps_match = re.match(r"^([a-zA-Z_-]+):\s*([^#]+)##", line.strip())
                    dependencies = []
                    if deps_match and deps_match.group(2).strip():
                        dependencies = [dep.strip() for dep in deps_match.group(2).strip().split()]

                    # Look for the actual command in next lines
                    commands = []
                    j = i + 1
                    while j < len(lines) and (lines[j].startswith("\t") or lines[j].strip() == ""):
                        if lines[j].startswith("\t") and lines[j].strip():
                            commands.append(lines[j][1:])  # Remove tab
                        j += 1

                    self.targets[target_name] = {
                        "description": description,
                        "dependencies": dependencies,
                        "commands": commands,
                        "line_number": i + 1,
                    }

    def _extract_variables(self, content: str):
        """Extract Make variables"""
        lines = content.split("\n")

        for i, line in enumerate(lines):
            # Look for variable assignments
            match = re.match(r"^([A-Z_]+)\s*:=\s*(.+)$", line.strip())
            if match:
                var_name = match.group(1)
                var_value = match.group(2)

                # Look for comment on same line or previous line
                comment = ""
                if "#" in line:
                    comment = line.split("#", 1)[1].strip()
                elif i > 0 and lines[i - 1].strip().startswith("#"):
                    comment = lines[i - 1].strip()[1:].strip()

                self.variables[var_name] = {"value": var_value, "comment": comment, "line_number": i + 1}

    def _extract_functions(self, content: str):
        """Extract Make functions"""
        lines = content.split("\n")

        for i, line in enumerate(lines):
            # Look for function definitions
            match = re.match(r"^define\s+([a-zA-Z_]+)$", line.strip())
            if match:
                func_name = match.group(1)

                # Extract function body
                body = []
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith("endef"):
                    body.append(lines[j])
                    j += 1

                self.functions[func_name] = {"body": body, "line_number": i + 1}


class DocumentationGenerator:
    def __init__(self, analysis_data: dict):
        self.data = analysis_data

    def generate_reference_doc(self) -> str:
        """Generate the makefile reference documentation"""
        doc = []

        # Header
        doc.append("# 📖 Makefile Reference - Unhinged Platform")
        doc.append("")
        doc.append("> **Purpose**: Comprehensive documentation of all Make targets and development workflows")
        doc.append("> **Audience**: Developers and AI assistants working on the Unhinged platform")
        doc.append(f"> **Last Updated**: Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc.append("")

        # Quick reference
        doc.append("## 🎯 Quick Reference")
        doc.append("")
        doc.append("### Most Used Commands")
        doc.append("```bash")

        # Find most important commands
        important_commands = ["help", "status", "setup", "dev", "clean"]
        for cmd in important_commands:
            if cmd in self.data["targets"]:
                desc = self.data["targets"][cmd]["description"]
                doc.append(f"make {cmd:<15} # {desc}")

        doc.append("```")
        doc.append("")

        # Group targets by category
        categories = self._categorize_targets()

        for category, targets in categories.items():
            doc.append(f"## {category}")
            doc.append("")

            for target_name in targets:
                target = self.data["targets"][target_name]
                doc.append(f"#### `make {target_name}`")
                doc.append(f"**Purpose**: {target['description']}")
                doc.append(f"**Usage**: `make {target_name}`")

                if target["dependencies"]:
                    doc.append(f"**Dependencies**: {', '.join(target['dependencies'])}")

                if target["commands"]:
                    doc.append("**Actions**:")
                    for cmd in target["commands"][:3]:  # Show first 3 commands
                        if not cmd.startswith("@") and not cmd.startswith("#"):
                            doc.append(f"- {cmd.strip()}")

                doc.append("")

        # Variables section
        if self.data["variables"]:
            doc.append("## 🔧 Configuration Variables")
            doc.append("")

            for var_name, var_info in self.data["variables"].items():
                if var_info["comment"]:
                    doc.append(f"- **{var_name}**: {var_info['value']} - {var_info['comment']}")
                else:
                    doc.append(f"- **{var_name}**: {var_info['value']}")

            doc.append("")

        # Footer
        doc.append("---")
        doc.append("")
        doc.append("**Note**: This documentation is automatically generated from the Makefile.")
        doc.append("Run `make docs-update` to refresh after Makefile changes.")

        return "\n".join(doc)

    def _categorize_targets(self) -> dict[str, list[str]]:
        """Categorize targets based on their names and descriptions"""
        categories = {
            "🔧 Setup and Installation": [],
            "🐳 Docker Services Management": [],
            "🗄️ Database Operations": [],
            "🔧 Protobuf Operations": [],
            "🏗️ Backend Development": [],
            "🚀 Development Workflows": [],
            "🧪 Testing and Debugging": [],
            "🧹 Cleanup Operations": [],
            "📋 Information and Help": [],
            "🔗 Aliases": [],
        }

        for target_name, target_info in self.data["targets"].items():
            desc = target_info["description"].lower()

            if any(word in target_name for word in ["setup", "install"]):
                categories["🔧 Setup and Installation"].append(target_name)
            elif any(word in target_name for word in ["up", "down", "restart", "logs"]):
                categories["🐳 Docker Services Management"].append(target_name)
            elif target_name.startswith("db-"):
                categories["🗄️ Database Operations"].append(target_name)
            elif target_name.startswith("proto-"):
                categories["🔧 Protobuf Operations"].append(target_name)
            elif target_name.startswith("backend-"):
                categories["🏗️ Backend Development"].append(target_name)
            elif target_name.startswith("dev"):
                categories["🚀 Development Workflows"].append(target_name)
            elif any(word in target_name for word in ["test", "debug", "health"]):
                categories["🧪 Testing and Debugging"].append(target_name)
            elif any(word in target_name for word in ["clean"]):
                categories["🧹 Cleanup Operations"].append(target_name)
            elif any(word in target_name for word in ["help", "status", "version", "ports"]):
                categories["📋 Information and Help"].append(target_name)
            elif target_name in ["build", "run", "demo", "test"]:
                categories["🔗 Aliases"].append(target_name)
            else:
                # Default category
                categories["🔧 Setup and Installation"].append(target_name)

        # Remove empty categories
        return {k: v for k, v in categories.items() if v}


def main():
    """Main function to generate documentation"""
    if len(sys.argv) > 1:
        makefile_path = sys.argv[1]
    else:
        makefile_path = "Makefile"

    if not os.path.exists(makefile_path):
        print(f"Error: Makefile not found at {makefile_path}")
        sys.exit(1)

    # Analyze Makefile
    analyzer = MakefileAnalyzer(makefile_path)
    analysis_data = analyzer.analyze()

    # Generate documentation
    generator = DocumentationGenerator(analysis_data)
    reference_doc = generator.generate_reference_doc()

    # Write to output file
    output_path = "docs/development/makefile-reference.md"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        f.write(reference_doc)

    print(f"✅ Generated Makefile documentation: {output_path}")
    print(f"📊 Found {len(analysis_data['targets'])} targets")
    print(f"📊 Found {len(analysis_data['variables'])} variables")
    print(f"📊 Found {len(analysis_data['functions'])} functions")


if __name__ == "__main__":
    main()
