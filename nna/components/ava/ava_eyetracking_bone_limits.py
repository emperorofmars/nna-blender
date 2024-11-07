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
				"up": 15.,
				"down": 12.,
				"in": 15.,
				"out": 16.,
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

	up: bpy.props.FloatProperty(name="Up", default=15, min=0, soft_min=4, max=90, soft_max=30, precision=2, step=2) # type: ignore
	down: bpy.props.FloatProperty(name="Down", default=12, min=0, soft_min=4, max=90, soft_max=30, precision=2, step=2) # type: ignore
	inner: bpy.props.FloatProperty(name="In", default=15, min=0, soft_min=4, max=90, soft_max=30, precision=2, step=2) # type: ignore
	outer: bpy.props.FloatProperty(name="Out", default=16, min=0, soft_min=4, max=90, soft_max=30, precision=2, step=2) # type: ignore
	
	def invoke(self, context, event):
		json_component = nna_utils_json.get_component(self.target_id, self.component_index)

		if("up" in json_component): self.up = json_component["up"]
		if("down" in json_component): self.down = json_component["down"]
		if("in" in json_component): self.inner = json_component["in"]
		if("out" in json_component): self.outer = json_component["out"]

		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			json_component = nna_utils_json.get_component(self.target_id, self.component_index)
			
			json_component["up"] = round(self.up, 2)
			json_component["down"] = round(self.down, 2)
			json_component["in"] = round(self.inner, 2)
			json_component["out"] = round(self.outer, 2)

			nna_utils_json.replace_component(self.target_id, json_component, self.component_index)
			self.report({'INFO'}, "Component successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.prop(self, "up", expand=True)
		self.layout.prop(self, "down", expand=True)
		self.layout.prop(self, "inner", expand=True)
		self.layout.prop(self, "outer", expand=True)


def display_ava_eyetracking_bone_limits_component(object, layout, json_component):
	row = layout.row(); row.label(text="Up"); row.label(text=str(json_component["up"]))
	row = layout.row(); row.label(text="Down"); row.label(text=str(json_component["down"]))
	row = layout.row(); row.label(text="In"); row.label(text=str(json_component["in"]))
	row = layout.row(); row.label(text="Out"); row.label(text=str(json_component["out"]))


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
		target = nna_utils_tree.get_object_by_target_id(self.target_id)
		match(nna_utils_name.detect_symmetry(nna_utils_name.get_nna_name(self.target_id))):
			case nna_utils_name.SymmetrySide.Both: self.side = "_"; self.side_changable = True
			case nna_utils_name.SymmetrySide.Left: self.side = ".L"; self.side_changable = False
			case nna_utils_name.SymmetrySide.Right: self.side = ".R"; self.side_changable = False
		
		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			target = nna_utils_tree.get_object_by_target_id(self.target_id)
			(nna_name, symmetry) = nna_utils_name.get_symmetry(nna_utils_name.get_nna_name(self.target_id))

			nna_name = nna_name + "EyeBoneLimits" + str(round(self.up, 2)) + "," + str(round(self.down, 2)) + "," + str(round(self.inner, 2)) + "," + str(round(self.outer, 2))
			if(self.side_changable and self.side != "_"): target.name = nna_name + self.side
			else: target.name = nna_name + symmetry

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


_Match = r"(?i)EyeBoneLimits(?P<up>[0-9]*[.][0-9]+),(?P<down>[0-9]*[.][0-9]+),(?P<in>[0-9]*[.][0-9]+),(?P<out>[0-9]*[.][0-9]+)(?P<side>([._\-|:][lr])|[._\-|:\s]?(right|left))?$"

def name_match_ava_eyetracking_bone_limits(name: str) -> int:
	match = re.search(_Match, name)
	return -1 if not match else match.start()

def name_display_ava_eyetracking_bone_limits(layout, name: str):
	match = re.search(_Match, name)
	if(match.groupdict()["side"]):
		side = nna_utils_name.detect_symmetry(name)
		row = layout.row(); row.label(text="Limits for the " + str(side) + " eye.")
	else:
		row = layout.row(); row.label(text="Limits for both eyes.")
	row = layout.row(); row.label(text="Up"); row.label(text=match.groupdict()["up"])
	row = layout.row(); row.label(text="Down"); row.label(text=match.groupdict()["down"])
	row = layout.row(); row.label(text="Left"); row.label(text=match.groupdict()["in"])
	row = layout.row(); row.label(text="Right"); row.label(text=match.groupdict()["out"])


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
