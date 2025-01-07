import bpy
import re

from .. import NNA_Json_Add_Base
from .. import NNA_Json_Edit_Base
from .. import NNA_Name_Definition_Base

from ...nna_registry import NNAFunctionType

from ...ops import nna_operators_selector


_nna_name = "nna.twist"


class AddNNATwistComponentOperator(bpy.types.Operator, NNA_Json_Add_Base):
	"""Specifies a twist-bone constraint"""
	bl_idname = "nna.add_nna_twist"
	bl_label = "Add Twist Component"
	nna_name = _nna_name


class EditNNATwistComponentOperator(bpy.types.Operator, NNA_Json_Edit_Base):
	"""Specifies a twist-bone constraint"""
	bl_idname = "nna.edit_nna_twist"
	bl_label = "Edit Twist Component"

	weight: bpy.props.FloatProperty(name="weight", default=0.5, min=0, max=1, precision=2, step=2) # type: ignore

	def parse(self, json_component: dict):
		if("w" in json_component): self.weight = json_component["w"]
		nna_operators_selector.init_selector_relative(self.target_id, json_component.get("s"))

	def serialize(self, json_component: dict) -> dict:
		if(self.weight != 0.5): json_component["w"] = self.weight

		source_id = nna_operators_selector.get_selected_target_id_relative(self.target_id)
		if(source_id):
			json_component["s"] = source_id
		elif("s" in json_component):
			del json_component["s"]

		return json_component

	def draw(self, context):
		self.layout.prop(self, "weight", text="Weight", expand=True)
		self.layout.label(text="Source")
		nna_operators_selector.draw_selector_prop(self.target_id, self.layout)


def display_nna_twist_component(target_id: str, layout: bpy.types.UILayout, json_component: dict, component_index: int):
	row = layout.split(factor=0.4); row.label(text="Weight"); row.label(text=str(json_component.get("w", "default (0.5)")))
	row = layout.split(factor=0.4); row.label(text="Source"); row.label(text=str(json_component.get("s", "default (grandparent)")))


_Match = r"(?i)\$twist(?P<source_node_path>[a-zA-Z][a-zA-Z0-9._\-|:\s]*(\&[a-zA-Z][a-zA-Z0-9._\-|:\s]*)*)?,?(?P<weight>[0-9]*[.][0-9]+)?(?P<side>(([._\-|:][lr])|[._\-|:\s]?(right|left))$)?$"

class NNATwistNameDefinitionOperator(bpy.types.Operator, NNA_Name_Definition_Base):
	"""Specifies a twist-bone constraint"""
	bl_idname = "nna.nna_twist_name_definition"
	bl_label = "NNA Twist Name Definition"

	weight: bpy.props.FloatProperty(name="weight", default=0.5, min=0, max=1, precision=2, step=2) # type: ignore

	def parse(self, nna_name: str):
		match = re.search(_Match, nna_name)
		if(match and match.groupdict()["weight"]): self.weight = float(match.groupdict()["weight"])
		if(match and match.groupdict()["source_node_path"]):
			nna_operators_selector.init_selector_relative(self.target_id, match.groupdict()["source_node_path"], target_split_char="&")
		else:
			nna_operators_selector.init_selector()

	def serialize(self, target: bpy.types.Object | bpy.types.Bone, base_object: bpy.types.Object | None, nna_name: str, symmetry: str) -> str:
		match = re.search(_Match, nna_name)
		if(match): nna_name = nna_name[:match.start()]

		if(self.clear_definition_on_import): nna_name += "$"
		nna_name += "$Twist"

		source_id = nna_operators_selector.get_selected_target_id_relative(self.target_id, target_split_char="&")
		if(source_id):
			nna_name += source_id
			if(self.weight != 0.5): nna_name += ","

		if(self.weight != 0.5): nna_name += str(round(self.weight, 2))

		return nna_name + symmetry

	def draw(self, context):
		NNA_Name_Definition_Base.draw(self, context)

		self.layout.prop(self, "weight", text="Weight", expand=True)
		self.layout.label(text="Source")
		nna_operators_selector.draw_selector_prop(self.target_id, self.layout)

def name_match_nna_twist(name: str) -> int:
	match = re.search(_Match, name)
	return -1 if not match else match.start()

def name_display_nna_twist(layout: bpy.types.UILayout, name: str):
	match = re.search(_Match, name)
	row = layout.split(factor=0.4); row.label(text="Weight"); row.label(text=str(match.groupdict()["weight"]) if match.groupdict()["weight"] else "default (0.5)")
	row = layout.split(factor=0.4); row.label(text="Source"); row.label(text=match.groupdict()["source_node_path"] if match.groupdict()["source_node_path"] else "default (grandparent)")


nna_types = {
	_nna_name: {
		NNAFunctionType.JsonAdd: AddNNATwistComponentOperator.bl_idname,
		NNAFunctionType.JsonEdit: EditNNATwistComponentOperator.bl_idname,
		NNAFunctionType.JsonDisplay: display_nna_twist_component,
		NNAFunctionType.NameSet: NNATwistNameDefinitionOperator.bl_idname,
		NNAFunctionType.NameMatch: name_match_nna_twist,
		NNAFunctionType.NameDisplay: name_display_nna_twist
	},
}
