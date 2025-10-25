#!/usr/bin/env python3
"""
@llm-type validation-script
@llm-legend Comprehensive validation script for mobile UI framework integration
@llm-key Validates complete mobile UI framework integration with Unhinged architecture
@llm-map Validation script for mobile UI framework in Unhinged build system
@llm-axiom Validation must be thorough, reliable, and provide actionable feedback
@llm-contract Provides comprehensive validation of mobile UI framework integration
@llm-token mobile_ui_validation: Complete integration validation for mobile-responsive UI framework
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import importlib.util
from dataclasses import dataclass
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class ValidationLevel(Enum):
    """
    @llm-type enum
    @llm-legend Validation severity levels
    @llm-key Defines validation result severity for proper reporting
    """
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """
    @llm-type result-class
    @llm-legend Validation result with detailed information
    @llm-key Contains validation outcome and actionable feedback
    """
    component: str
    test_name: str
    level: ValidationLevel
    message: str
    details: Optional[str] = None
    fix_suggestion: Optional[str] = None


class MobileUIIntegrationValidator:
    """
    @llm-type validator-class
    @llm-legend Comprehensive validator for mobile UI framework integration
    @llm-key Validates all aspects of mobile UI framework integration with Unhinged
    @llm-map Central validation system for mobile UI framework integration
    @llm-axiom Validation must be comprehensive and provide actionable feedback
    @llm-contract Validates mobile UI framework integration across all components
    @llm-token MobileUIIntegrationValidator: Complete integration validation system
    
    Comprehensive validator for mobile UI framework integration.
    Validates build system, components, tools, themes, and documentation.
    """
    
    def __init__(self):
        self.project_root = project_root
        self.results: List[ValidationResult] = []
        
        # Validation configuration
        self.required_directories = [
            "control/native_gui/ui",
            "control/native_gui/tools/input_capture",
            "build/modules",
            "generated",
            "docs"
        ]
        
        self.required_files = [
            "control/native_gui/ui/responsive_layout.py",
            "control/native_gui/ui/touch_interface.py",
            "control/native_gui/ui/components.py",
            "control/native_gui/ui/input_integration.py",
            "control/native_gui/tools/input_capture/tool.py",
            "control/native_gui/tools/input_capture/__init__.py",
            "build/modules/mobile_ui_builder.py",
            "control/native_gui/tests/test_mobile_ui_integration.py",
            "docs/mobile_ui_framework.md",
            "control/native_gui/README_MOBILE_UI.md"
        ]
        
        print("🔍 Mobile UI Integration Validator initialized")
    
    def validate_all(self) -> bool:
        """
        @llm-type method
        @llm-legend Run complete validation suite
        @llm-key Executes all validation checks and returns overall success status
        """
        print("🚀 Starting comprehensive mobile UI integration validation...")
        print("=" * 70)
        
        # Run all validation checks
        self._validate_directory_structure()
        self._validate_file_existence()
        self._validate_python_imports()
        self._validate_build_system()
        self._validate_component_library()
        self._validate_tool_integration()
        self._validate_theme_system()
        self._validate_documentation()
        self._validate_tests()
        self._validate_generated_assets()
        
        # Generate report
        return self._generate_validation_report()
    
    def _validate_directory_structure(self):
        """
        @llm-type method
        @llm-legend Validate required directory structure exists
        @llm-key Ensures all necessary directories are present
        """
        print("📁 Validating directory structure...")
        
        for directory in self.required_directories:
            dir_path = self.project_root / directory
            
            if dir_path.exists() and dir_path.is_dir():
                self._add_result(ValidationResult(
                    component="Directory Structure",
                    test_name=f"Directory {directory}",
                    level=ValidationLevel.SUCCESS,
                    message=f"Directory exists: {directory}"
                ))
            else:
                self._add_result(ValidationResult(
                    component="Directory Structure",
                    test_name=f"Directory {directory}",
                    level=ValidationLevel.ERROR,
                    message=f"Missing required directory: {directory}",
                    fix_suggestion=f"Create directory: mkdir -p {directory}"
                ))
    
    def _validate_file_existence(self):
        """
        @llm-type method
        @llm-legend Validate required files exist
        @llm-key Ensures all necessary files are present
        """
        print("📄 Validating file existence...")
        
        for file_path in self.required_files:
            full_path = self.project_root / file_path
            
            if full_path.exists() and full_path.is_file():
                self._add_result(ValidationResult(
                    component="File Structure",
                    test_name=f"File {file_path}",
                    level=ValidationLevel.SUCCESS,
                    message=f"File exists: {file_path}"
                ))
            else:
                self._add_result(ValidationResult(
                    component="File Structure",
                    test_name=f"File {file_path}",
                    level=ValidationLevel.ERROR,
                    message=f"Missing required file: {file_path}",
                    fix_suggestion=f"Create or restore file: {file_path}"
                ))
    
    def _validate_python_imports(self):
        """
        @llm-type method
        @llm-legend Validate Python module imports work correctly
        @llm-key Ensures all mobile UI modules can be imported without errors
        """
        print("🐍 Validating Python imports...")
        
        import_tests = [
            ("control.native_gui.ui.responsive_layout", "ResponsiveLayout"),
            ("control.native_gui.ui.touch_interface", "TouchGestureRecognizer"),
            ("control.native_gui.ui.components", "Card"),
            ("control.native_gui.ui.input_integration", "InputMonitorWidget"),
            ("control.native_gui.core.tool_manager", "ToolViewport"),
            ("control.native_gui.core.theme_manager", "ThemeManager"),
            ("build.modules.mobile_ui_builder", "MobileUIBuilder")
        ]
        
        for module_name, class_name in import_tests:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, class_name):
                    self._add_result(ValidationResult(
                        component="Python Imports",
                        test_name=f"Import {module_name}.{class_name}",
                        level=ValidationLevel.SUCCESS,
                        message=f"Successfully imported {class_name} from {module_name}"
                    ))
                else:
                    self._add_result(ValidationResult(
                        component="Python Imports",
                        test_name=f"Import {module_name}.{class_name}",
                        level=ValidationLevel.ERROR,
                        message=f"Class {class_name} not found in {module_name}",
                        fix_suggestion=f"Check class definition in {module_name}"
                    ))
            except ImportError as e:
                self._add_result(ValidationResult(
                    component="Python Imports",
                    test_name=f"Import {module_name}",
                    level=ValidationLevel.ERROR,
                    message=f"Failed to import {module_name}: {e}",
                    fix_suggestion=f"Check module path and dependencies for {module_name}"
                ))
    
    def _validate_build_system(self):
        """
        @llm-type method
        @llm-legend Validate build system integration
        @llm-key Ensures mobile UI builder integrates correctly with build system
        """
        print("🔨 Validating build system integration...")
        
        try:
            # Test mobile UI builder
            from build.modules.mobile_ui_builder import MobileUIBuilder
            builder = MobileUIBuilder()
            
            self._add_result(ValidationResult(
                component="Build System",
                test_name="Mobile UI Builder Creation",
                level=ValidationLevel.SUCCESS,
                message="Mobile UI builder can be instantiated"
            ))
            
            # Test builder methods
            required_methods = ['build', 'clean', '_generate_css_themes', '_discover_components']
            for method in required_methods:
                if hasattr(builder, method):
                    self._add_result(ValidationResult(
                        component="Build System",
                        test_name=f"Builder Method {method}",
                        level=ValidationLevel.SUCCESS,
                        message=f"Builder has required method: {method}"
                    ))
                else:
                    self._add_result(ValidationResult(
                        component="Build System",
                        test_name=f"Builder Method {method}",
                        level=ValidationLevel.ERROR,
                        message=f"Builder missing required method: {method}",
                        fix_suggestion=f"Implement {method} in MobileUIBuilder"
                    ))
            
        except Exception as e:
            self._add_result(ValidationResult(
                component="Build System",
                test_name="Mobile UI Builder",
                level=ValidationLevel.CRITICAL,
                message=f"Failed to validate mobile UI builder: {e}",
                fix_suggestion="Check mobile UI builder implementation"
            ))
    
    def _validate_component_library(self):
        """
        @llm-type method
        @llm-legend Validate component library functionality
        @llm-key Ensures all UI components can be created and used
        """
        print("🎨 Validating component library...")
        
        try:
            # Test component imports
            from control.native_gui.ui.components import (
                Card, StatusIndicator, MetricCard, ComponentVariant,
                LoadingSpinner, EmptyState
            )
            
            # Test component creation
            components_to_test = [
                ("Card", lambda: Card("Test", "Test card")),
                ("StatusIndicator", lambda: StatusIndicator("Test", ComponentVariant.SUCCESS)),
                ("MetricCard", lambda: MetricCard("Test", "100%")),
                ("LoadingSpinner", lambda: LoadingSpinner("Loading...")),
                ("EmptyState", lambda: EmptyState("Empty", "No data"))
            ]
            
            for component_name, creator in components_to_test:
                try:
                    component = creator()
                    self._add_result(ValidationResult(
                        component="Component Library",
                        test_name=f"Create {component_name}",
                        level=ValidationLevel.SUCCESS,
                        message=f"{component_name} can be created successfully"
                    ))
                except Exception as e:
                    self._add_result(ValidationResult(
                        component="Component Library",
                        test_name=f"Create {component_name}",
                        level=ValidationLevel.ERROR,
                        message=f"Failed to create {component_name}: {e}",
                        fix_suggestion=f"Check {component_name} implementation"
                    ))
            
        except ImportError as e:
            self._add_result(ValidationResult(
                component="Component Library",
                test_name="Component Imports",
                level=ValidationLevel.CRITICAL,
                message=f"Failed to import components: {e}",
                fix_suggestion="Check component library implementation"
            ))
    
    def _validate_tool_integration(self):
        """
        @llm-type method
        @llm-legend Validate tool integration with mobile UI framework
        @llm-key Ensures tools can use mobile UI framework correctly
        """
        print("🔧 Validating tool integration...")
        
        try:
            from control.native_gui.core.tool_manager import BaseTool, ToolViewport
            from control.native_gui.tools.input_capture.tool import InputCaptureTool
            
            # Test enhanced BaseTool
            class TestTool(BaseTool):
                def _create_viewport_widget(self, viewport):
                    import gi
                    gi.require_version('Gtk', '4.0')
                    from gi.repository import Gtk
                    return Gtk.Label(label=f"Test {viewport.value}")
            
            tool = TestTool()
            
            # Test viewport support
            for viewport in ToolViewport:
                if tool.supports_viewport(viewport):
                    try:
                        widget = tool.create_widget(viewport)
                        self._add_result(ValidationResult(
                            component="Tool Integration",
                            test_name=f"Create {viewport.value} Widget",
                            level=ValidationLevel.SUCCESS,
                            message=f"Tool can create {viewport.value} widget"
                        ))
                    except Exception as e:
                        self._add_result(ValidationResult(
                            component="Tool Integration",
                            test_name=f"Create {viewport.value} Widget",
                            level=ValidationLevel.ERROR,
                            message=f"Failed to create {viewport.value} widget: {e}",
                            fix_suggestion=f"Check viewport widget creation for {viewport.value}"
                        ))
            
            # Test input capture tool
            input_tool = InputCaptureTool()
            self._add_result(ValidationResult(
                component="Tool Integration",
                test_name="Input Capture Tool",
                level=ValidationLevel.SUCCESS,
                message="Input capture tool can be instantiated"
            ))
            
        except Exception as e:
            self._add_result(ValidationResult(
                component="Tool Integration",
                test_name="Tool Integration",
                level=ValidationLevel.CRITICAL,
                message=f"Failed to validate tool integration: {e}",
                fix_suggestion="Check tool integration implementation"
            ))
    
    def _validate_theme_system(self):
        """
        @llm-type method
        @llm-legend Validate enhanced theme system
        @llm-key Ensures theme system works with mobile UI framework
        """
        print("🎨 Validating theme system...")
        
        try:
            from control.native_gui.core.theme_manager import ThemeManager, ThemeConfig, ThemeVariant
            
            # Test theme manager creation
            config = ThemeConfig(variant=ThemeVariant.DARK, mobile_optimized=True)
            theme_manager = ThemeManager(config)
            
            self._add_result(ValidationResult(
                component="Theme System",
                test_name="Theme Manager Creation",
                level=ValidationLevel.SUCCESS,
                message="Enhanced theme manager can be created"
            ))
            
            # Test theme methods
            theme_methods = ['get_theme_info', 'set_mobile_mode', '_generate_base_css', '_generate_mobile_css']
            for method in theme_methods:
                if hasattr(theme_manager, method):
                    self._add_result(ValidationResult(
                        component="Theme System",
                        test_name=f"Theme Method {method}",
                        level=ValidationLevel.SUCCESS,
                        message=f"Theme manager has method: {method}"
                    ))
                else:
                    self._add_result(ValidationResult(
                        component="Theme System",
                        test_name=f"Theme Method {method}",
                        level=ValidationLevel.WARNING,
                        message=f"Theme manager missing method: {method}",
                        fix_suggestion=f"Implement {method} in ThemeManager"
                    ))
            
        except Exception as e:
            self._add_result(ValidationResult(
                component="Theme System",
                test_name="Theme System",
                level=ValidationLevel.ERROR,
                message=f"Failed to validate theme system: {e}",
                fix_suggestion="Check theme system implementation"
            ))
    
    def _validate_documentation(self):
        """
        @llm-type method
        @llm-legend Validate documentation completeness
        @llm-key Ensures documentation is present and comprehensive
        """
        print("📚 Validating documentation...")
        
        doc_files = [
            ("docs/mobile_ui_framework.md", "Main Documentation"),
            ("control/native_gui/README_MOBILE_UI.md", "Integration Guide")
        ]
        
        for doc_file, doc_type in doc_files:
            doc_path = self.project_root / doc_file
            
            if doc_path.exists():
                # Check file size (should be substantial)
                file_size = doc_path.stat().st_size
                if file_size > 1000:  # At least 1KB
                    self._add_result(ValidationResult(
                        component="Documentation",
                        test_name=doc_type,
                        level=ValidationLevel.SUCCESS,
                        message=f"{doc_type} exists and has substantial content ({file_size} bytes)"
                    ))
                else:
                    self._add_result(ValidationResult(
                        component="Documentation",
                        test_name=doc_type,
                        level=ValidationLevel.WARNING,
                        message=f"{doc_type} exists but seems incomplete ({file_size} bytes)",
                        fix_suggestion=f"Expand documentation in {doc_file}"
                    ))
            else:
                self._add_result(ValidationResult(
                    component="Documentation",
                    test_name=doc_type,
                    level=ValidationLevel.ERROR,
                    message=f"Missing {doc_type}: {doc_file}",
                    fix_suggestion=f"Create documentation file: {doc_file}"
                ))
    
    def _validate_tests(self):
        """
        @llm-type method
        @llm-legend Validate test suite exists and can run
        @llm-key Ensures integration tests are present and functional
        """
        print("🧪 Validating test suite...")
        
        test_file = self.project_root / "control/native_gui/tests/test_mobile_ui_integration.py"
        
        if test_file.exists():
            self._add_result(ValidationResult(
                component="Test Suite",
                test_name="Integration Tests",
                level=ValidationLevel.SUCCESS,
                message="Integration test file exists"
            ))
            
            # Try to run a basic import test
            try:
                spec = importlib.util.spec_from_file_location("test_mobile_ui", test_file)
                test_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(test_module)
                
                self._add_result(ValidationResult(
                    component="Test Suite",
                    test_name="Test Import",
                    level=ValidationLevel.SUCCESS,
                    message="Integration tests can be imported"
                ))
            except Exception as e:
                self._add_result(ValidationResult(
                    component="Test Suite",
                    test_name="Test Import",
                    level=ValidationLevel.WARNING,
                    message=f"Test import failed: {e}",
                    fix_suggestion="Check test dependencies and imports"
                ))
        else:
            self._add_result(ValidationResult(
                component="Test Suite",
                test_name="Integration Tests",
                level=ValidationLevel.ERROR,
                message="Integration test file missing",
                fix_suggestion="Create integration test file"
            ))
    
    def _validate_generated_assets(self):
        """
        @llm-type method
        @llm-legend Validate generated assets can be created
        @llm-key Ensures build system can generate required assets
        """
        print("📦 Validating generated assets...")
        
        generated_dir = self.project_root / "generated"
        
        if generated_dir.exists():
            self._add_result(ValidationResult(
                component="Generated Assets",
                test_name="Generated Directory",
                level=ValidationLevel.SUCCESS,
                message="Generated directory exists"
            ))
        else:
            self._add_result(ValidationResult(
                component="Generated Assets",
                test_name="Generated Directory",
                level=ValidationLevel.WARNING,
                message="Generated directory missing",
                fix_suggestion="Run build system to create generated directory"
            ))
        
        # Check if mobile UI builder can run
        try:
            from build.modules.mobile_ui_builder import MobileUIBuilder
            builder = MobileUIBuilder()
            
            # Test discovery (doesn't actually build)
            result = builder._discover_components()
            if result.success:
                self._add_result(ValidationResult(
                    component="Generated Assets",
                    test_name="Component Discovery",
                    level=ValidationLevel.SUCCESS,
                    message="Mobile UI builder can discover components"
                ))
            else:
                self._add_result(ValidationResult(
                    component="Generated Assets",
                    test_name="Component Discovery",
                    level=ValidationLevel.WARNING,
                    message=f"Component discovery issues: {result.message}",
                    fix_suggestion="Check mobile UI component structure"
                ))
                
        except Exception as e:
            self._add_result(ValidationResult(
                component="Generated Assets",
                test_name="Build System Test",
                level=ValidationLevel.ERROR,
                message=f"Build system test failed: {e}",
                fix_suggestion="Check mobile UI builder implementation"
            ))
    
    def _add_result(self, result: ValidationResult):
        """Add validation result to results list"""
        self.results.append(result)
    
    def _generate_validation_report(self) -> bool:
        """
        @llm-type method
        @llm-legend Generate comprehensive validation report
        @llm-key Creates detailed report of validation results with actionable feedback
        """
        print("\n" + "=" * 70)
        print("📊 MOBILE UI INTEGRATION VALIDATION REPORT")
        print("=" * 70)
        
        # Count results by level
        counts = {level: 0 for level in ValidationLevel}
        for result in self.results:
            counts[result.level] += 1
        
        # Print summary
        print(f"\n📈 SUMMARY:")
        print(f"  ✅ Success: {counts[ValidationLevel.SUCCESS]}")
        print(f"  ⚠️  Warning: {counts[ValidationLevel.WARNING]}")
        print(f"  ❌ Error: {counts[ValidationLevel.ERROR]}")
        print(f"  🚨 Critical: {counts[ValidationLevel.CRITICAL]}")
        print(f"  📊 Total: {len(self.results)}")
        
        # Print detailed results by component
        components = {}
        for result in self.results:
            if result.component not in components:
                components[result.component] = []
            components[result.component].append(result)
        
        print(f"\n📋 DETAILED RESULTS:")
        for component, results in components.items():
            print(f"\n🔍 {component}:")
            
            for result in results:
                icon = {
                    ValidationLevel.SUCCESS: "✅",
                    ValidationLevel.WARNING: "⚠️",
                    ValidationLevel.ERROR: "❌",
                    ValidationLevel.CRITICAL: "🚨"
                }[result.level]
                
                print(f"  {icon} {result.test_name}: {result.message}")
                
                if result.details:
                    print(f"     Details: {result.details}")
                
                if result.fix_suggestion:
                    print(f"     Fix: {result.fix_suggestion}")
        
        # Determine overall success
        has_critical = counts[ValidationLevel.CRITICAL] > 0
        has_errors = counts[ValidationLevel.ERROR] > 0
        
        print(f"\n🎯 OVERALL RESULT:")
        if has_critical:
            print("🚨 CRITICAL ISSUES FOUND - Integration not ready for production")
            success = False
        elif has_errors:
            print("❌ ERRORS FOUND - Integration needs fixes before use")
            success = False
        elif counts[ValidationLevel.WARNING] > 0:
            print("⚠️  WARNINGS FOUND - Integration functional but could be improved")
            success = True
        else:
            print("✅ ALL VALIDATIONS PASSED - Integration ready for use")
            success = True
        
        print("=" * 70)
        
        return success


def main():
    """
    @llm-type main-function
    @llm-legend Main entry point for mobile UI integration validation
    @llm-key Executes comprehensive validation and returns appropriate exit code
    """
    print("🚀 Mobile UI Framework Integration Validation")
    print("=" * 50)
    
    validator = MobileUIIntegrationValidator()
    success = validator.validate_all()
    
    if success:
        print("\n🎉 Mobile UI integration validation completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Mobile UI integration validation failed!")
        print("Please address the issues above before proceeding.")
        sys.exit(1)


if __name__ == "__main__":
    main()
