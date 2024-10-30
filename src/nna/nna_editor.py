import bpy
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
		self.layout.label(text="Edit Raw NNA Json")
		self.layout.prop(context.object, "nna_json", text="", expand=True)

		button = self.layout.operator(CommitNNAJsonChangesOperator.bl_idname, text="Commit Changes")
		button.target = context.object.name
		button.json = context.object.nna_json

		resetButton = self.layout.operator(ResetNNAJsonOperator.bl_idname, text="Reset")
		resetButton.target = context.object.name

def msgbus_callback_set_json(*arg):
	match determineNNAObjectState(bpy.context.active_object):
		case NNAObjectState.HasTargetingObject:
			json = getJsonFromTargetingObject(findNNATargetingObject(bpy.context.active_object.name))
			bpy.context.active_object.nna_json = json
		case _:
			bpy.context.active_object.nna_json = ""

def register():
	bpy.types.Object.nna_json = bpy.props.StringProperty(name="nna_json")
	bpy.msgbus.subscribe_rna(key=(bpy.types.LayerObjects, "active"), owner="NNA", args=("",), notify=msgbus_callback_set_json)

def unregister():
	del bpy.types.Object.nna_json
	bpy.msgbus.clear_by_owner("NNA")


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