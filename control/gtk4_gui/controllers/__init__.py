"""
Controllers package for desktop_app.py refactoring

Controllers handle specific aspects of the application:
- UIController: Window creation, navigation, layout
- ContentController: Tab content creation and management
- ActionController: Button clicks, user interactions

This extraction supports the 75% → 90% reduction targets.
"""

from .ui_controller import UIController
from .content_controller import ContentController
from .action_controller import ActionController

__all__ = ['UIController', 'ContentController', 'ActionController']
