#!/usr/bin/env python3

"""
@llm-type proto-handler
@llm-legend Kotlin protobuf client generation handler for JVM services and persistence platform
@llm-key Generates Kotlin protobuf clients with gRPC support for JVM-based services and persistence layer
@llm-map Kotlin language handler for the polyglot proto engine providing JVM gRPC client generation
@llm-axiom Kotlin proto clients must integrate seamlessly with existing JVM services and provide coroutine support
@llm-contract Implements ProtoLanguageHandler interface for Kotlin protobuf and gRPC client generation
@llm-token kotlin-proto-handler: Kotlin protobuf client generation for JVM services and persistence platform

Kotlin Protocol Buffer Client Handler

Generates Kotlin protobuf clients for:
- Persistence platform services
- JVM-based microservices
- Ktor web applications
- Coroutine-based async services

Features:
- Kotlin protobuf generation
- gRPC Kotlin stubs
- Coroutine integration
- Gradle build integration
- Package organization

Author: Unhinged Team
Version: 1.0.0
Date: 2025-10-20
"""

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

class KotlinProtoHandler(ProtoLanguageHandler):
    """Kotlin protobuf client generation handler"""
    
    def validate_tools(self) -> List[str]:
        """Validate Kotlin protobuf tools are available"""
        missing_tools = []
        
        # Check for protoc
        if not BuildUtils.check_tool_available('protoc'):
            missing_tools.append('protoc')
        
        # Check for Java (required for Kotlin compilation)
        if not BuildUtils.check_tool_available('java'):
            missing_tools.append('java')
        
        # Note: protoc-gen-kotlin is typically provided by Gradle plugin
        # We'll check for Gradle instead
        if not BuildUtils.check_tool_available('gradle'):
            missing_tools.append('gradle')
        
        return missing_tools
    
    def prepare_output_directory(self, output_dir: Path) -> bool:
        """Prepare Kotlin output directory structure"""
        try:
            # Create standard Kotlin/Java package structure
            main_dir = output_dir / "src" / "main" / "kotlin" / "com" / "unhinged" / "proto"
            main_dir.mkdir(parents=True, exist_ok=True)
            
            # Create Gradle build file
            gradle_content = self._generate_build_gradle()
            gradle_file = output_dir / "build.gradle.kts"
            with open(gradle_file, 'w') as f:
                f.write(gradle_content)
            
            # Create settings.gradle.kts
            settings_content = self._generate_settings_gradle()
            settings_file = output_dir / "settings.gradle.kts"
            with open(settings_file, 'w') as f:
                f.write(settings_content)
            
            # Create gradle.properties
            properties_content = self._generate_gradle_properties()
            properties_file = output_dir / "gradle.properties"
            with open(properties_file, 'w') as f:
                f.write(properties_content)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to prepare Kotlin output directory: {e}")
            return False
    
    def build_protoc_command(self, proto_files: List[Path], output_dir: Path, proto_path: Path) -> List[str]:
        """Build protoc command for Kotlin generation"""
        kotlin_out = output_dir / "src" / "main" / "kotlin"
        java_out = output_dir / "src" / "main" / "java"
        
        # Create java output directory for compatibility
        java_out.mkdir(parents=True, exist_ok=True)
        
        # Use local grpc-java plugin
        grpc_java_plugin = self.context.project_root / "protoc-gen-grpc-java"

        cmd = [
            'protoc',
            f'--proto_path={proto_path}',
            f'--kotlin_out={kotlin_out}',
            f'--java_out={java_out}',
            f'--grpc-java_out={java_out}',
            f'--plugin=protoc-gen-grpc-java={grpc_java_plugin}'
        ]
        
        # Add proto files
        cmd.extend([str(pf) for pf in proto_files])
        
        return cmd
    
    def post_process_artifacts(self, output_dir: Path) -> List[BuildArtifact]:
        """Post-process Kotlin generated files"""
        artifacts = []
        
        try:
            # Collect Kotlin source files
            kotlin_src = output_dir / "src" / "main" / "kotlin"
            for kt_file in kotlin_src.rglob("*.kt"):
                artifacts.append(BuildUtils.create_build_artifact(
                    kt_file,
                    'kotlin-client',
                    {'language': 'kotlin', 'grpc': True}
                ))
            
            # Collect Java source files (for gRPC stubs)
            java_src = output_dir / "src" / "main" / "java"
            for java_file in java_src.rglob("*.java"):
                artifacts.append(BuildUtils.create_build_artifact(
                    java_file,
                    'java-grpc-stub',
                    {'language': 'kotlin', 'type': 'java-stub'}
                ))
            
            # Create artifacts for build files
            gradle_file = output_dir / "build.gradle.kts"
            if gradle_file.exists():
                artifacts.append(BuildUtils.create_build_artifact(
                    gradle_file,
                    'kotlin-gradle-build',
                    {'language': 'kotlin', 'type': 'gradle-build'}
                ))
            
            settings_file = output_dir / "settings.gradle.kts"
            if settings_file.exists():
                artifacts.append(BuildUtils.create_build_artifact(
                    settings_file,
                    'kotlin-gradle-settings',
                    {'language': 'kotlin', 'type': 'gradle-settings'}
                ))
            
            # Generate client registry for easy access
            self._generate_client_registry(output_dir)
            registry_file = output_dir / "src" / "main" / "kotlin" / "com" / "unhinged" / "proto" / "ClientRegistry.kt"
            if registry_file.exists():
                artifacts.append(BuildUtils.create_build_artifact(
                    registry_file,
                    'kotlin-client-registry',
                    {'language': 'kotlin', 'type': 'client-registry'}
                ))
            
            self.logger.info(f"Generated {len(artifacts)} Kotlin proto artifacts")
            
        except Exception as e:
            self.logger.error(f"Error post-processing Kotlin artifacts: {e}")
        
        return artifacts
    
    def _generate_build_gradle(self) -> str:
        """Generate build.gradle.kts for Kotlin proto clients"""
        return '''// Generated build.gradle.kts for Unhinged Proto Clients (Kotlin)

plugins {
    kotlin("jvm") version "1.9.20"
    id("com.google.protobuf") version "0.9.4"
    `maven-publish`
}

group = "com.unhinged"
version = "1.0.0"

repositories {
    mavenCentral()
}

dependencies {
    // Kotlin
    implementation("org.jetbrains.kotlin:kotlin-stdlib")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    
    // Protobuf and gRPC
    implementation("com.google.protobuf:protobuf-kotlin:3.24.4")
    implementation("io.grpc:grpc-kotlin-stub:1.4.0")
    implementation("io.grpc:grpc-netty-shaded:1.58.0")
    implementation("io.grpc:grpc-protobuf:1.58.0")
    
    // Testing
    testImplementation("org.jetbrains.kotlin:kotlin-test")
    testImplementation("io.grpc:grpc-testing:1.58.0")
}

protobuf {
    protoc {
        artifact = "com.google.protobuf:protoc:3.24.4"
    }
    plugins {
        id("grpc") {
            artifact = "io.grpc:protoc-gen-grpc-java:1.58.0"
        }
        id("grpckt") {
            artifact = "io.grpc:protoc-gen-grpc-kotlin:1.4.0:jdk8@jar"
        }
    }
    generateProtoTasks {
        all().forEach {
            it.plugins {
                id("grpc")
                id("grpckt")
            }
            it.builtins {
                id("kotlin")
            }
        }
    }
}

tasks.test {
    useJUnitPlatform()
}

kotlin {
    jvmToolchain(17)
}

publishing {
    publications {
        create<MavenPublication>("maven") {
            from(components["java"])
            
            pom {
                name.set("Unhinged Proto Clients (Kotlin)")
                description.set("Generated Kotlin protobuf clients for Unhinged platform")
                url.set("https://github.com/unhinged/proto-clients")
                
                licenses {
                    license {
                        name.set("MIT License")
                        url.set("https://opensource.org/licenses/MIT")
                    }
                }
                
                developers {
                    developer {
                        id.set("unhinged-team")
                        name.set("Unhinged Team")
                        email.set("team@unhinged.dev")
                    }
                }
            }
        }
    }
}
'''
    
    def _generate_settings_gradle(self) -> str:
        """Generate settings.gradle.kts"""
        return '''rootProject.name = "unhinged-proto-clients-kotlin"
'''
    
    def _generate_gradle_properties(self) -> str:
        """Generate gradle.properties"""
        return '''kotlin.code.style=official
org.gradle.jvmargs=-Xmx2g -XX:MaxMetaspaceSize=512m
org.gradle.parallel=true
org.gradle.caching=true
'''
    
    def _generate_client_registry(self, output_dir: Path):
        """Generate Kotlin client registry for easy access"""
        try:
            registry_content = '''// Generated Kotlin Proto Client Registry
// This file is auto-generated - do not edit manually

package com.unhinged.proto

import io.grpc.ManagedChannel
import io.grpc.ManagedChannelBuilder
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.asExecutor

/**
 * Registry for Unhinged proto clients
 * Provides easy access to all generated gRPC service clients
 */
object ClientRegistry {
    
    /**
     * Create a gRPC channel for the specified endpoint
     */
    fun createChannel(host: String, port: Int, useTls: Boolean = false): ManagedChannel {
        val builder = ManagedChannelBuilder.forAddress(host, port)
        
        if (!useTls) {
            builder.usePlaintext()
        }
        
        return builder
            .executor(Dispatchers.IO.asExecutor())
            .build()
    }
    
    /**
     * Create a gRPC channel with default settings for local development
     */
    fun createLocalChannel(port: Int): ManagedChannel {
        return createChannel("localhost", port, useTls = false)
    }
    
    // Service client factory methods will be added here during generation
    // based on the actual proto service definitions found
}
'''
            
            registry_file = output_dir / "src" / "main" / "kotlin" / "com" / "unhinged" / "proto" / "ClientRegistry.kt"
            registry_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(registry_file, 'w') as f:
                f.write(registry_content)
                
        except Exception as e:
            self.logger.error(f"Failed to generate Kotlin client registry: {e}")
