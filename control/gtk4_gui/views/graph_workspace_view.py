"""
GraphWorkspaceView - Visual graph editor workspace for the GTK4 UI

Provides a complete workspace for editing node-based graphs with:
- Graph canvas for visual editing
- Toolbar with zoom and grid controls
- Node/edge creation and manipulation
- Integration with document store and graph service
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Adw, Gtk, GObject
from typing import Optional, Dict, Any, List
import asyncio
import sys
from pathlib import Path

# Add proto clients to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "generated" / "python" / "clients"))

# Import graph canvas component
try:
    from ..components import GraphCanvasWidget
    from ..components.graph_serializer import GraphSerializer
    from ..components.document_store_client import DocumentStoreClient
    from ..components.graph_service_client import GraphServiceClient
    GRAPH_CANVAS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some graph components not available: {e}")
    GRAPH_CANVAS_AVAILABLE = False


class GraphWorkspaceView:
    """Visual graph editor workspace for editing node-based graphs"""
    
    def __init__(self, parent_app):
        """Initialize graph workspace view"""
        self.app = parent_app
        self.project_root = parent_app.project_root

        # UI components
        self.canvas = None
        self.toolbar = None
        self.zoom_label = None
        self.grid_toggle = None
        self.snap_toggle = None

        # Graph state
        self.current_graph = None
        self.nodes = []
        self.edges = []
        self.current_execution_id = None

        # Service clients
        self.doc_store_client = DocumentStoreClient()
        self.graph_service_client = GraphServiceClient()
        self.serializer = GraphSerializer()
    
    def create_content(self):
        """Create the graph workspace content"""
        if not GRAPH_CANVAS_AVAILABLE:
            return self._create_error_view("Graph canvas component not available")
        
        try:
            # Create main container
            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            main_box.set_hexpand(True)
            main_box.set_vexpand(True)
            
            # Create toolbar
            toolbar = self._create_toolbar()
            main_box.append(toolbar)
            
            # Create canvas
            self.canvas = GraphCanvasWidget()
            self.canvas.set_hexpand(True)
            self.canvas.set_vexpand(True)
            
            # Connect canvas signals
            self.canvas.connect('node-selected', self._on_node_selected)
            self.canvas.connect('node-moved', self._on_node_moved)
            self.canvas.connect('edge-created', self._on_edge_created)
            self.canvas.connect('viewport-changed', self._on_viewport_changed)
            
            main_box.append(self.canvas)
            
            # Create status bar
            status_bar = self._create_status_bar()
            main_box.append(status_bar)
            
            return main_box
        
        except Exception as e:
            print(f"❌ Failed to create graph workspace: {e}")
            import traceback
            traceback.print_exc()
            return self._create_error_view(f"Failed to create workspace: {e}")
    
    def _create_toolbar(self) -> Gtk.Widget:
        """Create the graph editing toolbar"""
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        toolbar.set_margin_top(8)
        toolbar.set_margin_bottom(8)
        toolbar.set_margin_start(8)
        toolbar.set_margin_end(8)
        toolbar.add_css_class("toolbar")
        
        # Zoom controls
        zoom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        
        zoom_out_btn = Gtk.Button(label="−")
        zoom_out_btn.connect('clicked', self._on_zoom_out)
        zoom_box.append(zoom_out_btn)
        
        self.zoom_label = Gtk.Label(label="100%")
        self.zoom_label.set_size_request(50, -1)
        zoom_box.append(self.zoom_label)
        
        zoom_in_btn = Gtk.Button(label="+")
        zoom_in_btn.connect('clicked', self._on_zoom_in)
        zoom_box.append(zoom_in_btn)
        
        zoom_reset_btn = Gtk.Button(label="Reset")
        zoom_reset_btn.connect('clicked', self._on_zoom_reset)
        zoom_box.append(zoom_reset_btn)
        
        toolbar.append(zoom_box)
        
        # Separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        toolbar.append(separator)
        
        # Grid controls
        grid_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        
        self.grid_toggle = Gtk.ToggleButton(label="Grid")
        self.grid_toggle.set_active(True)
        self.grid_toggle.connect('toggled', self._on_grid_toggled)
        grid_box.append(self.grid_toggle)
        
        self.snap_toggle = Gtk.ToggleButton(label="Snap")
        self.snap_toggle.set_active(True)
        self.snap_toggle.connect('toggled', self._on_snap_toggled)
        grid_box.append(self.snap_toggle)
        
        toolbar.append(grid_box)
        
        # Separator
        separator2 = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        toolbar.append(separator2)
        
        # Action buttons
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        
        clear_btn = Gtk.Button(label="Clear")
        clear_btn.connect('clicked', self._on_clear_canvas)
        action_box.append(clear_btn)
        
        load_btn = Gtk.Button(label="Load Graph")
        load_btn.connect('clicked', self._on_load_graph)
        action_box.append(load_btn)
        
        save_btn = Gtk.Button(label="Save Graph")
        save_btn.connect('clicked', self._on_save_graph)
        action_box.append(save_btn)
        
        toolbar.append(action_box)
        
        # Spacer
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        toolbar.append(spacer)
        
        return toolbar
    
    def _create_status_bar(self) -> Gtk.Widget:
        """Create the status bar"""
        status_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        status_bar.set_margin_top(4)
        status_bar.set_margin_bottom(4)
        status_bar.set_margin_start(8)
        status_bar.set_margin_end(8)
        status_bar.add_css_class("status-bar")
        
        # Status label
        status_label = Gtk.Label(label="Ready")
        status_label.set_hexpand(True)
        status_label.set_halign(Gtk.Align.START)
        status_bar.append(status_label)
        
        # Store reference for updates
        self._status_label = status_label
        
        return status_bar
    
    def _create_error_view(self, message: str) -> Gtk.Widget:
        """Create an error view"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        
        error_label = Gtk.Label(label="⚠️ Error")
        error_label.add_css_class("title-1")
        box.append(error_label)
        
        message_label = Gtk.Label(label=message)
        message_label.set_wrap(True)
        box.append(message_label)
        
        return box
    
    def _on_zoom_in(self, button):
        """Handle zoom in button"""
        if self.canvas:
            self.canvas.viewport.zoom_at(1.1, 200, 150)
            self._update_zoom_label()
            self.canvas.queue_draw()
    
    def _on_zoom_out(self, button):
        """Handle zoom out button"""
        if self.canvas:
            self.canvas.viewport.zoom_at(0.9, 200, 150)
            self._update_zoom_label()
            self.canvas.queue_draw()
    
    def _on_zoom_reset(self, button):
        """Handle zoom reset button"""
        if self.canvas:
            self.canvas.reset_viewport()
            self._update_zoom_label()
    
    def _on_grid_toggled(self, button):
        """Handle grid toggle"""
        if self.canvas:
            self.canvas.show_grid = button.get_active()
            self.canvas.queue_draw()
    
    def _on_snap_toggled(self, button):
        """Handle snap toggle"""
        if self.canvas:
            self.canvas.snap_to_grid = button.get_active()
    
    def _on_clear_canvas(self, button):
        """Handle clear canvas button"""
        if self.canvas:
            self.canvas.set_nodes([])
            self.canvas.set_edges([])
            self.nodes = []
            self.edges = []
            self._update_status("Canvas cleared")
    
    def _on_load_graph(self, button):
        """Handle load graph button"""
        # TODO: Implement graph loading from document store
        self._update_status("Load graph not yet implemented")
    
    def _on_save_graph(self, button):
        """Handle save graph button"""
        # TODO: Implement graph saving to document store
        self._update_status("Save graph not yet implemented")
    
    def _on_node_selected(self, canvas, node_id: str):
        """Handle node selection"""
        self._update_status(f"Selected node: {node_id}")
    
    def _on_node_moved(self, canvas, node_id: str, x: float, y: float):
        """Handle node moved"""
        self._update_status(f"Moved node {node_id} to ({x:.0f}, {y:.0f})")
    
    def _on_edge_created(self, canvas, edge_id: str, source: str, target: str, handle: str):
        """Handle edge created"""
        self._update_status(f"Created edge from {source} to {target}")
    
    def _on_viewport_changed(self, canvas, x: float, y: float, zoom: float):
        """Handle viewport changed"""
        self._update_zoom_label()
    
    def _update_zoom_label(self):
        """Update zoom label"""
        if self.canvas and self.zoom_label:
            zoom_percent = int(self.canvas.viewport.zoom * 100)
            self.zoom_label.set_label(f"{zoom_percent}%")
    
    def _update_status(self, message: str):
        """Update status bar"""
        if hasattr(self, '_status_label'):
            self._status_label.set_label(message)
    
    def load_sample_graph(self):
        """Load a sample graph for testing"""
        if not self.canvas:
            return
        
        # Create sample nodes
        self.nodes = [
            {
                'id': 'node-1',
                'label': 'STT',
                'type': 'speech_to_text',
                'position': {'x': 100, 'y': 100},
                'data': {}
            },
            {
                'id': 'node-2',
                'label': 'LLM',
                'type': 'llm_chat',
                'position': {'x': 300, 'y': 100},
                'data': {}
            },
            {
                'id': 'node-3',
                'label': 'TTS',
                'type': 'text_to_speech',
                'position': {'x': 500, 'y': 100},
                'data': {}
            }
        ]
        
        # Create sample edges
        self.edges = [
            {
                'id': 'edge-1',
                'source': 'node-1',
                'target': 'node-2',
                'sourceHandle': 'output',
                'targetHandle': 'input'
            },
            {
                'id': 'edge-2',
                'source': 'node-2',
                'target': 'node-3',
                'sourceHandle': 'output',
                'targetHandle': 'input'
            }
        ]
        
        # Update canvas
        self.canvas.set_nodes(self.nodes)
        self.canvas.set_edges(self.edges)
        self._update_status("Sample graph loaded")

    def _on_save_graph(self, button):
        """Handle save graph button"""
        self._update_status("Saving graph...")

        # Get current canvas state
        nodes = self.canvas.nodes if self.canvas else []
        edges = self.canvas.edges if self.canvas else []

        if not nodes:
            self._update_status("❌ No nodes to save")
            return

        # Serialize to protobuf
        try:
            graph = self.serializer.serialize_graph(
                nodes=nodes,
                edges=edges,
                graph_name="My Graph",
                graph_type="dag"
            )

            # Save asynchronously
            asyncio.create_task(self._save_graph_async(graph))

        except Exception as e:
            self._update_status(f"❌ Error serializing graph: {e}")
            print(f"Error: {e}")

    async def _save_graph_async(self, graph):
        """Save graph to document store asynchronously"""
        try:
            await self.doc_store_client.connect()
            await self.doc_store_client.save_graph(graph)
            self._update_status(f"✅ Graph saved: {graph.name}")
            await self.doc_store_client.disconnect()
        except Exception as e:
            self._update_status(f"❌ Failed to save graph: {e}")
            print(f"Error: {e}")

    def _on_load_graph(self, button):
        """Handle load graph button"""
        self._update_status("Loading graph...")

        # For now, load sample graph
        # In future, this would open a dialog to select a graph
        self.load_sample_graph()

    def _update_status(self, message: str):
        """Update status bar message"""
        if hasattr(self, '_status_label'):
            self._status_label.set_label(message)

    def execute_graph(self):
        """Execute the current graph"""
        if not self.canvas or not self.canvas.nodes:
            self._update_status("❌ No graph to execute")
            return

        self._update_status("Executing graph...")

        # Serialize graph
        try:
            graph = self.serializer.serialize_graph(
                nodes=self.canvas.nodes,
                edges=self.canvas.edges,
                graph_name="Execution Graph",
                graph_type="dag"
            )

            # Execute asynchronously
            asyncio.create_task(self._execute_graph_async(graph))

        except Exception as e:
            self._update_status(f"❌ Error executing graph: {e}")
            print(f"Error: {e}")

    async def _execute_graph_async(self, graph):
        """Execute graph and stream events"""
        try:
            await self.graph_service_client.connect()

            # Create graph in service
            graph_id = await self.graph_service_client.create_graph(graph)

            # Execute graph
            execution_id = await self.graph_service_client.execute_graph(graph_id)
            self.current_execution_id = execution_id

            self._update_status(f"Execution started: {execution_id}")

            # Stream execution events
            async for event in self.graph_service_client.stream_execution(execution_id):
                self._handle_execution_event(event)

            await self.graph_service_client.disconnect()

        except Exception as e:
            self._update_status(f"❌ Execution failed: {e}")
            print(f"Error: {e}")

    def _handle_execution_event(self, event):
        """Handle execution event and update canvas"""
        event_type = event.event_type
        node_id = event.node_id

        if event_type == "EXECUTION_STARTED":
            self._update_status("⏳ Execution started")

        elif event_type == "NODE_STARTED":
            # Update node status to running
            self._update_node_status(node_id, "running")
            self._update_status(f"⏳ Running node: {node_id}")

        elif event_type == "NODE_COMPLETED":
            # Update node status to completed
            self._update_node_status(node_id, "completed")
            self._update_status(f"✅ Completed node: {node_id}")

        elif event_type == "NODE_FAILED":
            # Update node status to failed
            self._update_node_status(node_id, "failed")
            error_msg = event.event_data.get('error', 'Unknown error') if event.event_data else 'Unknown error'
            self._update_status(f"❌ Failed node: {node_id} - {error_msg}")

        elif event_type == "EXECUTION_COMPLETED":
            self._update_status("✅ Execution completed")

        elif event_type == "EXECUTION_FAILED":
            error_msg = event.event_data.get('error', 'Unknown error') if event.event_data else 'Unknown error'
            self._update_status(f"❌ Execution failed: {error_msg}")

        elif event_type == "EXECUTION_CANCELLED":
            self._update_status("⏹️ Execution cancelled")

    def _update_node_status(self, node_id: str, status: str):
        """Update node status in canvas"""
        if not self.canvas:
            return

        # Find and update node
        for node in self.canvas.nodes:
            if node.get('id') == node_id:
                node['status'] = status
                break

        # Redraw canvas
        self.canvas.queue_draw()

