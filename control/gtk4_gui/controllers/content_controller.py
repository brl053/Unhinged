"""
Content Controller - Handles all tab content creation

Extracted from desktop_app.py to achieve 75% reduction target.
Manages main content, welcome sections, development tools, and logs.
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')



class ContentController:
    """Controller for tab content creation and management"""

    def __init__(self, app):
        """Initialize content controller with app reference"""
        self.app = app
        self.project_root = app.project_root

    # Main tab content removed - functionality migrated to Status tab
    # All helper methods (create_welcome_section, create_control_section, etc.) removed
    # Platform controls now available in enhanced Status tab
