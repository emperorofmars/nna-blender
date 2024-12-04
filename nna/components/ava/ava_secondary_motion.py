# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import bpy

from ...nna_registry import NNAFunctionType

from ... import nna_utils_name
from ... import nna_utils_json
from ... import nna_utils_tree

_nna_name = "ava.secondary_motion"


class AddAVASecondaryMotionComponentOperator(bpy.types.Operator):
	"""Create simple bone physics definition"""
	bl_idname = "nna.add_ava_secondary_motion"
	bl_label = "Create simple bone physics definition"
	bl_options = {"REGISTER", "UNDO"}
	
	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	
	def execute(self, context):
		try:
			nna_utils_json.add_component(self.target_id, {
				"t": _nna_name,
				"intensity": 0.3,
			})
			self.report({'INFO'}, "Component successfully added")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}


class EditAVASecondaryMotionComponentOperator(bpy.types.Operator):
	"""Edit simple bone physics definition"""
	bl_idname = "nna.edit_ava_secondary_motion"
	bl_label = "Edit simple bone physics definition"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	component_index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore

	intensity: bpy.props.FloatProperty(name="Intensity", default=0.3, min=0, max=1, precision=2, step=2) # type: ignore
	
	def invoke(self, context, event):
		json_component = nna_utils_json.get_component(self.target_id, self.component_index)
		self.intensity = json_component.get("intensity", 0.3)
		return context.window_manager.invoke_props_dialog(self)
	
	def execute(self, context):
		try:
			json_component = nna_utils_json.get_component(self.target_id, self.component_index)

			json_component["intensity"] = round(self.intensity, 2)

			nna_utils_json.replace_component(self.target_id, json_component, self.component_index)
			self.report({'INFO'}, "Component successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.prop(self, "intensity", expand=True)


def display_ava_secondary_motion_component(otarget_id: str, layout: bpy.types.UILayout, json_component: dict, component_index: int):
	row = layout.split(factor=0.4); row.label(text="Intensity"); row.label(text=str(json_component.get("intensity", "default (0.3)")))



nna_types = {
	_nna_name: {
		NNAFunctionType.JsonAdd: AddAVASecondaryMotionComponentOperator.bl_idname,
		NNAFunctionType.JsonEdit: EditAVASecondaryMotionComponentOperator.bl_idname,
		NNAFunctionType.JsonDisplay: display_ava_secondary_motion_component,
	},
}
