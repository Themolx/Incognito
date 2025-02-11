#!/usr/bin/env python3
import sys
import xml.etree.ElementTree as ET

def remove_render_color_main(xstage_filename, output_filename):
    """
    Load the xstage file, remove the WRITE module with name "renderColorMain"
    and remove any <link> element that has an attribute (in or out) equal to "renderColorMain".
    Write the modified XML to the output_filename.
    """
    try:
        tree = ET.parse(xstage_filename)
    except Exception as e:
        print(f"Error parsing file {xstage_filename}: {e}")
        sys.exit(1)
        
    root = tree.getroot()

    # --- Remove the WRITE module node named "renderColorMain" ---
    # This example assumes that the module nodes are found under a <nodeslist> element.
    # (The actual structure may vary, so adjust the XPath accordingly.)
    for nodelist in root.findall('.//nodeslist'):
        modules_to_remove = []
        for module in nodelist.findall('module'):
            module_name = module.get('name')
            module_type = module.get('type')
            if module_name == "renderColorMain" and module_type == "WRITE":
                modules_to_remove.append(module)
        for module in modules_to_remove:
            print(f"Removing module: type='{module.get('type')}', name='{module.get('name')}'")
            nodelist.remove(module)

    # --- Remove any <link> element in the linkedlist that references renderColorMain ---
    # Look for any link element whose "in" or "out" attribute equals "renderColorMain"
    for linkedlist in root.findall('.//linkedlist'):
        links_to_remove = []
        for link in linkedlist.findall('link'):
            link_in = link.get('in')
            link_out = link.get('out')
            if link_in == "renderColorMain" or link_out == "renderColorMain":
                links_to_remove.append(link)
        for link in links_to_remove:
            print("Removing link element that references 'renderColorMain'")
            linkedlist.remove(link)

    # Write out the modified XML
    try:
        tree.write(output_filename, encoding="utf-8", xml_declaration=True)
        print(f"Modified file saved to: {output_filename}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python remove_render_color.py <xstage_file> [output_file]")
        sys.exit(1)

    xstage_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "modified.xstage"

    remove_render_color_main(xstage_file, output_file)

if __name__ == "__main__":
    main()
