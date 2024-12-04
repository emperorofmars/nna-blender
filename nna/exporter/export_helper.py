# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
import bpy
import bpy_extras
import os

from .. import nna_utils_tree
from .. import nna_utils_json


class NNAExportFBX(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
	"""Export as `nna.fbx` file."""
	bl_idname = "nna.export_nna_fbx"
	bl_label = "Export as `nna.fbx` file"

	filename_ext = ".nna.fbx"

	def invoke(self, context, _event):
		# Determine export file name
		export_name = ""
		if(not self.filepath):
			meta = nna_utils_tree.determine_nna_meta()
			if(meta):
				json_text = nna_utils_json.get_json_from_targeting_object(meta)
				json_meta = json.loads(json_text) if json_text else {}
				if("name" in json_meta):
					export_name = json_meta["name"]
			if(not export_name):
				export_name = context.blend_data.filepath
				if(not export_name):
					export_name = "superawesomemodel"
				else:
					export_name = os.path.splitext(export_name)[0]
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

