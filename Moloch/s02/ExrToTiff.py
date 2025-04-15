import nuke
import os
from datetime import datetime

def create_write_nodes_for_selected_reads():
    # Get current date in YYYYMMDD format for the conversion folder
    today = datetime.now().strftime("%Y%m%d")
    
    # Define source and destination paths
    base_path = "Y:/MOLOCH_02426/sources/_raw_material/EP02"
    output_folder = "Tiff_Convert"
    
    # Get all selected Read nodes
    selected_reads = [n for n in nuke.selectedNodes() if n.Class() == "Read"]
    
    if not selected_reads:
        nuke.message("No Read nodes selected. Please select at least one Read node.")
        return
    
    for read in selected_reads:
        # Get the file path from the Read node
        read_path = read['file'].value()
        
        # Extract folder name from the read path
        path_parts = read_path.split('/')
        
        # Find the EP02 part and get the subsequent folder
        for i, part in enumerate(path_parts):
            if part == "EP02" and i+1 < len(path_parts):
                folder_name = path_parts[i+1]
                break
        else:
            # If EP02 not found or it's the last part, use a default folder name
            folder_name = "default_folder"
        
        # Create the output path
        output_dir = f"{base_path}/{output_folder}/{folder_name}"
        
        # Get the filename from the original path
        filename = os.path.basename(read_path)
        
        # Change extension from exr to tiff
        if filename.endswith('.exr'):
            filename = filename.replace('.exr', '.tiff')
        elif '%' in filename and '.exr' in filename:  # Handle frame ranges
            filename = filename.replace('.exr', '.tiff')
        
        # Create the complete output path
        output_path = f"{output_dir}/{filename}"
        
        # Create Write node
        write = nuke.createNode("Write", inpanel=False)
        
        # Connect the Write to the Read
        write.setInput(0, read)
        
        # Set Write node parameters
        write['file'].setValue(output_path)
        write['colorspace'].setValue("color_picking")  # sRGB conversion
        write['file_type'].setValue("tiff")
        write['datatype'].setValue("16 bit")
        write['checkHashOnRead'].setValue(False)
        write['create_directories'].setValue(True)  # Enable directory creation
        
        # Position the Write node below the Read
        read_pos = (read.xpos(), read.ypos())
        write.setXYpos(read_pos[0] + 5, read_pos[1] + 132)  # Position slightly offset and below
        
        print(f"Created Write node for {read.name()} -> {output_path}")
        print(f"Output directory: {output_dir}")

# Run the function
create_write_nodes_for_selected_reads()
