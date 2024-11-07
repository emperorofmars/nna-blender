import json
import bpy

from . import nna_operators_common
from . import nna_operators_raw_json
from . import nna_registry
from . import nna_utils_tree
from . import nna_utils_json


class NNAObjectPanel(bpy.types.Panel):
	"""Display the NNA editor for Blender objects"""
	bl_idname = "OBJECT_PT_nna_editor"
	bl_label = "NNA Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_category = "NNA"
	bl_context = "object"

	@classmethod
	def poll(cls, context):
		return (context.object is not None)

	def draw_header(self, context):
		pass
		
	def draw(self, context):
		draw_nna_editor(self, context, context.object.name, nna_utils_tree.determine_nna_object_state(context.object))


class NNABonePanel(bpy.types.Panel):
	"""Display the NNA editor for Blender bones"""
	bl_idname = "OBJECT_PT_nna_bone_editor"
	bl_label = "NNA Bone Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_category = "NNA"
	bl_context = "bone"

	@classmethod
	def poll(cls, context):
		return (context.object is not None)

	def draw_header(self, context):
		pass
		
	def draw(self, context):
		draw_nna_editor(self, context, context.object.name + "$" + context.bone.name, nna_utils_tree.determine_nna_bone_state(context.object, context.bone))


def draw_nna_editor(self, context, target_id, state):
	match state:
		case nna_utils_tree.NNAObjectState.IsRootObject:
			button = self.layout.operator(nna_operators_common.CreateNNATargetingObjectOperator.bl_idname, text="Initializie NNA for the Export Root")
			button.target_id = target_id
		case nna_utils_tree.NNAObjectState.IsRootObjectWithTargeting:
			self.layout.label(text="This is the Json definition for: The Scene Root")
			draw_nna_json_editor(self, context, target_id)
		case nna_utils_tree.NNAObjectState.NotInited:
			draw_nna_name_editor(self, context, target_id)
			self.layout.separator(type="LINE", factor=2)
			box = self.layout.box()
			box.label(text="Json Components Not Enabled")
			button = box.operator(operator=nna_operators_common.InitializeNNAOperator.bl_idname)
			button.nna_init_collection = context.collection.name
		case nna_utils_tree.NNAObjectState.InitedOutsideTree:
			draw_nna_name_editor(self, context, target_id)
			self.layout.separator(type="LINE", factor=2)
			box = self.layout.box()
			box.label(text="Json Components Not Enabled")
			box.label(text="This Node is outside the NNA tree!")
		case nna_utils_tree.NNAObjectState.InitedInsideTree:
			if(not draw_nna_name_editor(self, context, target_id)):
				self.layout.separator(type="LINE", factor=2)
				box = self.layout.box()
				box.label(text="Json Components Not Enabled")
				button = box.operator(nna_operators_common.CreateNNATargetingObjectOperator.bl_idname)
				button.target_id = target_id
		case nna_utils_tree.NNAObjectState.IsTargetingObject:
			self.layout.label(text="This is the Json definition for: " + ("The Scene Root" if target_id == "$root" else target_id[8:]))
			if(target_id == "$root"):
				draw_nna_json_editor(self, context, "$nna")
			else:
				_draw_nna_editor_for_target(self, context, target_id[8:])
		case nna_utils_tree.NNAObjectState.IsJsonDefinition:
			if(not context.object.parent.name[8:]):
				self.layout.label(text="This part of the Json definition for: The Scene Root" + context.object.parent.name[8:])
				draw_nna_json_editor(self, context, "$nna")
			else:
				self.layout.label(text="This part of the Json definition for: " + context.object.parent.name[8:])
				_draw_nna_editor_for_target(self, context, context.object.parent.name[8:])
		case nna_utils_tree.NNAObjectState.IsInvalidTargetingObject:
			self.layout.label(text="Invalid Target: '" + context.object.name[8:] + "' does NOT exist!")
		case nna_utils_tree.NNAObjectState.HasTargetingObject:
			_draw_nna_editor_for_target(self, context, target_id)

def _draw_nna_editor_for_target(self, context, target_id):
	if(draw_nna_name_editor(self, context, target_id, True)):
		box = self.layout.box()
		box.label(text="Warning: This Node has both a Name and Component definition.")
		box.label(text="It is recommended to use only one.")
	draw_nna_json_editor(self, context, target_id)


def draw_nna_name_editor(self, context, target_id, ignore_no_match = False) -> bool:
	name_match_operators = nna_registry.get_nna_operators(nna_registry.NNAFunctionType.NameMatch)
	name_draw_operators = nna_registry.get_nna_operators(nna_registry.NNAFunctionType.NameDisplay)

	name_definition_match = None
	for nna_type, match in name_match_operators.items():
		if(match):
			nna_name = nna_utils_tree.get_object_by_target_id(target_id).name
			index = match(nna_name)
			if(index >= 0):
				name_definition_match = {"nna_name": nna_name, "index": index, "nna_type": nna_type}
				break
	
	if(name_definition_match):
		box = self.layout.box()
		box.label(text="Name Definition: " + name_definition_match["nna_type"])
		if(name_definition_match["nna_type"] in name_draw_operators):
			name_draw_operators[name_definition_match["nna_type"]](box, name_definition_match["nna_name"])
		if(name_definition_match["index"] > 0):
			remove_button = box.operator(nna_operators_common.RemoveNNANameDefinitionOperator.bl_idname, text="Remove")
			remove_button.target_id = target_id
			remove_button.name_definition_index = name_definition_match["index"]
	elif(not name_definition_match and not ignore_no_match):
		box = self.layout.box()
		box.label(text="No Name Definition Set")
		row = box.row()
		row.prop(bpy.context.scene, "nna_oparators_name", text="")
		name_button = row.operator(bpy.context.scene.nna_oparators_name, text="Set Name Definition")
		if(name_button): name_button.target_id = target_id
		else: row.label(text="No Types Loaded")
	
	return name_definition_match


def draw_nna_json_editor(self, context, target_id):
	jsonText = nna_utils_json.get_json_from_target_id(target_id)
	
	preview_operators = nna_registry.get_nna_operators(nna_registry.NNAFunctionType.JsonDisplay)
	edit_operators = nna_registry.get_nna_operators(nna_registry.NNAFunctionType.JsonEdit)
	remove_operators = nna_registry.get_nna_operators(nna_registry.NNAFunctionType.JsonRemove)
	
	box = self.layout.box()
	box.label(text="Components")

	if(len(jsonText) > 2):
		try:
			col = box.column(heading="Components")
			componentsList = json.loads(jsonText)
			for idx, component in enumerate(componentsList):
				component_box = col.box()
				row = component_box.row()
				row.label(text="Type")
				row.label(text=str(component["t"]))

				if(str(component["t"]) in preview_operators):
					preview_operators[str(component["t"])](context.object, component_box, component)
				else:
					for property in component.keys():
						if(property == "t"): continue
						row = component_box.row()
						row.label(text=property)
						row.label(text=str(component[property]))

				component_box.separator(type="LINE", factor=1)
				row = component_box.row()
				if(str(component["t"]) in edit_operators):
					editButton = row.operator(edit_operators[str(component["t"])], text="Edit")
					editButton.target_id = target_id
					editButton.component_index = idx
				editRawButton = row.operator(nna_operators_raw_json.EditNNARawJsonComponentOperator.bl_idname, text="Edit Raw Json")
				editRawButton.target_id = target_id
				editRawButton.component_index = idx
				if(str(component["t"]) in remove_operators):
					deleteButton = row.operator(remove_operators[str(component["t"])], text="Remove")
					deleteButton.target_id = target_id
					deleteButton.component_index = idx
				else:
					deleteButton = row.operator(nna_operators_common.RemoveNNAJsonComponentOperator.bl_idname, text="Remove")
					deleteButton.target_id = target_id
					deleteButton.component_index = idx

				if(idx < len(componentsList) - 1): col.separator(factor=1)
		except ValueError as e:
			box.label(text="Invalid Json: " + str(e))
	else:
		box.label(text="No Components Added")
	
	box.separator(type="LINE", factor=1)
	row = box.row()
	row.prop(bpy.context.scene, "nna_oparators_add", text="")
	button_add = row.operator(bpy.context.scene.nna_oparators_add, text="Add Component")
	if(button_add):	button_add.target_id = target_id
	else: row.label(text="No Types Loaded")
	button_edit_raw = row.operator(nna_operators_raw_json.EditNNARawJsonOperator.bl_idname, text="Edit Raw Json")
	button_edit_raw.target_id = target_id

	box.separator(type="LINE", factor=2)
	button_remove_nna_targeting = box.operator(nna_operators_common.RemoveNNATargetingObjectOperator.bl_idname)
	button_remove_nna_targeting.target_id = target_id
