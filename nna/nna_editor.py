import json
import bpy

from . import nna_meta

from .exporter.export_helper import NNAExportFBX

from . import nna_operators_common
from . import nna_operators_raw_json
from . import nna_registry
from . import nna_utils_tree
from . import nna_utils_json


class NNAObjectPanel(bpy.types.Panel):
	"""Display the NNA editor for Blender objects"""
	bl_idname = "OBJECT_PT_nna_editor"
	bl_label = "NNA Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_category = "NNA"
	bl_context = "object"

	@classmethod
	def poll(cls, context):
		return (context.object is not None)

	def draw_header(self, context):
		pass
		
	def draw(self, context):
		draw_nna_editor(self, context, context.object.name, nna_utils_tree.determine_nna_object_state(context.object))


class NNABonePanel(bpy.types.Panel):
	"""Display the NNA editor for Blender bones"""
	bl_idname = "OBJECT_PT_nna_bone_editor"
	bl_label = "NNA Bone Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_category = "NNA"
	bl_context = "bone"

	@classmethod
	def poll(cls, context):
		return (context.object is not None)

	def draw_header(self, context):
		pass
		
	def draw(self, context):
		draw_nna_editor(self, context, context.object.name + "$" + context.bone.name, nna_utils_tree.determine_nna_bone_state(context.object, context.bone))


def draw_nna_editor(self, context, target_id, state):
	match state:
		case nna_utils_tree.NNAObjectState.IsRootObject:
			self.layout.operator(NNAExportFBX.bl_idname)
			self.layout.separator(type="LINE", factor=2)

			_draw_meta_editor(self, context)
			self.layout.separator(type="LINE", factor=2)

			button = self.layout.operator(nna_operators_common.CreateNNATargetingObjectOperator.bl_idname, text="Initializie NNA for the Export Root")
			button.target_id = target_id
		case nna_utils_tree.NNAObjectState.IsRootObjectWithTargeting:
			self.layout.operator(NNAExportFBX.bl_idname)
			self.layout.separator(type="LINE", factor=2)

			_draw_meta_editor(self, context)
			self.layout.separator(type="LINE", factor=2)

			self.layout.label(text="This is the NNA definition for: The Scene Root")
			_draw_nna_json_editor(self, context, target_id)
		case nna_utils_tree.NNAObjectState.NotInited:
			_draw_nna_name_editor(self, context, target_id)
			self.layout.separator(type="LINE", factor=2)
			box = self.layout.box()
			box.label(text="NNA Components Not Enabled")
			button = box.operator(operator=nna_operators_common.InitializeNNAOperator.bl_idname)
			button.nna_init_collection = context.collection.name
		case nna_utils_tree.NNAObjectState.InitedOutsideTree:
			_draw_nna_name_editor(self, context, target_id)
			self.layout.separator(type="LINE", factor=2)
			box = self.layout.box()
			box.label(text="This Node is outside the NNA Collection!")
		case nna_utils_tree.NNAObjectState.InitedInsideTree:
			if(not _draw_nna_name_editor(self, context, target_id)):
				self.layout.separator(type="LINE", factor=2)
				box = self.layout.box()
				box.label(text="NNA Components Not Enabled")
				button = box.operator(nna_operators_common.CreateNNATargetingObjectOperator.bl_idname)
				button.target_id = target_id
		case nna_utils_tree.NNAObjectState.IsTargetingObject:
			if(target_id == "$root"):
				self.layout.label(text="This is the NNA definition for: The Scene Root")
				_draw_nna_json_editor(self, context, "$nna")
			else:
				self.layout.label(text="This is the NNA definition for: " + target_id[8:])
				_draw_nna_editors_for_target(self, context, target_id[8:])
		case nna_utils_tree.NNAObjectState.IsJsonDefinition:
			if(not context.object.parent.name[8:]):
				self.layout.label(text="This part of the NNA definition for: The Scene Root" + context.object.parent.name[8:])
				_draw_nna_json_editor(self, context, "$nna")
			else:
				self.layout.label(text="This part of the NNA definition for: " + context.object.parent.name[8:])
				_draw_nna_editors_for_target(self, context, context.object.parent.name[8:])
		case nna_utils_tree.NNAObjectState.IsInvalidTargetingObject:
			self.layout.label(text="Invalid Target: '" + context.object.name[8:] + "' does NOT exist!")
		case nna_utils_tree.NNAObjectState.HasTargetingObject:
			_draw_nna_editors_for_target(self, context, target_id)

def _draw_nna_editors_for_target(self, context, target_id):
	if(_draw_nna_name_editor(self, context, target_id, True)):
		box = self.layout.box()
		box.label(text="Warning: This Node has both a Name and Component definition.")
		box.label(text="It is recommended to use only one.")
	_draw_nna_json_editor(self, context, target_id)


def _draw_meta_editor(self, context):
	meta = nna_utils_tree.determine_nna_meta()
	box = self.layout.box()
	box.label(text="Asset Meta")
	if(meta):
		json_text = nna_utils_json.get_json_from_targeting_object(meta)
		json_meta = json.loads(json_text) if json_text else {}

		row = box.row(); row.label(text="Name"); row.label(text=json_meta["name"] if "name" in json_meta else "not set")
		if("version" in json_meta): row = box.row(); row.label(text="Version"); row.label(text=json_meta["version"])
		row = box.row(); row.label(text="Author"); row.label(text=json_meta["author"] if "author" in json_meta else "not set")
		if("url" in json_meta): row = box.row(); row.label(text="URL"); row.label(text=json_meta["url"])
		if("license" in json_meta): row = box.row(); row.label(text="License"); row.label(text=json_meta["license"])
		if("license_url" in json_meta): row = box.row(); row.label(text="License Link"); row.label(text=json_meta["license_url"])
		if("documentation" in json_meta): row = box.row(); row.label(text="Documentation"); row.label(text=json_meta["documentation"])
		if("documentation_url" in json_meta): row = box.row(); row.label(text="Documentation Link"); row.label(text=json_meta["documentation_url"])
		if(len(json_meta.keys()) > 8):
			box.separator(factor=1)
			row = box.row(); row.label(text="Custom Properties")
			for property in json_meta.keys():
				if(property in ["name", "version", "author", "url", "license", "license_url", "documentation", "documentation_url"]): continue
				row = json_meta.row(); row.label(text=property); row.label(text=str(json_meta[property]))
		box.operator(nna_meta.EditNNAMetaOperator.bl_idname)
	else:
		box.operator(nna_meta.SetupNNAMetaOperator.bl_idname)


def _draw_nna_name_editor(self, context, target_id, ignore_no_match = False) -> bool:
	name_match_operators = nna_registry.get_nna_operators(nna_registry.NNAFunctionType.NameMatch)
	name_draw_operators = nna_registry.get_nna_operators(nna_registry.NNAFunctionType.NameDisplay)

	name_definition_match = None
	try:
		for nna_type, match in name_match_operators.items():
			if(match):
				nna_name = nna_utils_tree.get_object_by_target_id(target_id).name
				index = match(nna_name)
				if(index >= 0):
					name_definition_match = {"nna_name": nna_name, "index": index, "nna_type": nna_type}
					break
		
		if(name_definition_match):
			box = self.layout.box()
			box.label(text="Name Definition: " + name_definition_match["nna_type"])
			if(name_definition_match["nna_type"] in name_draw_operators):
				name_draw_operators[name_definition_match["nna_type"]](box, name_definition_match["nna_name"])
			if(name_definition_match["index"] > 0):
				remove_button = box.operator(nna_operators_common.RemoveNNANameDefinitionOperator.bl_idname, text="Remove")
				remove_button.target_id = target_id
				remove_button.name_definition_index = name_definition_match["index"]
		elif(not name_definition_match and not ignore_no_match):
			box = self.layout.box()
			box.label(text="No Name Definition Set")
			row = box.row()
			row.prop(bpy.context.scene, "nna_oparators_name", text="")
			name_button = row.operator(bpy.context.scene.nna_oparators_name, text="Set Name Definition")
			if(name_button): name_button.target_id = target_id
			else: row.label(text="No Types Loaded")
	except ValueError as e:
		box = self.layout.box()
		box.label(text="Name Definition Error: " + str(e))
	
	return name_definition_match


def _draw_nna_json_editor(self, context, target_id):
	jsonText = nna_utils_json.get_json_from_target_id(target_id)
	
	preview_operators = nna_registry.get_nna_operators(nna_registry.NNAFunctionType.JsonDisplay)
	edit_operators = nna_registry.get_nna_operators(nna_registry.NNAFunctionType.JsonEdit)
	remove_operators = nna_registry.get_nna_operators(nna_registry.NNAFunctionType.JsonRemove)
	
	box = self.layout.box()
	box.label(text="Components")

	if(len(jsonText) > 2):
		try:
			col = box.column(heading="Components")
			componentsList = json.loads(jsonText)
			for idx, component in enumerate(componentsList):
				component_box = col.box()
				row = component_box.row()
				row.label(text="Type")
				row.label(text=str(component["t"]))

				if(str(component["t"]) in preview_operators):
					try:
						preview_operators[str(component["t"])](context.object, component_box, component)
					except:
						component_box.label(text="Invalid Definition!")
				else:
					for property in component.keys():
						if(property == "t"): continue
						row = component_box.row()
						row.label(text=property)
						row.label(text=str(component[property]))

				component_box.separator(type="LINE", factor=1)
				row = component_box.row()
				if(str(component["t"]) in edit_operators):
					editButton = row.operator(edit_operators[str(component["t"])], text="Edit")
					editButton.target_id = target_id
					editButton.component_index = idx
				editRawButton = row.operator(nna_operators_raw_json.EditNNARawJsonComponentOperator.bl_idname, text="Edit Raw Json")
				editRawButton.target_id = target_id
				editRawButton.component_index = idx
				if(str(component["t"]) in remove_operators):
					deleteButton = row.operator(remove_operators[str(component["t"])], text="Remove")
					deleteButton.target_id = target_id
					deleteButton.component_index = idx
				else:
					deleteButton = row.operator(nna_operators_common.RemoveNNAJsonComponentOperator.bl_idname, text="Remove")
					deleteButton.target_id = target_id
					deleteButton.component_index = idx

				if(idx < len(componentsList) - 1): col.separator(factor=1)
		except ValueError as e:
			box = self.layout.box()
			box.label(text="Name Definition Error: " + str(e))
	else:
		box.label(text="No Components Added")
	
	box.separator(type="LINE", factor=1)
	row = box.row()
	row.prop(bpy.context.scene, "nna_oparators_add", text="")
	button_add = row.operator(bpy.context.scene.nna_oparators_add, text="Add Component")
	if(button_add):	button_add.target_id = target_id
	else: row.label(text="No Types Loaded")
	button_edit_raw = row.operator(nna_operators_raw_json.EditNNARawJsonOperator.bl_idname, text="Edit Raw Json")
	button_edit_raw.target_id = target_id

	box.separator(type="LINE", factor=2)
	button_remove_nna_targeting = box.operator(nna_operators_common.RemoveNNATargetingObjectOperator.bl_idname)
	button_remove_nna_targeting.target_id = target_id
