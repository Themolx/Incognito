#!/usr/bin/env python
# RenameWriteNodes.py v1.3
#
# This script:
# 1. Renames selected nodes to client shot name
# 2. Changes write node paths inside selected group nodes
#    - Replaces "prerenderAnimaticMxf" with client shot name in paths
#    - Removes frame pattern from path
# 
# Usage: Select nodes and run the script

import nuke
import re

def modify_write_path(write_node, new_name):
    """Modify the Write node's file path."""
    current_path = write_node['file'].value()
    
    # Get the directory and filename parts
    directory = '/'.join(current_path.split('/')[:-1])
    filename = current_path.split('/')[-1]
    
    # Create new filename without frame pattern
    new_filename = f"{new_name}.mxf"
    
    # Construct new path
    new_path = f"{directory}/{new_filename}"
    
    write_node['file'].setValue(new_path)

def process_nodes():
    """Process selected nodes."""
    selected = nuke.selectedNodes()
    if not selected:
        nuke.message("Please select nodes to process")
        return
    
    new_name = "D_990"  # Target name to change to
    
    for node in selected:
        # Rename the node
        node['name'].setValue(new_name)
        
        # If it's a group node, process Write nodes inside
        if node.Class() == "Group":
            with node:
                write_nodes = nuke.allNodes('Write')
                for write_node in write_nodes:
                    modify_write_path(write_node, new_name)

if __name__ == '__main__':
    process_nodes()
