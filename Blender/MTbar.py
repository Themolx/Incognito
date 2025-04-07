bl_info = {
    "name": "Custom Scripts Panel",
    "author": "Cascade",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Custom Scripts",
    "description": "Panel with buttons for running internal scripts",
    "category": "Interface",
}

import bpy
import os
from bpy.props import StringProperty

# Hardcoded path to scripts folder
SCRIPTS_FOLDER = r"P:\2D_TESTY_0000\BlenderScripts"

# Panel to display script buttons
class CUSTOM_PT_ScriptsPanel(bpy.types.Panel):
    bl_label = "Custom Scripts"
    bl_idname = "CUSTOM_PT_scripts_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Custom Scripts'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Display info about the scripts folder
        layout.label(text=f"Scripts Folder: {SCRIPTS_FOLDER}")
        layout.operator("custom.refresh_scripts")
        
        # Display script buttons
        if hasattr(context.scene, "custom_script_items"):
            for script in context.scene.custom_script_items:
                row = layout.row()
                op = row.operator("custom.run_script", text=script.name)
                op.script_path = script.path

# Operator to refresh the script list
class CUSTOM_OT_RefreshScripts(bpy.types.Operator):
    bl_idname = "custom.refresh_scripts"
    bl_label = "Refresh Scripts"
    
    def execute(self, context):
        scan_scripts_folder(context)
        return {'FINISHED'}

# Operator to run a script
class CUSTOM_OT_RunScript(bpy.types.Operator):
    bl_idname = "custom.run_script"
    bl_label = "Run Script"
    script_path: StringProperty()
    
    def execute(self, context):
        try:
            with open(self.script_path, 'r') as file:
                script_text = file.read()
                exec(compile(script_text, self.script_path, 'exec'))
            self.report({'INFO'}, f"Script executed: {os.path.basename(self.script_path)}")
        except Exception as e:
            self.report({'ERROR'}, f"Error executing script: {str(e)}")
        
        return {'FINISHED'}

# Script item for the collection
class CustomScriptItem(bpy.types.PropertyGroup):
    name: StringProperty()
    path: StringProperty()

# Function to scan the scripts folder
def scan_scripts_folder(context=None):
    path = SCRIPTS_FOLDER
    
    if context is None or not hasattr(context, "scene") or not hasattr(context.scene, "custom_script_items"):
        return
    
    # Clear existing items
    context.scene.custom_script_items.clear()
    
    if os.path.exists(path) and os.path.isdir(path):
        for filename in os.listdir(path):
            if filename.endswith('.py'):
                script_path = os.path.join(path, filename)
                item = context.scene.custom_script_items.add()
                item.name = os.path.splitext(filename)[0]
                item.path = script_path
    else:
        print(f"Path does not exist or is not a directory: {path}")

# Handler to run after scene is updated
def on_scene_update(scene):
    if hasattr(scene, "custom_script_items") and len(scene.custom_script_items) == 0:
        scan_scripts_folder(bpy.context)

# Register
def register():
    bpy.utils.register_class(CustomScriptItem)
    bpy.utils.register_class(CUSTOM_PT_ScriptsPanel)
    bpy.utils.register_class(CUSTOM_OT_RefreshScripts)
    bpy.utils.register_class(CUSTOM_OT_RunScript)
    
    bpy.types.Scene.custom_script_items = bpy.props.CollectionProperty(type=CustomScriptItem)
    
    # Instead of calling scan_scripts_folder directly, use a handler
    bpy.app.handlers.depsgraph_update_post.append(on_scene_update)

# Unregister
def unregister():
    # Remove the handler
    if on_scene_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_scene_update)
    
    del bpy.types.Scene.custom_script_items
    
    bpy.utils.unregister_class(CUSTOM_OT_RunScript)
    bpy.utils.unregister_class(CUSTOM_OT_RefreshScripts)
    bpy.utils.unregister_class(CUSTOM_PT_ScriptsPanel)
    bpy.utils.unregister_class(CustomScriptItem)

if __name__ == "__main__":
    register()
