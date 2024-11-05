import bpy
import json

from .. import nna_name_utils
from .. import nna_json_utils
from .. import nna_tree_utils


class AddNNAHumanoidComponentOperator(bpy.types.Operator):
	bl_idname = "nna.add_nna_humanoid"
	bl_label = "Add Humanoid Component"
	bl_options = {"REGISTER", "UNDO"}
	
	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	
	def execute(self, context):
		try:
			nna_json_utils.add_component(self.target_id, json.dumps({"t":"nna.humanoid"}))
			self.report({'INFO'}, "Component successfully added")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}


def display_nna_humanoid_component(object, layout, json_dict):
	row = layout.row()
	row.label(text="Locomotion Type")
	row.label(text=json_dict["lc"] if "lc" in json_dict else "default (planti)")
	row = layout.row()
	row.label(text="No Jaw Mapping")
	row.label(text=str(json_dict["nj"]) if "nj" in json_dict else "default (False)")


class EditNNAHumanoidComponentOperator(bpy.types.Operator):
	bl_idname = "nna.edit_nna_humanoid"
	bl_label = "Edit Humanoid Component"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	component_index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore

	locomotion_type: bpy.props.EnumProperty(items=[("planti", "Plantigrade", ""),("digi", "Digitigrade", "")], name="Locomotion Type", default="planti") # type: ignore
	no_jaw: bpy.props.BoolProperty(name="No Jaw Mapping", default=False) # type: ignore
	
	def invoke(self, context, event):
		json_component = nna_json_utils.get_component_dict(self.target_id, self.component_index)

		if("lc" in json_component): self.locomotion_type = json_component["lc"]
		if("nj" in json_component): self.no_jaw = json_component["nj"]

		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			json_component = nna_json_utils.get_component_dict(self.target_id, self.component_index)

			if(self.locomotion_type != "planti"): json_component["lc"] = self.locomotion_type
			elif("lc" in json_component): del json_component["lc"]

			if(self.no_jaw == True): json_component["nj"] = True
			elif("nj" in json_component): del json_component["nj"]

			nna_json_utils.replace_component(self.target_id, json.dumps(json_component), self.component_index)
			self.report({'INFO'}, "Component successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.prop(self, "locomotion_type", expand=True)
		self.layout.prop(self, "no_jaw", expand=True)


def name_match_nna_humanoid(name: str) -> int:
	return name.find("Humanoid") # TODO use legit regex instead


class NNAHumanoidNameDefinitionOperator(bpy.types.Operator):
	bl_idname = "nna.nna_humanoid_name_definition"
	bl_label = "NNA Humanoid Name Definition"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	
	locomotion_type: bpy.props.EnumProperty(items=[("planti", "Plantigrade", ""),("digi", "Digitigrade", "")], name="Locomotion Type", default="planti") # type: ignore
	no_jaw: bpy.props.BoolProperty(name="No Jaw Mapping", default=False) # type: ignore

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

			nna_name = nna_name + "Humanoid"
			
			if(self.locomotion_type != "planti"): nna_name += str(self.locomotion_type).capitalize()
			if(self.no_jaw == True): nna_name += "NoJaw"

			target.name = nna_name + symmetry

			self.report({'INFO'}, "Component successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.prop(self, "locomotion_type", expand=True)
		self.layout.prop(self, "no_jaw", expand=True)


nna_types = {
	"nna.humanoid": {
		"json_add": AddNNAHumanoidComponentOperator.bl_idname,
		"json_edit": EditNNAHumanoidComponentOperator.bl_idname,
		"json_display": display_nna_humanoid_component,
		"name_match": name_match_nna_humanoid,
		"name_set": NNAHumanoidNameDefinitionOperator.bl_idname
	},
}
