"""
Controllers package for desktop_app.py refactoring

Controllers handle specific aspects of the application:
- UIController: Window creation, navigation, layout
- ContentController: Tab content creation and management
- ActionController: Button clicks, user interactions

This extraction supports the 75% → 90% reduction targets.
"""

try:
    from .action_controller import ActionController
    from .content_controller import ContentController
    from .ui_controller import UIController
except ImportError:
    # Fallback for when running as script
    from action_controller import ActionController
    from content_controller import ContentController
    from ui_controller import UIController

__all__ = ["UIController", "ContentController", "ActionController"]
