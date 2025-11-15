#!/usr/bin/env python3

"""
Complete GTK4 Component Example using Design System
Demonstrates how to create a GTK4 component that uses the generated design tokens.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from pathlib import Path

from gi.repository import Adw, Gtk


class DesignSystemExample(Adw.ApplicationWindow):
    """Example GTK4 window showcasing design system usage"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Design System Example")
        self.set_default_size(800, 600)

        # Load design system CSS
        self._load_design_system_css()

        # Create UI
        self._create_ui()

    def _load_design_system_css(self):
        """Load the generated design system CSS files"""
        css_provider = Gtk.CssProvider()

        # Path to generated CSS files
        project_root = Path(__file__).parent.parent.parent.parent
        css_dir = project_root / "generated" / "design_system" / "gtk4"

        # Load CSS files in correct order
        css_files = [
            "design-tokens.css",  # Base semantic tokens
            "theme-light.css",  # Light theme (default)
            "components.css",  # Component patterns
        ]

        combined_css = ""
        for css_file in css_files:
            css_path = css_dir / css_file
            if css_path.exists():
                combined_css += css_path.read_text() + "\n"
                print(f"✅ Loaded: {css_file}")
            else:
                print(f"⚠️  Missing: {css_file}")

        # Additional component-specific CSS using design tokens
        component_css = """
        /* Example component using design system tokens */
        .example-card {
            background-color: var(--color-surface-elevated);
            border: var(--border-thin) solid var(--color-border-subtle);
            border-radius: var(--radius-md);
            padding: var(--spacing-sp-4);
            margin: var(--spacing-sp-3);
            box-shadow: var(--elevation-2);
        }

        .example-card:hover {
            box-shadow: var(--elevation-3);
        }

        .example-title {
            font-family: var(--font-family-prose);
            font-size: var(--font-size-heading);
            font-weight: var(--font-weight-medium);
            color: var(--color-text-primary);
            margin-bottom: var(--spacing-sp-3);
        }

        .example-body {
            font-family: var(--font-family-prose);
            font-size: var(--font-size-body);
            color: var(--color-text-secondary);
            line-height: var(--line-height-body);
        }

        .example-button-primary {
            background-color: var(--color-action-primary);
            color: var(--color-text-inverse);
            border: var(--border-thin) solid var(--color-action-primary);
            border-radius: var(--radius-md);
            padding: var(--spacing-sp-2) var(--spacing-sp-4);
            font-family: var(--font-family-prose);
            font-size: var(--font-size-body);
            font-weight: var(--font-weight-medium);
        }

        .example-button-primary:hover {
            box-shadow: var(--elevation-1);
        }

        .example-button-secondary {
            background-color: var(--color-action-secondary);
            color: var(--color-text-inverse);
            border: var(--border-thin) solid var(--color-action-secondary);
            border-radius: var(--radius-md);
            padding: var(--spacing-sp-2) var(--spacing-sp-4);
            font-family: var(--font-family-prose);
            font-size: var(--font-size-body);
            font-weight: var(--font-weight-medium);
        }

        .example-input {
            background-color: var(--color-surface-default);
            color: var(--color-text-primary);
            border: var(--border-thin) solid var(--color-border-default);
            border-radius: var(--radius-sm);
            padding: var(--spacing-sp-2) var(--spacing-sp-3);
            font-family: var(--font-family-prose);
            font-size: var(--font-size-body);
        }

        .example-input:focus {
            border-width: var(--border-medium);
            border-color: var(--color-interactive-focus);
        }

        .theme-switcher {
            padding: var(--spacing-sp-2);
            margin: var(--spacing-sp-2);
        }
        """

        combined_css += component_css

        try:
            css_provider.load_from_data(combined_css.encode())
            Gtk.StyleContext.add_provider_for_display(
                self.get_display(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )
            print("✅ Design system CSS loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load CSS: {e}")

    def _create_ui(self):
        """Create the example UI"""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_content(main_box)

        # Header with theme switcher
        header = self._create_header()
        main_box.append(header)

        # Scrolled content area
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        main_box.append(scrolled)

        # Content container
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content_box.set_margin_start(20)
        content_box.set_margin_end(20)
        content_box.set_margin_top(20)
        content_box.set_margin_bottom(20)
        scrolled.set_child(content_box)

        # Add example components
        content_box.append(self._create_typography_examples())
        content_box.append(self._create_button_examples())
        content_box.append(self._create_form_examples())
        content_box.append(self._create_card_examples())

    def _create_header(self):
        """Create header with theme switcher"""
        header_bar = Adw.HeaderBar()
        header_bar.set_title_widget(Gtk.Label(label="Design System Example"))
        header_bar.add_css_class("theme-switcher")

        # Theme switcher button
        theme_button = Gtk.Button(label="Toggle Dark Theme")
        theme_button.connect("clicked", self._on_theme_toggle)
        header_bar.pack_end(theme_button)

        return header_bar

    def _create_typography_examples(self):
        """Create typography examples"""
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        card.add_css_class("example-card")

        title = Gtk.Label(label="Typography Examples")
        title.add_css_class("example-title")
        title.set_halign(Gtk.Align.START)
        card.append(title)

        # Different text sizes
        display_text = Gtk.Label(label="Display Text (Large)")
        display_text.set_markup(
            '<span font_size="x-large" weight="bold">Display Text (Large)</span>'
        )
        display_text.set_halign(Gtk.Align.START)
        card.append(display_text)

        heading_text = Gtk.Label(label="Heading Text (Medium)")
        heading_text.set_markup(
            '<span font_size="large" weight="medium">Heading Text (Medium)</span>'
        )
        heading_text.set_halign(Gtk.Align.START)
        card.append(heading_text)

        body_text = Gtk.Label(label="Body text for regular content and paragraphs.")
        body_text.add_css_class("example-body")
        body_text.set_halign(Gtk.Align.START)
        card.append(body_text)

        caption_text = Gtk.Label(label="Caption text for annotations and metadata")
        caption_text.set_markup(
            '<span font_size="small">Caption text for annotations and metadata</span>'
        )
        caption_text.set_halign(Gtk.Align.START)
        card.append(caption_text)

        return card

    def _create_button_examples(self):
        """Create button examples"""
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        card.add_css_class("example-card")

        title = Gtk.Label(label="Button Examples")
        title.add_css_class("example-title")
        title.set_halign(Gtk.Align.START)
        card.append(title)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        primary_btn = Gtk.Button(label="Primary Action")
        primary_btn.add_css_class("example-button-primary")
        button_box.append(primary_btn)

        secondary_btn = Gtk.Button(label="Secondary Action")
        secondary_btn.add_css_class("example-button-secondary")
        button_box.append(secondary_btn)

        disabled_btn = Gtk.Button(label="Disabled")
        disabled_btn.set_sensitive(False)
        button_box.append(disabled_btn)

        card.append(button_box)
        return card

    def _create_form_examples(self):
        """Create form examples"""
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        card.add_css_class("example-card")

        title = Gtk.Label(label="Form Examples")
        title.add_css_class("example-title")
        title.set_halign(Gtk.Align.START)
        card.append(title)

        # Text input
        entry = Gtk.Entry()
        entry.set_placeholder_text("Enter some text...")
        entry.add_css_class("example-input")
        card.append(entry)

        # Switch
        switch_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        switch_label = Gtk.Label(label="Enable notifications")
        switch = Gtk.Switch()
        switch_box.append(switch_label)
        switch_box.append(switch)
        card.append(switch_box)

        return card

    def _create_card_examples(self):
        """Create card examples"""
        main_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_card.add_css_class("example-card")

        title = Gtk.Label(label="Card Examples")
        title.add_css_class("example-title")
        title.set_halign(Gtk.Align.START)
        main_card.append(title)

        # Nested cards
        for i in range(3):
            nested_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            nested_card.add_css_class("example-card")

            card_title = Gtk.Label(label=f"Card {i + 1}")
            card_title.add_css_class("example-title")
            card_title.set_halign(Gtk.Align.START)
            nested_card.append(card_title)

            card_body = Gtk.Label(
                label="This is an example card using design system tokens for consistent styling."
            )
            card_body.add_css_class("example-body")
            card_body.set_wrap(True)
            card_body.set_halign(Gtk.Align.START)
            nested_card.append(card_body)

            main_card.append(nested_card)

        return main_card

    def _on_theme_toggle(self, button):
        """Toggle between light and dark themes"""
        current_theme = self.get_root().get_data("current_theme") or "light"
        new_theme = "dark" if current_theme == "light" else "light"

        # Apply theme by setting data attribute
        self.get_root().set_data("current_theme", new_theme)

        # Update button text
        button.set_label(f"Switch to {'Light' if new_theme == 'dark' else 'Dark'} Theme")

        print(f"🎨 Switched to {new_theme} theme")


class DesignSystemApp(Adw.Application):
    """Example application"""

    def __init__(self):
        super().__init__(application_id="com.unhinged.design_system_example")
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        """Application activation"""
        window = DesignSystemExample(application=app)
        window.present()


if __name__ == "__main__":
    app = DesignSystemApp()
    app.run()
