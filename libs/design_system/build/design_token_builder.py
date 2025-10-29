#!/usr/bin/env python3

"""
@llm-type config.build
@llm-does design token generation module following protoclientbuild...
@llm-rule design tokens must be generated before ui compilation and provide consistent ...
"""

import hashlib
import logging
import shutil
import time
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

# Import build system components
try:
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent.parent / "build" / "modules"))
    from __init__ import BuildModule, BuildContext, BuildModuleResult, BuildUtils, BuildArtifact
except ImportError:
    # Fallback for development/testing
    print("Warning: Build system modules not available, using fallback classes")
    class BuildModule:
        def __init__(self, context):
            self.context = context
    class BuildContext:
        def __init__(self):
            self.project_root = Path.cwd()
    class BuildModuleResult:
        def __init__(self, success, artifacts, build_time, message):
            self.success = success
            self.artifacts = artifacts
            self.build_time = build_time
            self.message = message
    class BuildUtils: pass
    class BuildArtifact:
        def __init__(self, path, type, platform, description):
            self.path = path
            self.type = type
            self.platform = platform
            self.description = description

# Import GTK4 generator
from generators.gtk4_generator import GTK4CSSGenerator


class DesignTokenBuilder(BuildModule):
    """
@llm-type config.build
@llm-does design token generation following protoclientbuilder arch...
"""

    def __init__(self, context: BuildContext):
        super().__init__(context)
        self.tokens_dir = context.project_root / "libs" / "design_system" / "tokens"
        self.output_base = context.project_root / "generated" / "design_system"
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Primary platform (following designer specifications)
        self.primary_platform = 'gtk4'
        self.supported_platforms = ['gtk4']  # Start with GTK4, expand later

        # Token files to process (designer's constraint system)
        self.token_files = [
            'colors.yaml',      # 16 semantic color roles
            'typography.yaml',  # 5 type sizes, 3 weights, 2 families
            'spacing.yaml',     # 10 spacing values, 4px base unit
            'elevation.yaml',   # 4 shadow depths, relative z-index
            'motion.yaml',      # Interaction states system
            'components.yaml'   # Component composition primitives
        ]

        # Initialize GTK4 generator
        self.gtk4_generator = GTK4CSSGenerator(
            self.tokens_dir,
            self.output_base / "gtk4"
        )
    
    def can_handle(self, target_name: str) -> bool:
        """Check if this module can handle design token generation targets"""
        design_targets = {
            'design-tokens', 'design-tokens-all', 'design-tokens-gtk4',
            'design-system', 'styling', 'tokens', 'css-tokens'
        }
        return target_name in design_targets or 'design-token' in target_name

    def get_dependencies(self, target_name: str) -> List[str]:
        """Get design token file dependencies for caching"""
        dependencies = []

        # All semantic token files (designer's constraint system)
        if self.tokens_dir.exists():
            for token_file in self.token_files:
                token_path = self.tokens_dir / token_file
                if token_path.exists():
                    dependencies.append(str(token_path))

        # Generator source files (for cache invalidation)
        generator_dir = Path(__file__).parent / "generators"
        if generator_dir.exists():
            for py_file in generator_dir.glob("*.py"):
                dependencies.append(str(py_file))

        return dependencies

    def validate_tokens(self) -> Tuple[bool, List[str]]:
        """Validate semantic tokens against designer constraints"""
        errors = []

        # Load tokens for validation
        self.gtk4_generator.load_tokens()
        tokens = self.gtk4_generator.tokens

        # Validate color system (16 semantic roles)
        if 'colors' in tokens:
            color_errors = self._validate_color_system(tokens['colors'])
            errors.extend(color_errors)

        # Validate typography system (5 type sizes)
        if 'typography' in tokens:
            typo_errors = self._validate_typography_system(tokens['typography'])
            errors.extend(typo_errors)

        # Validate spacing system (10 spacing values)
        if 'spacing' in tokens:
            spacing_errors = self._validate_spacing_system(tokens['spacing'])
            errors.extend(spacing_errors)

        return len(errors) == 0, errors

    def _validate_color_system(self, colors: Dict[str, Any]) -> List[str]:
        """Validate color system follows designer constraints"""
        errors = []

        required_categories = ['action', 'feedback', 'surface', 'text', 'border', 'interactive']
        if 'colors' in colors:
            color_system = colors['colors']
            for category in required_categories:
                if category not in color_system:
                    errors.append(f"Missing required color category: {category}")

        return errors

    def _validate_typography_system(self, typography: Dict[str, Any]) -> List[str]:
        """Validate typography system follows designer constraints"""
        errors = []

        if 'typography' in typography:
            typo_system = typography['typography']

            # Check for 5 type sizes
            if 'scale' in typo_system:
                required_sizes = ['display', 'heading', 'body', 'caption', 'code']
                scale = typo_system['scale']
                for size in required_sizes:
                    if size not in scale:
                        errors.append(f"Missing required type size: {size}")

            # Check for 2 font families maximum
            if 'families' in typo_system:
                families = typo_system['families']
                if len(families) > 2:
                    errors.append(f"Too many font families: {len(families)} (maximum 2 allowed)")

        return errors

    def _validate_spacing_system(self, spacing: Dict[str, Any]) -> List[str]:
        """Validate spacing system follows designer constraints"""
        errors = []

        if 'spacing' in spacing:
            spacing_system = spacing['spacing']

            # Check for 10 spacing values
            if 'scale' in spacing_system:
                scale = spacing_system['scale']
                if len(scale) != 10:
                    errors.append(f"Incorrect spacing scale size: {len(scale)} (expected 10)")

        return errors
    
    def build(self, target_name: str) -> BuildModuleResult:
        """Build design tokens for specified target following ProtoClientBuilder pattern"""
        start_time = time.time()

        try:
            # Validate semantic tokens against designer constraints
            is_valid, validation_errors = self.validate_tokens()
            if not is_valid:
                return BuildModuleResult(
                    success=False,
                    duration=time.time() - start_time,
                    artifacts=[],
                    error_message=f"Token validation failed: {'; '.join(validation_errors)}"
                )

            # Determine target platforms
            platforms = self._get_target_platforms(target_name)

            # Generate artifacts for each platform
            artifacts = []
            for platform in platforms:
                platform_artifacts = self._generate_platform_artifacts(platform)
                artifacts.extend(platform_artifacts)

            build_time = time.time() - start_time

            # Performance metrics
            total_css_size = sum(len(Path(artifact.path).read_text()) for artifact in artifacts)
            avg_generation_time = build_time / len(platforms) if platforms else 0

            return BuildModuleResult(
                success=True,
                duration=build_time,
                artifacts=artifacts,
                cache_hit=False,
                metrics={
                    "platforms": len(platforms),
                    "token_files": len(self.token_files),
                    "css_files_generated": len(artifacts),
                    "total_css_size_bytes": total_css_size,
                    "avg_generation_time_per_platform": avg_generation_time,
                    "tokens_per_second": len(self.token_files) / build_time if build_time > 0 else 0
                }
            )

        except Exception as e:
            return BuildModuleResult(
                success=False,
                duration=time.time() - start_time,
                artifacts=[],
                error_message=f"Design token generation failed: {e}"
            )
    
    def _get_target_platforms(self, target_name: str) -> List[str]:
        """Determine which platforms to generate for based on target"""
        if target_name in ['design-tokens-all', 'design-tokens', 'design-system']:
            return self.supported_platforms
        elif target_name == 'design-tokens-gtk4':
            return ['gtk4']
        else:
            # Default to primary platform
            return [self.primary_platform]

    def _generate_platform_artifacts(self, platform: str) -> List[BuildArtifact]:
        """Generate design token artifacts for a specific platform"""
        artifacts = []

        if platform == 'gtk4':
            artifacts.extend(self._generate_gtk4_css())
        # Future platform implementations can be added here

        return artifacts

    def _generate_gtk4_css(self) -> List[BuildArtifact]:
        """Generate GTK4 CSS artifacts using the GTK4CSSGenerator"""
        artifacts: List[BuildArtifact] = []

        try:
            # Ensure output directory exists
            output_dir = self.output_base / "gtk4"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Load tokens and generate CSS
            self.gtk4_generator.load_tokens()
            css_files = self.gtk4_generator.generate_css()

            if not css_files:
                self.logger.warning("No CSS files generated by GTK4CSSGenerator")
                return artifacts

            # Create artifacts for each generated CSS file
            for filename, css_content in css_files.items():
                output_path = output_dir / filename

                # Write CSS file
                with open(output_path, 'w') as f:
                    f.write(css_content)

                # Create build artifact with checksum
                with open(output_path, 'rb') as f:
                    checksum = hashlib.md5(f.read()).hexdigest()

                artifact = BuildArtifact(
                    path=output_path,
                    type="css",
                    size=len(css_content),
                    checksum=checksum,
                    metadata={
                        "platform": "gtk4",
                        "description": f"GTK4 {filename} - Generated from semantic design tokens",
                        "generator": "DesignTokenBuilder",
                        "semantic_tokens": True
                    }
                )
                artifacts.append(artifact)

        except Exception as e:
            self.logger.error(f"Failed to generate GTK4 CSS: {e}")
            raise

        return artifacts
    
    def calculate_cache_key(self, target_name: str) -> str:
        """Calculate cache key for build caching (BuildModule interface requirement)"""
        dependencies = self.get_dependencies(target_name)

        # Create hash from all dependency file modification times
        cache_data: List[str] = []

        for dep_path in dependencies:
            path = Path(dep_path)
            if path.exists():
                cache_data.append(f"{dep_path}:{path.stat().st_mtime}")

        cache_string = "|".join(sorted(cache_data))
        return hashlib.md5(cache_string.encode()).hexdigest()

    def clean(self, target_name: str) -> bool:
        """Clean build artifacts for the target (BuildModule interface requirement)"""
        try:
            # Determine platforms to clean
            platforms = self._get_target_platforms(target_name)

            for platform in platforms:
                platform_output_dir = self.output_base / platform
                if platform_output_dir.exists():
                    shutil.rmtree(platform_output_dir)
                    self.logger.info(f"Cleaned {platform} artifacts from {platform_output_dir}")

            return True
        except Exception as e:
            self.logger.error(f"Failed to clean artifacts: {e}")
            return False

    def is_cache_valid(self, target_name: str, cache_key: str) -> bool:
        """Check if cached artifacts are still valid"""
        current_key = self.calculate_cache_key(target_name)
        return current_key == cache_key

    def get_build_info(self) -> Dict[str, Any]:
        """Get build information for debugging and monitoring"""
        return {
            "module": "DesignTokenBuilder",
            "version": "1.0.0",
            "supported_platforms": self.supported_platforms,
            "primary_platform": self.primary_platform,
            "token_files": self.token_files,
            "tokens_dir": str(self.tokens_dir),
            "output_base": str(self.output_base),
            "designer_constraints": {
                "color_roles": 16,
                "type_sizes": 5,
                "font_families_max": 2,
                "spacing_values": 10,
                "shadow_depths": 4,
                "base_unit": "4px"
            }
        }


# Integration with build system
def create_design_token_builder(context: BuildContext) -> DesignTokenBuilder:
    """Factory function for build system integration"""
    return DesignTokenBuilder(context)


# CLI interface for testing and utilities
if __name__ == "__main__":
    import argparse
    import sys
    from pathlib import Path

    # Mock context for CLI usage
    class MockContext:
        def __init__(self):
            self.project_root = Path(__file__).parent.parent.parent.parent

    parser = argparse.ArgumentParser(description='Design Token Builder CLI')
    parser.add_argument('--validate', action='store_true',
                       help='Validate semantic tokens against designer constraints')
    parser.add_argument('--clean', action='store_true',
                       help='Clean generated design system artifacts')
    parser.add_argument('--build', choices=['design-tokens', 'design-tokens-gtk4'],
                       help='Build design tokens for specified target')
    parser.add_argument('--info', action='store_true',
                       help='Show build information and constraints')

    args = parser.parse_args()

    context = MockContext()
    builder = DesignTokenBuilder(context)

    if args.validate:
        print("🔍 Validating design tokens...")
        is_valid, errors = builder.validate_tokens()
        if is_valid:
            print("✅ Token validation PASSED")
            sys.exit(0)
        else:
            print("❌ Token validation FAILED:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)

    elif args.clean:
        print("🧹 Cleaning design system artifacts...")
        success = builder.clean('design-tokens')
        if success:
            print("✅ Design system artifacts cleaned")
            sys.exit(0)
        else:
            print("❌ Failed to clean artifacts")
            sys.exit(1)

    elif args.build:
        print(f"🔨 Building {args.build}...")
        result = builder.build(args.build)
        if result.success:
            print(f"✅ Build SUCCESS: {len(result.artifacts)} artifacts in {result.duration:.2f}s")
            if result.metrics:
                print(f"📊 Metrics: {result.metrics}")
            sys.exit(0)
        else:
            print(f"❌ Build FAILED: {result.error_message}")
            sys.exit(1)

    elif args.info:
        info = builder.get_build_info()
        print(f"📋 {info['module']} v{info['version']}")
        print(f"🎯 Primary platform: {info['primary_platform']}")
        print(f"🔧 Supported platforms: {', '.join(info['supported_platforms'])}")
        print(f"📁 Tokens directory: {info['tokens_dir']}")
        print(f"📁 Output directory: {info['output_base']}")
        print("🎨 Designer constraints:")
        for constraint, value in info['designer_constraints'].items():
            print(f"  - {constraint}: {value}")
        sys.exit(0)

    else:
        # Default: run validation and build test
        print("🧪 Design Token Builder Test")
        print(f"Can handle 'design-tokens': {builder.can_handle('design-tokens')}")
        print(f"Dependencies: {len(builder.get_dependencies('design-tokens'))} files")

        # Validate tokens
        is_valid, errors = builder.validate_tokens()
        print(f"Token validation: {'PASS' if is_valid else 'FAIL'}")
        if errors:
            for error in errors:
                print(f"  - {error}")

        # Test build
        result = builder.build('design-tokens-gtk4')
        print(f"Build result: {'SUCCESS' if result.success else 'FAILED'}")
        print(f"Duration: {result.duration:.2f}s")
        print(f"Artifacts: {len(result.artifacts)}")
        if result.error_message:
            print(f"Error: {result.error_message}")
        if result.metrics:
            print(f"Metrics: {result.metrics}")

        # Show build info
        info = builder.get_build_info()
        print(f"Build info: {info['module']} v{info['version']}")
        print(f"Designer constraints: {info['designer_constraints']}")
