import bpy
from enum import Enum, auto
import re

class NNAObjectState(Enum):
	NotInited = auto()
	InitedOutsideTree = auto()
	InitedInsideTree = auto()
	IsRootObject = auto()
	IsRootObjectWithTargeting = auto()
	IsTargetingObject = auto()
	IsJsonDefinition = auto()
	HasTargetingObject = auto()

def determine_nna_object_state(object: bpy.types.Object) -> NNAObjectState:
	if(object.name == "$nna"):
		for child in object.children:
			if(child.name == "$root"):
				return NNAObjectState.IsRootObjectWithTargeting
		return NNAObjectState.IsRootObject
	if(object.name.startswith("$target:") or object.name == "$root"): return NNAObjectState.IsTargetingObject
	if(re.match("^\$[0-9]+\$.+", object.name)): return NNAObjectState.IsJsonDefinition
	nnaCollection = findNNARootCollection()
	if(nnaCollection == None): return NNAObjectState.NotInited
	for collection in [nnaCollection, *nnaCollection.children_recursive]:
		if(collection in object.users_collection):
			if(find_nna_targeting_object(object.name)):
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
	return bpy.data.objects.get("$nna")

def findNNARootInCollection(collection: bpy.types.Collection) -> bpy.types.Object | None:
	for child in collection.objects:
		if(child.name == "$nna"):
			return child
	return None

def find_nna_targeting_object(name: str) -> bpy.types.Object | None:
	for child in findNNARoot().children:
		if(child.name.startswith("$target:" + name)):
			return child
		elif(name == "$nna" and child.name == "$root"):
			return child
	return None

def initNNARoot(collection: bpy.types.Collection):
	originalSelectedObject = bpy.context.active_object
	bpy.ops.object.empty_add()
	nnaObject = bpy.context.active_object
	nnaObject.name = "$nna"
	if(collection not in nnaObject.users_collection):
		collection.objects.link(nnaObject)
		for linkedCollection in nnaObject.users_collection:
			if(linkedCollection != collection):
				linkedCollection.objects.unlink(nnaObject)
	bpy.context.view_layer.objects.active = originalSelectedObject

def createTargetingObject(root: bpy.types.Object, name: str):
	originalSelectedObject = bpy.context.active_object
	bpy.ops.object.empty_add()
	nnaObject = bpy.context.active_object
	if(name == "$nna"):
		nnaObject.name = "$root"
	else:
		nnaObject.name = "$target:" + name
	nnaObject.parent = root
	bpy.context.view_layer.objects.active = originalSelectedObject
