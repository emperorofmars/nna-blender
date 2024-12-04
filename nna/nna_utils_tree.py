# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import bpy
from enum import Enum, auto
import re


class NNAObjectState(Enum):
	NotInited = auto()					# NNA root (`$nna`) object doesn't exist.
	InitedOutsideTree = auto()			# NNA root (`$nna`) object exists, the current object isn't part of the Collection in which the root sits.
	InitedInsideTree = auto()			# NNA root (`$nna`) object exists and can be used.
	IsRootObject = auto()				# NNA root (`$nna`) is currently selected.
	IsRootObjectWithTargeting = auto()	# NNA root (`$nna`) is currently selected, and it has a child named `$root`, used to specify components for the exported root object.
	IsMetaObject = auto()				# NNA meta data object is currently selected.
	IsTargetingObject = auto()			# The currently selected object is a targeting object. It is parented to the NNA root (`$nna`), and it points to an object in the scene.
	IsJsonDefinition = auto()			# The currently selected object is a line in a NNA component definition.
	HasTargetingObject = auto()			# The currently selected object has a targeting object. In this state its components can be created or edited.
	IsInvalidTargetingObject = auto()	# The currently selected object is a targeting object with an invalid target_id
	IsInvalidJsonDefinition = auto()	# The currently selected object is a line in a NNA component definition for an invalid target_id
	Invalid = auto()					# rip

def determine_nna_object_state(object: bpy.types.Object) -> NNAObjectState:
	if(object.name == "$nna"):
		for child in object.children:
			if(child.name == "$root"):
				return NNAObjectState.IsRootObjectWithTargeting
		return NNAObjectState.IsRootObject
	if(object.name.startswith("$target:") and object.parent and object.parent.name == "$nna"):
		if(get_base_object_by_target_id(object.name[8:])):
			return NNAObjectState.IsTargetingObject
		else:
			return NNAObjectState.IsInvalidTargetingObject
	if(object.name == "$meta" and object.parent and object.parent.name == "$nna"):
		return NNAObjectState.IsMetaObject
	elif(object.name == "$root" and object.parent and object.parent.name == "$nna"):
		return NNAObjectState.IsTargetingObject
	if(re.match("^\$[0-9]+\$.+", object.name) and object.parent and object.parent.name.startswith("$target:") and object.parent.parent and object.parent.parent.name == "$nna"):
		if(get_base_object_by_target_id(object.parent.name[8:])):
			return NNAObjectState.IsJsonDefinition
		else:
			return NNAObjectState.IsInvalidJsonDefinition
	if(re.match("^\$[0-9]+\$.+", object.name) and object.parent and object.parent.name == "$root" and object.parent.parent and object.parent.parent.name == "$nna"):
		return NNAObjectState.IsJsonDefinition
	nnaCollection = find_nna_root_collection()
	if(nnaCollection == None):
		return NNAObjectState.NotInited
	for collection in [nnaCollection, *nnaCollection.children_recursive]:
		if(collection in object.users_collection):
			if(find_nna_targeting_object(object.name)):
				return NNAObjectState.HasTargetingObject
			else:
				return NNAObjectState.InitedInsideTree
	return NNAObjectState.InitedOutsideTree

def determine_nna_bone_state(object: bpy.types.Object, bone: bpy.types.Bone) -> NNAObjectState:
	if(object.name == "$nna"):
		return NNAObjectState.Invalid
	if(object.name.startswith("$target:") or object.name == "$root"): return NNAObjectState.Invalid
	if(re.match("^\$[0-9]+\$.+", object.name)): return NNAObjectState.Invalid
	nnaCollection = find_nna_root_collection()
	for collection in [nnaCollection, *nnaCollection.children_recursive]:
		if(collection in object.users_collection):
			if(find_nna_targeting_object(object.name + "$" + bone.name)):
				return NNAObjectState.HasTargetingObject
			else:
				return NNAObjectState.InitedInsideTree
	return NNAObjectState.InitedOutsideTree


def determine_nna_meta() -> bpy.types.Object | None:
	for child in find_nna_root().children:
		if(child.name == "$meta"):
			return child
	else:
		return None


def find_nna_root_collection() -> bpy.types.Collection | None:
	for collection in [bpy.context.scene.collection, *bpy.context.scene.collection.children_recursive]:
		if(find_nna_root_in_collection(collection)):
			return collection
	return None

def find_nna_root() -> bpy.types.Object | None:
	return bpy.data.objects.get("$nna")

def find_nna_root_in_collection(collection: bpy.types.Collection) -> bpy.types.Object | None:
	for child in collection.objects:
		if(child.name == "$nna"):
			return child
	return None

def find_nna_targeting_object(target_id: str) -> bpy.types.Object | None:
	for child in find_nna_root().children:
		if(child.name == "$target:" + target_id):
			return child
		elif(target_id == "$nna" and child.name == "$root"):
			return child
	return None


def get_object_by_target_id(target_id: str, split_char = '$') -> bpy.types.Object | bpy.types.Bone | None:
	if(not target_id): return None
	object = bpy.data.objects.get(target_id)
	if(object): return object
	parts = target_id.split(split_char)
	object: bpy.types.Object = bpy.data.objects.get(parts[0])
	if(len(parts) > 1): return object.data.bones.get(parts[1])
	else: return object

def get_base_object_by_target_id(target_id: str, split_char = '$') -> bpy.types.Object | None:
	if(not target_id): return None
	object = bpy.data.objects.get(target_id)
	if(object): return object
	parts = target_id.split(split_char)
	return bpy.data.objects.get(parts[0])


def init_nna_root(collection: bpy.types.Collection):
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

def create_targeting_object(root: bpy.types.Object, name: str):
	originalSelectedObject = bpy.context.active_object
	bpy.ops.object.empty_add()
	nnaObject = bpy.context.active_object
	if(name == "$nna"):
		nnaObject.name = "$root"
	else:
		nnaObject.name = "$target:" + name
	nnaObject.parent = root
	bpy.context.view_layer.objects.active = originalSelectedObject
