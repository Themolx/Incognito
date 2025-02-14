import nuke

def mask_channel_splitter_with_individual_premults_and_hero_dot():
    try:
        node = nuke.selectedNode()
    except ValueError:
        nuke.message("Error: No node selected. Please select a node with matte channels and run the script again.")
        return

    # Get all channels from the node and determine unique matte layers (exclude 'rgb' & 'rgba')
    all_channels = node.channels()
    matte_layers = set()
    for chan in all_channels:
        parts = chan.split('.')
        if len(parts) == 2:
            layer, channel = parts
            if layer.lower() in ['rgb', 'rgba']:
                continue
            matte_layers.add(layer)
    matte_layers = list(matte_layers)
    if not matte_layers:
        nuke.message("No matte channels found in the selected node.")
        return

    offset_y = 250
    offset_x = 0
    all_created_nodes = []

    # Create a hero dot representing the Beauty (RGB) pass
    hero_dot = nuke.nodes.Dot(inputs=[node])
    hero_dot.setXYpos(node.xpos() + 34, node.ypos() + 200)
    hero_dot['label'].setValue("Beauty")
    hero_dot['note_font_size'].setValue(20)
    all_created_nodes.append(hero_dot)

    # For each matte layer, create a shuffle that extracts its red channel and a corresponding premult node
    for layer in matte_layers:
        # Create a shuffle node that extracts the red channel from the matte layer
        shuffle_node = nuke.nodes.Shuffle(
            name=f"{layer}_mask",
            inputs=[hero_dot],
            postage_stamp=True,
            hide_input=False
        )
        # Use the red channel from the matte layer (e.g. "matte.red")
        shuffle_node['in'].setValue(f"{layer}.red")
        shuffle_node['out'].setValue('alpha')
        all_created_nodes.append(shuffle_node)

        # Create a premult node that uses the shuffled mask to premultiply the Beauty
        premult_node = nuke.nodes.Premult(
            name=f"Premult_{layer}",
            inputs=[shuffle_node, hero_dot]
        )
        all_created_nodes.append(premult_node)

        # Position the nodes relative to the hero dot
        xpos = hero_dot.xpos() + offset_x
        ypos = hero_dot.ypos() + offset_y
        shuffle_node.setXYpos(xpos, ypos)
        premult_node.setXYpos(xpos, ypos + 100)

        offset_x += 200

    # Wrap all created nodes in a backdrop for organization
    if all_created_nodes:
        bdX = min(n.xpos() for n in all_created_nodes) - 50
        bdY = min(n.ypos() for n in all_created_nodes) - 50
        bdW = max(n.xpos() + n.screenWidth() for n in all_created_nodes) - bdX + 100
        bdH = max(n.ypos() + n.screenHeight() for n in all_created_nodes) - bdY + 100

        backdrop = nuke.nodes.BackdropNode(
            xpos=bdX,
            bdwidth=bdW,
            ypos=bdY,
            bdheight=bdH,
            tile_color=0x7171C600,
            label='<center>MaskChecker'
        )
        backdrop['note_font_size'].setValue(42)
        backdrop['note_font'].setValue('Verdana')

    nuke.message(f"Created a hero Dot for beauty and {len(matte_layers)} individual Shuffle and Premult nodes (using the red channel from each matte layer), wrapped in a MaskChecker backdrop.")

if __name__ == "__main__":
    mask_channel_splitter_with_individual_premults_and_hero_dot()
