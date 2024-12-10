# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import bpy
import re

from ...nna_registry import NNAFunctionType

from ... import nna_utils_name
from ... import nna_utils_json
from ... import nna_utils_tree
from ... import nna_operators_selector


_nna_name = "nna.twist"


class AddNNATwistComponentOperator(bpy.types.Operator):
	"""Specifies a twist-bone constraint"""
	bl_idname = "nna.add_nna_twist"
	bl_label = "Add Twist Component"
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


class EditNNATwistComponentOperator(bpy.types.Operator):
	"""Specifies a twist-bone constraint"""
	bl_idname = "nna.edit_nna_twist"
	bl_label = "Edit Twist Component"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	component_index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore

	weight: bpy.props.FloatProperty(name="weight", default=0.5, min=0, max=1, precision=2, step=2) # type: ignore

	def invoke(self, context, event):
		json_component = nna_utils_json.get_component(self.target_id, self.component_index)

		if("w" in json_component): self.weight = json_component["w"]
		nna_operators_selector.init_selector_relative(self.target_id, json_component.get("s"))

		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		try:
			json_component = nna_utils_json.get_component(self.target_id, self.component_index)

			if(self.weight != 0.5): json_component["w"] = self.weight

			source_id = nna_operators_selector.get_selected_target_id_relative(self.target_id)
			if(source_id):
				json_component["s"] = source_id
			elif("s" in json_component):
				del json_component["s"]

			nna_utils_json.replace_component(self.target_id, json_component, self.component_index)
			self.report({'INFO'}, "Component successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}

	def draw(self, context):
		self.layout.prop(self, "weight", text="Weight", expand=True)
		self.layout.label(text="Source")
		nna_operators_selector.draw_selector_prop(self.target_id, self.layout)


def display_nna_twist_component(target_id: str, layout: bpy.types.UILayout, json_component: dict, component_index: int):
	row = layout.split(factor=0.4); row.label(text="Weight"); row.label(text=str(json_component.get("w", "default (0.5)")))
	row = layout.split(factor=0.4); row.label(text="Source"); row.label(text=str(json_component.get("s", "default (grandparent)")))


class NNATwistNameDefinitionOperator(bpy.types.Operator):
	"""Specifies a twist-bone constraint"""
	bl_idname = "nna.nna_twist_name_definition"
	bl_label = "NNA Twist Name Definition"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore

	weight: bpy.props.FloatProperty(name="weight", default=0.5, min=0, max=1, precision=2, step=2) # type: ignore

	def invoke(self, context, event):
		name = nna_utils_name.get_nna_name(self.target_id)
		match = re.search(_Match, name)
		if(match and match.groupdict()["weight"]): self.weight = float(match.groupdict()["weight"])

		if(match and match.groupdict()["source_node_path"]):
			nna_operators_selector.init_selector_relative(self.target_id, match.groupdict()["source_node_path"], target_split_char="&")
		else:
			nna_operators_selector.init_selector()

		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		try:
			target = nna_utils_tree.get_object_by_target_id(self.target_id)
			base_object = nna_utils_tree.get_base_object_by_target_id(self.target_id)
			(nna_name, symmetry) = nna_utils_name.get_symmetry(nna_utils_name.get_nna_name(self.target_id))

			match = re.search(_Match, nna_name)
			if(match): nna_name = nna_name[:match.start()]

			nna_name = nna_name + "$Twist"

			source_id = nna_operators_selector.get_selected_target_id_relative(self.target_id, target_split_char="&")
			if(source_id):
				nna_name += source_id
				if(self.weight != 0.5): nna_name += ","

			if(self.weight != 0.5): nna_name += str(round(self.weight, 2))

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
		self.layout.prop(self, "weight", text="Weight", expand=True)
		self.layout.label(text="Source")
		nna_operators_selector.draw_selector_prop(self.target_id, self.layout)


_Match = r"(?i)\$twist(?P<source_node_path>[a-zA-Z][a-zA-Z0-9._\-|:\s]*(\&[a-zA-Z][a-zA-Z0-9._\-|:\s]*)*)?,?(?P<weight>[0-9]*[.][0-9]+)?(?P<side>(([._\-|:][lr])|[._\-|:\s]?(right|left))$)?$"

def name_match_nna_twist(name: str) -> int:
	match = re.search(_Match, name)
	return -1 if not match else match.start()

def name_display_nna_twist(layout: bpy.types.UILayout, name: str):
	match = re.search(_Match, name)
	row = layout.split(factor=0.4); row.label(text="Weight"); row.label(text=str(match.groupdict()["weight"]) if match.groupdict()["weight"] else "default (0.5)")
	row = layout.split(factor=0.4); row.label(text="Source"); row.label(text=match.groupdict()["source_node_path"] if match.groupdict()["source_node_path"] else "default (grandparent)")


nna_types = {
	_nna_name: {
		NNAFunctionType.JsonAdd: AddNNATwistComponentOperator.bl_idname,
		NNAFunctionType.JsonEdit: EditNNATwistComponentOperator.bl_idname,
		NNAFunctionType.JsonDisplay: display_nna_twist_component,
		NNAFunctionType.NameSet: NNATwistNameDefinitionOperator.bl_idname,
		NNAFunctionType.NameMatch: name_match_nna_twist,
		NNAFunctionType.NameDisplay: name_display_nna_twist
	},
}
