import bpy

from ...nna_registry import NNAFunctionType
from ...ops.nna_operators_util import CreateNewObjectOperator, SetActiveObjectOperator

from ..base_add_json import NNA_Json_Add_Base
from ..base_edit_json import NNA_Json_Edit_Base


_nna_name = "ava.avatar"


class AddAVAAvatarComponentOperator(bpy.types.Operator, NNA_Json_Add_Base):
	"""Specifies this object to be a VR & V-Tubing avatar.
	This component is not nescessary, unless you want to disable on-import-automapping of features.
	"""
	bl_idname = "ava.add_ava_avatar"
	bl_label = "Add AVA Avatar Component"
	nna_name = _nna_name


class EditAVAAvatarComponentOperator(bpy.types.Operator, NNA_Json_Edit_Base):
	"""Specifies this object to be a VR & V-Tubing avatar.
	This component is not nescessary, unless you want to disable on-import-automapping of features.
	"""
	bl_idname = "nna.edit_ava_avatar"
	bl_label = "Edit AVA Avatar Component"

	automap: bpy.props.BoolProperty(name="Automap", default=True) # type: ignore

	def parse(self, json_component: dict):
		if("auto" in json_component): self.automap = json_component["auto"]

	def serialize(self, json_component: dict) -> dict:
		if(not self.automap): json_component["auto"] = False
		elif("auto" in json_component):
			del json_component["auto"]
		return json_component

	def draw(self, context):
		self.layout.prop(self, "automap", expand=True)


def display_ava_avatar_component(target_id: str, layout: bpy.types.UILayout, json_component: dict, component_index: int):
	autodect = "auto" in json_component and not json_component["auto"]
	row = layout.split(factor=0.4)
	row.label(text="Automap")
	row.label(text="False" if autodect else "True")

	viewport_object = bpy.data.objects.get("$ViewportFirstPerson")
	if(viewport_object):
		row = layout.row()
		row.label(text="Viewport defined by '$ViewportFirstPerson'")
		row.operator(SetActiveObjectOperator.bl_idname).target_name = "$ViewportFirstPerson"
	else:
		row = layout.row()
		row.operator(CreateNewObjectOperator.bl_idname, text="Create Viewport Object").target_name = "$ViewportFirstPerson"


def name_match_ava_viewport_first_person(name: str) -> int:
	return 0 if name == "$ViewportFirstPerson" else -1


nna_types = {
	_nna_name: {
		NNAFunctionType.JsonAdd: AddAVAAvatarComponentOperator.bl_idname,
		NNAFunctionType.JsonEdit: EditAVAAvatarComponentOperator.bl_idname,
		NNAFunctionType.JsonDisplay: display_ava_avatar_component,
	},
	"ava.viewport.first_person": {
		NNAFunctionType.NameMatch: name_match_ava_viewport_first_person,
	}
}
