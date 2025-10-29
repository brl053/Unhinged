#!/usr/bin/env python3

"""
@llm-type service.builder
@llm-does polyglot protobuf client generation for multiple languages
"""

import hashlib
import json
import subprocess
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
try:
    from . import BuildModule, BuildContext, BuildModuleResult, BuildUtils, BuildArtifact
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from __init__ import BuildModule, BuildContext, BuildModuleResult, BuildUtils, BuildArtifact

@dataclass
class ProtoLanguageConfig:
    """Configuration for a specific language's proto generation"""
    name: str
    plugin: str
    output_flag: str
    options: List[str]
    extensions: List[str]
    requires_tools: List[str]
    post_process: Optional[str] = None

@dataclass
class ProtoGenerationResult:
    """Result of proto generation for a specific language"""
    language: str
    artifacts: List[BuildArtifact]
    warnings: List[str]
    duration: float
    success: bool
    error_message: Optional[str] = None

class ProtoLanguageHandler(ABC):
    """Abstract base class for language-specific proto generation handlers"""
    
    def __init__(self, config: ProtoLanguageConfig, context: BuildContext):
        self.config = config
        self.context = context
        import logging
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def validate_tools(self) -> List[str]:
        """Validate required tools are available, return missing tools"""
        pass
    
    @abstractmethod
    def prepare_output_directory(self, output_dir: Path) -> bool:
        """Prepare output directory for generation"""
        pass
    
    @abstractmethod
    def build_protoc_command(self, proto_files: List[Path], output_dir: Path, proto_path: Path) -> List[str]:
        """Build protoc command for this language"""
        pass
    
    @abstractmethod
    def post_process_artifacts(self, output_dir: Path) -> List[BuildArtifact]:
        """Post-process generated files and return artifacts"""
        pass
    
    def generate_clients(self, proto_files: List[Path], output_dir: Path, proto_path: Path) -> ProtoGenerationResult:
        """Generate proto clients for this language"""
        start_time = time.time()
        warnings = []
        artifacts = []
        
        try:
            # Validate tools
            missing_tools = self.validate_tools()
            if missing_tools:
                warning = f"Missing tools for {self.config.name}: {', '.join(missing_tools)}"
                warnings.append(warning)
                self.logger.warning(warning)
                return ProtoGenerationResult(
                    language=self.config.name,
                    artifacts=[],
                    warnings=warnings,
                    duration=time.time() - start_time,
                    success=False,
                    error_message=warning
                )
            
            # Prepare output directory
            if not self.prepare_output_directory(output_dir):
                warnings.append(f"Failed to prepare output directory for {self.config.name}")
                return ProtoGenerationResult(
                    language=self.config.name,
                    artifacts=[],
                    warnings=warnings,
                    duration=time.time() - start_time,
                    success=False,
                    error_message="Failed to prepare output directory"
                )
            
            # Build and execute protoc command
            cmd = self.build_protoc_command(proto_files, output_dir, proto_path)
            success, stdout, stderr = BuildUtils.run_command(' '.join(cmd), self.context.project_root)
            
            if not success:
                warnings.append(f"{self.config.name} generation failed: {stderr}")
                return ProtoGenerationResult(
                    language=self.config.name,
                    artifacts=[],
                    warnings=warnings,
                    duration=time.time() - start_time,
                    success=False,
                    error_message=stderr
                )
            
            # Post-process and collect artifacts
            artifacts = self.post_process_artifacts(output_dir)
            
            self.logger.info(f"Generated {len(artifacts)} {self.config.name} proto client artifacts")
            
            return ProtoGenerationResult(
                language=self.config.name,
                artifacts=artifacts,
                warnings=warnings,
                duration=time.time() - start_time,
                success=True,
                error_message=None
            )
            
        except Exception as e:
            warnings.append(f"Unexpected error generating {self.config.name} clients: {str(e)}")
            self.logger.error(f"Error in {self.config.name} proto generation: {e}")
            return ProtoGenerationResult(
                language=self.config.name,
                artifacts=[],
                warnings=warnings,
                duration=time.time() - start_time,
                success=False,
                error_message=str(e)
            )

class PolyglotProtoEngine:
    """
@llm-type config.build
@llm-does unified engine for generating protobuf clients across
"""
    
    def __init__(self, context: BuildContext):
        self.context = context
        import logging
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.proto_dir = context.project_root / "proto"
        self.output_base = context.project_root / "generated"
        
        # Language configurations
        self.language_configs = {
            'typescript': ProtoLanguageConfig(
                name='typescript',
                plugin='ts-proto',
                output_flag='--ts_proto_out',
                options=[
                    'esModuleInterop=true',
                    'forceLong=string',
                    'useOptionals=messages',
                    'outputServices=grpc-js',
                    'outputClientImpl=grpc-web'
                ],
                extensions=['.ts'],
                requires_tools=['protoc', 'node']
            ),
            'c': ProtoLanguageConfig(
                name='c',
                plugin='cpp',
                output_flag='--cpp_out',
                options=[],
                extensions=['.pb.h', '.pb.cc'],
                requires_tools=['protoc', 'grpc_cpp_plugin']
            ),
            'python': ProtoLanguageConfig(
                name='python',
                plugin='python',
                output_flag='--python_out',
                options=[],
                extensions=['.py', '_pb2.py', '_pb2_grpc.py'],
                requires_tools=['protoc', 'python3']
            ),
            'kotlin': ProtoLanguageConfig(
                name='kotlin',
                plugin='kotlin',
                output_flag='--kotlin_out',
                options=[],
                extensions=['.kt'],
                requires_tools=['protoc', 'java', 'gradle']
            )
        }
        
        # Language handlers (will be populated by register_handler)
        self.handlers: Dict[str, ProtoLanguageHandler] = {}
    
    def register_handler(self, language: str, handler: ProtoLanguageHandler):
        """Register a language-specific handler"""
        self.handlers[language] = handler
    
    def get_proto_files(self) -> List[Path]:
        """Get all proto files in the proto directory"""
        if not self.proto_dir.exists():
            return []

        # Get all proto files
        all_files = list(self.proto_dir.rglob("*.proto"))

        # Exclude problematic files that cause conflicts
        excluded_files = {
            "chat_with_gateway.proto",  # Conflicts with chat.proto
            "universal_event.proto",    # Conflicts with cdc_events.proto
        }

        # Filter out excluded files
        filtered_files = []
        for file in all_files:
            if file.name not in excluded_files:
                filtered_files.append(file)
            else:
                self.logger.info(f"Excluding problematic proto file: {file.name}")

        return filtered_files
    
    def calculate_cache_key(self, languages: List[str]) -> str:
        """Calculate cache key for proto generation"""
        hasher = hashlib.sha256()
        
        # Hash proto files
        proto_files = self.get_proto_files()
        for proto_file in sorted(proto_files):
            hasher.update(str(proto_file).encode())
            if proto_file.exists():
                hasher.update(BuildUtils.calculate_file_hash(proto_file).encode())
        
        # Hash language configurations
        for lang in sorted(languages):
            if lang in self.language_configs:
                config_str = json.dumps(self.language_configs[lang].__dict__, sort_keys=True)
                hasher.update(config_str.encode())
        
        return hasher.hexdigest()
    
    def generate_clients(self, languages: List[str]) -> Tuple[List[BuildArtifact], List[str]]:
        """Generate proto clients for specified languages"""
        all_artifacts = []
        all_warnings = []
        
        proto_files = self.get_proto_files()
        if not proto_files:
            warning = f"No proto files found in {self.proto_dir}"
            all_warnings.append(warning)
            self.logger.warning(warning)
            return all_artifacts, all_warnings
        
        self.logger.info(f"Generating proto clients for languages: {', '.join(languages)}")
        self.logger.info(f"Found {len(proto_files)} proto files")
        
        # Generate clients for each language
        for language in languages:
            if language not in self.language_configs:
                warning = f"Unknown language: {language}"
                all_warnings.append(warning)
                self.logger.warning(warning)
                continue
            
            if language not in self.handlers:
                warning = f"No handler registered for language: {language}"
                all_warnings.append(warning)
                self.logger.warning(warning)
                continue
            
            # Prepare output directory
            output_dir = self.output_base / language / "clients"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate clients using language handler
            handler = self.handlers[language]
            result = handler.generate_clients(proto_files, output_dir, self.proto_dir)
            
            all_artifacts.extend(result.artifacts)
            all_warnings.extend(result.warnings)
            
            if result.success:
                self.logger.info(f"✅ {language} generation completed in {result.duration:.2f}s")
            else:
                error_msg = f"❌ {language} generation failed"
                if result.error_message:
                    error_msg += f": {result.error_message}"
                self.logger.error(error_msg)
        
        return all_artifacts, all_warnings
    
    def validate_environment(self) -> Dict[str, List[str]]:
        """Validate that required tools are available for all languages"""
        validation_results = {}

        for language, config in self.language_configs.items():
            # Use handler's validation if available, otherwise use config
            if language in self.handlers:
                missing_tools = self.handlers[language].validate_tools()
            else:
                missing_tools = []
                for tool in config.requires_tools:
                    if not BuildUtils.check_tool_available(tool):
                        missing_tools.append(tool)
            validation_results[language] = missing_tools

        return validation_results
