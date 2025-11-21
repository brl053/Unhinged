#!/usr/bin/env python3

"""
@llm-type config.build
@llm-does proto-to-polyglot client library generation module using ...
@llm-rule client libraries must be generated before service compilation and provide typ...
"""

import time
from pathlib import Path

try:
    from . import BuildArtifact, BuildContext, BuildModule, BuildModuleResult, BuildUtils
    from .c_proto_handler import CProtoHandler
    from .kotlin_proto_handler import KotlinProtoHandler
    from .polyglot_proto_engine import PolyglotProtoEngine
    from .python_proto_handler import PythonProtoHandler
    from .typescript_proto_handler import TypeScriptProtoHandler
except ImportError:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))
    from __init__ import BuildArtifact, BuildContext, BuildModule, BuildModuleResult, BuildUtils
    from c_proto_handler import CProtoHandler
    from kotlin_proto_handler import KotlinProtoHandler
    from polyglot_proto_engine import PolyglotProtoEngine
    from python_proto_handler import PythonProtoHandler
    from typescript_proto_handler import TypeScriptProtoHandler


class ProtoClientBuilder(BuildModule):
    """
    @llm-type config.build
    @llm-does polyglot protobuf client generation using unified dry
    """

    def __init__(self, context: BuildContext):
        super().__init__(context)
        self.proto_dir = context.project_root / "proto"
        self.output_base = context.project_root / "generated"

        # Initialize polyglot engine
        self.engine = PolyglotProtoEngine(context)

        # Register language handlers
        self._register_language_handlers()

        # Supported languages
        self.supported_languages = ["typescript", "c", "python", "kotlin"]

    def _register_language_handlers(self):
        """Register all language-specific handlers with the engine"""
        # TypeScript handler
        ts_config = self.engine.language_configs["typescript"]
        ts_handler = TypeScriptProtoHandler(ts_config, self.context)
        self.engine.register_handler("typescript", ts_handler)

        # C/C++ handler
        c_config = self.engine.language_configs["c"]
        c_handler = CProtoHandler(c_config, self.context)
        self.engine.register_handler("c", c_handler)

        # Python handler
        python_config = self.engine.language_configs["python"]
        python_handler = PythonProtoHandler(python_config, self.context)
        self.engine.register_handler("python", python_handler)

        # Kotlin handler
        kotlin_config = self.engine.language_configs["kotlin"]
        kotlin_handler = KotlinProtoHandler(kotlin_config, self.context)
        self.engine.register_handler("kotlin", kotlin_handler)

    def can_handle(self, target_name: str) -> bool:
        """Check if this module can handle proto client generation targets"""
        proto_targets = {
            "proto-clients",
            "proto-clients-all",
            "proto-clients-typescript",
            "proto-clients-c",
            "proto-clients-python",
            "proto-clients-kotlin",
            "grpc-clients",
            "client-libraries",
            "api-clients",
        }
        return target_name in proto_targets or "proto-client" in target_name

    def get_dependencies(self, target_name: str) -> list[str]:
        """Get proto file dependencies"""
        dependencies = []

        # All proto files
        if self.proto_dir.exists():
            for proto_file in self.proto_dir.rglob("*.proto"):
                dependencies.append(str(proto_file))

        # Build configuration affects generation
        build_config = self.context.project_root / "build" / "config" / "build-config.yml"
        if build_config.exists():
            dependencies.append(str(build_config))

        # Language-specific configuration files
        config_files = [
            "package.json",  # TypeScript/JavaScript
            "requirements.txt",  # Python
            "build.gradle.kts",  # Kotlin
            "CMakeLists.txt",  # C/C++
        ]

        for config_file in config_files:
            config_path = self.context.project_root / config_file
            if config_path.exists():
                dependencies.append(str(config_path))

        return dependencies

    def calculate_cache_key(self, target_name: str) -> str:
        """Calculate cache key using polyglot engine"""
        languages = self._get_target_languages(target_name)
        return self.engine.calculate_cache_key(languages)

    def build(self, target_name: str) -> BuildModuleResult:
        """Build proto clients using polyglot engine"""
        start_time = time.time()

        try:
            # Determine target languages
            languages = self._get_target_languages(target_name)

            if not languages:
                return BuildModuleResult(
                    success=False,
                    artifacts=[],
                    warnings=[f"No languages specified for target: {target_name}"],
                    duration=time.time() - start_time,
                    cache_hit=False,
                )

            self.logger.info(f"Generating proto clients for: {', '.join(languages)}")

            # Validate environment
            validation_results = self.engine.validate_environment()
            warnings = []

            for language in languages:
                missing_tools = validation_results.get(language, [])
                if missing_tools:
                    warning = f"Missing tools for {language}: {', '.join(missing_tools)}"
                    warnings.append(warning)
                    self.logger.warning(warning)

            # Generate clients using polyglot engine
            artifacts, generation_warnings = self.engine.generate_clients(languages)
            warnings.extend(generation_warnings)

            # Generate client registry for browser consumption if TypeScript is included
            if "typescript" in languages:
                registry_artifact = self._generate_client_registry()
                if registry_artifact:
                    artifacts.append(registry_artifact)

            duration = time.time() - start_time
            success = len(artifacts) > 0

            if success:
                self.logger.info(f"✅ Generated {len(artifacts)} proto client artifacts in {duration:.2f}s")
            else:
                self.logger.error("❌ Proto client generation failed")

            return BuildModuleResult(
                success=success,
                artifacts=artifacts,
                warnings=warnings,
                duration=duration,
                cache_hit=False,
                metrics={
                    "languages": languages,
                    "proto_files_count": len(self.engine.get_proto_files()),
                    "artifacts_by_language": {
                        lang: len([a for a in artifacts if a.metadata.get("language") == lang]) for lang in languages
                    },
                },
            )

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Proto client generation failed: {str(e)}"
            self.logger.error(error_msg)

            return BuildModuleResult(
                success=False, artifacts=[], warnings=[error_msg], duration=duration, cache_hit=False
            )

    def _get_target_languages(self, target_name: str) -> list[str]:
        """Determine which languages to generate based on target name"""
        if target_name == "proto-clients-all":
            return self.supported_languages
        elif target_name.startswith("proto-clients-"):
            lang = target_name.replace("proto-clients-", "")
            return [lang] if lang in self.supported_languages else []
        else:
            # Default: generate TypeScript for browser consumption
            return ["typescript"]

    def _generate_client_registry(self) -> BuildArtifact | None:
        """Generate client registry for browser consumption"""
        try:
            registry_content = self._create_client_registry_content()

            # Write to generated directory following Artifactory pattern
            registry_path = self.context.project_root / "generated" / "static_html" / "api-clients.js"
            registry_path.parent.mkdir(parents=True, exist_ok=True)

            with open(registry_path, "w") as f:
                f.write(registry_content)

            return BuildUtils.create_build_artifact(
                registry_path,
                "client-registry",
                {"language": "javascript", "type": "browser-registry", "generated_at": time.time()},
            )

        except Exception as e:
            self.logger.error(f"Failed to generate client registry: {e}")
            return None

    def clean(self, target_name: str) -> bool:
        """Clean generated proto client artifacts"""
        try:
            languages = self._get_target_languages(target_name)

            # Clean language-specific output directories
            cleaned = False
            for language in languages:
                output_dir = self.output_base / language / "clients"
                if output_dir.exists():
                    import shutil

                    shutil.rmtree(output_dir)
                    self.logger.info(f"Cleaned {language} proto clients: {output_dir}")
                    cleaned = True

            # Clean client registry if it exists
            registry_path = self.context.project_root / "generated" / "static_html" / "api-clients.js"
            if registry_path.exists():
                registry_path.unlink()
                self.logger.info(f"Cleaned client registry: {registry_path}")
                cleaned = True

            return cleaned

        except Exception as e:
            self.logger.error(f"Failed to clean proto client artifacts: {e}")
            return False

    def _create_client_registry_content(self) -> str:
        """Create JavaScript content for client registry"""
        return (
            """/**
 * Unhinged Proto Client Registry
 * Auto-generated client registry for browser consumption
 * Generated at: """
            + str(time.time())
            + """
 */

class UnhingedProtoClientRegistry {
    constructor() {
        this.clients = new Map();
        this.serviceEndpoints = {
            'persistence': 'http://localhost:8090',
            'audio': 'http://localhost:8000',
            'vision': 'http://localhost:8001',
            'context': 'http://localhost:8002'
        };
    }

    /**
     * Get or create a service client
     */
    getClient(serviceName, options = {}) {
        if (this.clients.has(serviceName)) {
            return this.clients.get(serviceName);
        }

        const client = this._createServiceClient(serviceName, options);
        this.clients.set(serviceName, client);
        return client;
    }

    /**
     * Create service client instance
     */
    _createServiceClient(serviceName, options) {
        const endpoint = options.endpoint || this.serviceEndpoints[serviceName];

        return {
            serviceName,
            endpoint,

            async call(method, request) {
                const response = await fetch(`${endpoint}/${method}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(request)
                });

                return await response.json();
            }
        };
    }
}

// Global registry instance
window.UnhingedClients = new UnhingedProtoClientRegistry();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UnhingedProtoClientRegistry;
}
"""
        )
