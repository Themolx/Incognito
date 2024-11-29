# BatchRenderWriteNodes.py v1.1
#
# This script renders selected Write nodes with custom frame ranges.
# Usage: Select Write nodes in Nuke's node graph, run the script,
# and input custom frame ranges for each Write node.
#
# Features:
# - Renders multiple Write nodes
# - Custom frame range per Write node
# - Integer-only frame validation
# - Progress feedback
# - Error handling
#
# Author: Claude
# Last Updated: 2024-11-29

import nuke
import re

# User Variables 
FRAME_PATTERN = r'^\d+\-\d+$'  # Pattern for frame range validation (e.g., 1001-1100)
DEFAULT_FRAME_RANGE = "1001-1100"  # Default frame range suggestion
ERROR_COLOR = 0xFF0000FF  # Red color for error highlighting

def validate_frame_range(frame_range):
    """Validate frame range string format and ensure integer values."""
    try:
        # Check format
        if not re.match(FRAME_PATTERN, frame_range):
            return False, "Invalid format. Use: startFrame-endFrame (integers only)"
        
        # Parse values and ensure they're integers
        start_str, end_str = frame_range.split('-')
        
        # Convert to integers and check for float values
        if '.' in start_str or '.' in end_str:
            return False, "Frame numbers must be integers, not decimal numbers"
            
        start = int(start_str)
        end = int(end_str)
        
        # Validate values
        if start > end:
            return False, "Start frame must be less than or equal to end frame"
            
        return True, (start, end)
    except ValueError:
        return False, "Invalid frame numbers"

def get_frame_range_for_node(node):
    """Get frame range from user for a specific Write node."""
    while True:
        # Get current frame range from node if exists, ensure integers
        current_start = int(node['first'].value())
        current_end = int(node['last'].value())
        current_range = f"{current_start}-{current_end}"
        
        # Prompt user
        msg = f'Enter frame range for {node.name()}\n(format: startFrame-endFrame, integers only)'
        frame_range = nuke.getInput(msg, current_range)
        
        if frame_range is None:  # User canceled
            return None
            
        # Validate input
        valid, result = validate_frame_range(frame_range)
        if valid:
            return result
        else:
            nuke.message(f"Error: {result}\nPlease try again.")

def render_write_nodes():
    """Main function to handle Write node rendering."""
    
    # Get selected Write nodes
    write_nodes = [n for n in nuke.selectedNodes() if n.Class() == "Write"]
    
    if not write_nodes:
        nuke.message("Please select at least one Write node.")
        return
        
    # Store original frame ranges to restore later
    original_ranges = {}
    
    try:
        # Get frame ranges for each node
        render_queue = []
        for node in write_nodes:
            frame_range = get_frame_range_for_node(node)
            if frame_range is None:  # User canceled
                return
                
            # Store original range as integers
            original_ranges[node] = (int(node['first'].value()), int(node['last'].value()))
            
            # Set new range
            start, end = frame_range
            node['first'].setValue(start)
            node['last'].setValue(end)
            render_queue.append((node, start, end))
        
        # Render each node
        for node, start, end in render_queue:
            try:
                print(f"Rendering {node.name()} frames {start}-{end}")
                nuke.execute(node, start, end)
            except Exception as e:
                nuke.message(f"Error rendering {node.name()}: {str(e)}")
                
    finally:
        # Restore original frame ranges
        for node, (start, end) in original_ranges.items():
            node['first'].setValue(start)
            node['last'].setValue(end)

if __name__ == "__main__":
    render_write_nodes()
