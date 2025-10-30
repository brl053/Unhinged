#!/usr/bin/env python3
"""
Session Management Components for GTK4 GUI

Provides session creation UI with progressive disclosure pattern.
Integrates with chat service's embedded session management.

@llm-type component.session-management
@llm-does GTK4 session management UI with progressive disclosure
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GObject, GLib
import threading
import time
import uuid
from typing import Dict, List, Optional, Any, Callable
import logging

from .base import BaseComponent

# gRPC client imports
try:
    from libs.python.grpc.client_factory import create_chat_client
    from unhinged_proto_clients import chat_pb2
    GRPC_AVAILABLE = True
except ImportError:
    GRPC_AVAILABLE = False
    print("⚠️ gRPC clients not available for session management")

class SessionState(GObject.Object):
    """Session state data model"""
    
    __gtype_name__ = 'SessionState'
    
    def __init__(self):
        super().__init__()
        self.session_id = None
        self.conversation_id = None
        self.is_active = False
        self.created_at = None
        self.metadata = {}

class SessionManager(BaseComponent):
    """
    Session management component with progressive disclosure
    
    Features:
    - Session creation button (prominent when no session)
    - Session ID display when active
    - Progressive enablement of chat functionality
    - Write-through session storage via gRPC
    """
    
    __gtype_name__ = 'SessionManager'
    
    # Signals
    __gsignals__ = {
        'session-created': (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        'session-ended': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'session-error': (GObject.SignalFlags.RUN_FIRST, None, (str,))
    }
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Session state
        self.session_state = SessionState()
        self.grpc_client = None
        self.grpc_address = "localhost:9095"  # Chat service with sessions
        
        # UI state callbacks
        self.ui_state_callbacks = []
        
        self._build_ui()
        self._initialize_grpc_client()
    
    def _initialize_grpc_client(self):
        """Initialize gRPC client for chat service"""
        if not GRPC_AVAILABLE:
            self.logger.warning("gRPC not available, session management will be disabled")
            return
        
        try:
            self.grpc_client = create_chat_client(self.grpc_address)
            self.logger.info(f"gRPC client initialized for {self.grpc_address}")
        except Exception as e:
            self.logger.error(f"Failed to initialize gRPC client: {e}")
            self.grpc_client = None
    
    def _build_ui(self):
        """Build session management UI"""
        # Main container
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.set_margin_top(6)
        self.set_margin_bottom(6)
        self.set_margin_start(12)
        self.set_margin_end(12)
        
        # Session status container
        self.status_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.status_container.set_halign(Gtk.Align.CENTER)
        
        # Create session button (prominent when no session)
        self.create_session_button = Gtk.Button()
        self.create_session_button.set_label("🚀 Create Session")
        self.create_session_button.add_css_class("suggested-action")
        self.create_session_button.add_css_class("pill")
        self.create_session_button.set_size_request(200, 40)
        self.create_session_button.connect("clicked", self._on_create_session_clicked)
        
        # Session info display (hidden initially)
        self.session_info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.session_info_box.set_visible(False)
        
        # Session ID label
        self.session_id_label = Gtk.Label()
        self.session_id_label.add_css_class("monospace")
        self.session_id_label.add_css_class("dim-label")
        
        # Session status indicator
        self.session_status_icon = Gtk.Image()
        self.session_status_icon.set_from_icon_name("emblem-ok-symbolic")
        self.session_status_icon.add_css_class("success")
        
        # End session button
        self.end_session_button = Gtk.Button()
        self.end_session_button.set_icon_name("window-close-symbolic")
        self.end_session_button.set_tooltip_text("End Session")
        self.end_session_button.add_css_class("destructive-action")
        self.end_session_button.add_css_class("circular")
        self.end_session_button.connect("clicked", self._on_end_session_clicked)
        
        # Assemble session info
        self.session_info_box.append(self.session_status_icon)
        self.session_info_box.append(self.session_id_label)
        self.session_info_box.append(self.end_session_button)
        
        # Add to status container
        self.status_container.append(self.create_session_button)
        self.status_container.append(self.session_info_box)
        
        # Progress indicator (hidden initially)
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_visible(False)
        self.progress_bar.set_text("Creating session...")
        self.progress_bar.set_show_text(True)
        self.progress_bar.pulse()
        
        # Status message
        self.status_label = Gtk.Label()
        self.status_label.set_text("Create a session to start chatting")
        self.status_label.add_css_class("dim-label")
        self.status_label.set_halign(Gtk.Align.CENTER)
        
        # Add all components
        self.append(self.status_container)
        self.append(self.progress_bar)
        self.append(self.status_label)
        
        # Update initial UI state
        self._update_ui_state()
    
    def _on_create_session_clicked(self, button):
        """Handle create session button click"""
        if not self.grpc_client:
            self._show_error("gRPC client not available")
            return
        
        # Start session creation
        self._start_session_creation()
    
    def _start_session_creation(self):
        """Start session creation process"""
        # Update UI to show progress
        self.create_session_button.set_sensitive(False)
        self.progress_bar.set_visible(True)
        self.status_label.set_text("Creating session...")
        
        # Start progress pulse
        GLib.timeout_add(100, self._pulse_progress)
        
        # Create session in background thread
        thread = threading.Thread(target=self._create_session_thread, daemon=True)
        thread.start()
    
    def _pulse_progress(self):
        """Pulse progress bar"""
        if self.progress_bar.get_visible():
            self.progress_bar.pulse()
            return True  # Continue pulsing
        return False  # Stop pulsing
    
    def _create_session_thread(self):
        """Create session via gRPC in background thread"""
        try:
            # Create conversation request (which creates session)
            request = chat_pb2.CreateConversationRequest()
            request.team_id = "default"
            request.namespace_id = "default"
            request.title = f"Chat Session {int(time.time())}"
            request.description = "Interactive chat session"
            
            # Set default settings
            request.settings.model = "gpt-4"
            request.settings.temperature = 0.7
            request.settings.max_tokens = 2048
            request.settings.include_context = True
            request.settings.enable_tools = True
            
            # Make gRPC call
            response = self.grpc_client.CreateConversation(request)
            
            if response.response.success:
                # Session created successfully
                conversation_id = response.conversation.metadata.id
                GLib.idle_add(self._on_session_created, conversation_id)
            else:
                GLib.idle_add(self._on_session_error, "Failed to create session")
                
        except Exception as e:
            GLib.idle_add(self._on_session_error, str(e))
    
    def _on_session_created(self, conversation_id: str):
        """Handle successful session creation"""
        # Update session state
        self.session_state.session_id = conversation_id[:8]  # Short ID for display
        self.session_state.conversation_id = conversation_id
        self.session_state.is_active = True
        self.session_state.created_at = time.time()
        
        # Update UI
        self._update_ui_state()
        
        # Emit signal
        self.emit('session-created', conversation_id)
        
        self.logger.info(f"Session created: {conversation_id}")
    
    def _on_session_error(self, error_message: str):
        """Handle session creation error"""
        self._show_error(error_message)
        self.logger.error(f"Session creation failed: {error_message}")
    
    def _on_end_session_clicked(self, button):
        """Handle end session button click"""
        # Reset session state
        self.session_state.session_id = None
        self.session_state.conversation_id = None
        self.session_state.is_active = False
        self.session_state.created_at = None
        
        # Update UI
        self._update_ui_state()
        
        # Emit signal
        self.emit('session-ended')
        
        self.logger.info("Session ended by user")
    
    def _update_ui_state(self):
        """Update UI based on session state"""
        if self.session_state.is_active:
            # Session active - show session info
            self.create_session_button.set_visible(False)
            self.session_info_box.set_visible(True)
            self.progress_bar.set_visible(False)
            
            # Update session display
            self.session_id_label.set_text(f"Session: {self.session_state.session_id}")
            self.status_label.set_text("Session active - chat functionality enabled")
            
            # Enable create session button for next session
            self.create_session_button.set_sensitive(True)
            
        else:
            # No session - show create button
            self.create_session_button.set_visible(True)
            self.session_info_box.set_visible(False)
            self.progress_bar.set_visible(False)
            
            # Reset button state
            self.create_session_button.set_sensitive(True)
            self.status_label.set_text("Create a session to start chatting")
        
        # Notify UI state callbacks
        self._notify_ui_state_callbacks()
    
    def _show_error(self, error_message: str):
        """Show error state"""
        self.create_session_button.set_sensitive(True)
        self.progress_bar.set_visible(False)
        self.status_label.set_text(f"❌ Error: {error_message}")
        
        # Emit error signal
        self.emit('session-error', error_message)
    
    def _notify_ui_state_callbacks(self):
        """Notify registered UI state callbacks"""
        for callback in self.ui_state_callbacks:
            try:
                callback(self.session_state.is_active)
            except Exception as e:
                self.logger.error(f"UI state callback failed: {e}")
    
    # ========================================================================
    # Public API
    # ========================================================================
    
    def register_ui_state_callback(self, callback: Callable[[bool], None]):
        """Register callback for UI state changes"""
        self.ui_state_callbacks.append(callback)
    
    def get_session_state(self) -> SessionState:
        """Get current session state"""
        return self.session_state
    
    def is_session_active(self) -> bool:
        """Check if session is active"""
        return self.session_state.is_active
    
    def get_conversation_id(self) -> Optional[str]:
        """Get current conversation ID"""
        return self.session_state.conversation_id
