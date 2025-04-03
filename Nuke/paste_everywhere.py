"""
Paste Everywhere for Nuke
Author: Cascade
Date: 2025-04-03

Description:
    This script allows you to paste clipboard content to multiple selected nodes at once.
    
Usage:
    1. Copy something to clipboard
    2. Select multiple nodes in Nuke
    3. Press Ctrl+Alt+V to paste the clipboard content to all selected nodes
    
Installation:
    1. Place this script in your .nuke folder or a folder that's in your Nuke plugin path
    2. Add the following to your menu.py file:
    
    import paste_everywhere
    paste_everywhere.register_paste_everywhere()
"""

import nuke
import nukescripts

def paste_everywhere():
    """
    Get clipboard content and paste it to all selected nodes
    """
    # Get all selected nodes
    selected_nodes = nuke.selectedNodes()
    
    if not selected_nodes:
        nuke.message("No nodes selected. Please select at least one node.")
        return
    
    # Using '%clipboard%' as the special string to access the system clipboard
    clipboard = '%clipboard%'
    
    # Store original selection
    original_selection = selected_nodes
    
    # For each selected node
    for node in original_selection:
        # Select only this node to paste to it
        for n in nuke.selectedNodes():
            n.setSelected(False)
        
        node.setSelected(True)
        
        # Paste clipboard content using the special clipboard string
        nuke.nodePaste(clipboard)
    
    # Restore original selection
    for n in nuke.allNodes():
        n.setSelected(False)
    
    for node in original_selection:
        node.setSelected(True)
    
    nuke.message(f"Pasted to {len(selected_nodes)} node(s).")


def register_paste_everywhere():
    """
    Register the paste_everywhere function with a keyboard shortcut and add to menus
    """
    # Add to Edit menu
    edit_menu = nuke.menu('Nuke').findItem('Edit')
    edit_menu.addCommand('Paste Everywhere', paste_everywhere, 'ctrl+alt+v')
    
    # Add to Node graph right-click menu
    nuke.menu('Nodes').addCommand('Edit/Paste Everywhere', paste_everywhere, 'ctrl+alt+v')
    
    # Add to custom menu
    toolbar = nuke.menu('Nodes')
    custom_menu = toolbar.addMenu('Custom')
    custom_menu.addCommand('Paste Everywhere', paste_everywhere, 'ctrl+alt+v')
    
    # Add to Nuke menu bar (top-level menu)
    menubar = nuke.menu('Nuke')
    util_menu = menubar.addMenu('Utilities')
    util_menu.addCommand('Paste Everywhere', paste_everywhere, 'ctrl+alt+v')
    
    print("Paste Everywhere registered with shortcut Ctrl+Alt+V and added to menus")


# Auto-register if this script is run directly
if __name__ == "__main__":
    register_paste_everywhere()
