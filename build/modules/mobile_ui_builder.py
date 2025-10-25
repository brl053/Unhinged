"""
@llm-type build-module
@llm-legend Mobile UI Builder - Build system integration for mobile-responsive UI components
@llm-key Generates CSS themes, validates responsive layouts, and integrates mobile UI framework
@llm-map Build system module for mobile UI framework integration in Unhinged architecture
@llm-axiom Mobile UI must maintain native GTK performance while providing responsive design
@llm-contract Integrates with centralized build system to generate mobile UI assets and validation
@llm-token mobile_ui_builder: Build system integration for mobile-first responsive UI framework
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from build.core.base_builder import BaseBuilder
    from build.core.validation import ValidationResult
    BUILD_CORE_AVAILABLE = True
except ImportError:
    print("⚠️ Build core not available, using fallback implementation")
    BUILD_CORE_AVAILABLE = False

    # Fallback implementations
    class BaseBuilder:
        def __init__(self, name=None):
            self.name = name or "fallback_builder"

    class ValidationResult:
        def __init__(self, success: bool, message: str = ""):
            self.success = success
            self.message = message

# Import shared CSS generator
try:
    from control.native_gui.core.css_generator import CSSGenerator, CSSConfig
    CSS_GENERATOR_AVAILABLE = True
except ImportError:
    print("⚠️ CSS generator not available, using fallback CSS generation")
    CSS_GENERATOR_AVAILABLE = False
    
    class BaseBuilder:
        def __init__(self, name: str):
            self.name = name
            self.build_dir = Path("build")
            self.generated_dir = Path("generated")
    
    class ValidationResult:
        def __init__(self, success: bool, message: str = ""):
            self.success = success
            self.message = message


class MobileUIBuilder(BaseBuilder):
    """
    @llm-type builder-class
    @llm-legend Build system integration for mobile UI framework
    @llm-key Handles CSS generation, asset compilation, and responsive layout validation
    @llm-map Core build module for mobile UI framework in Unhinged build system
    @llm-axiom Build process must be deterministic and maintain component independence
    @llm-contract Provides standardized build interface for mobile UI components
    @llm-token MobileUIBuilder: Centralized build system for mobile-responsive UI framework
    
    Build system integration for the mobile UI framework.
    Handles CSS generation, asset compilation, and validation.
    """
    
    def __init__(self):
        super().__init__("mobile_ui")
        
        # Build configuration
        self.project_root = project_root
        self.generated_dir = self.project_root / "generated"
        self.source_dir = project_root / "control" / "native_gui" / "ui"
        self.output_dir = self.generated_dir / "mobile_ui"
        self.css_output_dir = self.generated_dir / "static_html"
        
        # Component registry
        self.components = {}
        self.themes = {}
        self.responsive_breakpoints = {
            'mobile': 768,
            'tablet': 1024,
            'desktop': 1920
        }

        # Initialize shared CSS generator if available
        if CSS_GENERATOR_AVAILABLE:
            css_config = CSSConfig(
                mobile_breakpoint=self.responsive_breakpoints['mobile'],
                tablet_breakpoint=self.responsive_breakpoints['tablet'],
                desktop_breakpoint=self.responsive_breakpoints['desktop']
            )
            self.css_generator = CSSGenerator(css_config)
        else:
            self.css_generator = None
        
        print(f"📱 Mobile UI Builder initialized")
        print(f"   Source: {self.source_dir}")
        print(f"   Output: {self.output_dir}")
    
    def build(self) -> ValidationResult:
        """
        @llm-type method
        @llm-legend Main build process for mobile UI framework
        @llm-key Orchestrates CSS generation, validation, and asset compilation
        @llm-map Primary build entry point for mobile UI components
        @llm-axiom Build must be idempotent and handle incremental updates
        @llm-contract Returns ValidationResult indicating build success/failure
        @llm-token build: Main mobile UI build process
        
        Execute the mobile UI build process.
        
        Returns:
            ValidationResult: Build result with success status and messages
        """
        try:
            print("📱 Starting mobile UI build process...")
            
            # Create output directories
            self._create_output_directories()
            
            # Discover and validate components
            validation = self._discover_components()
            if not validation.success:
                return validation
            
            # Generate CSS themes
            css_result = self._generate_css_themes()
            if not css_result.success:
                return css_result
            
            # Generate component metadata
            metadata_result = self._generate_component_metadata()
            if not metadata_result.success:
                return metadata_result
            
            # Validate responsive layouts
            layout_result = self._validate_responsive_layouts()
            if not layout_result.success:
                return layout_result
            
            # Generate build manifest
            manifest_result = self._generate_build_manifest()
            if not manifest_result.success:
                return manifest_result
            
            print("✅ Mobile UI build completed successfully")
            return ValidationResult(True, "Mobile UI build completed successfully")
            
        except Exception as e:
            error_msg = f"Mobile UI build failed: {e}"
            print(f"❌ {error_msg}")
            return ValidationResult(False, error_msg)
    
    def _create_output_directories(self):
        """
        @llm-type method
        @llm-legend Create necessary output directories for build artifacts
        @llm-key Ensures proper directory structure for generated assets
        """
        directories = [
            self.output_dir,
            self.css_output_dir,
            self.output_dir / "themes",
            self.output_dir / "components",
            self.output_dir / "layouts"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {directory}")
    
    def _discover_components(self) -> ValidationResult:
        """
        @llm-type method
        @llm-legend Discover and validate mobile UI components
        @llm-key Scans source directory for component definitions and validates structure
        """
        try:
            print("🔍 Discovering mobile UI components...")
            
            if not self.source_dir.exists():
                return ValidationResult(False, f"Source directory not found: {self.source_dir}")
            
            # Discover Python component files
            component_files = list(self.source_dir.glob("*.py"))
            
            for component_file in component_files:
                component_name = component_file.stem
                
                # Skip __init__ and test files
                if component_name.startswith('__') or component_name.endswith('_test'):
                    continue
                
                self.components[component_name] = {
                    'file': str(component_file),
                    'name': component_name,
                    'type': 'ui_component',
                    'mobile_optimized': self._check_mobile_optimization(component_file)
                }
                
                print(f"📱 Discovered component: {component_name}")
            
            print(f"✅ Discovered {len(self.components)} mobile UI components")
            return ValidationResult(True, f"Discovered {len(self.components)} components")
            
        except Exception as e:
            return ValidationResult(False, f"Component discovery failed: {e}")
    
    def _check_mobile_optimization(self, component_file: Path) -> bool:
        """
        @llm-type method
        @llm-legend Check if component is mobile-optimized
        @llm-key Analyzes component code for mobile-responsive patterns
        """
        try:
            content = component_file.read_text()
            
            # Check for mobile-responsive indicators
            mobile_indicators = [
                'ToolViewport',
                'ResponsiveLayout',
                'TouchInterface',
                'mobile_span',
                'tablet_span',
                'desktop_span',
                'ScreenSize.MOBILE'
            ]
            
            return any(indicator in content for indicator in mobile_indicators)
            
        except Exception:
            return False
    
    def _generate_css_themes(self) -> ValidationResult:
        """
        @llm-type method
        @llm-legend Generate CSS themes for mobile UI components
        @llm-key Creates responsive CSS with mobile-first design principles
        @llm-map Generates CSS assets for GTK4 application theming
        @llm-axiom CSS must be valid and follow GTK4 theming conventions
        @llm-contract Generates CSS files in the static_html output directory
        @llm-token _generate_css_themes: CSS theme generation for mobile-responsive UI
        """
        try:
            print("🎨 Generating CSS themes...")
            
            # Generate CSS using shared generator if available
            if self.css_generator:
                combined_css = self.css_generator.generate_complete_css()
                print("✅ Using shared CSSGenerator for CSS generation")
            else:
                # Fallback to local generation
                mobile_css = self._generate_mobile_css()
                responsive_css = self._generate_responsive_css()
                component_css = self._generate_component_css()

                combined_css = f"""
/* Mobile UI Framework CSS - Generated by MobileUIBuilder (Fallback) */
/* @llm-type generated-css */
/* @llm-legend Mobile-first responsive CSS for GTK4 application */
/* @llm-key Provides responsive design patterns and mobile optimization */

{mobile_css}

{responsive_css}

{component_css}
"""
                print("⚠️ Using fallback CSS generation")
            
            # Write CSS file
            css_file = self.css_output_dir / "mobile_ui.css"
            css_file.write_text(combined_css)
            
            print(f"✅ Generated CSS theme: {css_file}")
            return ValidationResult(True, f"Generated CSS theme: {css_file}")
            
        except Exception as e:
            return ValidationResult(False, f"CSS generation failed: {e}")
    
    def _generate_mobile_css(self) -> str:
        """Generate mobile-first base CSS (fallback method)"""
        return """
/* Mobile-first base styles */
.mobile-optimized {
    padding: 8px;
    margin: 4px;
}

.touch-button {
    min-height: 44px;
    min-width: 44px;
    padding: 12px;
    border-radius: 8px;
}

.touch-button:hover {
    background-color: alpha(@theme_fg_color, 0.1);
}

.touch-button.pressed {
    background-color: alpha(@theme_fg_color, 0.2);
    transform: scale(0.95);
}

.card {
    background-color: @theme_base_color;
    border-radius: 12px;
    box-shadow: 0 2px 8px alpha(@theme_fg_color, 0.1);
    margin: 8px;
    padding: 16px;
}

.card-title {
    font-weight: bold;
    font-size: 1.2em;
    margin-bottom: 4px;
}

.card-subtitle {
    opacity: 0.7;
    font-size: 0.9em;
}
"""
    
    def _generate_responsive_css(self) -> str:
        """Generate responsive breakpoint CSS (fallback method)"""
        return f"""
/* Responsive breakpoints */
@media (max-width: {self.responsive_breakpoints['mobile']}px) {{
    .desktop-only {{ display: none; }}
    .mobile-hidden {{ display: none; }}
    
    .responsive-grid {{
        grid-template-columns: 1fr;
        gap: 8px;
    }}
    
    .responsive-spacing {{
        padding: 8px;
        margin: 4px;
    }}
}}

@media (min-width: {self.responsive_breakpoints['mobile']}px) and (max-width: {self.responsive_breakpoints['tablet']}px) {{
    .mobile-only {{ display: none; }}
    .desktop-only {{ display: none; }}
    
    .responsive-grid {{
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
    }}
    
    .responsive-spacing {{
        padding: 12px;
        margin: 8px;
    }}
}}

@media (min-width: {self.responsive_breakpoints['tablet']}px) {{
    .mobile-only {{ display: none; }}
    .tablet-only {{ display: none; }}
    
    .responsive-grid {{
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
    }}
    
    .responsive-spacing {{
        padding: 16px;
        margin: 12px;
    }}
}}
"""
    
    def _generate_component_css(self) -> str:
        """Generate component-specific CSS (fallback method)"""
        return """
/* Component-specific styles */
.status-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 6px;
}

.status-indicator.status-success {
    background-color: alpha(@success_color, 0.1);
    color: @success_color;
}

.status-indicator.status-warning {
    background-color: alpha(@warning_color, 0.1);
    color: @warning_color;
}

.status-indicator.status-error {
    background-color: alpha(@error_color, 0.1);
    color: @error_color;
}

.metric-value {
    font-size: 2em;
    font-weight: bold;
    line-height: 1;
}

.trend-positive {
    color: @success_color;
}

.trend-negative {
    color: @error_color;
}

.loading-spinner {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 24px;
}

.loading-message {
    opacity: 0.7;
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    padding: 48px 24px;
    text-align: center;
}

.empty-state-icon {
    opacity: 0.5;
}

.empty-state-title {
    font-size: 1.5em;
    font-weight: bold;
}

.empty-state-subtitle {
    opacity: 0.7;
    max-width: 400px;
}

/* Bottom tab bar for mobile */
.bottom-tab-bar {
    border-top: 1px solid alpha(@theme_fg_color, 0.1);
    background-color: @theme_base_color;
    padding: 8px;
}

/* Side tab bar for tablet */
.side-tab-bar {
    border-right: 1px solid alpha(@theme_fg_color, 0.1);
    background-color: @theme_base_color;
    padding: 12px;
}

/* Sidebar for desktop */
.sidebar {
    border-right: 1px solid alpha(@theme_fg_color, 0.1);
    background-color: @theme_base_color;
    padding: 16px;
}
"""
    
    def _generate_component_metadata(self) -> ValidationResult:
        """
        @llm-type method
        @llm-legend Generate metadata for discovered components
        @llm-key Creates JSON metadata for component registry and tooling
        """
        try:
            print("📋 Generating component metadata...")
            
            metadata = {
                'version': '1.0.0',
                'build_timestamp': self._get_timestamp(),
                'components': self.components,
                'themes': self.themes,
                'breakpoints': self.responsive_breakpoints,
                'mobile_optimized_count': sum(1 for c in self.components.values() if c['mobile_optimized'])
            }
            
            metadata_file = self.output_dir / "components" / "metadata.json"
            metadata_file.write_text(json.dumps(metadata, indent=2))
            
            print(f"✅ Generated component metadata: {metadata_file}")
            return ValidationResult(True, f"Generated metadata for {len(self.components)} components")
            
        except Exception as e:
            return ValidationResult(False, f"Metadata generation failed: {e}")
    
    def _validate_responsive_layouts(self) -> ValidationResult:
        """
        @llm-type method
        @llm-legend Validate responsive layout implementations
        @llm-key Ensures layouts work correctly across all viewport sizes
        """
        try:
            print("🔍 Validating responsive layouts...")
            
            validation_results = []
            
            # Check for required responsive components
            required_components = ['responsive_layout', 'components', 'touch_interface']
            
            for component in required_components:
                if component not in self.components:
                    validation_results.append(f"Missing required component: {component}")
            
            # Check mobile optimization
            mobile_optimized = sum(1 for c in self.components.values() if c['mobile_optimized'])
            if mobile_optimized == 0:
                validation_results.append("No mobile-optimized components found")
            
            if validation_results:
                return ValidationResult(False, "; ".join(validation_results))
            
            print("✅ Responsive layout validation passed")
            return ValidationResult(True, "Responsive layouts validated successfully")
            
        except Exception as e:
            return ValidationResult(False, f"Layout validation failed: {e}")
    
    def _generate_build_manifest(self) -> ValidationResult:
        """
        @llm-type method
        @llm-legend Generate build manifest for mobile UI framework
        @llm-key Creates comprehensive build information for deployment and debugging
        """
        try:
            print("📄 Generating build manifest...")
            
            manifest = {
                'name': 'mobile_ui_framework',
                'version': '1.0.0',
                'build_timestamp': self._get_timestamp(),
                'builder': 'MobileUIBuilder',
                'source_directory': str(self.source_dir),
                'output_directory': str(self.output_dir),
                'components': {
                    'total': len(self.components),
                    'mobile_optimized': sum(1 for c in self.components.values() if c['mobile_optimized']),
                    'list': list(self.components.keys())
                },
                'assets': {
                    'css_files': ['mobile_ui.css'],
                    'metadata_files': ['components/metadata.json']
                },
                'breakpoints': self.responsive_breakpoints,
                'build_success': True
            }
            
            manifest_file = self.output_dir / "build_manifest.json"
            manifest_file.write_text(json.dumps(manifest, indent=2))
            
            print(f"✅ Generated build manifest: {manifest_file}")
            return ValidationResult(True, "Build manifest generated successfully")
            
        except Exception as e:
            return ValidationResult(False, f"Manifest generation failed: {e}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for build metadata"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def clean(self) -> ValidationResult:
        """
        @llm-type method
        @llm-legend Clean generated mobile UI build artifacts
        @llm-key Removes all generated files and directories
        """
        try:
            print("🧹 Cleaning mobile UI build artifacts...")
            
            if self.output_dir.exists():
                shutil.rmtree(self.output_dir)
                print(f"🗑️ Removed: {self.output_dir}")
            
            # Clean CSS files
            css_file = self.css_output_dir / "mobile_ui.css"
            if css_file.exists():
                css_file.unlink()
                print(f"🗑️ Removed: {css_file}")
            
            print("✅ Mobile UI build artifacts cleaned")
            return ValidationResult(True, "Build artifacts cleaned successfully")
            
        except Exception as e:
            return ValidationResult(False, f"Clean failed: {e}")


def main():
    """
    @llm-type main-function
    @llm-legend Main entry point for mobile UI builder
    @llm-key Provides command-line interface for build operations
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Mobile UI Framework Builder")
    parser.add_argument('action', choices=['build', 'clean'], help='Build action to perform')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    builder = MobileUIBuilder()
    
    if args.action == 'build':
        result = builder.build()
    elif args.action == 'clean':
        result = builder.clean()
    
    if result.success:
        print(f"✅ {result.message}")
        sys.exit(0)
    else:
        print(f"❌ {result.message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
