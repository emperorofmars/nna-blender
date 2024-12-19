import re
import bpy

from ...nna_registry import NNAFunctionType

from ... import nna_utils_json
from ... import nna_utils_name
from ... import nna_utils_tree


_nna_name = "ava.collider"


_MatchSphere = r"(?i)\$ColSphere(?P<inside_bounds>In)?(?P<radius>r[0-9]*[.][0-9]+)(?P<side>(([._\-|:][lr])|[._\-|:\s]?(right|left))$)?$"
_MatchCapsule = r"(?i)\$ColCapsule(?P<inside_bounds>In)?(?P<radius>r[0-9]*[.][0-9]+)(?P<height>h[0-9]*[.][0-9]+)(?P<side>(([._\-|:][lr])|[._\-|:\s]?(right|left))$)?$"
_MatchPlane = r"(?i)\$ColPlane(?P<inside_bounds>In)?(?P<side>(([._\-|:][lr])|[._\-|:\s]?(right|left))$)?$"


class SetAVAColliderNameDefinitionOperator(bpy.types.Operator):
	"""Define a collider"""

	bl_idname = "nna.set_ava_collider_name"
	bl_label = "AVA Collider"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore

	col_shape: bpy.props.EnumProperty(name="Shape", items=[("sphere", "Sphere", ""), ("capsule", "Capsule", ""), ("plane", "Plane", "")], default="sphere") # type: ignore
	inside_bounds: bpy.props.BoolProperty(name="Inside Bounds", default=False) # type: ignore
	radius: bpy.props.FloatProperty(name="Radius", default=0.1, min=0, soft_min=0.001, precision=3, step=3) # type: ignore
	height: bpy.props.FloatProperty(name="Height", default=0.2, min=0, soft_min=0.001, precision=3, step=3) # type: ignore

	def invoke(self, context, event):
		nna_name = nna_utils_name.get_nna_name(self.target_id)

		if(match := re.search(_MatchSphere, nna_name)):
			self.col_shape = "sphere"
			self.inside_bounds = True if match.groupdict()["inside_bounds"] else False
			self.radius = float(match.groupdict()["radius"][1:])
		elif(match := re.search(_MatchCapsule, nna_name)):
			self.col_shape = "capsule"
			self.inside_bounds = True if match.groupdict()["inside_bounds"] else False
			self.radius = float(match.groupdict()["radius"][1:])
			self.height = float(match.groupdict()["height"][1:])
		elif(match := re.search(_MatchPlane, nna_name)):
			self.col_shape = "plane"
			self.inside_bounds = True if match.groupdict()["inside_bounds"] else False

		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		try:
			target = nna_utils_tree.get_object_by_target_id(self.target_id)
			(nna_name, symmetry) = nna_utils_name.get_side_suffix(nna_utils_name.get_nna_name(self.target_id))

			if(match := (re.search(_MatchSphere, nna_name) or re.search(_MatchCapsule, nna_name) or re.search(_MatchPlane, nna_name))):
				nna_name = nna_name[:match.start()]

			if(self.col_shape == "sphere"):
				nna_name = nna_name + "$ColSphere"\
					+ ("In" if self.inside_bounds else "")\
					+ "R" + str(round(self.radius, 3))
			elif(self.col_shape == "capsule"):
				nna_name = nna_name + "$ColCapsule"\
					+ ("In" if self.inside_bounds else "")\
					+ "R" + str(round(self.radius, 3))\
					+ "H" + str(round(self.height, 3))
			elif(self.col_shape == "plane"):
				nna_name = nna_name + "$ColPlane"\
					+ ("In" if self.inside_bounds else "")

			nna_name += symmetry

			if(len(str.encode(nna_name)) > 63):
				self.report({'ERROR'}, "Name too long")
				return {"CANCELLED"}
			else:
				nna_utils_tree.reparent_nna_targeting_object(self.target_id, nna_utils_name.construct_nna_id(self.target_id, nna_name))
				target.name = nna_name
				self.report({'INFO'}, "Component successfully edited")
				return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}

	def draw(self, context):
		self.layout.prop(self, "col_shape", expand=True)
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
