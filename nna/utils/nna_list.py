import bpy


class NNAListProperty(bpy.types.PropertyGroup):
	value: bpy.props.StringProperty(name="Value", default="") # type: ignore


def create_list_string(nna_list: list) -> str:
	display = ""
	for index, value in enumerate(nna_list):
		display += value
		if(index < len(nna_list) - 1): display += ", "
	return display


def edit_list(self, context):
	for index, value in enumerate(context.scene.nna_list):
		row = self.layout.row()
		row.prop(value, "value")
		delete_button = row.operator(NNAListPropertyDeleteOperator.bl_idname, text="", icon="X")
		delete_button.index = index
	self.layout.operator(NNAListPropertyAddOperator.bl_idname, icon="ADD")

class NNAListPropertyAddOperator(bpy.types.Operator):
	bl_idname = "nna.edit_list_add"
	bl_label = "Add"
	bl_options = {"REGISTER", "UNDO"}

	def execute(self, context):
		context.scene.nna_list.add()
		return {"FINISHED"}

class NNAListPropertyDeleteOperator(bpy.types.Operator):
	bl_idname = "nna.edit_list_delete"
	bl_label = "Delete"
	bl_options = {"REGISTER", "UNDO"}

	index: bpy.props.IntProperty(name = "index", default=-1) # type: ignore

	def execute(self, context):
		context.scene.nna_list.remove(self.index)
		return {"FINISHED"}


def register():
	bpy.types.Scene.nna_list = bpy.props.CollectionProperty(type=NNAListProperty, name="List", options={"SKIP_SAVE"}, override={"USE_INSERTION"}) # type: ignore

def unregister():
	if hasattr(bpy.types.Scene, "nna_list"):
		del bpy.types.Scene.nna_list

