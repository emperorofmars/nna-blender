import re
import bpy

from ...nna_registry import NNAFunctionType

from .. import NNA_Json_Add_Base
from .. import NNA_Json_Edit_Base
from .. import NNA_Name_Definition_Base


_nna_name = "nna.humanoid"


class AddNNAHumanoidComponentOperator(bpy.types.Operator, NNA_Json_Add_Base):
	"""Specifies options for the automapping of the Unity compatible humanoid rig"""
	bl_idname = "nna.add_nna_humanoid"
	bl_label = "Add Humanoid Component"
	nna_name = _nna_name


class EditNNAHumanoidComponentOperator(bpy.types.Operator, NNA_Json_Edit_Base):
	"""Specifies options for the automapping of the Unity compatible humanoid rig"""
	bl_idname = "nna.edit_nna_humanoid"
	bl_label = "Edit Humanoid Component"

	locomotion_type: bpy.props.EnumProperty(items=[("planti", "Plantigrade", ""),("digi", "Digitigrade", "")], name="Locomotion Type", default="planti") # type: ignore
	no_jaw: bpy.props.BoolProperty(name="No Jaw Mapping", default=False) # type: ignore

	def parse(self, json_component: dict):
		if("lc" in json_component): self.locomotion_type = json_component["lc"]
		if("nj" in json_component): self.no_jaw = json_component["nj"]

	def serialize(self, json_component: dict) -> dict:
		if(self.locomotion_type != "planti"): json_component["lc"] = self.locomotion_type
		elif("lc" in json_component): del json_component["lc"]

		if(self.no_jaw == True): json_component["nj"] = True
		elif("nj" in json_component): del json_component["nj"]

		return json_component

	def draw(self, context):
		self.layout.prop(self, "locomotion_type", expand=True)
		self.layout.prop(self, "no_jaw", expand=True)


def display_nna_humanoid_component(target_id: str, layout: bpy.types.UILayout, json_component: dict, component_index: int):
	row = layout.split(factor=0.4)
	row.label(text="Locomotion Type")
	row.label(text=json_component["lc"] if "lc" in json_component else "default (planti)")
	row = layout.split(factor=0.4)
	row.label(text="No Jaw Mapping")
	row.label(text=str(json_component["nj"]) if "nj" in json_component else "default (False)")


_Match = r"(?i)\$humanoid(?P<digi>digi)?(?P<no_jaw>nojaw)?(([._\-|:][lr])|[._\-|:\s]?(right|left))?$"

class NNAHumanoidNameDefinitionOperator(bpy.types.Operator, NNA_Name_Definition_Base):
	"""Specifies options for the automapping of the Unity compatible humanoid rig"""
	bl_idname = "nna.nna_humanoid_name_definition"
	bl_label = "NNA Humanoid Name Definition"

	locomotion_type: bpy.props.EnumProperty(items=[("planti", "Plantigrade", ""),("digi", "Digitigrade", "")], name="Locomotion Type", default="planti") # type: ignore
	no_jaw: bpy.props.BoolProperty(name="No Jaw Mapping", default=False) # type: ignore

	def parse(self, name: str):
		match = re.search(_Match, name)
		if(match):
			if(match.groupdict()["digi"]): self.locomotion_type = "digi"
			if(match.groupdict()["no_jaw"]): self.no_jaw = True

	def serialize(self, target: bpy.types.Object | bpy.types.Bone, base_object: bpy.types.Object | None, nna_name: str, symmetry: str) -> str:
		match = re.search(_Match, nna_name)
		if(match): nna_name = nna_name[:match.start()]

		nna_name += "$Humanoid"

		if(self.locomotion_type != "planti"): nna_name += str(self.locomotion_type).capitalize()
		if(self.no_jaw == True): nna_name += "NoJaw"

		return nna_name + symmetry

	def draw(self, context):
		NNA_Name_Definition_Base.draw(self, context)

		self.layout.label(text="Note: Set the 'locomotion type' to Digitigrade")
		self.layout.label(text="ONLY if your rig itself  is digitigrade!")
		self.layout.prop(self, "locomotion_type", expand=True)

		self.layout.separator(factor=1, type="SPACE")
		self.layout.prop(self, "no_jaw", expand=True)


def name_match_nna_humanoid(name: str) -> int:
	match = re.search(_Match, name)
	return -1 if not match else match.start()

def name_display_nna_humanoid(layout: bpy.types.UILayout, name: str):
	match = re.search(_Match, name)
	row = layout.split(factor=0.4)
	row.label(text="Locomotion Type")
	row.label(text="Digitigrade" if match.groupdict()["digi"] else "default (Plantigrade)")
	row = layout.split(factor=0.4)
	row.label(text="No Jaw Mapping")
	row.label(text="True" if match.groupdict()["no_jaw"] else "False")


nna_types = {
	_nna_name: {
		NNAFunctionType.JsonAdd: AddNNAHumanoidComponentOperator.bl_idname,
		NNAFunctionType.JsonEdit: EditNNAHumanoidComponentOperator.bl_idname,
		NNAFunctionType.JsonDisplay: display_nna_humanoid_component,
		NNAFunctionType.NameSet: NNAHumanoidNameDefinitionOperator.bl_idname,
		NNAFunctionType.NameMatch: name_match_nna_humanoid,
		NNAFunctionType.NameDisplay: name_display_nna_humanoid
	},
}
