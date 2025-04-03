"""
Compare Frame Ranges for Nuke
Author: Cascade
Date: 2025-04-03

Description:
    This script checks if two selected nodes have the same frame range or length.
    
Usage:
    1. Select exactly two nodes in Nuke
    2. Press Alt+F to compare their frame ranges
    
Installation:
    1. Place this script in your .nuke folder or a folder that's in your Nuke plugin path
    2. Add the following to your menu.py file:
    
    import compare_frame_ranges
    compare_frame_ranges.register_compare_frame_ranges()
"""

import nuke

def get_frame_range(node):
    """
    Get the frame range of a node
    Returns a tuple of (first_frame, last_frame)
    """
    # Different node types store frame range differently
    first_frame = None
    last_frame = None
    
    # Read nodes
    if 'first' in node.knobs() and 'last' in node.knobs():
        first_frame = node['first'].value()
        last_frame = node['last'].value()
    
    # TimeClip or Retime nodes
    elif 'frame_range' in node.knobs():
        range_str = node['frame_range'].value()
        if '-' in range_str:
            parts = range_str.split('-')
            first_frame = float(parts[0])
            last_frame = float(parts[1])
    
    # FrameRange node
    elif 'knob.range' in node.knobs():
        range_str = node['knob.range'].value()
        if '-' in range_str:
            parts = range_str.split('-')
            first_frame = float(parts[0])
            last_frame = float(parts[1])
    
    # TimeOffset nodes
    elif 'time_offset' in node.knobs():
        # This doesn't have a range itself, but if connected to something,
        # we can determine the offset
        offset = node['time_offset'].value()
        if node.input(0):
            input_first, input_last = get_frame_range(node.input(0))
            if input_first is not None and input_last is not None:
                first_frame = input_first + offset
                last_frame = input_last + offset
    
    # If first/last not found, check for common format knobs
    if first_frame is None and 'format' in node.knobs():
        try:
            fmt = node['format'].value()
            if hasattr(fmt, 'first') and hasattr(fmt, 'last'):
                first_frame = fmt.first()
                last_frame = fmt.last()
        except:
            pass
    
    # For nodes that display their input's frame range
    if first_frame is None and node.input(0):
        return get_frame_range(node.input(0))
    
    # For constant nodes or if we can't determine the range
    if first_frame is None:
        first_frame = nuke.root()['first_frame'].value()
        last_frame = nuke.root()['last_frame'].value()
        
    return (first_frame, last_frame)

def compare_frame_ranges():
    """
    Compare frame ranges of two selected nodes
    """
    selected_nodes = nuke.selectedNodes()
    
    # Check that exactly two nodes are selected
    if len(selected_nodes) != 2:
        nuke.message("Please select exactly two nodes to compare.")
        return
    
    node1 = selected_nodes[0]
    node2 = selected_nodes[1]
    
    # Get frame ranges
    range1 = get_frame_range(node1)
    range2 = get_frame_range(node2)
    
    # Calculate lengths
    length1 = range1[1] - range1[0] + 1
    length2 = range2[1] - range2[0] + 1
    
    # Prepare result message
    msg = f"Node: {node1.name()}\nRange: {range1[0]} - {range1[1]} (Length: {length1} frames)\n\n"
    msg += f"Node: {node2.name()}\nRange: {range2[0]} - {range2[1]} (Length: {length2} frames)\n\n"
    
    # Compare ranges
    same_range = (range1[0] == range2[0] and range1[1] == range2[1])
    same_length = (length1 == length2)
    
    if same_range:
        msg += "RESULT: Nodes have IDENTICAL frame ranges."
    elif same_length:
        msg += f"RESULT: Nodes have DIFFERENT frame ranges but SAME length ({length1} frames)."
    else:
        msg += f"RESULT: Nodes have DIFFERENT frame ranges AND lengths."
        diff = abs(length1 - length2)
        msg += f"\nLength difference: {diff} frames"
    
    # Display result
    nuke.message(msg)

def register_compare_frame_ranges():
    """
    Register the compare_frame_ranges function with a keyboard shortcut and add to menus
    """
    # Add to Edit menu
    edit_menu = nuke.menu('Nuke').findItem('Edit')
    edit_menu.addCommand('Compare Frame Ranges', compare_frame_ranges, 'alt+f')
    
    # Add to Node graph right-click menu
    nuke.menu('Nodes').addCommand('Edit/Compare Frame Ranges', compare_frame_ranges, 'alt+f')
    
    # Add to custom menu
    toolbar = nuke.menu('Nodes')
    custom_menu = toolbar.addMenu('Custom')
    custom_menu.addCommand('Compare Frame Ranges', compare_frame_ranges, 'alt+f')
    
    # Add to Nuke menu bar (top-level menu)
    menubar = nuke.menu('Nuke')
    util_menu = menubar.findItem('Utilities') or menubar.addMenu('Utilities')
    util_menu.addCommand('Compare Frame Ranges', compare_frame_ranges, 'alt+f')
    
    print("Compare Frame Ranges registered with shortcut Alt+F and added to menus")


# Auto-register if this script is run directly
if __name__ == "__main__":
    register_compare_frame_ranges()
