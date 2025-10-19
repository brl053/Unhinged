#!/usr/bin/env python3

"""
@llm-type test-script
@llm-legend Test script for DAG control plane validation
@llm-key Comprehensive testing of control plane components and integration
@llm-map Test script that validates all control plane functionality
@llm-axiom Tests must be comprehensive, fast, and provide clear feedback
@llm-contract Returns clear pass/fail status with detailed error information
@llm-token control-test: Test script for control plane validation

Control Plane Test Script

Comprehensive testing of:
- DAG engine functionality
- HTTP server operations
- Human interface generation
- Configuration loading
- Integration points

Author: Unhinged Team
Version: 1.0.0
Date: 2025-10-19
"""

import sys
import time
import threading
import urllib.request
import urllib.error
from pathlib import Path

def test_imports():
    """Test that all control plane modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from control.dag import DAG, DAGNode, NodeStatus
        from control.server import start_dag_server, DAGHandler
        from control.human import HumanInterface
        from control.config import CONTROL_PLANE_CONFIG, DAG_TARGETS
        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_dag_functionality():
    """Test core DAG functionality"""
    print("🔍 Testing DAG functionality...")
    
    try:
        from control.dag import DAG, DAGNode
        
        # Create test DAG
        dag = DAG()
        
        # Add nodes
        node1 = DAGNode("test1", "echo 'test1'")
        node2 = DAGNode("test2", "echo 'test2'")
        node3 = DAGNode("test3", "echo 'test3'")
        
        dag.add_node(node1)
        dag.add_node(node2)
        dag.add_node(node3)
        
        # Add dependencies: test3 depends on test1 and test2
        dag.add_dependency("test3", "test1")
        dag.add_dependency("test3", "test2")
        
        # Test validation
        is_valid, errors = dag.validate()
        if not is_valid:
            print(f"❌ DAG validation failed: {errors}")
            return False
        
        # Test execution order
        execution_order = dag.get_execution_order("test3")
        expected_groups = 2  # Group 1: [test1, test2], Group 2: [test3]
        
        if len(execution_order) != expected_groups:
            print(f"❌ Execution order incorrect: got {len(execution_order)} groups, expected {expected_groups}")
            return False
        
        # Test cycle detection
        dag.add_dependency("test1", "test3")  # Create cycle
        is_valid, errors = dag.validate()
        if is_valid:
            print("❌ Cycle detection failed - should have detected cycle")
            return False
        
        print("✅ DAG functionality tests passed")
        return True
        
    except Exception as e:
        print(f"❌ DAG functionality test failed: {e}")
        return False

def test_http_server():
    """Test HTTP server functionality"""
    print("🔍 Testing HTTP server...")
    
    try:
        from control.server import start_dag_server
        import threading
        import time
        
        # Start server in background thread
        server_thread = threading.Thread(
            target=start_dag_server, 
            args=(9001,),  # Use different port for testing
            daemon=True
        )
        server_thread.start()
        
        # Wait for server to start
        time.sleep(2)
        
        # Test health endpoint
        try:
            request = urllib.request.Request("http://localhost:9001/dag/health")
            response = urllib.request.urlopen(request, timeout=5)

            if response.status != 200:
                print(f"❌ Health check failed: status {response.status}")
                return False

            # Parse JSON response
            import json
            response_data = response.read().decode()
            health_data = json.loads(response_data)

            if health_data.get("status") != "healthy":
                print(f"❌ Health check failed: status not healthy")
                return False

        except urllib.error.URLError as e:
            print(f"❌ HTTP server test failed: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            return False
        
        # Test status endpoint
        try:
            response = urllib.request.urlopen("http://localhost:9001/dag/status", timeout=5)
            if response.status != 200:
                print(f"❌ Status endpoint failed: status {response.status}")
                return False
        except urllib.error.URLError as e:
            print(f"❌ Status endpoint test failed: {e}")
            return False
        
        # Test targets endpoint
        try:
            response = urllib.request.urlopen("http://localhost:9001/dag/targets", timeout=5)
            if response.status != 200:
                print(f"❌ Targets endpoint failed: status {response.status}")
                return False
        except urllib.error.URLError as e:
            print(f"❌ Targets endpoint test failed: {e}")
            return False
        
        print("✅ HTTP server tests passed")
        return True
        
    except Exception as e:
        print(f"❌ HTTP server test failed: {e}")
        return False

def test_human_interface():
    """Test human interface functionality"""
    print("🔍 Testing human interface...")
    
    try:
        from control.human import HumanInterface
        import tempfile
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            human_interface = HumanInterface(temp_dir)
            
            # Test approval page generation
            approval_html = human_interface.generate_approval_page(
                request=type('ApprovalRequest', (), {
                    'target': 'test-target',
                    'node': 'test-node',
                    'description': 'Test description',
                    'estimated_duration': 30.0,
                    'dependencies': ['dep1', 'dep2'],
                    'timestamp': time.time()
                })(),
                approval_id='test-approval-123'
            )
            
            # Check that HTML contains expected elements
            required_elements = [
                'DAG Execution Approval',
                'test-target',
                'test-node',
                'Test description',
                'Approve Execution',
                'Reject Execution'
            ]
            
            for element in required_elements:
                if element not in approval_html:
                    print(f"❌ Missing element in approval HTML: {element}")
                    return False
            
            print("✅ Human interface tests passed")
            return True
            
    except Exception as e:
        print(f"❌ Human interface test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("🔍 Testing configuration...")
    
    try:
        from control.config import (
            CONTROL_PLANE_CONFIG, 
            DAG_TARGETS, 
            get_node_command,
            requires_human_approval
        )
        
        # Test configuration structure
        required_config_keys = ['server_port', 'static_html_path', 'max_parallel_jobs']
        for key in required_config_keys:
            if key not in CONTROL_PLANE_CONFIG:
                print(f"❌ Missing configuration key: {key}")
                return False
        
        # Test DAG targets
        if not DAG_TARGETS:
            print("❌ No DAG targets defined")
            return False
        
        # Test that targets have required structure
        for target_name, target_config in DAG_TARGETS.items():
            required_keys = ['description', 'nodes']
            for key in required_keys:
                if key not in target_config:
                    print(f"❌ Target {target_name} missing key: {key}")
                    return False
        
        # Test utility functions
        test_command = get_node_command('proto-gen')
        if not test_command:
            print("❌ get_node_command returned empty result")
            return False
        
        print("✅ Configuration tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_integration():
    """Test integration between components"""
    print("🔍 Testing component integration...")
    
    try:
        from control import create_sample_dag
        
        # Create sample DAG
        dag = create_sample_dag()
        
        # Test that sample DAG is valid
        is_valid, errors = dag.validate()
        if not is_valid:
            print(f"❌ Sample DAG validation failed: {errors}")
            return False
        
        # Test execution (dry run)
        results = dag.execute("start-services", human_approval=False)
        
        # Check that all nodes executed successfully
        failed_results = [r for r in results if not r.success]
        if failed_results:
            print(f"❌ Sample DAG execution failed: {len(failed_results)} failures")
            for result in failed_results:
                print(f"  - {result.node_name}: {result.error_message}")
            return False
        
        print("✅ Integration tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 CONTROL PLANE TEST SUITE")
    print("=" * 50)
    print()
    
    tests = [
        ("Import Tests", test_imports),
        ("DAG Functionality", test_dag_functionality),
        ("HTTP Server", test_http_server),
        ("Human Interface", test_human_interface),
        ("Configuration", test_configuration),
        ("Integration", test_integration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"🔬 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} ERROR: {e}")
        print()
    
    # Summary
    total = passed + failed
    print("📊 TEST SUMMARY")
    print("-" * 30)
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(passed/total*100):.1f}%")
    print()
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Control plane is ready for use!")
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        print("🔧 Please fix the issues above before using the control plane.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
