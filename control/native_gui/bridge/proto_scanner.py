
# Initialize GUI event logger
gui_logger = create_gui_logger("unhinged-proto-scanner", "1.0.0")

"""
@llm-type control-system
@llm-legend proto_scanner.py - system control component
@llm-key Core functionality for proto_scanner
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token proto_scanner: system control component
"""
"""
🔍 Proto Scanner - Direct Python Implementation

Scans for .proto files and parses gRPC services.
No HTTP bridge - direct Python method calls for instant response.

Features:
- Recursive proto file discovery
- Service and method parsing
- Message type extraction
- Import dependency resolution
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from unhinged_events import create_gui_logger


class ProtoScanner:
    """
    Proto file scanner and parser.
    
    Direct Python implementation - no HTTP bridge needed.
    Instant response times with zero network overhead.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        
        # Default search paths for proto files
        self.search_paths = [
            self.project_root / "proto",
            self.project_root / "services",
            self.project_root / "platforms",
            self.project_root,
        ]
        
    
    def scan_proto_files(self) -> Dict[str, Any]:
        """
        Scan for all .proto files in the project.
        
        Returns:
            Dict with success status and list of proto files
        """
        try:
            proto_files = []
            
            for search_path in self.search_paths:
                if search_path.exists():
                    proto_files.extend(self._scan_directory(search_path))
            
            # Remove duplicates based on absolute path
            unique_files = {}
            for file_info in proto_files:
                abs_path = file_info["absolute_path"]
                if abs_path not in unique_files:
                    unique_files[abs_path] = file_info
            
            result_files = list(unique_files.values())
            
            return {
                "success": True,
                "proto_files": result_files,
                "count": len(result_files),
                "search_paths": [str(p) for p in self.search_paths]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to scan proto files: {str(e)}",
                "proto_files": [],
                "count": 0
            }
    
    def _scan_directory(self, directory: Path) -> List[Dict[str, Any]]:
        """Recursively scan directory for .proto files"""
        proto_files = []
        
        try:
            for root, dirs, files in os.walk(directory):
                root_path = Path(root)
                
                for file in files:
                    if file.endswith('.proto'):
                        file_path = root_path / file
                        
                        # Get file stats
                        stat = file_path.stat()
                        
                        # Calculate relative path from project root
                        try:
                            relative_path = file_path.relative_to(self.project_root)
                        except ValueError:
                            relative_path = file_path
                        
                        file_info = {
                            "path": str(relative_path),
                            "absolute_path": str(file_path.absolute()),
                            "name": file,
                            "size": stat.st_size,
                            "modified": stat.st_mtime,
                            "directory": str(root_path.relative_to(self.project_root))
                        }
                        
                        proto_files.append(file_info)
                        
        except Exception as e:
            gui_logger.error(f" Error scanning directory {directory}: {e}")
        
        return proto_files
    
    def parse_proto_services(self, proto_file_path: str) -> Dict[str, Any]:
        """
        Parse gRPC services from a proto file.
        
        Args:
            proto_file_path: Path to the .proto file
            
        Returns:
            Dict with success status and parsed services
        """
        try:
            # Resolve file path
            if Path(proto_file_path).is_absolute():
                file_path = Path(proto_file_path)
            else:
                file_path = self.project_root / proto_file_path
            
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"Proto file not found: {file_path}",
                    "services": []
                }
            
            # Read and parse the proto file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            services = self._parse_services_from_content(content)
            
            return {
                "success": True,
                "services": services,
                "file_path": str(file_path),
                "service_count": len(services)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse proto file: {str(e)}",
                "services": []
            }
    
    def _parse_services_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Parse gRPC services from proto file content"""
        services = []
        
        # Remove comments and normalize whitespace
        content = self._remove_comments(content)
        
        # Find all service definitions
        service_pattern = r'service\s+(\w+)\s*\{([^}]+)\}'
        service_matches = re.finditer(service_pattern, content, re.MULTILINE | re.DOTALL)
        
        for service_match in service_matches:
            service_name = service_match.group(1)
            service_body = service_match.group(2)
            
            # Parse methods within the service
            methods = self._parse_service_methods(service_body)
            
            service_info = {
                "name": service_name,
                "methods": methods,
                "method_count": len(methods)
            }
            
            services.append(service_info)
        
        return services
    
    def _parse_service_methods(self, service_body: str) -> List[Dict[str, Any]]:
        """Parse RPC methods from service body"""
        methods = []
        
        # Pattern to match RPC method definitions
        # rpc MethodName(RequestType) returns (ResponseType);
        method_pattern = r'rpc\s+(\w+)\s*\(\s*(\w+)\s*\)\s*returns\s*\(\s*(\w+)\s*\)\s*;'
        method_matches = re.finditer(method_pattern, service_body, re.MULTILINE)
        
        for method_match in method_matches:
            method_name = method_match.group(1)
            request_type = method_match.group(2)
            response_type = method_match.group(3)
            
            method_info = {
                "name": method_name,
                "request_type": request_type,
                "response_type": response_type,
                "full_signature": f"rpc {method_name}({request_type}) returns ({response_type})"
            }
            
            methods.append(method_info)
        
        return methods
    
    def _remove_comments(self, content: str) -> str:
        """Remove comments from proto file content"""
        # Remove single-line comments
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        return content
    
    def get_message_template(self, message_type: str, proto_file_path: str) -> Dict[str, Any]:
        """
        Generate a template for a protobuf message type.
        
        Args:
            message_type: Name of the message type
            proto_file_path: Path to the proto file containing the message
            
        Returns:
            Dict with success status and message template
        """
        try:
            # Resolve file path
            if Path(proto_file_path).is_absolute():
                file_path = Path(proto_file_path)
            else:
                file_path = self.project_root / proto_file_path
            
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"Proto file not found: {file_path}",
                    "template": {}
                }
            
            # Read proto file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse message definition
            template = self._parse_message_template(content, message_type)
            
            return {
                "success": True,
                "template": template,
                "message_type": message_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate template: {str(e)}",
                "template": {}
            }
    
    def _parse_message_template(self, content: str, message_type: str) -> Dict[str, Any]:
        """Parse message definition and generate JSON template"""
        # Remove comments
        content = self._remove_comments(content)
        
        # Find message definition
        message_pattern = rf'message\s+{re.escape(message_type)}\s*\{{([^}}]+)\}}'
        message_match = re.search(message_pattern, content, re.MULTILINE | re.DOTALL)
        
        if not message_match:
            return {"error": f"Message type '{message_type}' not found"}
        
        message_body = message_match.group(1)
        
        # Parse fields
        template = {}
        field_pattern = r'(\w+)\s+(\w+)\s*=\s*\d+\s*;'
        field_matches = re.finditer(field_pattern, message_body)
        
        for field_match in field_matches:
            field_type = field_match.group(1)
            field_name = field_match.group(2)
            
            # Generate default value based on type
            default_value = self._get_default_value_for_type(field_type)
            template[field_name] = default_value
        
        return template
    
    def _get_default_value_for_type(self, field_type: str) -> Any:
        """Get default value for protobuf field type"""
        type_defaults = {
            'string': "",
            'int32': 0,
            'int64': 0,
            'uint32': 0,
            'uint64': 0,
            'float': 0.0,
            'double': 0.0,
            'bool': False,
            'bytes': "",
        }
        
        return type_defaults.get(field_type.lower(), {})  # Default to empty object for custom types
