import re
import bpy

from ...nna_registry import NNAFunctionType
from ...nna_operators_util import CreateNewObjectOperator, SetActiveObjectOperator

from ... import nna_utils_name
from ... import nna_utils_json
from ... import nna_utils_tree


_nna_name = "ava.eyetracking_bone_limits"


class AddAVAEyetrackingBoneLimitsComponentOperator(bpy.types.Operator):
	"""Set the rotation limits for the avatars eye-bones in degrees.
	The avatar must be satisfy the Unity humanoid requirements"""

	bl_idname = "ava.add_ava_eyetracking_bone_limits"
	bl_label = "Add AVA Eyetracking Bone Limits Component"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore

	def execute(self, context):
		try:
			nna_utils_json.add_component(self.target_id, {
				"t": _nna_name,
				"left_up": 15.,
				"left_down": 12.,
				"left_in": 15.,
				"left_out": 16.,
				"linked": True,
			})
			self.report({'INFO'}, "Component successfully added")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}


class EditAVAEyetrackingBoneLimitsComponentOperator(bpy.types.Operator):
	"""Set the rotation limits for the avatars eye-bones in degrees.
	The avatar must be satisfy the Unity humanoid requirements"""

	bl_idname = "nna.edit_ava_eyetracking_bone_limits"
	bl_label = "Edit AVA Eyetracking Bone Limits Component"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	component_index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore

	left_up: bpy.props.FloatProperty(name="Left Up", default=15, min=0, soft_min=4, max=90, soft_max=30, precision=2, step=2) # type: ignore
	left_down: bpy.props.FloatProperty(name="Left Down", default=12, min=0, soft_min=4, max=90, soft_max=30, precision=2, step=2) # type: ignore
	left_in: bpy.props.FloatProperty(name="Left In", default=15, min=0, soft_min=4, max=90, soft_max=30, precision=2, step=2) # type: ignore
	left_out: bpy.props.FloatProperty(name="Left Out", default=16, min=0, soft_min=4, max=90, soft_max=30, precision=2, step=2) # type: ignore

	linked: bpy.props.BoolProperty(name="Linked", default=True) # type: ignore

	right_up: bpy.props.FloatProperty(name="Right Up", default=15, min=0, soft_min=4, max=90, soft_max=30, precision=2, step=2) # type: ignore
	right_down: bpy.props.FloatProperty(name="Right Down", default=12, min=0, soft_min=4, max=90, soft_max=30, precision=2, step=2) # type: ignore
	right_in: bpy.props.FloatProperty(name="Right In", default=15, min=0, soft_min=4, max=90, soft_max=30, precision=2, step=2) # type: ignore
	right_out: bpy.props.FloatProperty(name="Right Out", default=16, min=0, soft_min=4, max=90, soft_max=30, precision=2, step=2) # type: ignore

	def invoke(self, context, event):
		json_component = nna_utils_json.get_component(self.target_id, self.component_index)

		if("left_up" in json_component): self.left_up = json_component["left_up"]
		if("left_down" in json_component): self.left_down = json_component["left_down"]
		if("left_in" in json_component): self.left_in = json_component["left_in"]
		if("left_out" in json_component): self.left_out = json_component["left_out"]

		if("linked" in json_component): self.linked = json_component["linked"]

		if("right_up" in json_component): self.right_up = json_component["right_up"]
		if("right_down" in json_component): self.right_down = json_component["right_down"]
		if("right_in" in json_component): self.right_in = json_component["right_in"]
		if("right_out" in json_component): self.right_out = json_component["right_out"]

		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		try:
			json_component = nna_utils_json.get_component(self.target_id, self.component_index)

			json_component["left_up"] = round(self.left_up, 2)
			json_component["left_down"] = round(self.left_down, 2)
			json_component["left_in"] = round(self.left_in, 2)
			json_component["left_out"] = round(self.left_out, 2)

			json_component["linked"] = self.linked

			if(not self.linked):
				json_component["right_up"] = round(self.right_up, 2)
				json_component["right_down"] = round(self.right_down, 2)
				json_component["right_in"] = round(self.right_in, 2)
				json_component["right_out"] = round(self.right_out, 2)

			nna_utils_json.replace_component(self.target_id, json_component, self.component_index)
			self.report({'INFO'}, "Component successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}

	def draw(self, context):
		self.layout.prop(self, "linked", expand=True)

		self.layout.prop(self, "left_up", expand=True)
		self.layout.prop(self, "left_down", expand=True)
		self.layout.prop(self, "left_in", expand=True)
		self.layout.prop(self, "left_out", expand=True)

		if(not self.linked):
			self.layout.prop(self, "right_up", expand=True)
			self.layout.prop(self, "right_down", expand=True)
			self.layout.prop(self, "right_in", expand=True)
			self.layout.prop(self, "right_out", expand=True)


def display_ava_eyetracking_bone_limits_component(target_id: str, layout: bpy.types.UILayout, json_component: dict, component_index: int):
	row = layout.split(factor=0.4); row.label(text="Linked"); row.label(text=str(json_component["linked"]))
	side_str = ""
	if(not json_component["linked"]): side_str = "Left "
	row = layout.split(factor=0.4); row.label(text=side_str + "Up"); row.label(text=str(json_component["left_up"]))
	row = layout.split(factor=0.4); row.label(text=side_str + "Down"); row.label(text=str(json_component["left_down"]))
	row = layout.split(factor=0.4); row.label(text=side_str + "In"); row.label(text=str(json_component["left_in"]))
	row = layout.split(factor=0.4); row.label(text=side_str + "Out"); row.label(text=str(json_component["left_out"]))
	if(not json_component["linked"]):
		side_str = "Right "
		row = layout.split(factor=0.4); row.label(text=side_str + "Up"); row.label(text=str(json_component["right_up"]))
		row = layout.split(factor=0.4); row.label(text=side_str + "Down"); row.label(text=str(json_component["right_down"]))
		row = layout.split(factor=0.4); row.label(text=side_str + "In"); row.label(text=str(json_component["right_in"]))
		row = layout.split(factor=0.4); row.label(text=side_str + "Out"); row.label(text=str(json_component["right_out"]))


class SetAVAEyetrackingBoneLimitsNameDefinitionOperator(bpy.types.Operator):
	"""Set the rotation limits for the avatars eye-bones in degrees.
	The avatar must be satisfy the Unity humanoid requirements"""

	bl_idname = "nna.set_ava_eyetracking_bone_limits_name"
	bl_label = "AVA Eye Bone Rotation Limits"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore

	up: bpy.props.FloatProperty(name="Up", default=15, min=0, soft_min=4, max=90, soft_max=30, precision=2, step=2) # type: ignore
	down: bpy.props.FloatProperty(name="Down", default=12, min=0, soft_min=4, max=90, soft_max=30, precision=2, step=2) # type: ignore
	inner: bpy.props.FloatProperty(name="In", default=15, min=0, soft_min=4, max=90, soft_max=30, precision=2, step=2) # type: ignore
	outer: bpy.props.FloatProperty(name="Out", default=16, min=0, soft_min=4, max=90, soft_max=30, precision=2, step=2) # type: ignore

	side_changable: bpy.props.BoolProperty(default=True) # type: ignore
	side: bpy.props.EnumProperty(name="Side", items=[("_", "Both", ""),(".L", "Left", ""),(".R", "Right", "")], default=0) # type: ignore

	def invoke(self, context, event):
		nna_name = nna_utils_name.get_nna_name(self.target_id)
		#target = nna_utils_tree.get_object_by_target_id(self.target_id)
		match(nna_utils_name.detect_side(nna_name)):
			case nna_utils_name.SymmetrySide.Both: self.side = "_"; self.side_changable = True
			case nna_utils_name.SymmetrySide.Left: self.side = ".L"; self.side_changable = False
			case nna_utils_name.SymmetrySide.Right: self.side = ".R"; self.side_changable = False

		match = re.search(_Match, nna_name)
		if(match):
			if(match.groupdict()["up"]): self.up = float(match.groupdict()["up"])
			if(match.groupdict()["down"]): self.down = float(match.groupdict()["down"])
			if(match.groupdict()["in"]): self.inner = float(match.groupdict()["in"])
			if(match.groupdict()["out"]): self.outer = float(match.groupdict()["out"])

		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		try:
			target = nna_utils_tree.get_object_by_target_id(self.target_id)
			(nna_name, symmetry) = nna_utils_name.get_symmetry(nna_utils_name.get_nna_name(self.target_id))

			match = re.search(_Match, nna_name)
			if(match): nna_name = nna_name[:match.start()]

			nna_name = nna_name + "$EyeBoneLimits" + str(round(self.up, 2)) + "," + str(round(self.down, 2)) + "," + str(round(self.inner, 2)) + "," + str(round(self.outer, 2))

			if(self.side_changable and self.side != "_"): target.name += self.side
			else: nna_name += symmetry

			if(len(str.encode(nna_name)) > 63):
				self.report({'ERROR'}, "Name too long")
				return {"CANCELLED"}
			else:
				target.name = nna_name
				self.report({'INFO'}, "Component successfully edited")
				return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}

	def draw(self, context):
		if(self.side_changable): self.layout.prop(self, "side", expand=True)
		self.layout.prop(self, "up", expand=True)
		self.layout.prop(self, "down", expand=True)
		self.layout.prop(self, "inner", expand=True)
		self.layout.prop(self, "outer", expand=True)


_Match = r"(?i)\$EyeBoneLimits(?P<up>[0-9]*[.][0-9]+),(?P<down>[0-9]*[.][0-9]+),(?P<in>[0-9]*[.][0-9]+),(?P<out>[0-9]*[.][0-9]+)(?P<side>([._\-|:][lr])|[._\-|:\s]?(right|left))?$"

def name_match_ava_eyetracking_bone_limits(name: str) -> int:
	match = re.search(_Match, name)
	return -1 if not match else match.start()

def name_display_ava_eyetracking_bone_limits(layout: bpy.types.UILayout, name: str):
	match = re.search(_Match, name)
	if(match.groupdict()["side"]):
		side = nna_utils_name.detect_side(name)
		row = layout.row(); row.label(text="Limits for the " + str(side) + " eye.")
	else:
		row = layout.row(); row.label(text="Limits for both eyes.")
	row = layout.row(); row.label(text="Up"); row.label(text=match.groupdict()["up"])
	row = layout.row(); row.label(text="Down"); row.label(text=match.groupdict()["down"])
	row = layout.row(); row.label(text="In"); row.label(text=match.groupdict()["in"])
	row = layout.row(); row.label(text="Out"); row.label(text=match.groupdict()["out"])


nna_types = {
	_nna_name: {
		NNAFunctionType.JsonAdd: AddAVAEyetrackingBoneLimitsComponentOperator.bl_idname,
		NNAFunctionType.JsonEdit: EditAVAEyetrackingBoneLimitsComponentOperator.bl_idname,
		NNAFunctionType.JsonDisplay: display_ava_eyetracking_bone_limits_component,
		NNAFunctionType.NameSet: SetAVAEyetrackingBoneLimitsNameDefinitionOperator.bl_idname,
		NNAFunctionType.NameMatch: name_match_ava_eyetracking_bone_limits,
		NNAFunctionType.NameDisplay: name_display_ava_eyetracking_bone_limits,
	},
}
