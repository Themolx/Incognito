#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simplified Delivery Script for TIFF Files with a Specific Shuffle Node

This script processes selected Read nodes containing TIFF files (full CG shots):
1. Inserts a Shuffle node (with alpha set to white) right after the Read node.
2. Creates a Write node connected to the Shuffle node.
3. Sets up PIZ compression.
4. Saves files to a subfolder (named after the shot) in the specified output directory,
   using a clean shot name (without any formatting strings like %05d) and the hash syntax (####)
   to specify the frame sequence.
"""

import nuke
import os
import re

# Default output directory
OUTPUT_DIR = "Y:/MOLOCH_02426/sources/Users/MT/s02_temp_forpublish"

def get_shot_name(file_path):
    """
    Get shot name from file path using the base filename.
    Removes the file extension, any trailing frame numbers, and any formatting
    specifier (e.g., %05d) that might be present in the filename.
    """
    base_name = os.path.basename(file_path)
    shot_name = os.path.splitext(base_name)[0]
    # Remove trailing frame numbers if present (e.g., ".1234")
    shot_name = re.sub(r'\.\d+$', '', shot_name)
    # Remove any formatting specifier (e.g., %05d)
    shot_name = re.sub(r'%0\d+d', '', shot_name)
    # Remove any trailing underscores that might result from the removal
    shot_name = shot_name.rstrip('_')
    return shot_name

def sanitize_node_name(name):
    """
    Sanitize a string to produce a valid Nuke node name:
      - Replaces invalid characters with underscores.
      - If the name begins with a digit, prefixes it with 'N_'.
    """
    sanitized = re.sub(r'[^\w\-]', '_', name)
    if sanitized and sanitized[0].isdigit():
        sanitized = "N_" + sanitized
    return sanitized

def generate_unique_node_name(base_name):
    """
    Generate a unique node name by appending a numeric suffix if the name already exists.
    """
    node_name = base_name
    counter = 1
    while nuke.exists(node_name):
        node_name = f"{base_name}_{counter}"
        counter += 1
    return node_name

def process_tiff_files():
    """
    Process all selected Read nodes containing TIFF files:
      - Creates a Shuffle node after the Read node with alpha set to white.
      - Creates a Write node connected to the Shuffle node with appropriate settings.
      - Cleans up the shot name so that it doesn't contain frame formatting symbols.
    """
    selected_nodes = nuke.selectedNodes('Read')
    if not selected_nodes:
        nuke.message("Please select one or more Read nodes with TIFF files.")
        return

    results = []
    for read_node in selected_nodes:
        file_path = read_node['file'].value()

        # Check if the file is a TIFF file
        if not file_path.lower().endswith(('.tif', '.tiff')):
            results.append((read_node.name(), False, "Not a TIFF file. Skipping."))
            continue

        # Set colorspace to "color_picking" if the knob exists
        if 'colorspace' in read_node.knobs():
            read_node['colorspace'].setValue('color_picking')

        # Extract a clean shot name from the file path
        shot_name = get_shot_name(file_path)

        # Create a subfolder inside the OUTPUT_DIR for the shot
        subfolder = os.path.join(OUTPUT_DIR, shot_name)
        if not os.path.exists(subfolder):
            os.makedirs(subfolder)

        # Construct the output path using the shot subfolder.
        # The output file will use the "####" notation for frame numbers.
        output_path = os.path.join(subfolder, f"{shot_name}.####.exr")

        # Create the Shuffle node after the Read node
        shuffle_node = nuke.createNode("Shuffle", inpanel=False)
        shuffle_node.setInput(0, read_node)
        shuffle_node.setXYpos(read_node.xpos(), read_node.ypos() + 50)
        
        # Configure the Shuffle node:
        #  - Map the input channels as is (rgba)
        #  - Set alpha channel to white
        #  - Set a label to identify it as the specific Shuffle node.
        shuffle_node["in"].setValue("rgba")
        shuffle_node["in2"].setValue("none")
        shuffle_node["red"].setValue("red")
        shuffle_node["green"].setValue("green")
        shuffle_node["blue"].setValue("blue")
        shuffle_node["alpha"].setValue("white")
        shuffle_node["label"].setValue("Specific Shuffle Node")

        # Create the Write node and connect it to the Shuffle node output
        write_node = nuke.createNode("Write", inpanel=False)
        write_node.setInput(0, shuffle_node)
        write_node['channels'].setValue("all")
        write_node['file'].setValue(output_path)
        write_node['file_type'].setValue("exr")
        write_node['compression'].setValue("PIZ Wavelet (32 scanlines)")
        write_node['metadata'].setValue("all metadata")
        write_node['first_part'].setValue("rgba")
        write_node['create_directories'].setValue(True)
        write_node.setXYpos(read_node.xpos(), read_node.ypos() + 100)

        # Sanitize and generate a unique name for the Write node
        base_node_name = "Write_" + sanitize_node_name(shot_name)
        unique_node_name = generate_unique_node_name(base_node_name)
        write_node.setName(unique_node_name)

        results.append((read_node.name(), True, f"Successfully processed {shot_name}"))

    # Prepare and display a summary of the processing results
    summary = "Processing Results:\n\n"
    for node_name, success, message in results:
        status = "✓ Success" if success else "✗ Failed"
        summary += f"{node_name}: {status} - {message}\n"
    nuke.message(summary)

# Create a menu item in Nuke for the TIFF Processor
menu = nuke.menu('Nuke').addMenu('TIFF Processor')
menu.addCommand('Process TIFF Files', process_tiff_files)

if __name__ == "__main__":
    process_tiff_files()
