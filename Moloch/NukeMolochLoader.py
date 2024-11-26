import json
import nuke
from PySide2.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QComboBox, 
                             QFileDialog, QMessageBox)

class ShotFrameSelector(QDialog):
    def __init__(self, parent=None):
        super(ShotFrameSelector, self).__init__(parent)
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
        self.setWindowTitle("Shot Frame Selector")
        self.setMinimumWidth(400)
        
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
        load_btn = QPushButton("Load JSON")
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
        
        # Info display
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("QLabel { background-color: #2f2f2f; padding: 10px; }")
        main_layout.addWidget(self.info_label)
        
        # Apply button
        self.apply_btn = QPushButton("Apply Frame to Read Node")
        self.apply_btn.setEnabled(False)
        self.apply_btn.clicked.connect(self.applyFrame)
        main_layout.addWidget(self.apply_btn)
        
        self.setLayout(main_layout)
    
    def loadJSON(self):
        """Load the JSON file containing shot data"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select JSON file",
                "",
                "JSON Files (*.json)"
            )
            
            if not file_path:
                return
            
            with open(file_path, 'r') as f:
                self.shots_data = json.load(f)
            
            self.path_label.setText(f"Loaded: {file_path}")
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
        
        # Add shots to combo box
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
        """Apply the selected frame to the Read node's 'first' frame"""
        if not self.read_node:
            QMessageBox.warning(self, "Warning", "Please select a Read node first!")
            return
            
        try:
            marker = self.shot_combo.currentData()
            frame = marker['frame']
            
            # Begin undo group
            nuke.Undo().begin("Set Read Node First Frame")
            
            # Set the first frame
            self.read_node['first'].setValue(frame)
            
            # Update original range if needed
            if 'origfirst' in self.read_node.knobs():
                self.read_node['origfirst'].setValue(frame)
            
            nuke.Undo().end()
            
            QMessageBox.information(
                self,
                "Success",
                f"Set first frame to {frame} for node: {self.read_node.name()}"
            )
            
        except Exception as e:
            nuke.Undo().cancel()
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to set frame: {str(e)}"
            )

# Direct execution
dialog = ShotFrameSelector()
dialog.exec_()
