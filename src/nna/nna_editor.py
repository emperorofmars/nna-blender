from enum import Enum, auto
import bpy

class NNAObjectState(Enum):
	NotInited = auto()
	InitedOutsideTree = auto()
	InitedInsideTree = auto()
	IsRootObject = auto()
	IsTargetingObject = auto()
	HasTargetingObject = auto()


class InitializeNNAOperator(bpy.types.Operator):
	bl_idname = 'nna.init'
	bl_label = 'Initializie NNA'
	bl_options = {"REGISTER", "UNDO"}

	nna_init_collection: bpy.props.StringProperty(name = "nna_init_collection") # type: ignore
	
	def execute(self, context):
		if bpy.context.scene.collection.name == self.nna_init_collection:
			initNNA(bpy.context.scene.collection)
			return {"FINISHED"}
		else:
			for collection in [bpy.context.scene.collection, *bpy.context.scene.collection.children_recursive]:
				if(collection.name == self.nna_init_collection):
					initNNA(collection)
					return {"FINISHED"}
		return {"FAILED"}


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
		self.layout.label(text=context.collection.name)
		if(context.object.name == "$nna"):
			self.layout.label(text="This is the NNA Root")
		else:
			nnaCollection = findNNARootCollection()
			if(nnaCollection == None):
				if(len(bpy.context.scene.collection.children_recursive) == 0):
					button = self.layout.operator(operator=InitializeNNAOperator.bl_idname, text="Initialize NNA in Scene") # icon="BLENDER"
					button.nna_init_collection = bpy.context.scene.collection.name
				else:
					# self.layout.sele
					button = self.layout.operator(operator=InitializeNNAOperator.bl_idname, text="Initialize NNA in Collection") # icon="BLENDER"
					button.nna_init_collection = context.collection.name
			else:
				success = False
				for collection in [nnaCollection, *nnaCollection.children_recursive]:
					if(collection in context.object.users_collection):
						self.drawNNAEditor(context, nnaCollection)
						success = True
				if(not success):
					self.layout.label(text="This object is outside the NNA tree!")
	
	def drawNNAEditor(self, context, nnaCollection: bpy.types.Collection):
		self.layout.label(text="NNA initialized in " + nnaCollection.name)
		objectIndex = nnaCollection.objects.find("$target:" + context.object.name)
		if(objectIndex >= 0):
			nnaDef = nnaCollection.objects[objectIndex]
			self.layout.label(text="nnaDef: " + nnaDef.name)
		else:
			self.layout.label(text="Initialize NNA for this object")


def findNNARootCollection() -> bpy.types.Collection:
	for collection in [bpy.context.scene.collection, *bpy.context.scene.collection.children_recursive]:
		if(findNNARootInCollection(collection)):
			return collection
	return None

def findNNARoot() -> bpy.types.Collection:
	for collection in [bpy.context.scene.collection, *bpy.context.scene.collection.children_recursive]:
		root = findNNARootInCollection(collection)
		if(root):
			return root
	return None

def findNNARootInCollection(collection: bpy.types.Collection) -> bool:
	for child in collection.objects:
		if(child.name == "$nna"):
			return child
	return None

def initNNA(collection: bpy.types.Collection) -> object:
	bpy.ops.object.empty_add()
	nnaObject = bpy.context.active_object
	nnaObject.name = "$nna"
	if(collection not in nnaObject.users_collection):
		collection.objects.link(nnaObject)
		for linkedCollection in nnaObject.users_collection:
			if(linkedCollection != collection):
				linkedCollection.objects.unlink(nnaObject)


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