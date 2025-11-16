from __future__ import annotations

from typing import TYPE_CHECKING

from gi.repository import GLib, Gtk

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from .chatroom_view import ChatroomView


class ChatImageHandler:
    """Handle /image command and image display for ChatroomView."""

    def __init__(self, view: ChatroomView) -> None:
        self.view = view

    def handle_slash_image_command(self, prompt: str):
        """Handle /image command for GPU-accelerated image generation"""
        thinking_box = None
        try:
            # Add user command to chat
            self.view._add_chat_message("You", f"/image {prompt}", "user")

            # Add thinking indicator
            thinking_box = self.view._add_thinking_indicator()

            # Submit to thread pool for image generation
            import sys
            from pathlib import Path as PathlibPath

            project_root = PathlibPath(__file__).parent.parent.parent

            # Add project root to path for proper imports
            sys.path.insert(0, str(project_root))

            from libs.services import ImageGenerationService

            # Run image generation in background thread
            def generate_image_thread():
                try:
                    service = ImageGenerationService()
                    result = service.generate_image(
                        prompt=prompt,
                        num_inference_steps=20,  # Fast generation
                        guidance_scale=7.5,
                        height=512,
                        width=512,
                    )

                    # Update UI on main thread
                    GLib.idle_add(self._display_generated_image, thinking_box, result, prompt)

                except Exception as e:
                    print(f"❌ Image generation error: {e}")
                    GLib.idle_add(self.view._add_error_message, f"Image generation failed: {e}")

            # Submit to thread pool
            import threading

            thread = threading.Thread(target=generate_image_thread, daemon=True)
            thread.start()

        except Exception as e:
            print(f"❌ /image command error: {e}")
            # Remove thinking indicator if it was created
            if thinking_box and thinking_box.get_parent():
                self.view._messages_container.remove(thinking_box)
            self.view._add_error_message(f"Command failed: {e}")

    def _display_generated_image(self, thinking_box, result, prompt):
        """Display generated image in chat using GeneratedArtifactWidget"""
        try:
            # Remove thinking indicator
            if thinking_box and thinking_box.get_parent():
                self.view._messages_container.remove(thinking_box)

            # Import the widget
            from ..components import GeneratedArtifactWidget

            # Create artifact widget
            image_path = result.get("image_path", "")
            generation_time = result.get("generation_time", 0)

            artifact_widget = GeneratedArtifactWidget(
                artifact_type="image",
                artifact_path=image_path,
                artifact_title=f"Generated Image ({generation_time:.1f}s)",
                artifact_metadata={
                    "prompt": prompt,
                    "generation_time": generation_time,
                    "model": result.get("model", "unknown"),
                    "device": result.get("device", "unknown"),
                    "steps": result.get("num_inference_steps", 20),
                },
            )

            # Add widget to chat
            if self.view._messages_container:
                self.view._messages_container.append(artifact_widget.get_widget())
                self.view._scroll_to_bottom()

            # Log generation
            if hasattr(self.view.app, "session_logger") and self.view.app.session_logger:
                self.view.app.session_logger.log_gui_event(
                    "IMAGE_GENERATED",
                    f"Prompt: {prompt[:50]}... | Time: {generation_time:.1f}s | Path: {image_path}",
                )

            # Show toast
            if hasattr(self.view.app, "show_toast"):
                self.view.app.show_toast(f"✅ Image generated in {generation_time:.1f}s")

        except Exception as e:
            print(f"❌ Display generated image error: {e}")
            self.view._add_error_message(f"Failed to display image: {e}")

    def _add_image_generation_indicator(self, prompt):
        """Add image generation progress indicator to chat"""
        try:
            # Create thinking indicator container
            thinking_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            thinking_container.add_css_class("message-container")
            thinking_container.add_css_class("assistant-message")
            thinking_container.set_margin_top(8)
            thinking_container.set_margin_bottom(8)
            thinking_container.set_margin_start(12)
            thinking_container.set_margin_end(12)

            # Add image generation icon
            icon = Gtk.Image.new_from_icon_name("image-x-generic-symbolic")
            icon.set_icon_size(Gtk.IconSize.LARGE)
            thinking_container.append(icon)

            # Add status label
            status_label = Gtk.Label()
            status_label.set_markup(f"<b>Generating image...</b>\nPrompt: {prompt[:50]}...")
            status_label.set_halign(Gtk.Align.START)
            status_label.set_valign(Gtk.Align.CENTER)
            thinking_container.append(status_label)

            # Add progress bar
            progress_bar = Gtk.ProgressBar()
            progress_bar.set_pulse_step(0.1)
            progress_bar.set_show_text(True)
            progress_bar.set_text("Initializing...")
            progress_bar.set_hexpand(True)
            thinking_container.append(progress_bar)

            # Store progress bar reference for updates
            thinking_container.progress_bar = progress_bar
            thinking_container.status_label = status_label

            # Add to messages container
            self.view._messages_container.append(thinking_container)
            self.view._scroll_to_bottom()

            return thinking_container

        except Exception as e:
            print(f" Add image generation indicator error: {e}")
            return None

    def _update_image_progress(self, thinking_box, progress_data):
        """Update image generation progress"""
        try:
            if thinking_box and hasattr(thinking_box, "progress_bar"):
                progress = progress_data.get("progress", 0)
                step = progress_data.get("step", 0)
                total_steps = progress_data.get("total_steps", 25)

                thinking_box.progress_bar.set_fraction(progress)
                thinking_box.progress_bar.set_text(f"Step {step}/{total_steps} ({int(progress * 100)}%)")

        except Exception as e:
            print(f" Update image progress error: {e}")

    def _display_generated_images(self, thinking_box, result, original_message):
        """Display generated images in chat interface"""
        try:
            # Remove thinking indicator
            if thinking_box and thinking_box.get_parent():
                self.view._messages_container.remove(thinking_box)

            # Create image message container
            image_container = self._create_image_message_container(result, original_message)

            # Add to chat
            self.view._messages_container.append(image_container)

            # Scroll to bottom
            self.view._scroll_to_bottom()

        except Exception as e:
            print(f" Display images error: {e}")

    def _create_image_message_container(self, result, original_message):
        """Create container for generated images"""
        try:
            container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            container.add_css_class("message-container")
            container.add_css_class("assistant-message")
            container.set_margin_top(8)
            container.set_margin_bottom(8)
            container.set_margin_start(12)
            container.set_margin_end(12)

            # Add generation info
            info_label = Gtk.Label()
            info_label.set_markup(f"<b>Generated Images</b> (Prompt: {original_message[:50]}...)")
            info_label.set_halign(Gtk.Align.START)
            container.append(info_label)

            # Add images
            images_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            images_box.set_homogeneous(True)

            for image_path in result.get("images", []):
                if self._image_path_exists(image_path):
                    image_widget = self._create_image_widget(image_path)
                    images_box.append(image_widget)

            container.append(images_box)

            # Add metadata
            metadata_label = Gtk.Label()
            generation_time = result.get("generation_time", 0)
            seed = result.get("seed", "Unknown")
            metadata_label.set_markup(f"<small>Generated in {generation_time:.1f}s  Seed: {seed}</small>")
            metadata_label.add_css_class("dim-label")
            metadata_label.set_halign(Gtk.Align.START)
            container.append(metadata_label)

            return container

        except Exception as e:
            print(f" Create image message container error: {e}")
            return Gtk.Label(label="Error displaying generated images")

    def _create_image_widget(self, image_path):
        """Create image widget with progressive loading and memory management"""
        try:
            # Check memory usage for progressive loading decision
            memory_threshold = 75.0  # Switch to thumbnails above 75% memory usage

            try:
                import psutil

                memory_percent = psutil.virtual_memory().percent
                use_thumbnail = memory_percent > memory_threshold
            except ImportError:
                use_thumbnail = False  # Default to full images if psutil not available

            if use_thumbnail:
                return self._create_thumbnail_widget(image_path)
            else:
                return self._create_full_image_widget(image_path)

        except Exception as e:
            print(f" Create image widget error: {e}")
            return Gtk.Label(label="Error loading image")

    def _create_full_image_widget(self, image_path):
        """Create full-size image widget"""
        try:
            # Create image widget
            image = Gtk.Picture()
            image.set_filename(image_path)
            image.set_size_request(256, 256)
            image.set_content_fit(Gtk.ContentFit.COVER)
            image.add_css_class("generated-image")

            # Make it clickable for full-size view
            click_controller = Gtk.GestureClick()
            click_controller.connect(
                "pressed",
                lambda gesture, n_press, x, y: self._show_full_image(image_path),
            )
            image.add_controller(click_controller)

            return image

        except Exception as e:
            print(f" Create full image widget error: {e}")
            return Gtk.Label(label="Error loading full image")

    def _create_thumbnail_widget(self, image_path):
        """Create thumbnail widget for memory-constrained situations"""
        try:
            # Create container for thumbnail with load button
            container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            container.set_size_request(256, 256)
            container.add_css_class("generated-image-thumbnail")

            # Create thumbnail placeholder
            thumbnail = Gtk.Image()
            thumbnail.set_from_icon_name("image-x-generic-symbolic")
            thumbnail.set_pixel_size(128)
            thumbnail.add_css_class("thumbnail-placeholder")
            container.append(thumbnail)

            # Add load button
            load_button = Gtk.Button()
            load_button.set_label("Load Image")
            load_button.add_css_class("suggested-action")
            load_button.connect("clicked", lambda btn: self._load_full_image(container, image_path))
            container.append(load_button)

            # Add memory info
            try:
                import psutil

                memory_percent = psutil.virtual_memory().percent
                info_label = Gtk.Label()
                info_label.set_markup(f"<small>Thumbnail mode (Memory: {memory_percent:.1f}%)</small>")
                info_label.add_css_class("dim-label")
                container.append(info_label)
            except ImportError:
                pass

            # Store image path for later loading
            container.image_path = image_path

            return container

        except Exception as e:
            print(f"❌ Create thumbnail widget error: {e}")
            return Gtk.Label(label="Error creating thumbnail")

    def _load_full_image(self, container, image_path):
        """Load full image replacing thumbnail"""
        try:
            # Check memory again before loading
            try:
                import psutil

                memory_percent = psutil.virtual_memory().percent
                if memory_percent > 85.0:
                    # Show warning instead of loading
                    self._show_memory_warning(container, memory_percent)
                    return
            except ImportError:
                pass

            # Create full image widget
            full_image = self._create_full_image_widget(image_path)

            # Replace container content
            parent = container.get_parent()
            if parent:
                parent.remove(container)
                parent.append(full_image)

        except Exception as e:
            print(f"❌ Load full image error: {e}")

    def _show_memory_warning(self, container, memory_percent):
        """Show memory warning instead of loading image"""
        try:
            # Clear container
            child = container.get_first_child()
            while child:
                next_child = child.get_next_sibling()
                container.remove(child)
                child = next_child

            # Add warning icon
            warning_icon = Gtk.Image()
            warning_icon.set_from_icon_name("dialog-warning-symbolic")
            warning_icon.set_pixel_size(64)
            warning_icon.add_css_class("warning")
            container.append(warning_icon)

            # Add warning message
            warning_label = Gtk.Label()
            warning_label.set_markup(
                f"<b>Memory Usage High</b>\n{memory_percent:.1f}% used\n\nClose some applications\nto load images"
            )
            warning_label.set_justify(Gtk.Justification.CENTER)
            warning_label.add_css_class("warning-text")
            container.append(warning_label)

            # Add view button for external viewer
            view_button = Gtk.Button()
            view_button.set_label("Open Externally")
            view_button.connect("clicked", lambda btn: self._open_image_externally(container.image_path))
            container.append(view_button)

        except Exception as e:
            print(f"❌ Show memory warning error: {e}")

    def _open_image_externally(self, image_path):
        """Open image in external viewer"""
        try:
            import os
            import subprocess

            if os.path.exists(image_path):
                # Use xdg-open on Linux
                subprocess.Popen(["xdg-open", image_path])
            else:
                print(f"❌ Image file not found: {image_path}")

        except Exception as e:
            print(f"❌ Open image externally error: {e}")

    def _image_path_exists(self, image_path):
        """Check if image path exists"""
        try:
            from pathlib import Path

            return Path(image_path).exists()
        except Exception:
            return False

    def _show_full_image(self, image_path):
        """Show full-size image in dialog"""
        try:
            # Create dialog
            dialog = Gtk.Dialog()
            dialog.set_title("Generated Image")
            dialog.set_modal(True)
            dialog.set_transient_for(self.view.app.window)
            dialog.set_default_size(800, 600)

            # Add image
            image = Gtk.Picture()
            image.set_filename(image_path)
            image.set_content_fit(Gtk.ContentFit.CONTAIN)

            scrolled = Gtk.ScrolledWindow()
            scrolled.set_child(image)

            dialog.get_content_area().append(scrolled)

            # Add close button
            dialog.add_button("Close", Gtk.ResponseType.CLOSE)
            dialog.connect("response", lambda d, r: d.destroy())

            dialog.present()

        except Exception as e:
            print(f"❌ Show full image error: {e}")

    def _show_generation_error(self, thinking_box, error_msg):
        """Show image generation error"""
        try:
            # Remove thinking indicator
            if thinking_box and thinking_box.get_parent():
                self.view._messages_container.remove(thinking_box)

            # Add error message
            self.view._add_error_message(f"Image generation failed: {error_msg}")

        except Exception as e:
            print(f"❌ Show generation error: {e}")
