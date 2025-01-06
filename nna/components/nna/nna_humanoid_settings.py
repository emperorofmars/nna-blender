import re
import bpy

from ...nna_registry import NNAFunctionType

from .. import NNA_Json_Add_Base
from .. import NNA_Json_Edit_Base


_nna_name = "nna.humanoid.settings"


class AddNNAHumanoidSettingsComponentOperator(bpy.types.Operator, NNA_Json_Add_Base):
	"""Specifies humanoid rig settings"""
	bl_idname = "nna.add_humanoid_settings"
	bl_label = "Add Humanoid Settings Component"

	def init(self) -> dict:
		return {
			"t": _nna_name,
			"upper_arm_twist": 0.5,
			"lower_arm_twist": 0.5,
			"upper_leg_twist": 0.5,
			"lower_leg_twist": 0.5,
			"arm_stretch": 0.05,
			"leg_stretch": 0.05,
			"feet_spacing": 0,
			"translation_dof": False,
		}


class EditNNAHumanoidSettingsComponentOperator(bpy.types.Operator, NNA_Json_Edit_Base):
	"""Specifies humanoid rig settings"""
	bl_idname = "nna.edit_nna_humanoid_settings"
	bl_label = "Edit Humanoid Settings Component"

	upper_arm_twist: bpy.props.FloatProperty(name="Upper Arm Twist", default=0.5, min=0, max=1, precision=2, step=2) # type: ignore
	lower_arm_twist: bpy.props.FloatProperty(name="Lower Arm Twist", default=0.5, min=0, max=1, precision=2, step=2) # type: ignore
	upper_leg_twist: bpy.props.FloatProperty(name="Upper Leg Twist", default=0.5, min=0, max=1, precision=2, step=2) # type: ignore
	lower_leg_twist: bpy.props.FloatProperty(name="Lower Leg Twist", default=0.5, min=0, max=1, precision=2, step=2) # type: ignore
	arm_stretch: bpy.props.FloatProperty(name="Arm Stretch", default=0.05, min=0, max=1, precision=2, step=2) # type: ignore
	leg_stretch: bpy.props.FloatProperty(name="Leg Stretch", default=0.05, min=0, max=1, precision=2, step=2) # type: ignore
	feet_spacing: bpy.props.FloatProperty(name="Feet Spacing", default=0, min=0, max=1, precision=2, step=2) # type: ignore
	translation_dof: bpy.props.BoolProperty(name="Translation DoF", default=False) # type: ignore

	def parse(self, json_component: dict):
		if("upper_arm_twist" in json_component): self.upper_arm_twist = json_component["upper_arm_twist"]
		if("lower_arm_twist" in json_component): self.lower_arm_twist = json_component["lower_arm_twist"]
		if("upper_leg_twist" in json_component): self.upper_leg_twist = json_component["upper_leg_twist"]
		if("lower_leg_twist" in json_component): self.lower_leg_twist = json_component["lower_leg_twist"]
		if("arm_stretch" in json_component): self.arm_stretch = json_component["arm_stretch"]
		if("leg_stretch" in json_component): self.leg_stretch = json_component["leg_stretch"]
		if("feet_spacing" in json_component): self.feet_spacing = json_component["feet_spacing"]
		if("translation_dof" in json_component): self.translation_dof = json_component["translation_dof"]

	def serialize(self, json_component: dict) -> dict:
		json_component["upper_arm_twist"] = self.upper_arm_twist
		json_component["lower_arm_twist"] = self.lower_arm_twist
		json_component["upper_leg_twist"] = self.upper_leg_twist
		json_component["lower_leg_twist"] = self.lower_leg_twist
		json_component["arm_stretch"] = self.arm_stretch
		json_component["leg_stretch"] = self.leg_stretch
		json_component["feet_spacing"] = self.feet_spacing
		json_component["translation_dof"] = self.translation_dof

		return json_component

	def draw(self, context):
		self.layout.prop(self, "upper_arm_twist", expand=True)
		self.layout.prop(self, "lower_arm_twist", expand=True)
		self.layout.prop(self, "upper_leg_twist", expand=True)
		self.layout.prop(self, "lower_leg_twist", expand=True)
		self.layout.prop(self, "arm_stretch", expand=True)
		self.layout.prop(self, "leg_stretch", expand=True)
		self.layout.prop(self, "feet_spacing", expand=True)
		self.layout.prop(self, "translation_dof", expand=True)


def display_nna_humanoid_settings_component(target_id: str, layout: bpy.types.UILayout, json_component: dict, component_index: int):
	row = layout.split(factor=0.4); row.label(text="Upper Arm Twist"); row.label(text=str(json_component.get("upper_arm_twist", "default (0.5)")))
	row = layout.split(factor=0.4); row.label(text="Lower Arm Twist"); row.label(text=str(json_component.get("lower_arm_twist", "default (0.5)")))
	row = layout.split(factor=0.4); row.label(text="Upper Leg Twist"); row.label(text=str(json_component.get("upper_leg_twist", "default (0.5)")))
	row = layout.split(factor=0.4); row.label(text="Lower Leg Twist"); row.label(text=str(json_component.get("lower_leg_twist", "default (0.5)")))
	row = layout.split(factor=0.4); row.label(text="Arm Stretch"); row.label(text=str(json_component.get("arm_stretch", "default (0.05)")))
	row = layout.split(factor=0.4); row.label(text="Leg Stretch"); row.label(text=str(json_component.get("leg_stretch", "default (0.05)")))
	row = layout.split(factor=0.4); row.label(text="Feet Spacing"); row.label(text=str(json_component.get("feet_spacing", "default (0)")))
	row = layout.split(factor=0.4); row.label(text="Translation DoF"); row.label(text=str(json_component.get("translation_dof", "default (false)")))


nna_types = {
	_nna_name: {
		NNAFunctionType.JsonAdd: AddNNAHumanoidSettingsComponentOperator.bl_idname,
		NNAFunctionType.JsonEdit: EditNNAHumanoidSettingsComponentOperator.bl_idname,
		NNAFunctionType.JsonDisplay: display_nna_humanoid_settings_component,
	},
}
