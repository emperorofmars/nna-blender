import bpy
import json
from .nna_tree_utils import *
from .nna_operators import *
from .nna_json_utils import *

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
		match determineNNAObjectState(context.object):
			case NNAObjectState.IsRootObject:
				self.layout.label(text="This is the NNA Root")
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
				self.layout.label(text="This is the Component definition for: " + context.object.name[8:])
			case NNAObjectState.IsJsonDefinition:
				self.layout.label(text="This part of the Json definition for: " + context.object.parent.name[8:])
			case NNAObjectState.HasTargetingObject:
				self.drawNNAEditor(context)
	
	def drawNNAEditor(self, context):
		jsonText = getJsonFromTargetName(context.object.name)
		if(len(jsonText) > 0):
			try:
				componentsList = json.loads(jsonText)
				self.layout.label(text="Components")
				col = self.layout.column(heading="Components")
				for idx, component in enumerate(componentsList):
					box = col.box()
					row = box.row()
					row.label(text="Type")
					row.label(text=str(component["t"]))
					for property in component.keys():
						if(property == "t"): continue
						row = box.row()
						row.label(text=property)
						row.label(text=str(component[property]))

					btnRow = col.row()
					editButton = btnRow.operator(EditNNARawJsonComponentOperator.bl_idname, text="Edit")
					editButton.componentIdx = idx
					deleteButton = btnRow.operator(RemoveNNAJsonComponentOperator.bl_idname, text="Remove")
					deleteButton.componentIdx = idx

					if(idx < len(componentsList) - 1): col.separator(factor=2)
			except ValueError as e:
				self.layout.label(text="Invalid Json: " + str(e))
		else:
			self.layout.label(text="No Component Added")
		
		self.layout.separator(factor=2)
		self.layout.operator(AddNNARawJsonComponentOperator.bl_idname, text="Add Component")

		self.layout.separator(type="LINE", factor=5)
		self.layout.operator(EditNNARawJsonOperator.bl_idname)


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