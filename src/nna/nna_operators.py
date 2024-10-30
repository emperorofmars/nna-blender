import bpy
import json
from .nna_tree_utils import *
from .nna_json_utils import *

class InitializeNNAOperator(bpy.types.Operator):
	bl_idname = 'nna.init'
	bl_label = 'Initializie NNA'
	bl_options = {"REGISTER", "UNDO"}

	nna_init_collection: bpy.props.StringProperty(name = "nna_init_collection") # type: ignore
	
	def execute(self, context):
		if bpy.context.scene.collection.name == self.nna_init_collection:
			initNNARoot(bpy.context.scene.collection)
			return {"FINISHED"}
		else:
			for collection in [bpy.context.scene.collection, *bpy.context.scene.collection.children_recursive]:
				if(collection.name == self.nna_init_collection):
					initNNARoot(collection)
					return {"FINISHED"}
		return {"CANCELLED"}

class CreateNNATargetingObjectOperator(bpy.types.Operator):
	bl_idname = 'nna.create_targeting_object'
	bl_label = 'Initializie NNA'
	bl_options = {"REGISTER", "UNDO"}

	target: bpy.props.StringProperty(name = "target") # type: ignore
	
	def execute(self, context):
		createTargetingObject(findNNARoot(), self.target)
		return {"FINISHED"}

class EditNNARawJsonOperator(bpy.types.Operator):
	bl_idname = "nna.edit_raw_json"
	bl_label = "Edit Raw NNA Json"
	bl_options = {"REGISTER", "UNDO"}

	target: bpy.props.StringProperty(name = "target") # type: ignore
	json: bpy.props.StringProperty(name = "json") # type: ignore
	
	def invoke(self, context, event):
		self.target = context.object.name
		targetingObject = findNNATargetingObject(context.object.name)
		self.json = getJsonFromTargetingObject(targetingObject)
		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		targetingObject = findNNATargetingObject(self.target)
		try:
			json.loads(self.json)
			serializeJsonToTargetingObject(targetingObject, self.json)
			return {"FINISHED"}
		except:
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.label(text="Target Object: " + self.target)
		self.layout.prop(self, "json", text="", expand=True)

class EditNNARawJsonComponentOperator(bpy.types.Operator):
	bl_idname = "nna.edit_raw_json_component"
	bl_label = "Edit Raw NNA Json Component"
	bl_options = {"REGISTER", "UNDO"}

	target: bpy.props.StringProperty(name = "target") # type: ignore
	json: bpy.props.StringProperty(name = "json") # type: ignore

	jsonComponent: bpy.props.StringProperty(name = "jsonComponent") # type: ignore

	componentIdx: bpy.props.IntProperty(name = "componentIdx") # type: ignore
	
	def invoke(self, context, event):
		self.target = context.object.name
		targetingObject = findNNATargetingObject(context.object.name)
		self.json = getJsonFromTargetingObject(targetingObject)
		try:
			jsonObject = json.loads(self.json)
			self.jsonComponent = json.dumps(jsonObject[self.componentIdx])
			print()
			print(self.jsonComponent)
			print()
		except:
			pass
		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		targetingObject = findNNATargetingObject(self.target)
		try:
			jsonComponent = json.loads(self.jsonComponent)
			jsonObject = json.loads(self.json)
			jsonObject[self.componentIdx] = jsonComponent
			serializeJsonToTargetingObject(targetingObject, json.dumps(jsonObject))
			return {"FINISHED"}
		except ValueError as error:
			print("FAIL")
			print(error)
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.label(text="Target Object: " + self.target)
		self.layout.prop(self, "jsonComponent", text="", expand=True)
