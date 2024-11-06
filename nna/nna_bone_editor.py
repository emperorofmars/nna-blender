import bpy

from . import nna_editor
from .nna_tree_utils import NNAObjectState, determine_nna_bone_state
from . import nna_operators_common

class NNABoneEditor(bpy.types.Panel):
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
		target_id = context.object.name + "$" + context.bone.name
		match determine_nna_bone_state(context.object, context.bone):
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
			case NNAObjectState.HasTargetingObject:
				nna_editor.draw_nna_json_editor(self, context, target_id)
		
