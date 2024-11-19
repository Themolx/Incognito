import nuke
import json
import os
from datetime import datetime

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

def export_node_data():
    """
    Main function to export transform and corner pin data from selected nodes
    """
    # Get selected nodes
    selected_nodes = nuke.selectedNodes()
    valid_nodes = [n for n in selected_nodes if n.Class() in ('Transform', 'CornerPin2D')]
    
    if not valid_nodes:
        nuke.message('Please select at least one Transform or CornerPin2D node')
        return
    
    # Prepare export data
    export_data = {
        'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'nuke_version': nuke.NUKE_VERSION_STRING,
        'nodes': {}
    }
    
    # Collect data from each selected node
    for node in valid_nodes:
        node_name = node.name()
        node_class = node.Class()
        
        export_data['nodes'][node_name] = {
            'type': node_class,
            'data': get_transform_data(node) if node_class == 'Transform' else get_cornerpin_data(node)
        }
    
    # Get export path
    script_path = nuke.root().name()
    if not script_path:
        script_path = os.path.expanduser('~')
    
    default_path = os.path.join(
        os.path.dirname(script_path),
        'node_transform_data.json'
    )
    
    # Show file dialog
    export_path = nuke.getFilename(
        'Save Node Data',
        '*.json',
        default_path,
        type='save'
    )
    
    if export_path:
        try:
            # Ensure the file has .json extension
            if not export_path.endswith('.json'):
                export_path += '.json'
                
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=4)
            nuke.message(f'Node data successfully exported to:\n{export_path}')
        except Exception as e:
            nuke.message(f'Error exporting node data:\n{str(e)}')

def create_menu():
    """
    Create menu items for the export functionality
    """
    toolbar = nuke.menu('Nuke')
    m = toolbar.addMenu('Scripts')
    m.addCommand('Export Transform/CornerPin Data', export_node_data)

# Create menu when the script is loaded
create_menu()

# You can also call it directly for testing
# export_node_data()