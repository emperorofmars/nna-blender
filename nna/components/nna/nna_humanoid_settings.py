import re
import bpy

from ...nna_registry import NNAFunctionType

from ... import nna_utils_json
from ... import nna_utils_name
from ... import nna_utils_tree


_nna_name = "nna.humanoid.settings"


class AddNNAHumanoidSettingsComponentOperator(bpy.types.Operator):
	"""Specifies humanoid rig settings."""
	bl_idname = "nna.add_humanoid_settings"
	bl_label = "Add Humanoid Settings Component"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore

	def execute(self, context):
		try:
			nna_utils_json.add_component(self.target_id, {"t":_nna_name})
			self.report({'INFO'}, "Component successfully added")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}

nna_types = {
	_nna_name: {
		NNAFunctionType.JsonAdd: AddNNAHumanoidSettingsComponentOperator.bl_idname,
		#NNAFunctionType.JsonEdit: EditNNATwistComponentOperator.bl_idname,
		#NNAFunctionType.JsonDisplay: display_nna_twist_component,
	},
}
