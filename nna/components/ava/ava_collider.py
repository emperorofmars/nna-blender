import re
import bpy

from ...nna_registry import NNAFunctionType

from ..base_edit_name import NNA_Name_Definition_Base


_nna_name = "ava.collider"


_MatchSphere = r"(?i)\$ColSphere(?P<inside_bounds>In)?(?P<radius>r[0-9]*[.][0-9]+)(?P<default_disabled>D)?(?P<side>(([._\-|:][lr])|[._\-|:\s]?(right|left))$)?$"
_MatchCapsule = r"(?i)\$ColCapsule(?P<inside_bounds>In)?(?P<radius>r[0-9]*[.][0-9]+)(?P<height>h[0-9]*[.][0-9]+)(?P<default_disabled>D)?(?P<side>(([._\-|:][lr])|[._\-|:\s]?(right|left))$)?$"
_MatchPlane = r"(?i)\$ColPlane(?P<inside_bounds>In)?(?P<default_disabled>D)?(?P<side>(([._\-|:][lr])|[._\-|:\s]?(right|left))$)?$"


class SetAVAColliderNameDefinitionOperator(bpy.types.Operator, NNA_Name_Definition_Base):
	"""Define a collider"""
	bl_idname = "nna.set_ava_collider_name"
	bl_label = "AVA Collider"

	default_clear_definition_on_import = True

	col_shape: bpy.props.EnumProperty(name="Shape", items=[("sphere", "Sphere", ""), ("capsule", "Capsule", ""), ("plane", "Plane", "")], default="sphere") # type: ignore
	inside_bounds: bpy.props.BoolProperty(name="Inside Bounds", default=False) # type: ignore
	default_disabled: bpy.props.BoolProperty(name="Disabled by Default", default=False) # type: ignore
	radius: bpy.props.FloatProperty(name="Radius", default=0.1, min=0, soft_min=0.001, precision=3, step=3) # type: ignore
	height: bpy.props.FloatProperty(name="Height", default=0.2, min=0, soft_min=0.001, precision=3, step=3) # type: ignore

	def parse(self, nna_name: str):
		if(match := re.search(_MatchSphere, nna_name)):
			self.col_shape = "sphere"
			self.inside_bounds = True if match.groupdict()["inside_bounds"] else False
			self.default_disabled = True if match.groupdict()["default_disabled"] else False
			self.radius = float(match.groupdict()["radius"][1:])
		elif(match := re.search(_MatchCapsule, nna_name)):
			self.col_shape = "capsule"
			self.inside_bounds = True if match.groupdict()["inside_bounds"] else False
			self.default_disabled = True if match.groupdict()["default_disabled"] else False
			self.radius = float(match.groupdict()["radius"][1:])
			self.height = float(match.groupdict()["height"][1:])
		elif(match := re.search(_MatchPlane, nna_name)):
			self.col_shape = "plane"
			self.default_disabled = True if match.groupdict()["default_disabled"] else False

	def serialize(self, target: bpy.types.Object | bpy.types.Bone, base_object: bpy.types.Object | None, nna_name: str, symmetry: str) -> str:
		if(match := (re.search(_MatchSphere, nna_name) or re.search(_MatchCapsule, nna_name) or re.search(_MatchPlane, nna_name))):
			nna_name = nna_name[:match.start()]

		if(self.col_shape == "sphere"):
			nna_name = nna_name + "$ColSphere"\
				+ ("In" if self.inside_bounds else "")\
				+ "R" + str(round(self.radius, 3))\
				+ ("D" if self.default_disabled else "")
		elif(self.col_shape == "capsule"):
			nna_name = nna_name + "$ColCapsule"\
				+ ("In" if self.inside_bounds else "")\
				+ "R" + str(round(self.radius, 3))\
				+ "H" + str(round(self.height, 3))\
				+ ("D" if self.default_disabled else "")
		elif(self.col_shape == "plane"):
			nna_name = nna_name + "$ColPlane"\
				+ ("D" if self.default_disabled else "")

		return nna_name + symmetry

	def draw(self, context):
		NNA_Name_Definition_Base.draw(self, context)

		self.layout.prop(self, "col_shape", expand=True)
		self.layout.prop(self, "default_disabled", expand=True)
		self.layout.prop(self, "inside_bounds", expand=True)
		if(self.col_shape in ["sphere", "capsule"]): self.layout.prop(self, "radius", expand=True)
		if(self.col_shape in ["capsule"]): self.layout.prop(self, "height", expand=True)


def name_match_ava_collider(name: str) -> int:
	if(match := (re.search(_MatchSphere, name) or re.search(_MatchCapsule, name) or re.search(_MatchPlane, name))):
		return match.start()
	else:
		return -1

def name_display_ava_collider(layout: bpy.types.UILayout, name: str):
	if(match := re.search(_MatchSphere, name)):
		row = layout.row(); row.label(text="Shape"); row.label(text="Sphere")
		row = layout.row(); row.label(text="Inside Bounds"); row.label(text="Yes" if match.groupdict()["inside_bounds"] else "No")
		row = layout.row(); row.label(text="Radius"); row.label(text=match.groupdict()["radius"][1:])
	elif(match := re.search(_MatchCapsule, name)):
		row = layout.row(); row.label(text="Shape"); row.label(text="Capsule")
		row = layout.row(); row.label(text="Inside Bounds"); row.label(text="Yes" if match.groupdict()["inside_bounds"] else "No")
		row = layout.row(); row.label(text="Radius"); row.label(text=match.groupdict()["radius"][1:])
		row = layout.row(); row.label(text="Height"); row.label(text=match.groupdict()["height"][1:])
	elif(match := re.search(_MatchPlane, name)):
		row = layout.row(); row.label(text="Shape"); row.label(text="Capsule")
		row = layout.row(); row.label(text="Inside Bounds"); row.label(text="Yes" if match.groupdict()["inside_bounds"] else "No")


nna_types = {
	_nna_name: {
		NNAFunctionType.NameSet: SetAVAColliderNameDefinitionOperator.bl_idname,
		NNAFunctionType.NameMatch: name_match_ava_collider,
		NNAFunctionType.NameDisplay: name_display_ava_collider,
	},
}
