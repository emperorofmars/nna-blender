# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import bpy


class NNAKVProperty(bpy.types.PropertyGroup):
	key: bpy.props.StringProperty(name="Key", default="") # type: ignore
	value: bpy.props.StringProperty(name="Value", default="") # type: ignore


def create_kv_list_string(kv_list: list) -> str:
	display = ""
	for index, kv_pair in enumerate(kv_list):
		display += str(kv_pair["key"]) + ": " + str(kv_pair["value"])
		if(index < len(kv_list) - 1): display += ", "
	return display


def edit_kv_list(self, context):
	for index, kv_entry in enumerate(context.scene.nna_kv_list):
		row = self.layout.row()
		row.prop(kv_entry, "key")
		row.prop(kv_entry, "value")
		delete_button = row.operator(NNAKVPropertyDeleteOperator.bl_idname, text="", icon="X")
		delete_button.index = index
	self.layout.operator(NNAKVPropertyAddOperator.bl_idname, icon="ADD")

class NNAKVPropertyAddOperator(bpy.types.Operator):
	bl_idname = "nna.edit_kv_list_add"
	bl_label = "Add"
	bl_options = {"REGISTER", "UNDO"}

	def execute(self, context):
		context.scene.nna_kv_list.add()
		return {"FINISHED"}

class NNAKVPropertyDeleteOperator(bpy.types.Operator):
	bl_idname = "nna.edit_kv_list_delete"
	bl_label = "Delete"
	bl_options = {"REGISTER", "UNDO"}

	index: bpy.props.IntProperty(name = "index", default=-1) # type: ignore

	def execute(self, context):
		context.scene.nna_kv_list.remove(self.index)
		return {"FINISHED"}


def register():
	bpy.types.Scene.nna_kv_list = bpy.props.CollectionProperty(type=NNAKVProperty, name="Key Value List", options={"SKIP_SAVE"}, override={"USE_INSERTION"}) # type: ignore

def unregister():
	if hasattr(bpy.types.Scene, "nna_kv_list"):
		del bpy.types.Scene.nna_kv_list

