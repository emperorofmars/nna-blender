import re
import bpy

from ...nna_registry import NNAFunctionType

from ..base_add_json import NNA_Json_Add_Base
from ..base_edit_json import NNA_Json_Edit_Base
from ..base_edit_name import NNA_Name_Definition_Base


_nna_name = "nna.bone_length"

class AddNNABoneLengthComponentOperator(bpy.types.Operator, NNA_Json_Add_Base):
	"""Specifies the length of a bone"""
	bl_idname = "nna.add_nna_bone_length"
	bl_label = "Add Bone Length"

	def init(self) -> dict:
		return {"t":self.nna_name,"length":0}


class EditNNABoneLengthComponentOperator(bpy.types.Operator, NNA_Json_Edit_Base):
	"""Specifies the length of a bone"""
	bl_idname = "nna.edit_nna_bone_length"
	bl_label = "Add Bone Length"

	length: bpy.props.FloatProperty(name="Length", default=0, min=0, soft_max=10, precision=3, step=2) # type: ignore

	def parse(self, json_component: dict):
		if("length" in json_component): self.length = json_component["length"]

	def serialize(self, json_component: dict) -> dict:
		json_component["length"] = self.length
		return json_component


def display_nna_bone_length_component(target_id: str, layout: bpy.types.UILayout, json_component: dict, component_index: int):
	row = layout.split(factor=0.4)
	row.label(text="Length")
	row.label(text=str(json_component["length"]))



_Match = r"(?i)\$BoneLen(?P<length>[0-9]*([.][0-9]+)?)(?P<side>([._\-|:][lr])|[._\-|:\s]?(right|left))?$"

class NNABoneLengthNameDefinitionOperator(bpy.types.Operator, NNA_Name_Definition_Base):
	"""Specifies the length of a bone"""
	bl_idname = "nna.nna_bone_length_name_definition"
	bl_label = "Add Bone Length"

	length: bpy.props.FloatProperty(name="Length", default=0.12, min=0, soft_max=10, precision=3, step=2) # type: ignore

	def parse(self, name: str):
		match = re.search(_Match, name)
		if(match):
			self.length = float(match.groupdict()["length"])

	def serialize(self, target: bpy.types.Object | bpy.types.Bone, base_object: bpy.types.Object | None, nna_name: str, symmetry: str) -> str:
			match = re.search(_Match, nna_name)
			if(match): nna_name = nna_name[:match.start()]
			nna_name = nna_name + "$BoneLen" + str(round(self.length, 3))
			return nna_name + symmetry

	def draw(self, context):
		self.layout.prop(self, "length", expand=True)

def name_match_nna_bone_length(name: str) -> int:
	match = re.search(_Match, name)
	return -1 if not match else match.start()

def name_display_nna_bone_length(layout: bpy.types.UILayout, name: str):
	match = re.search(_Match, name)
	row = layout.split(factor=0.4); row.label(text="Length"); row.label(text=match.groupdict()["length"])


nna_types = {
	_nna_name: {
		NNAFunctionType.JsonAdd: AddNNABoneLengthComponentOperator.bl_idname,
		NNAFunctionType.JsonEdit: EditNNABoneLengthComponentOperator.bl_idname,
		NNAFunctionType.JsonDisplay: display_nna_bone_length_component,
		NNAFunctionType.NameSet: NNABoneLengthNameDefinitionOperator.bl_idname,
		NNAFunctionType.NameMatch: name_match_nna_bone_length,
		NNAFunctionType.NameDisplay: name_display_nna_bone_length
	},
}
