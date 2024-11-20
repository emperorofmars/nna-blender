import json
import bpy
from . import nna_utils_json


class EditNNARawJsonOperator(bpy.types.Operator):
	"""Edit the raw Json for the whole object"""
	bl_idname = "nna.edit_raw_json"
	bl_label = "Edit Raw NNA Json Object"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	raw_json: bpy.props.StringProperty(name = "raw_json") # type: ignore
	
	def invoke(self, context, event):
		self.raw_json = nna_utils_json.get_json_from_target_id(self.target_id)
		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			component_list_valid = nna_utils_json.validate_component_list_text(self.raw_json)
			if(not component_list_valid["success"]):
				self.report({'ERROR'}, component_list_valid["error"])
				return {"CANCELLED"}

			nna_utils_json.serialize_json_to_target_id(self.target_id, self.raw_json)
			self.report({'INFO'}, "Object Json successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.label(text="Target Object: " + self.target_id)
		self.layout.prop(self, "raw_json", text="", expand=True)


class AddNNARawJsonComponentOperator(bpy.types.Operator):
	"""Add a new component specified in raw Json"""
	bl_idname = "nna.add_raw_json_component"
	bl_label = "Add"
	bl_options = {"REGISTER", "UNDO"}
	
	target_id: bpy.props.StringProperty(name="targetId") # type: ignore
	new_component: bpy.props.StringProperty(name="new_component", default="{\"t\":\"example_type\"}") # type: ignore

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			json_component_valid = nna_utils_json.validate_component_text(self.new_component)
			if(not json_component_valid["success"]):
				self.report({'ERROR'}, json_component_valid["error"])
				return {"CANCELLED"}
			
			nna_utils_json.add_component(self.target_id, json_component_valid["value"])
			self.report({'INFO'}, "Component successfully added")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.label(text="Target Object: " + self.target_id)
		self.layout.prop(self, "new_component", text="", expand=True)


class EditNNARawJsonComponentOperator(bpy.types.Operator):
	"""Edit the raw Json of this component"""
	bl_idname = "nna.edit_raw_json_component"
	bl_label = "Edit"
	bl_options = {"REGISTER", "UNDO"}

	component_index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore
	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore

	json_component: bpy.props.StringProperty(name = "json_component") # type: ignore
	
	def invoke(self, context, event):
		try:
			self.json_component = json.dumps(nna_utils_json.get_component(self.target_id, self.component_index))
		except Exception as error:
			self.report({'ERROR'}, str(error))
			return None
		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			json_component_valid = nna_utils_json.validate_component_text(self.json_component)
			if(not json_component_valid["success"]):
				self.report({'ERROR'}, json_component_valid["error"])
				return {"CANCELLED"}
			
			nna_utils_json.replace_component(self.target_id, json_component_valid["value"], self.component_index)
			self.report({'INFO'}, "Component successfully edited")
			return {"FINISHED"}
		except Exception as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.label(text="Target Object: " + self.target_id)
		self.layout.prop(self, "json_component", text="", expand=True)
