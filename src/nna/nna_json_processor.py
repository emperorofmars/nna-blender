import bpy

from .nna_json_utils import *

class AddNNAJsonComponentOperator(bpy.types.Operator):
	bl_idname = "nna.add_json_component"
	bl_label = "Add Json Component"
	bl_options = {"REGISTER", "UNDO"}
	
	target: bpy.props.StringProperty(name = "target") # type: ignore
	json: bpy.props.StringProperty(name = "json") # type: ignore
	type: bpy.props.StringProperty(name = "type") # type: ignore
	newComponent: bpy.props.StringProperty(name = "newComponent") # type: ignore

	def invoke(self, context, event):
		self.target = context.object.name
		self.json = getJsonFromTargetName(context.object.name)
		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			jsonText = addComponentToNNA(self.json, self.newComponent)
			serializeJsonToTargetName(self.target, jsonText)
			self.report({'INFO'}, "Component successfully added")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.label(text="Target Object: " + self.target)
		self.layout.prop(self, "type", text="Type", expand=True)
		self.layout.prop(self, "newComponent", text="Values", expand=True)

def nna_register():
	pass

def nna_unregister():
	pass