import bpy
import json
from ..nna_registry import *
from ..nna_json_utils import *

class AddNNATwistComponentOperator(bpy.types.Operator):
	bl_idname = "nna.add_nna_twist"
	bl_label = "Add Twist Component"
	bl_options = {"REGISTER", "UNDO"}
	
	target: bpy.props.StringProperty(name = "target") # type: ignore
	json: bpy.props.StringProperty(name = "json") # type: ignore

	def invoke(self, context, event):
		self.target = context.object.name
		self.json = get_json_from_targetname(context.object.name)
		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			jsonText = add_component_to_nna(self.json, json.dumps({"t":"nna.twist"}))
			serialize_json_to_targetname(self.target, jsonText)
			self.report({'INFO'}, "Component successfully added")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.label(text="Target Object: " + self.target)
		self.layout.prop(self, "newComponent", text="Values", expand=True)

def preview_nna_twist_component(layout, json):
	row = layout.row()
	row.label(text="AAAAAA")

nna_types = {
	"nna.twist": {
		NNAOperatorType.Add: AddNNATwistComponentOperator.bl_idname,
		NNAOperatorType.Preview: preview_nna_twist_component
	},
}
