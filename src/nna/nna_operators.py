import bpy
import json
from .nna_tree_utils import *
from .nna_json_utils import *

class InitializeNNAOperator(bpy.types.Operator):
	bl_idname = "nna.init"
	bl_label = "Initializie NNA"
	bl_options = {"REGISTER", "UNDO"}

	nna_init_collection: bpy.props.StringProperty(name = "nna_init_collection") # type: ignore
	
	def execute(self, context):
		if bpy.context.scene.collection.name == self.nna_init_collection:
			initNNARoot(bpy.context.scene.collection)
			self.report({"INFO"}, "NNA inited in Scene Collection")
			return {"FINISHED"}
		else:
			for collection in [bpy.context.scene.collection, *bpy.context.scene.collection.children_recursive]:
				if(collection.name == self.nna_init_collection):
					initNNARoot(collection)
					self.report({"INFO"}, "NNA inited in " + collection.name)
					return {"FINISHED"}
		return {"CANCELLED"}

class CreateNNATargetingObjectOperator(bpy.types.Operator):
	bl_idname = "nna.create_targeting_object"
	bl_label = "Initializie NNA for this Object"
	bl_options = {"REGISTER", "UNDO"}

	target: bpy.props.StringProperty(name = "target") # type: ignore
	
	def execute(self, context):
		createTargetingObject(findNNARoot(), self.target)
		self.report({"INFO"}, "Targeting object created")
		return {"FINISHED"}

class RemoveNNATargetingObjectOperator(bpy.types.Operator):
	bl_idname = "nna.remove_targeting_object"
	bl_label = "Remove NNA from this Object"
	bl_options = {"REGISTER", "UNDO"}

	target: bpy.props.StringProperty(name = "target") # type: ignore

	def invoke(self, context, event):
		self.target = context.object.name
		return context.window_manager.invoke_confirm(self, event)
	
	def execute(self, context):
		remove_targeting_object(find_nna_targeting_object(self.target))
		self.report({"INFO"}, "NNA functionality has been removed from: " + self.target)
		return {"FINISHED"}

class EditNNARawJsonOperator(bpy.types.Operator):
	bl_idname = "nna.edit_raw_json"
	bl_label = "Edit Raw NNA Json Object"
	bl_options = {"REGISTER", "UNDO"}

	target: bpy.props.StringProperty(name = "target") # type: ignore
	json: bpy.props.StringProperty(name = "json") # type: ignore
	
	def invoke(self, context, event):
		self.target = context.object.name
		self.json = get_json_from_targetname(context.object.name)
		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			json.loads(self.json)
			serialize_json_to_targetname(self.target, self.json)
			self.report({'INFO'}, "Object Json successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.label(text="Target Object: " + self.target)
		self.layout.prop(self, "json", text="", expand=True)

class AddNNARawJsonComponentOperator(bpy.types.Operator):
	bl_idname = "nna.add_raw_json_component"
	bl_label = "Add Raw Json Component"
	bl_options = {"REGISTER", "UNDO"}
	
	target: bpy.props.StringProperty(name = "target") # type: ignore
	json: bpy.props.StringProperty(name = "json") # type: ignore
	newComponent: bpy.props.StringProperty(name = "newComponent") # type: ignore

	def invoke(self, context, event):
		self.target = context.object.name
		self.json = get_json_from_targetname(context.object.name)
		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			jsonText = add_component_to_nna(self.json, self.newComponent)
			serialize_json_to_targetname(self.target, jsonText)
			self.report({'INFO'}, "Component successfully added")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.label(text="Target Object: " + self.target)
		self.layout.prop(self, "newComponent", text="", expand=True)

class EditNNARawJsonComponentOperator(bpy.types.Operator):
	bl_idname = "nna.edit_raw_json_component"
	bl_label = "Edit Raw Json Component"
	bl_options = {"REGISTER", "UNDO"}

	target: bpy.props.StringProperty(name = "target") # type: ignore
	json: bpy.props.StringProperty(name = "json") # type: ignore
	jsonComponent: bpy.props.StringProperty(name = "jsonComponent") # type: ignore

	componentIdx: bpy.props.IntProperty(name = "componentIdx", default=-1) # type: ignore
	
	def invoke(self, context, event):
		self.target = context.object.name
		self.json = get_json_from_targetname(context.object.name)
		try:
			self.jsonComponent = get_component_from_nna(self.json, self.componentIdx)
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return None
		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			jsonText = replace_component_in_nna(self.json, self.jsonComponent, self.componentIdx)
			serialize_json_to_targetname(self.target, jsonText)
			self.report({'INFO'}, "Component successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.label(text="Target Object: " + self.target)
		self.layout.prop(self, "jsonComponent", text="", expand=True)

class RemoveNNAJsonComponentOperator(bpy.types.Operator):
	bl_idname = "nna.remove_json_component"
	bl_label = "Remove Json Component"
	bl_options = {"REGISTER", "UNDO"}

	target: bpy.props.StringProperty(name = "target") # type: ignore
	json: bpy.props.StringProperty(name = "json") # type: ignore
	componentIdx: bpy.props.IntProperty(name = "componentIdx", default=-1) # type: ignore

	def invoke(self, context, event):
		self.target = context.object.name
		self.json = get_json_from_targetname(context.object.name)
		return context.window_manager.invoke_confirm(self, event)
	
	def execute(self, context):
		try:
			jsonText = remove_component_from_nna(self.json, self.componentIdx)
			serialize_json_to_targetname(self.target, jsonText)
			self.report({'INFO'}, "Component successfully removed")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
