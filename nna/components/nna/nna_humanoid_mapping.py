# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import re
import bpy

from ...nna_registry import NNAFunctionType

from ... import nna_utils_name
from ... import nna_utils_json
from ... import nna_utils_tree


_nna_name = "nna.humanoid"


class AddNNAHumanoidComponentOperator(bpy.types.Operator):
	"""Specifies options for the automapping of the Unity compatible humanoid rig"""
	bl_idname = "nna.add_nna_humanoid"
	bl_label = "Add Humanoid Component"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore

	def execute(self, context):
		try:
			nna_utils_json.add_component(self.target_id, {"t":_nna_name})
			self.report({'INFO'}, "Component successfully added")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}


class EditNNAHumanoidComponentOperator(bpy.types.Operator):
	"""Specifies options for the automapping of the Unity compatible humanoid rig"""
	bl_idname = "nna.edit_nna_humanoid"
	bl_label = "Edit Humanoid Component"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	component_index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore

	locomotion_type: bpy.props.EnumProperty(items=[("planti", "Plantigrade", ""),("digi", "Digitigrade", "")], name="Locomotion Type", default="planti") # type: ignore
	no_jaw: bpy.props.BoolProperty(name="No Jaw Mapping", default=False) # type: ignore

	def invoke(self, context, event):
		json_component = nna_utils_json.get_component(self.target_id, self.component_index)

		if("lc" in json_component): self.locomotion_type = json_component["lc"]
		if("nj" in json_component): self.no_jaw = json_component["nj"]

		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		try:
			json_component = nna_utils_json.get_component(self.target_id, self.component_index)

			if(self.locomotion_type != "planti"): json_component["lc"] = self.locomotion_type
			elif("lc" in json_component): del json_component["lc"]

			if(self.no_jaw == True): json_component["nj"] = True
			elif("nj" in json_component): del json_component["nj"]

			nna_utils_json.replace_component(self.target_id, json_component, self.component_index)
			self.report({'INFO'}, "Component successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}

	def draw(self, context):
		self.layout.prop(self, "locomotion_type", expand=True)
		self.layout.prop(self, "no_jaw", expand=True)


def display_nna_humanoid_component(target_id: str, layout: bpy.types.UILayout, json_component: dict, component_index: int):
	row = layout.split(factor=0.4)
	row.label(text="Locomotion Type")
	row.label(text=json_component["lc"] if "lc" in json_component else "default (planti)")
	row = layout.split(factor=0.4)
	row.label(text="No Jaw Mapping")
	row.label(text=str(json_component["nj"]) if "nj" in json_component else "default (False)")


class NNAHumanoidNameDefinitionOperator(bpy.types.Operator):
	"""Specifies options for the automapping of the Unity compatible humanoid rig"""
	bl_idname = "nna.nna_humanoid_name_definition"
	bl_label = "NNA Humanoid Name Definition"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name="target_id") # type: ignore

	locomotion_type: bpy.props.EnumProperty(items=[("planti", "Plantigrade", ""),("digi", "Digitigrade", "")], name="Locomotion Type", default="planti") # type: ignore
	no_jaw: bpy.props.BoolProperty(name="No Jaw Mapping", default=False) # type: ignore

	def invoke(self, context, event):
		name = nna_utils_name.get_nna_name(self.target_id)
		match = re.search(_Match, name)
		if(match):
			if(match.groupdict()["digi"]): self.locomotion_type = "digi"
			if(match.groupdict()["no_jaw"]): self.no_jaw = True

		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		try:
			target = nna_utils_tree.get_object_by_target_id(self.target_id)
			(nna_name, symmetry) = nna_utils_name.get_symmetry(nna_utils_name.get_nna_name(self.target_id))

			match = re.search(_Match, nna_name)
			if(match): nna_name = nna_name[:match.start()]

			nna_name = nna_name + "$Humanoid"

			if(self.locomotion_type != "planti"): nna_name += str(self.locomotion_type).capitalize()
			if(self.no_jaw == True): nna_name += "NoJaw"

			nna_name += symmetry

			if(len(str.encode(nna_name)) > 63):
				self.report({'ERROR'}, "Name too long")
				return {"CANCELLED"}
			else:
				target.name = nna_name
				self.report({'INFO'}, "Component successfully edited")
				return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}

	def draw(self, context):
		self.layout.prop(self, "locomotion_type", expand=True)
		self.layout.prop(self, "no_jaw", expand=True)


_Match = r"(?i)\$humanoid(?P<digi>digi)?(?P<no_jaw>nojaw)?(([._\-|:][lr])|[._\-|:\s]?(right|left))?$"

def name_match_nna_humanoid(name: str) -> int:
	match = re.search(_Match, name)
	return -1 if not match else match.start()

def name_display_nna_humanoid(layout: bpy.types.UILayout, name: str):
	match = re.search(_Match, name)
	row = layout.row()
	row.label(text="Locomotion Type")
	row.label(text="Digitigrade" if match.groupdict()["digi"] else "default (Plantigrade)")
	row = layout.row()
	row.label(text="No Jaw Mapping")
	row.label(text="True" if match.groupdict()["no_jaw"] else "False")


nna_types = {
	_nna_name: {
		NNAFunctionType.JsonAdd: AddNNAHumanoidComponentOperator.bl_idname,
		NNAFunctionType.JsonEdit: EditNNAHumanoidComponentOperator.bl_idname,
		NNAFunctionType.JsonDisplay: display_nna_humanoid_component,
		NNAFunctionType.NameSet: NNAHumanoidNameDefinitionOperator.bl_idname,
		NNAFunctionType.NameMatch: name_match_nna_humanoid,
		NNAFunctionType.NameDisplay: name_display_nna_humanoid
	},
}
