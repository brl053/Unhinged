"""
Exception hierarchy for Unhinged Desktop GUI

This module defines a clear error hierarchy that separates different types of
failures and provides meaningful error messages for users and developers.
"""

from typing import Optional, Dict, Any


class UnhingedError(Exception):
    """Base exception for all Unhinged application errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.details:
            detail_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({detail_str})"
        return self.message


class ConfigurationError(UnhingedError):
    """Raised when there's a configuration problem"""
    pass


class ServiceError(UnhingedError):
    """Base class for service-related errors"""
    
    def __init__(self, service_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        self.service_name = service_name
        super().__init__(f"{service_name}: {message}", details)


class ServiceUnavailableError(ServiceError):
    """Raised when a required service is not available"""
    
    def __init__(self, service_name: str, endpoint: str, details: Optional[Dict[str, Any]] = None):
        self.endpoint = endpoint
        super().__init__(
            service_name, 
            f"Service unavailable at {endpoint}",
            details
        )


class ServiceTimeoutError(ServiceError):
    """Raised when a service call times out"""
    
    def __init__(self, service_name: str, timeout_seconds: float, details: Optional[Dict[str, Any]] = None):
        self.timeout_seconds = timeout_seconds
        super().__init__(
            service_name,
            f"Service call timed out after {timeout_seconds}s",
            details
        )


class ServiceResponseError(ServiceError):
    """Raised when a service returns an error response"""
    
    def __init__(self, service_name: str, status_code: Optional[str] = None, 
                 response_message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.status_code = status_code
        self.response_message = response_message
        
        message_parts = []
        if status_code:
            message_parts.append(f"Status: {status_code}")
        if response_message:
            message_parts.append(f"Message: {response_message}")
        
        message = " - ".join(message_parts) if message_parts else "Service returned an error"
        super().__init__(service_name, message, details)


class AudioError(UnhingedError):
    """Base class for audio-related errors"""
    pass


class AudioRecordingError(AudioError):
    """Raised when audio recording fails"""
    
    def __init__(self, message: str, device: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.device = device
        if device:
            message = f"Recording failed on device '{device}': {message}"
        super().__init__(message, details)


class AudioTranscriptionError(AudioError):
    """Raised when audio transcription fails"""
    
    def __init__(self, message: str, file_path: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.file_path = file_path
        if file_path:
            message = f"Transcription failed for '{file_path}': {message}"
        super().__init__(message, details)


class AudioFileSizeError(AudioError):
    """Raised when audio file is too large or too small"""
    
    def __init__(self, file_size: int, max_size: Optional[int] = None, min_size: Optional[int] = None):
        self.file_size = file_size
        self.max_size = max_size
        self.min_size = min_size
        
        if max_size and file_size > max_size:
            message = f"Audio file too large: {file_size} bytes exceeds {max_size} bytes limit"
        elif min_size and file_size < min_size:
            message = f"Audio file too small: {file_size} bytes is below {min_size} bytes minimum"
        else:
            message = f"Invalid audio file size: {file_size} bytes"
        
        super().__init__(message, {
            'file_size': file_size,
            'max_size': max_size,
            'min_size': min_size
        })


class UIError(UnhingedError):
    """Base class for UI-related errors"""
    pass


class ComponentNotFoundError(UIError):
    """Raised when a required UI component is not found"""
    
    def __init__(self, component_name: str, details: Optional[Dict[str, Any]] = None):
        self.component_name = component_name
        super().__init__(f"UI component not found: {component_name}", details)


class UserInputError(UnhingedError):
    """Raised when user input is invalid"""
    
    def __init__(self, field_name: str, value: Any, expected: str, details: Optional[Dict[str, Any]] = None):
        self.field_name = field_name
        self.value = value
        self.expected = expected
        
        message = f"Invalid {field_name}: got '{value}', expected {expected}"
        super().__init__(message, details)


class NetworkError(UnhingedError):
    """Base class for network-related errors"""
    pass


class ConnectionError(NetworkError):
    """Raised when network connection fails"""
    
    def __init__(self, endpoint: str, reason: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.endpoint = endpoint
        self.reason = reason
        
        message = f"Connection failed to {endpoint}"
        if reason:
            message += f": {reason}"
        
        super().__init__(message, details)


def handle_grpc_error(error: Exception, service_name: str) -> ServiceError:
    """Convert gRPC errors to our error hierarchy
    
    Args:
        error: The original gRPC error
        service_name: Name of the service that failed
        
    Returns:
        Appropriate ServiceError subclass
    """
    error_str = str(error)
    
    # Handle common gRPC error patterns
    if "UNAVAILABLE" in error_str or "failed to connect" in error_str.lower():
        return ServiceUnavailableError(service_name, "unknown", {'original_error': error_str})
    
    elif "DEADLINE_EXCEEDED" in error_str or "timeout" in error_str.lower():
        return ServiceTimeoutError(service_name, 0, {'original_error': error_str})
    
    elif "RESOURCE_EXHAUSTED" in error_str:
        # Extract size information if available
        details = {'original_error': error_str}
        if "larger than max" in error_str:
            import re
            match = re.search(r'(\d+) vs\. (\d+)', error_str)
            if match:
                details['received_size'] = int(match.group(1))
                details['max_size'] = int(match.group(2))
        
        return ServiceResponseError(service_name, "RESOURCE_EXHAUSTED", "Message too large", details)
    
    else:
        # Generic service error
        return ServiceResponseError(service_name, "UNKNOWN", error_str, {'original_error': error_str})


def get_user_friendly_message(error: Exception) -> str:
    """Get a user-friendly error message
    
    Args:
        error: The exception to convert
        
    Returns:
        User-friendly error message
    """
    if isinstance(error, ServiceUnavailableError):
        return f"The {error.service_name} service is not available. Please check that all services are running."
    
    elif isinstance(error, ServiceTimeoutError):
        return f"The {error.service_name} service is taking too long to respond. Please try again."
    
    elif isinstance(error, AudioFileSizeError):
        if error.max_size and error.file_size > error.max_size:
            max_mb = error.max_size / (1024 * 1024)
            return f"Audio file is too large. Maximum size is {max_mb:.1f}MB. Try recording shorter audio."
        else:
            return "Audio file is invalid. Please try recording again."
    
    elif isinstance(error, AudioRecordingError):
        return f"Recording failed: {error.message}. Please check your microphone and try again."
    
    elif isinstance(error, AudioTranscriptionError):
        return f"Transcription failed: {error.message}. Please try recording again."
    
    elif isinstance(error, ConfigurationError):
        return f"Configuration error: {error.message}. Please check your settings."
    
    elif isinstance(error, UserInputError):
        return f"Invalid input: {error.message}"
    
    elif isinstance(error, UnhingedError):
        return error.message
    
    else:
        # Generic error
        return f"An unexpected error occurred: {str(error)}"
