import bpy
from . import nna_utils_json
from . import nna_utils_tree


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



class EditNNASelectionListOperator(bpy.types.Operator):
	"""Edit Selection List"""
	bl_idname = "nna.edit_selection_list"
	bl_label = "Edit"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	component_index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore
	json_key: bpy.props.StringProperty(name = "json_key") # type: ignore
	
	def invoke(self, context, event):
		json_component = nna_utils_json.get_component(self.target_id, self.component_index)
		object = nna_utils_tree.get_object_by_target_id(self.target_id)

		object.nna_selector_list.clear()
		for selection in json_component.get(self.json_key, []):
			object.nna_selector_list.add().target_id = str(selection)

		return context.window_manager.invoke_props_dialog(self)
	
	def execute(self, context):
		try:
			json_component = nna_utils_json.get_component(self.target_id, self.component_index)
			object = nna_utils_tree.get_object_by_target_id(self.target_id)

			selection_list = []
			for selection in object.nna_selector_list:
				if(selection.target_id): selection_list.append(selection.target_id)
			json_component[self.json_key] = selection_list

			nna_utils_json.replace_component(self.target_id, json_component, self.component_index)
			self.report({'INFO'}, "Selectors successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		object = nna_utils_tree.get_object_by_target_id(self.target_id)
		for index, selection in enumerate(object.nna_selector_list):
			row = self.layout.row(); row.label(text=selection.target_id)
			#row.prop(selection, "target_id", text="ID " + str(index))
			edit_button = row.operator(NNASelectorPropertyEditOperator.bl_idname, text="", icon="OPTIONS")
			edit_button.target_id = self.target_id
			edit_button.selector_target_id = selection.target_id
			delete_button = row.operator(NNASelectorPropertyDeleteOperator.bl_idname, text="", icon="X")
			delete_button.target_id = self.target_id
			delete_button.index = index
		self.layout.operator(NNASelectorPropertyAddOperator.bl_idname, icon="ADD").target_id = self.target_id


class NNASelectorProperty(bpy.types.PropertyGroup):
	target_id: bpy.props.StringProperty(name="Target", default="") # type: ignore

class NNASelectorPropertyAddOperator(bpy.types.Operator):
	bl_idname = "nna.edit_selector_list_add"
	bl_label = "Add"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore

	def invoke(self, context, event):
		init_selector_relative(self.target_id)
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		object = nna_utils_tree.get_object_by_target_id(self.target_id)
		new_entry = object.nna_selector_list.add()
		new_entry.target_id = get_selected_target_id_relative(self.target_id)
		return {"FINISHED"}

	def draw(self, context):
		draw_selector_prop(self.target_id, self.layout)

class NNASelectorPropertyEditOperator(bpy.types.Operator):
	bl_idname = "nna.edit_selector_list"
	bl_label = "Edit"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	selector_target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	index: bpy.props.IntProperty(name = "index") # type: ignore

	def invoke(self, context, event):
		init_selector_relative(self.target_id, self.selector_target_id)
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		object = nna_utils_tree.get_object_by_target_id(self.target_id)
		object.nna_selector_list[self.index].target_id = get_selected_target_id_relative(self.target_id)
		return {"FINISHED"}

	def draw(self, context):
		draw_selector_prop(self.target_id, self.layout)

class NNASelectorPropertyDeleteOperator(bpy.types.Operator):
	bl_idname = "nna.edit_selector_list_delete"
	bl_label = "Delete"
	bl_options = {"REGISTER", "UNDO"}
	
	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore

	def execute(self, context):
		object = nna_utils_tree.get_object_by_target_id(self.target_id)
		object.nna_selector_list.remove(self.index)
		return {"FINISHED"}


def draw_selector_list(target_id: str, layout: bpy.types.UILayout, json_component: dict, component_index: int, json_key: str, label_text: str = None):
	if(label_text == None): label_text = json_key.capitalize()
	row = layout.split(factor=0.4)
	row.label(text=label_text)
	row = row.row()
	selection_list = ""
	for index, selection in enumerate(json_component.get(json_key, [])):
		selection_list += str(selection)
		if(index < len(json_component.get(json_key)) - 1): selection_list += ", "
	row.label(text=selection_list if selection_list else "-")
	collider_list_button = row.operator(EditNNASelectionListOperator.bl_idname, text="", icon="OPTIONS")
	collider_list_button.target_id = target_id
	collider_list_button.component_index = component_index
	collider_list_button.json_key = json_key



def _build_bone_enum(self, context) -> list:
	if(bpy.context.scene.nna_object_selector and hasattr(bpy.context.scene.nna_object_selector.data, "bones")):
		ret = [((bone.name, bone.name, "")) for bone in bpy.context.scene.nna_object_selector.data.bones]
		ret.append((("$", "", "")))
		return ret
	else:
		return []

def _poll_objects(self, object: bpy.types.Object) -> bool:
	return not object.name.startswith("$")


def register():
	bpy.types.Scene.nna_object_selector = bpy.props.PointerProperty(type=bpy.types.Object, poll=_poll_objects, name="Object", options={"SKIP_SAVE"}) # type: ignore
	bpy.types.Scene.nna_bone_selector = bpy.props.EnumProperty(items=_build_bone_enum, name="Bone", options={"SKIP_SAVE"}) # type: ignore
	bpy.types.Object.nna_selector_list = bpy.props.CollectionProperty(type=NNASelectorProperty, options={"SKIP_SAVE"}, override={"USE_INSERTION"}) # type: ignore
	bpy.types.Bone.nna_selector_list = bpy.props.CollectionProperty(type=NNASelectorProperty, options={"SKIP_SAVE"}, override={"USE_INSERTION"}) # type: ignore

def unregister():
	if hasattr(bpy.types.Scene, "nna_object_selector"):
		del bpy.types.Scene.nna_object_selector
	if hasattr(bpy.types.Scene, "nna_bone_selector"):
		del bpy.types.Scene.nna_bone_selector
	if hasattr(bpy.types.Object, "nna_selector_list"):
		del bpy.types.Object.nna_selector_list
	if hasattr(bpy.types.Bone, "nna_selector_list"):
		del bpy.types.Bone.nna_selector_list
