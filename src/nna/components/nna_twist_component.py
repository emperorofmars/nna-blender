import bpy
import json
from ..nna_registry import *
from ..nna_json_utils import *

class AddNNATwistComponentOperator(bpy.types.Operator):
	bl_idname = "nna.add_nna_twist"
	bl_label = "Add Twist Component"
	bl_options = {"REGISTER", "UNDO"}
		
	def execute(self, context):
		target = context.object.name
		nna_json = get_json_from_targetname(context.object.name)
		try:
			jsonText = add_component_to_nna(nna_json, json.dumps({"t":"nna.twist"}))
			serialize_json_to_targetname(target, jsonText)
			self.report({'INFO'}, "Component successfully added")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}

def display_nna_twist_component(layout, json):
	row = layout.row()
	row.label(text="AAAAAA")

nna_types = {
	"nna.twist": {
		NNAFunctionType.Add: AddNNATwistComponentOperator.bl_idname,
		NNAFunctionType.Display: display_nna_twist_component
	},
}
