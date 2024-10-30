import inspect
import sys
import bpy
import addon_utils

class NNA_Registry:
	# <nna_type: str, (AddOperator_bl_idname: str, EditOperator_bl_idname: str, DeleteOperator_bl_idname: str)>
	_registry = {}
	
	@staticmethod
	def register(nna_type: str, bl_idnames: tuple[str, str, str]):
		pass
	
	@staticmethod
	def unregister(nna_type: str):
		pass
	
	@staticmethod
	def get(nna_type: str) -> tuple[str, str, str]:
		pass


def register():
	findNNAModules()
	pass

def unregister():
	pass

def findNNAModules():
	nna_modules = []
	for mod_name in bpy.context.preferences.addons.keys():
		if(mod_name in sys.modules):
			module = sys.modules[mod_name]
			if((reg := findFunction(module, "nna_register")) is not None and (unreg := findFunction(module, "nna_unregister")) is not None):
				nna_modules.append((addon_utils.module_bl_info(module), reg, unreg))
	# for module in nna_modules: print(module[0].get("name"))
	return nna_modules

def findFunction(module, func_name: str):
	for name, obj in inspect.getmembers(module):
		if inspect.isfunction(obj) and name == func_name:
			return obj
	return None
