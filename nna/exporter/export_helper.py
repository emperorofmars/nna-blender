import bpy
import bpy_extras

from .. import nna_utils_tree


class NNAExportFBX(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
	"""Export as `nna.fbx` file."""
	bl_idname = "nna.export_nna_fbx"
	bl_label = "Export as `nna.fbx` file"

	filename_ext = ".nna.fbx"

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
				bake_anim=False, # TODO Export animation non-baked once Blender 4.4 is released
				# bake_anim_use_all_bones=False
				use_custom_props=True,
				add_leaf_bones=False, # TODO Make this editable
			)
			self.report({'INFO'}, "NNA asset exported successfully!")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}

