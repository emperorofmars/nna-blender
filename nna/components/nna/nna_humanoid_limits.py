import re
import bpy

from ...nna_registry import NNAFunctionType

from ... import nna_utils_json
from ... import nna_utils_name
from ... import nna_utils_tree


_nna_name = "nna.humanoid.limit"

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


class NNAHumanoidLimitNameDefinitionOperator(bpy.types.Operator):
	"""Specifies rotation limits for humanoid bones"""
	bl_idname = "nna.nna_humanoid_limit_name_definition"
	bl_label = "NNA Humanoid Limit Definition"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore

	primary_min: bpy.props.FloatProperty(name="Primary Min", default=0, soft_min=-180, soft_max=0, precision=2, step=2) # type: ignore
	primary_max: bpy.props.FloatProperty(name="Primary Max", default=0, soft_min=0, soft_max=180, precision=2, step=2) # type: ignore
	secondary_min: bpy.props.FloatProperty(name="Secondary Min", default=0, soft_min=-180, soft_max=0, precision=2, step=2) # type: ignore
	secondary_max: bpy.props.FloatProperty(name="Secondary Max", default=0, soft_min=0, soft_max=180, precision=2, step=2) # type: ignore
	twist_min: bpy.props.FloatProperty(name="Twist Min", default=0, soft_min=-180, soft_max=0, precision=2, step=2) # type: ignore
	twist_max: bpy.props.FloatProperty(name="Twist Max", default=0, soft_min=0, soft_max=180, precision=2, step=2) # type: ignore
	bone_length: bpy.props.FloatProperty(name="Bone Length", default=0, min=0, soft_max=10, precision=3, step=2) # type: ignore

	def invoke(self, context, event):
		name = nna_utils_name.get_nna_name(self.target_id)

		limits = parse_limits(name)
		self.primary_min = limits[0][0]
		self.primary_max = limits[1][0]

		self.secondary_min = limits[0][1]
		self.secondary_max = limits[1][1]

		self.twist_min = limits[0][2]
		self.twist_max = limits[1][2]

		self.bone_length = limits[2]

		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		try:
			target = nna_utils_tree.get_object_by_target_id(self.target_id)
			base_object = nna_utils_tree.get_base_object_by_target_id(self.target_id)
			(nna_name, symmetry) = nna_utils_name.get_side_suffix(nna_utils_name.get_nna_name(self.target_id))

			match = re.search(_Match, nna_name)
			if(match): nna_name = nna_name[:match.start()]

			nna_name = nna_name + "$HuLim"

			if(self.primary_min and self.primary_min != None and self.primary_max and self.primary_max != None):
				nna_name += "P" + str(round(self.primary_min, 2)) + "," + str(round(self.primary_max, 2))

			if(self.secondary_min and self.secondary_min != None and self.secondary_max and self.secondary_max != None):
				nna_name += "S" + str(round(self.secondary_min, 2)) + "," + str(round(self.secondary_max, 2))

			if(self.twist_min and self.twist_min != None and self.twist_max and self.twist_max != None):
				nna_name += "T" + str(round(self.twist_min, 2)) + "," + str(round(self.twist_max, 2))

			if(self.bone_length and self.bone_length != None):
				nna_name += "BL" + str(round(self.bone_length, 2))

			nna_name += symmetry

			if(len(str.encode(nna_name)) > 63):
				self.report({'ERROR'}, "Name too long")
				return {"CANCELLED"}
			else:
				nna_utils_tree.reparent_nna_targeting_object(self.target_id, nna_utils_name.construct_nna_id(self.target_id, nna_name))
				target.name = nna_name
				self.report({'INFO'}, "Component successfully edited")
				return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}

	def draw(self, context):
		split = self.layout.split(factor=0.4); split.label(text = "Primary")
		col = split.column(); col.prop(self, "primary_min", text="Min", expand=True); col.prop(self, "primary_max", text="Max", expand=True)
		self.layout.separator(factor=0.5)

		split = self.layout.split(factor=0.4); split.label(text = "Secondary")
		col = split.column(); col.prop(self, "secondary_min", text="Min", expand=True); col.prop(self, "secondary_max", text="Max", expand=True)
		self.layout.separator(factor=0.5)

		split = self.layout.split(factor=0.4); split.label(text = "Twist")
		col = split.column(); col.prop(self, "twist_min", text="Min", expand=True); col.prop(self, "twist_max", text="Max", expand=True)
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
		NNAFunctionType.NameSet: NNAHumanoidLimitNameDefinitionOperator.bl_idname,
		NNAFunctionType.NameMatch: name_match_nna_humanoid_limit,
		NNAFunctionType.NameDisplay: name_display_nna_humanoid_limit
	},
}
