import bpy

from ...ops.nna_operators_common import EditNNAComponentStringOperator
from ...nna_registry import NNAFunctionType


_nna_name = "vrc.contact_receiver"


def display_vrc_contact_receiver_component(target_id: str, layout: bpy.types.UILayout, json_component: dict, component_index: int):
	row = layout.split(factor=0.4)
	row.label(text="Target None Name")
	row.label(text=json_component.get("target_node_name", "-"))
	edit_target_node_name_button = row.operator(EditNNAComponentStringOperator.bl_idname)
	edit_target_node_name_button.target_id = target_id
	edit_target_node_name_button.component_index = component_index
	edit_target_node_name_button.property_name = "target_node_name"

	row = layout.split(factor=0.4); row.label(text="Raw Values"); row.label(text=str(json_component.get("parsed")))


nna_types = {
	_nna_name: {
		NNAFunctionType.JsonDisplay: display_vrc_contact_receiver_component,
	},
}
