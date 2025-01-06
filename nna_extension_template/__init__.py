# Custom NNA TYPE Template
from .nna_extension_template import nna_types

from .get_blender_nna_module_prefix import nna_blender_module_prefix

def register():
	if(nna_blender_module_prefix):
		from .nna_extension_template import register
		register()

def unregister():
	if(nna_blender_module_prefix):
		from .nna_extension_template import unregister
		unregister()
