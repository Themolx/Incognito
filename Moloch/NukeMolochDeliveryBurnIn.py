#!/usr/bin/env python
# CreateShotText.py v1.0
#
# This script:
# 1. Creates a new Text node based on selected node position
# 2. Displays frame number and shot name
# 3. Uses existing shot name lookup logic
#
# Usage: Select a node and run the script

import nuke
import re

def get_shot_name():
    """Get the shot name based on the lookup logic."""
    # Shot and product name dictionaries from original script
    shotlist = ["ME1_0050", "ME1_0060", "ME1_0070", "ME1_0080", "ME1_0090", "ME1_0110", "ME1_0120", "ME1_0130", "ME1_0150", "ME1_0170", "ME1_0190", "ME1_0210", "ME1_0220", "ME1_0230", "ME1_0250", "ME1_0260", "ME1_0270", "ME1_0290", "ME1_0300", "ME1_0310", "ME1_0320", "ME1_0330", "ME1_0340", "ME1_0350", "ME1_0360", "ME1_0370", "ME1_0380", "ME1_0390", "ME1_0400", "ME1_0410", "ME1_0420", "ME1_0430", "ME1_0440", "ME1_0470", "ME1_0480", "ME1_0490", "ME1_0500", "ME1_0510", "ME1_0520", "ME1_0570", "ME1_0580", "ME1_0590", "ME1_0700", "ME1_0710", "ME1_0720", "ME1_0730", "ME1_0740", "ME1_0750", "ME1_0760", "ME1_0770", "ME1_0780", "ME1_0790", "ME1_0800", "ME1_0810", "ME1_0830", "ME1_0832", "ME1_0850", "ME1_0860", "ME1_0870", "ME1_0880", "ME1_0900", "ME1_0910", "ME1_0920", "ME1_0930", "ME1_0940", "ME1_0950", "ME1_0960", "ME1_0970", "ME1_0980", "ME1_0990", "ME1_1000", "ME1_1010", "ME1_1020", "ME1_1030", "ME1_1040", "ME1_1050", "ME1_1060", "ME1_9990"]
    productlist = ["EP01_G_0050", "EP01_G_0060", "EP01_G_0070", "EP01_G_0080", "EP01_G_0090", "EP01_G_0110", "EP01_D_0120", "EP01_D_0130", "EP01_D_0150", "EP01_D_0170", "EP01_D_0190", "EP01_D_0210", "EP01_G_0220", "EP01_G_0230", "EP01_G_0250", "EP01_G_0260", "EP01_G_0270", "EP01_G_0290", "EP01_G_0300", "EP01_G_0310", "EP01_G_0320", "EP01_G_0330", "EP01_G_0340", "EP01_G_0350", "EP01_D_0360", "EP01_D_0370", "EP01_D_0380", "EP01_D_0390", "EP01_D_0400", "EP01_D_0410", "EP01_D_0420", "EP01_D_0430", "EP01_G_0440", "EP01_D_0470", "EP01_D_0480", "EP01_D_0490", "EP01_G_0500", "EP01_D_0510", "EP01_D_0520", "EP01_G_0570", "EP01_D_0580", "EP01_G_0590", "EP01_G_0700", "EP01_G_0710", "EP01_G_0720", "EP01_D_0730", "EP01_D_0740", "EP01_G_0750", "EP01_G_0760", "EP01_G_0770", "EP01_G_0780", "EP01_D_0790", "EP01_D_0800", "EP01_D_0810", "EP01_D_0830", "EP01_D_0832", "EP01_G_0850", "EP01_G_0860", "EP01_G_0870", "EP01_G_0880", "EP01_G_0900", "EP01_G_0910", "EP01_G_0920", "EP01_G_0930", "EP01_F_0940", "EP01_F_0950", "EP01_F_0960", "EP01_F_0970", "EP01_F_0980", "EP01_D_0990", "EP01_D_1000", "EP01_D_1010", "EP01_D_1020", "EP01_D_1030", "EP01_D_1040", "EP01_G_1050", "EP01_G_1060", "EP01_G_9990"]
    
    filename = nuke.root().name()
    shotname = re.search(r"ME1_\d{4}", filename)
    
    if not shotname:
        nuke.message("The script name is not matching the pattern ME1_0000.\nExiting script")
        return None
        
    shotname = shotname.group()
    if shotname in shotlist:
        position = shotlist.index(shotname)
        if position <= (len(productlist)-1):
            return productlist[position]
    
    nuke.message(f"The shotname {shotname} was not found in dictionary of shots or has no counterpart.")
    return None

def create_text_node():
    """Create a text node with frame number and shot name."""
    selected = nuke.selectedNodes()
    if not selected:
        nuke.message("Please select a node")
        return
    
    # Get the shot name
    shot_name = get_shot_name()
    if not shot_name:
        return
        
    # Create text node
    text_node = nuke.createNode("Text2")
    
    # Set position based on selected node
    ref_node = selected[0]
    text_node.setXYpos(ref_node.xpos() + 100, ref_node.ypos())
    
    # Configure the text node to match the reference
    text_node['message'].setValue('[frame] - ' + shot_name)
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
    
    # Make the text node global (visible in all views)
    text_node['global'].setValue(True)

# Run the script
create_text_node()
