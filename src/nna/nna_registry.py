from enum import Enum, auto
import inspect
import sys
import bpy

class NNAFunctionType(Enum):
	Add = auto()
	Edit = auto()
	Remove = auto()
	Display = auto()

def get_nna_types_from_module(module, operator_type: NNAFunctionType) -> dict[str, str]:
	ret = {}
	if(nna_types := getattr(module, "nna_types", None)):
		for nna_type, value in nna_types.items():
			if(value.get(operator_type)):
				ret[nna_type] = value.get(operator_type)
	return ret

def get_local_nna_operators(operator_type: NNAFunctionType) -> dict[str, str]:
	ret = {}
	
	from . import components

	for name, module in inspect.getmembers(components, inspect.ismodule):
		if(nna_types := get_nna_types_from_module(module, operator_type)):
			ret = ret | nna_types
	return ret

def get_loaded_nna_operators(operator_type: NNAFunctionType) -> dict[str, str]:
	ret = {}
	for addon_name in bpy.context.preferences.addons.keys():
		if(addon_name in sys.modules):
			module = sys.modules[addon_name]
			if(nna_types := get_nna_types_from_module(module, operator_type)):
				ret = ret | nna_types
	return ret

def get_nna_operators(operator_type: NNAFunctionType) -> dict[str, str]:
	return get_local_nna_operators(operator_type) | get_loaded_nna_operators(operator_type)


def _build_operator_enum(operator_type) -> list:
	NNACache[operator_type] = get_nna_operators(operator_type)
	_NNAEnumCache[operator_type] = [((key, value, "")) for key, value in NNACache[operator_type].items()]
	return _NNAEnumCache[operator_type]

def _build_operator_add_enum_callback(self, context) -> list:
	return _build_operator_enum(NNAFunctionType.Add)

_NNAEnumCache = {
	NNAFunctionType.Add: []
}

NNACache = {
	NNAFunctionType.Add: {}
}

def register():
	bpy.types.Scene.nna_oparators_add = bpy.props.EnumProperty(
		items=_build_operator_add_enum_callback,
		name="NNA Add Operators",
		description="Default & hot-loaded NNA add operators",
		options={"SKIP_SAVE"}
	)

def unregister():
	if hasattr(bpy.types.Scene, "nna_oparators_add"):
		del bpy.types.Scene.nna_oparators_add
