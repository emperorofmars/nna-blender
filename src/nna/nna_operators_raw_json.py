import bpy
from . import nna_json_utils


class EditNNARawJsonOperator(bpy.types.Operator):
	bl_idname = "nna.edit_raw_json"
	bl_label = "Edit Raw NNA Json Object"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			nna_json = nna_json_utils.get_json_from_targetname(self.target_id)
			nna_json_utils.serialize_json_to_targetname(self.target_id, nna_json)
			self.report({'INFO'}, "Object Json successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.label(text="Target Object: " + self.target)
		self.layout.prop(self, "json", text="", expand=True)


class AddNNARawJsonComponentOperator(bpy.types.Operator):
	bl_idname = "nna.add_raw_json_component"
	bl_label = "Add Raw Json Component"
	bl_options = {"REGISTER", "UNDO"}
	
	target_id: bpy.props.StringProperty(name="targetId") # type: ignore

	new_component: bpy.props.StringProperty(name="new_component", default="{\"t\":\"example\"}") # type: ignore

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			nna_json = nna_json_utils.get_json_from_targetname(self.target_id)
			new_nna_json = nna_json_utils.add_component_to_nna(nna_json, self.new_component)
			nna_json_utils.serialize_json_to_targetname(self.target_id, new_nna_json)
			self.report({'INFO'}, "Component successfully added")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.label(text="Target Object: " + self.target_id)
		self.layout.prop(self, "new_component", text="", expand=True)


class EditNNARawJsonComponentOperator(bpy.types.Operator):
	bl_idname = "nna.edit_raw_json_component"
	bl_label = "Edit Raw Json Component"
	bl_options = {"REGISTER", "UNDO"}

	component_index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore
	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore

	json_component: bpy.props.StringProperty(name = "json_component") # type: ignore
	
	def invoke(self, context, event):
		nna_json = nna_json_utils.get_json_from_targetname(self.target_id)
		try:
			self.json_component = nna_json_utils.get_component_from_nna(nna_json, self.component_index)
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return None
		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			nna_json = nna_json_utils.get_json_from_targetname(self.target_id)
			jsonText = nna_json_utils.replace_component_in_nna(nna_json, self.json_component, self.component_index)
			nna_json_utils.serialize_json_to_targetname(self.target_id, jsonText)

			self.report({'INFO'}, "Component successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.label(text="Target Object: " + self.target_id)
		self.layout.prop(self, "json_component", text="", expand=True)
