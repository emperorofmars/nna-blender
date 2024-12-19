import re
import bpy

from ...nna_registry import NNAFunctionType

from ..base_add_json import NNA_Json_Add_Base
from ..base_edit_json import NNA_Json_Edit_Base
from ..base_edit_name import NNA_Name_Definition_Base


_nna_name = "nna.humanoid.settings"


class AddNNAHumanoidSettingsComponentOperator(bpy.types.Operator, NNA_Json_Add_Base):
	"""Specifies humanoid rig settings."""
	bl_idname = "nna.add_humanoid_settings"
	bl_label = "Add Humanoid Settings Component"
	nna_name = _nna_name

nna_types = {
	_nna_name: {
		NNAFunctionType.JsonAdd: AddNNAHumanoidSettingsComponentOperator.bl_idname,
		#NNAFunctionType.JsonEdit: EditNNATwistComponentOperator.bl_idname,
		#NNAFunctionType.JsonDisplay: display_nna_twist_component,
	},
}
