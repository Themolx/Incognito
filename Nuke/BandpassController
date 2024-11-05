import nuke

def link_bandpass_to_grade():
    # Get selected node
    selected = nuke.selectedNode()
    
    # Check if selected node is PxF_Bandpass
    if selected.Class() != "Group" or "PxF_Bandpass" not in selected.name():
        nuke.message("Please select a PxF_Bandpass node")
        return
    
    # Create a Grade node
    grade = nuke.createNode("Grade")
    grade.setName("Grade_BandpassControl")
    
    # Position grade node to the right of selected node
    grade.setXYpos(selected.xpos() + 100, selected.ypos())
    
    # Link Bandpass values to get values FROM Grade node
    selected['brightness'].setExpression(f"{grade.name()}.white")
    selected['offset'].setExpression(f"{grade.name()}.add")
    selected['bc'].setExpression(f"{grade.name()}.black_clamp")
    selected['wc'].setExpression(f"{grade.name()}.white_clamp")
    
    # Set initial Grade values to match current Bandpass values
    grade['white'].setValue(selected['brightness'].value())
    grade['add'].setValue(selected['offset'].value())
    grade['black_clamp'].setValue(selected['bc'].value())
    grade['white_clamp'].setValue(selected['wc'].value())
    
    # Select the new grade node
    grade.setSelected(True)
    selected.setSelected(False)

# Create menu item
nuke.menu('Nuke').addCommand('Custom/Create Control Grade', link_bandpass_to_grade)
