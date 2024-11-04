
from .nna_operators import *
from .nna_registry import *
from .nna_json_utils import *


def draw_nna_name_editor(self, context, target_id):
	name_operators = get_nna_operators(NNAFunctionType.Name)

	self.layout.label(text="Name Definition")
	row = self.layout.row()
	row.prop(bpy.context.scene, "nna_oparators_name", text="")
	name_button = row.operator(bpy.context.scene.nna_oparators_name, text="Name Definition")
	name_button.target_id = target_id


def draw_nna_json_editor(self, context, target_id):
	jsonText = get_json_from_targetname(target_id)
	preview_operators = get_nna_operators(NNAFunctionType.JsonDisplay)
	edit_operators = get_nna_operators(NNAFunctionType.JsonEdit)
	remove_operators = get_nna_operators(NNAFunctionType.JsonRemove)
	
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
				editRawButton = row.operator(EditNNARawJsonComponentOperator.bl_idname, text="Edit Raw Json")
				editRawButton.target_id = target_id
				editRawButton.component_index = idx
				if(str(component["t"]) in remove_operators):
					deleteButton = row.operator(remove_operators[str(component["t"])], text="Remove")
					deleteButton.target_id = target_id
					deleteButton.component_index = idx
				else:
					deleteButton = row.operator(RemoveNNAJsonComponentOperator.bl_idname, text="Remove")
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
	button_edit_raw = self.layout.operator(EditNNARawJsonOperator.bl_idname, text="Edit Raw Json")
	button_edit_raw.target_id = target_id

	self.layout.separator(type="LINE", factor=5)
	self.layout.operator(RemoveNNATargetingObjectOperator.bl_idname)
	button_edit_raw.target_id = target_id
