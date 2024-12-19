import bpy

from .. import nna_utils_json

class NNA_Json_Add_Base:
	"""Base class for Add-Json Operators"""
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore

	nna_name: None

	def init(self) -> dict:
		return {"t":self.nna_name}

	def execute(self, context):
		try:
			nna_utils_json.add_component(self.target_id, self.init())
			self.report({'INFO'}, "Component successfully added")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
