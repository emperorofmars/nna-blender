from enum import Enum, auto
import inspect
import sys
import bpy

class NNAOperatorType(Enum):
	Add = auto()
	Edit = auto()
	Remove = auto()

def get_nna_types_from_module(module, operator_type: NNAOperatorType):
	ret = {}
	if(nna_types := getattr(module, "nna_types", None)):
		for nna_type, value in nna_types.items():
			if(value.get(operator_type)):
				ret[nna_type] = value.get(operator_type)
	return ret

def get_local_nna_operators(operator_type: NNAOperatorType):
	ret = {}
	
	from . import components

	for name, module in inspect.getmembers(components, inspect.ismodule):
		if(nna_types := get_nna_types_from_module(module, operator_type)):
			ret = ret | nna_types
	return ret

def get_loaded_nna_operators(operator_type: NNAOperatorType):
	ret = {}
	for addon_name in bpy.context.preferences.addons.keys():
		if(addon_name in sys.modules):
			module = sys.modules[addon_name]
			if(nna_types := get_nna_types_from_module(module, operator_type)):
				ret = ret | nna_types
	return ret

def get_nna_operators(operator_type: NNAOperatorType):
	return get_local_nna_operators(operator_type) | get_loaded_nna_operators(operator_type)

