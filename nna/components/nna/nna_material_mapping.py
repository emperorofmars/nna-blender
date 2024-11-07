import bpy

from ... import nna_utils_name
from ... import nna_utils_json
from ... import nna_utils_tree


class AddNNAMaterialMappingComponentOperator(bpy.types.Operator):
	bl_idname = "nna.add_nna_material_mapping"
	bl_label = "Add Material Mapping Component"
	bl_options = {"REGISTER", "UNDO"}
	
	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	
	def execute(self, context):
		try:
			nna_utils_json.add_component(self.target_id, {"t":"nna.material_mapping","slots":[]})
			self.report({'INFO'}, "Component successfully added")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}


def display_nna_material_mapping_component(object, layout, json_dict):
	for idx, slot in enumerate(json_dict["slots"]):
		row = layout.row()
		row.label(text=str(idx))
		row.label(text=slot)
	if(len(json_dict["slots"]) == 0):
		layout.label(text="No Material Slots Mapped")


class EditNNAMaterialMappingComponentOperator(bpy.types.Operator):
	bl_idname = "nna.edit_nna_material_mapping"
	bl_label = "Edit Material Mapping Component"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	component_index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore
	
	def invoke(self, context, event):
		json_component = nna_utils_json.get_component(self.target_id, self.component_index)
		object = nna_utils_tree.get_object_by_target_id(self.target_id)

		object.nna_material_mapping_collection.clear()
		for slot in json_component["slots"]:
			object.nna_material_mapping_collection.add().mapping = str(slot)

		return context.window_manager.invoke_props_dialog(self)
	
	def execute(self, context):
		try:
			json_component = nna_utils_json.get_component(self.target_id, self.component_index)
			object = nna_utils_tree.get_object_by_target_id(self.target_id)

			slots = []
			for idx, slot in enumerate(object.nna_material_mapping_collection):
				slots.append(slot.mapping)
			json_component["slots"] = slots

			nna_utils_json.replace_component(self.target_id, json_component, self.component_index)
			self.report({'INFO'}, "Component successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
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
	"nna.material_mapping": {
		"json_add": AddNNAMaterialMappingComponentOperator.bl_idname,
		"json_edit": EditNNAMaterialMappingComponentOperator.bl_idname,
		"json_display": display_nna_material_mapping_component,
	},
}


def register():
	bpy.types.Object.nna_material_mapping_collection = bpy.props.CollectionProperty(type=NNAMaterialSlotsProperty, options={"SKIP_SAVE"}, override={"USE_INSERTION"}) # type: ignore

def unregister():
	if hasattr(bpy.types.Object, "nna_material_mapping_collection"):
		del bpy.types.Object.nna_material_mapping_collection
