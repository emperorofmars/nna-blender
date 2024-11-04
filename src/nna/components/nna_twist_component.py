import bpy
import json

from ..nna_name_utils import *
from ..nna_registry import *
from ..nna_json_utils import *

class AddNNATwistComponentOperator(bpy.types.Operator):
	bl_idname = "nna.add_nna_twist"
	bl_label = "Add Twist Component"
	bl_options = {"REGISTER", "UNDO"}
	
	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	
	def execute(self, context):
		try:
			nna_json = get_json_from_targetname(self.target_id)
			jsonText = add_component_to_nna(nna_json, json.dumps({"t":"nna.twist"}))
			serialize_json_to_targetname(self.target_id, jsonText)
			self.report({'INFO'}, "Component successfully added")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}


def display_nna_twist_component(object, layout, json):
	row = layout.row()
	row.label(text="weight")
	row.label(text=str(json["w"]) if "w" in json else "default (0.5)")
	row = layout.row()
	row.label(text="source")
	row.label(text=json["s"] if "s" in json else "default (grandparent)")


class EditNNATwistComponentOperator(bpy.types.Operator):
	bl_idname = "nna.edit_nna_twist"
	bl_label = "Edit Twist Component"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	component_index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore

	weight: bpy.props.FloatProperty(name="weight", default=0.5, min=0, max=1) # type: ignore
	
	def invoke(self, context, event):
		nna_json = get_json_from_targetname(self.target_id)
		json_component = json.loads(get_component_from_nna(nna_json, self.component_index))

		if("w" in json_component): self.weight = json_component["w"]
		if("s" in json_component): context.scene.nna_twist_object_selector = bpy.context.scene.objects[json_component["s"]]
		else: context.scene.nna_twist_object_selector = None

		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			nna_json = get_json_from_targetname(self.target_id)
			json_component = json.loads(get_component_from_nna(nna_json, self.component_index))

			if(self.weight != 0.5): json_component["w"] = self.weight
			if(context.scene.nna_twist_object_selector): json_component["s"] = context.scene.nna_twist_object_selector.name
			else: del json_component["s"]

			new_nna_json = replace_component_in_nna(nna_json, json.dumps(json_component), self.component_index)
			serialize_json_to_targetname(self.target_id, new_nna_json)

			self.report({'INFO'}, "Component successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.prop(self, "weight", text="Weight", expand=True)
		self.layout.prop_search(context.scene, "nna_twist_object_selector", bpy.data, "objects", text="Source")


class NNATwistNameDefinitionOperator(bpy.types.Operator):
	bl_idname = "nna.nna_twist_name_definition"
	bl_label = "NNA Twist Name Definition"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore

	weight: bpy.props.FloatProperty(name="weight", default=0.5, min=0, max=1) # type: ignore
	
	def invoke(self, context, event):
		(nna_name, symmetry) = get_symmetry(get_nna_name(self.target_id))

		# TODO parse values
		#if("w" in json_component): self.weight = json_component["w"]
		#if("s" in json_component): context.scene.nna_twist_object_selector = bpy.context.scene.objects[json_component["s"]]
		#else: context.scene.nna_twist_object_selector = None


		context.scene.nna_twist_object_selector = None

		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			target = get_object_by_target_id(self.target_id)
			(nna_name, symmetry) = get_symmetry(get_nna_name(self.target_id))

			nna_name = nna_name + "Twist"
			if(self.weight != 0.5): nna_name += str(round(self.weight, 2))
			if(context.scene.nna_twist_object_selector): nna_name += context.scene.nna_twist_object_selector.name

			target.name = nna_name + symmetry

			self.report({'INFO'}, "Component successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.prop(self, "weight", text="Weight", expand=True)
		self.layout.prop_search(context.scene, "nna_twist_object_selector", bpy.data, "objects", text="Source")


nna_types = {
	"nna.twist": {
		"json_add": AddNNATwistComponentOperator.bl_idname,
		"json_edit": EditNNATwistComponentOperator.bl_idname,
		"json_display": display_nna_twist_component,
		"name": NNATwistNameDefinitionOperator.bl_idname,
	},
}


def register():
	bpy.types.Scene.nna_twist_object_selector = bpy.props.PointerProperty(type=bpy.types.Object, name="source object", options={"SKIP_SAVE"}) # type: ignore

def unregister():
	if hasattr(bpy.types.Scene, "nna_twist_object_selector"):
		del bpy.types.Scene.nna_twist_object_selector
