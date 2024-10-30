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


class ResetNNAJsonOperator(bpy.types.Operator):
	bl_idname = 'nna.reset_json'
	bl_label = 'Parse NNA Json'
	bl_options = {"REGISTER", "UNDO"}

	target: bpy.props.StringProperty(name = "target") # type: ignore

	def execute(self, context):
		targetingObject = findNNATargetingObject(self.target)
		json = getJsonFromTargetingObject(targetingObject)
		print("JSON: " + json)
		context.object.nna_json = json
		return {"FINISHED"}


class CommitNNAJsonChangesOperator(bpy.types.Operator):
	bl_idname = 'nna.commit_json_changes'
	bl_label = 'Initializie NNA'
	bl_options = {"REGISTER", "UNDO"}

	target: bpy.props.StringProperty(name = "target") # type: ignore
	json: bpy.props.StringProperty(name = "json") # type: ignore
	
	@classmethod
	def poll(cls, context):
		try:
			json.loads(context.object.nna_json)
			return True
		except:
			return None
	
	def execute(self, context):
		targetingObject = findNNATargetingObject(self.target)
		if(len(self.json) > 0):
			serializeJsonToTargetingObject(targetingObject, self.json)
			return {"FINISHED"}
		return {"CANCELLED"}
