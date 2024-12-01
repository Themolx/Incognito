# BatchRenderWriteNodes.py v1.3
#
# This script renders selected Write nodes and shows progress in a single window.
# Usage: Select Write nodes in Nuke's node graph, run the script.
# Click 'Go' to start rendering after reviewing the nodes to be rendered.
#
# Features:
# - Single window interface
# - Shows all Write nodes to be rendered
# - Progress updates in real-time
# - Go button to start rendering
# - Error handling
#
# Author: Claude
# Last Updated: 2024-11-29

import nuke
from PySide2 import QtWidgets, QtCore
import re

# User Variables 
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 300
WINDOW_TITLE = "Batch Render Progress"

class RenderWindow(QtWidgets.QDialog):
    def __init__(self, write_nodes):
        super().__init__()
        
        self.write_nodes = write_nodes
        self.completed_renders = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Window setup
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)
        
        # Main layout
        layout = QtWidgets.QVBoxLayout()
        
        # Info header
        self.header_label = QtWidgets.QLabel(f"Found {len(self.write_nodes)} Write nodes to render:")
        layout.addWidget(self.header_label)
        
        # Create text area for nodes
        self.info_text = QtWidgets.QTextEdit()
        self.info_text.setReadOnly(True)
        
        # Populate node information
        node_info = ""
        for node in self.write_nodes:
            start = int(node['first'].value())
            end = int(node['last'].value())
            node_info += f"Node: {node.name()}\n"
            node_info += f"Frame Range: {start}-{end}\n"
            node_info += "-" * 40 + "\n"
        
        self.info_text.setText(node_info)
        layout.addWidget(self.info_text)
        
        # Progress section
        self.progress_label = QtWidgets.QLabel("Ready to render...")
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setMaximum(len(self.write_nodes))
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Current render label
        self.current_render_label = QtWidgets.QLabel("Waiting to start...")
        layout.addWidget(self.current_render_label)
        
        # Go button
        self.go_button = QtWidgets.QPushButton("Go")
        self.go_button.clicked.connect(self.start_render)
        layout.addWidget(self.go_button)
        
        self.setLayout(layout)
        
    def update_progress(self, node_name):
        """Update progress display"""
        self.completed_renders += 1
        self.progress_bar.setValue(self.completed_renders)
        self.progress_label.setText(f"Completed: {self.completed_renders}/{len(self.write_nodes)} renders")
        self.current_render_label.setText(f"Current: {node_name}")
        
        # Process events to show updates
        QtWidgets.QApplication.processEvents()
        
    def start_render(self):
        """Start the rendering process"""
        self.go_button.setEnabled(False)
        self.go_button.setText("Rendering...")
        
        try:
            # Store original ranges
            original_ranges = {}
            
            for node in self.write_nodes:
                try:
                    # Store original range
                    original_ranges[node] = (int(node['first'].value()), int(node['last'].value()))
                    
                    # Execute render
                    start = int(node['first'].value())
                    end = int(node['last'].value())
                    print(f"Rendering {node.name()} frames {start}-{end}")
                    
                    self.current_render_label.setText(f"Rendering: {node.name()}")
                    nuke.execute(node, start, end)
                    self.update_progress(node.name())
                    
                except Exception as e:
                    nuke.message(f"Error rendering {node.name()}: {str(e)}")
                    
        finally:
            # Restore original ranges
            for node, (start, end) in original_ranges.items():
                node['first'].setValue(start)
                node['last'].setValue(end)
            
            self.go_button.setText("Complete!")
            self.current_render_label.setText("All renders completed!")

def render_write_nodes():
    """Main function to handle Write node rendering."""
    
    # Get selected Write nodes
    write_nodes = [n for n in nuke.selectedNodes() if n.Class() == "Write"]
    
    if not write_nodes:
        nuke.message("Please select at least one Write node.")
        return
    
    # Create and show window
    render_window = RenderWindow(write_nodes)
    render_window.exec_()

if __name__ == "__main__":
    render_write_nodes()
