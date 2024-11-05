import bpy
import json

from .. import nna_name_utils
from .. import nna_json_utils
from .. import nna_tree_utils


class AddNNAHumanoidComponentOperator(bpy.types.Operator):
	bl_idname = "nna.add_nna_humanoid"
	bl_label = "Add Twist Component"
	bl_options = {"REGISTER", "UNDO"}
	
	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	
	def execute(self, context):
		try:
			nna_json_utils.add_component(self.target_id, json.dumps({"t":"nna.humanoid"}))
			self.report({'INFO'}, "Component successfully added")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}


def display_nna_humanoid_component(object, layout, json_dict):
	row = layout.row()
	row.label(text="Locomotion")
	row.label(text=str(json_dict["lc"]) if "lc" in json_dict else "default (planti)")
	row = layout.row()
	row.label(text="No Jaw Mapping")
	row.label(text=json_dict["nj"] if "nj" in json_dict else "default (False)")


nna_types = {
	"nna.humanoid": {
		"json_add": AddNNAHumanoidComponentOperator.bl_idname,
		"json_display": display_nna_humanoid_component,
	},
}
