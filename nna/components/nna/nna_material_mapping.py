import bpy

from ...nna_registry import NNAFunctionType

from .. import NNA_Json_Add_Base
from .. import NNA_Json_Edit_Base

from ...utils import nna_utils_tree


_nna_name = "nna.material_mapping"


class AddNNAMaterialMappingComponentOperator(bpy.types.Operator, NNA_Json_Add_Base):
	"""Maps materials to this mesh from the game-engine projects assets on import based, on the name."""
	bl_idname = "nna.add_nna_material_mapping"
	bl_label = "Add Material Mapping Component"
	nna_name = _nna_name

	def init(self) -> dict:
		return {
			"t": self.nna_name,
			"slots": []
		}


class EditNNAMaterialMappingComponentOperator(bpy.types.Operator, NNA_Json_Edit_Base):
	"""Maps materials to this mesh from the game-engine projects assets on import based, on the name."""
	bl_idname = "nna.edit_nna_material_mapping"
	bl_label = "Edit Material Mapping Component"

	def parse(self, json_component: dict):
		object = nna_utils_tree.get_object_by_target_id(self.target_id)

		object.nna_material_mapping_collection.clear()
		for slot in json_component["slots"]:
			object.nna_material_mapping_collection.add().mapping = str(slot)

	def serialize(self, json_component: dict) -> dict:
		object = nna_utils_tree.get_object_by_target_id(self.target_id)
		slots = []
		for idx, slot in enumerate(object.nna_material_mapping_collection):
			slots.append(slot.mapping)
		json_component["slots"] = slots
		return json_component

	def draw(self, context):
		object = nna_utils_tree.get_object_by_target_id(self.target_id)
		for idx, slot in enumerate(object.nna_material_mapping_collection):
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
			if(idx == len(object.nna_material_mapping_collection) - 1): col.enabled = False
			row.operator(NNAMaterialSlotsDeleteOperator.bl_idname, text="", icon="X").index = idx
		self.layout.operator(NNAMaterialSlotsAddOperator.bl_idname)


def display_nna_material_mapping_component(target_id: str, layout: bpy.types.UILayout, json_component: dict, component_index: int):
	for idx, slot in enumerate(json_component["slots"]):
		row = layout.split(factor=0.4)
		row.label(text=str(idx))
		row.label(text=slot)
	if(len(json_component["slots"]) == 0):
		layout.label(text="No Material Slots Mapped")


class NNAMaterialSlotsProperty(bpy.types.PropertyGroup):
	mapping: bpy.props.StringProperty(name="Mapping", default="") # type: ignore

class NNAMaterialSlotsAddOperator(bpy.types.Operator):
	bl_idname = "nna.edit_nna_material_mapping_slots_add"
	bl_label = "Add Slot"
	bl_options = {"REGISTER", "UNDO"}

	def execute(self, context):
		context.object.nna_material_mapping_collection.add()
		return {"FINISHED"}

class NNAMaterialSlotsDeleteOperator(bpy.types.Operator):
	bl_idname = "nna.edit_nna_material_mapping_slots_delete"
	bl_label = "Delete Slot"
	bl_options = {"REGISTER", "UNDO"}

	index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore

	def execute(self, context):
		context.object.nna_material_mapping_collection.remove(self.index)
		return {"FINISHED"}

class NNAMaterialSlotsMoveOperator(bpy.types.Operator):
	bl_idname = "nna.edit_nna_material_mapping_slots_move"
	bl_label = "Delete Slot"
	bl_options = {"REGISTER", "UNDO"}

	index: bpy.props.IntProperty(name = "index", default=-1) # type: ignore
	direction: bpy.props.BoolProperty(name = "direction", default=True) # type: ignore

	def execute(self, context):
		offset = -1 if self.direction else 1
		tmp = context.object.nna_material_mapping_collection[self.index].mapping
		context.object.nna_material_mapping_collection[self.index].mapping = context.object.nna_material_mapping_collection[self.index + offset].mapping
		context.object.nna_material_mapping_collection[self.index + offset].mapping = tmp
		return {"FINISHED"}


nna_types = {
	_nna_name: {
		NNAFunctionType.JsonAdd: AddNNAMaterialMappingComponentOperator.bl_idname,
		NNAFunctionType.JsonEdit: EditNNAMaterialMappingComponentOperator.bl_idname,
		NNAFunctionType.JsonDisplay: display_nna_material_mapping_component,
	},
}


def register():
	bpy.types.Object.nna_material_mapping_collection = bpy.props.CollectionProperty(type=NNAMaterialSlotsProperty, options={"SKIP_SAVE"}, override={"USE_INSERTION"}) # type: ignore

def unregister():
	if hasattr(bpy.types.Object, "nna_material_mapping_collection"):
		del bpy.types.Object.nna_material_mapping_collection
