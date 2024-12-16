import bpy
from . import nna_utils_tree
from . import nna_utils_json
from . import nna_utils_name


class SetActiveObjectOperator(bpy.types.Operator):
	"""Select the specified object in the scene"""
	bl_idname = "nna.util_set_active_object"
	bl_label = "Select"
	bl_options = {"REGISTER", "UNDO"}

	target_name: bpy.props.StringProperty(name = "target_name") # type: ignore

	def execute(self, context):
		target = nna_utils_tree.get_base_object_by_target_id(self.target_name)
		for selected in bpy.context.selected_objects:
			selected.select_set(False)
		target.select_set(True)
		bpy.context.view_layer.objects.active = target
		return {"FINISHED"}


class CreateNewObjectOperator(bpy.types.Operator):
	"""Create a new object with the specified name"""
	bl_idname = "nna.util_create_new_object"
	bl_label = "Create new Object"
	bl_options = {"REGISTER", "UNDO"}

	target_name: bpy.props.StringProperty(name = "target_name") # type: ignore

	def execute(self, context):
		originalSelectedObject = bpy.context.active_object
		bpy.ops.object.empty_add()
		new_object = bpy.context.active_object
		new_object.name = self.target_name
		bpy.context.view_layer.objects.active = originalSelectedObject
		return {"FINISHED"}
