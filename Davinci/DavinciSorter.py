#!/usr/bin/env python
import sys, os, re

def get_resolve():
    """
    Connect to DaVinci Resolve and return the instance.
    Adjust the scripting module path as necessary.
    """
    try:
        script_module_path = os.path.normpath("C:/Program Files/Blackmagic Design/DaVinci Resolve/Support/Developer/Scripting")
        if script_module_path not in sys.path:
            sys.path.append(script_module_path)
        import DaVinciResolveScript as dvr
        resolve = dvr.scriptapp("Resolve")
        return resolve
    except Exception as e:
        print("Error connecting to DaVinci Resolve:", e)
        return None

def get_or_create_subbin(media_pool, parent_folder, subbin_name):
    """
    Check if a subfolder with the given name exists under parent_folder.
    If not, create it using AddSubFolder.
    """
    try:
        subs = parent_folder.GetSubFolders()
        if subs:
            for s in subs.values():
                if s.GetName().lower() == subbin_name.lower():
                    return s
        new_sub = media_pool.AddSubFolder(parent_folder, subbin_name)
        if new_sub:
            print(f"Created sub-bin '{new_sub.GetName()}' under '{parent_folder.GetName()}'")
        else:
            print(f"Failed to create sub-bin '{subbin_name}' under '{parent_folder.GetName()}'")
        return new_sub
    except Exception as e:
        print(f"Error in get_or_create_subbin for '{subbin_name}':", e)
        return None

def get_clip_category(clip):
    """
    Determine the main category for a clip based on its properties.
    Evaluation order:
      1. TIMELINES: if Media Type is "timeline"
      2. OFFLINE: if no file path or name contains "offline"
      3. RAW_MATERIALS: if "raw" appears in name or file path
      4. RENDERS: if file extension is ".exr"
      5. DAILIES: if name starts with "moloch_s" or "ep01_"
      6. ME_SHOTS: if name starts with "mlch_me1_"
      7. NUMERIC_SEQUENCE: if name begins with digits
      8. Check file path markers: "\assets\", "\output\_precomp\", "\sources\"
      9. Otherwise, check file extension:
           - if in VIDEO list → "VIDEO"
           - if in AUDIO list → "AUDIO"
           - if in PICTURES list → "PICTURES"
     10. Else, return "OTHERS".
    """
    try:
        props = clip.GetClipProperty()
        clip_name = props.get("Clip Name", "").strip()
        file_path = props.get("File Path", "").strip()
        clip_name_lower = clip_name.lower()
        file_path_lower = file_path.lower()
        media_type = props.get("Media Type", "").lower()
        
        video_exts = [".mp4", ".mov", ".avi", ".mxf", ".mkv"]
        audio_exts = [".wav", ".mp3", ".aif", ".aiff", ".aac", ".m4a"]
        picture_exts = [".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"]
        
        # 1. Timelines
        if media_type == "timeline":
            return "TIMELINES"
        # 2. Offline
        if not file_path or "offline" in clip_name_lower:
            return "OFFLINE"
        # 3. RAW_MATERIALS: if "raw" appears anywhere
        if "raw" in clip_name_lower or "raw" in file_path_lower:
            return "RAW_MATERIALS"
        # 4. RENDERS: if file extension is .exr
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".exr":
            return "RENDERS"
        # 5. DAILIES: if name starts with "moloch_s" or "ep01_"
        if clip_name_lower.startswith("moloch_s") or clip_name_lower.startswith("ep01_"):
            return "DAILIES"
        # 6. ME_SHOTS: if name starts with "mlch_me1_"
        if clip_name_lower.startswith("mlch_me1_"):
            return "ME_SHOTS"
        # 7. NUMERIC_SEQUENCE: if name begins with digits
        if re.match(r'^\d+', clip_name):
            return "NUMERIC_SEQUENCE"
        # 8. File path markers
        if "\\assets\\" in file_path_lower:
            return "ASSETS"
        if "\\output\\_precomp\\" in file_path_lower:
            return "PRECOMP"
        if "\\sources\\" in file_path_lower:
            return "SOURCES"
        # 9. Otherwise, check the file extension for file-based media
        if ext in video_exts:
            return "VIDEO"
        if ext in audio_exts:
            return "AUDIO"
        if ext in picture_exts:
            return "PICTURES"
        # 10. Fallback
        return "OTHERS"
    except Exception as e:
        print(f"Error categorizing clip '{clip.GetName()}':", e)
        return "OTHERS"

def move_clip(clip, media_pool, main_bins, subfolder_categories):
    """
    Determine the main category for the clip and move it.
    For file-based categories, create a sub-bin based on the file extension.
    """
    main_cat = get_clip_category(clip)
    target_bin = main_bins.get(main_cat)
    
    if main_cat in subfolder_categories:
        props = clip.GetClipProperty()
        file_path = props.get("File Path", "")
        ext = os.path.splitext(file_path)[1].lower().strip(".")
        if not ext:
            ext = "UNKNOWN"
        sub_bin = get_or_create_subbin(media_pool, target_bin, ext.upper())
        if sub_bin:
            target_bin = sub_bin
    try:
        if hasattr(media_pool, "MoveClips"):
            media_pool.MoveClips([clip], target_bin)
        elif hasattr(media_pool, "MoveClip"):
            media_pool.MoveClip(clip, target_bin)
        print(f"Moved clip '{clip.GetName()}' to bin '{target_bin.GetName()}'")
    except Exception as e:
        print(f"Error moving clip '{clip.GetName()}': {e}")

def traverse_and_move(folder, media_pool, main_bins, subfolder_categories, container_name):
    """
    Recursively traverse folders (skipping the container bin) and move all clips.
    """
    if folder.GetName() == container_name:
        return
    clips = folder.GetClipList()
    if clips:
        for clip in clips:
            move_clip(clip, media_pool, main_bins, subfolder_categories)
    subfolders = folder.GetSubFolderList()
    if subfolders:
        for sub in subfolders:
            traverse_and_move(sub, media_pool, main_bins, subfolder_categories, container_name)

def organize_media_pool_complex():
    """
    Organize the Media Pool into a complex hierarchy.
    A container bin "ORGANIZED_CLIPS" is created under the root.
    Under that, main bins for various categories are created.
    For VIDEO, AUDIO, PICTURES, and RENDERS, sub-bins are created based on file extension.
    """
    resolve = get_resolve()
    if not resolve:
        return
    project_manager = resolve.GetProjectManager()
    current_project = project_manager.GetCurrentProject()
    if not current_project:
        print("No project is open.")
        return
    media_pool = current_project.GetMediaPool()
    if not media_pool:
        print("Could not access the Media Pool.")
        return
    root_folder = media_pool.GetRootFolder()
    if not root_folder:
        print("Could not access the root folder.")
        return

    container_name = "ORGANIZED_CLIPS"
    organized_container = get_or_create_subbin(media_pool, root_folder, container_name)
    if not organized_container:
        print("Failed to create container bin.")
        return

    # Define main categories. Note that VIDEO, AUDIO, and PICTURES are now separate.
    main_categories = [
        "TIMELINES", "RAW_MATERIALS", "RENDERS", "DAILIES",
        "ME_SHOTS", "NUMERIC_SEQUENCE", "VIDEO", "AUDIO", "PICTURES",
        "ASSETS", "PRECOMP", "SOURCES", "OFFLINE", "OTHERS"
    ]
    # Categories that should get subfolders by file extension.
    subfolder_categories = ["VIDEO", "AUDIO", "PICTURES", "RENDERS"]

    main_bins = {}
    for cat in main_categories:
        bin_obj = get_or_create_subbin(media_pool, organized_container, cat)
        if bin_obj:
            main_bins[cat] = bin_obj
            print(f"Created main bin: {cat}")
        else:
            print(f"Failed to create main bin: {cat}")

    # Traverse the entire Media Pool starting from the root folder (except our container)
    traverse_and_move(root_folder, media_pool, main_bins, subfolder_categories, container_name)
    print("Complex Media Pool organization complete!")

if __name__ == "__main__":
    organize_media_pool_complex()
