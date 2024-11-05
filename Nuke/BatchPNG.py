def create_png_writes():
    # Get all selected nodes
    selected_nodes = nuke.selectedNodes('Read')
    
    for read_node in selected_nodes:
        # Create Write node
        write_node = nuke.createNode('Write', inpanel=False)
        
        # Position write node below the read node
        write_node.setXYpos(read_node.xpos(), read_node.ypos() + 100)
        
        # Connect write node to read node
        write_node.setInput(0, read_node)
        
        # Get read node's file path
        original_path = read_node['file'].value()
        import os
        
        # Split the path into components
        directory = os.path.dirname(original_path)
        filename = os.path.basename(original_path)
        name_without_ext = os.path.splitext(filename)[0]
        
        # Remove any existing frame patterns from the filename
        import re
        name_clean = re.sub(r'\.?%\d*d|\.?\#+', '', name_without_ext)
        
        # Create png subfolder path and maintain Windows separators
        png_directory = directory + '/png'
        
        # Construct new path with frame pattern at the end
        new_path = png_directory + '/' + name_clean + '_png_sRGB.%04d.png'
        
        # Configure write node settings
        write_node['file'].setValue(new_path)
        write_node['channels'].setValue('rgba')
        write_node['file_type'].setValue('png')
        write_node['create_directories'].setValue(True)
        write_node['checkHashOnRead'].setValue(False)
        write_node['colorspace'].setValue('color_picking')

# Execute the function
create_png_writes()
