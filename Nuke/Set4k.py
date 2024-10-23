import nuke
import nukescripts
import os

def get_project_name_from_path():
    script_path = nuke.root().name()
    
    if not script_path:
        print("No script is currently loaded.")
        return None
        
    # Split the path into components
    path_parts = script_path.split('/')
    # Convert backslashes to forward slashes if needed
    if len(path_parts) <= 1:
        path_parts = script_path.split('\\')
    
    # Find the project folder (should be right after the drive letter)
    for part in path_parts:
        if part == "3PRINCEZNY_02421":
            return part
            
    # Alternative method: get the second element after splitting by disk letter
    try:
        without_drive = script_path.split(':', 1)[1]
        cleaned_path = without_drive.strip('/\\')
        first_folder = cleaned_path.split('/')[0].split('\\')[0]
        
        if first_folder == "3PRINCEZNY_02421":
            return first_folder
    except:
        pass
        
    print("This script is not part of the 3PRINCEZNY_02421 project.")
    return None

def setup_4k_uhd_project():
    # First check if this is the correct project
    project_name = get_project_name_from_path()
    if project_name != "3PRINCEZNY_02421":
        print("Resolution setup skipped - not in 3PRINCEZNY_02421 project")
        return
        
    print(f"Setting up 4K UHD format for {project_name}")
    
    root = nuke.root()
    format_knob = root['format']
    
    # UHD 4K specifications
    desired_width = 3840
    desired_height = 2160
    desired_pixel_aspect = 1.0
    desired_name = "3PRINCEZNY_02421"
    
    # Check if format already exists
    existing_format = None
    for format in nuke.formats():
        if (format.width() == desired_width and
            format.height() == desired_height and
            format.pixelAspect() == desired_pixel_aspect and
            format.name() == desired_name):
            existing_format = format
            break
    
    if existing_format:
        print(f"UHD 4K format already exists. Setting project to use it.")
        format_knob.setValue(desired_name)
    else:
        print(f"UHD 4K format not found. Creating and setting it.")
        try:
            new_format = f"{desired_width} {desired_height} {desired_pixel_aspect} {desired_name}"
            nuke.addFormat(new_format)
            format_knob.setValue(desired_name)
        except RuntimeError as e:
            print(f"Error creating new format: {e}")
            print("Attempting to set format using existing method...")
            format_knob.fromScript(f"{desired_width} {desired_height} {desired_pixel_aspect}")
    
    # Print current format info for verification
    current_format = format_knob.value()
    print(f"\nProject Format:")
    print(f"Name: {current_format.name()}")
    print(f"Resolution: {current_format.width()}x{current_format.height()}")
    print(f"Pixel Aspect Ratio: {current_format.pixelAspect()}")

if __name__ == "__main__":
    setup_4k_uhd_project()
