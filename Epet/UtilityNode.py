import nuke

# Function to delete all BackdropNodes
def delete_all_backdrops():
    for node in nuke.allNodes("BackdropNode"):
        nuke.delete(node)

# Function to force update all Cryptomatte nodes by calling "forceUpdate"
def force_update_all_cryptomattes():
    for node in nuke.allNodes("Cryptomatte"):
        # Check if the node has the 'forceUpdate' knob
        if 'forceUpdate' in node.knobs():
            # Execute the forceUpdate knob
            node.knob("forceUpdate").execute()
        else:
            nuke.tprint("Node {} does not have a 'forceUpdate' knob.".format(node.name()))

# Create a NoOp node (without opening the properties panel) and rename it
utility_node = nuke.createNode("NoOp", inpanel=False)
utility_node.setName("UtilityNode")

# Add a button to delete all backdrops
delete_button = nuke.PyScript_Knob("deleteButton", "Delete All Backdrops", "delete_all_backdrops()")
utility_node.addKnob(delete_button)

# Add a button to force update all Cryptomatte nodes
force_update_button = nuke.PyScript_Knob("forceUpdateButton", "Force Update All Cryptomattes", "force_update_all_cryptomattes()")
utility_node.addKnob(force_update_button)
