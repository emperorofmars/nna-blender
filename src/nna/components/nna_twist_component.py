import bpy
import json
from ..nna_registry import *
from ..nna_json_utils import *

class AddNNATwistComponentOperator(bpy.types.Operator):
	bl_idname = "nna.add_nna_twist"
	bl_label = "Add Json Component"
	bl_options = {"REGISTER", "UNDO"}
	
	target: bpy.props.StringProperty(name = "target") # type: ignore
	json: bpy.props.StringProperty(name = "json") # type: ignore

	def invoke(self, context, event):
		self.target = context.object.name
		self.json = getJsonFromTargetName(context.object.name)
		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			jsonText = addComponentToNNA(self.json, json.dumps({"t":"nna.twist"}))
			serializeJsonToTargetName(self.target, jsonText)
			self.report({'INFO'}, "Component successfully added")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.label(text="Target Object: " + self.target)
		self.layout.prop(self, "newComponent", text="Values", expand=True)

nna_types = {
	"nna.twist": {
		NNAOperatorType.Add: AddNNATwistComponentOperator.bl_idname
	},
}
