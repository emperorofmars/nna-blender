import bpy
import json
from .nna_tree_utils import *
from .nna_operators import *
from .nna_json_utils import *
from .nna_registry import *

class NNAEditor(bpy.types.Panel):
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
		match determine_nna_object_state(context.object):
			case NNAObjectState.IsRootObject:
				button = self.layout.operator(CreateNNATargetingObjectOperator.bl_idname, text="Create NNA Component List for Root")
				button.target = context.object.name
			case NNAObjectState.IsRootObjectWithTargeting:
				self.draw_nna_editor(context)
			case NNAObjectState.NotInited:
				if(len(bpy.context.scene.collection.children_recursive) == 0):
					button = self.layout.operator(operator=InitializeNNAOperator.bl_idname, text="Initialize NNA in Scene")
					button.nna_init_collection = bpy.context.scene.collection.name
				else:
					button = self.layout.operator(operator=InitializeNNAOperator.bl_idname, text="Initialize NNA in Collection")
					button.nna_init_collection = context.collection.name
			case NNAObjectState.InitedOutsideTree:
				self.layout.label(text="This object is outside the NNA tree!")
			case NNAObjectState.InitedInsideTree:
				button = self.layout.operator(CreateNNATargetingObjectOperator.bl_idname, text="Create NNA Component List")
				button.target = context.object.name
			case NNAObjectState.IsTargetingObject:
				self.layout.label(text="This is the Json definition for: " + ("The Scene Root" if context.object.name == "$root" else context.object.name[8:]))
			case NNAObjectState.IsJsonDefinition:
				self.layout.label(text="This part of the Json definition for: " + context.object.parent.name[8:])
			case NNAObjectState.HasTargetingObject:
				self.draw_nna_editor(context)
	
	def draw_nna_editor(self, context):
		jsonText = get_json_from_targetname(context.object.name)
		preview_operators = get_nna_operators(NNAFunctionType.Display)
		edit_operators = get_nna_operators(NNAFunctionType.Edit)
		remove_operators = get_nna_operators(NNAFunctionType.Remove)
		if(len(jsonText) > 2):
			try:
				componentsList = json.loads(jsonText)
				self.layout.label(text="Components")
				col = self.layout.column(heading="Components")
				for idx, component in enumerate(componentsList):
					box = col.box()
					row = box.row()
					row.label(text="Type")
					row.label(text=str(component["t"]))

					if(str(component["t"]) in preview_operators):
						preview_operators[str(component["t"])](box, component)
					else:
						for property in component.keys():
							if(property == "t"): continue
							row = box.row()
							row.label(text=property)
							row.label(text=str(component[property]))

					box.separator(type="LINE", factor=1)
					if(str(component["t"]) in edit_operators):
						row = box.row()
						editButton = row.operator(edit_operators[str(component["t"])], text="Edit")
						editButton.componentIdx = idx
						box.separator(factor=1)
					row = box.row()
					editRawButton = row.operator(EditNNARawJsonComponentOperator.bl_idname, text="Edit Raw Json")
					editRawButton.componentIdx = idx
					if(str(component["t"]) in remove_operators):
						deleteButton = row.operator(remove_operators[str(component["t"])], text="Remove")
						deleteButton.componentIdx = idx
					else:
						deleteButton = row.operator(RemoveNNAJsonComponentOperator.bl_idname, text="Remove")
						deleteButton.componentIdx = idx

					if(idx < len(componentsList) - 1): col.separator(factor=1)
			except ValueError as e:
				self.layout.label(text="Invalid Json: " + str(e))
		else:
			self.layout.label(text="No Component Added")
		
		self.layout.separator(type="LINE", factor=1)
		row = self.layout.row()
		row.prop(bpy.context.scene, "nna_oparators_add", text="")
		row.operator(NNACache[NNAFunctionType.Add][bpy.context.scene.nna_oparators_add], text="Add Component")

		self.layout.separator(factor=1)
		self.layout.operator(EditNNARawJsonOperator.bl_idname, text="Edit Raw Json")

		self.layout.separator(type="LINE", factor=5)
		self.layout.operator(RemoveNNATargetingObjectOperator.bl_idname)
		
		


"""
# TODO Create a new tab in the properties panel
class PropertiesTabTest(bpy.types.Panel):
	bl_idname = "OBJECT_PT_properties_tab_test"
	bl_label = "Properties Tab Test"
	bl_space_type = "PROPERTIES"
	bl_region_type = "NAVIGATION_BAR"

	def draw(self, context):
		self.layout.label(text="Hello World")
"""