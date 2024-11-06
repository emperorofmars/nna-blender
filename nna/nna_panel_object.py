import bpy

from . import nna_editor
from .nna_utils_tree import NNAObjectState, determine_nna_object_state
from . import nna_operators_common

class NNAObjectPanel(bpy.types.Panel):
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
		target_id = context.object.name
		match determine_nna_object_state(context.object):
			case NNAObjectState.IsRootObject:
				button = self.layout.operator(nna_operators_common.CreateNNATargetingObjectOperator.bl_idname, text="Initializie NNA for the Export Root")
				button.target_id = target_id
			case NNAObjectState.IsRootObjectWithTargeting:
				nna_editor.draw_nna_json_editor(self, context, target_id)
			case NNAObjectState.NotInited:
				nna_editor.draw_nna_name_editor(self, context, target_id)
				self.layout.separator(type="LINE", factor=2)
				box = self.layout.box()
				box.label(text="Json Components Not Enabled")
				button = box.operator(operator=nna_operators_common.InitializeNNAOperator.bl_idname)
				button.nna_init_collection = context.collection.name
			case NNAObjectState.InitedOutsideTree:
				nna_editor.draw_nna_name_editor(self, context, target_id)
				self.layout.separator(type="LINE", factor=2)
				box = self.layout.box()
				box.label(text="Json Components Not Enabled")
				box.label(text="This object is outside the NNA tree!")
			case NNAObjectState.InitedInsideTree:
				if(not nna_editor.draw_nna_name_editor(self, context, target_id)):
					self.layout.separator(type="LINE", factor=2)
					box = self.layout.box()
					box.label(text="Json Components Not Enabled")
					button = box.operator(nna_operators_common.CreateNNATargetingObjectOperator.bl_idname)
					button.target_id = target_id
			case NNAObjectState.IsTargetingObject:
				self.layout.label(text="This is the Json definition for: " + ("The Scene Root" if target_id == "$root" else target_id[8:]))
			case NNAObjectState.IsJsonDefinition:
				self.layout.label(text="This part of the Json definition for: " + context.object.parent.name[8:])
			case NNAObjectState.HasTargetingObject:
				if(nna_editor.draw_nna_name_editor(self, context, target_id)):
					box = self.layout.box()
					box.label(text="Warning: This Node has both a Name and Component definition.")
					box.label(text="It is recommended to use only one.")
				nna_editor.draw_nna_json_editor(self, context, target_id)

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