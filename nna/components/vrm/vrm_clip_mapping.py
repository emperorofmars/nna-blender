import bpy

from .. import NNA_Json_Add_Base, NNA_Json_Edit_Base
from ...utils.nna_list import edit_list
from ...nna_registry import NNAFunctionType


_nna_name = "vrm.clip_mapping"


class AddVRMClipMappingComponentOperator(bpy.types.Operator, NNA_Json_Add_Base):
	"""Map the names of VRM Clips to be mapped in the game-engine"""
	bl_idname = "vrm.add_vrm_clip_mapping"
	bl_label = "Add VRM Clip Mapping Component"

	def init(self) -> dict:
		return {
			"t": _nna_name,
			"clips": []
		}


class EditVRMClipMappingComponentOperator(bpy.types.Operator, NNA_Json_Edit_Base):
	"""Map the names of VRM Clips to be mapped in the game-engine"""
	bl_idname = "vrm.edit_vrm_clip_mapping"
	bl_label = "Edit VRM Clip Mapping Component"

	def parse(self, json_component: dict):
		bpy.context.scene.nna_list.clear()

		for clip in json_component.get("clips", []):
			entry = bpy.context.scene.nna_list.add()
			entry.value = clip

	def serialize(self, json_component: dict) -> dict:
		json_component["clips"] = []
		for entry in bpy.context.scene.nna_list:
			json_component["clips"].append(entry.value)
		return json_component

	def draw(self, context):
		edit_list(self, context)


def display_vrm_clip_mapping_component(target_id: str, layout: bpy.types.UILayout, json_component: dict, component_index: int):
	layout.label(text="Clip Filename Mappings")
	for clip in json_component.get("clips", []):
		layout.label(text=clip)


nna_types = {
	_nna_name: {
		NNAFunctionType.JsonAdd: AddVRMClipMappingComponentOperator.bl_idname,
		NNAFunctionType.JsonEdit: EditVRMClipMappingComponentOperator.bl_idname,
		NNAFunctionType.JsonDisplay: display_vrm_clip_mapping_component,
	},
}
