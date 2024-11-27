import json
import nuke
from PySide2.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QTableWidget,
                             QFileDialog, QMessageBox, QTableWidgetItem,
                             QSpinBox)

class ShotDurationCalculator(QDialog):
    def __init__(self, parent=None):
        super(ShotDurationCalculator, self).__init__(parent)
        self.shots_data = None
        self.handle_frames = 15  # Default handle length
        self.base_start = 1001   # Default start frame
        self.setupUI()
        
    def setupUI(self):
        """Setup the UI elements"""
        self.setWindowTitle("Shot Duration Calculator")
        self.setMinimumWidth(1200)  # Increased width for more columns
        self.setMinimumHeight(600)
        
        # Create main layout
        main_layout = QVBoxLayout()
        
        # JSON section
        json_layout = QHBoxLayout()
        self.path_label = QLabel("No JSON loaded")
        self.path_label.setWordWrap(True)
        load_btn = QPushButton("Load Moloch JSON")
        load_btn.clicked.connect(self.loadJSON)
        json_layout.addWidget(self.path_label)
        json_layout.addWidget(load_btn)
        main_layout.addLayout(json_layout)
        
        # Handle settings
        handle_layout = QHBoxLayout()
        handle_layout.addWidget(QLabel("Handle Frames:"))
        self.handle_spin = QSpinBox()
        self.handle_spin.setMinimum(0)
        self.handle_spin.setMaximum(1000)
        self.handle_spin.setValue(self.handle_frames)
        self.handle_spin.valueChanged.connect(self.handleValueChanged)
        handle_layout.addWidget(self.handle_spin)
        
        # Start frame settings
        handle_layout.addWidget(QLabel("Base Start Frame:"))
        self.start_spin = QSpinBox()
        self.start_spin.setMinimum(0)
        self.start_spin.setMaximum(10000)
        self.start_spin.setValue(self.base_start)
        self.start_spin.valueChanged.connect(self.startFrameChanged)
        handle_layout.addWidget(self.start_spin)
        
        handle_layout.addStretch()
        main_layout.addLayout(handle_layout)
        
        # Table for displaying durations
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "Shot",
            "Source Start Frame",
            "Source End Frame", 
            "Source Duration (frames)",
            "Source Duration with Handles (frames)",
            "Source Range with Handles",
            "Relative Start Frame",
            "Relative End Frame",
            "Relative Duration (frames)",
            "Relative Duration with Handles (frames)",
            "Relative Range with Handles"
        ])
        main_layout.addWidget(self.table)
        
        # Add export button
        export_btn = QPushButton("Export to Text File")
        export_btn.clicked.connect(self.exportToText)
        main_layout.addWidget(export_btn)
        
        self.setLayout(main_layout)
    
    def handleValueChanged(self, value):
        """Update handle frames value and recalculate"""
        self.handle_frames = value
        if self.shots_data:
            self.calculateDurations()
    
    def startFrameChanged(self, value):
        """Update base start frame and recalculate"""
        self.base_start = value
        if self.shots_data:
            self.calculateDurations()
    
    def loadJSON(self):
        """Load the JSON file and calculate durations"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Moloch JSON file",
                "",
                "JSON Files (*.json)"
            )
            
            if not file_path:
                return
            
            with open(file_path, 'r') as f:
                self.shots_data = json.load(f)
            
            self.path_label.setText(f"Loaded: {file_path}")
            self.calculateDurations()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load JSON: {str(e)}"
            )
    
    def calculateDurations(self):
        """Calculate and display shot durations"""
        if not self.shots_data or 'markers' not in self.shots_data:
            return
        
        markers = self.shots_data['markers']
        self.table.setRowCount(len(markers) - 1)  # One less than markers as we need pairs
        
        for i in range(len(markers) - 1):
            current_shot = markers[i]
            next_shot = markers[i + 1]
            
            # Calculate source durations (original frames)
            start_frame = current_shot['frame']
            end_frame = next_shot['frame'] - 1
            duration_frames = end_frame - start_frame + 1
            duration_seconds = duration_frames / float(self.shots_data.get('frameRate', 25))
            
            # Calculate frames with handles (source)
            handle_duration = duration_frames + (self.handle_frames * 2)
            first_frame_with_handles = start_frame - self.handle_frames
            last_frame_with_handles = end_frame + self.handle_frames
            
            # Calculate relative frames (starting from base_start)
            relative_start = self.base_start
            relative_end = self.base_start + duration_frames - 1
            relative_duration = duration_frames
            relative_first_with_handles = self.base_start - self.handle_frames
            relative_last_with_handles = relative_end + self.handle_frames
            
            # Create table items
            items = [
                current_shot['shotNumber'],
                str(start_frame),
                str(end_frame),
                str(duration_frames),
                str(handle_duration),
                f"{first_frame_with_handles}-{last_frame_with_handles}",
                str(relative_start),
                str(relative_end),
                str(relative_duration),
                str(handle_duration),
                f"{relative_first_with_handles}-{relative_last_with_handles}"
            ]
            
            for col, item in enumerate(items):
                self.table.setItem(i, col, QTableWidgetItem(item))
        
        # Resize columns to content
        self.table.resizeColumnsToContents()
    
    def exportToText(self):
        """Export the duration data to a text file"""
        if not self.shots_data:
            return
            
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Duration Report",
                "",
                "Text Files (*.txt)"
            )
            
            if not file_path:
                return
                
            with open(file_path, 'w') as f:
                f.write(f"Shot Duration Report\n")
                f.write(f"Handle Frames: {self.handle_frames}\n")
                f.write(f"Base Start Frame: {self.base_start}\n")
                f.write("-" * 80 + "\n\n")
                
                for row in range(self.table.rowCount()):
                    shot_num = self.table.item(row, 0).text()
                    source_range = f"{self.table.item(row, 1).text()}-{self.table.item(row, 2).text()}"
                    duration = self.table.item(row, 3).text()
                    duration_sec = self.table.item(row, 4).text()
                    source_handles = self.table.item(row, 6).text()
                    relative_range = f"{self.table.item(row, 8).text()}-{self.table.item(row, 9).text()}"
                    relative_handles = self.table.item(row, 11).text()
                    
                    f.write(f"Shot: {shot_num}\n")
                    f.write(f"Source Range: {source_range} ({duration} frames, {duration_sec} seconds)\n")
                    f.write(f"Source with Handles: {source_handles}\n")
                    f.write(f"Relative Range: {relative_range}\n")
                    f.write(f"Relative with Handles: {relative_handles}\n")
                    f.write("-" * 40 + "\n")
            
            QMessageBox.information(
                self,
                "Success",
                "Duration report exported successfully!"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to export report: {str(e)}"
            )

def show_duration_calculator():
    """Show the Shot Duration Calculator dialog"""
    dialog = ShotDurationCalculator()
    dialog.exec_()

# Add to menu.py:
# import NukeShotDurationCalculator
# toolbar = nuke.toolbar('Tools')
# toolbar.addCommand('Shot Duration Calculator', 'NukeShotDurationCalculator.show_duration_calculator()')
