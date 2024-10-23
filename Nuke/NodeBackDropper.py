"""
Nuke Node Finder and Backdrop Creator
===================================

A Nuke script that automatically finds specific nodes in your script and creates colored backdrops around them
for better organization and visibility.

Features:
---------
- Detects Reduce Noise nodes (v4 and v5)
- Detects MODNet nodes by name
- Creates colored backdrops around found nodes
- Customizable colors and sizes
- Reports total count of found nodes

Installation:
------------
1. Copy this script to your .nuke directory or a directory in your NUKE_PATH
2. In Nuke, you can run it using:
   import node_finder
   node_finder.highlight_nodes_with_backdrops()

Optional: Add to menu.py:
   import node_finder
   nuke.menu('Nuke').addCommand('Custom/Highlight Nodes', 'node_finder.highlight_nodes_with_backdrops()')

Configuration:
-------------
You can modify the USER VARIABLES section below to customize:
- Backdrop colors
- Backdrop size offsets
- Font size
- Z-order of backdrops

Author: Your Name
Version: 1.0.0
Created: October 2024
License: MIT
Requirements: Nuke 11+
"""

import nuke

# USER VARIABLES
# Colors in 0xRRGGBBFF format
REDUCE_NOISE_COLOR = int(0xFF0000FF)  # Red
MODNET_COLOR = int(0xFF8000FF)        # Orange

# Backdrop parameters
BACKDROP_FONT_SIZE = 42
BACKDROP_X_OFFSET = 50    # Pixels to add on left/right
BACKDROP_Y_OFFSET = 50    # Pixels to add on top/bottom
BACKDROP_Z_ORDER = 1      # Z-order of the backdrop (higher numbers = more forward)

# Node name patterns
MODNET_NAME_PATTERN = "MODNet"  # Pattern to match MODNet node names
REDUCE_NOISE_CLASSES = [
    "OFXcom.absoft.neatvideo4_v4",
    "OFXcom.absoft.neatvideo5_v5"
]

def find_nodes():
    """
    Searches through all nodes in the current Nuke script to find 
    Reduce Noise and MODNet nodes.
    
    Returns:
        tuple: Two lists containing (reduce_noise_nodes, modnet_nodes)
    """
    reduce_noise_nodes = []
    modnet_nodes = []
    
    for node in nuke.allNodes():
        # Check for Reduce Noise nodes by class
        if node.Class() in REDUCE_NOISE_CLASSES:
            reduce_noise_nodes.append(node)
        # Check for MODNet nodes by name
        elif node.name().startswith(MODNET_NAME_PATTERN):
            modnet_nodes.append(node)
            
    return reduce_noise_nodes, modnet_nodes

def create_backdrop(node, color):
    """
    Creates a backdrop node behind the specified node with given color.
    
    Args:
        node: Nuke node to create backdrop for
        color (int): Color for backdrop in 0xRRGGBBFF format
    
    Returns:
        nuke.Node: Created backdrop node
    """
    backdrop = nuke.nodes.BackdropNode()
    backdrop['label'].setValue(node.name())
    backdrop['note_font_size'].setValue(BACKDROP_FONT_SIZE)
    backdrop['tile_color'].setValue(color)
    
    # Set backdrop size and position
    bdX = node.xpos() - BACKDROP_X_OFFSET
    bdY = node.ypos() - BACKDROP_Y_OFFSET
    bdW = node.screenWidth() + (BACKDROP_X_OFFSET * 2)
    bdH = node.screenHeight() + (BACKDROP_Y_OFFSET * 2)
    
    backdrop.setXYpos(bdX, bdY)
    backdrop['bdwidth'].setValue(bdW)
    backdrop['bdheight'].setValue(bdH)
    backdrop['z_order'].setValue(BACKDROP_Z_ORDER)
    
    return backdrop

def highlight_nodes_with_backdrops():
    """
    Main function to find nodes and create backdrops around them.
    Shows a message dialog with the count of found nodes.
    """
    reduce_noise_nodes, modnet_nodes = find_nodes()
    
    # Create backdrops for each node type
    for node in reduce_noise_nodes:
        create_backdrop(node, REDUCE_NOISE_COLOR)
    
    for node in modnet_nodes:
        create_backdrop(node, MODNET_COLOR)
    
    # Create summary message
    message = []
    if reduce_noise_nodes:
        message.append(f"Found {len(reduce_noise_nodes)} Reduce Noise nodes")
    if modnet_nodes:
        message.append(f"Found {len(modnet_nodes)} MODNet nodes")
        
    if message:
        nuke.message(" and ".join(message) + ".")
    else:
        nuke.message("No Reduce Noise or MODNet nodes found.")

def remove_all_backdrops():
    """
    Utility function to remove all backdrop nodes created by this script.
    Useful for cleanup or reset.
    """
    for node in nuke.allNodes('BackdropNode'):
        nuke.delete(node)

if __name__ == "__main__":
    highlight_nodes_with_backdrops()
