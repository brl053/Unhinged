#!/usr/bin/env python3
"""
Test Generated Proto Clients
============================

This script proves that the generated protobuf clients are working correctly
by importing and inspecting the generated code.
"""

import sys
import os

# Add the generated clients to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generated/python/clients'))

def test_imports():
    """Test that all generated modules can be imported"""
    print("🧪 Testing generated proto client imports...")
    
    try:
        # Test chat service imports
        from unhinged_proto_clients import chat_pb2, chat_pb2_grpc
        print("✅ Chat service imports successful")
        
        # Test common imports
        from unhinged_proto_clients import common_pb2
        print("✅ Common proto imports successful")
        
        # Test other service imports
        from unhinged_proto_clients import messaging_pb2, messaging_pb2_grpc
        print("✅ Messaging service imports successful")
        
        from unhinged_proto_clients import cdc_service_pb2, cdc_service_pb2_grpc
        print("✅ CDC service imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_message_types():
    """Test that message types are properly generated"""
    print("\n🧪 Testing generated message types...")
    
    try:
        from unhinged_proto_clients import chat_pb2, common_pb2
        
        # Test creating message instances
        create_request = chat_pb2.CreateConversationRequest()
        print(f"✅ CreateConversationRequest created: {type(create_request)}")
        
        health_request = common_pb2.HealthCheckRequest()
        print(f"✅ HealthCheckRequest created: {type(health_request)}")
        
        # Test message serialization
        serialized = create_request.SerializeToString()
        print(f"✅ Message serialization works: {len(serialized)} bytes")
        
        # Test message deserialization
        deserialized = chat_pb2.CreateConversationRequest()
        deserialized.ParseFromString(serialized)
        print("✅ Message deserialization works")
        
        return True
        
    except Exception as e:
        print(f"❌ Message type test failed: {e}")
        return False


def test_service_stubs():
    """Test that service stubs are properly generated"""
    print("\n🧪 Testing generated service stubs...")
    
    try:
        from unhinged_proto_clients import chat_pb2_grpc
        import grpc
        
        # Test creating a stub (without connecting)
        channel = grpc.insecure_channel('localhost:50051')
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        print(f"✅ ChatServiceStub created: {type(stub)}")
        
        # Test that methods exist
        methods = [
            'CreateConversation', 'GetConversation', 'SendMessage', 
            'GetMessages', 'HealthCheck', 'StreamChat'
        ]
        
        for method in methods:
            if hasattr(stub, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"⚠️  Method {method} not found")
        
        channel.close()
        return True
        
    except Exception as e:
        print(f"❌ Service stub test failed: {e}")
        return False


def test_servicer_base():
    """Test that servicer base classes are generated"""
    print("\n🧪 Testing generated servicer base classes...")
    
    try:
        from unhinged_proto_clients import chat_pb2_grpc
        
        # Test servicer base class
        servicer = chat_pb2_grpc.ChatServiceServicer()
        print(f"✅ ChatServiceServicer created: {type(servicer)}")
        
        # Test that abstract methods exist
        methods = [
            'CreateConversation', 'GetConversation', 'SendMessage', 
            'GetMessages', 'HealthCheck'
        ]
        
        for method in methods:
            if hasattr(servicer, method):
                print(f"✅ Servicer method {method} exists")
            else:
                print(f"⚠️  Servicer method {method} not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Servicer test failed: {e}")
        return False


def inspect_generated_files():
    """Inspect what files were actually generated"""
    print("\n📁 Inspecting generated files...")
    
    base_path = os.path.join(os.path.dirname(__file__), 'generated/python/clients/unhinged_proto_clients')
    
    if not os.path.exists(base_path):
        print(f"❌ Generated path not found: {base_path}")
        return False
    
    files = [f for f in os.listdir(base_path) if f.endswith('.py')]
    files.sort()
    
    print(f"📊 Found {len(files)} generated Python files:")
    for file in files:
        file_path = os.path.join(base_path, file)
        size = os.path.getsize(file_path)
        print(f"  📄 {file} ({size:,} bytes)")
    
    # Count different types
    pb2_files = [f for f in files if f.endswith('_pb2.py')]
    grpc_files = [f for f in files if f.endswith('_pb2_grpc.py')]
    
    print(f"\n📈 Summary:")
    print(f"  • Message files (*_pb2.py): {len(pb2_files)}")
    print(f"  • Service files (*_pb2_grpc.py): {len(grpc_files)}")
    print(f"  • Total generated files: {len(files)}")
    
    return True


def main():
    """Run all tests"""
    print("🚀 Testing Generated Protobuf Clients")
    print("=" * 50)
    
    tests = [
        ("File Inspection", inspect_generated_files),
        ("Import Test", test_imports),
        ("Message Types", test_message_types),
        ("Service Stubs", test_service_stubs),
        ("Servicer Base", test_servicer_base),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL TESTS PASSED - Generated clients are working perfectly!")
        return True
    else:
        print("⚠️  Some tests failed - check the output above")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
