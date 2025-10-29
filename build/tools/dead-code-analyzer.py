#!/usr/bin/env python3
"""
@llm-type util.analyzer
@llm-does dead code detection and removal recommendations across polyglot codebase
@llm-rule dead code analysis must be conservative to prevent accidental removal
"""

import json
import re
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class SafetyLevel(Enum):
    """Safety level for cleanup recommendations"""
    SAFE = "safe"           # Definitely safe to remove
    LIKELY_SAFE = "likely_safe"  # Probably safe, but review recommended
    REVIEW = "review"       # Manual review required
    UNSAFE = "unsafe"       # Do not remove


@dataclass
class DeadCodeItem:
    """Represents a potentially dead/unused code item"""
    path: Path
    item_type: str  # file, directory, module, documentation
    safety_level: SafetyLevel
    reason: str
    references: List[str]
    size_bytes: int
    last_modified: Optional[str] = None
    recommendations: List[str] = None


class DeadCodeAnalyzer:
    """
@llm-type util.function
@llm-does main analyzer implementing multi-approach dead code detec...
"""
    
    def __init__(self, project_root: Path):
        """Initialize analyzer with project root."""
        self.project_root = project_root
        self.makefile_path = project_root / "Makefile"
        self.build_config_path = project_root / "build" / "config" / "build-config.yml"
        
        # Analysis results
        self.makefile_targets = set()
        self.makefile_references = set()
        self.build_config_modules = set()
        self.build_config_references = set()
        self.static_references = set()
        
        # Dead code findings
        self.dead_items = []
        
        # Exclusion patterns (known safe-to-ignore paths)
        self.exclusions = {
            ".git", ".gitignore", "venv", "__pycache__", "node_modules",
            "build/python/venv", ".build-cache", "generated"
        }
    
    def analyze(self) -> List[DeadCodeItem]:
        """
        Perform comprehensive dead code analysis.
        
        Returns:
            List of potentially dead code items with safety classifications
        """
        print("🔍 Starting comprehensive dead code analysis...")
        
        # Phase 1: Extract dependency roots
        self._analyze_makefile()
        self._analyze_build_config()
        
        # Phase 2: Static reference analysis
        self._analyze_static_references()
        
        # Phase 3: Identify dead code candidates
        self._identify_phantom_modules()
        self._identify_orphaned_documentation()
        self._identify_unused_scripts()
        self._identify_unused_build_artifacts()
        
        # Phase 4: Safety classification
        self._classify_safety_levels()
        
        print(f"✅ Analysis complete: {len(self.dead_items)} potential dead code items found")
        return self.dead_items
    
    def _analyze_makefile(self):
        """Extract targets and file references from Makefile."""
        print("  📋 Analyzing Makefile dependencies...")
        
        if not self.makefile_path.exists():
            return
        
        with open(self.makefile_path, 'r') as f:
            content = f.read()
        
        # Extract targets
        target_pattern = r'^([a-zA-Z][a-zA-Z0-9_-]*):.*'
        for match in re.finditer(target_pattern, content, re.MULTILINE):
            self.makefile_targets.add(match.group(1))
        
        # Extract file references
        file_patterns = [
            r'@python3\s+([^\s]+\.py)',
            r'@\$\(PYTHON_RUN\)\s+([^\s]+\.py)',
            r'@cd\s+([^\s]+)',
            r'include\s+([^\s]+)',
            r'@\./([^\s]+)',
        ]
        
        for pattern in file_patterns:
            for match in re.finditer(pattern, content):
                ref_path = match.group(1)
                if not ref_path.startswith('$'):  # Skip variables
                    self.makefile_references.add(ref_path)
    
    def _analyze_build_config(self):
        """Extract modules and references from build configuration."""
        print("  🔧 Analyzing build configuration...")
        
        if not self.build_config_path.exists():
            return
        
        try:
            with open(self.build_config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Extract build targets
            if 'targets' in config:
                for target_name, target_config in config['targets'].items():
                    self.build_config_modules.add(target_name)
                    
                    # Extract input/output references
                    for input_path in target_config.get('inputs', []):
                        self.build_config_references.add(input_path)
                    for output_path in target_config.get('outputs', []):
                        self.build_config_references.add(output_path)
            
            # Extract module configurations
            if 'modules' in config:
                for module_name, module_config in config['modules'].items():
                    self.build_config_modules.add(module_name)
                    
                    # Extract module references
                    if 'config' in module_config:
                        for key, value in module_config['config'].items():
                            if isinstance(value, str) and ('/' in value or value.endswith('.py')):
                                self.build_config_references.add(value)
                            elif isinstance(value, list):
                                for item in value:
                                    if isinstance(item, str) and ('/' in item or item.endswith('.py')):
                                        self.build_config_references.add(item)
        
        except Exception as e:
            print(f"  ⚠️  Failed to parse build config: {e}")
    
    def _analyze_static_references(self):
        """Analyze static file references across the codebase."""
        print("  🔗 Analyzing static file references...")
        
        # File patterns to search for references
        search_patterns = [
            r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)',
            r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import',
            r'require\(["\']([^"\']+)["\']\)',
            r'include\s*["\']([^"\']+)["\']',
            r'@import\s*["\']([^"\']+)["\']',
            r'href=["\']([^"\']+)["\']',
            r'src=["\']([^"\']+)["\']',
        ]
        
        # Search in code files
        code_extensions = {'.py', '.js', '.ts', '.kt', '.c', '.h', '.md', '.html', '.css', '.yaml', '.yml'}
        
        for file_path in self.project_root.rglob('*'):
            if (file_path.is_file() and 
                file_path.suffix in code_extensions and
                not any(excl in str(file_path) for excl in self.exclusions)):
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    for pattern in search_patterns:
                        for match in re.finditer(pattern, content):
                            ref = match.group(1)
                            self.static_references.add(ref)
                
                except Exception:
                    continue  # Skip files that can't be read
    
    def _identify_phantom_modules(self):
        """Identify phantom modules (configured but not implemented)."""
        print("  👻 Identifying phantom modules...")
        
        # Check build config modules against actual files
        for module_name in self.build_config_modules:
            # Convert module name to expected file path
            expected_paths = [
                self.project_root / "build" / "modules" / f"{module_name}.py",
                self.project_root / "build" / "modules" / f"{module_name}_builder.py",
                self.project_root / "libs" / "design_system" / "build" / f"{module_name}.py",
            ]
            
            exists = any(path.exists() for path in expected_paths)
            
            if not exists:
                # Check if it's referenced in Makefile
                referenced_in_makefile = any(module_name in target for target in self.makefile_targets)
                
                if referenced_in_makefile:
                    self.dead_items.append(DeadCodeItem(
                        path=Path(f"phantom:{module_name}"),
                        item_type="phantom_module",
                        safety_level=SafetyLevel.SAFE,
                        reason=f"Module '{module_name}' configured in build-config.yml but implementation missing",
                        references=[],
                        size_bytes=0,
                        recommendations=[
                            f"Remove '{module_name}' from build-config.yml",
                            f"Remove '{module_name}' references from Makefile",
                            "Verify no other configurations reference this module"
                        ]
                    ))
    
    def _identify_orphaned_documentation(self):
        """Identify documentation files that aren't linked or referenced."""
        print("  📚 Identifying orphaned documentation...")
        
        # Find all markdown files
        md_files = list(self.project_root.rglob('*.md'))
        
        for md_file in md_files:
            if any(excl in str(md_file) for excl in self.exclusions):
                continue
            
            relative_path = md_file.relative_to(self.project_root)
            
            # Check if referenced in other files
            referenced = False
            ref_count = 0
            
            # Check for references in the static analysis
            for ref in self.static_references:
                if str(relative_path) in ref or md_file.name in ref:
                    referenced = True
                    ref_count += 1
            
            # Check for references in Makefile
            if str(relative_path) in self.makefile_references:
                referenced = True
                ref_count += 1
            
            # Special cases - always keep certain docs
            important_docs = {'README.md', 'CHANGELOG.md', 'LICENSE.md', 'CONTRIBUTING.md'}
            if md_file.name in important_docs:
                continue
            
            if not referenced or ref_count < 2:
                safety = SafetyLevel.REVIEW if ref_count == 1 else SafetyLevel.LIKELY_SAFE
                
                self.dead_items.append(DeadCodeItem(
                    path=relative_path,
                    item_type="documentation",
                    safety_level=safety,
                    reason=f"Documentation file with {ref_count} references found",
                    references=[],
                    size_bytes=md_file.stat().st_size,
                    recommendations=[
                        "Review if documentation is still relevant",
                        "Consider consolidating with other documentation",
                        "Add references if documentation should be kept"
                    ]
                ))
    
    def _identify_unused_scripts(self):
        """Identify scripts that aren't referenced in build system."""
        print("  📜 Identifying unused scripts...")
        
        # Find Python scripts outside of main modules
        script_dirs = [
            self.project_root / "build" / "scripts",
            self.project_root / "build" / "tools",
            self.project_root / "tools",
        ]
        
        for script_dir in script_dirs:
            if not script_dir.exists():
                continue
            
            for script_file in script_dir.rglob('*.py'):
                if any(excl in str(script_file) for excl in self.exclusions):
                    continue
                
                relative_path = script_file.relative_to(self.project_root)
                
                # Check if referenced in Makefile or build config
                referenced = (
                    str(relative_path) in self.makefile_references or
                    str(relative_path) in self.build_config_references or
                    any(str(relative_path) in ref for ref in self.static_references)
                )
                
                if not referenced:
                    self.dead_items.append(DeadCodeItem(
                        path=relative_path,
                        item_type="script",
                        safety_level=SafetyLevel.REVIEW,
                        reason="Script not referenced in build system or other files",
                        references=[],
                        size_bytes=script_file.stat().st_size,
                        recommendations=[
                            "Review if script is still needed",
                            "Integrate into build system if useful",
                            "Document usage if script should be kept"
                        ]
                    ))
    
    def _identify_unused_build_artifacts(self):
        """Identify unused build artifacts and configurations."""
        print("  🏗️  Identifying unused build artifacts...")
        
        # This is a placeholder for more sophisticated build artifact analysis
        # Could be extended to check for unused Docker files, configs, etc.
        pass
    
    def _classify_safety_levels(self):
        """Refine safety classifications based on additional analysis."""
        print("  🛡️  Classifying safety levels...")
        
        # Additional safety checks could be added here
        # For now, maintain conservative classifications
        pass
    
    def generate_report(self, output_format: str = "text") -> str:
        """Generate cleanup report in specified format."""
        if output_format == "json":
            return self._generate_json_report()
        else:
            return self._generate_text_report()
    
    def _generate_text_report(self) -> str:
        """Generate human-readable text report."""
        report = []
        report.append("🧹 DEAD CODE ANALYSIS REPORT")
        report.append("=" * 50)
        report.append("")
        
        # Summary
        total_items = len(self.dead_items)
        safe_items = len([item for item in self.dead_items if item.safety_level == SafetyLevel.SAFE])
        likely_safe_items = len([item for item in self.dead_items if item.safety_level == SafetyLevel.LIKELY_SAFE])
        review_items = len([item for item in self.dead_items if item.safety_level == SafetyLevel.REVIEW])
        
        report.append(f"📊 SUMMARY:")
        report.append(f"  Total items found: {total_items}")
        report.append(f"  ✅ Safe to remove: {safe_items}")
        report.append(f"  🟡 Likely safe: {likely_safe_items}")
        report.append(f"  🔍 Needs review: {review_items}")
        report.append("")
        
        # Group by safety level
        for safety_level in SafetyLevel:
            items = [item for item in self.dead_items if item.safety_level == safety_level]
            if not items:
                continue
            
            report.append(f"## {safety_level.value.upper().replace('_', ' ')} ({len(items)} items)")
            report.append("")
            
            for item in items:
                report.append(f"📁 {item.path}")
                report.append(f"   Type: {item.item_type}")
                report.append(f"   Reason: {item.reason}")
                if item.size_bytes > 0:
                    report.append(f"   Size: {item.size_bytes:,} bytes")
                if item.recommendations:
                    report.append("   Recommendations:")
                    for rec in item.recommendations:
                        report.append(f"     - {rec}")
                report.append("")
        
        return "\n".join(report)
    
    def _generate_json_report(self) -> str:
        """Generate machine-readable JSON report."""
        data = {
            "analysis_summary": {
                "total_items": len(self.dead_items),
                "by_safety_level": {
                    level.value: len([item for item in self.dead_items if item.safety_level == level])
                    for level in SafetyLevel
                },
                "by_type": {}
            },
            "items": []
        }
        
        # Count by type
        for item in self.dead_items:
            data["analysis_summary"]["by_type"][item.item_type] = \
                data["analysis_summary"]["by_type"].get(item.item_type, 0) + 1
        
        # Add items
        for item in self.dead_items:
            data["items"].append({
                "path": str(item.path),
                "type": item.item_type,
                "safety_level": item.safety_level.value,
                "reason": item.reason,
                "size_bytes": item.size_bytes,
                "recommendations": item.recommendations or []
            })
        
        return json.dumps(data, indent=2)


def main():
    """CLI entry point for dead code analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze dead code and cruft in Unhinged codebase")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format")
    parser.add_argument("--output", type=Path, help="Output file (default: stdout)")
    
    args = parser.parse_args()
    
    # Run analysis
    analyzer = DeadCodeAnalyzer(args.project_root)
    dead_items = analyzer.analyze()
    
    # Generate report
    report = analyzer.generate_report(args.format)
    
    # Output report
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"📄 Report written to: {args.output}")
    else:
        print(report)
    
    return 0


if __name__ == "__main__":
    exit(main())
