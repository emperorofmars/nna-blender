import bpy
from . import nna_utils_tree


class NNASelectorProperty(bpy.types.PropertyGroup):
	object: bpy.props.StringProperty(name="Object", default="") # type: ignore
	bone: bpy.props.StringProperty(name="Bone", default="") # type: ignore


def init_selector(target_id: str = None, split_char: str = "$"):
	base_object = nna_utils_tree.get_base_object_by_target_id(target_id, split_char)
	target_object = nna_utils_tree.get_object_by_target_id(target_id, split_char)
	bpy.context.scene.nna_object_selector = base_object
	if(target_object and target_object != base_object and hasattr(base_object.data, "bones")):
		bpy.context.scene.nna_bone_selector = target_object.name


def init_selector_relative(origin_id: str, target_id: str = None, origin_split_char: str = "$", target_split_char: str = "$"):
	base_object = nna_utils_tree.get_base_object_by_target_id(origin_id, origin_split_char)
	if(target_id):
		if(hasattr(base_object.data, "bones")): # If the node is a bone, try to find its source within the same armature.
			source_id = base_object.name + "$" + target_id
			source_object = nna_utils_tree.get_object_by_target_id(source_id)
			if(source_object):
				init_selector(source_id)
			else: # Else try to find it by '&' separated target_id.
				init_selector(target_id, split_char=target_split_char)
		else: # If the node is not a bone, find the target object.
			init_selector(target_id)
	elif(base_object): # When the node has no specified source_node, check if its a bone and set the armature as the object if so.
		if(hasattr(base_object.data, "bones")):
			init_selector(base_object.name)
		else:
			init_selector()
	else:
		init_selector()


def get_selected_target_id(split_char: str = "$") -> str | None:
	if(bpy.context.scene.nna_object_selector and (not bpy.context.scene.nna_bone_selector or bpy.context.scene.nna_bone_selector == "$")):
		return bpy.context.scene.nna_object_selector.name
	elif(bpy.context.scene.nna_object_selector and bpy.context.scene.nna_bone_selector):
		return bpy.context.scene.nna_object_selector.name + split_char + bpy.context.scene.nna_bone_selector
	else:
		return None


def get_selected_target_id_relative(origin_id: str, origin_split_char: str = "$", target_split_char: str = "$") -> str | None:
	base_object = nna_utils_tree.get_base_object_by_target_id(origin_id, origin_split_char)
	if(bpy.context.scene.nna_object_selector and (not bpy.context.scene.nna_bone_selector or bpy.context.scene.nna_bone_selector == "$")):
		return bpy.context.scene.nna_object_selector.name
	elif(bpy.context.scene.nna_object_selector and bpy.context.scene.nna_bone_selector):
		if(base_object.name == bpy.context.scene.nna_object_selector.name):
			return bpy.context.scene.nna_bone_selector
		else:
			return bpy.context.scene.nna_object_selector.name + target_split_char + bpy.context.scene.nna_bone_selector
	else:
		return None


def draw_selector_prop(target_id: str, layout: bpy.types.UILayout):
	layout.prop_search(bpy.context.scene, "nna_object_selector", bpy.data, "objects")
	if(bpy.context.scene.nna_object_selector and hasattr(bpy.context.scene.nna_object_selector.data, "bones")):
		layout.prop(bpy.context.scene, "nna_bone_selector")


def _build_bone_enum(self, context) -> list:
	if(bpy.context.scene.nna_object_selector and hasattr(bpy.context.scene.nna_object_selector.data, "bones")):
		ret = [((bone.name, bone.name, "")) for bone in bpy.context.scene.nna_object_selector.data.bones]
		ret.append((("$", "", "")))
		return ret
	else:
		return []


def register():
	bpy.types.Scene.nna_object_selector = bpy.props.PointerProperty(type=bpy.types.Object, name="Object", options={"SKIP_SAVE"}) # type: ignore
	bpy.types.Scene.nna_bone_selector = bpy.props.EnumProperty(items=_build_bone_enum, name="Bone", options={"SKIP_SAVE"}) # type: ignore

def unregister():
	if hasattr(bpy.types.Scene, "nna_object_selector"):
		del bpy.types.Scene.nna_object_selector
	if hasattr(bpy.types.Scene, "nna_bone_selector"):
		del bpy.types.Scene.nna_bone_selector
