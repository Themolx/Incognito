#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integrated Plate Processor
This script combines plate finding and delivery functionalities:
1. Finds the original plate based on shot mapping (for raw plates)
2. Copies metadata from the original plate to the selected Read node (for raw plates)
3. Creates a Write node for delivery with appropriate settings

TIFF files (full CG shots):
- Bypass loading raw footage.
- Set the input colorspace to "color_picking".

Export paths are now structured as:
    <OUTPUT_BASE_DIR>/<shot>/<version>/<shot>_<version>.####.exr

This version processes multiple selected Read nodes.
"""

import nuke
import os
import re
import datetime
import csv

# Shot name mapping dictionary
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
    'ME1_0275': 'EP01_G_275',  # New mapping added
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
    'ME1_0450': 'EP01_D_450',  # New mapping added for ME1_0450
    'ME1_0460': 'EP01_D_460',
    'ME1_0470': 'EP01_D_470',
    'ME1_0480': 'EP01_D_480',
    'ME1_0490': 'EP01_D_490',
    'ME1_0500': 'EP01_G_500',
    'ME1_0510': 'EP01_D_510',
    'ME1_0520': 'EP01_D_520',
    'ME1_0560': 'EP01_G_560',
    'ME1_0570': 'EP01_G_570',
    'ME1_0580': 'EP01_D_580',
    'ME1_0590': 'EP01_G_590',
    'ME1_0591': 'EP01_G_591',
    'ME1_0595': 'EP01_G_595',
    'ME1_0630': 'EP01_G_630',  # New mapping added
    'ME1_0640': 'EP01_G_640',  # New mapping added
    'ME1_0650': 'EP01_G_650',  # New mapping added
    'ME1_0660': 'EP01_D_660',  # New mapping added
    'ME1_0670': 'EP01_D_670',  # New mapping added
    'ME1_0680': 'EP01_D_680',  # New mapping added
    'ME1_0700': 'EP01_G_700',
    'ME1_0710': 'EP01_G_710',
    'ME1_0715': 'EP01_D_715',
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
    'ME1_0820': 'EP01_D_820',
    'ME1_0830': 'EP01_D_830',
    'ME1_0832': 'EP01_D_832',
    'ME1_0840': 'EP01_D_840',
    'ME1_0850': 'EP01_G_850',
    'ME1_0860': 'EP01_G_860',
    'ME1_0870': 'EP01_G_870',
    'ME1_0880': 'EP01_G_880',
    'ME1_0890': 'EP01_G_890',
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
    user_prefs = nuke.toNode("preferences")
    
    if not user_prefs.knob("PlateProcessor"):
        tab = nuke.Tab_Knob('PlateProcessor', 'Plate Processor')
        divider = nuke.Text_Knob('plateProcessorDivider', '', 'Path Configuration')
        output_dir_knob = nuke.String_Knob('plateProcessorOutputDir', 'Output Directory', DEFAULT_OUTPUT_BASE_DIR)
        output_dir_knob.setTooltip('Base directory for delivered files')
        source_dir_knob = nuke.String_Knob('plateProcessorSourceDir', 'Source Plates Directory', DEFAULT_SOURCE_PLATES_DIR)
        source_dir_knob.setTooltip('Directory containing original plates')
        log_dir_knob = nuke.String_Knob('plateProcessorLogDir', 'Log Directory', DEFAULT_LOG_FILE_DIR)
        log_dir_knob.setTooltip('Directory where delivery logs will be saved')
        log_file_knob = nuke.String_Knob('plateProcessorLogFileName', 'Log File Name', DEFAULT_LOG_FILE_NAME)
        log_file_knob.setTooltip('Name of the CSV file for logging deliveries')
        
        user_prefs.addKnob(tab)
        user_prefs.addKnob(divider)
        user_prefs.addKnob(output_dir_knob)
        user_prefs.addKnob(source_dir_knob)
        user_prefs.addKnob(log_dir_knob)
        user_prefs.addKnob(log_file_knob)
    
    config = {
        'OUTPUT_BASE_DIR': user_prefs['plateProcessorOutputDir'].value() or DEFAULT_OUTPUT_BASE_DIR,
        'SOURCE_PLATES_DIR': user_prefs['plateProcessorSourceDir'].value() or DEFAULT_SOURCE_PLATES_DIR,
        'LOG_FILE_DIR': user_prefs['plateProcessorLogDir'].value() or DEFAULT_LOG_FILE_DIR,
        'LOG_FILE_NAME': user_prefs['plateProcessorLogFileName'].value() or DEFAULT_LOG_FILE_NAME
    }
    
    return config

CONFIG = setup_user_variables()
OUTPUT_BASE_DIR = CONFIG['OUTPUT_BASE_DIR']
SOURCE_PLATES_DIR = CONFIG['SOURCE_PLATES_DIR']
LOG_FILE_DIR = CONFIG['LOG_FILE_DIR']
LOG_FILE_NAME = CONFIG['LOG_FILE_NAME']

def extract_shot_name(file_path):
    """
    Extract shot name from file path.
    """
    match = re.search(r'(ME1_\d{4})', file_path)
    return match.group(1) if match else None

def extract_version(file_path):
    """
    Extract the version number from the file path.
    """
    match = re.search(r'v(\d{3})', file_path)
    return f"v{match.group(1)}" if match else None

def get_latest_delivered_version(shot_name):
    """
    Find the latest version delivered for a specific shot by reading the log file.
    """
    log_file_path = os.path.join(LOG_FILE_DIR, LOG_FILE_NAME)
    if not os.path.exists(log_file_path):
        if not os.path.exists(LOG_FILE_DIR):
            os.makedirs(LOG_FILE_DIR)
        with open(log_file_path, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'source_shot', 'delivery_shot', 'source_version', 'delivery_version', 'source_path', 'delivery_path']
            csv.DictWriter(csvfile, fieldnames=fieldnames).writeheader()
        return None, None
    
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
    Log delivery information to a CSV file.
    """
    log_file_path = os.path.join(LOG_FILE_DIR, LOG_FILE_NAME)
    if not os.path.exists(LOG_FILE_DIR):
        os.makedirs(LOG_FILE_DIR)
    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'source_shot', 'delivery_shot', 'source_version', 'delivery_version', 'source_path', 'delivery_path']
            csv.DictWriter(csvfile, fieldnames=fieldnames).writeheader()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file_path, 'a', newline='') as csvfile:
        fieldnames = ['timestamp', 'source_shot', 'delivery_shot', 'source_version', 'delivery_version', 'source_path', 'delivery_path']
        csv.DictWriter(csvfile, fieldnames=fieldnames).writerow({
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
    Process a single Read node.
    For TIFF files: set colorspace to "color_picking" and bypass loading raw footage.
    For non-TIFF files: process as before (load raw plate, copy metadata, etc.)
    """
    file_path = read_node['file'].value()
    
    # Process TIFF files (full CG shots)
    if file_path.lower().endswith(('.tif', '.tiff')):
        if 'colorspace' in read_node.knobs():
            read_node['colorspace'].setValue('color_picking')
        
        shot_name = extract_shot_name(file_path)
        if not shot_name:
            if not batch_mode:
                nuke.message(f"Could not extract shot name from {file_path}")
            return False, f"Could not extract shot name from {file_path}", {}
        
        delivery_shot = SHOT_MAPPING.get(shot_name, shot_name)
        source_version = extract_version(file_path) or "unknown"
        
        # Use internal version as delivery version instead of converting to v001
        delivery_version = source_version or "v001"
        
        latest_version, version_info = get_latest_delivered_version(delivery_shot)
        
        if latest_version:
            if batch_mode and version_choice_override is not None:
                version_choice = version_choice_override
            else:
                msg = (f"Shot {delivery_shot} has already been delivered as {latest_version}.\n"
                       f"Last delivery was from source {version_info['source_version']} on {version_info['timestamp']}.\n\n")
                version_choice = nuke.choice("Version Options", f"Shot {delivery_shot} already delivered", 
                                             ["Cancel", f"Use source version ({delivery_version})", "Overwrite existing version"])
            if version_choice == 0:
                if not batch_mode:
                    nuke.message("Delivery cancelled")
                return False, "Delivery cancelled", {}
            elif version_choice == 1:
                # Keep delivery_version as source_version (already set above)
                pass
            elif version_choice == 2:
                if not batch_mode:
                    nuke.message(f"WARNING: Overwriting existing delivery for {delivery_shot}!")
        
        # New folder structure: <OUTPUT_BASE_DIR>/<shot>/<version>/
        output_dir = f"{OUTPUT_BASE_DIR}/{delivery_shot}/{delivery_version}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_path = f"{output_dir}/{delivery_shot}_{delivery_version}.####.exr"
        
        write_node = nuke.createNode("Write")
        write_node.setInput(0, read_node)
        write_node['channels'].setValue("all")
        write_node['file'].setValue(output_path)
        write_node['file_type'].setValue("exr")
        write_node['compression'].setValue("PIZ Wavelet (32 scanlines)")
        write_node['metadata'].setValue("all metadata")
        write_node['first_part'].setValue("rgba")
        write_node['create_directories'].setValue(True)
        write_node.setXYpos(read_node.xpos(), read_node.ypos() + 100)
        write_node.setName(f"Write_{delivery_shot}_{delivery_version}")
        
        log_delivery(
            source_shot=shot_name,
            delivery_shot=delivery_shot,
            source_version=source_version,
            delivery_version=delivery_version,
            source_path=file_path,
            delivery_path=output_path
        )
        
        return True, f"Successfully processed {shot_name} (full CG shot)", {"write_node": write_node}
    
    # Process non-TIFF files (raw plates)
    shot_name = extract_shot_name(file_path)
    if not shot_name:
        if not batch_mode:
            nuke.message(f"Could not extract shot name from {file_path}")
        return False, f"Could not extract shot name from {file_path}", {}
    
    if shot_name not in SHOT_MAPPING:
        if not batch_mode:
            nuke.message(f"Shot {shot_name} not found in the mapping dictionary.")
        return False, f"Shot {shot_name} not found in the mapping dictionary.", {}
    
    original_shot = SHOT_MAPPING[shot_name]
    shot_number = original_shot.split('_')[-1]
    original_shot_with_zero = f"{original_shot[:6]}_0{shot_number}"
    original_plate_path = f"{SOURCE_PLATES_DIR}/{original_shot_with_zero}/{original_shot_with_zero}.####.exr"

    source_dir = os.path.dirname(original_plate_path.replace("####", "0001"))
    # If original directory not found, try with L1 suffix
    if not os.path.exists(source_dir):
        # Try alternate L1 naming pattern
        original_shot_with_l1 = f"{original_shot_with_zero}_L1"
        l1_plate_path = f"{SOURCE_PLATES_DIR}/{original_shot_with_l1}/{original_shot_with_l1}.####.exr"
        l1_source_dir = os.path.dirname(l1_plate_path.replace("####", "0001"))
        
        if os.path.exists(l1_source_dir):
            original_plate_path = l1_plate_path
            source_dir = l1_source_dir
        else:
            if not batch_mode:
                nuke.message(f"Original plate directory not found: {source_dir}\nAlso checked: {l1_source_dir}")
            return False, f"Original plate directory not found: {source_dir} or {l1_source_dir}", {}
    
    original_read = nuke.createNode("Read")
    original_read['file'].setValue(original_plate_path)
    original_read['file_type'].setValue('exr')
    if 'first' in read_node.knobs() and 'last' in read_node.knobs():
        original_read['first'].setValue(read_node['first'].value())
        original_read['last'].setValue(read_node['last'].value())
        original_read['origfirst'].setValue(read_node['first'].value())
        original_read['origlast'].setValue(read_node['last'].value())
    if 'format' in read_node.knobs():
        original_read['format'].setValue(read_node['format'].value())
    original_read['origset'].setValue(True)
    original_read.setXYpos(read_node.xpos() + 100, read_node.ypos())
    
    copy_metadata = nuke.createNode("CopyMetaData")
    copy_metadata.setInput(0, read_node)
    copy_metadata.setInput(1, original_read)
    copy_metadata.setXYpos(original_read.xpos() + 100, original_read.ypos() + 50)
    
    original_read.setName(f"OriginalPlate_{shot_name}")
    copy_metadata.setName(f"CopyMetaData_{shot_name}")
    
    source_version = extract_version(file_path) or "unknown"
    
    # Use internal version as delivery version instead of converting to v001
    delivery_version = source_version or "v001"
    
    latest_version, version_info = get_latest_delivered_version(original_shot)
    
    if latest_version:
        if batch_mode and version_choice_override is not None:
            version_choice = version_choice_override
        else:
            msg = (f"Shot {original_shot} has already been delivered as {latest_version}.\n"
                   f"Last delivery was from source {version_info['source_version']} on {version_info['timestamp']}.\n\n")
            version_choice = nuke.choice("Version Options", f"Shot {original_shot} already delivered",
                                         ["Cancel", f"Use source version ({delivery_version})", "Overwrite existing version"])
        if version_choice == 0:
            if not batch_mode:
                nuke.message("Delivery cancelled")
            return False, "Delivery cancelled", {"original_read": original_read, "copy_metadata": copy_metadata}
        elif version_choice == 1:
            # Keep delivery_version as source_version (already set above)
            pass
        elif version_choice == 2:
            if not batch_mode:
                nuke.message(f"WARNING: Overwriting existing delivery for {original_shot}!")
    
    # New folder structure: <OUTPUT_BASE_DIR>/<shot>/<version>/
    output_dir = f"{OUTPUT_BASE_DIR}/{original_shot}/{delivery_version}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = f"{output_dir}/{original_shot}_{delivery_version}.####.exr"
    
    write_node = nuke.createNode("Write")
    write_node.setInput(0, copy_metadata)
    write_node['channels'].setValue("all")
    write_node['file'].setValue(output_path)
    write_node['file_type'].setValue("exr")
    write_node['compression'].setValue("PIZ Wavelet (32 scanlines)")
    write_node['metadata'].setValue("all metadata")
    write_node['first_part'].setValue("rgba")
    write_node['create_directories'].setValue(True)
    write_node.setXYpos(copy_metadata.xpos(), copy_metadata.ypos() + 100)
    write_node.setName(f"Write_{original_shot}_{delivery_version}")
    
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
    Process all selected Read nodes.
    For each node, perform the operations (TIFF or non-TIFF) and display a summary.
    """
    selected_nodes = nuke.selectedNodes('Read')
    if not selected_nodes:
        nuke.message("Please select one or more Read nodes.")
        return
    results = []
    for read_node in selected_nodes:
        success, message, nodes = process_single_plate(read_node)
        results.append((read_node.name(), success, message))
    
    summary = "Processing Results:\n\n"
    for node_name, success, message in results:
        status = "✓ Success" if success else "✗ Failed"
        summary += f"{node_name}: {status} - {message}\n"
    nuke.message(summary)

def batch_process_plates():
    """
    Process multiple Read nodes with batch processing options.
    """
    selected_nodes = nuke.selectedNodes('Read')
    if not selected_nodes:
        return batch_process_from_list()
    results = []
    for read_node in selected_nodes:
        success, message, nodes = process_single_plate(read_node)
        results.append((read_node.name(), success, message))
    summary = "Batch Processing Results:\n\n"
    for node_name, success, message in results:
        status = "✓ Success" if success else "✗ Failed"
        summary += f"{node_name}: {status} - {message}\n"
    nuke.message(summary)

def batch_process_from_list():
    """
    Show a dialog to select shots and process them.
    """
    shot_choices = sorted(list(SHOT_MAPPING.keys()))
    shot_dialog = nuke.Panel("Select Shots to Process")
    shot_dialog.addMultilineTextInput("Shots", "\n".join(shot_choices[:10]) + "\n\n(Edit to include only the shots you want)")
    shot_dialog.addBooleanCheckBox("Overwrite Existing v001", False)
    if not shot_dialog.show():
        return
    selected_shots_text = shot_dialog.value("Shots")
    overwrite_existing = shot_dialog.value("Overwrite Existing v001")
    selected_shots = [shot.strip() for shot in selected_shots_text.split('\n') if shot.strip() in SHOT_MAPPING]
    if not selected_shots:
        nuke.message("No valid shots selected for processing.")
        return
    confirm_msg = f"You are about to process {len(selected_shots)} shots:\n\n"
    for shot in selected_shots[:10]:
        confirm_msg += f"• {shot} -> {SHOT_MAPPING[shot]}\n"
    if len(selected_shots) > 10:
        confirm_msg += f"• ... and {len(selected_shots) - 10} more\n"
    if overwrite_existing:
        confirm_msg += "\nWARNING: Overwriting existing v001 deliveries!"
    confirm_msg += "\n\nDo you want to continue?"
    if not nuke.ask(confirm_msg):
        return
    version_choice = 2 if overwrite_existing else 1
    results = []
    processed_count = 0
    progress_task = nuke.ProgressTask("Batch Processing")
    progress_task.setMessage("Setting up...")
    try:
        for i, shot in enumerate(selected_shots):
            if progress_task.isCancelled():
                nuke.message("Batch processing cancelled by user.")
                break
            progress_task.setProgress(int((i / float(len(selected_shots))) * 100))
            progress_task.setMessage(f"Processing {shot}...")
            dummy_read = nuke.createNode("Read", inpanel=False)
            dummy_read['file'].setValue(f"/path/to/{shot}/dummy_filename.exr")
            dummy_read.setName(f"DummyRead_{shot}")
            try:
                success, message, nodes = process_single_plate(
                    dummy_read, 
                    batch_mode=True,
                    version_choice_override=version_choice
                )
                results.append((shot, success, message))
                processed_count += 1 if success else 0
                if not success:
                    nuke.delete(dummy_read)
            except Exception as e:
                import traceback
                error_msg = traceback.format_exc()
                results.append((shot, False, f"Error: {str(e)}\n{error_msg}"))
                nuke.delete(dummy_read)
    finally:
        del progress_task
    summary = f"Batch Processing Complete\n\nSuccessfully processed: {processed_count}/{len(selected_shots)} shots\n\n"
    for shot, success, message in results:
        status = "✓ Success" if success else "✗ Failed"
        summary += f"{shot}: {status} - {message}\n"
    nuke.message(summary)

# Create menu items
menu = nuke.menu('Nuke').addMenu('Plate Processor')
menu.addCommand('Process Plates (All Selected Reads)', process_plate)
menu.addCommand('Batch Process Multiple Plates', batch_process_plates)
menu.addCommand('Edit Settings', 'nuke.tab("Preferences").showPanel("PlateProcessor")', '')

if __name__ == "__main__":
    # Reposition all selected Read nodes in a grid pattern (spaced 200px apart in X, fixed Y)
    read_nodes = nuke.selectedNodes("Read")
    if read_nodes:
        fixed_y = read_nodes[0].ypos()
        read_nodes.sort(key=lambda n: n.xpos())
        start_x = read_nodes[0].xpos()
        for i, node in enumerate(read_nodes):
            node.setXpos(start_x + i * 200)
            node.setYpos(fixed_y)
    else:
        nuke.message("No selected Read nodes found.")
    
    process_plate()
