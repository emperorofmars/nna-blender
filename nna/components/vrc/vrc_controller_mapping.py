import bpy

from ...nna_registry import NNAFunctionType

from ... import nna_utils_name
from ... import nna_utils_json
from ... import nna_utils_tree

_nna_name = "vrc.controller_mapping"


class AddVRCControllerMappingComponentOperator(bpy.types.Operator):
	"""This component will search for the appropriate Animator Controller in Unity and assign them on import."""
	bl_idname = "nna.add_vrc_controller_mapping"
	bl_label = "Add VRChat Controller Mapping Component"
	bl_options = {"REGISTER", "UNDO"}
	
	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	
	def execute(self, context):
		try:
			nna_utils_json.add_component(self.target_id, {
				"t": _nna_name,
				"base": None,
				"additive": None,
				"gesture": None,
				"action": None,
				"fx": None,
				"sitting": None,
				"tpose": None,
				"ikpose": None,
				"parameters": None,
				"menu": None,
			})
			self.report({'INFO'}, "Component successfully added")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}


class EditVRCControllerMappingComponentOperator(bpy.types.Operator):
	"""This component will search for the appropriate Animator Controller in Unity and assign them on import."""
	bl_idname = "nna.edit_vrc_controller_mapping"
	bl_label = "Edit VRChat Controller Mapping"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	component_index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore

	base: bpy.props.StringProperty(name="Base", default="") # type: ignore
	additive: bpy.props.StringProperty(name="Additive", default="") # type: ignore
	gesture: bpy.props.StringProperty(name="Gesture", default="") # type: ignore
	action: bpy.props.StringProperty(name="Action", default="") # type: ignore
	fx: bpy.props.StringProperty(name="FX", default="") # type: ignore
	
	sitting: bpy.props.StringProperty(name="Sitting", default="") # type: ignore
	tpose: bpy.props.StringProperty(name="TPose", default="") # type: ignore
	ikpose: bpy.props.StringProperty(name="IKPose", default="") # type: ignore
	
	parameters: bpy.props.StringProperty(name="Parameters", default="") # type: ignore
	menu: bpy.props.StringProperty(name="Menu", default="") # type: ignore
	
	def invoke(self, context, event):
		json_component = nna_utils_json.get_component(self.target_id, self.component_index)
		if("base" in json_component): self.base = json_component["base"]
		if("additive" in json_component): self.additive = json_component["additive"]
		if("gesture" in json_component): self.gesture = json_component["gesture"]
		if("action" in json_component): self.action = json_component["action"]
		if("fx" in json_component): self.fx = json_component["fx"]
		if("sitting" in json_component): self.sitting = json_component["sitting"]
		if("tpose" in json_component): self.tpose = json_component["tpose"]
		if("ikpose" in json_component): self.base = json_component["ikpose"]
		if("parameters" in json_component): self.parameters = json_component["parameters"]
		if("menu" in json_component): self.menu = json_component["menu"]
		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			json_component = nna_utils_json.get_component(self.target_id, self.component_index)

			if(self.base): json_component["base"] = self.base
			elif("base" in json_component): del json_component["base"]
			if(self.additive): json_component["additive"] = self.additive
			elif("additive" in json_component): del json_component["additive"]
			if(self.gesture): json_component["gesture"] = self.gesture
			elif("gesture" in json_component): del json_component["gesture"]
			if(self.action): json_component["action"] = self.action
			elif("action" in json_component): del json_component["action"]
			if(self.fx): json_component["fx"] = self.fx
			elif("fx" in json_component): del json_component["fx"]
			if(self.sitting): json_component["sitting"] = self.sitting
			elif("sitting" in json_component): del json_component["sitting"]
			if(self.tpose): json_component["tpose"] = self.tpose
			elif("tpose" in json_component): del json_component["tpose"]
			if(self.ikpose): json_component["ikpose"] = self.ikpose
			elif("ikpose" in json_component): del json_component["ikpose"]
			if(self.parameters): json_component["parameters"] = self.parameters
			elif("parameters" in json_component): del json_component["parameters"]
			if(self.menu): json_component["menu"] = self.menu
			elif("menu" in json_component): del json_component["menu"]

			nna_utils_json.replace_component(self.target_id, json_component, self.component_index)
			self.report({'INFO'}, "Component successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.prop(self, "base", expand=True)
		self.layout.prop(self, "additive", expand=True)
		self.layout.prop(self, "gesture", expand=True)
		self.layout.prop(self, "action", expand=True)
		self.layout.prop(self, "fx", expand=True)
		self.layout.separator(factor=1)
		self.layout.prop(self, "sitting", expand=True)
		self.layout.prop(self, "tpose", expand=True)
		self.layout.prop(self, "ikpose", expand=True)
		self.layout.separator(factor=1)
		self.layout.prop(self, "parameters", expand=True)
		self.layout.prop(self, "menu", expand=True)


def display_vrc_controller_mapping_component(target_id: str, layout: bpy.types.UILayout, json_component: dict):
	if("base" in json_component): row = layout.row(); row.label(text="Base"); row.label(text=json_component["base"])
	if("additive" in json_component): row = layout.row(); row.label(text="Additive"); row.label(text=json_component["additive"])
	if("gesture" in json_component): row = layout.row(); row.label(text="Gesture"); row.label(text=json_component["gesture"])
	if("action" in json_component): row = layout.row(); row.label(text="Action"); row.label(text=json_component["action"])
	if("fx" in json_component): row = layout.row(); row.label(text="FX"); row.label(text=json_component["fx"])
	if("sitting" in json_component): row = layout.row(); row.label(text="Sitting"); row.label(text=json_component["sitting"])
	if("tpose" in json_component): row = layout.row(); row.label(text="TPose"); row.label(text=json_component["tpose"])
	if("ikpose" in json_component): row = layout.row(); row.label(text="IKPose"); row.label(text=json_component["ikpose"])
	if("parameters" in json_component): row = layout.row(); row.label(text="Parameters"); row.label(text=json_component["parameters"])
	if("menu" in json_component): row = layout.row(); row.label(text="Menu"); row.label(text=json_component["menu"])


nna_types = {
	_nna_name: {
		NNAFunctionType.JsonAdd: AddVRCControllerMappingComponentOperator.bl_idname,
		NNAFunctionType.JsonEdit: EditVRCControllerMappingComponentOperator.bl_idname,
		NNAFunctionType.JsonDisplay: display_vrc_controller_mapping_component,
	},
}
