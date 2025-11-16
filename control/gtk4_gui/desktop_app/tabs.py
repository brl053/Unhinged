"""
@llm-doc Desktop App Tab Content Creation
@llm-version 1.0.0
@llm-date 2025-11-15

Tab content creation for all application tabs.
"""

import sys
import traceback
from pathlib import Path

from gi.repository import Gtk

# Add gtk4_gui to path for absolute imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TabContentFactory:
    """Factory for creating tab content."""

    @staticmethod
    def create_fallback(title: str):
        """Create a generic fallback widget for unavailable features."""
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        container.set_margin_top(16)
        container.set_margin_bottom(16)
        container.set_margin_start(16)
        container.set_margin_end(16)

        label = Gtk.Label(label=f"{title} functionality temporarily unavailable")
        label.add_css_class("dim-label")
        container.append(label)

        return container

    @staticmethod
    def create_status_tab(app):
        """Create the status tab content using extracted StatusView."""
        try:
            from views.status_view import StatusView

            app.status_view = StatusView(app)
            return app.status_view.create_content()
        except Exception as e:
            print(f"❌ CRITICAL: Status creation failed: {e}")
            traceback.print_exc()
            raise

    @staticmethod
    def create_system_info_tab(app):
        """Create the system info tab content using extracted SystemInfoView."""
        try:
            from views.system.system_view import SystemInfoView

            app.system_info_view = SystemInfoView(app)
            return app.system_info_view.create_content()
        except Exception as e:
            print(f"❌ CRITICAL: System Info creation failed: {e}")
            traceback.print_exc()
            raise

    @staticmethod
    def create_processes_tab(app):
        """Create the processes tab content using extracted ProcessesView."""
        try:
            from views.processes_view import ProcessesView

            app.processes_view = ProcessesView(app)
            return app.processes_view.create_content()
        except ImportError as e:
            print(f"⚠️ ProcessesView not available, using fallback: {e}")
            return TabContentFactory.create_fallback("Process monitoring")
        except Exception as e:
            print(f"❌ Error creating processes view: {e}")
            return TabContentFactory.create_fallback("Process monitoring")

    @staticmethod
    def create_input_tab(app):
        """Create the Input tab content using InputView."""
        try:
            from views.input_view import InputView

            input_view = InputView()
            widget = input_view.render()

            if app.session_logger:
                app.session_logger.log_gui_event("INPUT_TAB_CREATED", "Input tab created")

            return widget
        except Exception as e:
            print(f"❌ Error creating input view: {e}")
            return TabContentFactory.create_fallback("Input")

    @staticmethod
    def create_chatroom_tab(app):
        """Create the OS Chatroom tab content using extracted ChatroomView."""
        try:
            from views.chatroom.chatroom_view import ChatroomView

            app.chatroom_view = ChatroomView(app)
            return app.chatroom_view.create_content()
        except Exception as e:
            print(f"❌ CRITICAL: OS Chatroom creation failed: {e}")
            traceback.print_exc()
            raise

    @staticmethod
    def create_bluetooth_tab(app):
        """Create the Bluetooth tab content using extracted BluetoothView."""
        try:
            from views.bluetooth_view import BluetoothView

            app.bluetooth_view = BluetoothView(app)
            return app.bluetooth_view.create_content()
        except ImportError as e:
            print(f"⚠️ BluetoothView not available, using fallback: {e}")
            return TabContentFactory.create_fallback("Bluetooth")
        except Exception as e:
            print(f"❌ Error creating bluetooth view: {e}")
            return TabContentFactory.create_fallback("Bluetooth")

    @staticmethod
    def create_output_tab(app):
        """Create the Output tab content using extracted OutputView."""
        try:
            from views.output_view import OutputView

            app.output_view = OutputView(app)
            return app.output_view.create_content()
        except Exception as e:
            print(f"❌ Error creating output view: {e}")
            return TabContentFactory.create_fallback("Audio output")

    @staticmethod
    def create_usb_tab(app):
        """Create the USB tab content using extracted USBView."""
        try:
            from views.usb_view import USBView

            app.usb_view = USBView(app)
            return app.usb_view.create_content()
        except Exception as e:
            print(f"❌ Error creating USB view: {e}")
            traceback.print_exc()
            return TabContentFactory.create_fallback("USB Devices")

    @staticmethod
    def create_graph_tab(app):
        """Create the Graph Editor tab content using GraphWorkspaceView."""
        try:
            from views.graph_workspace_view import GraphWorkspaceView

            app.graph_workspace_view = GraphWorkspaceView(app)
            content = app.graph_workspace_view.create_content()
            app.graph_workspace_view.load_sample_graph()
            return content
        except Exception as e:
            print(f"❌ Error creating graph editor view: {e}")
            traceback.print_exc()
            return TabContentFactory.create_fallback("Graph Editor")

    @staticmethod
    def create_documents_tab(app):
        """Create the Documents tab content using DocumentWorkspaceView."""
        try:
            from views.document_workspace_view import DocumentWorkspaceView

            app.document_workspace_view = DocumentWorkspaceView(app, document_type="document")
            return app.document_workspace_view.create_content()
        except Exception as e:
            print(f"❌ Error creating documents view: {e}")
            traceback.print_exc()
            return TabContentFactory.create_fallback("Documents")

    @staticmethod
    def create_gpu_tab(app):
        """Create the GPU tab content using GPUView."""
        try:
            from views.gpu_view import GPUView

            app.gpu_view = GPUView(app)
            return app.gpu_view.create_content()
        except Exception as e:
            print(f"❌ Error creating GPU view: {e}")
            traceback.print_exc()
            return TabContentFactory.create_fallback("GPU")
