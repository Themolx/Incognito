#!/usr/bin/env python
import os
import sys
import datetime
import copy
import re

# USER EDITABLE VARIABLES:
VERSION_PREFIX = "v"
GRANDPARENT_FOLDER_INDEX = 3
DIGITS_FOR_VERSION = 3

# Example paths:
# version 1 example: C:\Film\shots\012\012_0010\publish\plate\platePlate\v001\Film_012_0010_platePlate_v001_h264.mp4
# version 2 example: C:\Film\shots\012\012_0010\publish\plate\platePlate\v002\Film_012_0010_platePlate_v002_h264.mp4

# ------------------------------------------------------------------
# DaVinci Resolve initialization (make sure this script is run within Resolve's scripting environment)
resolve = app.GetResolve()
fusion = resolve.Fusion()
projectManager = resolve.GetProjectManager()
mediastorage = resolve.GetMediaStorage()
getproject = projectManager.GetCurrentProject()
mediapool = getproject.GetMediaPool()
rootFolder = mediapool.GetRootFolder()
media = rootFolder.GetClipList()

def find_newest_version_path(input_path):
    # Split the path into components and filter out empty strings.
    path_components = [comp for comp in input_path.split(os.path.sep) if comp]

    # Determine the grandparent directory (assumes version folder is the second-to-last element)
    grandparent_directory_index = len(path_components) - 3
    grandparent_directory_path = os.path.join(*path_components[:grandparent_directory_index + 1])

    # List entries in the grandparent directory
    try:
        files_in_grandparent_directory = os.listdir(grandparent_directory_path)
    except Exception as e:
        print(f"Error listing directory {grandparent_directory_path}: {e}")
        return None

    # Extract the version folder and its prefix
    version_file = path_components[-2]
    version_file_prefix = version_file[:-3]  # Remove version number

    # Filter for matching version directories/files
    matching_versions = [filename for filename in files_in_grandparent_directory if filename.startswith(version_file_prefix)]
    
    if matching_versions:
        # If versions include the "v" marker, determine the newest version
        if "v" in matching_versions[0]:
            newest_version = max(matching_versions)
            print("Found versions:", matching_versions)
            # Update the version in the file name (last component)
            file_name_parts = path_components[-1].split("_v")
            if ".exr" in path_components[-1]:
                file_name_parts[-1] = newest_version + "." + transform_filename(file_name_parts[-1][4:])
                path_components[-1] = "_".join(file_name_parts)
                print("Handling .exr file naming.")
            else:
                file_name_parts[-1] = newest_version + file_name_parts[-1][3:]
                path_components[-1] = "_".join(file_name_parts)
            
            newest_version_path = os.path.join(*path_components)
            newest_version_path_fixed = newest_version_path.replace(version_file, newest_version)
            return newest_version_path_fixed
        else:
            return None
    else:
        return None

def extract_version(base_name):
    # Extracts the version number from a string ending with _v<number>
    pattern = r'_v(\d+)$'
    match = re.search(pattern, base_name)
    if match:
        version_number = match.group(1)
        print("Extracted version number:", version_number)
        return version_number
    else:
        print("No version number found in", base_name)
        return None

def find_newest_version_in_folder(file_path):
    # Separate folder and file name
    folder_path, file_name = os.path.split(file_path)
    base_name, extension = os.path.splitext(file_name)
    
    # Use the part before '_v' as the identifier
    new_base_name = base_name.split('_v')[0]
    print(f"Base name: {base_name} | Identifier: {new_base_name}")
    
    highest_version = 0
    for file in os.listdir(folder_path):
        if new_base_name in file:
            print("Matching file found:", file)
            file_name_only, _ = os.path.splitext(file)
            try:
                version_str = extract_version(file_name_only)
                if version_str is None:
                    continue
                version = int(version_str)
                if version > highest_version:
                    highest_version = version
                    print("New highest version:", highest_version)
            except (ValueError, TypeError):
                continue

    print("Highest version in folder:", highest_version)
    if highest_version > 0:
        newest_file_path = os.path.join(folder_path, f"{new_base_name}_v{highest_version}{extension}")
        print("Newest file path candidate:", newest_file_path)
        if os.path.exists(newest_file_path):
            return newest_file_path
    return None

def transform_filename(filename):
    first_number = filename[1:5]
    file_type = filename[-4:]
    result = first_number + file_type
    print("Transformed filename:", result)
    return result

def replace_one_clip(item):
    print("\nProcessing clip:", item)
    clip_name = item.GetClipProperty("Clip Name")
    print("Current Clip Name:", clip_name)
    item_path = item.GetClipProperty("File Path")
    print("Original File Path:", item_path)
    
    # Try to determine the new file path via version lookup
    new_file_path = find_newest_version_path(item_path)
    if new_file_path is None:
        new_file_path = find_newest_version_in_folder(item_path)
    
    if new_file_path is None:
        print("No newer version found for clip:", clip_name)
        return False

    new_file_name = os.path.basename(new_file_path)
    # Adjust path formatting if necessary
    new_file_path_raw = new_file_path.replace("\\", "\\")
    new_file_path_edited = new_file_path_raw.replace(":", ":\\")
    print("New file name:", new_file_name)
    print("New file path:", new_file_path_edited)
    
    # Update clip properties with the new version
    item.SetClipProperty('File Name', new_file_name)
    item.SetClipProperty('Clip Name', new_file_name)
    item.ReplaceClip(new_file_path_edited)
    item.SetClipProperty("File Path", new_file_path_edited)
    
    print("Updated Clip Properties:")
    print("  File Name:", item.GetClipProperty("File Name"))
    print("  Clip Name:", item.GetClipProperty("Clip Name"))
    print("  File Path:", item.GetClipProperty("File Path"))
    return True

def create_update_message():
    print("\n=== Timeline Update Finished ===\n")

def update_timeline():
    current_timeline = getproject.GetCurrentTimeline()
    if current_timeline is None:
        print("No current timeline found.")
        return

    for track_type in ["video", "audio"]:
        number_of_tracks = current_timeline.GetTrackCount(track_type)
        all_timeline_items = []
        for i in range(1, number_of_tracks + 1):
            item_list = current_timeline.GetItemListInTrack(track_type, i)
            for il in item_list:
                if il not in all_timeline_items:
                    all_timeline_items.append(il)
        for item in all_timeline_items:
            print("Timeline clip color:", item.GetClipColor())
            original_color = item.GetClipColor()
            # Skip clips that are marked with a specific color ("Chocolate" in this case)
            if original_color != "Chocolate":
                if replace_one_clip(item.GetMediaPoolItem()):
                    item.SetClipColor(original_color)
    create_update_message()

# Run only the timeline update when the script is executed
if __name__ == "__main__":
    update_timeline()
