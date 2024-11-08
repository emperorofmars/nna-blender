import json
import bpy

from . import nna_utils_tree
from . import nna_utils_json


class SetupNNAMetaOperator(bpy.types.Operator):
	"""Setup NNA Meta Information"""
	bl_idname = "nna.init_meta"
	bl_label = "Setup NNA Meta Information"
	bl_options = {"REGISTER", "UNDO"}
	
	def execute(self, context):
		root = nna_utils_tree.find_nna_root()
		if(root):
			originalSelectedObject = bpy.context.active_object
			bpy.ops.object.empty_add()
			nnaObject = bpy.context.active_object
			nnaObject.name = "$meta"
			nnaObject.parent = root
			bpy.context.view_layer.objects.active = originalSelectedObject
			self.report({"INFO"}, "NNA Meta successfully created")
			return {"FINISHED"}
		else:
			return {"CANCELLED"}


class EditNNAMetaOperator(bpy.types.Operator):
	"""Edit NNA Meta Information"""
	bl_idname = "nna.edit_meta"
	bl_label = "Edit NNA Meta Information"
	bl_options = {"REGISTER", "UNDO"}

	name: bpy.props.StringProperty(name="Asset Name") # type: ignore
	author: bpy.props.StringProperty(name="Author") # type: ignore
	version: bpy.props.StringProperty(name="Version") # type: ignore
	url: bpy.props.StringProperty(name="URL") # type: ignore
	license: bpy.props.StringProperty(name="License") # type: ignore
	license_url: bpy.props.StringProperty(name="License Link") # type: ignore
	documentation: bpy.props.StringProperty(name="Documentation") # type: ignore
	documentation_url: bpy.props.StringProperty(name="documentation_url Link") # type: ignore
	
	def invoke(self, context, event):
		meta = nna_utils_tree.determine_nna_meta()
		json_text = nna_utils_json.get_json_from_targeting_object(meta)
		json_meta = json.loads(json_text) if json_text else {}

		if("name" in json_meta): self.name = json_meta["name"]
		if("author" in json_meta): self.author = json_meta["author"]
		if("version" in json_meta): self.version = json_meta["version"]
		if("url" in json_meta): self.url = json_meta["url"]
		if("license" in json_meta): self.license = json_meta["license"]
		if("license_url" in json_meta): self.license_url = json_meta["license_url"]
		if("documentation" in json_meta): self.documentation = json_meta["documentation"]
		if("documentation_url" in json_meta): self.documentation_url = json_meta["documentation_url"]

		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			meta = nna_utils_tree.determine_nna_meta()
			json_text = nna_utils_json.get_json_from_targeting_object(meta)
			json_meta = json.loads(json_text) if json_text else {}

			if(self.name): json_meta["name"] = self.name
			elif("name" in json_meta): del json_meta["name"]
			if(self.author): json_meta["author"] = self.author
			elif("author" in json_meta): del json_meta["author"]
			if(self.version): json_meta["version"] = self.version
			elif("version" in json_meta): del json_meta["version"]
			if(self.url): json_meta["url"] = self.url
			elif("url" in json_meta): del json_meta["url"]
			if(self.license): json_meta["license"] = self.license
			elif("license" in json_meta): del json_meta["license"]
			if(self.license_url): json_meta["license_url"] = self.license_url
			elif("license_url" in json_meta): del json_meta["license_url"]
			if(self.documentation): json_meta["documentation"] = self.documentation
			elif("documentation" in json_meta): del json_meta["documentation"]
			if(self.documentation_url): json_meta["documentation_url"] = self.documentation_url
			elif("documentation_url" in json_meta): del json_meta["documentation_url"]

			nna_utils_json.serialize_json_to_targeting_object(meta, json.dumps(json_meta))
			self.report({'INFO'}, "Component successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.prop(self, "name", expand=True)
		self.layout.prop(self, "author", expand=True)
		self.layout.prop(self, "version", expand=True)
		self.layout.prop(self, "url", expand=True)
		self.layout.prop(self, "license", expand=True)
		self.layout.prop(self, "license_url", expand=True)
		self.layout.prop(self, "documentation", expand=True)
		self.layout.prop(self, "documentation_url", expand=True)


def display_nna_humanoid_component(object, layout, json_dict):
	row = layout.row()
	row.label(text="Locomotion Type")
	row.label(text=json_dict["lc"] if "lc" in json_dict else "default (planti)")
	row = layout.row()
	row.label(text="No Jaw Mapping")
	row.label(text=str(json_dict["nj"]) if "nj" in json_dict else "default (False)")
