"""
🌐 HTTP Client - Direct Python Implementation

Handles HTTP requests without bridge overhead.
Direct Python requests for maximum performance.

Features:
- HTTP method support (GET, POST, PUT, DELETE, etc.)
- Header management
- Request/response handling
- Error management
"""

import requests
import time
import json
from typing import Dict, Any, Optional


class HTTPClient:
    """
    Direct HTTP client implementation.
    
    No HTTP bridge - direct requests calls for instant response.
    """
    
    def __init__(self):
        self.session = requests.Session()
        print("🌐 HTTP client initialized")
    
    def send_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send HTTP request directly.
        
        Args:
            request_data: Request configuration
            
        Returns:
            Response data with status and timing
        """
        try:
            # Extract request details
            method = request_data.get("method", "GET").upper()
            url = request_data.get("url", "")
            headers = request_data.get("headers", {})
            body = request_data.get("body", "")
            
            if not url:
                return {
                    "success": False,
                    "error": "URL is required",
                    "status": 0,
                    "duration": 0
                }
            
            # Prepare request data
            kwargs = {
                "headers": headers,
                "timeout": 30
            }
            
            # Add body for methods that support it
            if method in ["POST", "PUT", "PATCH"] and body:
                if isinstance(body, dict):
                    kwargs["json"] = body
                else:
                    kwargs["data"] = body
            
            # Send request and measure time
            start_time = time.time()
            response = self.session.request(method, url, **kwargs)
            duration = int((time.time() - start_time) * 1000)  # Convert to ms
            
            # Parse response body
            try:
                if response.headers.get("content-type", "").startswith("application/json"):
                    response_body = response.json()
                else:
                    response_body = response.text
            except:
                response_body = response.text
            
            return {
                "success": True,
                "status": response.status_code,
                "headers": dict(response.headers),
                "body": response_body,
                "duration": duration,
                "method": method,
                "url": url
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"HTTP request failed: {str(e)}",
                "status": 0,
                "duration": 0
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "status": 0,
                "duration": 0
            }
