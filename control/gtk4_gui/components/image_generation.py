#!/usr/bin/env python3
"""
Image Generation Components for GTK4 GUI

Provides components for sovereign image generation interface.
Integrates with the image generation service.

@llm-type component.image-generation
@llm-does GTK4 components for sovereign image generation interface
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

import logging
import threading
from typing import Any

from gi.repository import Adw, Gio, GLib, GObject, Gtk

from ..config import get_service_config
from .base import BaseComponent

# gRPC client imports
try:
    from unhinged_proto_clients import common_pb2, image_generation_pb2

    from libs.python.grpc_clients.client_factory import create_image_generation_client
    GRPC_AVAILABLE = True
except ImportError:
    GRPC_AVAILABLE = False
    print("⚠️ gRPC clients not available for image generation")

class ImageGenerationRequest(GObject.Object):
    """Data model for image generation requests."""

    __gtype_name__ = 'ImageGenerationRequest'

    def __init__(self, prompt: str = "", negative_prompt: str = "",
                 width: int = 1024, height: int = 1024,
                 steps: int = 25, guidance: float = 7.5, seed: int | None = None):
        super().__init__()
        self.prompt = prompt
        self.negative_prompt = negative_prompt
        self.width = width
        self.height = height
        self.steps = steps
        self.guidance = guidance
        self.seed = seed

class ImageGenerationPanel(BaseComponent):
    """
    Main image generation panel with prompt input and generation controls.
    """

    __gtype_name__ = 'ImageGenerationPanel'

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Service configuration
        self.service_config = get_service_config()
        self.grpc_address = "localhost:9094"  # Image generation gRPC service
        self.grpc_client = None

        # Generation state
        self.is_generating = False
        self.current_request = None

        # Initialize gRPC client
        self._initialize_grpc_client()

        self._build_ui()
        self._connect_signals()

    def _initialize_grpc_client(self):
        """Initialize gRPC client for image generation service."""
        if not GRPC_AVAILABLE:
            self.logger.warning("gRPC not available, image generation will be disabled")
            return

        try:
            self.grpc_client = create_image_generation_client(self.grpc_address)
            self.logger.info(f"gRPC client initialized for {self.grpc_address}")
        except Exception as e:
            self.logger.error(f"Failed to initialize gRPC client: {e}")
            self.grpc_client = None

    def _build_ui(self):
        """Build the image generation UI."""
        # Main container
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(12)
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(12)
        self.set_margin_end(12)

        # Header
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Sovereign Image Generation"))
        self.append(header)

        # Prompt input section
        prompt_group = Adw.PreferencesGroup()
        prompt_group.set_title("Generation Parameters")
        prompt_group.set_description("Configure your image generation")

        # Prompt text view
        self.prompt_row = Adw.EntryRow()
        self.prompt_row.set_title("Prompt")
        self.prompt_row.set_text("a rubber duck in a bathtub, photorealistic, 4k")
        prompt_group.add(self.prompt_row)

        # Negative prompt
        self.negative_prompt_row = Adw.EntryRow()
        self.negative_prompt_row.set_title("Negative Prompt")
        self.negative_prompt_row.set_text("blurry, low quality, distorted")
        prompt_group.add(self.negative_prompt_row)

        # Dimensions
        dimensions_row = Adw.ActionRow()
        dimensions_row.set_title("Dimensions")

        self.width_spin = Gtk.SpinButton()
        self.width_spin.set_range(256, 2048)
        self.width_spin.set_increments(64, 256)
        self.width_spin.set_value(1024)
        dimensions_row.add_suffix(self.width_spin)

        dimensions_row.add_suffix(Gtk.Label(label="×"))

        self.height_spin = Gtk.SpinButton()
        self.height_spin.set_range(256, 2048)
        self.height_spin.set_increments(64, 256)
        self.height_spin.set_value(1024)
        dimensions_row.add_suffix(self.height_spin)

        prompt_group.add(dimensions_row)

        # Steps and guidance
        steps_row = Adw.ActionRow()
        steps_row.set_title("Inference Steps")
        steps_row.set_subtitle("More steps = higher quality, slower generation")

        self.steps_spin = Gtk.SpinButton()
        self.steps_spin.set_range(1, 100)
        self.steps_spin.set_increments(1, 5)
        self.steps_spin.set_value(25)
        steps_row.add_suffix(self.steps_spin)

        prompt_group.add(steps_row)

        guidance_row = Adw.ActionRow()
        guidance_row.set_title("Guidance Scale")
        guidance_row.set_subtitle("How closely to follow the prompt")

        self.guidance_spin = Gtk.SpinButton()
        self.guidance_spin.set_range(1.0, 20.0)
        self.guidance_spin.set_increments(0.5, 1.0)
        self.guidance_spin.set_digits(1)
        self.guidance_spin.set_value(7.5)
        guidance_row.add_suffix(self.guidance_spin)

        prompt_group.add(guidance_row)

        # Seed (optional)
        seed_row = Adw.ActionRow()
        seed_row.set_title("Seed (Optional)")
        seed_row.set_subtitle("Leave empty for random seed")

        self.seed_entry = Gtk.Entry()
        self.seed_entry.set_placeholder_text("Random")
        seed_row.add_suffix(self.seed_entry)

        prompt_group.add(seed_row)

        self.append(prompt_group)

        # Generation controls
        controls_group = Adw.PreferencesGroup()
        controls_group.set_title("Generation")

        # Generate button
        self.generate_button = Gtk.Button()
        self.generate_button.set_label("🎨 Generate Image")
        self.generate_button.add_css_class("suggested-action")
        self.generate_button.set_hexpand(True)

        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_visible(False)
        self.progress_bar.set_text("Generating...")
        self.progress_bar.set_show_text(True)

        # Status label
        self.status_label = Gtk.Label()
        self.status_label.set_text("Ready to generate")
        self.status_label.add_css_class("dim-label")

        controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        controls_box.append(self.generate_button)
        controls_box.append(self.progress_bar)
        controls_box.append(self.status_label)

        controls_group.add(Adw.ActionRow(child=controls_box))
        self.append(controls_group)

        # Results section
        self.results_group = Adw.PreferencesGroup()
        self.results_group.set_title("Generated Images")
        self.results_group.set_visible(False)
        self.append(self.results_group)

    def _connect_signals(self):
        """Connect UI signals."""
        self.generate_button.connect("clicked", self._on_generate_clicked)

    def _on_generate_clicked(self, button):
        """Handle generate button click."""
        if self.is_generating:
            return

        # Create request
        request = ImageGenerationRequest(
            prompt=self.prompt_row.get_text(),
            negative_prompt=self.negative_prompt_row.get_text(),
            width=int(self.width_spin.get_value()),
            height=int(self.height_spin.get_value()),
            steps=int(self.steps_spin.get_value()),
            guidance=self.guidance_spin.get_value(),
            seed=int(self.seed_entry.get_text()) if self.seed_entry.get_text() else None
        )

        # Start generation
        self._start_generation(request)

    def _start_generation(self, request: ImageGenerationRequest):
        """Start image generation process."""
        self.is_generating = True
        self.current_request = request

        # Update UI
        self.generate_button.set_sensitive(False)
        self.progress_bar.set_visible(True)
        self.progress_bar.pulse()
        self.status_label.set_text("Connecting to image generation service...")

        # Start generation in background
        GLib.timeout_add(100, self._pulse_progress)

        # Make API request (in a real implementation, this would be async)
        GLib.idle_add(self._generate_image_async, request)

    def _pulse_progress(self):
        """Pulse progress bar while generating."""
        if self.is_generating:
            self.progress_bar.pulse()
            return True  # Continue pulsing
        return False  # Stop pulsing

    def _generate_image_async(self, request: ImageGenerationRequest):
        """Generate image asynchronously using gRPC streaming."""
        if not self.grpc_client:
            self._on_generation_error("gRPC client not available")
            return False

        def grpc_generation_thread():
            """Run gRPC generation in separate thread."""
            try:
                # Create gRPC request
                grpc_request = image_generation_pb2.GenerateImageRequest()
                grpc_request.prompt = request.prompt
                grpc_request.negative_prompt = request.negative_prompt
                grpc_request.width = request.width
                grpc_request.height = request.height
                grpc_request.num_inference_steps = request.steps
                grpc_request.guidance_scale = request.guidance
                if request.seed:
                    grpc_request.seed = request.seed
                grpc_request.batch_size = 1

                # Start streaming generation
                stream = self.grpc_client.GenerateImage(grpc_request)

                final_result = None
                for chunk in stream:
                    if chunk.type == common_pb2.CHUNK_TYPE_PROGRESS:
                        # Update progress on main thread
                        progress_data = dict(chunk.structured)
                        GLib.idle_add(self._update_generation_progress, progress_data)

                    elif chunk.type == common_pb2.CHUNK_TYPE_DATA and chunk.is_final:
                        # Final result
                        final_result = dict(chunk.structured)
                        break

                if final_result:
                    GLib.idle_add(self._on_generation_success, final_result)
                else:
                    GLib.idle_add(self._on_generation_error, "No result received")

            except Exception as e:
                GLib.idle_add(self._on_generation_error, str(e))

        # Start generation in background thread
        thread = threading.Thread(target=grpc_generation_thread)
        thread.daemon = True
        thread.start()

        return False  # Don't repeat

    def _update_generation_progress(self, progress_data: dict[str, Any]):
        """Update generation progress from gRPC stream."""
        progress_percent = progress_data.get("progress_percent", 0.0)
        status_message = progress_data.get("status_message", "Generating...")

        # Update progress bar
        self.progress_bar.set_fraction(progress_percent / 100.0)
        self.progress_bar.set_text(f"{progress_percent:.0f}%")

        # Update status
        self.status_label.set_text(status_message)

    def _on_generation_success(self, response: dict[str, Any]):
        """Handle successful generation."""
        self.is_generating = False

        # Update UI
        self.generate_button.set_sensitive(True)
        self.progress_bar.set_visible(False)

        generation_time = response.get('total_time', response.get('generation_time', 0))
        self.status_label.set_text(f"✅ Generated in {generation_time:.1f}s")

        # Show results
        self._display_results(response)

    def _on_generation_error(self, error_message: str):
        """Handle generation error."""
        self.is_generating = False

        # Update UI
        self.generate_button.set_sensitive(True)
        self.progress_bar.set_visible(False)
        self.status_label.set_text(f"❌ Error: {error_message}")

        self.logger.error(f"Image generation failed: {error_message}")

    def _display_results(self, response: dict[str, Any]):
        """Display generation results."""
        self.results_group.set_visible(True)

        # Clear previous results
        child = self.results_group.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.results_group.remove(child)
            child = next_child

        # Add new results
        for i, image_path in enumerate(response.get("images", [])):
            image_row = self._create_image_result_row(image_path, response, i)
            self.results_group.add(image_row)

    def _create_image_result_row(self, image_path: str, response: dict[str, Any], index: int) -> Adw.ActionRow:
        """Create a row for displaying an image result."""
        row = Adw.ActionRow()
        row.set_title(f"Generated Image {index + 1}")
        row.set_subtitle(f"Seed: {response.get('seed', 'Unknown')} • Time: {response.get('generation_time', 0):.1f}s")

        # Add thumbnail (placeholder for now)
        thumbnail = Gtk.Image()
        thumbnail.set_from_icon_name("image-x-generic")
        thumbnail.set_pixel_size(64)
        row.add_prefix(thumbnail)

        # Add action buttons
        open_button = Gtk.Button()
        open_button.set_icon_name("document-open")
        open_button.set_tooltip_text("Open image")
        open_button.connect("clicked", lambda b: self._open_image(image_path))
        row.add_suffix(open_button)

        save_button = Gtk.Button()
        save_button.set_icon_name("document-save-as")
        save_button.set_tooltip_text("Save as...")
        save_button.connect("clicked", lambda b: self._save_image_as(image_path))
        row.add_suffix(save_button)

        return row

    def _open_image(self, image_path: str):
        """Open image in default viewer."""
        try:
            Gio.AppInfo.launch_default_for_uri(f"file://{image_path}", None)
        except Exception as e:
            self.logger.error(f"Failed to open image: {e}")

    def _save_image_as(self, image_path: str):
        """Save image with file chooser."""
        # This would open a file chooser dialog
        self.logger.info(f"Save as requested for: {image_path}")

class ImageGenerationView(Gtk.ScrolledWindow):
    """
    Scrollable view containing the image generation panel.
    """

    __gtype_name__ = 'ImageGenerationView'

    def __init__(self):
        super().__init__()

        # Configure scrolled window
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.set_vexpand(True)

        # Add image generation panel
        self.panel = ImageGenerationPanel()
        self.set_child(self.panel)

    def get_panel(self) -> ImageGenerationPanel:
        """Get the image generation panel."""
        return self.panel
