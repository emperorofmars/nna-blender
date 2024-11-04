import bpy

from . import nna_editor
from .nna_tree_utils import NNAObjectState, determine_nna_bone_state
from . import nna_operators

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
				self.layout.separator(type="LINE", factor=5)
				if(len(bpy.context.scene.collection.children_recursive) == 0):
					button = self.layout.operator(operator=nna_operators.InitializeNNAOperator.bl_idname, text="Initialize NNA in Scene")
					button.nna_init_collection = bpy.context.scene.collection.name
				else:
					button = self.layout.operator(operator=nna_operators.InitializeNNAOperator.bl_idname, text="Initialize NNA in Collection")
					button.nna_init_collection = context.collection.name
			case NNAObjectState.InitedOutsideTree:
				nna_editor.draw_nna_name_editor(self, context, target_id)
				self.layout.separator(type="LINE", factor=5)
				self.layout.label(text="This object is outside the NNA tree!")
			case NNAObjectState.InitedInsideTree:
				nna_editor.draw_nna_name_editor(self, context, target_id)
				self.layout.separator(type="LINE", factor=5)
				button = self.layout.operator(nna_operators.CreateNNATargetingObjectOperator.bl_idname, text="Create NNA Component List")
				button.target_id = target_id
			case NNAObjectState.HasTargetingObject:
				nna_editor.draw_nna_name_editor(self, context, target_id)
				self.layout.separator(type="LINE", factor=5)
				nna_editor.draw_nna_json_editor(self, context, target_id)
		
