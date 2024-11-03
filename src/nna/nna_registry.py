from enum import Enum, auto
import inspect
import sys
import bpy

class NNAOperatorType(Enum):
	Add = auto()
	Edit = auto()
	Remove = auto()

def get_nna_types_from_module(module, operator_type: NNAOperatorType) -> dict[str, str]:
	ret = {}
	if(nna_types := getattr(module, "nna_types", None)):
		for nna_type, value in nna_types.items():
			if(value.get(operator_type)):
				ret[nna_type] = value.get(operator_type)
	return ret

def get_local_nna_operators(operator_type: NNAOperatorType) -> dict[str, str]:
	ret = {}
	
	from . import components

	for name, module in inspect.getmembers(components, inspect.ismodule):
		if(nna_types := get_nna_types_from_module(module, operator_type)):
			ret = ret | nna_types
	return ret

def get_loaded_nna_operators(operator_type: NNAOperatorType) -> dict[str, str]:
	ret = {}
	for addon_name in bpy.context.preferences.addons.keys():
		if(addon_name in sys.modules):
			module = sys.modules[addon_name]
			if(nna_types := get_nna_types_from_module(module, operator_type)):
				ret = ret | nna_types
	return ret

def get_nna_operators(operator_type: NNAOperatorType) -> dict[str, str]:
	return get_local_nna_operators(operator_type) | get_loaded_nna_operators(operator_type)


def _build_operator_enum(operator_type) -> list:
	NNACache[operator_type] = get_nna_operators(operator_type)
	_NNAEnumCache[operator_type] = [((key, value, "")) for key, value in NNACache[operator_type].items()]
	return _NNAEnumCache[operator_type]

def _build_operator_add_enum_callback(self, context) -> list:
	return _build_operator_enum(NNAOperatorType.Add)

def _build_operator_edit_enum_callback(self, context) -> list:
	return _build_operator_enum(NNAOperatorType.Edit)

def _build_operator_remove_enum_callback(self, context) -> list:
	return _build_operator_enum(NNAOperatorType.Remove)

_NNAEnumCache = {
	NNAOperatorType.Add: [],
	NNAOperatorType.Edit: [],
	NNAOperatorType.Remove: [],
}

NNACache = {
	NNAOperatorType.Add: {},
	NNAOperatorType.Edit: {},
	NNAOperatorType.Remove: {},
}

def register():
	bpy.types.Scene.nna_oparators_add = bpy.props.EnumProperty(
		items=_build_operator_add_enum_callback,
		name="NNA Add Operators",
		description="Default & hot-loaded NNA add operators",
		options={"SKIP_SAVE"}
	)
	bpy.types.Scene.nna_oparators_edit = bpy.props.EnumProperty(
		items=_build_operator_edit_enum_callback,
		name="NNA Edit Operators",
		description="Default & hot-loaded NNA edit operators",
		options={"SKIP_SAVE"}
	)
	bpy.types.Scene.nna_oparators_remove = bpy.props.EnumProperty(
		items=_build_operator_remove_enum_callback,
		name="NNA Remove Operators",
		description="Default & hot-loaded NNA remove operators",
		options={"SKIP_SAVE"}
	)

def unregister():
	if hasattr(bpy.types.Scene, "nna_oparators_add"):
		del bpy.types.Scene.nna_oparators_add
	if hasattr(bpy.types.Scene, "nna_oparators_edit"):
		del bpy.types.Scene.nna_oparators_edit
	if hasattr(bpy.types.Scene, "nna_oparators_remove"):
		del bpy.types.Scene.nna_oparators_remove
