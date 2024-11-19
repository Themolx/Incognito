from PySide2.QtWidgets import *
from PySide2.QtCore import *
from mocha.ui import get_widgets
from mocha.project import get_current_project
import os
from pathlib import Path
import json

# Get the main Mocha window to parent our dialog
main_window = get_widgets()['MainWindow']

class QuickExportDialog(QDialog):
    def __init__(self, parent=main_window):
        super(QuickExportDialog, self).__init__(parent)
        self.setup_ui()
        self.process_current_path()
        
    def setup_ui(self):
        self.setWindowTitle("Quick Pipeline Export")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Current Project Info
        proj_group = QGroupBox("Current Project")
        proj_layout = QFormLayout()
        self.proj_path = QLabel()
        proj_layout.addRow("Path:", self.proj_path)
        proj_group.setLayout(proj_layout)
        layout.addWidget(proj_group)
        
        # Export Paths
        export_group = QGroupBox("Export Settings")
        export_layout = QFormLayout()
        
        self.ae_path = QLineEdit()
        self.nuke_path = QLineEdit()
        
        # Add browse buttons
        ae_browse = QPushButton("Browse")
        ae_browse.clicked.connect(lambda: self.browse_path(self.ae_path, "AE Export (*.json)"))
        ae_layout = QHBoxLayout()
        ae_layout.addWidget(self.ae_path)
        ae_layout.addWidget(ae_browse)
        
        nuke_browse = QPushButton("Browse")
        nuke_browse.clicked.connect(lambda: self.browse_path(self.nuke_path, "Nuke Script (*.nk)"))
        nuke_layout = QHBoxLayout()
        nuke_layout.addWidget(self.nuke_path)
        nuke_layout.addWidget(nuke_browse)
        
        export_layout.addRow("After Effects:", ae_layout)
        export_layout.addRow("Nuke:", nuke_layout)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self.do_export)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def browse_path(self, line_edit, file_filter):
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Select Export Path",
            line_edit.text(),
            file_filter
        )
        if file_path:
            line_edit.setText(file_path)
    
    def process_current_path(self):
        proj = get_current_project()
        if proj and proj.project_file:
            # Show current project path
            self.proj_path.setText(proj.project_file)
            
            # Get project directory
            proj_dir = str(Path(proj.project_file).parent)
            
            # Set default export paths
            self.ae_path.setText(os.path.join(proj_dir, "ae_export.json"))
            self.nuke_path.setText(os.path.join(proj_dir, "nuke_export.nk"))
    
    def do_export(self):
        try:
            proj = get_current_project()
            if not proj:
                raise Exception("No project loaded")
            
            # Create export directories
            for path in [self.ae_path.text(), self.nuke_path.text()]:
                os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Export AE Data
            ae_data = {
                'project': proj.project_file,
                'layers': []
            }
            
            # Export Nuke Data
            nuke_data = []
            nuke_data.append('# Mocha Export for Nuke\n\n')
            
            # Process each visible layer
            for layer in proj.layers:
                if not layer.visible:
                    continue
                    
                # Get layer data
                layer_data = {
                    'name': layer.name,
                    'frames': []
                }
                
                in_point = layer.parameter(['Basic', 'In_Point']).get()
                out_point = layer.parameter(['Basic', 'Out_Point']).get()
                
                # Add transform data for each frame
                for frame in range(in_point, out_point + 1):
                    ps = layer.parameter_set()
                    
                    frame_data = {
                        'frame': frame,
                        'scale_x': ps['Surface Scale X'].get(time=frame),
                        'scale_y': ps['Surface Scale Y'].get(time=frame),
                        'rotation': ps['Surface Angle'].get(time=frame),
                        'center_x': ps['Surface Center X'].get(time=frame),
                        'center_y': ps['Surface Center Y'].get(time=frame)
                    }
                    layer_data['frames'].append(frame_data)
                
                ae_data['layers'].append(layer_data)
                
                # Add Nuke node
                nuke_data.append(f'Transform {{\n')
                nuke_data.append(f'  name Mocha_{layer.name}\n')
                nuke_data.append('  selected true\n')
                nuke_data.append('}\n\n')
            
            # Write AE JSON
            with open(self.ae_path.text(), 'w') as f:
                json.dump(ae_data, f, indent=2)
            
            # Write Nuke Script
            with open(self.nuke_path.text(), 'w') as f:
                f.writelines(nuke_data)
            
            QMessageBox.information(self, "Success", "Export completed successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")

# Create and show the dialog
dialog = QuickExportDialog()
dialog.show()
