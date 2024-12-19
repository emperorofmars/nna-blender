import bpy

from ...nna_registry import NNAFunctionType

from ..base_add_json import NNA_Json_Add_Base
from ..base_edit_json import NNA_Json_Edit_Base

_nna_name = "ava.secondary_motion"


class AddAVASecondaryMotionComponentOperator(bpy.types.Operator, NNA_Json_Add_Base):
	"""Create simple bone physics definition"""
	bl_idname = "nna.add_ava_secondary_motion"
	bl_label = "Create simple bone physics definition"

	def init(self) -> dict:
		return {
			"t": _nna_name,
			"intensity": 0.3,
		}


class EditAVASecondaryMotionComponentOperator(bpy.types.Operator, NNA_Json_Edit_Base):
	"""Edit simple bone physics definition"""
	bl_idname = "nna.edit_ava_secondary_motion"
	bl_label = "Edit simple bone physics definition"

	intensity: bpy.props.FloatProperty(name="Intensity", default=0.3, min=0, max=1, precision=2, step=2) # type: ignore

	def parse(self, json_component: dict):
		self.intensity = json_component.get("intensity", 0.3)

	def serialize(self, json_component: dict) -> dict:
		json_component["intensity"] = round(self.intensity, 2)
		return json_component

	def draw(self, context):
		self.layout.prop(self, "intensity", expand=True)


def display_ava_secondary_motion_component(otarget_id: str, layout: bpy.types.UILayout, json_component: dict, component_index: int):
	row = layout.split(factor=0.4); row.label(text="Intensity"); row.label(text=str(json_component.get("intensity", "default (0.3)")))


nna_types = {
	_nna_name: {
		NNAFunctionType.JsonAdd: AddAVASecondaryMotionComponentOperator.bl_idname,
		NNAFunctionType.JsonEdit: EditAVASecondaryMotionComponentOperator.bl_idname,
		NNAFunctionType.JsonDisplay: display_ava_secondary_motion_component,
	},
}
