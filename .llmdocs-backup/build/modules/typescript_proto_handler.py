#!/usr/bin/env python3

"""
@llm-type proto-handler
@llm-legend TypeScript protobuf client generation handler with gRPC-Web support for browser applications
@llm-key Generates TypeScript protobuf clients with gRPC-Web integration for frontend applications
@llm-map TypeScript language handler for the polyglot proto engine providing browser-compatible gRPC clients
@llm-axiom TypeScript proto clients must support both Node.js and browser environments with type safety
@llm-contract Implements ProtoLanguageHandler interface for TypeScript protobuf and gRPC-Web client generation
@llm-token typescript-proto-handler: Type-safe TypeScript protobuf client generation for web applications

TypeScript Protocol Buffer Client Handler

Generates type-safe TypeScript protobuf clients for:
- Browser applications (gRPC-Web)
- Node.js services (gRPC)
- Frontend frameworks (React, Vue, Angular)
- Static HTML interfaces

Features:
- ts-proto plugin integration
- gRPC-Web client generation
- Type-safe interfaces
- ESModule compatibility
- Tree-shaking support

Author: Unhinged Team
Version: 1.0.0
Date: 2025-10-20
"""

import json
from pathlib import Path
from typing import List
try:
    from .polyglot_proto_engine import ProtoLanguageHandler, ProtoLanguageConfig
    from . import BuildUtils, BuildArtifact, BuildContext
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from polyglot_proto_engine import ProtoLanguageHandler, ProtoLanguageConfig
    from __init__ import BuildUtils, BuildArtifact, BuildContext

class TypeScriptProtoHandler(ProtoLanguageHandler):
    """TypeScript protobuf client generation handler"""
    
    def validate_tools(self) -> List[str]:
        """Validate TypeScript protobuf tools are available"""
        missing_tools = []
        
        # Check for protoc
        if not BuildUtils.check_tool_available('protoc'):
            missing_tools.append('protoc')
        
        # Check for ts-proto plugin
        ts_proto_bin = self.context.project_root / "node_modules" / ".bin" / "protoc-gen-ts_proto"
        if not ts_proto_bin.exists():
            missing_tools.append('protoc-gen-ts_proto (run: npm install ts-proto)')
        
        # Check for Node.js
        if not BuildUtils.check_tool_available('node'):
            missing_tools.append('node')
        
        return missing_tools
    
    def prepare_output_directory(self, output_dir: Path) -> bool:
        """Prepare TypeScript output directory structure"""
        try:
            # Create TypeScript module structure
            types_dir = output_dir / "types"
            services_dir = output_dir / "services"
            
            types_dir.mkdir(parents=True, exist_ok=True)
            services_dir.mkdir(parents=True, exist_ok=True)
            
            # Create package.json for the generated clients
            package_json = self._generate_package_json()
            package_file = output_dir / "package.json"
            with open(package_file, 'w') as f:
                json.dump(package_json, f, indent=2)
            
            # Create TypeScript configuration
            tsconfig = self._generate_tsconfig()
            tsconfig_file = output_dir / "tsconfig.json"
            with open(tsconfig_file, 'w') as f:
                json.dump(tsconfig, f, indent=2)
            
            # Create index.ts for easy imports
            index_content = self._generate_index_content()
            index_file = output_dir / "index.ts"
            with open(index_file, 'w') as f:
                f.write(index_content)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to prepare TypeScript output directory: {e}")
            return False
    
    def build_protoc_command(self, proto_files: List[Path], output_dir: Path, proto_path: Path) -> List[str]:
        """Build protoc command for TypeScript generation"""
        ts_proto_bin = self.context.project_root / "node_modules" / ".bin" / "protoc-gen-ts_proto"
        
        cmd = [
            'protoc',
            f'--proto_path={proto_path}',
            f'--plugin={ts_proto_bin}',
            f'--ts_proto_out={output_dir}',
            '--ts_proto_opt=esModuleInterop=true',
            '--ts_proto_opt=forceLong=string',
            '--ts_proto_opt=useOptionals=messages',
            '--ts_proto_opt=outputServices=grpc-js',
            '--ts_proto_opt=outputClientImpl=grpc-web',
            '--ts_proto_opt=exportCommonSymbols=false'
        ]
        
        # Add proto files
        cmd.extend([str(pf) for pf in proto_files])
        
        return cmd
    
    def post_process_artifacts(self, output_dir: Path) -> List[BuildArtifact]:
        """Post-process TypeScript generated files"""
        artifacts = []
        
        try:
            # Collect all generated TypeScript files
            for ts_file in output_dir.rglob("*.ts"):
                if ts_file.name != "index.ts":  # Skip our generated index
                    artifacts.append(BuildUtils.create_build_artifact(
                        ts_file,
                        'typescript-client',
                        {'language': 'typescript', 'grpc_web': True}
                    ))
            
            # Create artifacts for configuration files
            package_file = output_dir / "package.json"
            if package_file.exists():
                artifacts.append(BuildUtils.create_build_artifact(
                    package_file,
                    'typescript-package',
                    {'language': 'typescript', 'type': 'package-config'}
                ))
            
            tsconfig_file = output_dir / "tsconfig.json"
            if tsconfig_file.exists():
                artifacts.append(BuildUtils.create_build_artifact(
                    tsconfig_file,
                    'typescript-config',
                    {'language': 'typescript', 'type': 'ts-config'}
                ))
            
            # Update index.ts with actual generated files
            self._update_index_file(output_dir)
            index_file = output_dir / "index.ts"
            if index_file.exists():
                artifacts.append(BuildUtils.create_build_artifact(
                    index_file,
                    'typescript-index',
                    {'language': 'typescript', 'type': 'module-index'}
                ))
            
            self.logger.info(f"Generated {len(artifacts)} TypeScript proto artifacts")
            
        except Exception as e:
            self.logger.error(f"Error post-processing TypeScript artifacts: {e}")
        
        return artifacts
    
    def _generate_package_json(self) -> dict:
        """Generate package.json for TypeScript proto clients"""
        return {
            "name": "@unhinged/proto-clients-typescript",
            "version": "1.0.0",
            "description": "Generated TypeScript protobuf clients for Unhinged platform",
            "main": "index.js",
            "types": "index.d.ts",
            "scripts": {
                "build": "tsc",
                "clean": "rm -rf dist"
            },
            "dependencies": {
                "@grpc/grpc-js": "^1.9.0",
                "grpc-web": "^1.4.0",
                "google-protobuf": "^3.21.0"
            },
            "devDependencies": {
                "typescript": "^5.0.0",
                "@types/google-protobuf": "^3.15.0"
            },
            "keywords": ["protobuf", "grpc", "typescript", "unhinged"],
            "author": "Unhinged Team",
            "license": "MIT"
        }
    
    def _generate_tsconfig(self) -> dict:
        """Generate TypeScript configuration"""
        return {
            "compilerOptions": {
                "target": "ES2020",
                "module": "ESNext",
                "moduleResolution": "node",
                "declaration": True,
                "outDir": "dist",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "resolveJsonModule": True
            },
            "include": ["**/*.ts"],
            "exclude": ["node_modules", "dist"]
        }
    
    def _generate_index_content(self) -> str:
        """Generate initial index.ts content"""
        return """// Generated TypeScript Proto Clients Index
// This file is auto-generated - do not edit manually

// Export all generated proto types and services
// Individual exports will be added during post-processing

export * from './types';
export * from './services';

// Re-export common types for convenience
export type { Empty } from 'google-protobuf/google/protobuf/empty_pb';
export type { Timestamp } from 'google-protobuf/google/protobuf/timestamp_pb';
"""
    
    def _update_index_file(self, output_dir: Path):
        """Update index.ts with actual generated files"""
        try:
            exports = []
            
            # Find all generated TypeScript files
            for ts_file in output_dir.rglob("*.ts"):
                if ts_file.name == "index.ts":
                    continue
                
                # Convert file path to module import
                relative_path = ts_file.relative_to(output_dir)
                module_path = str(relative_path.with_suffix(''))
                exports.append(f"export * from './{module_path}';")
            
            if exports:
                index_content = """// Generated TypeScript Proto Clients Index
// This file is auto-generated - do not edit manually

""" + "\n".join(sorted(exports)) + """

// Re-export common types for convenience
export type { Empty } from 'google-protobuf/google/protobuf/empty_pb';
export type { Timestamp } from 'google-protobuf/google/protobuf/timestamp_pb';
"""
                
                index_file = output_dir / "index.ts"
                with open(index_file, 'w') as f:
                    f.write(index_content)
                
        except Exception as e:
            self.logger.error(f"Failed to update TypeScript index file: {e}")
