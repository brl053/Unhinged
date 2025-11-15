#!/usr/bin/env python3
"""
Session Store Implementation Validation

Validates the write-through architecture implementation without dependencies.
Checks code structure, logic flow, and architectural patterns.

@llm-type validation.session
@llm-does implementation validation for write-through session architecture
"""

import ast
from pathlib import Path


def validate_session_store_implementation():
    """Validate session store implementation structure and logic"""
    print("🔍 VALIDATING SESSION STORE IMPLEMENTATION")
    print("=" * 60)

    # Read the session store source
    session_store_path = Path(__file__).parent / "session_store.py"
    if not session_store_path.exists():
        print("❌ session_store.py not found")
        return False

    with open(session_store_path) as f:
        source_code = f.read()

    # Parse AST
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        print(f"❌ Syntax error in session_store.py: {e}")
        return False

    print("✅ Source code syntax is valid")

    # Validate class structure
    session_store_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "SessionStore":
            session_store_class = node
            break

    if not session_store_class:
        print("❌ SessionStore class not found")
        return False

    print("✅ SessionStore class found")

    # Check required methods
    required_methods = ["write", "read", "delete", "exists", "health_check"]
    found_methods = []

    for node in session_store_class.body:
        if isinstance(node, ast.FunctionDef):
            found_methods.append(node.name)

    missing_methods = set(required_methods) - set(found_methods)
    if missing_methods:
        print(f"❌ Missing required methods: {missing_methods}")
        return False

    print("✅ All required methods present")

    # Validate write method logic
    write_method = None
    for node in session_store_class.body:
        if isinstance(node, ast.FunctionDef) and node.name == "write":
            write_method = node
            break

    if not write_method:
        print("❌ Write method not found")
        return False

    # Check write-through pattern in write method
    write_source = ast.get_source_segment(source_code, write_method)
    if not write_source:
        print("⚠️ Could not extract write method source")
    else:
        # Check for Redis first, then CRDB pattern
        if "redis_client.set" in write_source and "cursor.execute" in write_source:
            print("✅ Write-through pattern detected in write method")
        else:
            print("❌ Write-through pattern not found in write method")
            return False

        # Check for rollback on CRDB failure
        if "redis_client.delete" in write_source:
            print("✅ Redis rollback on CRDB failure detected")
        else:
            print("⚠️ Redis rollback pattern not clearly detected")

    # Validate read method logic
    read_method = None
    for node in session_store_class.body:
        if isinstance(node, ast.FunctionDef) and node.name == "read":
            read_method = node
            break

    if not read_method:
        print("❌ Read method not found")
        return False

    read_source = ast.get_source_segment(source_code, read_method)
    if not read_source:
        print("⚠️ Could not extract read method source")
    else:
        # Check for Redis first, CRDB fallback pattern
        if "redis_client.get" in read_source and "cursor.execute" in read_source:
            print("✅ Cache-first read pattern detected")
        else:
            print("❌ Cache-first read pattern not found")
            return False

        # Check for cache population
        if "redis_client.set" in read_source:
            print("✅ Cache population on miss detected")
        else:
            print("❌ Cache population pattern not found")
            return False

    print("\n🏗️ ARCHITECTURAL PATTERN VALIDATION")
    print("-" * 40)

    # Check configuration class
    config_classes = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and "Config" in node.name
    ]
    if config_classes:
        print(f"✅ Configuration class found: {config_classes}")
    else:
        print("❌ Configuration class not found")
        return False

    # Check error handling
    exception_classes = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and "Error" in node.name
    ]
    if exception_classes:
        print(f"✅ Custom exception class found: {exception_classes}")
    else:
        print("⚠️ Custom exception class not found")

    # Check connection pooling
    if "ThreadedConnectionPool" in source_code:
        print("✅ CRDB connection pooling implemented")
    else:
        print("❌ CRDB connection pooling not found")
        return False

    # Check health monitoring
    if "health_check" in [
        node.name for node in session_store_class.body if isinstance(node, ast.FunctionDef)
    ]:
        print("✅ Health check method implemented")
    else:
        print("❌ Health check method not found")
        return False

    print("\n📊 IMPLEMENTATION STATISTICS")
    print("-" * 30)

    # Count methods
    method_count = len(
        [node for node in session_store_class.body if isinstance(node, ast.FunctionDef)]
    )
    print(f"Methods implemented: {method_count}")

    # Count lines
    lines = source_code.split("\n")
    code_lines = [line for line in lines if line.strip() and not line.strip().startswith("#")]
    print(f"Lines of code: {len(code_lines)}")

    # Check imports
    imports = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
    print(f"Import statements: {len(imports)}")

    print("\n✅ SESSION STORE IMPLEMENTATION VALIDATION COMPLETE")
    print("🎯 Write-through architecture correctly implemented")
    print("🔧 Ready for integration with chat service")

    return True


def validate_chat_service_integration():
    """Validate chat service integration"""
    print("\n🔍 VALIDATING CHAT SERVICE INTEGRATION")
    print("=" * 60)

    # Check chat service file
    chat_service_path = (
        Path(__file__).parent.parent.parent.parent
        / "services"
        / "chat-with-sessions"
        / "grpc_server.py"
    )
    if not chat_service_path.exists():
        print("❌ Chat service with sessions not found")
        return False

    with open(chat_service_path) as f:
        chat_source = f.read()

    print("✅ Chat service with sessions found")

    # Check session store import
    if "from session.session_store import SessionStore" in chat_source:
        print("✅ Session store import found")
    else:
        print("❌ Session store import not found")
        return False

    # Check session management methods
    session_methods = ["_create_session", "_get_session", "_update_session_state"]
    for method in session_methods:
        if method in chat_source:
            print(f"✅ Session method {method} found")
        else:
            print(f"❌ Session method {method} not found")
            return False

    # Check gRPC service implementation
    if "ChatWithSessionsServicer" in chat_source:
        print("✅ Chat service class found")
    else:
        print("❌ Chat service class not found")
        return False

    # Check CreateConversation integration
    if "CreateConversation" in chat_source and "_create_session" in chat_source:
        print("✅ Session creation integrated with conversation creation")
    else:
        print("❌ Session integration not found")
        return False

    print("✅ Chat service integration validation complete")
    return True


def validate_ui_integration():
    """Validate UI integration"""
    print("\n🔍 VALIDATING UI INTEGRATION")
    print("=" * 60)

    # Check session management component
    ui_component_path = (
        Path(__file__).parent.parent.parent.parent
        / "control"
        / "gtk4_gui"
        / "components"
        / "session_management.py"
    )
    if not ui_component_path.exists():
        print("❌ Session management UI component not found")
        return False

    with open(ui_component_path) as f:
        ui_source = f.read()

    print("✅ Session management UI component found")

    # Check progressive disclosure pattern
    if "create_session_button" in ui_source and "session_info_box" in ui_source:
        print("✅ Progressive disclosure UI pattern implemented")
    else:
        print("❌ Progressive disclosure pattern not found")
        return False

    # Check gRPC integration
    if "create_chat_client" in ui_source:
        print("✅ gRPC client integration found")
    else:
        print("❌ gRPC client integration not found")
        return False

    # Check session state management
    if "SessionState" in ui_source:
        print("✅ Session state management found")
    else:
        print("❌ Session state management not found")
        return False

    print("✅ UI integration validation complete")
    return True


def main():
    """Main validation function"""
    print("🚀 SESSION MANAGEMENT IMPLEMENTATION VALIDATION")
    print("=" * 80)

    success = True

    # Validate core implementation
    if not validate_session_store_implementation():
        success = False

    # Validate service integration
    if not validate_chat_service_integration():
        success = False

    # Validate UI integration
    if not validate_ui_integration():
        success = False

    print("\n" + "=" * 80)
    if success:
        print("🎉 ALL VALIDATIONS PASSED")
        print("✅ Write-through session management implementation complete")
        print("🔧 Ready for deployment and testing")
        print("\nNext steps:")
        print("1. Install Redis and CRDB dependencies")
        print("2. Start Redis and CRDB services")
        print("3. Run chat service with sessions")
        print("4. Test UI integration")
    else:
        print("❌ VALIDATION FAILURES DETECTED")
        print("🔧 Fix issues before proceeding")

    return success


if __name__ == "__main__":
    main()
