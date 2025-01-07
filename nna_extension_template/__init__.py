# Custom NNA TYPE Template

import bpy

def register():
	if("bl_ext.user_default.nna_blender" in bpy.context.preferences.addons.keys()):
		from .nna_extension_template import register
		register()

def unregister():
	if("bl_ext.user_default.nna_blender" in bpy.context.preferences.addons.keys()):
		from .nna_extension_template import unregister
		unregister()
