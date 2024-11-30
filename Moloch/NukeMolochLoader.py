# NukeMolochLoader_v1.1
#
# This script creates a Moloch Frame Selector tool for Nuke that allows users to:
# 1. Select a Read node
# 2. Load a JSON file containing shot/frame data from Moloch timeline markers
# 3. Select a shot from loaded data
# 4. Create a Retime node with input range from JSON and output range starting at 1001
#
# Usage:
# 1. Place script in ~/.nuke directory
# 2. Add to menu.py:
# import NukeMolochLoader
# toolbar = nuke.toolbar('Nodes')
# toolbar.addCommand('Tools/Moloch Loader', 'NukeMolochLoader.show_dialog()')

import json
import nuke
import os
from PySide2.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QComboBox, 
                             QFileDialog, QMessageBox, QCheckBox)

# User variables
WINDOW_TITLE = "Moloch Frame Selector"
WINDOW_MIN_WIDTH = 400
MOLOCH_MARKERS_PATH = r"Y:\MOLOCH_02426\assets\assets2D\Inserts_EP01\InsertTimelineMarkers"
BACKGROUND_COLOR = "#2f2f2f"
PADDING = "10px"

class MolochLoader(QDialog):
    def __init__(self, parent=None):
        super(MolochLoader, self).__init__(parent)
        self.shots_data = None
        self.read_node = self.getSelectedReadNode()
        self.setupUI()
        
    def getSelectedReadNode(self):
        """Check if a Read node is selected"""
        selected = nuke.selectedNodes()
        if not selected or selected[0].Class() != "Read":
            nuke.message("Please select a Read node!")
            return None
        return selected[0]
        
    def setupUI(self):
        """Setup the UI elements"""
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumWidth(WINDOW_MIN_WIDTH)
        
        # Create main layout
        main_layout = QVBoxLayout()
        
        # Node info
        node_name = self.read_node.name() if self.read_node else "No Read node selected"
        node_info = QLabel(f"Selected Read Node: {node_name}")
        main_layout.addWidget(node_info)
        
        # JSON section
        json_layout = QHBoxLayout()
        self.path_label = QLabel("No JSON loaded")
        self.path_label.setWordWrap(True)
        load_btn = QPushButton("Load Moloch JSON")
        load_btn.clicked.connect(self.loadJSON)
        json_layout.addWidget(self.path_label)
        json_layout.addWidget(load_btn)
        main_layout.addLayout(json_layout)
        
        # Shot selector
        shot_layout = QHBoxLayout()
        shot_layout.addWidget(QLabel("Select Shot:"))
        self.shot_combo = QComboBox()
        self.shot_combo.setEnabled(False)
        self.shot_combo.currentIndexChanged.connect(self.updateShotInfo)
        shot_layout.addWidget(self.shot_combo)
        main_layout.addLayout(shot_layout)
        
        # Frame range info
        range_info = QLabel("Input range will be set to JSON frame\nOutput range will start at 1001")
        range_info.setStyleSheet(f"QLabel {{ background-color: {BACKGROUND_COLOR}; padding: {PADDING}; }}")
        main_layout.addWidget(range_info)
        
        # Info display
        self.info_label = QLabel("")
        self.info_label.setStyleSheet(f"QLabel {{ background-color: {BACKGROUND_COLOR}; padding: {PADDING}; }}")
        main_layout.addWidget(self.info_label)
        
        # Apply button
        self.apply_btn = QPushButton("Create Retime Node")
        self.apply_btn.setEnabled(False)
        self.apply_btn.clicked.connect(self.applyFrame)
        main_layout.addWidget(self.apply_btn)
        
        self.setLayout(main_layout)
    
    def loadJSON(self):
        """Load the JSON file containing shot data"""
        try:
            # Create the directory if it doesn't exist
            if not os.path.exists(MOLOCH_MARKERS_PATH):
                os.makedirs(MOLOCH_MARKERS_PATH)
                
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Moloch JSON file",
                MOLOCH_MARKERS_PATH,  # Start in the Moloch markers directory
                "JSON Files (*.json)"
            )
            
            if not file_path:
                return
            
            with open(file_path, 'r') as f:
                self.shots_data = json.load(f)
            
            self.path_label.setText(f"Loaded: {os.path.basename(file_path)}")
            self.populateShots()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load JSON: {str(e)}"
            )
    
    def populateShots(self):
        """Populate the shot dropdown with data from JSON"""
        if not self.shots_data or 'markers' not in self.shots_data:
            return
        
        self.shot_combo.clear()
        self.shot_combo.setEnabled(True)
        self.apply_btn.setEnabled(True)
        
        for marker in self.shots_data['markers']:
            self.shot_combo.addItem(
                f"Shot_{marker['shotNumber']} (Frame {marker['frame']})",
                marker
            )
    
    def updateShotInfo(self):
        """Update the information display when a shot is selected"""
        if self.shot_combo.currentIndex() < 0:
            return
            
        marker = self.shot_combo.currentData()
        info_text = (
            f"Shot Number: {marker['shotNumber']}\n"
            f"Frame: {marker['frame']}\n"
            f"Timecode: {marker['timecode']}\n"
            f"Seconds: {marker['seconds']}"
        )
        self.info_label.setText(info_text)
    
    def applyFrame(self):
        """Create a Retime node with input range from JSON and output range starting at 1001"""
        if not self.read_node:
            QMessageBox.warning(self, "Warning", "Please select a Read node first!")
            return
            
        try:
            marker = self.shot_combo.currentData()
            input_first = int(marker['frame'])  # Convert to int since we know it's already a number
            frame_count = 115  # This will make the range span 115 frames (1116 - 1001 = 115)
            shot_name = f"Shot_{marker['shotNumber']}"
            
            # Create the TCL command for the Retime node
            tcl_cmd = f'''
            set cut_paste_input [stack 0]
            version 14.0 v5
            push $cut_paste_input
            Retime {{
                input.first {input_first}
                input.first_lock true
                input.last {input_first + frame_count}
                output.first 1001
                output.first_lock true
                output.last {1001 + frame_count}
                before continue
                after continue
                time ""
                name "Retime_{shot_name}"
                selected true
            }}
            '''
            
            # Execute the TCL command
            nuke.tcl(tcl_cmd)
            
            QMessageBox.information(
                self,
                "Success",
                f"Created Retime_{shot_name} node with input range {input_first}-{input_first + frame_count} "
                f"and output range 1001-{1001 + frame_count}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to create Retime node: {str(e)}"
            )

def show_dialog():
    """Show the Moloch Loader dialog"""
    dialog = MolochLoader()
    dialog.exec_()
show_dialog()
