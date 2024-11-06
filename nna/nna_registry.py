from enum import StrEnum
import inspect
import sys
import bpy

from .nna_operators_raw_json import AddNNARawJsonComponentOperator

class NNAFunctionType(StrEnum):
	JsonAdd = "json_add"
	JsonEdit = "json_edit"
	JsonRemove = "json_remove"
	JsonDisplay = "json_display"
	NameSet = "name_set"
	NameMatch = "name_match"

def get_nna_types_from_module(module, operator_type: NNAFunctionType) -> dict[str, any]:
	ret = {}
	if(nna_types := getattr(module, "nna_types", None)):
		for nna_type, value in nna_types.items():
			if(value.get(str(operator_type))):
				ret[nna_type] = value.get(str(operator_type))
	return ret

def get_local_nna_operators(operator_type: NNAFunctionType) -> dict[str, any]:
	ret = {}
	
	from .components import nna, ava

	for name, module in [*inspect.getmembers(nna, inspect.ismodule), *inspect.getmembers(ava, inspect.ismodule)]:
		if(nna_types := get_nna_types_from_module(module, str(operator_type))):
			ret = ret | nna_types
	return ret

def get_loaded_nna_operators(operator_type: NNAFunctionType) -> dict[str, any]:
	ret = {}
	for addon_name in bpy.context.preferences.addons.keys():
		if(addon_name in sys.modules):
			module = sys.modules[addon_name]
			if(nna_types := get_nna_types_from_module(module, str(operator_type))):
				ret = ret | nna_types
	return ret

def get_nna_operators(operator_type: NNAFunctionType) -> dict[str, any]:
	return get_local_nna_operators(str(operator_type)) | get_loaded_nna_operators(str(operator_type))


def _build_operator_enum(operator_type) -> list:
	_NNAEnumCache[str(operator_type)] = [((value, key, "")) for key, value in get_nna_operators(str(operator_type)).items()]
	if(operator_type == NNAFunctionType.JsonAdd): _NNAEnumCache[str(operator_type)].append(((AddNNARawJsonComponentOperator.bl_idname, "Raw Json", "")))
	return _NNAEnumCache[str(operator_type)]

def _build_operator_add_enum_callback(self, context) -> list:
	return _build_operator_enum(NNAFunctionType.JsonAdd)

def _build_operator_name_enum_callback(self, context) -> list:
	return _build_operator_enum(NNAFunctionType.NameSet)

_NNAEnumCache = {
	NNAFunctionType.JsonAdd: [],
	NNAFunctionType.NameSet: [],
}

def register():
	bpy.types.Scene.nna_oparators_add = bpy.props.EnumProperty(
		items=_build_operator_add_enum_callback,
		name="NNA Add Operators",
		description="Default & hot-loaded NNA add operators",
		options={"SKIP_SAVE"},
		default=0
	)
	bpy.types.Scene.nna_oparators_name = bpy.props.EnumProperty(
		items=_build_operator_name_enum_callback,
		name="NNA Name Operators",
		description="Default & hot-loaded NNA name operators",
		options={"SKIP_SAVE"}
	)

def unregister():
	if hasattr(bpy.types.Scene, "nna_oparators_add"):
		del bpy.types.Scene.nna_oparators_add
	if hasattr(bpy.types.Scene, "nna_oparators_name"):
		del bpy.types.Scene.nna_oparators_name
