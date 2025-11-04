#!/usr/bin/env python3
"""
GPU Drivers View

Read-only display of GPU driver information and specifications.
Shows available drivers for the GPU and their status.

Philosophy: GPUs first, then each vendor extends the GPU abstraction.
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

import sys
from pathlib import Path

from gi.repository import Adw, Gtk

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from gpu_driver_detector import GPUDriverDetector


class GPUDriversView:
    """Read-only view for GPU driver information"""

    def __init__(self, app):
        self.app = app
        self.detector = GPUDriverDetector()
        self.content = None

    def create_content(self) -> Gtk.Widget:
        """Create the GPU drivers view content"""
        try:
            # Main container
            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            main_box.set_margin_top(12)
            main_box.set_margin_bottom(12)
            main_box.set_margin_start(12)
            main_box.set_margin_end(12)

            # Create scrolled window
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_vexpand(True)
            scrolled.set_hexpand(True)
            scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

            # Create inner box for content
            content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            content_box.set_margin_top(12)
            content_box.set_margin_bottom(12)
            content_box.set_margin_start(12)
            content_box.set_margin_end(12)

            # Add status summary
            content_box.append(self._create_status_section())

            # Add GPU information
            if self.detector.nvidia_available and self.detector.gpus:
                content_box.append(self._create_gpu_section())
            else:
                content_box.append(self._create_no_gpu_section())

            scrolled.set_child(content_box)
            main_box.append(scrolled)

            self.content = main_box
            return main_box

        except Exception as e:
            print(f"❌ Error creating GPU drivers view: {e}")
            import traceback
            traceback.print_exc()
            return self._create_error_view(str(e))

    def _create_status_section(self) -> Gtk.Widget:
        """Create status summary section"""
        group = Adw.PreferencesGroup()
        group.set_title("GPU Driver Status")
        group.set_description("System GPU driver information")

        # Status row
        status_row = Adw.ActionRow()
        status_row.set_title("Status")

        status_label = Gtk.Label()
        status_label.set_text(self.detector.get_status_summary())
        status_label.set_halign(Gtk.Align.END)
        status_label.add_css_class("monospace")
        status_label.add_css_class("caption")
        status_row.add_suffix(status_label)

        group.add(status_row)
        return group

    def _create_gpu_section(self) -> Gtk.Widget:
        """Create GPU information section"""
        group = Adw.PreferencesGroup()
        group.set_title("GPU Information")
        group.set_description("Detected GPU devices and drivers")

        for gpu in self.detector.gpus:
            # GPU name row
            name_row = Adw.ActionRow()
            name_row.set_title(f"GPU {gpu.details['index']}: {gpu.name}")

            group.add(name_row)

            # Driver version row
            driver_row = Adw.ActionRow()
            driver_row.set_title("Driver Version")
            driver_label = Gtk.Label()
            driver_label.set_text(gpu.driver_version)
            driver_label.set_halign(Gtk.Align.END)
            driver_label.add_css_class("monospace")
            driver_row.add_suffix(driver_label)
            group.add(driver_row)

            # Driver type row
            type_row = Adw.ActionRow()
            type_row.set_title("Driver Type")
            type_label = Gtk.Label()
            type_label.set_text(gpu.details.get("driver_type", "Unknown"))
            type_label.set_halign(Gtk.Align.END)
            type_row.add_suffix(type_label)
            group.add(type_row)

            # CUDA version row
            cuda_row = Adw.ActionRow()
            cuda_row.set_title("CUDA Version")
            cuda_label = Gtk.Label()
            cuda_label.set_text(gpu.cuda_version or "N/A")
            cuda_label.set_halign(Gtk.Align.END)
            cuda_label.add_css_class("monospace")
            cuda_row.add_suffix(cuda_label)
            group.add(cuda_row)

            # Memory row
            memory_row = Adw.ActionRow()
            memory_row.set_title("Memory")
            memory_label = Gtk.Label()
            memory_label.set_text(f"{gpu.details['memory_gb']} GB")
            memory_label.set_halign(Gtk.Align.END)
            memory_row.add_suffix(memory_label)
            group.add(memory_row)

            # Compute capability row
            if gpu.compute_capability:
                compute_row = Adw.ActionRow()
                compute_row.set_title("Compute Capability")
                compute_label = Gtk.Label()
                compute_label.set_text(gpu.compute_capability)
                compute_label.set_halign(Gtk.Align.END)
                compute_row.add_suffix(compute_label)
                group.add(compute_row)

            # Add separator between GPUs
            if gpu != self.detector.gpus[-1]:
                separator = Gtk.Separator()
                group.add(separator)

        return group

    def _create_no_gpu_section(self) -> Gtk.Widget:
        """Create section when no GPU is detected"""
        group = Adw.PreferencesGroup()
        group.set_title("GPU Information")

        # No GPU row
        no_gpu_row = Adw.ActionRow()
        no_gpu_row.set_title("GPU Status")

        label = Gtk.Label()
        label.set_text("No NVIDIA GPU detected")
        label.set_halign(Gtk.Align.END)
        label.add_css_class("dim-label")
        no_gpu_row.add_suffix(label)

        group.add(no_gpu_row)
        return group

    def _create_error_view(self, error_msg: str) -> Gtk.Widget:
        """Create error view"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(24)
        box.set_margin_bottom(24)
        box.set_margin_start(24)
        box.set_margin_end(24)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)

        label = Gtk.Label()
        label.set_text(f"Error loading GPU drivers: {error_msg}")
        label.set_wrap(True)
        box.append(label)

        return box

