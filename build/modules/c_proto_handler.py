#!/usr/bin/env python3

"""
@llm-type config.build
@llm-does c/c++ protobuf client generation handler for high-perform...
@llm-rule c++ proto clients must provide maximum performance for system-level services
"""

import os
import shutil
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

class CProtoHandler(ProtoLanguageHandler):
    """C/C++ protobuf client generation handler"""
    
    def __init__(self, config: ProtoLanguageConfig, context: BuildContext):
        super().__init__(config, context)
        self.namespace = "unhinged"
    
    def validate_tools(self) -> List[str]:
        """Validate C++ protobuf tools are available"""
        missing_tools = []
        
        # Check for protoc
        if not BuildUtils.check_tool_available('protoc'):
            missing_tools.append('protoc')
        
        # Check for grpc_cpp_plugin
        if not BuildUtils.check_tool_available('grpc_cpp_plugin'):
            missing_tools.append('grpc_cpp_plugin')
        
        # Check for basic C++ compiler
        if not (BuildUtils.check_tool_available('g++') or BuildUtils.check_tool_available('clang++')):
            missing_tools.append('g++ or clang++')
        
        return missing_tools
    
    def prepare_output_directory(self, output_dir: Path) -> bool:
        """Prepare C++ output directory structure"""
        try:
            # Create standard C++ directory structure
            include_dir = output_dir / "include" / self.namespace
            src_dir = output_dir / "src"
            
            include_dir.mkdir(parents=True, exist_ok=True)
            src_dir.mkdir(parents=True, exist_ok=True)
            
            # Create CMakeLists.txt for easy integration
            cmake_content = self._generate_cmake_content()
            cmake_file = output_dir / "CMakeLists.txt"
            with open(cmake_file, 'w') as f:
                f.write(cmake_content)
            
            # Create pkg-config file for library discovery
            pkgconfig_content = self._generate_pkgconfig_content()
            pkgconfig_dir = output_dir / "pkgconfig"
            pkgconfig_dir.mkdir(exist_ok=True)
            pkgconfig_file = pkgconfig_dir / "unhinged-proto-clients.pc"
            with open(pkgconfig_file, 'w') as f:
                f.write(pkgconfig_content)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to prepare C++ output directory: {e}")
            return False
    
    def build_protoc_command(self, proto_files: List[Path], output_dir: Path, proto_path: Path) -> List[str]:
        """Build protoc command for C++ generation"""
        include_dir = output_dir / "include"
        src_dir = output_dir / "src"
        
        cmd = [
            'protoc',
            f'--proto_path={proto_path}',
            f'--cpp_out={include_dir}',
            f'--grpc_out={include_dir}',
            f'--plugin=protoc-gen-grpc=/usr/bin/grpc_cpp_plugin'
        ]
        
        # Add proto files
        cmd.extend([str(pf) for pf in proto_files])
        
        return cmd
    
    def post_process_artifacts(self, output_dir: Path) -> List[BuildArtifact]:
        """Post-process C++ generated files and organize them"""
        artifacts = []
        include_dir = output_dir / "include"
        src_dir = output_dir / "src"
        
        try:
            # Move .cc files to src directory and create artifacts
            for cc_file in include_dir.rglob("*.cc"):
                # Move to src directory
                dest_file = src_dir / cc_file.name
                shutil.move(str(cc_file), str(dest_file))
                
                artifacts.append(BuildUtils.create_build_artifact(
                    dest_file,
                    'cpp-source',
                    {'language': 'c', 'type': 'source'}
                ))
            
            # Create artifacts for header files
            for header_file in include_dir.rglob("*.h"):
                artifacts.append(BuildUtils.create_build_artifact(
                    header_file,
                    'cpp-header',
                    {'language': 'c', 'type': 'header'}
                ))
            
            # Create artifacts for build files
            cmake_file = output_dir / "CMakeLists.txt"
            if cmake_file.exists():
                artifacts.append(BuildUtils.create_build_artifact(
                    cmake_file,
                    'cmake-config',
                    {'language': 'c', 'type': 'build-config'}
                ))
            
            pkgconfig_file = output_dir / "pkgconfig" / "unhinged-proto-clients.pc"
            if pkgconfig_file.exists():
                artifacts.append(BuildUtils.create_build_artifact(
                    pkgconfig_file,
                    'pkgconfig',
                    {'language': 'c', 'type': 'pkg-config'}
                ))
            
            self.logger.info(f"Organized {len(artifacts)} C++ proto artifacts")
            
        except Exception as e:
            self.logger.error(f"Error post-processing C++ artifacts: {e}")
        
        return artifacts
    
    def _generate_cmake_content(self) -> str:
        """Generate CMakeLists.txt for C++ proto clients"""
        return """# Generated CMakeLists.txt for Unhinged Proto Clients (C++)
cmake_minimum_required(VERSION 3.16)
project(unhinged-proto-clients VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(Protobuf REQUIRED)
find_package(gRPC REQUIRED)

# Include directories
include_directories(include)

# Collect all source files
file(GLOB_RECURSE PROTO_SOURCES "src/*.cc")
file(GLOB_RECURSE PROTO_HEADERS "include/*.h")

# Create library
add_library(unhinged-proto-clients STATIC ${PROTO_SOURCES})

# Link libraries
target_link_libraries(unhinged-proto-clients
    protobuf::libprotobuf
    gRPC::grpc++
    gRPC::grpc++_reflection
)

# Set include directories for consumers
target_include_directories(unhinged-proto-clients PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Installation
install(TARGETS unhinged-proto-clients
    EXPORT unhinged-proto-clients-targets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
)

install(DIRECTORY include/ DESTINATION include)

install(EXPORT unhinged-proto-clients-targets
    FILE unhinged-proto-clients-config.cmake
    DESTINATION lib/cmake/unhinged-proto-clients
)

# Create example usage
add_executable(proto-client-example examples/example.cpp)
target_link_libraries(proto-client-example unhinged-proto-clients)
"""
    
    def _generate_pkgconfig_content(self) -> str:
        """Generate pkg-config file for library discovery"""
        return """# pkg-config file for Unhinged Proto Clients (C++)
prefix=/usr/local
exec_prefix=${prefix}
libdir=${exec_prefix}/lib
includedir=${prefix}/include

Name: unhinged-proto-clients
Description: Unhinged Protocol Buffer Client Libraries (C++)
Version: 1.0.0
Requires: protobuf grpc++
Libs: -L${libdir} -lunhinged-proto-clients
Cflags: -I${includedir}
"""
