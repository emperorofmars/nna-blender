import re
import bpy

from bl_ext.user_default.nna_blender.nna.components import NNA_Json_Add_Base, NNA_Json_Edit_Base, NNA_Name_Definition_Base
from bl_ext.user_default.nna_blender.nna.nna_registry import NNAFunctionType
from bl_ext.user_default.nna_blender.nna import utils

"""
from bl_ext.vscode_development.nna_blender.nna.components import NNA_Json_Add_Base, NNA_Json_Edit_Base, NNA_Name_Definition_Base
from bl_ext.vscode_development.nna_blender.nna.nna_registry import NNAFunctionType
from bl_ext.vscode_development.nna_blender.nna import utils
"""

_nna_name = "example.extension"


class AddExampleJsonComponent(bpy.types.Operator, NNA_Json_Add_Base):
	"""Example Add Json Component Operator"""
	bl_idname = "example.add_json_component"
	bl_label = "Add"

	def init(self) -> dict:
		return {"t": _nna_name, "foo": "bar"}


class EditExampleJsonComponent(bpy.types.Operator, NNA_Json_Edit_Base):
	"""Example Edit Json Component Operator"""
	bl_idname = "example.edit_json_component"
	bl_label = "Edit"

	foo: bpy.props.StringProperty(name="Foo") # type: ignore

	def parse(self, json_component: dict):
		self.foo = json_component.get("foo")

	def serialize(self, json_component: dict) -> dict:
		json_component["foo"] = self.foo
		return json_component

	def draw(self, context):
		self.layout.label(text="Super Awesome Example NNA Type")
		self.layout.prop(self, "foo")


def display_example_nna_json_component(target_id: str, layout: bpy.types.UILayout, json_component: dict, component_index: int):
	layout.label(text="Super Awesome Example NNA Type")
	row = layout.split(factor=0.4); row.label(text="Foo"); row.label(text=str(json_component["foo"]))


_Match = r"(?i)\$Example(?P<foo>[a-zA-Z0-9]*)(?P<side>([._\-|:][lr])|[._\-|:\s]?(right|left))?$"

class SetExampleNameDefinition(bpy.types.Operator, NNA_Name_Definition_Base):
	"""Set Example Name Definition"""
	bl_idname = "example.set_name_definition"
	bl_label = "Set Example Name Definition"

	foo: bpy.props.StringProperty(name="Foo") # type: ignore

	def parse(self, nna_name: str):
		match = re.search(_Match, nna_name)
		if(match):
			if(match.groupdict()["foo"]): self.foo = match.groupdict()["foo"]

	def serialize(self, target: bpy.types.Object | bpy.types.Bone, base_object: bpy.types.Object | None, nna_name: str, symmetry: str) -> str:
		match = re.search(_Match, nna_name)
		if(match): nna_name = nna_name[:match.start()]

		nna_name = nna_name + "$Example" + self.foo

		return nna_name + symmetry

	def draw(self, context):
		self.layout.label(text="Super Awesome Example NNA Type")
		self.layout.prop(self, "foo")


def name_match_example_name_definition(name: str) -> int:
	match = re.search(_Match, name)
	return -1 if not match else match.start()


def name_display_example_name_definition(layout: bpy.types.UILayout, name: str):
	if(match := re.search(_Match, name)):
		layout.label(text="Super Awesome Example NNA Type")
		row = layout.split(factor=0.4); row.label(text="Foo"); row.label(text=match.groupdict()["foo"])


nna_types = {
	_nna_name: {
		NNAFunctionType.JsonAdd: AddExampleJsonComponent.bl_idname,
		NNAFunctionType.JsonEdit: EditExampleJsonComponent.bl_idname,
		NNAFunctionType.JsonDisplay: display_example_nna_json_component,
		NNAFunctionType.NameSet: SetExampleNameDefinition.bl_idname,
		NNAFunctionType.NameMatch: name_match_example_name_definition,
		NNAFunctionType.NameDisplay: name_display_example_name_definition,
	},
}

def register():
	bpy.utils.register_class(AddExampleJsonComponent)
	bpy.utils.register_class(EditExampleJsonComponent)
	bpy.utils.register_class(SetExampleNameDefinition)

def unregister():
	bpy.utils.unregister_class(SetExampleNameDefinition)
	bpy.utils.unregister_class(EditExampleJsonComponent)
	bpy.utils.unregister_class(AddExampleJsonComponent)
