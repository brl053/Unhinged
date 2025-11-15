"""
Design system CSS loading and theme management.

Centralizes all CSS and theme configuration for the Unhinged desktop application.
"""

import logging
from pathlib import Path

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Adw, Gtk

logger = logging.getLogger(__name__)


def load_design_system_css(app: Gtk.Application) -> None:
    """Load design system CSS and apply theme.

    Args:
        app: GTK Application instance
    """
    css_provider = Gtk.CssProvider()

    # Define CSS for design system
    css_content = """
    /* Unhinged Design System */

    window {
        background-color: @view_bg_color;
    }

    .title-1 {
        font-size: 32px;
        font-weight: bold;
    }

    .title-2 {
        font-size: 24px;
        font-weight: bold;
    }

    .title-3 {
        font-size: 18px;
        font-weight: bold;
    }

    .body-large {
        font-size: 16px;
    }

    .body-medium {
        font-size: 14px;
    }

    .body-small {
        font-size: 12px;
    }

    .status-success {
        color: @success_color;
    }

    .status-warning {
        color: @warning_color;
    }

    .status-error {
        color: @error_color;
    }

    .status-info {
        color: @info_color;
    }

    .card {
        border-radius: 8px;
        background-color: @card_bg_color;
        padding: 12px;
    }

    .button-primary {
        background-color: @accent_color;
        color: white;
    }

    .button-secondary {
        background-color: @secondary_color;
    }

    .button-destructive {
        background-color: @destructive_color;
    }

    .monospace {
        font-family: "Monospace";
        font-size: 11px;
    }
    """

    css_provider.load_from_data(css_content.encode())

    # Apply CSS to application
    Gtk.StyleContext.add_provider_for_display(
        Adw.StyleManager.get_default().get_display(),
        css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    logger.debug("Design system CSS loaded")

