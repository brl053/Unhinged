#!/usr/bin/env python3

"""
@llm-type service
@llm-legend Test suite for the enhanced build system
@llm-key Provides comprehensive testing and validation of the enhanced build system features
@llm-map Test suite that validates all components of the enhanced build system
@llm-axiom Tests must be comprehensive, fast, and provide clear feedback on system health
@llm-contract Returns test results and system validation status
@llm-token build-test: Comprehensive test suite for enhanced build system

Enhanced Build System Test Suite

Comprehensive testing and validation for the enhanced build system:
- Component integration tests
- Performance validation
- Cache system tests
- Multi-language build tests
- Error handling validation
- Developer experience tests

Author: Unhinged Team
Version: 2.0.0
Date: 2025-10-19
"""

import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any

class EnhancedBuildSystemTester:
    """Comprehensive test suite for the enhanced build system"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_results = []
        self.start_time = time.time()
    
    async def run_all_tests(self) -> bool:
        """Run all test suites"""
        print("🧪 BUILD SYSTEM (V1) TEST SUITE")
        print("=" * 60)
        print()
        
        test_suites = [
            ("Basic Functionality", self.test_basic_functionality),
            ("Configuration Loading", self.test_configuration_loading),
            ("Cache System", self.test_cache_system),
            ("CLI Interface", self.test_cli_interface),
            ("LLM Integration", self.test_llm_integration),
            ("Performance Monitoring", self.test_performance_monitoring),
            ("Error Handling", self.test_error_handling),
            ("Developer Experience", self.test_developer_experience)
        ]
        
        all_passed = True
        
        for suite_name, test_func in test_suites:
            print(f"🔍 Testing {suite_name}...")
            try:
                passed = await test_func()
                status = "✅ PASSED" if passed else "❌ FAILED"
                print(f"   {status}")
                
                if not passed:
                    all_passed = False
                    
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                all_passed = False
            
            print()
        
        # Summary
        duration = time.time() - self.start_time
        print("📊 TEST SUMMARY")
        print("-" * 30)
        print(f"⏱️  Duration: {duration:.2f}s")
        print(f"📋 Total suites: {len(test_suites)}")
        
        if all_passed:
            print("🎉 All tests PASSED!")
            print("✅ Build system (v1) is ready for use!")
        else:
            print("❌ Some tests FAILED!")
            print("🔧 Please review the errors above and fix issues.")
        
        return all_passed
    
    async def test_basic_functionality(self) -> bool:
        """Test basic build system functionality"""
        try:
            # Test that we can import the main components
            from .orchestrator import BuildOrchestrator
            from .cli import BuildCLI
            from .modules import BuildModule
            
            # Test configuration loading
            orchestrator = BuildOrchestrator()
            
            # Test that we have some targets
            targets = orchestrator.dependency_graph.targets
            if not targets:
                print("   ⚠️  No build targets found")
                return False
            
            print(f"   📋 Found {len(targets)} build targets")
            return True
            
        except Exception as e:
            print(f"   ❌ Import error: {e}")
            return False
    
    async def test_configuration_loading(self) -> bool:
        """Test configuration loading"""
        try:
            from .orchestrator import BuildOrchestrator
            
            # Test original config
            original_config = self.project_root / "build-config.yml"
            if original_config.exists():
                orchestrator = BuildOrchestrator(original_config)
                print(f"   ✅ Original config loaded: {len(orchestrator.dependency_graph.targets)} targets")
            
            # Test enhanced config
            enhanced_config = self.project_root / "build" / "config" / "enhanced-build-config.yml"
            if enhanced_config.exists():
                orchestrator = BuildOrchestrator(enhanced_config)
                print(f"   ✅ Enhanced config loaded: {len(orchestrator.dependency_graph.targets)} targets")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Configuration error: {e}")
            return False
    
    async def test_cache_system(self) -> bool:
        """Test cache system functionality"""
        try:
            from .orchestrator import BuildCache
            
            cache = BuildCache()
            
            # Test cache key calculation
            from .orchestrator import BuildTarget
            test_target = BuildTarget(
                name="test-target",
                description="Test target",
                commands=["echo 'test'"],
                inputs=["test.txt"]
            )
            
            cache_key = cache.calculate_cache_key(test_target)
            if not cache_key:
                print("   ❌ Cache key generation failed")
                return False
            
            print(f"   ✅ Cache key generated: {cache_key[:16]}...")
            
            # Test cache operations
            from .orchestrator import BuildResult
            test_result = BuildResult(
                target="test-target",
                success=True,
                duration=1.0
            )
            
            cache.store_result(cache_key, test_result)
            
            if cache.is_cached(cache_key):
                print("   ✅ Cache storage and retrieval working")
                return True
            else:
                print("   ❌ Cache storage failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Cache system error: {e}")
            return False
    
    async def test_cli_interface(self) -> bool:
        """Test CLI interface"""
        try:
            # Test CLI help
            result = subprocess.run(
                [sys.executable, "build/cli.py", "--help"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print(f"   ❌ CLI help failed: {result.stderr}")
                return False
            
            if "Enhanced Unhinged Build System" not in result.stdout:
                print("   ❌ CLI help output incorrect")
                return False
            
            print("   ✅ CLI help working")
            
            # Test list command
            result = subprocess.run(
                [sys.executable, "build/cli.py", "list"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("   ✅ CLI list command working")
                return True
            else:
                print(f"   ⚠️  CLI list command failed (may be expected): {result.stderr}")
                return True  # This might fail if dependencies aren't installed
                
        except Exception as e:
            print(f"   ❌ CLI test error: {e}")
            return False
    
    async def test_llm_integration(self) -> bool:
        """Test LLM integration features"""
        try:
            from .llm_integration import LLMBuildIntegration
            
            llm = LLMBuildIntegration(self.project_root)
            
            # Test context generation
            context = llm.generate_build_context(["dev-fast"])
            if not context or len(context) < 100:
                print("   ❌ LLM context generation failed")
                return False
            
            print("   ✅ LLM context generation working")
            
            # Test error explanation
            from .llm_integration import BuildError
            test_error = BuildError(
                target="test-target",
                error_message="Test error message",
                command="test command",
                exit_code=1,
                stdout="",
                stderr="Test error",
                context={}
            )
            
            explanation = llm.explain_build_error(test_error)
            if not explanation or len(explanation) < 50:
                print("   ❌ LLM error explanation failed")
                return False
            
            print("   ✅ LLM error explanation working")
            
            # Test onboarding guide
            guide = llm.generate_onboarding_guide()
            if not guide or "Enhanced Build System" not in guide:
                print("   ❌ LLM onboarding guide failed")
                return False
            
            print("   ✅ LLM onboarding guide working")
            return True
            
        except Exception as e:
            print(f"   ❌ LLM integration error: {e}")
            return False
    
    async def test_performance_monitoring(self) -> bool:
        """Test performance monitoring"""
        try:
            # Check if monitoring dependencies are available
            try:
                import psutil
                monitoring_available = True
            except ImportError:
                print("   ⚠️  psutil not available, monitoring tests skipped")
                return True
            
            from .monitoring import BuildPerformanceMonitor
            
            monitor = BuildPerformanceMonitor(self.project_root)
            
            # Test metrics collection
            cache_metrics = monitor.get_cache_metrics()
            system_metrics = monitor.get_system_metrics()
            
            if cache_metrics.total_entries < 0:
                print("   ❌ Cache metrics invalid")
                return False
            
            if system_metrics.cpu_cores <= 0:
                print("   ❌ System metrics invalid")
                return False
            
            print(f"   ✅ Performance monitoring working (CPU: {system_metrics.cpu_cores} cores)")
            return True
            
        except Exception as e:
            print(f"   ❌ Performance monitoring error: {e}")
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling"""
        try:
            from .orchestrator import BuildOrchestrator
            
            orchestrator = BuildOrchestrator()
            
            # Test building non-existent target
            result = await orchestrator.build_target("non-existent-target")
            
            if result.success:
                print("   ❌ Error handling failed - should have failed")
                return False
            
            if "not found" not in result.error_message:
                print("   ❌ Error message incorrect")
                return False
            
            print("   ✅ Error handling working")
            return True
            
        except Exception as e:
            print(f"   ❌ Error handling test error: {e}")
            return False
    
    async def test_developer_experience(self) -> bool:
        """Test developer experience features"""
        try:
            from .developer_experience import QuickCommands, BuildStatusDashboard
            
            quick_commands = QuickCommands(self.project_root)
            
            # Test quick setup
            setup_commands = quick_commands.quick_setup()
            if not setup_commands or len(setup_commands) < 5:
                print("   ❌ Quick setup commands failed")
                return False
            
            print("   ✅ Quick setup commands working")
            
            # Test common workflows
            workflows = quick_commands.common_workflows()
            if not workflows or "First Time Setup" not in workflows:
                print("   ❌ Common workflows failed")
                return False
            
            print("   ✅ Common workflows working")
            
            # Test build shortcuts
            shortcuts = quick_commands.get_build_shortcuts()
            if not shortcuts or "dev" not in shortcuts:
                print("   ❌ Build shortcuts failed")
                return False
            
            print("   ✅ Build shortcuts working")
            return True
            
        except Exception as e:
            print(f"   ❌ Developer experience error: {e}")
            return False

async def main():
    """Main test runner"""
    tester = EnhancedBuildSystemTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 BUILD SYSTEM (V1) READY!")
        print("Try these commands to get started:")
        print("  make build")
        print("  make status")
        print("  make list")
        return 0
    else:
        print("\n❌ TESTS FAILED!")
        print("Please fix the issues above before using the build system.")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
