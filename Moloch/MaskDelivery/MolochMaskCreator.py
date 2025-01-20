set cut_paste_input [stack 0]
version 14.0 v5
push $cut_paste_input
Group {
 name MolochMaskCreator
 tile_color 0x272727ff
 note_font "Bitstream Vera Sans Bold"
 note_font_color 0xffffffff
 selected true
 xpos 2040
 ypos 132
 addUserKnob {20 Settings l "Moloch Mask Creator"}
 addUserKnob {22 copy_to_monitor l "Copy Alpha to Monitor Mask" t "Copies input alpha to monitor.mask channel. Creates the channel if it doesn't exist." T "def copyToMonitorMask():\n    n = nuke.thisNode()\n\n    if not n.input(1):\n        nuke.message('Please connect a matte input!')\n        return\n\n    # Create monitor.mask if needed\n    channelName = 'monitor'\n    fullChannelName = 'monitor.mask'\n    if not nuke.exists(fullChannelName):\n        nuke.Layer(channelName, \[fullChannelName])\n\n    # Get internal copy node\n    with n:\n        copy = nuke.toNode('Copy1')\n        if copy:\n            copy\['from0'].setValue('rgba.alpha')\n            copy\['to0'].setValue(fullChannelName)\n\n    # Update appearance\n    if n\['tile_color'].value() == 0x272727ff:\n        n\['tile_color'].setValue(0x46C7C7ff)\n    else:\n        n\['tile_color'].setValue(0x272727ff)\n\ncopyToMonitorMask()" +STARTLINE}
}
 Input {
  inputs 0
  name Matte
  label Matte
  xpos -129
  ypos 86
  number 1
 }
 Input {
  inputs 0
  name Input
  xpos 0
  ypos 0
 }
 Copy {
  inputs 2
  from0 rgba.alpha
  to0 rgba.alpha
  name Copy1
  xpos 0
  ypos 86
 }
 Output {
  name Output1
  xpos 0
  ypos 196
 }
end_group
