#!/usr/bin/env python3

"""
@llm-type service.builder
@llm-does typescript/npm builds with webpack optimization and hot reloading
"""

import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional
try:
    from . import BuildModule, BuildContext, BuildModuleResult, BuildUtils, BuildArtifact
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from __init__ import BuildModule, BuildContext, BuildModuleResult, BuildUtils, BuildArtifact

class TypeScriptBuilder(BuildModule):
    """Build module for TypeScript projects using npm/webpack"""
    
    def __init__(self, context: BuildContext):
        super().__init__(context)
        self.frontend_dir = self.context.project_root / "frontend"
        self.package_json = self.frontend_dir / "package.json"
        self.webpack_config = self.frontend_dir / "webpack.config.js"
        self.dist_dir = self.frontend_dir / "dist"
        self.node_modules = self.frontend_dir / "node_modules"
        
    def can_handle(self, target_name: str) -> bool:
        """Check if this module can handle TypeScript/npm targets"""
        typescript_targets = {
            'frontend-build', 'frontend-compile', 'frontend-test', 
            'frontend-dev', 'typescript-build', 'npm-build', 'webpack-build'
        }
        return target_name in typescript_targets or 'frontend' in target_name or 'typescript' in target_name
    
    def get_dependencies(self, target_name: str) -> List[str]:
        """Get TypeScript source dependencies"""
        dependencies = []
        
        # TypeScript source files
        src_dir = self.frontend_dir / "src"
        if src_dir.exists():
            for ts_file in src_dir.rglob("*.ts"):
                dependencies.append(str(ts_file))
            for tsx_file in src_dir.rglob("*.tsx"):
                dependencies.append(str(tsx_file))
            for js_file in src_dir.rglob("*.js"):
                dependencies.append(str(js_file))
            for jsx_file in src_dir.rglob("*.jsx"):
                dependencies.append(str(jsx_file))
        
        # Configuration files
        config_files = [
            "package.json",
            "package-lock.json",
            "tsconfig.json",
            "webpack.config.js",
            ".babelrc",
            ".eslintrc.js"
        ]
        
        for config_file in config_files:
            file_path = self.frontend_dir / config_file
            if file_path.exists():
                dependencies.append(str(file_path))
        
        # Generated protobuf files (if they exist)
        proto_generated = self.frontend_dir / "src" / "types" / "generated"
        if proto_generated.exists():
            for proto_file in proto_generated.rglob("*.ts"):
                dependencies.append(str(proto_file))
        
        return dependencies
    
    def calculate_cache_key(self, target_name: str) -> str:
        """Calculate cache key based on source files and configuration"""
        import hashlib
        hasher = hashlib.sha256()
        
        # Include target name
        hasher.update(target_name.encode())
        
        # Hash source files
        src_hash = BuildUtils.calculate_directory_hash(
            self.frontend_dir / "src",
            patterns=["*.ts", "*.tsx", "*.js", "*.jsx", "*.css", "*.scss"]
        )
        hasher.update(src_hash.encode())
        
        # Hash package.json for dependency changes
        if self.package_json.exists():
            hasher.update(BuildUtils.calculate_file_hash(self.package_json).encode())
        
        # Hash webpack config
        if self.webpack_config.exists():
            hasher.update(BuildUtils.calculate_file_hash(self.webpack_config).encode())
        
        # Include Node.js version
        node_version = self._get_node_version()
        hasher.update(node_version.encode())
        
        return hasher.hexdigest()
    
    def validate_environment(self) -> List[str]:
        """Validate npm/Node.js environment"""
        errors = []
        
        # Check if Node.js is available
        if not BuildUtils.check_tool_available("node"):
            errors.append("Node.js not found in PATH")
        
        # Check if npm is available
        if not BuildUtils.check_tool_available("npm"):
            errors.append("npm not found in PATH")
        
        # Check if frontend directory exists
        if not self.frontend_dir.exists():
            errors.append(f"Frontend directory not found: {self.frontend_dir}")
        
        # Check if package.json exists
        if not self.package_json.exists():
            errors.append(f"package.json not found: {self.package_json}")
        
        # Check if node_modules exists (dependencies installed)
        if not self.node_modules.exists():
            errors.append("node_modules not found - run 'npm install' first")
        
        return errors
    
    def get_estimated_duration(self, target_name: str) -> float:
        """Estimate build duration based on target type"""
        duration_map = {
            'frontend-compile': 20.0,
            'frontend-build': 60.0,
            'frontend-dev': 15.0,
            'frontend-test': 45.0
        }
        return duration_map.get(target_name, 30.0)
    
    def supports_incremental_build(self, target_name: str) -> bool:
        """TypeScript supports incremental compilation"""
        return target_name in ['frontend-compile', 'frontend-dev']
    
    def supports_parallel_build(self, target_name: str) -> bool:
        """Webpack supports parallel builds"""
        return True
    
    def build(self, target_name: str) -> BuildModuleResult:
        """Execute TypeScript/npm build"""
        start_time = time.time()
        
        # Validate environment first
        env_errors = self.validate_environment()
        if env_errors:
            return BuildModuleResult(
                success=False,
                duration=0.0,
                artifacts=[],
                error_message=f"Environment validation failed: {'; '.join(env_errors)}"
            )
        
        # Determine npm script based on target
        npm_script = self._get_npm_script(target_name)
        if not npm_script:
            return BuildModuleResult(
                success=False,
                duration=0.0,
                artifacts=[],
                error_message=f"Unknown TypeScript target: {target_name}"
            )
        
        # Build npm command
        npm_args = self._get_npm_args(target_name)
        command = f"npm run {npm_script} {' '.join(npm_args)}"
        
        self.logger.info(f"🔨 Building TypeScript target '{target_name}' with command: {command}")
        
        # Execute build
        success, stdout, stderr = BuildUtils.run_command(
            command, 
            self.frontend_dir,
            timeout=300  # 5 minutes for TypeScript builds
        )
        
        duration = time.time() - start_time
        
        if not success:
            return BuildModuleResult(
                success=False,
                duration=duration,
                artifacts=[],
                error_message=f"npm build failed: {stderr}",
                warnings=self._extract_warnings(stdout)
            )
        
        # Collect build artifacts
        artifacts = self._collect_artifacts(target_name)
        
        # Extract build metrics
        metrics = self._extract_build_metrics(stdout)
        
        self.logger.info(f"✅ TypeScript build '{target_name}' completed in {duration:.2f}s")
        
        return BuildModuleResult(
            success=True,
            duration=duration,
            artifacts=artifacts,
            warnings=self._extract_warnings(stdout),
            metrics=metrics
        )
    
    def clean(self, target_name: str) -> bool:
        """Clean TypeScript build artifacts"""
        # Remove dist directory
        if self.dist_dir.exists():
            import shutil
            shutil.rmtree(self.dist_dir)
        
        # Clean npm cache
        command = "npm run clean"
        success, _, _ = BuildUtils.run_command(command, self.frontend_dir)
        return success
    
    def _get_npm_script(self, target_name: str) -> Optional[str]:
        """Map target name to npm script"""
        script_map = {
            'frontend-compile': 'build:dev',
            'frontend-build': 'build',
            'frontend-dev': 'start',
            'frontend-test': 'test',
            'typescript-build': 'build',
            'npm-build': 'build',
            'webpack-build': 'build'
        }
        return script_map.get(target_name)
    
    def _get_npm_args(self, target_name: str) -> List[str]:
        """Get npm arguments based on context and target"""
        args = []
        
        # Environment-specific args
        if self.context.environment == "production":
            args.append("--production")
        elif self.context.environment == "development":
            args.append("--development")
        
        return args
    
    def _get_node_version(self) -> str:
        """Get Node.js version for cache key"""
        command = "node --version"
        success, stdout, _ = BuildUtils.run_command(command, self.frontend_dir, timeout=10)
        
        if success:
            return stdout.strip()
        
        return "unknown"
    
    def _collect_artifacts(self, target_name: str) -> List[BuildArtifact]:
        """Collect build artifacts from npm/webpack build"""
        artifacts = []
        
        # JavaScript bundles
        if self.dist_dir.exists():
            for js_file in self.dist_dir.rglob("*.js"):
                artifacts.append(BuildUtils.create_build_artifact(
                    js_file, 
                    "javascript",
                    {"webpack_bundle": True}
                ))
            
            # CSS files
            for css_file in self.dist_dir.rglob("*.css"):
                artifacts.append(BuildUtils.create_build_artifact(
                    css_file,
                    "stylesheet",
                    {"processed": True}
                ))
            
            # Source maps
            for map_file in self.dist_dir.rglob("*.map"):
                artifacts.append(BuildUtils.create_build_artifact(
                    map_file,
                    "sourcemap",
                    {"debug_info": True}
                ))
            
            # HTML files
            for html_file in self.dist_dir.rglob("*.html"):
                artifacts.append(BuildUtils.create_build_artifact(
                    html_file,
                    "html",
                    {"entry_point": True}
                ))
        
        # Test reports (if running tests)
        if 'test' in target_name:
            test_reports = self.frontend_dir / "test-results"
            if test_reports.exists():
                artifacts.append(BuildUtils.create_build_artifact(
                    test_reports,
                    "test_report",
                    {"format": "junit"}
                ))
        
        return artifacts
    
    def _extract_warnings(self, npm_output: str) -> List[str]:
        """Extract warnings from npm/webpack output"""
        warnings = []
        
        for line in npm_output.split('\n'):
            if 'warning' in line.lower() or 'deprecated' in line.lower():
                warnings.append(line.strip())
            elif 'WARN' in line:
                warnings.append(line.strip())
        
        return warnings
    
    def _extract_build_metrics(self, npm_output: str) -> Dict[str, any]:
        """Extract build metrics from npm/webpack output"""
        metrics = {}
        
        # Extract webpack bundle size
        size_pattern = r'(\d+(?:\.\d+)?)\s*(KB|MB|bytes)'
        matches = re.findall(size_pattern, npm_output, re.IGNORECASE)
        if matches:
            total_size = 0
            for size_str, unit in matches:
                size = float(size_str)
                if unit.upper() == 'KB':
                    size *= 1024
                elif unit.upper() == 'MB':
                    size *= 1024 * 1024
                total_size += size
            metrics['bundle_size_bytes'] = int(total_size)
        
        # Extract compilation time
        time_pattern = r'compiled.*?in (\d+)ms'
        match = re.search(time_pattern, npm_output, re.IGNORECASE)
        if match:
            metrics['compilation_time_ms'] = int(match.group(1))
        
        # Count compiled modules
        modules_pattern = r'(\d+) modules'
        match = re.search(modules_pattern, npm_output)
        if match:
            metrics['compiled_modules'] = int(match.group(1))
        
        # Extract chunk information
        chunks_pattern = r'(\d+) chunks'
        match = re.search(chunks_pattern, npm_output)
        if match:
            metrics['webpack_chunks'] = int(match.group(1))
        
        return metrics
