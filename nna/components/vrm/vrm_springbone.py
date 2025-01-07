import bpy
from ...nna_registry import NNAFunctionType
from ...utils import nna_id_list


_nna_name = "vrm.springbone"


def display_vrm_spring_component(target_id: str, layout: bpy.types.UILayout, json_component: dict, component_index: int):
	nna_id_list.draw_id_list(target_id, layout, json_component, component_index, "colliders")

	row = layout.split(factor=0.4); row.label(text="Raw Springbone Values"); row.label(text=str(json_component.get("parsed")))


nna_types = {
	_nna_name: {
		NNAFunctionType.JsonDisplay: display_vrm_spring_component,
	},
}
