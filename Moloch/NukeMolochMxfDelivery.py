#!/usr/bin/env python
# CreateDailiesWriteAndBurnin.py v1.0
#
# This script:
# 1. Takes all selected Read nodes
# 2. Creates Write nodes with EXR output settings
# 3. Adds text burn-in with frame number and shot name
#
# Usage: Select multiple Read nodes and run the script

import nuke
import re
import os
from datetime import datetime

def get_shot_mapping():
    """Return shot name mapping dictionaries."""
    shotlist = ["ME1_0050", "ME1_0060", "ME1_0070", "ME1_0080", "ME1_0090", "ME1_0110", "ME1_0120", "ME1_0130", "ME1_0150", "ME1_0170", "ME1_0190", "ME1_0210", "ME1_0220", "ME1_0230", "ME1_0250", "ME1_0260", "ME1_0270", "ME1_0290", "ME1_0300", "ME1_0310", "ME1_0320", "ME1_0330", "ME1_0340", "ME1_0350", "ME1_0360", "ME1_0370", "ME1_0380", "ME1_0390", "ME1_0400", "ME1_0410", "ME1_0420", "ME1_0430", "ME1_0440", "ME1_0470", "ME1_0480", "ME1_0490", "ME1_0500", "ME1_0510", "ME1_0520", "ME1_0570", "ME1_0580", "ME1_0590", "ME1_0700", "ME1_0710", "ME1_0720", "ME1_0730", "ME1_0740", "ME1_0750", "ME1_0760", "ME1_0770", "ME1_0780", "ME1_0790", "ME1_0800", "ME1_0810", "ME1_0830", "ME1_0832", "ME1_0850", "ME1_0860", "ME1_0870", "ME1_0880", "ME1_0900", "ME1_0910", "ME1_0920", "ME1_0930", "ME1_0940", "ME1_0950", "ME1_0960", "ME1_0970", "ME1_0980", "ME1_0990", "ME1_1000", "ME1_1010", "ME1_1020", "ME1_1030", "ME1_1040", "ME1_1050", "ME1_1060", "ME1_9990"]
    productlist = ["EP01_G_0050", "EP01_G_0060", "EP01_G_0070", "EP01_G_0080", "EP01_G_0090", "EP01_G_0110", "EP01_D_0120", "EP01_D_0130", "EP01_D_0150", "EP01_D_0170", "EP01_D_0190", "EP01_D_0210", "EP01_G_0220", "EP01_G_0230", "EP01_G_0250", "EP01_G_0260", "EP01_G_0270", "EP01_G_0290", "EP01_G_0300", "EP01_G_0310", "EP01_G_0320", "EP01_G_0330", "EP01_G_0340", "EP01_G_0350", "EP01_D_0360", "EP01_D_0370", "EP01_D_0380", "EP01_D_0390", "EP01_D_0400", "EP01_D_0410", "EP01_D_0420", "EP01_D_0430", "EP01_G_0440", "EP01_D_0470", "EP01_D_0480", "EP01_D_0490", "EP01_G_0500", "EP01_D_0510", "EP01_D_0520", "EP01_G_0570", "EP01_D_0580", "EP01_G_0590", "EP01_G_0700", "EP01_G_0710", "EP01_G_0720", "EP01_D_0730", "EP01_D_0740", "EP01_G_0750", "EP01_G_0760", "EP01_G_0770", "EP01_G_0780", "EP01_D_0790", "EP01_D_0800", "EP01_D_0810", "EP01_D_0830", "EP01_D_0832", "EP01_G_0850", "EP01_G_0860", "EP01_G_0870", "EP01_G_0880", "EP01_G_0900", "EP01_G_0910", "EP01_G_0920", "EP01_G_0930", "EP01_F_0940", "EP01_F_0950", "EP01_F_0960", "EP01_F_0970", "EP01_F_0980", "EP01_D_0990", "EP01_D_1000", "EP01_D_1010", "EP01_D_1020", "EP01_D_1030", "EP01_D_1040", "EP01_G_1050", "EP01_G_1060", "EP01_G_9990"]
    return shotlist, productlist

def get_client_shot_name(shot_name):
    """Convert ME1 shot name to client shot name."""
    shotlist, productlist = get_shot_mapping()
    
    if shot_name in shotlist:
        position = shotlist.index(shot_name)
        if position <= (len(productlist)-1):
            return productlist[position]
    return None

def create_text_node(client_shot, ref_node):
    """Create text node with frame number and shot name."""
    text_node = nuke.nodes.Text2()
    
    # Configure the text node
    text_node['message'].setValue('[frame] - ' + client_shot)
    text_node['font_size_toolbar'].setValue(100)
    text_node['font_width_toolbar'].setValue(100)
    text_node['font_height_toolbar'].setValue(100)
    text_node['box'].setValue([3.5, 32, 450.5, 82])
    text_node['xjustify'].setValue('left')
    text_node['yjustify'].setValue('center')
    text_node['global_font_scale'].setValue(0.49)
    text_node['center'].setValue([2048, 1080])
    text_node['enable_background'].setValue(True)
    text_node['background_opacity'].setValue(0.15)
    
    # Position text node
    text_node.setXYpos(ref_node.xpos(), ref_node.ypos() + 50)
    
    return text_node

def create_dailies_write():
    """Create Write nodes for dailies with correct naming."""
    
    # Get selected nodes
    selected = nuke.selectedNodes()
    read_nodes = [node for node in selected if node.Class() == "Read"]
    
    if not read_nodes:
        nuke.message("Please select at least one Read node")
        return
    
    # Keep track of processed and failed nodes
    processed = []
    failed = []
    
    # Process each Read node
    for read_node in read_nodes:
        try:
            # Get the read node's file path
            file_path = read_node['file'].value()
            
            # Try to find ME1_XXXX pattern in the path
            shot_match = re.search(r'ME1_\d{4}', file_path)
            if not shot_match:
                failed.append(f"{read_node.name()}: No shot number found in path")
                continue
                
            shot_name = shot_match.group()
            
            # Get client shot name
            client_shot = get_client_shot_name(shot_name)
            if not client_shot:
                failed.append(f"{read_node.name()}: No matching client shot for {shot_name}")
                continue
            
            # Create the dailies path
            base_path = r"Y:\MOLOCH_02426\output\_dailies\241129\MT"
            
            # Create shot subfolder
            shot_path = os.path.join(base_path, client_shot).replace('\\', '/')
            
            # Create new filename with frame padding
            new_filename = f"{client_shot}.%04d.exr"
            
            # Combine for final path
            final_path = os.path.join(shot_path, new_filename).replace('\\', '/')
            
            # Create text burn-in node
            text_node = create_text_node(client_shot, read_node)
            text_node.setInput(0, read_node)
            
            # Create Write node
            write_node = nuke.nodes.Write()
            
            # Set the Write node parameters
            write_node['file'].setValue(final_path)
            write_node['file_type'].setValue('exr')
            write_node['colorspace'].setValue('compositing_linear')
            write_node['metadata'].setValue('all metadata')
            write_node['first_part'].setValue('rgba')
            write_node['create_directories'].setValue(True)
            write_node['checkHashOnRead'].setValue(False)
            
            # Position write node
            write_node.setXYpos(text_node.xpos(), text_node.ypos() + 50)
            
            # Connect write node to text node
            write_node.setInput(0, text_node)
            
            # Set the frame range to match the read node
            write_node['first'].setValue(read_node['first'].value())
            write_node['last'].setValue(read_node['last'].value())
            
            processed.append(f"{read_node.name()} -> {client_shot}")
            
        except Exception as e:
            failed.append(f"{read_node.name()}: Error - {str(e)}")
    
    # Show summary message
    summary = "Process Complete\n\n"
    if processed:
        summary += "Successfully processed:\n" + "\n".join(processed) + "\n\n"
    if failed:
        summary += "Failed to process:\n" + "\n".join(failed)
    
    nuke.message(summary)

# Run the script
create_dailies_write()
