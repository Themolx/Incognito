import nuke
def create_grade_node(name, inputs):
    grade = nuke.nodes.Grade(name=name, inputs=inputs)
    grade['white'].setValue([2.5, 1, 1, 1])
    grade['white_panelDropped'].setValue(True)
    return grade

def mask_channel_splitter_with_grade_series():
    try:
        node = nuke.selectedNode()
    except ValueError:
        nuke.message("Error: No node selected. Please select a node with matte channels and run the script again.")
        return
    
    all_channels = node.channels()
    
    # Look specifically for .alpha channels in matte layers, or fall back to .a if needed
    matte_alpha_channels = []
    for channel in all_channels:
        if 'matte' in channel and channel.endswith('.alpha'):
            matte_alpha_channels.append(channel)
    
    # If no .alpha channels were found, look for .a channels as fallback
    if not matte_alpha_channels:
        matte_alpha_channels = [chan for chan in all_channels if 'matte' in chan and chan.endswith('.a')]
    
    if not matte_alpha_channels:
        nuke.message("No matte alpha channels found in the selected node.")
        return
    
    offset_y = 350
    offset_x = 34
    dot_nodes = []
    shuffle_nodes = []
    grade_nodes = []
    previous_node = node
    all_created_nodes = []
    
    for channel in matte_alpha_channels:
        # Get channel name without layer
        channel_name = channel.split('.')[-1]
        layer_name = channel.split('.')[0]
        
        dot_node = nuke.nodes.Dot()
        dot_nodes.append(dot_node)
        all_created_nodes.append(dot_node)
        
        shuffle_node = nuke.nodes.Shuffle(
            name=f"{layer_name}_{channel_name}",
            inputs=[dot_node],
            postage_stamp=True,
            hide_input=False
        )
        shuffle_node['in'].setValue(channel)
        shuffle_node['out'].setValue('alpha')
        shuffle_nodes.append(shuffle_node)
        all_created_nodes.append(shuffle_node)
        
        grade_node = create_grade_node(
            name=f"Grade_{layer_name}_{channel_name}",
            inputs=[previous_node, shuffle_node]
        )
        grade_nodes.append(grade_node)
        all_created_nodes.append(grade_node)
        
        xpos = node.xpos() + offset_x
        ypos = node.ypos() + offset_y
        dot_node.setXYpos(xpos, ypos)
        shuffle_node.setXYpos(xpos - 34, dot_node.ypos() + 50)
        grade_node.setXYpos(xpos - 34, shuffle_node.ypos() + 100)
        
        previous_node = grade_node
        offset_x += 200
    
    for i, dot in enumerate(dot_nodes):
        if i == 0:
            dot.setInput(0, node)
        else:
            dot.setInput(0, dot_nodes[i - 1])
    
    if grade_nodes:
        output_stamp = nuke.nodes.PostageStamp(name="Output", label="Output", postage_stamp=True)
        output_stamp.setInput(0, grade_nodes[-1])
        output_stamp_xpos = grade_nodes[-1].xpos() + grade_nodes[-1].screenWidth()/2 - output_stamp.screenWidth()/2
        output_stamp_ypos = grade_nodes[-1].ypos() + grade_nodes[-1].screenHeight() + 100
        output_stamp.setXYpos(int(output_stamp_xpos), int(output_stamp_ypos))
        output_stamp['note_font_size'].setValue(20)
        all_created_nodes.append(output_stamp)
    
    if all_created_nodes:
        bdX = min(node.xpos() for node in all_created_nodes) - 50
        bdY = min(node.ypos() for node in all_created_nodes) - 120
        bdW = max(node.xpos() + node.screenWidth() for node in all_created_nodes) - bdX + 100
        bdH = max(node.ypos() + node.screenHeight() for node in all_created_nodes) - bdY + 50
        backdrop = nuke.nodes.BackdropNode(
            xpos=bdX,
            bdwidth=bdW,
            ypos=bdY,
            bdheight=bdH,
            tile_color=0x7171C600,
            label='<center>MatteAlphaChecker'
        )
        backdrop['note_font_size'].setValue(42)
        backdrop['note_font'].setValue('Verdana')
    
    nuke.message(f"Created {len(matte_alpha_channels)} MatteAlphaChecker nodes!")

if __name__ == "__main__":
    mask_channel_splitter_with_grade_series()
