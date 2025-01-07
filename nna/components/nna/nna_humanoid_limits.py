import re
import bpy

from ...nna_registry import NNAFunctionType

from .. import NNA_Json_Add_Base
from .. import NNA_Json_Edit_Base
from .. import NNA_Name_Definition_Base


_nna_name = "nna.humanoid.limits"


class AddNNAHumanoidLimitComponentOperator(bpy.types.Operator, NNA_Json_Add_Base):
	"""Specifies rotation limits for a humanoid bone"""
	bl_idname = "nna.add_nna_humanoid_limits"
	bl_label = "Add Humanoid Limits Component"
	nna_name = _nna_name


class EditNNAHumanoidComponentOperator(bpy.types.Operator, NNA_Json_Edit_Base):
	"""Specifies rotation limits for a humanoid bone"""
	bl_idname = "nna.edit_nna_humanoid_limits"
	bl_label = "Edit Humanoid Limits Component"

	p_min: bpy.props.FloatProperty(name="Primary Min", default=0, soft_min=-180, soft_max=0, precision=2, step=2) # type: ignore
	p_max: bpy.props.FloatProperty(name="Primary Max", default=0, soft_min=0, soft_max=180, precision=2, step=2) # type: ignore
	s_min: bpy.props.FloatProperty(name="Secondary Min", default=0, soft_min=-180, soft_max=0, precision=2, step=2) # type: ignore
	s_max: bpy.props.FloatProperty(name="Secondary Max", default=0, soft_min=0, soft_max=180, precision=2, step=2) # type: ignore
	t_min: bpy.props.FloatProperty(name="Twist Min", default=0, soft_min=-180, soft_max=0, precision=2, step=2) # type: ignore
	t_max: bpy.props.FloatProperty(name="Twist Max", default=0, soft_min=0, soft_max=180, precision=2, step=2) # type: ignore
	bone_length: bpy.props.FloatProperty(name="Bone Length", default=0, min=0, soft_max=10, precision=3, step=2) # type: ignore

	def parse(self, json_component: dict):
		if("p_min" in json_component): self.p_min = json_component["p_min"]
		if("p_max" in json_component): self.p_max = json_component["p_max"]
		if("s_min" in json_component): self.s_min = json_component["s_min"]
		if("s_max" in json_component): self.s_max = json_component["s_max"]
		if("t_min" in json_component): self.t_min = json_component["t_min"]
		if("t_max" in json_component): self.t_max = json_component["t_max"]
		if("bone_length" in json_component): self.bone_length = json_component["bone_length"]

	def serialize(self, json_component: dict) -> dict:
		if(self.p_min and self.p_min != None and self.p_max and self.p_max != None):
			json_component["p_min"] = self.p_min
			json_component["p_max"] = self.p_max
		else:
			if("p_min" in json_component): del json_component["p_min"]
			if("p_max" in json_component): del json_component["p_max"]

		if(self.s_min and self.s_min != None and self.s_max and self.s_max != None):
			json_component["s_min"] = self.s_min
			json_component["s_max"] = self.s_max
		else:
			if("s_min" in json_component): del json_component["s_min"]
			if("s_max" in json_component): del json_component["s_max"]

		if(self.t_min and self.t_min != None and self.t_max and self.t_max != None):
			json_component["t_min"] = self.s_min
			json_component["t_max"] = self.s_max
		else:
			if("t_min" in json_component): del json_component["t_min"]
			if("t_max" in json_component): del json_component["t_max"]

		if(self.bone_length and self.bone_length != None):
			json_component["bone_length"] = self.bone_length
		else:
			if("bone_length" in json_component): del json_component["bone_length"]

		return json_component

	def draw(self, context):
		split = self.layout.split(factor=0.4); split.label(text = "Primary")
		col = split.column(); col.prop(self, "p_min", text="Min", expand=True); col.prop(self, "p_max", text="Max", expand=True)
		self.layout.separator(factor=0.5)

		split = self.layout.split(factor=0.4); split.label(text = "Secondary")
		col = split.column(); col.prop(self, "s_min", text="Min", expand=True); col.prop(self, "s_max", text="Max", expand=True)
		self.layout.separator(factor=0.5)

		split = self.layout.split(factor=0.4); split.label(text = "Twist")
		col = split.column(); col.prop(self, "t_min", text="Min", expand=True); col.prop(self, "t_max", text="Max", expand=True)
		self.layout.separator(factor=0.5)

		self.layout.prop(self, "bone_length", expand=True)


def display_nna_humanoid_limits_component(target_id: str, layout: bpy.types.UILayout, json_component: dict, component_index: int):
	if("p_min" in json_component and "p_max" in json_component):
		row = layout.split(factor=0.4); row.label(text="Primary"); row.label(text=str(json_component["p_min"]) + "  -  " + str(json_component["p_max"]))
	if("s_min" in json_component and "s_max" in json_component):
		row = layout.split(factor=0.4); row.label(text="Secondary"); row.label(text=str(json_component["s_min"]) + "  -  " + str(json_component["s_max"]))
	if("t_min" in json_component and "t_max" in json_component):
		row = layout.split(factor=0.4); row.label(text="Twist"); row.label(text=str(json_component["t_min"]) + "  -  " + str(json_component["t_max"]))
	if("bone_length" in json_component):
		row = layout.split(factor=0.4); row.label(text="Bone Length"); row.label(text=str(json_component["bone_length"]))



_Match = r"(?i)\$HuLim(?P<primary>[P][-]?[0-9]+([.][0-9]*)?,[-]?[0-9]+([.][0-9]*)?)?(?P<secondary>[S][-]?[0-9]+([.][0-9]*)?,[-]?[0-9]+([.][0-9]*)?)?(?P<twist>[T][-]?[0-9]+([.][0-9]*)?,[-]?[0-9]+([.][0-9]*)?)?(?P<bone_length>BL[0-9]*([.][0-9]+)?)?(?P<side>([._\-|:][lr])|[._\-|:\s]?(right|left))?$"
_MatchLimit = r"(?i)(?P<axis>[PST]+)(?P<min>[-]?[0-9]*([.][0-9]+)?),(?P<max>[-]?[0-9]*([.][0-9]+)?)"

def parse_limits(name: str) -> tuple[list[float], list[float], float]:
	match = re.search(_Match, name)

	limits_max = [0, 0, 0]
	limits_min = [0, 0, 0]

	if(match.groupdict()["primary"]):
		match_axis = re.search(_MatchLimit, match.groupdict()["primary"])
		limits_min[0] = float(match_axis.groupdict()["min"])
		limits_max[0] = float(match_axis.groupdict()["max"])

	if(match.groupdict()["secondary"]):
		match_axis = re.search(_MatchLimit, match.groupdict()["secondary"])
		limits_min[1] = float(match_axis.groupdict()["min"])
		limits_max[1] = float(match_axis.groupdict()["max"])

	if(match.groupdict()["twist"]):
		match_axis = re.search(_MatchLimit, match.groupdict()["twist"])
		limits_min[2] = float(match_axis.groupdict()["min"])
		limits_max[2] = float(match_axis.groupdict()["max"])

	bone_length = float(match.groupdict()["bone_length"][2:]) if match.groupdict()["bone_length"] else 0

	return (limits_min, limits_max, bone_length)


class NNAHumanoidLimitNameDefinitionOperator(bpy.types.Operator, NNA_Name_Definition_Base):
	"""Specifies rotation limits for a humanoid bone"""
	bl_idname = "nna.nna_humanoid_limits_name_definition"
	bl_label = "NNA Humanoid Limits Definition"

	p_min: bpy.props.FloatProperty(name="Primary Min", default=0, soft_min=-180, soft_max=0, precision=2, step=2) # type: ignore
	p_max: bpy.props.FloatProperty(name="Primary Max", default=0, soft_min=0, soft_max=180, precision=2, step=2) # type: ignore
	s_min: bpy.props.FloatProperty(name="Secondary Min", default=0, soft_min=-180, soft_max=0, precision=2, step=2) # type: ignore
	s_max: bpy.props.FloatProperty(name="Secondary Max", default=0, soft_min=0, soft_max=180, precision=2, step=2) # type: ignore
	t_min: bpy.props.FloatProperty(name="Twist Min", default=0, soft_min=-180, soft_max=0, precision=2, step=2) # type: ignore
	t_max: bpy.props.FloatProperty(name="Twist Max", default=0, soft_min=0, soft_max=180, precision=2, step=2) # type: ignore
	bone_length: bpy.props.FloatProperty(name="Bone Length", default=0, min=0, soft_max=10, precision=3, step=2) # type: ignore

	def parse(self, name: str):
		limits = parse_limits(name)
		self.p_min = limits[0][0]
		self.p_max = limits[1][0]

		self.s_min = limits[0][1]
		self.s_max = limits[1][1]

		self.t_min = limits[0][2]
		self.t_max = limits[1][2]

		self.bone_length = limits[2]

	def serialize(self, target: bpy.types.Object | bpy.types.Bone, base_object: bpy.types.Object | None, nna_name: str, symmetry: str) -> str:
		match = re.search(_Match, nna_name)
		if(match): nna_name = nna_name[:match.start()]

		nna_name += "$HuLim"

		if(self.p_min and self.p_min != None and self.p_max and self.p_max != None):
			nna_name += "P" + str(round(self.p_min, 2)) + "," + str(round(self.p_max, 2))

		if(self.s_min and self.s_min != None and self.s_max and self.s_max != None):
			nna_name += "S" + str(round(self.s_min, 2)) + "," + str(round(self.s_max, 2))

		if(self.t_min and self.t_min != None and self.t_max and self.t_max != None):
			nna_name += "T" + str(round(self.t_min, 2)) + "," + str(round(self.t_max, 2))

		if(self.bone_length and self.bone_length != None):
			nna_name += "BL" + str(round(self.bone_length, 2))

		return nna_name + symmetry

	def draw(self, context):
		NNA_Name_Definition_Base.draw(self, context)

		split = self.layout.split(factor=0.4); split.label(text = "Primary")
		col = split.column(); col.prop(self, "p_min", text="Min", expand=True); col.prop(self, "p_max", text="Max", expand=True)
		self.layout.separator(factor=0.5)

		split = self.layout.split(factor=0.4); split.label(text = "Secondary")
		col = split.column(); col.prop(self, "s_min", text="Min", expand=True); col.prop(self, "s_max", text="Max", expand=True)
		self.layout.separator(factor=0.5)

		split = self.layout.split(factor=0.4); split.label(text = "Twist")
		col = split.column(); col.prop(self, "t_min", text="Min", expand=True); col.prop(self, "t_max", text="Max", expand=True)
		self.layout.separator(factor=0.5)

		self.layout.prop(self, "bone_length", expand=True)


def name_match_nna_humanoid_limit(name: str) -> int:
	match = re.search(_Match, name)
	return -1 if not match else match.start()

def name_display_nna_humanoid_limit(layout: bpy.types.UILayout, name: str):
	limits = parse_limits(name)

	if(limits[0][0] and limits[1][0]):
		row = layout.split(factor=0.4); row.label(text="Primary"); row.label(text=str(limits[0][0]) + "  -  " + str(limits[1][0]))
	if(limits[0][1] and limits[1][1]):
		row = layout.split(factor=0.4); row.label(text="Secondary"); row.label(text=str(limits[0][1]) + "  -  " + str(limits[1][1]))
	if(limits[0][2] and limits[1][2]):
		row = layout.split(factor=0.4); row.label(text="Twist"); row.label(text=str(limits[0][2]) + "  -  " + str(limits[1][2]))

	if(limits[2]):
		row = layout.split(factor=0.4); row.label(text="Bone Length"); row.label(text=str(limits[2]))


nna_types = {
	_nna_name: {
		NNAFunctionType.JsonAdd: AddNNAHumanoidLimitComponentOperator.bl_idname,
		NNAFunctionType.JsonEdit: EditNNAHumanoidComponentOperator.bl_idname,
		NNAFunctionType.JsonDisplay: display_nna_humanoid_limits_component,
		NNAFunctionType.NameSet: NNAHumanoidLimitNameDefinitionOperator.bl_idname,
		NNAFunctionType.NameMatch: name_match_nna_humanoid_limit,
		NNAFunctionType.NameDisplay: name_display_nna_humanoid_limit,
	},
}
