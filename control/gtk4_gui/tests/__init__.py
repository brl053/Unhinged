#!/usr/bin/env python3
"""
@llm-doc GTK4 GUI Test Suite
@llm-version 1.0.0
@llm-date 2025-10-28

Consolidated test suite for the GTK4 GUI components and modules.
Provides comprehensive testing for all components, monitors, and integrations.
"""

# Test suite imports - explicit imports only
try:
    from .test_components import ComponentTestApp
    from .test_monitors import SystemInfoProductionTester
    # test_integration has no test classes currently
except ImportError:
    # Fallback for direct execution
    pass

__all__ = [
    # Available test classes
    "SystemInfoProductionTester",
    "TestApp",
    # Test utilities
    "run_all_tests",
    "run_monitor_tests",
    "run_component_tests",
]


def run_all_tests():
    """Run the complete test suite."""
    import unittest

    # Discover and run all tests
    loader = unittest.TestLoader()
    suite = loader.discover(".", pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


def run_monitor_tests():
    """Run only monitor-related tests."""
    import unittest

    from .test_monitors import TestProcessMonitor, TestSystemInfo

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSystemInfo))
    suite.addTest(unittest.makeSuite(TestProcessMonitor))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


def run_component_tests():
    """Run only component-related tests."""
    import unittest

    from .test_components import TestComplexComponents, TestPrimitiveComponents

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPrimitiveComponents))
    suite.addTest(unittest.makeSuite(TestComplexComponents))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


def run_integration_tests():
    """Run only integration tests."""
    import unittest

    from .test_integration import TestDesktopAppIntegration

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDesktopAppIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    print("🧪 Running GTK4 GUI Test Suite...")
    success = run_all_tests()

    if success:
        print("✅ All tests passed!")
        exit(0)
    else:
        print("❌ Some tests failed!")
        exit(1)
