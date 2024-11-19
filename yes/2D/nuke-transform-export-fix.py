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

def export_transform_data():
    """
    Main function to export transform data from selected nodes
    """
    # Get selected nodes
    selected_nodes = nuke.selectedNodes('Transform')
    
    if not selected_nodes:
        nuke.message('Please select at least one Transform node')
        return
    
    # Prepare export data
    export_data = {
        'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'nuke_version': nuke.NUKE_VERSION_STRING,
        'nodes': {}
    }
    
    # Collect data from each selected transform node
    for node in selected_nodes:
        node_name = node.name()
        export_data['nodes'][node_name] = get_transform_data(node)
    
    # Get export path
    script_path = nuke.root().name()
    if not script_path:
        script_path = os.path.expanduser('~')
    
    default_path = os.path.join(
        os.path.dirname(script_path),
        'transform_data.json'
    )
    
    # Show file dialog - fixed the getFilename parameters
    export_path = nuke.getFilename(
        'Save Transform Data',
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
            nuke.message(f'Transform data successfully exported to:\n{export_path}')
        except Exception as e:
            nuke.message(f'Error exporting transform data:\n{str(e)}')

# Create a menu if it doesn't exist
toolbar = nuke.menu('Nuke')
m = toolbar.addMenu('Scripts')
m.addCommand('Export Transform Data', export_transform_data)

# You can also call it directly for testing
# export_transform_data()
