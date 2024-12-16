import bpy
from ...nna_registry import NNAFunctionType
from ... import nna_operators_id_list
from ... import nna_operators_selector


_nna_name = "vrc.physbone"


def display_vrc_physbone_component(target_id: str, layout: bpy.types.UILayout, json_component: dict, component_index: int):
	nna_operators_id_list.draw_id_list(target_id, layout, json_component, component_index, "colliders")
	nna_operators_selector.draw_selector_list(target_id, layout, json_component, component_index, "ignoreTransforms", label_text="Ignored Nodes")

	row = layout.split(factor=0.4); row.label(text="Raw Physbone Values"); row.label(text=str(json_component.get("parsed")))


nna_types = {
	_nna_name: {
		NNAFunctionType.JsonDisplay: display_vrc_physbone_component,
	},
}
