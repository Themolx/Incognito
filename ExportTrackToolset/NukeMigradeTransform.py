# Transform_Export_Tools_v1.0.py
#
# This script provides two tools for exporting transform data from Nuke:
# 1. Transform Only Export - Exports only Transform node data
# 2. Transform and CornerPin Export - Exports both Transform and CornerPin2D node data
#
# Usage:
# The script adds two menu items under Scripts > Transform Export Tools:
# - Export Transform Data
# - Export Transform/CornerPin Data
#
# Each tool provides:
# - Export of static and animated values
# - JSON formatted output
# - Automatic frame range detection
# - Comprehensive error handling
# - Clear user feedback
#
# Note: Always keep your version control up to date

import nuke
import json
import os
from datetime import datetime

# User variables - Customize these as needed
DEFAULT_EXPORT_DIR = '' # Leave empty to use script directory
MENU_NAME = 'Transform Export Tools'
DEBUG_MODE = False  # Set to True for additional console output

def debug_print(message):
    """Utility function for debug printing"""
    if DEBUG_MODE:
        print(f"DEBUG: {message}")

def get_transform_data(node):
    """
    Extract transform data from a transform node
    Returns a dictionary of keyframed values or static values
    """
    transform_data = {}
    
    # List of transform parameters to extract
    params = ['translate', 'rotate', 'scale', 'center', 'skewX', 'skewY']
    
    for param in params:
        # Handle potentially animated parameters
        knob = node[param]
        
        if knob.isAnimated():
            # Get frame range
            first_frame = nuke.root()['first_frame'].value()
            last_frame = nuke.root()['last_frame'].value()
            
            # Store animated values
            param_data = []
            for frame in range(int(first_frame), int(last_frame + 1)):
                if param in ['translate', 'scale', 'center']:
                    value = [knob.valueAt(frame, i) for i in range(2)]
                else:
                    value = knob.valueAt(frame)
                param_data.append({
                    'frame': frame,
                    'value': value
                })
            transform_data[param] = param_data
        else:
            # Store static values
            if param in ['translate', 'scale', 'center']:
                transform_data[param] = [knob.value(i) for i in range(2)]
            else:
                transform_data[param] = knob.value()
    
    return transform_data

def get_cornerpin_data(node):
    """
    Extract corner pin data from a CornerPin2D node
    Returns a dictionary of keyframed values or static values for to1-to4 and from1-from4
    """
    cornerpin_data = {}
    
    # List of corner pin parameters to extract
    params = ['to1', 'to2', 'to3', 'to4', 'from1', 'from2', 'from3', 'from4']
    
    for param in params:
        knob = node[param]
        
        if knob.isAnimated():
            # Get frame range
            first_frame = nuke.root()['first_frame'].value()
            last_frame = nuke.root()['last_frame'].value()
            
            # Store animated values
            param_data = []
            for frame in range(int(first_frame), int(last_frame + 1)):
                value = [knob.valueAt(frame, i) for i in range(2)]
                param_data.append({
                    'frame': frame,
                    'value': value
                })
            cornerpin_data[param] = param_data
        else:
            # Store static values
            cornerpin_data[param] = [knob.value(i) for i in range(2)]
    
    return cornerpin_data

def get_export_path(default_filename):
    """
    Get the export path from user with proper error handling
    """
    script_path = nuke.root().name()
    if not script_path or DEFAULT_EXPORT_DIR:
        base_path = DEFAULT_EXPORT_DIR or os.path.expanduser('~')
    else:
        base_path = os.path.dirname(script_path)
    
    default_path = os.path.join(base_path, default_filename)
    
    return nuke.getFilename(
        'Save Transform Data',
        '*.json',
        default_path,
        type='save'
    )

def export_data_to_file(export_data, export_path):
    """
    Export the data to a JSON file
    """
    try:
        if not export_path.endswith('.json'):
            export_path += '.json'
            
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=4)
        nuke.message(f'Data successfully exported to:\n{export_path}')
        debug_print(f"Export successful to {export_path}")
    except Exception as e:
        nuke.message(f'Error exporting data:\n{str(e)}')
        debug_print(f"Export failed: {str(e)}")

def export_transform_only():
    """
    Export only Transform node data
    """
    selected_nodes = nuke.selectedNodes('Transform')
    
    if not selected_nodes:
        nuke.message('Please select at least one Transform node')
        return
    
    export_data = {
        'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'nuke_version': nuke.NUKE_VERSION_STRING,
        'nodes': {}
    }
    
    for node in selected_nodes:
        node_name = node.name()
        export_data['nodes'][node_name] = get_transform_data(node)
    
    export_path = get_export_path('transform_data.json')
    if export_path:
        export_data_to_file(export_data, export_path)

def export_transform_and_cornerpin():
    """
    Export both Transform and CornerPin2D node data
    """
    selected_nodes = nuke.selectedNodes()
    valid_nodes = [n for n in selected_nodes if n.Class() in ('Transform', 'CornerPin2D')]
    
    if not valid_nodes:
        nuke.message('Please select at least one Transform or CornerPin2D node')
        return
    
    export_data = {
        'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'nuke_version': nuke.NUKE_VERSION_STRING,
        'nodes': {}
    }
    
    for node in valid_nodes:
        node_name = node.name()
        node_class = node.Class()
        
        export_data['nodes'][node_name] = {
            'type': node_class,
            'data': get_transform_data(node) if node_class == 'Transform' else get_cornerpin_data(node)
        }
    
    export_path = get_export_path('node_transform_data.json')
    if export_path:
        export_data_to_file(export_path, export_data)

def create_menu():
    """
    Create menu items for both export functionalities
    """
    toolbar = nuke.menu('Nuke')
    menu = toolbar.addMenu(MENU_NAME)
    menu.addCommand('Export Transform Data', export_transform_only)
    menu.addCommand('Export Transform/CornerPin Data', export_transform_and_cornerpin)
    debug_print("Menu items created successfully")

# Create menu when the script is loaded
create_menu()