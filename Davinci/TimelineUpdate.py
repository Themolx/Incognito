#!/usr/bin/env python
import os
import sys
import datetime
import copy
from threading import currentThread
import tkinter as tk
from datetime import datetime
from tkinter import filedialog
import re


#USER EDITABLE VARIABLES:
VERSION_PREFIX = "v"
WINDOW_ALWAYS_ON_TOP = True
GRANDPARENT_FOLDER_INDEX = 3
DIGITS_FOR_VERSION = 3

#Example:
#version 1 example: C:\Film\shots\012\012_0010\publish\plate\platePlate\v001\Film_012_0010_platePlate_v001_h264.mp4
#version 2 example: C:\Film\shots\012\012_0010\publish\plate\platePlate\v002\Film_012_0010_platePlate_v002_h264.mp4

#Other "GRANDPARENT_FOLDER_INDEX = 4" example:
#version 1 example: C:\Film\shots\012\012_0010\publish\plate\platePlate\v001\Test\Film_012_0010_platePlate_v001_h264.mp4
#version 2 example: C:\Film\shots\012\012_0010\publish\plate\platePlate\v002\Test\Film_012_0010_platePlate_v002_h264.mp4

#Other "VERSION_PREFIX = version" example:
#version 1 example: C:\Film\shots\012\012_0010\publish\plate\platePlate\version001\Film_012_0010_platePlate_version001_h264.mp4
#version 2 example: C:\Film\shots\012\012_0010\publish\plate\platePlate\version002\Film_012_0010_platePlate_version002_h264.mp4



resolve = app.GetResolve()
fusion = resolve.Fusion()
projectManager = resolve.GetProjectManager()
mediastorage = resolve.GetMediaStorage()
getproject = projectManager.GetCurrentProject()
mediapool = getproject.GetMediaPool()
rootFolder = mediapool.GetRootFolder()
media = rootFolder.GetClipList()



def find_newest_version_path(input_path):
    # Split the path into components
    path_components = input_path.split(os.path.sep)

    # Ensure there are no empty elements in path_components
    path_components = [component for component in path_components if component]

    # Find the index of the grandparent directory in the path
    grandparent_directory_index = len(path_components) - 3

    # Construct the path to the grandparent directory
    grandparent_directory_path = os.path.join(*path_components[:grandparent_directory_index + 1])

    # List all files and directories in the grandparent directory
    files_in_grandparent_directory = os.listdir(grandparent_directory_path)

    # Extract the version prefix from the path¨
    version_file = path_components[-2]
    version_file_prefix = version_file[:-3]  # Exclude the version number from the path
    
    # Filter files in the grandparent directory that match the version prefix
    matching_versions = [filename for filename in files_in_grandparent_directory if filename.startswith(version_file_prefix)]

    # If there are matching versions, find the newest one
    if matching_versions:
        if "v" in matching_versions[0]:
            newest_version = max(matching_versions)
            print("VERSIONS: ", matching_versions)
            # Update the version in the last part of the path
            file_name_parts = path_components[-1].split("_v")
        
        

            if ".exr" in path_components[-1]: #Checks if .exr
                file_name_parts[-1] = newest_version + "." + transform_filename(file_name_parts[-1][4:])
                path_components[-1] = "_".join(file_name_parts)
                print("true")
            else:
                file_name_parts[-1] = newest_version + file_name_parts[-1][3:] #file_name_parts[-1] = newest_version + "_" + file_name_parts[-1].split("_", 1)[-1]
                path_components[-1] = "_".join(file_name_parts)

            # Construct the path to the newest version
            newest_version_path = os.path.join(*path_components)
            newest_version_path_fixed = newest_version_path.replace(version_file, newest_version)
            return newest_version_path_fixed
        else:
            return None
    else:
        return None



def extract_version(base_name):
    # Regular expression pattern to match version number
    pattern = r'_v(\d+)$'

#Search for the pattern in the base name
    match = re.search(pattern, base_name)

    if match:
        version_number = match.group(1)
        print("Version number:", version_number)
        return version_number
    else:
        print("No version number found")


def find_newest_version_in_folder(file_path):
    # Split the provided file path into folder path and file name
    folder_path, file_name = os.path.split(file_path)

#Split the file name into base name and extension
    base_name, extension = os.path.splitext(file_name)

#Extract the part of the base name before "_v"
    new_base_name = base_name.split('_v')[0]
    print(base_name, "   ", new_base_name)
    # Initialize the highest version number found
    highest_version = 0

    # Iterate through files in the folder
    for file in os.listdir(folder_path):
        # Check if the new base name is contained in the file name
        if new_base_name in file:
            print(file)
            file_name, extension = os.path.splitext(file)
            try:
                # Extract the version number from the file name
                version = int(extract_version(file_name))
                # Update the highest version number if a higher version is found
                print(version)
                if version > highest_version:
                    highest_version = version
                    print("true")
                    
            except ValueError:
                # If the file name does not contain a valid version number, skip it
                pass
    print(highest_version)
    # If a higher version is found, construct the file path and return it
    if highest_version > 0:
        newest_file_path = os.path.join(folder_path, f"{new_base_name}_v{highest_version}{extension}")
        print(newest_file_path)
        if os.path.exists(newest_file_path):
            return newest_file_path

    # If no higher version is found, return None
    return None

def transform_filename(filename):
    first_number = filename[1:5]
    file_type = filename[-4:]
    print(first_number + file_type)
    return first_number + file_type

def replace_one_clip(item):
        print("ITEM: ", item)
        print("ITEM NAME: ", item.GetClipProperty("Clip Name"))
        item_path = item.GetClipProperty("File Path")
        print("PATH: ", item_path)
        
        # Turn path to absolute path
        new_file_path = find_newest_version_path(item_path)
        if new_file_path == None:
            new_file_path = find_newest_version_in_folder(item_path)
        
        new_file_name = os.path.basename(new_file_path)
        new_file_path_raw = new_file_path.replace("\\", "\\")
        new_file_path_edited = new_file_path_raw.replace(":", ":\\")
        print(new_file_name, new_file_path, new_file_path_edited)
        
        # Replace item properties
        item.SetClipProperty('File Name', new_file_name)
        
        
        item.SetClipProperty('Clip Name', new_file_name)
        

        item.ReplaceClip(new_file_path_edited)
        item.SetClipProperty("File Path", new_file_path_edited)
        
        

        print("NEW FILE NAME: ", item.GetClipProperty("File Name"), "NEW CLIP NAME: ", item.GetClipProperty('Clip Name'), "NEW FILE PATH: ", item.GetClipProperty("File Path"))
        return True



all_clips = []


def is_audio_video(item):
    clip_properties = item.GetClipProperty()

    media_type = clip_properties['Type']
    file_path = item.GetClipProperty('File Path')
    file_extension = os.path.splitext(file_path)[-1].lower()

    if media_type in ["Video + Audio", "Audio", "Video"] or file_extension == ".exr": # Checks for video/audio files
        print("Media Type: ", media_type)
        return True
    else:
        print("Media Type: ", media_type, " Wrong media skipping..")
        return False

def list_clips_in_folder(folder):
    for clip in folder.GetClipList():

        all_clips.append(clip)
    


def create_update_window():
    # Create the main window
    window = tk.Tk()
    window.title("Update Status")
    window.attributes('-topmost', WINDOW_ALWAYS_ON_TOP)
    # Create a label with the desired text
    label = tk.Label(window, text="Updating Finished", font=("Helvetica", 16))

    # Pack the label into the window
    label.pack(padx=20, pady=20)


    # Run the Tkinter event loop
    window.mainloop()

# Function to recursively traverse through folders and subfolders
def traverse_folders(folder):
    list_clips_in_folder(folder)

    for subfolder in folder.GetSubFolderList():
        traverse_folders(subfolder)

def update_all():
    traverse_folders(rootFolder)
    for item in all_clips:
        if is_audio_video(item):
            replace_one_clip(item)
    create_update_window()

# Function for updating all mediapool items in folder
def update_folder():
    getcurrentfolder = mediapool.GetCurrentFolder()
    for item in getcurrentfolder.GetClipList():
        if is_audio_video(item):
            replace_one_clip(item)
    create_update_window()

def update_timeline():
    current_timeline = getproject.GetCurrentTimeline()
    for track_type in ["video", "audio"]:
        number_of_tracks = 0
        number_of_tracks = current_timeline.GetTrackCount(track_type)
        print(current_timeline.GetItemListInTrack(track_type, 1))

        all_timeline_items = []
        for i in range(1, number_of_tracks + 1):
            print(current_timeline.GetItemListInTrack(track_type, 1))


            
            item_list = current_timeline.GetItemListInTrack(track_type, i)
            for il in item_list:
                if il not in all_timeline_items:
                    all_timeline_items.append(il)
            


        for item in all_timeline_items:
            print("Item Color:  ", item.GetClipColor())
            item_color = item.GetClipColor()
            if item.GetClipColor() != "Chocolate":

                if replace_one_clip(item.GetMediaPoolItem()):
                    item.SetClipColor(item_color)
    create_update_window()


# Create the main window
window = tk.Tk()
window.title("Davinci Update Script")

# Create "Update All" button
btn_update_all = tk.Button(window, text="Update All", command=update_all)
btn_update_all.pack(pady=10)

# Create "Update Folder" button
btn_update_folder = tk.Button(window, text="Update Folder", command=update_folder)
btn_update_folder.pack(pady=10)

# Create "Update Timeline" button
btn_update_folder = tk.Button(window, text="Update Timeline", command=update_timeline)
btn_update_folder.pack(pady=10)
window.attributes('-topmost', WINDOW_ALWAYS_ON_TOP)
window.geometry("200x150")

# Run the main loop
window.mainloop()
