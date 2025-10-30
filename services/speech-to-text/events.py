#!/usr/bin/env python3
"""
Simple events logging module for speech-to-text service
"""

import logging
import sys


class ServiceLogger:
    """Simple service logger"""

    def __init__(self, service_name, version):
        self.service_name = service_name
        self.version = version

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(service_name)

    def info(self, message, metadata=None):
        """Log info message"""
        if metadata:
            self.logger.info(f"{message} - {metadata}")
        else:
            self.logger.info(message)

    def error(self, message, exception=None, metadata=None):
        """Log error message"""
        error_msg = message
        if exception:
            error_msg += f" - {str(exception)}"
        if metadata:
            error_msg += f" - {metadata}"
        self.logger.error(error_msg)

    def warning(self, message, metadata=None):
        """Log warning message"""
        if metadata:
            self.logger.warning(f"{message} - {metadata}")
        else:
            self.logger.warning(message)

    def debug(self, message, metadata=None):
        """Log debug message"""
        if metadata:
            self.logger.debug(f"{message} - {metadata}")
        else:
            self.logger.debug(message)

def create_service_logger(service_name, version):
    """Create a service logger instance"""
    return ServiceLogger(service_name, version)
