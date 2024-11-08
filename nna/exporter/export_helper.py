import bpy
import bpy_extras
import os

from .. import nna_utils_tree


class NNAExportFBX(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
	"""Export as `nna.fbx` file."""
	bl_idname = "nna.export_nna_fbx"
	bl_label = "Export as `nna.fbx` file"

	filename_ext = ".nna.fbx"

	def invoke(self, context, _event):
		# Determine export file name
		export_name = ""
		nna_collection = nna_utils_tree.find_nna_root_collection()
		if(nna_collection != bpy.context.scene.collection):
			export_name = nna_collection.name
		# TODO also check $meta definition
		else:
			blend_filepath = context.blend_data.filepath
			if not blend_filepath:
				blend_filepath = nna_utils_tree.find_nna_root_collection().name
			else:
				blend_filepath = os.path.splitext(blend_filepath)[0]
		
		self.filepath = export_name

		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

	def execute(self, context):
		try:
			bpy.ops.export_scene.fbx(
				filepath=self.filepath,
				collection=nna_utils_tree.find_nna_root_collection().name,
				apply_scale_options="FBX_SCALE_ALL",
				embed_textures=True,
				path_mode="COPY",
				use_mesh_modifiers=False, # TODO Make this editable maybe
				use_visible=True, # TODO Make this editable
				# colors_type="NONE" # TODO Make this editable
				# use_subsurf=False, # TODO Make this editable
				# use_triangles=False # TODO Make this editable
				bake_anim=False, # TODO Export animations non-baked once Blender 4.4 is released
				# bake_anim_use_all_bones=False
				use_custom_props=True,
				add_leaf_bones=False, # TODO Make this editable
			)
			self.report({'INFO'}, "NNA asset exported successfully!")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}

