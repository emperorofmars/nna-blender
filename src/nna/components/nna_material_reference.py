import bpy
import json

from .. import nna_name_utils
from .. import nna_json_utils
from .. import nna_tree_utils


class AddNNAMaterialReferenceComponentOperator(bpy.types.Operator):
	bl_idname = "nna.add_nna_material_reference"
	bl_label = "Add Material Reference Component"
	bl_options = {"REGISTER", "UNDO"}
	
	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	
	def execute(self, context):
		try:
			nna_json_utils.add_component(self.target_id, json.dumps({"t":"nna.material_reference","slots":[]}))
			self.report({'INFO'}, "Component successfully added")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}


def display_nna_material_reference_component(object, layout, json_dict):
	for idx, slot in enumerate(json_dict["slots"]):
		row = layout.row()
		row.label(text=str(idx))
		row.label(text=slot)
	if(len(json_dict["slots"]) == 0):
		layout.label(text="No Material Slots Mapped")


class EditNNAMaterialReferenceComponentOperator(bpy.types.Operator):
	bl_idname = "nna.edit_nna_material_reference"
	bl_label = "Edit Material Reference Component"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	component_index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore

	#slots: bpy.props.CollectionProperty(type=_MaterialSlotsProperty, options={"SKIP_SAVE"}, override={"USE_INSERTION"}) # type: ignore
	
	def invoke(self, context, event):
		json_component = nna_json_utils.get_component_dict(self.target_id, self.component_index)
		object = nna_tree_utils.get_object_by_target_id(self.target_id)

		object.nna_material_reference_collection.clear()
		for slot in json_component["slots"]:
			object.nna_material_reference_collection.add().mapping = str(slot)

		return context.window_manager.invoke_props_dialog(self)
	
	def execute(self, context):
		try:
			json_component = nna_json_utils.get_component_dict(self.target_id, self.component_index)
			object = nna_tree_utils.get_object_by_target_id(self.target_id)

			slots = []
			for idx, slot in enumerate(object.nna_material_reference_collection):
				slots.append(slot.mapping)
			json_component["slots"] = slots

			nna_json_utils.replace_component(self.target_id, json.dumps(json_component), self.component_index)
			self.report({'INFO'}, "Component successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		object = nna_tree_utils.get_object_by_target_id(self.target_id)
		for idx, slot in enumerate(object.nna_material_reference_collection):
			row = self.layout.row()
			row.prop(slot, "mapping", text="Slot " + str(idx))
			col = row.column()
			up = col.operator(NNAMaterialSlotsMoveOperator.bl_idname, text="", icon="TRIA_UP")
			up.index = idx
			up.direction = True
			if(idx == 0): col.enabled = False
			col = row.column()
			down = col.operator(NNAMaterialSlotsMoveOperator.bl_idname, text="", icon="TRIA_DOWN")
			down.index = idx
			down.direction = False
			if(idx == len(object.nna_material_reference_collection) - 1): col.enabled = False
			row.operator(NNAMaterialSlotsDeleteOperator.bl_idname, text="", icon="X").index = idx
		self.layout.operator(NNAMaterialSlotsAddOperator.bl_idname)


class NNAMaterialSlotsProperty(bpy.types.PropertyGroup):
    mapping: bpy.props.StringProperty(name="Mapping", default="") # type: ignore

class NNAMaterialSlotsAddOperator(bpy.types.Operator):
	bl_idname = "nna.edit_nna_material_reference_slots_add"
	bl_label = "Add Slot"
	bl_options = {"REGISTER", "UNDO"}

	def execute(self, context):
		context.object.nna_material_reference_collection.add()
		return {"FINISHED"}

class NNAMaterialSlotsDeleteOperator(bpy.types.Operator):
	bl_idname = "nna.edit_nna_material_reference_slots_delete"
	bl_label = "Delete Slot"
	bl_options = {"REGISTER", "UNDO"}
	
	index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore

	def execute(self, context):
		context.object.nna_material_reference_collection.remove(self.index)
		return {"FINISHED"}

class NNAMaterialSlotsMoveOperator(bpy.types.Operator):
	bl_idname = "nna.edit_nna_material_reference_slots_move"
	bl_label = "Delete Slot"
	bl_options = {"REGISTER", "UNDO"}
	
	index: bpy.props.IntProperty(name = "index", default=-1) # type: ignore
	direction: bpy.props.BoolProperty(name = "direction", default=True) # type: ignore

	def execute(self, context):
		offset = -1 if self.direction else 1
		tmp = context.object.nna_material_reference_collection[self.index].mapping
		context.object.nna_material_reference_collection[self.index].mapping = context.object.nna_material_reference_collection[self.index + offset].mapping
		context.object.nna_material_reference_collection[self.index + offset].mapping = tmp
		return {"FINISHED"}


nna_types = {
	"nna.material_reference": {
		"json_add": AddNNAMaterialReferenceComponentOperator.bl_idname,
		"json_edit": EditNNAMaterialReferenceComponentOperator.bl_idname,
		"json_display": display_nna_material_reference_component,
	},
}


def register():
	bpy.types.Object.nna_material_reference_collection = bpy.props.CollectionProperty(type=NNAMaterialSlotsProperty, options={"SKIP_SAVE"}, override={"USE_INSERTION"}) # type: ignore

def unregister():
	if hasattr(bpy.types.Object, "nna_material_reference_collection"):
		del bpy.types.Object.nna_material_reference_collection
