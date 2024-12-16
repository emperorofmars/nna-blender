from enum import StrEnum
import inspect
import sys
import bpy

from .nna_operators_raw_json import AddNNARawJsonComponentOperator

"""To register additional types not NNA, create a dict named `nna_types` at the root of your Blender-Python module.

It contains dicts of your additional NNA types.
The keys are the NNA names of your components.
The values must match the string value of the `NNAFunctionType` enum.

Example:
```
nna_types = {
	"your.component_name": {
		"json_add": AddYourJsonComponent.bl_idname,
		"json_edit": EditYourJsonComponent.bl_idname,
		"json_display": display_your_json_component,
		"name_match": match_your_name_definition,
		"name_set": SetYourNameDefinition.bl_idname,
		"name_display": display_your_name_definition
	},
}
```
"""

class NNAFunctionType(StrEnum):
	"""Types of hot-loadable code for an NNA type.

	* `JsonAdd`: str (bl_idname of a Blender operator)
		Operator Properties:
			* target_id: str
		Creates a new component of your NNA type.
	* `JsonEdit`: str (bl_idname of a Blender operator)
		Operator Properties:
			* target_id: str
			* component_index: int
		Lets the user edit the values of your NNA component
	`JsonRemove`: str (bl_idname of a Blender operator)
		Operator Properties:
			* target_id: str
			* component_index: int
		Removes the NNA component. Unless your type does something special, this is not needed. NNA can just remove it.
	`JsonDisplay`: function(object, layout, json_dict)
		Callback function which draws your NNA component, passed as a dict
	`NameSet`: str (bl_idname of a Blender operator)
		Operator Properties:
			* target_id: str
		Renames the Node (Object or Bone) to add your NNA name definition.
	`NameMatch`: function(name: str) -> int
		Callback function which returns the index of the first character where the NNA name definition starts in a node name. If no match is found, returns `-1`
	`NameDisplay` functionname_display_nna_twist(object, layout, name: str)
		Callback function which draws the properties of your NNA name definition.
	"""
	JsonAdd = "json_add"
	JsonEdit = "json_edit"
	JsonRemove = "json_remove"
	JsonDisplay = "json_display"
	NameSet = "name_set"
	NameMatch = "name_match"
	NameDisplay = "name_display"


def get_nna_types_from_module(module, function_type: NNAFunctionType) -> dict[str, any]:
	ret = {}
	if(nna_types := getattr(module, "nna_types", None)):
		for nna_type, value in nna_types.items():
			if(value.get(str(function_type))):
				ret[nna_type] = value.get(str(function_type))
	return ret

def _concat_module_members(*modules) -> list:
	ret = []
	for module in modules:
		ret = [*ret, *inspect.getmembers(module, inspect.ismodule)]
	return ret

def get_local_nna_operators(function_type: NNAFunctionType) -> dict[str, any]:
	ret = {}

	from .components import nna, ava, vrc, vrm

	for name, module in _concat_module_members(nna, ava, vrc, vrm):
		if(nna_types := get_nna_types_from_module(module, str(function_type))):
			ret = ret | nna_types
	return ret

def get_loaded_nna_operators(function_type: NNAFunctionType) -> dict[str, any]:
	ret = {}
	for addon_name in bpy.context.preferences.addons.keys():
		if(addon_name in sys.modules):
			module = sys.modules[addon_name]
			if(nna_types := get_nna_types_from_module(module, str(function_type))):
				ret = ret | nna_types
	return ret

def get_nna_operators(function_type: NNAFunctionType) -> dict[str, any]:
	"""Get the `NNAFunctionType` from all loaded NNA types which, have this `NNAFunctionType` registered."""
	return get_local_nna_operators(str(function_type)) | get_loaded_nna_operators(str(function_type))


def _build_operator_enum(function_type) -> list:
	_NNAEnumCache[str(function_type)] = [((value, key, "")) for key, value in get_nna_operators(str(function_type)).items()]
	return _NNAEnumCache[str(function_type)]

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
