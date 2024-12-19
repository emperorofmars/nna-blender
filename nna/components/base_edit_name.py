import bpy

from .. import nna_utils_name
from .. import nna_utils_tree

class NNA_Name_Definition_Base:
	"""Base class for Name-Definition Operators"""
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore

	def parse(self, nna_name: str): pass
	def serialize(self, target: bpy.types.Object | bpy.types.Bone, base_object: bpy.types.Object | None, nna_name: str, symmetry: str) -> str: pass

	def invoke(self, context, event):
		nna_name = nna_utils_name.get_nna_name(self.target_id)

		self.parse(nna_name)

		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		try:
			target = nna_utils_tree.get_object_by_target_id(self.target_id)
			base_object = nna_utils_tree.get_base_object_by_target_id(self.target_id)
			(nna_name, symmetry) = nna_utils_name.get_side_suffix(nna_utils_name.get_nna_name(self.target_id))

			new_name = self.serialize(target, base_object, nna_name, symmetry)

			if(len(str.encode(new_name)) > 63):
				self.report({'ERROR'}, "Name too long")
				return {"CANCELLED"}
			else:
				targeting_object = nna_utils_tree.find_nna_targeting_object(self.target_id)
				if(targeting_object): nna_utils_tree.reparent_nna_targeting_object(self.target_id, nna_utils_name.construct_nna_id(self.target_id, new_name))
				target.name = new_name
				self.report({'INFO'}, "Component successfully edited")
				return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
