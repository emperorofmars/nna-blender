import json
import traceback
import bpy

from . import nna_meta

from .exporter.export_helper import NNAExportFBX

from .ops import nna_operators_common
from .ops import nna_operators_raw_json
from . import nna_registry
from .utils import nna_utils_tree
from .utils import nna_utils_json
from .utils import nna_id_list
from .utils import nna_kv_list


class NNACollectionPanel(bpy.types.Panel):
	"""Display the NNA editor for Blender collections"""
	bl_idname = "OBJECT_PT_nna_collection_editor"
	bl_label = "NNA Collection Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_category = "NNA"
	bl_context = "collection"

	@classmethod
	def poll(cls, context):
		return (context.collection is not None)

	def draw(self, context):
		root = nna_utils_tree.find_nna_root()
		if(not root):
			self.layout.label(text="NNA Components Not Enabled")
			button = self.layout.operator(operator=nna_operators_common.InitializeNNAOperator.bl_idname)
			button.nna_init_collection = context.collection.name
		elif(context.collection in root.users_collection):
			draw_nna_editor(self, context, root.name, nna_utils_tree.determine_nna_object_state(root))
		else:
			self.layout.label(text="NNA is setup in another Collection")


class NNAObjectPanel(bpy.types.Panel):
	"""Display the NNA editor for Blender objects"""
	bl_idname = "OBJECT_PT_nna_object_editor"
	bl_label = "NNA Object Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_category = "NNA"
	bl_context = "object"

	@classmethod
	def poll(cls, context):
		return (context.object is not None)

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
		return (context.object is not None and context.bone is not None)

	def draw(self, context):
		draw_nna_editor(self, context, context.object.name + ";" + context.bone.name, nna_utils_tree.determine_nna_bone_state(context.object, context.bone))


def draw_nna_editor(self: bpy.types.Panel, context: bpy.types.Context | None, target_id: str, state: nna_utils_tree.NNAObjectState):
	base_object = nna_utils_tree.get_base_object_by_target_id(target_id)
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

			self.layout.label(text="This is the NNA definition for the Scene Root")
			_draw_nna_json_editor(self, context, target_id)
		case nna_utils_tree.NNAObjectState.IsMetaObject:
			_draw_meta_editor(self, context)
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
			_draw_nna_name_editor(self, context, target_id)
			self.layout.separator(type="LINE", factor=2)
			box = self.layout.box()
			box.label(text="NNA Components Not Enabled")
			button = box.operator(nna_operators_common.CreateNNATargetingObjectOperator.bl_idname)
			button.target_id = target_id
		case nna_utils_tree.NNAObjectState.IsTargetingObject:
			if(target_id == "$root"):
				self.layout.label(text="This is the NNA definition for the Scene Root")
				_draw_nna_json_editor(self, context, "$nna")
			else:
				self.layout.label(text="This is the NNA definition for: " + target_id[8:])
				_draw_nna_editors_for_target(self, context, target_id[8:])
		case nna_utils_tree.NNAObjectState.IsJsonDefinition:
			if(not base_object.parent.name[8:]):
				self.layout.label(text="This part of the NNA definition for the Scene Root" + base_object.parent.name[8:])
				_draw_nna_json_editor(self, context, "$nna")
			else:
				self.layout.label(text="This part of the NNA definition for: " + base_object.parent.name[8:])
				_draw_nna_editors_for_target(self, context, base_object.parent.name[8:])
		case nna_utils_tree.NNAObjectState.IsInvalidTargetingObject:
			self.layout.label(text="Invalid Target: '" + base_object.name[8:] + "' does NOT exist!")
		case nna_utils_tree.NNAObjectState.HasTargetingObject:
			_draw_nna_editors_for_target(self, context, target_id)
		case _:
			self.layout.label(text="Invalid!")


def _draw_meta_editor(self: bpy.types.Panel, context: bpy.types.Context | None):
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

		if("custom_properties" in json_meta):
			box.separator(factor=0.5)
			box.label(text="Custom Properties")
			for key, value in json_meta["custom_properties"]:
				row = box.row(); row.label(text=key); row.label(text=value)

		box.operator(nna_meta.EditNNAMetaOperator.bl_idname)
	else:
		box.operator(nna_meta.SetupNNAMetaOperator.bl_idname)


def _draw_nna_editors_for_target(self: bpy.types.Panel, context: bpy.types.Context | None, target_id: str):
	if(_draw_nna_name_editor(self, context, target_id, False)):
		box = self.layout.box()
		box.label(text="This Node has both a Name and Component definition.")
		box.label(text="Warning: Do not rename this Node manually!")
	_draw_nna_json_editor(self, context, target_id)


def _draw_nna_name_editor(self: bpy.types.Panel, context: bpy.types.Context | None, target_id: str, ignore_no_match = False) -> bool:
	name_match_operators = nna_registry.get_nna_operators(nna_registry.NNAFunctionType.NameMatch)
	name_draw_operators = nna_registry.get_nna_operators(nna_registry.NNAFunctionType.NameDisplay)
	name_set_operators = nna_registry.get_nna_operators(nna_registry.NNAFunctionType.NameSet)

	name_definition_match = None
	try:
		shortest_start_index = -1
		for nna_type, match in name_match_operators.items():
			nna_name = nna_utils_tree.get_object_by_target_id(target_id).name
			start_index = match(nna_name)
			if(start_index >= 0 and (shortest_start_index < 0 or start_index < shortest_start_index)):
				shortest_start_index = start_index
				name_definition_match = {"nna_name": nna_name, "index": start_index, "nna_type": nna_type}
		if(name_definition_match):
			box = self.layout.box()
			box.label(text="Name Definition: " + name_definition_match["nna_type"])
			if(name_definition_match["nna_type"] in name_draw_operators):
				name_draw_operators[name_definition_match["nna_type"]](box, name_definition_match["nna_name"])
			else:
				pass

			row = box.row()
			if(name_definition_match["nna_type"] in name_set_operators):
				edit_button = row.operator(name_set_operators[name_definition_match["nna_type"]], text="Edit")
				edit_button.target_id = target_id
			if(name_definition_match["index"] > 0):
				remove_button = row.operator(nna_operators_common.RemoveNNANameDefinitionOperator.bl_idname, text="Remove")
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
	except Exception as error:
		box = self.layout.box()
		box.label(text="Name Definition Error: " + str(error))
		print(traceback.format_exc())
		return None

	return name_definition_match


def _draw_nna_json_editor(self: bpy.types.Panel, context: bpy.types.Context | None, target_id: str):
	jsonText = nna_utils_json.get_json_from_target_id(target_id)

	preview_operators = nna_registry.get_nna_operators(nna_registry.NNAFunctionType.JsonDisplay)
	edit_operators = nna_registry.get_nna_operators(nna_registry.NNAFunctionType.JsonEdit)
	remove_operators = nna_registry.get_nna_operators(nna_registry.NNAFunctionType.JsonRemove)

	self.layout.label(text="Components List:")

	if(len(jsonText) > 2):
		try:
			col = self.layout.column()
			componentsList = json.loads(jsonText)
			for idx, component in enumerate(componentsList):
				component_box = col.box()

				split = component_box.split(factor=0.4)
				col_type = split.column()
				col_type.label(text="Type:")
				col_type.label(text=str(component["t"]))
				enabled_row = col_type.row()
				enabled_row.label(text="Enabled" if component.get("default_enabled", True) else "Disabled")
				toggleEnabledButton = enabled_row.operator(nna_operators_common.ToggleNNAComponentEnabledOperator.bl_idname)
				toggleEnabledButton.target_id = target_id
				toggleEnabledButton.component_index = idx

				header_row = split.column()

				row = header_row.box().row()
				row.label(text="ID: " + component["id"] if component.get("id") else "No ID")
				editIDButton = row.operator(nna_operators_common.EditNNAComponentIDOperator.bl_idname, text="", icon="OPTIONS")
				editIDButton.target_id = target_id
				editIDButton.component_index = idx

				nna_id_list.draw_id_list(target_id, header_row.box(), component, idx, "overrides")

				component_box.separator(type="LINE", factor=1)

				if(str(component["t"]) in preview_operators):
					try:
						preview_operators[str(component["t"])](target_id, component_box, component, idx)
					except Exception as error:
						component_box.label(text="Invalid Definition! Error: " + str(error))
				else:
					for property in component.keys():
						if(property in ["t", "id", "overrides"]): continue
						row = component_box.split(factor=0.4); row.label(text=property); row.label(text=str(component[property]))

				component_box.separator(factor=1)
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
		except Exception as error:
			box = self.layout.box()
			box.label(text="Name Definition Error: " + str(error))
	else:
		self.layout.label(text="No Components Added")

	self.layout.separator(factor=1)
	row = self.layout.row(align=True)
	row.prop(bpy.context.scene, "nna_oparators_add", text="")
	button_add = row.operator(bpy.context.scene.nna_oparators_add, text="Add Component", icon="ADD")
	if(button_add):	button_add.target_id = target_id
	else: row.label(text="No Types Loaded")
	row.separator()
	button_add_raw = row.operator(nna_operators_raw_json.AddNNARawJsonComponentOperator.bl_idname, text="Add Raw Json Component")
	button_add_raw.target_id = target_id

	self.layout.separator(factor=2)
	row = self.layout.row()
	button_edit_raw = row.operator(nna_operators_raw_json.EditNNARawJsonOperator.bl_idname, text="Edit Raw Json")
	button_edit_raw.target_id = target_id
	button_remove_nna_targeting = row.operator(nna_operators_common.RemoveNNATargetingObjectOperator.bl_idname)
	button_remove_nna_targeting.target_id = target_id
