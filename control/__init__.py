#!/usr/bin/env python3

"""
@llm-type control-plane-init
@llm-legend Control plane package initialization and main entry point
@llm-key Provides unified access to control plane components and startup functionality
@llm-map Package initialization that exposes control plane API and provides main entry point
@llm-axiom Control plane must be easily importable and provide clear entry points
@llm-contract Exports main control plane classes and provides startup functionality
@llm-token control-init: Control plane package initialization

Control Plane Package

Minimal DAG control plane providing:
- DAG execution engine
- HTTP API server
- Human approval workflows
- Browser integration

Author: Unhinged Team
Version: 1.0.0
Date: 2025-10-19
"""

from .dag import DAG, DAGNode, NodeStatus, ExecutionResult
from .server import start_dag_server, DAGHandler
from .human import HumanInterface, ApprovalRequest, ApprovalResult
from .config import (
    CONTROL_PLANE_CONFIG,
    DAG_TARGETS,
    SERVICE_INTEGRATION,
    get_node_command,
    requires_human_approval
)

__version__ = "1.0.0"
__author__ = "Unhinged Team"

# Export main classes and functions
__all__ = [
    # Core DAG classes
    'DAG',
    'DAGNode', 
    'NodeStatus',
    'ExecutionResult',
    
    # Server components
    'start_dag_server',
    'DAGHandler',
    
    # Human interface
    'HumanInterface',
    'ApprovalRequest',
    'ApprovalResult',
    
    # Configuration
    'CONTROL_PLANE_CONFIG',
    'DAG_TARGETS',
    'SERVICE_INTEGRATION',
    'get_node_command',
    'requires_human_approval',
    
    # Utility functions
    'main',
    'create_sample_dag',
    'test_control_plane'
]

def create_sample_dag() -> DAG:
    """Create a sample DAG for testing"""
    dag = DAG()
    
    # Create sample nodes
    proto_node = DAGNode(
        name="proto-gen",
        description="Generate protobuf bindings",
        command="echo 'Generating protobuf bindings...'"
    )
    
    backend_node = DAGNode(
        name="backend-compile",
        description="Compile Kotlin backend",
        command="echo 'Compiling Kotlin backend...'"
    )
    
    frontend_node = DAGNode(
        name="frontend-compile", 
        description="Compile TypeScript frontend",
        command="echo 'Compiling TypeScript frontend...'"
    )
    
    services_node = DAGNode(
        name="start-services",
        description="Start development services",
        command="echo 'Starting development services...'"
    )
    
    # Add nodes to DAG
    dag.add_node(proto_node)
    dag.add_node(backend_node)
    dag.add_node(frontend_node)
    dag.add_node(services_node)
    
    # Add dependencies
    dag.add_dependency("backend-compile", "proto-gen")
    dag.add_dependency("frontend-compile", "proto-gen")
    dag.add_dependency("start-services", "backend-compile")
    dag.add_dependency("start-services", "frontend-compile")
    
    return dag

def test_control_plane():
    """Test the control plane functionality"""
    print("🧪 Testing Control Plane...")
    
    # Test DAG creation and validation
    dag = create_sample_dag()
    is_valid, errors = dag.validate()
    
    if is_valid:
        print("✅ DAG validation passed")
    else:
        print(f"❌ DAG validation failed: {errors}")
        return False
    
    # Test execution order
    try:
        execution_order = dag.get_execution_order("start-services")
        print(f"✅ Execution order: {execution_order}")
    except Exception as e:
        print(f"❌ Execution order failed: {e}")
        return False
    
    # Test DAG execution (dry run)
    print("🔄 Testing DAG execution...")
    try:
        results = dag.execute("start-services", human_approval=False)
        success_count = sum(1 for r in results if r.success)
        print(f"✅ DAG execution completed: {success_count}/{len(results)} successful")
    except Exception as e:
        print(f"❌ DAG execution failed: {e}")
        return False
    
    print("🎉 Control plane test completed successfully!")
    return True

def main():
    """Main entry point for control plane"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Unhinged DAG Control Plane",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m control                    # Start HTTP server
  python -m control --test             # Run tests
  python -m control --port 9001        # Start on custom port
  python -m control --sample           # Create and run sample DAG
        """
    )
    
    parser.add_argument(
        '--port', 
        type=int, 
        default=CONTROL_PLANE_CONFIG["server_port"],
        help='HTTP server port (default: 9000)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run control plane tests'
    )
    
    parser.add_argument(
        '--sample',
        action='store_true', 
        help='Create and execute sample DAG'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate control plane installation'
    )
    
    args = parser.parse_args()
    
    # Handle different modes
    if args.test:
        success = test_control_plane()
        sys.exit(0 if success else 1)
    
    elif args.sample:
        print("🎯 Creating and executing sample DAG...")
        dag = create_sample_dag()
        results = dag.execute("start-services", human_approval=False)
        
        print("\n📊 Results:")
        for result in results:
            status = "✅" if result.success else "❌"
            print(f"{status} {result.node_name}: {result.duration:.2f}s")
        
        sys.exit(0)
    
    elif args.validate:
        print("✅ Validating control plane installation...")
        
        # Check imports
        try:
            from .dag import DAG
            from .server import start_dag_server
            from .human import HumanInterface
            print("✅ All modules imported successfully")
        except ImportError as e:
            print(f"❌ Import error: {e}")
            sys.exit(1)
        
        # Test basic functionality
        success = test_control_plane()
        if success:
            print("✅ Control plane validation passed")
            sys.exit(0)
        else:
            print("❌ Control plane validation failed")
            sys.exit(1)
    
    else:
        # Default: start HTTP server
        print("🎛️ Starting DAG Control Plane...")
        print(f"📡 Server will run on port {args.port}")
        print("🌐 Browser interface will be available via static_html")
        print("⏹️  Press Ctrl+C to stop")
        print()
        
        try:
            from .server import start_dag_server
            start_dag_server(args.port)
        except KeyboardInterrupt:
            print("\n🛑 Control plane stopped by user")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Failed to start control plane: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
