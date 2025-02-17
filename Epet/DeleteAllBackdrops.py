import nuke

# Define the function that deletes all BackdropNodes.
def delete_all_backdrops():
    for node in nuke.allNodes("BackdropNode"):
        nuke.delete(node)

# Create a NoOp node (set inpanel=False so it doesn't show the default knob panel)
node = nuke.createNode("NoOp", inpanel=False)
node.setName("DeleteBackdropsNode")  # Optionally, give the node a custom name

# Add a Python button knob that calls the delete_all_backdrops function when pressed.
py_button = nuke.PyScript_Knob("deleteButton", "Delete All Backdrops", "delete_all_backdrops()")
node.addKnob(py_button)
