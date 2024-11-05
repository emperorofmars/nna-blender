import json
import bpy

from . import nna_operators_common
from . import nna_operators_raw_json
from . import nna_registry
from . import nna_tree_utils
from . import nna_json_utils
from . import nna_name_utils


def draw_nna_name_editor(self, context, target_id):
	#name_operators = nna_registry.get_nna_operators(nna_registry.NNAFunctionType.NameSet)
	name_match_operators = nna_registry.get_nna_operators(nna_registry.NNAFunctionType.NameMatch)

	name_definition_match = False
	for nna_type, match in name_match_operators.items():
		if(match):
			nna_name = nna_tree_utils.get_object_by_target_id(target_id).name
			index = match(nna_name)
			if(index > 0):
				self.layout.label(text="Name Definition: " + nna_type)
				remove_button = self.layout.operator(nna_operators_common.RemoveNNANameDefinitionOperator.bl_idname, text="Remove")
				remove_button.target_id = target_id
				remove_button.name_definition_index = index
				name_definition_match = True
				break
	
	if(not name_definition_match):
		#self.layout.label(text="Set Name Definition")
		row = self.layout.row()
		row.prop(bpy.context.scene, "nna_oparators_name", text="")
		name_button = row.operator(bpy.context.scene.nna_oparators_name, text="Set Name Definition")
		name_button.target_id = target_id


def draw_nna_json_editor(self, context, target_id):
	jsonText = nna_json_utils.get_json_from_targetname(target_id)
	
	preview_operators = nna_registry.get_nna_operators(nna_registry.NNAFunctionType.JsonDisplay)
	edit_operators = nna_registry.get_nna_operators(nna_registry.NNAFunctionType.JsonEdit)
	remove_operators = nna_registry.get_nna_operators(nna_registry.NNAFunctionType.JsonRemove)
	
	self.layout.label(text="Json Components")
	if(len(jsonText) > 2):
		try:
			componentsList = json.loads(jsonText)
			col = self.layout.column(heading="Components")
			for idx, component in enumerate(componentsList):
				box = col.box()
				row = box.row()
				row.label(text="Type")
				row.label(text=str(component["t"]))

				if(str(component["t"]) in preview_operators):
					preview_operators[str(component["t"])](context.object, box, component)
				else:
					for property in component.keys():
						if(property == "t"): continue
						row = box.row()
						row.label(text=property)
						row.label(text=str(component[property]))

				box.separator(type="LINE", factor=1)
				row = box.row()
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
			self.layout.label(text="Invalid Json: " + str(e))
	else:
		self.layout.label(text="No Component Added")
	
	self.layout.separator(type="LINE", factor=1)
	row = self.layout.row()
	row.prop(bpy.context.scene, "nna_oparators_add", text="")
	button_add = row.operator(bpy.context.scene.nna_oparators_add, text="Add Component")
	button_add.target_id = target_id

	self.layout.separator(factor=1)
	button_edit_raw = self.layout.operator(nna_operators_raw_json.EditNNARawJsonOperator.bl_idname, text="Edit Raw Json")
	button_edit_raw.target_id = target_id

	self.layout.separator(type="LINE", factor=5)
	button_remove_nna_targeting = self.layout.operator(nna_operators_common.RemoveNNATargetingObjectOperator.bl_idname)
	button_remove_nna_targeting.target_id = target_id
