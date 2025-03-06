#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integrated Plate Processor
This script combines plate finding and delivery functionalities:
1. Finds the original plate based on shot mapping
2. Copies metadata from the original plate to the selected Read node
3. Creates a Write node for delivery with appropriate settings
"""

import nuke
import os
import re
import datetime
import csv

# Shot mapping dictionary
SHOT_MAPPING = {
    'ME1_0050': 'EP01_G_050',
    'ME1_0060': 'EP01_G_060',
    'ME1_0070': 'EP01_G_070',
    'ME1_0080': 'EP01_G_080',
    'ME1_0090': 'EP01_G_090',
    'ME1_0100': 'EP01_D_100',
    'ME1_0110': 'EP01_G_110',
    'ME1_0120': 'EP01_D_120',
    'ME1_0130': 'EP01_D_130',
    'ME1_0140': 'EP01_D_140',
    'ME1_0150': 'EP01_D_150',
    'ME1_0160': 'EP01_D_160',
    'ME1_0170': 'EP01_D_170',
    'ME1_0180': 'EP01_D_180',
    'ME1_0190': 'EP01_D_190',
    'ME1_0200': 'EP01_D_200',
    'ME1_0210': 'EP01_D_210',
    'ME1_0220': 'EP01_G_220',
    'ME1_0230': 'EP01_G_230',
    'ME1_0240': 'EP01_G_240',
    'ME1_0250': 'EP01_G_250',
    'ME1_0260': 'EP01_G_260',
    'ME1_0270': 'EP01_G_270',
    'ME1_0275': 'EP01_G_275',
    'ME1_0280': 'EP01_G_280',
    'ME1_0290': 'EP01_G_290',
    'ME1_0300': 'EP01_G_300',
    'ME1_0310': 'EP01_G_310',
    'ME1_0320': 'EP01_G_320',
    'ME1_0330': 'EP01_G_330',
    'ME1_0340': 'EP01_G_340',
    'ME1_0350': 'EP01_G_350',
    'ME1_0360': 'EP01_D_360',
    'ME1_0370': 'EP01_D_370',
    'ME1_0380': 'EP01_D_380',
    'ME1_0390': 'EP01_D_390',
    'ME1_0400': 'EP01_D_400',
    'ME1_0410': 'EP01_D_410',
    'ME1_0420': 'EP01_D_420',
    'ME1_0430': 'EP01_D_430',
    'ME1_0440': 'EP01_G_440',
    'ME1_0470': 'EP01_D_470',
    'ME1_0480': 'EP01_D_480',
    'ME1_0490': 'EP01_D_490',
    'ME1_0500': 'EP01_G_500',
    'ME1_0510': 'EP01_D_510',
    'ME1_0520': 'EP01_D_520',
    'ME1_0570': 'EP01_G_570',
    'ME1_0580': 'EP01_D_580',
    'ME1_0590': 'EP01_G_590',
    'ME1_0700': 'EP01_G_700',
    'ME1_0710': 'EP01_G_710',
    'ME1_0720': 'EP01_G_720',
    'ME1_0730': 'EP01_D_730',
    'ME1_0740': 'EP01_D_740',
    'ME1_0750': 'EP01_G_750',
    'ME1_0760': 'EP01_G_760',
    'ME1_0770': 'EP01_G_770',
    'ME1_0780': 'EP01_G_780',
    'ME1_0790': 'EP01_D_790',
    'ME1_0800': 'EP01_D_800',
    'ME1_0810': 'EP01_D_810',
    'ME1_0830': 'EP01_D_830',
    'ME1_0832': 'EP01_D_832',
    'ME1_0850': 'EP01_G_850',
    'ME1_0860': 'EP01_G_860',
    'ME1_0870': 'EP01_G_870',
    'ME1_0880': 'EP01_G_880',
    'ME1_0900': 'EP01_G_900',
    'ME1_0910': 'EP01_G_910',
    'ME1_0920': 'EP01_G_920',
    'ME1_0930': 'EP01_G_930',
    'ME1_0940': 'EP01_F_940',
    'ME1_0950': 'EP01_F_950',
    'ME1_0960': 'EP01_F_960',
    'ME1_0970': 'EP01_F_970',
    'ME1_0980': 'EP01_F_980',
    'ME1_0990': 'EP01_D_990',
    'ME1_1000': 'EP01_D_1000',
    'ME1_1010': 'EP01_D_1010',
    'ME1_1020': 'EP01_D_1020',
    'ME1_1030': 'EP01_D_1030',
    'ME1_1040': 'EP01_D_1040',
    'ME1_1050': 'EP01_G_1050',
    'ME1_1060': 'EP01_G_1060',
    'ME1_9990': 'EP01_G_9990'
}

# Default directory and file settings
DEFAULT_OUTPUT_BASE_DIR = "Y:/MOLOCH_02426/sources/Users/MT/tmp"
DEFAULT_SOURCE_PLATES_DIR = "Y:/MOLOCH_02426/sources/_raw_material"
DEFAULT_LOG_FILE_DIR = "Y:/MOLOCH_02426/sources/Users/MT/logs"
DEFAULT_LOG_FILE_NAME = "nuke_delivery_log.csv"

def setup_user_variables():
    """
    Set up user-configurable variables in Nuke preferences.
    Creates knobs for path configuration if they don't exist.
    Returns a dictionary containing the current values.
    """
    # Get the user preferences
    user_prefs = nuke.toNode("preferences")
    
    # Create a tab for the plate processor if it doesn't exist
    if not user_prefs.knob("PlateProcessor"):
        tab = nuke.Tab_Knob('PlateProcessor', 'Plate Processor')
        divider = nuke.Text_Knob('plateProcessorDivider', '', 'Path Configuration')
        
        # Create knobs for each configurable path
        output_dir_knob = nuke.String_Knob('plateProcessorOutputDir', 'Output Directory', DEFAULT_OUTPUT_BASE_DIR)
        output_dir_knob.setTooltip('Base directory for delivered files')
        
        source_dir_knob = nuke.String_Knob('plateProcessorSourceDir', 'Source Plates Directory', DEFAULT_SOURCE_PLATES_DIR)
        source_dir_knob.setTooltip('Directory containing original plates')
        
        log_dir_knob = nuke.String_Knob('plateProcessorLogDir', 'Log Directory', DEFAULT_LOG_FILE_DIR)
        log_dir_knob.setTooltip('Directory where delivery logs will be saved')
        
        log_file_knob = nuke.String_Knob('plateProcessorLogFileName', 'Log File Name', DEFAULT_LOG_FILE_NAME)
        log_file_knob.setTooltip('Name of the CSV file for logging deliveries')

        # Add all knobs to the preferences
        user_prefs.addKnob(tab)
        user_prefs.addKnob(divider)
        user_prefs.addKnob(output_dir_knob)
        user_prefs.addKnob(source_dir_knob)
        user_prefs.addKnob(log_dir_knob)
        user_prefs.addKnob(log_file_knob)
    
    # Get current values (or defaults if not set)
    config = {
        'OUTPUT_BASE_DIR': user_prefs['plateProcessorOutputDir'].value() or DEFAULT_OUTPUT_BASE_DIR,
        'SOURCE_PLATES_DIR': user_prefs['plateProcessorSourceDir'].value() or DEFAULT_SOURCE_PLATES_DIR,
        'LOG_FILE_DIR': user_prefs['plateProcessorLogDir'].value() or DEFAULT_LOG_FILE_DIR,
        'LOG_FILE_NAME': user_prefs['plateProcessorLogFileName'].value() or DEFAULT_LOG_FILE_NAME
    }
    
    return config

# Get current user variable settings
CONFIG = setup_user_variables()

# Base output directory for renders
OUTPUT_BASE_DIR = CONFIG['OUTPUT_BASE_DIR']

# Raw material source directory
SOURCE_PLATES_DIR = CONFIG['SOURCE_PLATES_DIR']

# Log file location
LOG_FILE_DIR = CONFIG['LOG_FILE_DIR']
LOG_FILE_NAME = CONFIG['LOG_FILE_NAME']

def extract_shot_name(file_path):
    """
    Extract shot name from file path.
    Should work with different path formats.
    """
    # Try to find ME1_XXXX pattern in the path
    match = re.search(r'(ME1_\d{4})', file_path)
    if match:
        return match.group(1)
    return None

def extract_version(file_path):
    """
    Extract the version number from the file path if available.
    Expected format: .../something_vXXX/... or .../something_vXXX.ext
    """
    match = re.search(r'v(\d{3})', file_path)
    if match:
        return f"v{match.group(1)}"
    return None

def get_latest_delivered_version(shot_name):
    """
    Check the log file to find the latest version delivered for a specific shot.
    Returns a tuple of (latest_version, version_info) or (None, None) if no delivery found.
    """
    log_file_path = os.path.join(LOG_FILE_DIR, LOG_FILE_NAME)
    
    # Check if the log file exists
    if not os.path.exists(log_file_path):
        # Create the directory if it doesn't exist
        if not os.path.exists(LOG_FILE_DIR):
            os.makedirs(LOG_FILE_DIR)
            
        # Create the log file with headers
        with open(log_file_path, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'source_shot', 'delivery_shot', 'source_version', 'delivery_version', 'source_path', 'delivery_path']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
        
        return None, None
    
    # Read the log file to find the latest version
    latest_version = None
    version_info = None
    
    with open(log_file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['delivery_shot'] == shot_name:
                if latest_version is None or row['delivery_version'] > latest_version:
                    latest_version = row['delivery_version']
                    version_info = row
    
    return latest_version, version_info

def log_delivery(source_shot, delivery_shot, source_version, delivery_version, source_path, delivery_path):
    """
    Log the delivery information to a CSV file.
    """
    log_file_path = os.path.join(LOG_FILE_DIR, LOG_FILE_NAME)
    
    # Create the directory if it doesn't exist
    if not os.path.exists(LOG_FILE_DIR):
        os.makedirs(LOG_FILE_DIR)
    
    # Check if the log file exists, create it with headers if not
    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'source_shot', 'delivery_shot', 'source_version', 'delivery_version', 'source_path', 'delivery_path']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    
    # Get the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Log the delivery
    with open(log_file_path, 'a', newline='') as csvfile:
        fieldnames = ['timestamp', 'source_shot', 'delivery_shot', 'source_version', 'delivery_version', 'source_path', 'delivery_path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({
            'timestamp': timestamp,
            'source_shot': source_shot,
            'delivery_shot': delivery_shot,
            'source_version': source_version,
            'delivery_version': delivery_version,
            'source_path': source_path,
            'delivery_path': delivery_path
        })

def process_single_plate(read_node, batch_mode=False, version_choice_override=None):
    """
    Process a single read node:
    1. Find original plate
    2. Copy metadata
    3. Create delivery Write node
    
    Args:
        read_node: The Read node to process
        batch_mode: If True, suppresses individual messages and uses version_choice_override
        version_choice_override: If provided, uses this choice for versioning (1=new, 2=overwrite)
        
    Returns a tuple (success, message, nodes) where:
    - success: True if processing was successful, False otherwise
    - message: A string message about the result
    - nodes: A dictionary of created nodes
    """
    # Get file path from the Read node
    file_path = read_node['file'].value()
    
    # Extract shot name
    shot_name = extract_shot_name(file_path)
    
    if not shot_name:
        if not batch_mode:
            nuke.message(f"Could not extract shot name from {file_path}")
        return False, f"Could not extract shot name from {file_path}", {}
    
    # Check if shot is in the mapping dictionary
    if shot_name not in SHOT_MAPPING:
        if not batch_mode:
            nuke.message(f"Shot {shot_name} not found in the mapping dictionary.")
        return False, f"Shot {shot_name} not found in the mapping dictionary.", {}
    
    # Get the original shot name from the dictionary
    original_shot = SHOT_MAPPING[shot_name]
    
    # Construct the original plate path
    # Format: Y:/MOLOCH_02426/sources/_raw_material/EP01_G_0230/EP01_G_0230.####.exr
    # Need to add a leading zero to match the format in the original path
    shot_number = original_shot.split('_')[-1]
    original_shot_with_zero = f"{original_shot[:6]}_0{shot_number}"
    original_plate_path = f"{SOURCE_PLATES_DIR}/{original_shot_with_zero}/{original_shot_with_zero}.####.exr"
    
    # Check if original plate directory exists
    source_dir = os.path.dirname(original_plate_path.replace("####", "0001"))
    if not os.path.exists(source_dir):
        if not batch_mode:
            nuke.message(f"Original plate directory not found: {source_dir}")
        return False, f"Original plate directory not found: {source_dir}", {}
    
    # Create a new Read node with the original plate path
    original_read = nuke.createNode("Read")
    
    # Set the file path
    original_read['file'].setValue(original_plate_path)
    original_read['file_type'].setValue('exr')
    
    # Try to get frame range info from the source read node if available
    if 'first' in read_node.knobs() and 'last' in read_node.knobs():
        original_read['first'].setValue(read_node['first'].value())
        original_read['last'].setValue(read_node['last'].value())
        original_read['origfirst'].setValue(read_node['first'].value())
        original_read['origlast'].setValue(read_node['last'].value())
        
    # Set format if available from the original node
    if 'format' in read_node.knobs():
        original_read['format'].setValue(read_node['format'].value())
        
    # Set origset to true
    original_read['origset'].setValue(True)
    
    # Position the new node
    original_read.setXYpos(read_node.xpos() + 100, read_node.ypos())
    
    # Create a CopyMetaData node
    copy_metadata = nuke.createNode("CopyMetaData")
    
    # Connect the CopyMetaData node inputs:
    # Input 0: Selected read node (that should receive the metadata)
    # Input 1: Original plate read node (source of the metadata)
    copy_metadata.setInput(0, read_node)
    copy_metadata.setInput(1, original_read)
    
    # Position the CopyMetaData node
    copy_metadata.setXYpos(original_read.xpos() + 100, original_read.ypos() + 50)
    
    # Rename the nodes for clarity
    original_read.setName(f"OriginalPlate_{shot_name}")
    copy_metadata.setName(f"CopyMetaData_{shot_name}")
    
    # Extract the source version (for logging purposes)
    source_version = extract_version(file_path) or "unknown"
    
    # Check if this shot has already been delivered
    latest_version, version_info = get_latest_delivered_version(original_shot)
    
    delivery_version = "v001"
    
    # If already delivered, ask if we should deliver a new version or overwrite v001
    if latest_version:
        latest_ver_num = int(latest_version[1:])
        next_ver_num = latest_ver_num + 1
        next_version = f"v{next_ver_num:03d}"
        
        # In batch mode, use the override
        if batch_mode and version_choice_override is not None:
            version_choice = version_choice_override
        else:
            msg = f"Shot {original_shot} has already been delivered as {latest_version}.\n"
            msg += f"Last delivery was from source {version_info['source_version']} on {version_info['timestamp']}.\n\n"
            
            # Create a dialog with options
            version_choice = nuke.choice(
                "Version Options", 
                f"Shot {original_shot} already delivered", 
                ["Cancel", f"Use new version ({next_version})", "Overwrite existing v001"]
            )
        
        if version_choice == 0:  # Cancel
            if not batch_mode:
                nuke.message("Delivery cancelled")
            return False, "Delivery cancelled", {"original_read": original_read, "copy_metadata": copy_metadata}
        elif version_choice == 1:  # Use new version
            delivery_version = next_version
        elif version_choice == 2:  # Overwrite v001
            delivery_version = "v001"
            if not batch_mode:
                nuke.message(f"WARNING: You are overwriting the existing v001 delivery for {original_shot}!")
    
    # Create the output directory path
    output_dir = os.path.join(OUTPUT_BASE_DIR, original_shot)
    
    # Create the directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create the output file path
    output_path = f"{output_dir}/{original_shot}_{delivery_version}.%04d.exr"
    
    # Create the Write node and connect it to the CopyMetaData node
    write_node = nuke.createNode("Write")
    write_node.setInput(0, copy_metadata)
    
    # Set the Write node properties
    write_node['channels'].setValue("all")
    write_node['file'].setValue(output_path)
    write_node['file_type'].setValue("exr")
    write_node['compression'].setValue("PIZ Wavelet (32 scanlines)")
    write_node['metadata'].setValue("all metadata")
    write_node['first_part'].setValue("rgba")
    write_node['create_directories'].setValue(True)
    
    # Position the Write node
    write_node.setXYpos(copy_metadata.xpos(), copy_metadata.ypos() + 100)
    write_node.setName(f"Write_{original_shot}_{delivery_version}")
    
    # Log the delivery information
    log_delivery(
        source_shot=shot_name,
        delivery_shot=original_shot,
        source_version=source_version,
        delivery_version=delivery_version,
        source_path=file_path,
        delivery_path=output_path
    )
    
    return True, f"Successfully processed {shot_name} to {original_shot}", {
        "original_read": original_read,
        "copy_metadata": copy_metadata,
        "write_node": write_node
    }

def process_plate():
    """
    Main function that combines all steps:
    1. Find original plate
    2. Copy metadata
    3. Create delivery Write node
    """
    # Get selected nodes
    selected_nodes = nuke.selectedNodes('Read')
    
    if not selected_nodes:
        nuke.message("Please select a Read node.")
        return
    
    read_node = selected_nodes[0]
    
    # Process the selected read node
    return process_single_plate(read_node)

def batch_process_plates():
    """
    Process multiple Read nodes at once.
    """
    # Get all selected Read nodes
    selected_nodes = nuke.selectedNodes('Read')
    
    if not selected_nodes:
        # If no nodes are selected, show a shot selection dialog
        return batch_process_from_list()
    
    # Process each selected Read node
    results = []
    for read_node in selected_nodes:
        success, message, nodes = process_single_plate(read_node)
        results.append((read_node.name(), success, message))
    
    # Show summary
    summary = "Batch Processing Results:\n\n"
    for node_name, success, message in results:
        status = "✓ Success" if success else "✗ Failed"
        summary += f"{node_name}: {status} - {message}\n"
    
    nuke.message(summary)

def batch_process_from_list():
    """
    Show a dialog with all available shots and process the selected ones.
    """
    # Create a dialog with a list of all shots in the mapping
    shot_choices = sorted(list(SHOT_MAPPING.keys()))
    
    # Create a multiline text field with shots
    shot_dialog = nuke.Panel("Select Shots to Process")
    shot_dialog.addMultilineTextInput("Shots", "\n".join(shot_choices[:10]) + "\n\n(Edit this list to include only the shots you want to process)")
    shot_dialog.addBooleanCheckBox("Overwrite Existing v001", False)
    
    if not shot_dialog.show():
        return  # User cancelled
    
    # Get the selected shots from the text field
    selected_shots_text = shot_dialog.value("Shots")
    overwrite_existing = shot_dialog.value("Overwrite Existing v001")
    
    # Parse the text to get a list of shots
    selected_shots = [shot.strip() for shot in selected_shots_text.split('\n') if shot.strip() in SHOT_MAPPING]
    
    if not selected_shots:
        nuke.message("No valid shots selected for processing.")
        return
    
    # Confirm the selections
    confirm_msg = f"You are about to process {len(selected_shots)} shots:\n\n"
    for shot in selected_shots[:10]:
        confirm_msg += f"• {shot} -> {SHOT_MAPPING[shot]}\n"
    
    if len(selected_shots) > 10:
        confirm_msg += f"• ... and {len(selected_shots) - 10} more\n"
    
    if overwrite_existing:
        confirm_msg += "\nWARNING: You have chosen to overwrite existing v001 deliveries!"
    
    confirm_msg += "\n\nDo you want to continue?"
    
    if not nuke.ask(confirm_msg):
        return  # User cancelled
    
    # Setup version handling for batch
    version_choice = 2 if overwrite_existing else 1  # 1=New Version, 2=Overwrite v001
    
    # Process each selected shot
    results = []
    processed_count = 0
    
    # Create a progress bar
    progress_task = nuke.ProgressTask("Batch Processing")
    progress_task.setMessage("Setting up...")
    
    try:
        for i, shot in enumerate(selected_shots):
            if progress_task.isCancelled():
                nuke.message("Batch processing cancelled by user.")
                break
            
            # Update progress
            progress_task.setProgress(int((i / float(len(selected_shots))) * 100))
            progress_task.setMessage(f"Processing {shot}...")
            
            # Create a proper Read node for this shot
            # Need to create a Read node with a file path that will extract to the correct shot name
            dummy_read = nuke.createNode("Read", inpanel=False)
            dummy_read['file'].setValue(f"/path/to/{shot}/dummy_filename.exr")
            dummy_read.setName(f"DummyRead_{shot}")
            
            # Process the shot with batch mode enabled and version override
            try:
                success, message, nodes = process_single_plate(
                    dummy_read, 
                    batch_mode=True,
                    version_choice_override=version_choice
                )
                results.append((shot, success, message))
                processed_count += 1 if success else 0
                
                # If processing failed, clean up the nodes
                if not success:
                    # Clean up the nodes
                    for node in [dummy_read]:
                        if node:
                            nuke.delete(node)
                            
            except Exception as e:
                import traceback
                error_msg = traceback.format_exc()
                results.append((shot, False, f"Error: {str(e)}\n{error_msg}"))
                
                # Clean up the nodes
                for node in [dummy_read]:
                    if node:
                        nuke.delete(node)
    finally:
        # Make sure to get rid of the progress bar
        del progress_task
    
    # Show summary
    summary = f"Batch Processing Complete\n\n"
    summary += f"Successfully processed: {processed_count}/{len(selected_shots)} shots\n\n"
    
    for shot, success, message in results:
        status = "✓ Success" if success else "✗ Failed"
        summary += f"{shot}: {status} - {message}\n"
    
    nuke.message(summary)

# Create menu items
menu = nuke.menu('Nuke').addMenu('Plate Processor')
menu.addCommand('Process Plate (Find, Copy Metadata, Create Write)', process_plate)
menu.addCommand('Batch Process Multiple Plates', batch_process_plates)
menu.addCommand('Edit Settings', 'nuke.tab("Preferences").showPanel("PlateProcessor")', '')

# If you want to run this when the script is directly executed
if __name__ == "__main__":
    process_plate()
