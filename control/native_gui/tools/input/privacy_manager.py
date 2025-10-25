
import logging; gui_logger = logging.getLogger(__name__)

"""
Privacy Manager for Input Capture
Provides privacy controls, data filtering, and secure storage for input monitoring.
"""

import hashlib
import json
import time
import re
from typing import Dict, List, Optional, Set, Callable
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
import threading


class PrivacyLevel(Enum):
    """Privacy levels for input capture"""
    FULL_LOGGING = "full"           # Log everything
    FILTERED = "filtered"           # Filter sensitive data
    ANONYMOUS = "anonymous"         # Hash/anonymize data
    STATISTICS_ONLY = "stats_only"  # Only statistics, no content
    DISABLED = "disabled"           # No logging


@dataclass
class PrivacyConfig:
    """Privacy configuration for input capture"""
    level: PrivacyLevel = PrivacyLevel.FILTERED
    
    # Content filtering
    filter_passwords: bool = True
    filter_emails: bool = False
    filter_urls: bool = False
    filter_numbers: bool = False
    filter_custom_patterns: List[str] = None
    
    # Application filtering
    blocked_applications: Set[str] = None
    allowed_applications: Set[str] = None
    
    # Data retention
    max_retention_days: int = 7
    auto_cleanup: bool = True
    
    # Encryption
    encrypt_storage: bool = True
    encryption_key: Optional[str] = None
    
    # Anonymization
    hash_usernames: bool = True
    hash_file_paths: bool = True
    replace_with_placeholders: bool = True


class PrivacyManager:
    """Manages privacy controls for input capture"""
    
    def __init__(self, config: Optional[PrivacyConfig] = None):
        self.config = config or PrivacyConfig()
        
        # Initialize default patterns
        if self.config.filter_custom_patterns is None:
            self.config.filter_custom_patterns = []
        
        if self.config.blocked_applications is None:
            self.config.blocked_applications = {
                'keepass', 'bitwarden', '1password', 'lastpass',  # Password managers
                'banking', 'paypal', 'venmo',  # Financial apps
                'signal', 'telegram', 'whatsapp'  # Secure messaging
            }
        
        # Compile regex patterns
        self.patterns = self._compile_patterns()
        
        # Active application tracking
        self.current_application = ""
        self.application_lock = threading.Lock()
        
        # Data filters
        self.content_filters: List[Callable[[str], str]] = []
        self._setup_content_filters()
        
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for content filtering"""
        patterns = {}
        
        if self.config.filter_passwords:
            # Common password field patterns
            patterns['password'] = re.compile(
                r'(?i)(password|passwd|pwd|pin|secret|key|token)[:=\s]*[^\s\n]{3,}',
                re.IGNORECASE
            )
        
        if self.config.filter_emails:
            patterns['email'] = re.compile(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            )
        
        if self.config.filter_urls:
            patterns['url'] = re.compile(
                r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
            )
        
        if self.config.filter_numbers:
            # Credit card, SSN, phone number patterns
            patterns['credit_card'] = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')
            patterns['ssn'] = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
            patterns['phone'] = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
        
        # Custom patterns
        for pattern in self.config.filter_custom_patterns:
            try:
                patterns[f'custom_{len(patterns)}'] = re.compile(pattern)
            except re.error as e:
                gui_logger.warn(f" Invalid regex pattern '{pattern}': {e}")
        
        return patterns
    
    def _setup_content_filters(self):
        """Setup content filtering functions"""
        if self.config.level == PrivacyLevel.FULL_LOGGING:
            return  # No filtering
        
        if self.config.level == PrivacyLevel.ANONYMOUS:
            self.content_filters.append(self._anonymize_content)
        
        if self.config.level in [PrivacyLevel.FILTERED, PrivacyLevel.ANONYMOUS]:
            self.content_filters.append(self._filter_sensitive_content)
        
        if self.config.replace_with_placeholders:
            self.content_filters.append(self._replace_with_placeholders)
    
    def should_capture_application(self, app_name: str) -> bool:
        """Check if application should be captured"""
        app_lower = app_name.lower()
        
        # Check blocked applications
        if any(blocked in app_lower for blocked in self.config.blocked_applications):
            return False
        
        # Check allowed applications (if specified)
        if self.config.allowed_applications:
            return any(allowed in app_lower for allowed in self.config.allowed_applications)
        
        return True
    
    def should_log_content(self) -> bool:
        """Check if content should be logged based on privacy level"""
        return self.config.level not in [PrivacyLevel.STATISTICS_ONLY, PrivacyLevel.DISABLED]
    
    def filter_keyboard_event(self, event_data: Dict) -> Optional[Dict]:
        """Filter keyboard event based on privacy settings"""
        if self.config.level == PrivacyLevel.DISABLED:
            return None
        
        # Check application filtering
        if not self.should_capture_application(self.current_application):
            return None
        
        # Create filtered copy
        filtered_event = event_data.copy()
        
        # Apply privacy level filtering
        if self.config.level == PrivacyLevel.STATISTICS_ONLY:
            # Remove all content, keep only metadata
            filtered_event = {
                'timestamp': event_data.get('timestamp'),
                'event_type': event_data.get('event_type'),
                'is_special': event_data.get('is_special', False)
            }
        else:
            # Filter content
            if 'char' in filtered_event and filtered_event['char']:
                filtered_event['char'] = self._filter_content(filtered_event['char'])
            
            if 'key' in filtered_event:
                filtered_event['key'] = self._filter_content(filtered_event['key'])
        
        return filtered_event
    
    def filter_mouse_event(self, event_data: Dict) -> Optional[Dict]:
        """Filter mouse event based on privacy settings"""
        if self.config.level == PrivacyLevel.DISABLED:
            return None
        
        # Check application filtering
        if not self.should_capture_application(self.current_application):
            return None
        
        # Mouse events are generally less sensitive
        filtered_event = event_data.copy()
        
        if self.config.level == PrivacyLevel.STATISTICS_ONLY:
            # Keep only basic event info
            filtered_event = {
                'timestamp': event_data.get('timestamp'),
                'event_type': event_data.get('event_type'),
                'button': event_data.get('button')
            }
        
        return filtered_event
    
    def _filter_content(self, content: str) -> str:
        """Apply content filters to text"""
        if not content or not self.should_log_content():
            return ""
        
        filtered_content = content
        
        # Apply all content filters
        for filter_func in self.content_filters:
            filtered_content = filter_func(filtered_content)
        
        return filtered_content
    
    def _filter_sensitive_content(self, content: str) -> str:
        """Filter sensitive content using regex patterns"""
        filtered = content
        
        for pattern_name, pattern in self.patterns.items():
            if pattern_name == 'password':
                filtered = pattern.sub('[PASSWORD]', filtered)
            elif pattern_name == 'email':
                filtered = pattern.sub('[EMAIL]', filtered)
            elif pattern_name == 'url':
                filtered = pattern.sub('[URL]', filtered)
            elif pattern_name == 'credit_card':
                filtered = pattern.sub('[CREDIT_CARD]', filtered)
            elif pattern_name == 'ssn':
                filtered = pattern.sub('[SSN]', filtered)
            elif pattern_name == 'phone':
                filtered = pattern.sub('[PHONE]', filtered)
            elif pattern_name.startswith('custom_'):
                filtered = pattern.sub('[FILTERED]', filtered)
        
        return filtered
    
    def _anonymize_content(self, content: str) -> str:
        """Anonymize content by hashing"""
        if not content:
            return content
        
        # Hash the content
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:8]
        return f"[HASH:{content_hash}]"
    
    def _replace_with_placeholders(self, content: str) -> str:
        """Replace content with placeholders"""
        if not content:
            return content
        
        if content.isalnum():
            return '*' * len(content)
        else:
            return '[FILTERED]'
    
    def set_current_application(self, app_name: str):
        """Set current active application"""
        with self.application_lock:
            self.current_application = app_name.lower()
    
    def get_current_application(self) -> str:
        """Get current active application"""
        with self.application_lock:
            return self.current_application
    
    def add_blocked_application(self, app_name: str):
        """Add application to blocked list"""
        self.config.blocked_applications.add(app_name.lower())
    
    def remove_blocked_application(self, app_name: str):
        """Remove application from blocked list"""
        self.config.blocked_applications.discard(app_name.lower())
    
    def add_custom_filter_pattern(self, pattern: str):
        """Add custom regex filter pattern"""
        try:
            # Test pattern compilation
            re.compile(pattern)
            self.config.filter_custom_patterns.append(pattern)
            
            # Recompile patterns
            self.patterns = self._compile_patterns()
            self._setup_content_filters()
            
        except re.error as e:
            gui_logger.error(f" Invalid regex pattern: {e}")
    
    def get_privacy_summary(self) -> Dict:
        """Get privacy configuration summary"""
        return {
            'privacy_level': self.config.level.value,
            'content_logging': self.should_log_content(),
            'blocked_applications': len(self.config.blocked_applications),
            'filter_patterns': len(self.patterns),
            'encryption_enabled': self.config.encrypt_storage,
            'retention_days': self.config.max_retention_days,
            'current_application': self.get_current_application()
        }
    
    def export_privacy_config(self, filename: str):
        """Export privacy configuration to file"""
        try:
            config_data = {
                'level': self.config.level.value,
                'filter_passwords': self.config.filter_passwords,
                'filter_emails': self.config.filter_emails,
                'filter_urls': self.config.filter_urls,
                'filter_numbers': self.config.filter_numbers,
                'filter_custom_patterns': self.config.filter_custom_patterns,
                'blocked_applications': list(self.config.blocked_applications),
                'max_retention_days': self.config.max_retention_days,
                'encrypt_storage': self.config.encrypt_storage,
                'timestamp': time.time()
            }
            
            with open(filename, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            
        except Exception as e:
            gui_logger.error(f" Failed to export privacy config: {e}")
    
    def import_privacy_config(self, filename: str):
        """Import privacy configuration from file"""
        try:
            with open(filename, 'r') as f:
                config_data = json.load(f)
            
            # Update configuration
            self.config.level = PrivacyLevel(config_data.get('level', 'filtered'))
            self.config.filter_passwords = config_data.get('filter_passwords', True)
            self.config.filter_emails = config_data.get('filter_emails', False)
            self.config.filter_urls = config_data.get('filter_urls', False)
            self.config.filter_numbers = config_data.get('filter_numbers', False)
            self.config.filter_custom_patterns = config_data.get('filter_custom_patterns', [])
            self.config.blocked_applications = set(config_data.get('blocked_applications', []))
            self.config.max_retention_days = config_data.get('max_retention_days', 7)
            self.config.encrypt_storage = config_data.get('encrypt_storage', True)
            
            # Recompile patterns and filters
            self.patterns = self._compile_patterns()
            self._setup_content_filters()
            
            
        except Exception as e:
            gui_logger.error(f" Failed to import privacy config: {e}")


# Test function
def test_privacy_manager():
    """Test privacy manager functionality"""
    
    try:
        # Test different privacy levels
        config = PrivacyConfig(level=PrivacyLevel.FILTERED)
        manager = PrivacyManager(config)
        
        # Test content filtering
        test_content = "My password is secret123 and email is user@example.com"
        filtered = manager._filter_content(test_content)
        
        # Test application filtering
        manager.set_current_application("keepass")
        should_capture = manager.should_capture_application("keepass")
        
        # Test event filtering
        keyboard_event = {
            'key': 'a',
            'char': 'a',
            'timestamp': time.time(),
            'event_type': 'press'
        }
        
        filtered_event = manager.filter_keyboard_event(keyboard_event)
        
        # Get privacy summary
        summary = manager.get_privacy_summary()
        
        gui_logger.info(" Privacy manager test completed", {"status": "success"})
        
    except Exception as e:
        gui_logger.error(f" Privacy manager test failed: {e}")


if __name__ == "__main__":
    test_privacy_manager()
