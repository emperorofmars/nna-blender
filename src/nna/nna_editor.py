
from .nna_operators import *
from .nna_registry import *
from .nna_json_utils import *


def draw_nna_editor(self, context, target_id):
	jsonText = get_json_from_targetname(target_id)
	preview_operators = get_nna_operators(NNAFunctionType.Display)
	edit_operators = get_nna_operators(NNAFunctionType.Edit)
	remove_operators = get_nna_operators(NNAFunctionType.Remove)
	if(len(jsonText) > 2):
		try:
			componentsList = json.loads(jsonText)
			#self.layout.label(text="Components")
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
	row.operator(bpy.context.scene.nna_oparators_add, text="Add Component")

	self.layout.separator(factor=1)
	self.layout.operator(EditNNARawJsonOperator.bl_idname, text="Edit Raw Json")

	self.layout.separator(type="LINE", factor=5)
	self.layout.operator(RemoveNNATargetingObjectOperator.bl_idname)
