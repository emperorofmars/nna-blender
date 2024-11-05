import bpy
import json

from .. import nna_name_utils
from .. import nna_json_utils
from .. import nna_tree_utils

class AddNNATwistComponentOperator(bpy.types.Operator):
	bl_idname = "nna.add_nna_twist"
	bl_label = "Add Twist Component"
	bl_options = {"REGISTER", "UNDO"}
	
	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	
	def execute(self, context):
		try:
			nna_json_utils.add_component(self.target_id, json.dumps({"t":"nna.twist"}))
			self.report({'INFO'}, "Component successfully added")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}


def display_nna_twist_component(object, layout, json_dict):
	row = layout.row()
	row.label(text="weight")
	row.label(text=str(json_dict["w"]) if "w" in json_dict else "default (0.5)")
	row = layout.row()
	row.label(text="source")
	row.label(text=json_dict["s"] if "s" in json_dict else "default (grandparent)")


class EditNNATwistComponentOperator(bpy.types.Operator):
	bl_idname = "nna.edit_nna_twist"
	bl_label = "Edit Twist Component"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	component_index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore

	weight: bpy.props.FloatProperty(name="weight", default=0.5, min=0, max=1) # type: ignore
	
	def invoke(self, context, event):
		json_component = nna_json_utils.get_component_dict(self.target_id, self.component_index)

		if("w" in json_component): self.weight = json_component["w"]

		if("s" in json_component):
			context.scene.nna_twist_object_selector = nna_tree_utils.get_base_object_by_target_id(json_component["s"], '&')
		else:
			context.scene.nna_twist_object_selector = None

		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			json_component = nna_json_utils.get_component_dict(self.target_id, self.component_index)

			if(self.weight != 0.5): json_component["w"] = self.weight
			
			if(context.scene.nna_twist_object_selector and (not context.scene.nna_twist_bone_selector or context.scene.nna_twist_bone_selector == "$")):
				json_component["s"] = context.scene.nna_twist_object_selector.name
			elif(context.scene.nna_twist_object_selector and context.scene.nna_twist_bone_selector):
				json_component["s"] = context.scene.nna_twist_object_selector.name + "&" + context.scene.nna_twist_bone_selector
			elif("s" in json_component):
				del json_component["s"]

			nna_json_utils.replace_component(self.target_id, json.dumps(json_component), self.component_index)
			self.report({'INFO'}, "Component successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.prop(self, "weight", text="Weight", expand=True)
		self.layout.prop_search(context.scene, "nna_twist_object_selector", bpy.data, "objects", text="Source Object")
		if(context.scene.nna_twist_object_selector and hasattr(context.scene.nna_twist_object_selector.data, "bones")):
			self.layout.prop(context.scene, "nna_twist_bone_selector", text="Source Bone")


class NNATwistNameDefinitionOperator(bpy.types.Operator):
	bl_idname = "nna.nna_twist_name_definition"
	bl_label = "NNA Twist Name Definition"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore

	weight: bpy.props.FloatProperty(name="weight", default=0.5, min=0, max=1) # type: ignore
	
	def invoke(self, context, event):
		(nna_name, symmetry) = nna_name_utils.get_symmetry(nna_name_utils.get_nna_name(self.target_id))

		# TODO parse values
		#if("w" in json_component): self.weight = json_component["w"]
		#if("s" in json_component): context.scene.nna_twist_object_selector = bpy.context.scene.objects[json_component["s"]]
		#else: context.scene.nna_twist_object_selector = None
		
		#if("s" in json_component):
		#	context.scene.nna_twist_object_selector = nna_tree_utils.get_base_object_by_target_id(json_component["s"], '&')
		#else:
		base_object = nna_tree_utils.get_base_object_by_target_id(self.target_id)
		if(hasattr(base_object.data, "bones")):
			context.scene.nna_twist_object_selector = base_object
		else:
			context.scene.nna_twist_object_selector = None

		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			target = nna_tree_utils.get_object_by_target_id(self.target_id)
			(nna_name, symmetry) = nna_name_utils.get_symmetry(nna_name_utils.get_nna_name(self.target_id))

			nna_name = nna_name + "Twist"
			if(self.weight != 0.5): nna_name += str(round(self.weight, 2))
			
			if(context.scene.nna_twist_object_selector and (not context.scene.nna_twist_bone_selector or context.scene.nna_twist_bone_selector == "$")):
				nna_name += context.scene.nna_twist_object_selector.name
			elif(context.scene.nna_twist_object_selector and context.scene.nna_twist_bone_selector):
				nna_name += context.scene.nna_twist_object_selector.name + "&" + context.scene.nna_twist_bone_selector

			target.name = nna_name + symmetry

			self.report({'INFO'}, "Component successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.prop(self, "weight", text="Weight", expand=True)
		self.layout.prop_search(context.scene, "nna_twist_object_selector", bpy.data, "objects", text="Source")
		if(context.scene.nna_twist_object_selector and hasattr(context.scene.nna_twist_object_selector.data, "bones")):
			self.layout.prop(context.scene, "nna_twist_bone_selector", text="Source Bone")


def name_match_nna_twist(name: str) -> int:
	return name.find("Twist") # TODO use legit regex instead


nna_types = {
	"nna.twist": {
		"json_add": AddNNATwistComponentOperator.bl_idname,
		"json_edit": EditNNATwistComponentOperator.bl_idname,
		"json_display": display_nna_twist_component,
		"name_match": name_match_nna_twist,
		"name_set": NNATwistNameDefinitionOperator.bl_idname,
	},
}


def _build_bone_enum(self, context) -> list:
	if(bpy.context.scene.nna_twist_object_selector and hasattr(bpy.context.scene.nna_twist_object_selector.data, "bones")):
		ret = [((bone.name, bone.name, "")) for bone in bpy.context.scene.nna_twist_object_selector.data.bones]
		ret.append((("$", "", "")))
		return ret
	else:
		return []


def register():
	bpy.types.Scene.nna_twist_object_selector = bpy.props.PointerProperty(type=bpy.types.Object, name="source object", options={"SKIP_SAVE"}) # type: ignore
	bpy.types.Scene.nna_twist_bone_selector = bpy.props.EnumProperty(items=_build_bone_enum, name="source object", options={"SKIP_SAVE"}) # type: ignore

def unregister():
	if hasattr(bpy.types.Scene, "nna_twist_object_selector"):
		del bpy.types.Scene.nna_twist_object_selector
	if hasattr(bpy.types.Scene, "nna_twist_bone_selector"):
		del bpy.types.Scene.nna_twist_bone_selector
