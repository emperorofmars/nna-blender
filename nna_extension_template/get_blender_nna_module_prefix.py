import bpy

nna_blender_module_prefix = None

if("nna_blender" in bpy.context.preferences.addons.keys()):
	nna_blender_module_prefix = "nna_blender.nna"
elif("bl_ext.vscode_development.nna_blender" in bpy.context.preferences.addons.keys()):
	nna_blender_module_prefix = "bl_ext.vscode_development.nna_blender.nna"


if(nna_blender_module_prefix):
	print("Loading NNA Template Extension")
else:
	print("Could Not Load NNA Template Extension")
