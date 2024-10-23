

import nuke
import nukescripts

def setup_4k_uhd_project():
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
