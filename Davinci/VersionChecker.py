import os
import re
import DaVinciResolveScript as dvr_script

# ===== User Configuration Variables =====
TRACK_TO_CHECK = 9                # Default video track to check
FILE_PROPERTY_NAME = "File Path"  # The media property used to obtain the file path
VERSION_FOLDER_REGEX = r'\\(v\d{3})\\'  # Regex pattern to match a version folder (e.g., "v013")
# ===== End User Configuration Variables =====

# Get the Resolve instance
resolve = dvr_script.scriptapp("Resolve")
project_manager = resolve.GetProjectManager()
project = project_manager.GetCurrentProject()
timeline = project.GetCurrentTimeline()

# Verify that the specified video track exists
video_track_count = timeline.GetTrackCount("video")
if video_track_count < TRACK_TO_CHECK:
    print(f"Track {TRACK_TO_CHECK} does not exist. There are only {video_track_count} video tracks.")
    exit()

# Retrieve all timeline items on the specified track
items = timeline.GetItemListInTrack("video", TRACK_TO_CHECK)
if not items or len(items) == 0:
    print(f"No clips found on video track {TRACK_TO_CHECK}.")
    exit()

# Process each clip in the track
for clip_index, timeline_item in enumerate(items, start=1):
    clip_name = timeline_item.GetName()
    media_pool_item = timeline_item.GetMediaPoolItem()
    file_path = media_pool_item.GetClipProperty(FILE_PROPERTY_NAME)
    
    print(f"\nClip {clip_index} '{clip_name}':")
    if not file_path:
        print("  File path not found.")
        continue
    print("  File path: " + file_path)
    
    # Extract the version folder using the specified regex
    version_match = re.search(VERSION_FOLDER_REGEX, file_path, re.IGNORECASE)
    if not version_match:
        print("  No version folder found in path.")
        continue
    
    current_version_str = version_match.group(1)  # e.g., "v013"
    try:
        current_version = int(current_version_str[1:])  # Convert "013" to integer 13
    except ValueError:
        print("  Could not parse the current version.")
        continue
    print("  Current version: " + current_version_str)
    
    # Determine the parent directory that holds the version folders
    version_folder = os.path.dirname(file_path)  # This should be the version folder (e.g., ...\v013)
    parent_dir = os.path.dirname(version_folder)   # Parent folder (e.g., ...\renderCompositingMain)
    
    # List all subdirectories in the parent directory
    try:
        subdirs = os.listdir(parent_dir)
    except Exception as e:
        print("  Error listing directory: " + str(e))
        continue

    # Look for folders that match the version pattern (e.g., "v012", "v013", "v014", etc.)
    version_numbers = []
    for subdir in subdirs:
        match = re.match(r'v(\d{3})$', subdir, re.IGNORECASE)
        if match:
            try:
                ver_num = int(match.group(1))
                version_numbers.append(ver_num)
            except ValueError:
                continue

    if not version_numbers:
        print("  No version folders found in parent directory.")
        continue

    max_version = max(version_numbers)
    if max_version > current_version:
        print("  Newer version available: v{:03d}".format(max_version))
    else:
        print("  No newer version found.")
