import bpy

from ..utils import nna_utils_json

class NNA_Json_Edit_Base:
	"""Base class for Edit-Json Operators"""
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	component_index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore

	def parse(self, json_component: dict): pass
	def serialize(self, original_json_component: dict) -> dict: pass

	def invoke(self, context, event):
		json_component = nna_utils_json.get_component(self.target_id, self.component_index)

		self.parse(json_component)

		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		try:
			json_component = nna_utils_json.get_component(self.target_id, self.component_index)

			new_json_component = self.serialize(json_component)

			nna_utils_json.replace_component(self.target_id, new_json_component, self.component_index)
			self.report({'INFO'}, "Component successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
