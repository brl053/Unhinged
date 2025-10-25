
import logging; gui_logger = logging.getLogger(__name__)

"""
@llm-type control-system
@llm-legend schema_validator.py - system control component
@llm-key Core functionality for schema_validator
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token schema_validator: system control component
"""
"""
🔍 Schema Validator - Request Validation Engine

Validates requests against discovered service schemas.
Provides real-time validation and intelligent suggestions.

Features:
    pass
- JSON schema validation
- gRPC message type validation
- Real-time error highlighting
- Field suggestions and auto-completion
- Type checking and format validation
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple


class SchemaValidator:
    """
    Request schema validator for gRPC and HTTP services.
    
    Validates requests against discovered service schemas
    and provides intelligent suggestions and error reporting.
    """
    
    def __init__(self):
        self.service_schemas = {}
        self.validation_cache = {}
        
        gui_logger.debug(" Schema validator initialized", {"event_type": "scanning"})
    
    def update_service_schemas(self, network_services: Dict[str, Any]):
        """Update service schemas from network discovery"""
        self.service_schemas = {}
        
        for service_key, service_info in network_services.items():
            if 'proto_info' in service_info and service_info['proto_info']:
                proto_info = service_info['proto_info']
                if 'services' in proto_info:
                    for service in proto_info['services']:
                        service_name = service['name']
                        self.service_schemas[service_name] = {
                            'methods': service.get('methods', []),
                            'endpoint': service_info['endpoint'],
                            'source': 'reflection'
                        }
        
    
    def validate_request(self, service_name: str, method_name: str, request_body: str) -> Dict[str, Any]:
        """
        Validate a request against service schema.
        
        Args:
            service_name: Name of the service
            method_name: Name of the method
            request_body: JSON request body to validate
            
        Returns:
            Validation result with errors and suggestions
        """
        try:
            # Parse JSON
            try:
                request_data = json.loads(request_body) if request_body.strip() else {}
            except json.JSONDecodeError as e:
                return {
                    "valid": False,
                    "errors": [f"Invalid JSON: {str(e)}"],
                    "suggestions": ["Check JSON syntax and formatting"],
                    "error_type": "json_syntax"
                }
            
            # Get service schema
            if service_name not in self.service_schemas:
                return {
                    "valid": True,
                    "warnings": [f"No schema available for service: {service_name}"],
                    "suggestions": ["Schema validation skipped - service not in discovery"],
                    "error_type": "no_schema"
                }
            
            service_schema = self.service_schemas[service_name]
            
            # Find method schema
            method_schema = None
            for method in service_schema['methods']:
                if method['name'] == method_name:
                    method_schema = method
                    break
            
            if not method_schema:
                return {
                    "valid": True,
                    "warnings": [f"Method {method_name} not found in schema"],
                    "suggestions": [f"Available methods: {[m['name'] for m in service_schema['methods']]}"],
                    "error_type": "method_not_found"
                }
            
            # Validate against method schema
            validation_result = self._validate_against_method_schema(request_data, method_schema)
            
            return validation_result
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "suggestions": ["Check request format and try again"],
                "error_type": "validation_error"
            }
    
    def _validate_against_method_schema(self, request_data: Dict[str, Any], method_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate request data against method schema"""
        errors = []
        warnings = []
        suggestions = []
        
        request_type = method_schema.get('request_type', '')
        
        # Basic validation based on common patterns
        if 'Get' in method_schema['name']:
            # GET methods typically need an ID
            if 'id' not in request_data and 'user_id' not in request_data:
                warnings.append("GET methods typically require an 'id' field")
                suggestions.append("Add an 'id' or 'user_id' field to identify the resource")
        
        elif 'List' in method_schema['name']:
            # LIST methods typically have pagination
            if 'limit' not in request_data:
                suggestions.append("Consider adding 'limit' for pagination")
            if 'offset' not in request_data and 'page' not in request_data:
                suggestions.append("Consider adding 'offset' or 'page' for pagination")
        
        elif 'Create' in method_schema['name']:
            # CREATE methods typically need data
            if not request_data or len(request_data) == 0:
                errors.append("CREATE methods typically require data fields")
                suggestions.append("Add the data fields for the resource being created")
        
        elif 'Update' in method_schema['name']:
            # UPDATE methods typically need ID and data
            if 'id' not in request_data:
                errors.append("UPDATE methods typically require an 'id' field")
            if 'data' not in request_data and len(request_data) <= 1:
                warnings.append("UPDATE methods typically require data to update")
        
        elif 'Delete' in method_schema['name']:
            # DELETE methods typically need ID
            if 'id' not in request_data:
                errors.append("DELETE methods typically require an 'id' field")
        
        # Type validation for common fields
        for field, value in request_data.items():
            field_suggestions = self._validate_field_type(field, value)
            suggestions.extend(field_suggestions)
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions,
            "method_type": method_schema['name'],
            "request_type": request_type
        }
    
    def _validate_field_type(self, field_name: str, value: Any) -> List[str]:
        """Validate individual field types"""
        suggestions = []
        
        # Common field validations
        if field_name.endswith('_id') or field_name == 'id':
            if not isinstance(value, (str, int)):
                suggestions.append(f"Field '{field_name}' should be a string or number")
        
        elif field_name in ['email', 'email_address']:
            if isinstance(value, str) and '@' not in value:
                suggestions.append(f"Field '{field_name}' should be a valid email address")
        
        elif field_name in ['limit', 'offset', 'page', 'size']:
            if not isinstance(value, int) or value < 0:
                suggestions.append(f"Field '{field_name}' should be a positive integer")
        
        elif field_name.endswith('_at') or field_name.endswith('_time'):
            if isinstance(value, str) and not self._is_valid_timestamp(value):
                suggestions.append(f"Field '{field_name}' should be a valid timestamp (ISO 8601)")
        
        elif field_name in ['active', 'enabled', 'deleted', 'verified']:
            if not isinstance(value, bool):
                suggestions.append(f"Field '{field_name}' should be a boolean (true/false)")
        
        return suggestions
    
    def _is_valid_timestamp(self, timestamp_str: str) -> bool:
        """Check if string is a valid timestamp"""
        # Basic ISO 8601 pattern check
        iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z?$'
        return bool(re.match(iso_pattern, timestamp_str))
    
    def get_field_suggestions(self, service_name: str, method_name: str, partial_field: str = "") -> List[str]:
        """Get field suggestions for auto-completion"""
        suggestions = []
        
        if service_name not in self.service_schemas:
            return suggestions
        
        service_schema = self.service_schemas[service_name]
        
        # Find method
        method_schema = None
        for method in service_schema['methods']:
            if method['name'] == method_name:
                method_schema = method
                break
        
        if not method_schema:
            return suggestions
        
        # Generate suggestions based on method type
        method_type = method_schema['name']
        
        if 'Get' in method_type:
            suggestions.extend(['id', 'user_id', 'fields', 'include'])
        elif 'List' in method_type:
            suggestions.extend(['limit', 'offset', 'page', 'filter', 'sort_by', 'sort_order'])
        elif 'Create' in method_type:
            suggestions.extend(['name', 'data', 'metadata', 'tags'])
        elif 'Update' in method_type:
            suggestions.extend(['id', 'data', 'update_mask', 'merge'])
        elif 'Delete' in method_type:
            suggestions.extend(['id', 'force', 'cascade'])
        
        # Filter by partial field if provided
        if partial_field:
            suggestions = [s for s in suggestions if s.startswith(partial_field.lower())]
        
        return suggestions
    
    def get_template_for_method(self, service_name: str, method_name: str) -> Dict[str, Any]:
        """Get a smart template for a specific method"""
        if service_name not in self.service_schemas:
            return {}
        
        service_schema = self.service_schemas[service_name]
        
        # Find method
        method_schema = None
        for method in service_schema['methods']:
            if method['name'] == method_name:
                method_schema = method
                break
        
        if not method_schema:
            return {}
        
        # Generate template based on method type
        return self._generate_method_template(method_schema)
    
    def _generate_method_template(self, method_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a smart template for a method"""
        method_name = method_schema['name']
        request_type = method_schema.get('request_type', '')
        
        templates = {
            'Get': {
                'id': '12345',
                'fields': ['name', 'email', 'created_at']
            },
            'List': {
                'limit': 10,
                'offset': 0,
                'filter': {},
                'sort_by': 'created_at',
                'sort_order': 'desc'
            },
            'Create': {
                'name': 'Example Name',
                'email': 'user@example.com',
                'data': {},
                'metadata': {}
            },
            'Update': {
                'id': '12345',
                'data': {
                    'name': 'Updated Name'
                },
                'update_mask': ['name']
            },
            'Delete': {
                'id': '12345',
                'force': False
            }
        }
        
        # Find matching template
        for pattern, template in templates.items():
            if pattern in method_name:
                # Add method-specific comment
                template[f'// Generated for {request_type}'] = ''
                return template
        
        # Default template
        return {
            f'// Request for {request_type}': '',
            'data': {},
            'timestamp': '2023-01-01T00:00:00Z'
        }
