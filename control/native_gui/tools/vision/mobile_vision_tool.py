
# Initialize GUI event logger
gui_logger = create_gui_logger("unhinged-mobile-vision-tool", "1.0.0")

"""
Mobile Vision Tool - Camera and screen capture interface
Provides camera controls, screenshot capture, and vision AI integration for mobile interface.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gdk, GdkPixbuf
import cv2
import numpy as np
import threading
import time
from typing import Optional, Dict, List
from pathlib import Path
from unhinged_events import create_gui_logger

# Import vision modules
try:
    from .camera_capture import CameraCapture, CameraConfig
    from .screen_capture import ScreenCapture, ScreenConfig
    from .vision_client import VisionClient
    from .image_analysis import ImageAnalysisPipeline, AnalysisConfig
    VISION_MODULES_AVAILABLE = True
except ImportError as e:
    gui_logger.warn(f" Vision modules not available: {e}")
    VISION_MODULES_AVAILABLE = False


class MobileVisionTool(Adw.Bin):
    """Mobile interface for vision tools"""
    
    def __init__(self):
        super().__init__()
        
        # Vision components
        self.camera_capture = None
        self.screen_capture = None
        self.vision_client = None
        self.analysis_pipeline = None
        
        # UI state
        self.is_camera_active = False
        self.is_recording = False
        self.current_frame = None

        # Gallery state
        self.captured_images = []
        self.gallery_visible = False
        
        # Create UI
        self._create_ui()
        
        # Initialize vision components
        if VISION_MODULES_AVAILABLE:
            self._initialize_vision_components()
    
    def _create_ui(self):
        """Create mobile vision interface"""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(12)
        main_box.set_margin_start(12)
        main_box.set_margin_end(12)
        
        # Header
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Vision Tools"))
        main_box.append(header)
        
        # Camera preview area with overlay
        self.camera_preview = self._create_camera_preview()
        main_box.append(self.camera_preview)
        
        # Camera controls
        camera_controls = self._create_camera_controls()
        main_box.append(camera_controls)
        
        # Screenshot controls
        screenshot_controls = self._create_screenshot_controls()
        main_box.append(screenshot_controls)
        
        # Gallery area
        self.gallery_area = self._create_gallery_area()
        main_box.append(self.gallery_area)

        # Analysis results
        self.results_area = self._create_results_area()
        main_box.append(self.results_area)
        
        # Status bar
        self.status_label = Gtk.Label(label="Vision tools ready")
        self.status_label.add_css_class("dim-label")
        main_box.append(self.status_label)
        
        self.set_child(main_box)

    def _create_camera_preview(self) -> Gtk.Widget:
        """Create enhanced camera preview with overlay"""
        # Main preview container
        preview_overlay = Gtk.Overlay()

        # Camera frame
        self.camera_frame = Gtk.Frame()
        self.camera_frame.set_size_request(400, 300)
        self.camera_frame.add_css_class("camera-preview")

        # Camera image
        self.camera_image = Gtk.Picture()
        self.camera_image.set_content_fit(Gtk.ContentFit.COVER)
        self.camera_image.set_can_shrink(True)

        # Placeholder when no camera
        self.camera_placeholder = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.camera_placeholder.set_valign(Gtk.Align.CENTER)
        self.camera_placeholder.set_halign(Gtk.Align.CENTER)

        camera_icon = Gtk.Label(label="📹")
        camera_icon.add_css_class("large-emoji")

        camera_text = Gtk.Label(label="Camera Preview")
        camera_text.add_css_class("dim-label")

        self.camera_placeholder.append(camera_icon)
        self.camera_placeholder.append(camera_text)

        self.camera_frame.set_child(self.camera_placeholder)
        preview_overlay.set_child(self.camera_frame)

        # Detection overlay
        self.detection_overlay = Gtk.DrawingArea()
        self.detection_overlay.set_draw_func(self._draw_detections)
        preview_overlay.add_overlay(self.detection_overlay)

        # Info overlay (top-right)
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        info_box.set_valign(Gtk.Align.START)
        info_box.set_halign(Gtk.Align.END)
        info_box.set_margin_top(8)
        info_box.set_margin_end(8)

        # FPS counter
        self.fps_label = Gtk.Label(label="")
        self.fps_label.add_css_class("caption")
        self.fps_label.add_css_class("osd")
        info_box.append(self.fps_label)

        # Detection count
        self.detection_label = Gtk.Label(label="")
        self.detection_label.add_css_class("caption")
        self.detection_label.add_css_class("osd")
        info_box.append(self.detection_label)

        preview_overlay.add_overlay(info_box)

        # Control overlay (bottom)
        control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        control_box.set_valign(Gtk.Align.END)
        control_box.set_halign(Gtk.Align.CENTER)
        control_box.set_margin_bottom(8)

        # Quick capture button
        self.quick_capture_btn = Gtk.Button()
        self.quick_capture_btn.set_icon_name("camera-photo-symbolic")
        self.quick_capture_btn.add_css_class("circular")
        self.quick_capture_btn.add_css_class("osd")
        self.quick_capture_btn.connect("clicked", self._on_quick_capture)
        control_box.append(self.quick_capture_btn)

        # Analysis toggle
        self.analysis_toggle = Gtk.ToggleButton()
        self.analysis_toggle.set_icon_name("view-reveal-symbolic")
        self.analysis_toggle.add_css_class("circular")
        self.analysis_toggle.add_css_class("osd")
        self.analysis_toggle.set_tooltip_text("Toggle AI analysis")
        self.analysis_toggle.connect("toggled", self._on_analysis_toggle)
        control_box.append(self.analysis_toggle)

        preview_overlay.add_overlay(control_box)

        return preview_overlay

    def _draw_detections(self, area, cr, width, height, user_data):
        """Draw detection overlays on camera preview"""
        if not hasattr(self, 'current_detections') or not self.current_detections:
            return

        # Get camera image dimensions
        if not self.camera_image.get_paintable():
            return

        paintable = self.camera_image.get_paintable()
        img_width = paintable.get_intrinsic_width()
        img_height = paintable.get_intrinsic_height()

        if img_width <= 0 or img_height <= 0:
            return

        # Calculate scaling factors
        scale_x = width / img_width
        scale_y = height / img_height

        # Draw detection boxes
        cr.set_line_width(2)

        for detection in self.current_detections:
            bbox = detection.get('bbox', [0, 0, 0, 0])
            confidence = detection.get('confidence', 0)
            class_name = detection.get('class_name', 'unknown')

            x, y, w, h = bbox

            # Scale coordinates
            x *= scale_x
            y *= scale_y
            w *= scale_x
            h *= scale_y

            # Set color based on confidence
            if confidence > 0.8:
                cr.set_source_rgba(0, 1, 0, 0.8)  # Green
            elif confidence > 0.5:
                cr.set_source_rgba(1, 1, 0, 0.8)  # Yellow
            else:
                cr.set_source_rgba(1, 0.5, 0, 0.8)  # Orange

            # Draw bounding box
            cr.rectangle(x, y, w, h)
            cr.stroke()

            # Draw label background
            cr.set_source_rgba(0, 0, 0, 0.7)
            cr.rectangle(x, y - 20, len(class_name) * 8 + 10, 20)
            cr.fill()

            # Draw label text (simplified - would need Pango for proper text)
            cr.set_source_rgba(1, 1, 1, 1)
            cr.move_to(x + 5, y - 5)
            # Note: Cairo text rendering is basic, would need Pango for proper text
    
    def _create_camera_controls(self) -> Gtk.Widget:
        """Create camera control buttons"""
        group = Adw.PreferencesGroup()
        group.set_title("Camera")
        
        # Camera toggle row
        camera_row = Adw.ActionRow()
        camera_row.set_title("Camera Preview")
        camera_row.set_subtitle("Start/stop camera preview")
        
        self.camera_switch = Gtk.Switch()
        self.camera_switch.connect("notify::active", self._on_camera_toggle)
        camera_row.add_suffix(self.camera_switch)
        
        group.add(camera_row)
        
        # Camera selection row
        self.camera_select_row = Adw.ComboRow()
        self.camera_select_row.set_title("Camera Device")
        self.camera_select_row.set_subtitle("Select camera to use")
        
        # Create camera list model
        self.camera_model = Gtk.StringList()
        self.camera_select_row.set_model(self.camera_model)
        self.camera_select_row.connect("notify::selected", self._on_camera_selected)
        
        group.add(self.camera_select_row)
        
        # Capture buttons
        capture_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        capture_box.set_homogeneous(True)
        
        # Photo capture
        photo_button = Gtk.Button(label="📸 Photo")
        photo_button.connect("clicked", self._on_capture_photo)
        capture_box.append(photo_button)
        
        # Video recording
        self.video_button = Gtk.Button(label="🎬 Record")
        self.video_button.connect("clicked", self._on_toggle_recording)
        capture_box.append(self.video_button)
        
        capture_row = Adw.ActionRow()
        capture_row.set_title("Capture")
        capture_row.add_suffix(capture_box)
        
        group.add(capture_row)

        # Camera settings
        settings_row = Adw.ExpanderRow()
        settings_row.set_title("Camera Settings")
        settings_row.set_subtitle("Resolution, FPS, and filters")

        # Resolution selection
        self.resolution_row = Adw.ComboRow()
        self.resolution_row.set_title("Resolution")

        self.resolution_model = Gtk.StringList()
        resolutions = ["640x480", "800x600", "1280x720", "1920x1080"]
        for res in resolutions:
            self.resolution_model.append(res)

        self.resolution_row.set_model(self.resolution_model)
        self.resolution_row.set_selected(0)
        self.resolution_row.connect("notify::selected", self._on_resolution_changed)
        settings_row.add_row(self.resolution_row)

        # FPS selection
        self.fps_row = Adw.ComboRow()
        self.fps_row.set_title("Frame Rate")

        self.fps_model = Gtk.StringList()
        fps_options = ["15 FPS", "30 FPS", "60 FPS"]
        for fps in fps_options:
            self.fps_model.append(fps)

        self.fps_row.set_model(self.fps_model)
        self.fps_row.set_selected(1)  # Default to 30 FPS
        self.fps_row.connect("notify::selected", self._on_fps_changed)
        settings_row.add_row(self.fps_row)

        # Brightness adjustment
        self.brightness_row = Adw.ActionRow()
        self.brightness_row.set_title("Brightness")

        self.brightness_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 1, 0.1)
        self.brightness_scale.set_value(0.5)
        self.brightness_scale.set_hexpand(True)
        self.brightness_scale.connect("value-changed", self._on_brightness_changed)
        self.brightness_row.add_suffix(self.brightness_scale)
        settings_row.add_row(self.brightness_row)

        # Contrast adjustment
        self.contrast_row = Adw.ActionRow()
        self.contrast_row.set_title("Contrast")

        self.contrast_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 1, 0.1)
        self.contrast_scale.set_value(0.5)
        self.contrast_scale.set_hexpand(True)
        self.contrast_scale.connect("value-changed", self._on_contrast_changed)
        self.contrast_row.add_suffix(self.contrast_scale)
        settings_row.add_row(self.contrast_row)

        # Filters
        filters_row = Adw.ActionRow()
        filters_row.set_title("Filters")

        filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        # Grayscale filter
        self.grayscale_toggle = Gtk.ToggleButton(label="B&W")
        self.grayscale_toggle.connect("toggled", self._on_filter_changed)
        filter_box.append(self.grayscale_toggle)

        # Edge detection filter
        self.edge_toggle = Gtk.ToggleButton(label="Edges")
        self.edge_toggle.connect("toggled", self._on_filter_changed)
        filter_box.append(self.edge_toggle)

        # Blur filter
        self.blur_toggle = Gtk.ToggleButton(label="Blur")
        self.blur_toggle.connect("toggled", self._on_filter_changed)
        filter_box.append(self.blur_toggle)

        filters_row.add_suffix(filter_box)
        settings_row.add_row(filters_row)

        group.add(settings_row)

        return group
    
    def _create_screenshot_controls(self) -> Gtk.Widget:
        """Create screenshot control buttons"""
        group = Adw.PreferencesGroup()
        group.set_title("Screenshots")
        
        # Screenshot buttons
        screenshot_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        screenshot_box.set_homogeneous(True)
        
        # Full screen
        fullscreen_button = Gtk.Button(label="📺 Full Screen")
        fullscreen_button.connect("clicked", self._on_screenshot_fullscreen)
        screenshot_box.append(fullscreen_button)
        
        # Region select
        region_button = Gtk.Button(label="🎯 Region")
        region_button.connect("clicked", self._on_screenshot_region)
        screenshot_box.append(region_button)
        
        screenshot_row = Adw.ActionRow()
        screenshot_row.set_title("Capture Screen")
        screenshot_row.add_suffix(screenshot_box)
        
        group.add(screenshot_row)
        
        # OCR toggle
        ocr_row = Adw.ActionRow()
        ocr_row.set_title("Extract Text (OCR)")
        ocr_row.set_subtitle("Extract text from screenshots")
        
        self.ocr_switch = Gtk.Switch()
        self.ocr_switch.set_active(True)
        ocr_row.add_suffix(self.ocr_switch)
        
        group.add(ocr_row)
        
        return group
    
    def _create_results_area(self) -> Gtk.Widget:
        """Create results display area"""
        group = Adw.PreferencesGroup()
        group.set_title("Analysis Results")
        
        # Results text view
        self.results_buffer = Gtk.TextBuffer()
        self.results_view = Gtk.TextView()
        self.results_view.set_buffer(self.results_buffer)
        self.results_view.set_editable(False)
        self.results_view.set_size_request(-1, 150)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(self.results_view)
        
        results_row = Adw.ActionRow()
        results_row.set_title("Latest Analysis")
        
        # Clear button
        clear_button = Gtk.Button(label="Clear")
        clear_button.connect("clicked", self._on_clear_results)
        results_row.add_suffix(clear_button)
        
        group.add(results_row)
        group.add(scrolled)

        return group

    def _create_gallery_area(self) -> Gtk.Widget:
        """Create image gallery area"""
        self.gallery_group = Adw.PreferencesGroup()
        self.gallery_group.set_title("Captured Images")

        # Gallery toggle
        gallery_toggle_row = Adw.ActionRow()
        gallery_toggle_row.set_title("Show Gallery")
        gallery_toggle_row.set_subtitle("View captured images")

        self.gallery_toggle = Gtk.Switch()
        self.gallery_toggle.connect("notify::active", self._on_gallery_toggle)
        gallery_toggle_row.add_suffix(self.gallery_toggle)

        self.gallery_group.add(gallery_toggle_row)

        # Gallery grid (initially hidden)
        self.gallery_scrolled = Gtk.ScrolledWindow()
        self.gallery_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.gallery_scrolled.set_max_content_height(200)
        self.gallery_scrolled.set_visible(False)

        self.gallery_flow = Gtk.FlowBox()
        self.gallery_flow.set_max_children_per_line(3)
        self.gallery_flow.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.gallery_flow.connect("child-activated", self._on_gallery_item_activated)

        self.gallery_scrolled.set_child(self.gallery_flow)
        self.gallery_group.add(self.gallery_scrolled)

        # Gallery controls
        gallery_controls_row = Adw.ActionRow()
        gallery_controls_row.set_title("Gallery Actions")

        gallery_controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        # Clear gallery button
        clear_gallery_btn = Gtk.Button(label="🗑️ Clear")
        clear_gallery_btn.connect("clicked", self._on_clear_gallery)
        gallery_controls_box.append(clear_gallery_btn)

        # Export gallery button
        export_gallery_btn = Gtk.Button(label="📤 Export")
        export_gallery_btn.connect("clicked", self._on_export_gallery)
        gallery_controls_box.append(export_gallery_btn)

        gallery_controls_row.add_suffix(gallery_controls_box)
        gallery_controls_row.set_visible(False)
        self.gallery_controls_row = gallery_controls_row

        self.gallery_group.add(gallery_controls_row)

        return self.gallery_group
    
    def _initialize_vision_components(self):
        """Initialize vision components"""
        try:
            # Initialize screen capture
            self.screen_capture = ScreenCapture()
            
            # Initialize vision client
            self.vision_client = VisionClient()
            if self.vision_client.is_connected():
                self.screen_capture.enable_ocr(self.vision_client)
                self._update_status("Vision AI connected")
            else:
                self._update_status("Vision AI not available")
            
            # Load available cameras
            self._load_available_cameras()
            
        except Exception as e:
            gui_logger.error(f" Failed to initialize vision components: {e}")
            self._update_status(f"Initialization failed: {e}")
    
    def _load_available_cameras(self):
        """Load available cameras into selection"""
        if not self.camera_capture:
            # Create temporary camera capture to detect devices
            try:
                temp_capture = CameraCapture()
                cameras = temp_capture.get_available_cameras()
                temp_capture.cleanup()
                
                # Clear existing items
                self.camera_model.splice(0, self.camera_model.get_n_items())
                
                # Add cameras to model
                for camera in cameras:
                    self.camera_model.append(f"{camera['name']} ({camera['width']}x{camera['height']})")
                
                if cameras:
                    self.camera_select_row.set_selected(0)
                    self._update_status(f"Found {len(cameras)} camera(s)")
                else:
                    self._update_status("No cameras found")
                    
            except Exception as e:
                gui_logger.warn(f" Camera detection failed: {e}")
                self._update_status("Camera detection failed")
    
    def _on_camera_toggle(self, switch, pspec):
        """Handle camera toggle"""
        if switch.get_active():
            self._start_camera()
        else:
            self._stop_camera()
    
    def _on_camera_selected(self, combo_row, pspec):
        """Handle camera selection change"""
        if self.is_camera_active:
            # Restart camera with new selection
            self._stop_camera()
            self._start_camera()
    
    def _start_camera(self):
        """Start camera preview"""
        try:
            if self.camera_capture:
                self.camera_capture.cleanup()
            
            # Get selected camera index
            selected_index = self.camera_select_row.get_selected()
            
            # Create camera config
            config = CameraConfig(device_index=selected_index)
            self.camera_capture = CameraCapture(config)
            
            # Set frame callback
            self.camera_capture.on_frame_captured = self._on_camera_frame
            
            # Start capture
            if self.camera_capture.start_capture():
                self.is_camera_active = True
                self.camera_frame.set_child(self.camera_image)
                self._update_status("Camera started")
            else:
                self._update_status("Failed to start camera")
                self.camera_switch.set_active(False)
                
        except Exception as e:
            gui_logger.error(f" Camera start failed: {e}")
            self._update_status(f"Camera error: {e}")
            self.camera_switch.set_active(False)
    
    def _stop_camera(self):
        """Stop camera preview"""
        try:
            if self.camera_capture:
                self.camera_capture.stop_capture()
                self.camera_capture.cleanup()
                self.camera_capture = None
            
            self.is_camera_active = False
            self.camera_frame.set_child(self.camera_placeholder)
            self._update_status("Camera stopped")
            
        except Exception as e:
            gui_logger.error(f" Camera stop failed: {e}")
    
    def _on_camera_frame(self, frame: np.ndarray):
        """Handle new camera frame"""
        try:
            self.current_frame = frame.copy()

            # Apply filters
            processed_frame = self._apply_filters(frame)

            # Process detections if analysis enabled
            if self.analysis_toggle.get_active() and hasattr(self, 'camera_capture'):
                self._process_frame_detections(processed_frame)

            # Convert frame to GdkPixbuf for display
            rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)

            # Resize for preview (maintain aspect ratio)
            height, width = rgb_frame.shape[:2]
            max_width, max_height = 400, 300

            if width > max_width or height > max_height:
                scale = min(max_width / width, max_height / height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                rgb_frame = cv2.resize(rgb_frame, (new_width, new_height))

            # Convert to GdkPixbuf
            pixbuf = GdkPixbuf.Pixbuf.new_from_data(
                rgb_frame.tobytes(),
                GdkPixbuf.Colorspace.RGB,
                False, 8,
                rgb_frame.shape[1], rgb_frame.shape[0],
                rgb_frame.shape[1] * 3
            )

            # Update UI in main thread
            GLib.idle_add(self._update_camera_preview, pixbuf)

        except Exception as e:
            gui_logger.warn(f" Frame processing error: {e}")

    def _process_frame_detections(self, frame: np.ndarray):
        """Process frame for object detections"""
        try:
            if hasattr(self.camera_capture, 'yolo_model') and self.camera_capture.yolo_model:
                # Get YOLO detections
                detections = self.camera_capture._detect_objects_yolo(frame)

                # Update detections for overlay
                self.current_detections = detections

                # Update detection count
                GLib.idle_add(self._update_detection_info, len(detections))

                # Trigger overlay redraw
                GLib.idle_add(self.detection_overlay.queue_draw)

        except Exception as e:
            gui_logger.warn(f" Detection processing error: {e}")

    def _update_detection_info(self, count: int):
        """Update detection count display"""
        if count > 0:
            self.detection_label.set_text(f"🎯 {count} objects")
        else:
            self.detection_label.set_text("")
        return False
    
    def _update_camera_preview(self, pixbuf):
        """Update camera preview in main thread"""
        self.camera_image.set_pixbuf(pixbuf)

        # Update FPS if available
        if hasattr(self, 'camera_capture') and self.camera_capture:
            fps = getattr(self.camera_capture, 'fps_actual', 0)
            if fps > 0:
                self.fps_label.set_text(f"📊 {fps:.1f} FPS")

        return False  # Don't repeat

    def _on_quick_capture(self, button):
        """Quick capture button handler"""
        self._on_capture_photo(button)

    def _on_analysis_toggle(self, button):
        """Toggle AI analysis overlay"""
        if button.get_active():
            self._update_status("AI analysis enabled")
            # Initialize detections list
            self.current_detections = []
        else:
            self._update_status("AI analysis disabled")
            # Clear detections
            self.current_detections = []
            self.detection_label.set_text("")
            self.detection_overlay.queue_draw()

    def _apply_filters(self, frame: np.ndarray) -> np.ndarray:
        """Apply selected filters to frame"""
        try:
            filtered_frame = frame.copy()

            # Grayscale filter
            if hasattr(self, 'grayscale_toggle') and self.grayscale_toggle.get_active():
                gray = cv2.cvtColor(filtered_frame, cv2.COLOR_BGR2GRAY)
                filtered_frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

            # Edge detection filter
            if hasattr(self, 'edge_toggle') and self.edge_toggle.get_active():
                gray = cv2.cvtColor(filtered_frame, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                filtered_frame = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

            # Blur filter
            if hasattr(self, 'blur_toggle') and self.blur_toggle.get_active():
                filtered_frame = cv2.GaussianBlur(filtered_frame, (15, 15), 0)

            return filtered_frame

        except Exception as e:
            gui_logger.warn(f" Filter application error: {e}")
            return frame

    def _on_resolution_changed(self, combo_row, pspec):
        """Handle resolution change"""
        try:
            selected = combo_row.get_selected()
            resolutions = [(640, 480), (800, 600), (1280, 720), (1920, 1080)]

            if selected < len(resolutions):
                width, height = resolutions[selected]

                if self.camera_capture and hasattr(self.camera_capture, 'config'):
                    self.camera_capture.config.width = width
                    self.camera_capture.config.height = height

                    # Restart camera with new resolution
                    if self.is_camera_active:
                        self._restart_camera()

                    self._update_status(f"Resolution: {width}x{height}")

        except Exception as e:
            gui_logger.warn(f" Resolution change error: {e}")

    def _on_fps_changed(self, combo_row, pspec):
        """Handle FPS change"""
        try:
            selected = combo_row.get_selected()
            fps_values = [15, 30, 60]

            if selected < len(fps_values):
                fps = fps_values[selected]

                if self.camera_capture and hasattr(self.camera_capture, 'config'):
                    self.camera_capture.config.fps = fps

                    # Restart camera with new FPS
                    if self.is_camera_active:
                        self._restart_camera()

                    self._update_status(f"FPS: {fps}")

        except Exception as e:
            gui_logger.warn(f" FPS change error: {e}")

    def _on_brightness_changed(self, scale):
        """Handle brightness adjustment"""
        try:
            brightness = scale.get_value()

            if self.camera_capture and self.camera_capture.cap:
                self.camera_capture.cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
                self._update_status(f"Brightness: {brightness:.1f}")

        except Exception as e:
            gui_logger.warn(f" Brightness adjustment error: {e}")

    def _on_contrast_changed(self, scale):
        """Handle contrast adjustment"""
        try:
            contrast = scale.get_value()

            if self.camera_capture and self.camera_capture.cap:
                self.camera_capture.cap.set(cv2.CAP_PROP_CONTRAST, contrast)
                self._update_status(f"Contrast: {contrast:.1f}")

        except Exception as e:
            gui_logger.warn(f" Contrast adjustment error: {e}")

    def _on_filter_changed(self, toggle_button):
        """Handle filter toggle"""
        try:
            filter_name = "Unknown"

            if toggle_button == self.grayscale_toggle:
                filter_name = "Grayscale"
            elif toggle_button == self.edge_toggle:
                filter_name = "Edge Detection"
            elif toggle_button == self.blur_toggle:
                filter_name = "Blur"

            status = "enabled" if toggle_button.get_active() else "disabled"
            self._update_status(f"{filter_name} filter {status}")

            # Ensure only one filter is active at a time
            if toggle_button.get_active():
                if toggle_button != self.grayscale_toggle:
                    self.grayscale_toggle.set_active(False)
                if toggle_button != self.edge_toggle:
                    self.edge_toggle.set_active(False)
                if toggle_button != self.blur_toggle:
                    self.blur_toggle.set_active(False)

                # Re-activate the selected filter
                toggle_button.set_active(True)

        except Exception as e:
            gui_logger.warn(f" Filter toggle error: {e}")

    def _restart_camera(self):
        """Restart camera with new settings"""
        try:
            if self.is_camera_active:
                self._stop_camera()
                time.sleep(0.5)  # Brief pause
                self._start_camera()

        except Exception as e:
            gui_logger.warn(f" Camera restart error: {e}")
    
    def _on_capture_photo(self, button):
        """Capture photo from camera"""
        if self.current_frame is None:
            self._update_status("No camera frame available")
            return

        try:
            # Save photo
            timestamp = int(time.time())
            filename = f"photo_{timestamp}.jpg"

            cv2.imwrite(filename, self.current_frame)
            self._update_status(f"Photo saved: {filename}")

            # Add to gallery
            self._add_to_gallery(filename, self.current_frame)

            # Analyze with vision AI if available
            if self.vision_client and self.vision_client.is_connected():
                self._analyze_image(self.current_frame, "camera photo")

        except Exception as e:
            gui_logger.error(f" Photo capture failed: {e}")
            self._update_status(f"Photo capture failed: {e}")

    def _add_to_gallery(self, filename: str, image: np.ndarray):
        """Add captured image to gallery"""
        try:
            # Store image info
            image_info = {
                'filename': filename,
                'timestamp': int(time.time()),
                'image': image.copy()
            }

            self.captured_images.append(image_info)

            # Create thumbnail for gallery
            self._create_gallery_thumbnail(image_info)

            # Show gallery controls if first image
            if len(self.captured_images) == 1:
                self.gallery_controls_row.set_visible(True)

        except Exception as e:
            gui_logger.warn(f" Gallery add error: {e}")

    def _create_gallery_thumbnail(self, image_info: Dict):
        """Create thumbnail widget for gallery"""
        try:
            image = image_info['image']

            # Create thumbnail
            height, width = image.shape[:2]
            thumb_size = 80

            if width > height:
                new_width = thumb_size
                new_height = int(height * thumb_size / width)
            else:
                new_height = thumb_size
                new_width = int(width * thumb_size / height)

            thumbnail = cv2.resize(image, (new_width, new_height))
            rgb_thumb = cv2.cvtColor(thumbnail, cv2.COLOR_BGR2RGB)

            # Convert to GdkPixbuf
            pixbuf = GdkPixbuf.Pixbuf.new_from_data(
                rgb_thumb.tobytes(),
                GdkPixbuf.Colorspace.RGB,
                False, 8,
                rgb_thumb.shape[1], rgb_thumb.shape[0],
                rgb_thumb.shape[1] * 3
            )

            # Create gallery item
            gallery_item = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

            # Thumbnail image
            thumb_picture = Gtk.Picture()
            thumb_picture.set_pixbuf(pixbuf)
            thumb_picture.set_size_request(thumb_size, thumb_size)
            gallery_item.append(thumb_picture)

            # Filename label
            name_label = Gtk.Label(label=Path(image_info['filename']).stem)
            name_label.add_css_class("caption")
            name_label.set_ellipsize(3)  # ELLIPSIZE_END
            gallery_item.append(name_label)

            # Add to flow box
            self.gallery_flow.append(gallery_item)

            # Store reference for later use
            gallery_item.image_info = image_info

        except Exception as e:
            gui_logger.warn(f" Thumbnail creation error: {e}")

    def _on_gallery_toggle(self, switch, pspec):
        """Toggle gallery visibility"""
        visible = switch.get_active()
        self.gallery_scrolled.set_visible(visible)
        self.gallery_visible = visible

        if visible and self.captured_images:
            self._update_status(f"Gallery: {len(self.captured_images)} images")
        else:
            self._update_status("Gallery hidden")

    def _on_gallery_item_activated(self, flow_box, child):
        """Handle gallery item selection"""
        try:
            gallery_item = child.get_child()
            if hasattr(gallery_item, 'image_info'):
                image_info = gallery_item.image_info
                filename = image_info['filename']

                self._update_status(f"Selected: {filename}")

                # Analyze selected image
                if self.vision_client and self.vision_client.is_connected():
                    self._analyze_image(image_info['image'], f"gallery image {filename}")

        except Exception as e:
            gui_logger.warn(f" Gallery selection error: {e}")

    def _on_clear_gallery(self, button):
        """Clear all images from gallery"""
        try:
            # Clear gallery flow box
            child = self.gallery_flow.get_first_child()
            while child:
                next_child = child.get_next_sibling()
                self.gallery_flow.remove(child)
                child = next_child

            # Clear image list
            self.captured_images.clear()

            # Hide controls
            self.gallery_controls_row.set_visible(False)

            self._update_status("Gallery cleared")

        except Exception as e:
            gui_logger.warn(f" Gallery clear error: {e}")

    def _on_export_gallery(self, button):
        """Export gallery images"""
        try:
            if not self.captured_images:
                self._update_status("No images to export")
                return

            # Create export directory
            export_dir = Path(f"gallery_export_{int(time.time())}")
            export_dir.mkdir(exist_ok=True)

            # Copy images to export directory
            for i, image_info in enumerate(self.captured_images):
                src_file = Path(image_info['filename'])
                dst_file = export_dir / f"image_{i:03d}_{src_file.name}"

                if src_file.exists():
                    import shutil
                    shutil.copy2(src_file, dst_file)

            self._update_status(f"Gallery exported to {export_dir}")

        except Exception as e:
            gui_logger.warn(f" Gallery export error: {e}")
            self._update_status(f"Export failed: {e}")
    
    def _on_toggle_recording(self, button):
        """Toggle video recording"""
        if not self.camera_capture:
            self._update_status("Camera not active")
            return
        
        try:
            if not self.is_recording:
                # Start recording
                timestamp = int(time.time())
                filename = f"video_{timestamp}.mp4"
                
                if self.camera_capture.start_video_recording(filename):
                    self.is_recording = True
                    self.video_button.set_label("⏹️ Stop")
                    self._update_status(f"Recording started: {filename}")
                else:
                    self._update_status("Failed to start recording")
            else:
                # Stop recording
                filename = self.camera_capture.stop_video_recording()
                self.is_recording = False
                self.video_button.set_label("🎬 Record")
                
                if filename:
                    self._update_status(f"Recording saved: {filename}")
                else:
                    self._update_status("Recording failed")
                    
        except Exception as e:
            gui_logger.error(f" Recording toggle failed: {e}")
            self._update_status(f"Recording error: {e}")
    
    def _on_screenshot_fullscreen(self, button):
        """Capture fullscreen screenshot"""
        try:
            if not self.screen_capture:
                self._update_status("Screen capture not available")
                return
            
            # Capture screenshot
            img = self.screen_capture.capture_screenshot()
            if img is None:
                self._update_status("Screenshot capture failed")
                return
            
            # Save screenshot
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.jpg"
            
            if self.screen_capture.save_screenshot(filename):
                self._update_status(f"Screenshot saved: {filename}")
                
                # Extract text if OCR enabled
                if self.ocr_switch.get_active():
                    text = self.screen_capture.extract_text_from_screen()
                    if text:
                        self._add_result(f"OCR Text from {filename}:", text)
                
                # Analyze with vision AI
                if self.vision_client and self.vision_client.is_connected():
                    self._analyze_image(img, f"screenshot {filename}")
            else:
                self._update_status("Failed to save screenshot")
                
        except Exception as e:
            gui_logger.error(f" Screenshot failed: {e}")
            self._update_status(f"Screenshot error: {e}")
    
    def _on_screenshot_region(self, button):
        """Capture region screenshot (placeholder)"""
        # TODO: Implement region selection UI
        self._update_status("Region selection not implemented yet")
    
    def _analyze_image(self, image: np.ndarray, source: str):
        """Analyze image with vision AI"""
        def analyze_async():
            try:
                result = self.vision_client.analyze_frame(image, "Describe what you see in this image")
                
                if result.get('success'):
                    description = result['description']
                    confidence = result.get('confidence', 0)
                    
                    GLib.idle_add(self._add_result, 
                                f"Vision Analysis ({source}):", 
                                f"{description}\n(Confidence: {confidence:.2f})")
                else:
                    GLib.idle_add(self._add_result, 
                                f"Vision Analysis Failed ({source}):", 
                                result.get('error', 'Unknown error'))
                    
            except Exception as e:
                GLib.idle_add(self._add_result, 
                            f"Vision Analysis Error ({source}):", 
                            str(e))
        
        # Run analysis in background
        threading.Thread(target=analyze_async, daemon=True).start()
    
    def _add_result(self, title: str, content: str):
        """Add result to results area"""
        current_text = self.results_buffer.get_text(
            self.results_buffer.get_start_iter(),
            self.results_buffer.get_end_iter(),
            False
        )
        
        new_text = f"{title}\n{content}\n\n{current_text}"
        
        # Limit to last 1000 characters
        if len(new_text) > 1000:
            new_text = new_text[:1000] + "...\n[Truncated]"
        
        self.results_buffer.set_text(new_text)
        return False  # Don't repeat
    
    def _on_clear_results(self, button):
        """Clear results area"""
        self.results_buffer.set_text("")
    
    def _update_status(self, message: str):
        """Update status message"""
        self.status_label.set_text(message)
    
    def cleanup(self):
        """Clean up resources"""
        if self.camera_capture:
            self.camera_capture.cleanup()
        
        if self.screen_capture:
            self.screen_capture.cleanup()
        
        if self.vision_client:
            self.vision_client.close()
        
        if self.analysis_pipeline:
            self.analysis_pipeline.cleanup()


# Test function
def test_mobile_vision_tool():
    """Test mobile vision tool"""
    
    app = Adw.Application()
    
    def on_activate(app):
        window = Adw.ApplicationWindow(application=app)
        window.set_title("Vision Tool Test")
        window.set_default_size(400, 600)
        
        vision_tool = MobileVisionTool()
        window.set_content(vision_tool)
        
        window.present()
    
    app.connect("activate", on_activate)
    app.run()


if __name__ == "__main__":
    test_mobile_vision_tool()
