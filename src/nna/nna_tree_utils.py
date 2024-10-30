import bpy
from enum import Enum, auto

class NNAObjectState(Enum):
	NotInited = auto()
	InitedOutsideTree = auto()
	InitedInsideTree = auto()
	IsRootObject = auto()
	IsTargetingObject = auto()
	HasTargetingObject = auto()

def determineNNAObjectState(object: bpy.types.Object) -> NNAObjectState:
	if(object.name == "$nna"): return NNAObjectState.IsRootObject
	if(object.name.startswith("$target:")): return NNAObjectState.IsTargetingObject
	nnaCollection = findNNARootCollection()
	if(nnaCollection == None): return NNAObjectState.NotInited
	for collection in [nnaCollection, *nnaCollection.children_recursive]:
		if(collection in object.users_collection):
			if(findNNATargetingObject(findNNARoot(), object.name)):
				return NNAObjectState.HasTargetingObject
			else:
				return NNAObjectState.InitedInsideTree
	return NNAObjectState.InitedOutsideTree

def findNNARootCollection() -> bpy.types.Collection | None:
	for collection in [bpy.context.scene.collection, *bpy.context.scene.collection.children_recursive]:
		if(findNNARootInCollection(collection)):
			return collection
	return None

def findNNARoot() -> bpy.types.Object | None:
	for collection in [bpy.context.scene.collection, *bpy.context.scene.collection.children_recursive]:
		root = findNNARootInCollection(collection)
		if(root):
			return root
	return None

def findNNARootInCollection(collection: bpy.types.Collection) -> bpy.types.Object | None:
	for child in collection.objects:
		if(child.name == "$nna"):
			return child
	return None

def findNNATargetingObject(root: bpy.types.Object, name: str) -> bpy.types.Object | None:
	for child in root.children:
		if(child.name.startswith("$target:" + name)):
			return child
	return None

def initNNARoot(collection: bpy.types.Collection):
	bpy.ops.object.empty_add()
	nnaObject = bpy.context.active_object
	nnaObject.name = "$nna"
	if(collection not in nnaObject.users_collection):
		collection.objects.link(nnaObject)
		for linkedCollection in nnaObject.users_collection:
			if(linkedCollection != collection):
				linkedCollection.objects.unlink(nnaObject)

def createTargetingObject(root: bpy.types.Object, name: str):
	bpy.ops.object.empty_add()
	nnaObject = bpy.context.active_object
	nnaObject.name = "$target:" + name
	nnaObject.parent = root
