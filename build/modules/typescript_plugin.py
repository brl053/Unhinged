#!/usr/bin/env python3
"""
TypeScript Builder Plugin

Implements the standardized plugin interface for TypeScript builds.
Handles TypeScript projects using npm/webpack build system.

@llm-type plugin.typescript
@llm-does typescript builds with standardized plugin interface
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Any

try:
    from ..core.plugin_interface import (
        BuilderPlugin, PluginMetadata, PluginCapability, FilePattern, 
        PluginResult, BuildArtifact
    )
    from . import BuildContext, BuildUtils
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.plugin_interface import (
        BuilderPlugin, PluginMetadata, PluginCapability, FilePattern, 
        PluginResult, BuildArtifact
    )
    from modules import BuildContext, BuildUtils

class TypeScriptBuilderPlugin(BuilderPlugin):
    """TypeScript builder implementing standardized plugin interface."""
    
    def __init__(self, context: BuildContext):
        super().__init__(context)
        self.frontend_dir = self.context.project_root / "frontend"
        self.package_json = self.frontend_dir / "package.json"
        self.tsconfig = self.frontend_dir / "tsconfig.json"
        self.dist_dir = self.frontend_dir / "dist"
    
    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="typescript",
            version="2.0.0",
            description="TypeScript builder with npm/webpack support",
            author="Unhinged Build System",
            supported_extensions=[".ts", ".tsx", ".js", ".jsx"],
            capabilities={
                PluginCapability.INCREMENTAL_BUILD,
                PluginCapability.PARALLEL_BUILD,
                PluginCapability.DEPENDENCY_RESOLUTION,
                PluginCapability.CACHE_OPTIMIZATION,
                PluginCapability.HOT_RELOAD,
                PluginCapability.TESTING,
                PluginCapability.LINTING,
                PluginCapability.PACKAGING
            },
            dependencies=["node", "npm"]
        )
    
    @property
    def file_patterns(self) -> List[FilePattern]:
        """Return file patterns this plugin can handle."""
        return [
            FilePattern(".ts", priority=10, required_files=["package.json", "tsconfig.json"]),
            FilePattern(".tsx", priority=10, required_files=["package.json", "tsconfig.json"]),
            FilePattern(".js", priority=8, required_files=["package.json"]),
            FilePattern(".jsx", priority=8, required_files=["package.json"]),
            FilePattern(".ts", priority=5),  # Generic TypeScript files
            FilePattern(".js", priority=3)   # Generic JavaScript files
        ]
    
    def detect_files(self, path: Path) -> List[Path]:
        """Return list of TypeScript/JavaScript files this builder handles."""
        source_files = []
        
        # Look for TypeScript and JavaScript files
        for pattern in ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"]:
            source_files.extend(path.glob(pattern))
        
        # Filter out common non-source directories
        excluded_dirs = {"node_modules", "dist", "build", ".git", "coverage"}
        
        filtered_files = []
        for file_path in source_files:
            if any(excluded_dir in file_path.parts for excluded_dir in excluded_dirs):
                continue
            filtered_files.append(file_path)
        
        return filtered_files
    
    def calculate_checksum(self, file_paths: List[Path]) -> str:
        """Calculate content-based checksum for caching."""
        return self._calculate_combined_checksum(file_paths)
    
    def get_dependencies(self, file_paths: List[Path]) -> List[Path]:
        """Get list of file dependencies for TypeScript files."""
        dependencies = set()
        
        # Add npm configuration files
        config_files = [
            self.package_json,
            self.tsconfig.json,
            self.frontend_dir / "webpack.config.js",
            self.frontend_dir / "webpack.config.ts",
            self.frontend_dir / ".eslintrc.js",
            self.frontend_dir / ".eslintrc.json",
            self.frontend_dir / "package-lock.json",
            self.frontend_dir / "yarn.lock"
        ]
        
        for config_file in config_files:
            if config_file.exists():
                dependencies.add(config_file)
        
        # Parse imports from TypeScript/JavaScript files
        for file_path in file_paths:
            if file_path.suffix in [".ts", ".tsx", ".js", ".jsx"]:
                imported_files = self._parse_local_imports(file_path)
                dependencies.update(imported_files)
        
        return list(dependencies)
    
    def _parse_local_imports(self, file_path: Path) -> List[Path]:
        """Parse local imports from a TypeScript/JavaScript file."""
        local_imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            
            # Find relative imports
            import_patterns = [
                r'import.*from\s+[\'"](\./[^\'"]+)[\'"]',  # import from './module'
                r'import.*from\s+[\'"](\.\./[^\'"]+)[\'"]',  # import from '../module'
                r'require\([\'"](\./[^\'"]+)[\'"]\)',  # require('./module')
                r'require\([\'"](\.\./[^\'"]+)[\'"]\)'  # require('../module')
            ]
            
            base_dir = file_path.parent
            
            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    # Convert import path to file path
                    import_path = Path(match)
                    
                    # Try different extensions
                    possible_files = [
                        base_dir / f"{import_path}.ts",
                        base_dir / f"{import_path}.tsx",
                        base_dir / f"{import_path}.js",
                        base_dir / f"{import_path}.jsx",
                        base_dir / import_path / "index.ts",
                        base_dir / import_path / "index.js"
                    ]
                    
                    for possible_file in possible_files:
                        if possible_file.exists():
                            local_imports.append(possible_file)
                            break
        
        except Exception as e:
            self.logger.warning(f"Failed to parse imports from {file_path}: {e}")
        
        return local_imports
    
    def validate_environment(self) -> List[str]:
        """Validate TypeScript/Node environment."""
        missing_requirements = []
        
        # Check Node.js
        if not self._check_tool_available("node"):
            missing_requirements.append("node")
        
        # Check npm
        if not self._check_tool_available("npm"):
            missing_requirements.append("npm")
        
        # Check package.json
        if not self.package_json.exists():
            missing_requirements.append("package.json")
        
        # Check if node_modules exists (dependencies installed)
        node_modules = self.frontend_dir / "node_modules"
        if not node_modules.exists():
            missing_requirements.append("node_modules (run npm install)")
        
        return missing_requirements
    
    def build(self, file_paths: List[Path], options: Dict[str, Any] = None) -> PluginResult:
        """Execute TypeScript build."""
        start_time = time.time()
        options = options or {}
        
        # Validate environment
        env_errors = self.validate_environment()
        if env_errors:
            return PluginResult(
                success=False,
                duration=0.0,
                artifacts=[],
                error_message=f"Environment validation failed: {'; '.join(env_errors)}"
            )
        
        self.logger.info(f"🔨 Building {len(file_paths)} TypeScript files")
        
        # Determine npm script based on options
        npm_script = options.get("script", "build")
        npm_args = options.get("args", [])
        
        # Build npm command
        command = f"npm run {npm_script}"
        if npm_args:
            command += f" -- {' '.join(npm_args)}"
        
        self.logger.info(f"🔧 Running: {command}")
        
        # Execute build
        success, stdout, stderr = self._run_command(
            command, 
            self.frontend_dir,
            timeout=300  # 5 minutes for TypeScript builds
        )
        
        duration = time.time() - start_time
        
        if not success:
            return PluginResult(
                success=False,
                duration=duration,
                artifacts=[],
                error_message=f"npm build failed: {stderr}",
                warnings=self._extract_warnings(stdout)
            )
        
        # Collect build artifacts
        artifacts = self._collect_build_artifacts()
        warnings = self._extract_warnings(stdout)
        
        return PluginResult(
            success=True,
            duration=duration,
            artifacts=artifacts,
            warnings=warnings,
            metrics={
                "files_processed": len(file_paths),
                "npm_script": npm_script
            }
        )
    
    def _collect_build_artifacts(self) -> List[BuildArtifact]:
        """Collect TypeScript build artifacts."""
        artifacts = []
        
        if not self.dist_dir.exists():
            return artifacts
        
        # Look for JavaScript files in dist
        js_files = list(self.dist_dir.glob("**/*.js"))
        for js_file in js_files:
            artifacts.append(BuildArtifact(
                path=js_file,
                artifact_type="javascript",
                size_bytes=js_file.stat().st_size,
                checksum=self._calculate_file_checksum(js_file),
                metadata={"language": "typescript", "compiled": True}
            ))
        
        # Look for CSS files
        css_files = list(self.dist_dir.glob("**/*.css"))
        for css_file in css_files:
            artifacts.append(BuildArtifact(
                path=css_file,
                artifact_type="stylesheet",
                size_bytes=css_file.stat().st_size,
                checksum=self._calculate_file_checksum(css_file),
                metadata={"language": "css"}
            ))
        
        # Look for HTML files
        html_files = list(self.dist_dir.glob("**/*.html"))
        for html_file in html_files:
            artifacts.append(BuildArtifact(
                path=html_file,
                artifact_type="html",
                size_bytes=html_file.stat().st_size,
                checksum=self._calculate_file_checksum(html_file),
                metadata={"language": "html"}
            ))
        
        return artifacts
    
    def _extract_warnings(self, output: str) -> List[str]:
        """Extract warnings from npm output."""
        warnings = []
        
        for line in output.split('\n'):
            line = line.strip()
            if ('warning' in line.lower() or 
                'deprecated' in line.lower() or
                'warn' in line.lower()):
                warnings.append(line)
        
        return warnings
    
    def clean(self, file_paths: List[Path]) -> PluginResult:
        """Clean TypeScript build artifacts."""
        start_time = time.time()
        
        # Remove dist directory
        if self.dist_dir.exists():
            import shutil
            shutil.rmtree(self.dist_dir)
        
        duration = time.time() - start_time
        
        return PluginResult(
            success=True,
            duration=duration,
            artifacts=[],
            metrics={"directories_cleaned": 1}
        )
    
    def test(self, file_paths: List[Path], options: Dict[str, Any] = None) -> PluginResult:
        """Run TypeScript tests."""
        start_time = time.time()
        
        # Run npm test
        command = "npm test"
        success, stdout, stderr = self._run_command(command, self.frontend_dir, timeout=300)
        
        duration = time.time() - start_time
        
        return PluginResult(
            success=success,
            duration=duration,
            artifacts=[],
            error_message=stderr if not success else None,
            warnings=self._extract_warnings(stdout),
            metrics={"npm_script": "test"}
        )
    
    def lint(self, file_paths: List[Path], options: Dict[str, Any] = None) -> PluginResult:
        """Run TypeScript linting."""
        start_time = time.time()
        warnings = []
        
        # Run ESLint if available
        ts_files = [f for f in file_paths if f.suffix in [".ts", ".tsx", ".js", ".jsx"]]
        command = f"npx eslint {' '.join(str(f) for f in ts_files)}"
        success, stdout, stderr = self._run_command(command, self.frontend_dir)
        
        if stdout:
            warnings.extend(stdout.split('\n'))
        
        return PluginResult(
            success=True,  # Linting warnings don't fail the build
            duration=time.time() - start_time,
            artifacts=[],
            warnings=warnings,
            metrics={"files_linted": len(ts_files)}
        )
    
    def package(self, file_paths: List[Path], options: Dict[str, Any] = None) -> PluginResult:
        """Create TypeScript package."""
        start_time = time.time()
        
        # Run npm pack to create package
        command = "npm pack"
        success, stdout, stderr = self._run_command(command, self.frontend_dir)
        
        duration = time.time() - start_time
        
        if not success:
            return PluginResult(
                success=False,
                duration=duration,
                artifacts=[],
                error_message=f"npm pack failed: {stderr}"
            )
        
        # Look for generated .tgz file
        tgz_files = list(self.frontend_dir.glob("*.tgz"))
        artifacts = []
        
        for tgz_file in tgz_files:
            artifacts.append(BuildArtifact(
                path=tgz_file,
                artifact_type="package",
                size_bytes=tgz_file.stat().st_size,
                checksum=self._calculate_file_checksum(tgz_file),
                metadata={"language": "typescript", "format": "npm"}
            ))
        
        return PluginResult(
            success=True,
            duration=duration,
            artifacts=artifacts,
            warnings=self._extract_warnings(stdout),
            metrics={"npm_script": "pack"}
        )
