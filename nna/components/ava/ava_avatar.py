import bpy

from ...nna_operators_util import CreateNewObjectOperator, SetActiveObjectOperator

from ... import nna_utils_name
from ... import nna_utils_json
from ... import nna_utils_tree


class AddAVAAvatarComponentOperator(bpy.types.Operator):
	bl_idname = "ava.add_ava_avatar"
	bl_label = "Add AVA Avatar Component"
	bl_options = {"REGISTER", "UNDO"}
	
	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	
	def execute(self, context):
		try:
			nna_utils_json.add_component(self.target_id, {"t":"ava.avatar"})
			self.report({'INFO'}, "Component successfully added")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}


def display_ava_avatar_component(object, layout, json_dict):
	autodect = "auto" in json_dict and not json_dict["auto"]
	row = layout.row()
	row.label(text="Automap")
	row.label(text="False" if autodect else "True")

	viewport_object = bpy.data.objects.get("ViewportFirstPerson")
	if(viewport_object):
		row = layout.row()
		row.label(text="Viewport defined by 'ViewportFirstPerson'")
		row.operator(SetActiveObjectOperator.bl_idname).target_name = "ViewportFirstPerson"
	else:
		row = layout.row()
		row.operator(CreateNewObjectOperator.bl_idname, text="Create Viewport Object").target_name = "ViewportFirstPerson"



nna_types = {
	"ava.avatar": {
		"json_add": AddAVAAvatarComponentOperator.bl_idname,
#		"json_edit": EditNNATwistComponentOperator.bl_idname,
		"json_display": display_ava_avatar_component,
#		"name_set": NNATwistNameDefinitionOperator.bl_idname,
#		"name_match": name_match_nna_twist,
#		"name_display": name_display_nna_twist
	},
	"ava.viewport_first_person": {
#		"name_match": name_match_nna_twist,
	}
}
