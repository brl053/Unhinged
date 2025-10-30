#!/usr/bin/env python3
"""
Simple event logging for chat service with sessions
Minimal implementation for production deployment
"""

import logging
import time
import json
from typing import Dict, Any, Optional

class ServiceLogger:
    """Simple service logger for production deployment"""
    
    def __init__(self, service_name: str, version: str):
        self.service_name = service_name
        self.version = version
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format=f'%(asctime)s - {service_name} - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(service_name)
    
    def info(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Log info message with optional structured data"""
        if data:
            log_message = f"{message} | {json.dumps(data, default=str)}"
        else:
            log_message = message
        self.logger.info(log_message)
    
    def error(self, message: str, exception: Optional[Exception] = None, data: Optional[Dict[str, Any]] = None):
        """Log error message with optional exception and data"""
        if exception:
            log_message = f"{message} | Exception: {str(exception)}"
        else:
            log_message = message
            
        if data:
            log_message += f" | {json.dumps(data, default=str)}"
            
        self.logger.error(log_message)
    
    def warning(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Log warning message with optional structured data"""
        if data:
            log_message = f"{message} | {json.dumps(data, default=str)}"
        else:
            log_message = message
        self.logger.warning(log_message)
    
    def debug(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Log debug message with optional structured data"""
        if data:
            log_message = f"{message} | {json.dumps(data, default=str)}"
        else:
            log_message = message
        self.logger.debug(log_message)

def create_service_logger(service_name: str, version: str) -> ServiceLogger:
    """Create service logger instance"""
    return ServiceLogger(service_name, version)
