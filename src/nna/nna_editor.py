import bpy
from .nna_tree_utils import *

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
		return {"FAILED"}

class CreateNNATargetingObjectOperator(bpy.types.Operator):
	bl_idname = 'nna.create_targeting_object'
	bl_label = 'Initializie NNA'
	bl_options = {"REGISTER", "UNDO"}

	target: bpy.props.StringProperty(name = "target") # type: ignore
	
	def execute(self, context):
		createTargetingObject(findNNARoot(), self.target)
		return {"FINISHED"}

class CommitNNAJsonChanges(bpy.types.Operator):
	bl_idname = 'nna.commit_json_changes'
	bl_label = 'Initializie NNA'
	bl_options = {"REGISTER", "UNDO"}

	target: bpy.props.StringProperty(name = "target") # type: ignore
	json: bpy.props.StringProperty(name = "json") # type: ignore
	
	def execute(self, context):
		t = findNNATargetingObject(self.target)
		jsonBytes = self.json # get actual bytes
		bpy.ops.object.empty_add()
		nnaObject = bpy.context.active_object
		nnaObject.name = jsonBytes
		nnaObject.parent = t
		return {"FINISHED"}


class NNAEditor(bpy.types.Panel):
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
		match determineNNAObjectState(context.object):
			case NNAObjectState.IsRootObject:
				self.layout.label(text="This is the NNA Root")
			case NNAObjectState.NotInited:
				if(len(bpy.context.scene.collection.children_recursive) == 0):
					button = self.layout.operator(operator=InitializeNNAOperator.bl_idname, text="Initialize NNA in Scene")
					button.nna_init_collection = bpy.context.scene.collection.name
				else:
					button = self.layout.operator(operator=InitializeNNAOperator.bl_idname, text="Initialize NNA in Collection")
					button.nna_init_collection = context.collection.name
			case NNAObjectState.InitedOutsideTree:
				self.layout.label(text="This object is outside the NNA tree!")
			case NNAObjectState.InitedInsideTree:
				button = self.layout.operator(CreateNNATargetingObjectOperator.bl_idname, text="Create NNA Component List")
				button.target = context.object.name
			case NNAObjectState.IsTargetingObject:
				self.layout.label(text="This is the Component definition for: " + context.object.name[8:])
			case NNAObjectState.HasTargetingObject:
				self.drawNNAEditor(context)
	
	def drawNNAEditor(self, context):
		targetingObject = findNNATargetingObject(context.object.name)
		
		self.layout.label(text="nnaDef: " + targetingObject.name)

		self.layout.prop(context.scene, "nna_json", expand=True)

		button = self.layout.operator(CommitNNAJsonChanges.bl_idname, text="Commit changes")
		button.target = context.object.name
		button.json = context.scene.nna_json # combine subtree names


def register():
	bpy.types.Scene.nna_json = bpy.props.StringProperty(name="nna_json", default="asdfasdf")

def unregister():
	del bpy.types.Scene.nna_json

"""
# TODO Create a new tab in the properties panel
class PropertiesTabTest(bpy.types.Panel):
	bl_idname = "OBJECT_PT_properties_tab_test"
	bl_label = "Properties Tab Test"
	bl_space_type = "PROPERTIES"
	bl_region_type = "NAVIGATION_BAR"

	def draw(self, context):
		self.layout.label(text="Hello World")
"""