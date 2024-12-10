# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import bpy
from . import nna_utils_tree
from . import nna_utils_json


class EditNNAIDListOperator(bpy.types.Operator):
	"""Edit list of IDs"""
	bl_idname = "nna.edit_id_list"
	bl_label = "Edit"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	component_index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore
	json_key: bpy.props.StringProperty(name = "json_key") # type: ignore

	def invoke(self, context, event):
		json_component = nna_utils_json.get_component(self.target_id, self.component_index)
		object = nna_utils_tree.get_object_by_target_id(self.target_id)

		object.nna_id_list.clear()
		for id in json_component.get(self.json_key, []):
			object.nna_id_list.add().id = str(id)

		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		try:
			json_component = nna_utils_json.get_component(self.target_id, self.component_index)
			object = nna_utils_tree.get_object_by_target_id(self.target_id)

			id_list = []
			for id in object.nna_id_list:
				if(id.id): id_list.append(id.id)
			json_component[self.json_key] = id_list

			nna_utils_json.replace_component(self.target_id, json_component, self.component_index)
			self.report({'INFO'}, "IDs successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}

	def draw(self, context):
		object = nna_utils_tree.get_object_by_target_id(self.target_id)
		for index, id in enumerate(object.nna_id_list):
			row = self.layout.row()
			row.prop(id, "id", text="ID " + str(index))
			delete_button = row.operator(NNAIDPropertyDeleteOperator.bl_idname, text="", icon="X")
			delete_button.target_id = self.target_id
			delete_button.index = index
		self.layout.operator(NNAIDPropertyAddOperator.bl_idname, icon="ADD").target_id = self.target_id



class NNAIDProperty(bpy.types.PropertyGroup):
	id: bpy.props.StringProperty(name="Id", default="") # type: ignore

class NNAIDPropertyAddOperator(bpy.types.Operator):
	bl_idname = "nna.edit_id_list_add"
	bl_label = "Add"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore

	def execute(self, context):
		object = nna_utils_tree.get_object_by_target_id(self.target_id)
		object.nna_id_list.add()
		return {"FINISHED"}

class NNAIDPropertyDeleteOperator(bpy.types.Operator):
	bl_idname = "nna.edit_id_list_delete"
	bl_label = "Delete"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore

	def execute(self, context):
		object = nna_utils_tree.get_object_by_target_id(self.target_id)
		object.nna_id_list.remove(self.index)
		return {"FINISHED"}


def draw_id_list(target_id: str, layout: bpy.types.UILayout, json_component: dict, component_index: int, json_key: str, label_text: str = None):
	if(label_text == None): label_text = json_key.capitalize()
	row = layout.split(factor=0.4)
	row.label(text=label_text)
	row = row.row()
	id_list = ""
	for index, id in enumerate(json_component.get(json_key, [])):
		id_list += str(id)
		if(index < len(json_component.get(json_key)) - 1): id_list += ", "
	row.label(text=id_list if id_list else "-")
	edit_list_button = row.operator(EditNNAIDListOperator.bl_idname, text="", icon="OPTIONS")
	edit_list_button.target_id = target_id
	edit_list_button.component_index = component_index
	edit_list_button.json_key = json_key


def register():
	bpy.types.Object.nna_id_list = bpy.props.CollectionProperty(type=NNAIDProperty, name="ID List", options={"SKIP_SAVE"}, override={"USE_INSERTION"}) # type: ignore
	bpy.types.Bone.nna_id_list = bpy.props.CollectionProperty(type=NNAIDProperty, name="ID List", options={"SKIP_SAVE"}, override={"USE_INSERTION"}) # type: ignore

def unregister():
	if hasattr(bpy.types.Object, "nna_id_list"):
		del bpy.types.Object.nna_id_list
	if hasattr(bpy.types.Bone, "nna_id_list"):
		del bpy.types.Bone.nna_id_list
