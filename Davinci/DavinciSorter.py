#!/usr/bin/env python

def get_resolve():
    """Get the current DaVinci Resolve instance."""
    try:
        # The actual path may vary depending on your OS and Resolve version
        import sys
        import os
        
        # Try to find and import the module
        script_module_path = os.path.normpath('C:/Program Files/Blackmagic Design/DaVinci Resolve/Support/Developer/Scripting')
        if script_module_path not in sys.path:
            sys.path.append(script_module_path)
            
        import DaVinciResolveScript as dvr
        resolve = dvr.scriptapp("Resolve")
        return resolve
    except Exception as e:
        print(f"Error: Could not initialize Resolve: {str(e)}")
        return None

def organize_media_pool():
    """Main function to organize the Media Pool."""
    resolve = get_resolve()
    if not resolve:
        print("Could not connect to DaVinci Resolve.")
        return

    # Get current project
    project_manager = resolve.GetProjectManager()
    current_project = project_manager.GetCurrentProject()
    if not current_project:
        print("No project is currently open.")
        return

    # Get Media Pool
    media_pool = current_project.GetMediaPool()
    if not media_pool:
        print("Could not access Media Pool.")
        return

    root_folder = media_pool.GetRootFolder()
    if not root_folder:
        print("Could not access root folder.")
        return

    # Create organization bins if they don't exist
    bin_categories = {
        "VIDEO": [".mp4", ".mov", ".mxf", ".avi", ".mkv", ".r3d", ".braw", ".arri"],
        "AUDIO": [".wav", ".mp3", ".aac", ".m4a", ".aif", ".aiff"],
        "PICTURES": [".jpg", ".jpeg", ".png", ".tif", ".tiff", ".exr", ".dpx"],
        "SHOTS": [],  # Will be populated based on naming patterns
        "OTHER": []
    }

    # Debug: Print available methods
    print("\nAvailable MediaPool methods:")
    for method in dir(media_pool):
        if not method.startswith('__'):
            print(f"- {method}")
    
    print("\nAvailable RootFolder methods:")
    for method in dir(root_folder):
        if not method.startswith('__'):
            print(f"- {method}")

    # Try to create bins using the correct API method
    created_bins = {}
    for bin_name in bin_categories.keys():
        try:
            # Try the most common method first
            new_bin = media_pool.AddSubFolder(root_folder, bin_name)
            
            if new_bin:
                created_bins[bin_name] = new_bin
                print(f"Successfully created/found bin: {bin_name}")
            else:
                print(f"Failed to create bin {bin_name} - returned None")
        except Exception as e:
            print(f"Error creating bin {bin_name}: {str(e)}")

    def get_clip_category(clip):
        """Determine the category for a clip based on its properties."""
        try:
            clip_props = clip.GetClipProperty()
            file_path = clip_props.get("File Path", "").lower()
            clip_name = clip_props.get("Clip Name", "").lower()
            
            # Check if it's a shot based on naming pattern
            if any(pattern in clip_name for pattern in ["shot", "sh_", "sc_", "scene"]):
                return "SHOTS"
                
            # Check file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            for category, extensions in bin_categories.items():
                if file_ext in extensions:
                    return category
                    
            return "OTHER"
        except Exception as e:
            print(f"Error categorizing clip: {str(e)}")
            return "OTHER"

    def process_folder(folder):
        """Process all clips in a folder and its subfolders."""
        try:
            # Get all clips in current folder
            clips = folder.GetClipList()
            if clips:
                for clip in clips:
                    category = get_clip_category(clip)
                    if category in created_bins:
                        try:
                            # Try different methods to move the clip
                            target_bin = created_bins[category]
                            if hasattr(media_pool, "MoveClips"):
                                media_pool.MoveClips([clip], target_bin)
                            elif hasattr(media_pool, "MoveClip"):
                                media_pool.MoveClip(clip, target_bin)
                            print(f"Moved clip {clip.GetName()} to {category}")
                        except Exception as e:
                            print(f"Error moving clip {clip.GetName()}: {str(e)}")

            # Process subfolders
            subfolders = folder.GetSubFolderList()
            if subfolders:
                for subfolder in subfolders:
                    process_folder(subfolder)
        except Exception as e:
            print(f"Error processing folder: {str(e)}")

    # Start processing from root folder
    process_folder(root_folder)
    print("Media Pool organization complete!")

if __name__ == "__main__":
    organize_media_pool()
