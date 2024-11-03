import json
import bpy
import re
from .nna_tree_utils import *

def get_json_from_targetname(targetObjectName: str) -> str:
	return get_json_from_targeting_object(find_nna_targeting_object(targetObjectName))

def get_json_from_targeting_object(targetingObject: bpy.types.Object) -> str:
	list = []
	for child in targetingObject.children:
		m = re.match("^\$[0-9]+\$.+", child.name)
		if(m):
			nnaNumIdx = child.name.index('$', 1)
			list.append((int(child.name[1:nnaNumIdx]), child.name[nnaNumIdx + 1:]))
	list.sort(key=lambda e: e[0])
	match len(list):
		case 0: return ""
		case 1: return list[0][1]
		case _:
			str = ""
			for line in list:
				str += line[1]
			return str

def serialize_json_to_targetname(targetObjectName: str, json: str):
	serialize_json_to_targeting_object(find_nna_targeting_object(targetObjectName), json)

def serialize_json_to_targeting_object(targetingObject: bpy.types.Object, json: str):
	clear_targeting_object(targetingObject)
	remainingJsonBytes = str.encode(json) # get actual bytes
	lineNr = 0
	while(len(remainingJsonBytes) > 0):
		line = remainingJsonBytes[0:61-len(str(lineNr))]
		remainingJsonBytes = remainingJsonBytes[len(line):]
		add_line_to_targeting_object(targetingObject, line.decode(), lineNr)
		lineNr += 1

def clear_targeting_object(object: bpy.types.Object):
	for child in object.children:
		bpy.data.objects.remove(child)

def remove_targeting_object(object: bpy.types.Object):
	for child in object.children:
		bpy.data.objects.remove(child)
	bpy.data.objects.remove(object)

def add_line_to_targeting_object(targetingObject: bpy.types.Object, line: str, lineNr: int):
	originalSelectedObject = bpy.context.active_object
	bpy.ops.object.empty_add()
	nnaObject = bpy.context.active_object
	nnaObject.name = "$" + str(lineNr) + "$" + line
	nnaObject.parent = targetingObject
	bpy.context.view_layer.objects.active = originalSelectedObject

def get_component_from_nna(jsonText: str, componentIndex: int) -> str:
	jsonObject = json.loads(jsonText)
	return json.dumps(jsonObject[componentIndex])

def replace_component_in_nna(jsonText: str, jsonComponentText: str, componentIndex: int) -> str:
	jsonObject = json.loads(jsonText)
	jsonObject[componentIndex] = json.loads(jsonComponentText)
	return json.dumps(jsonObject)

def remove_component_from_nna(jsonText: str, componentIndex: int) -> str:
	jsonObject = json.loads(jsonText)
	del(jsonObject[componentIndex])
	return json.dumps(jsonObject)

def add_component_to_nna(jsonText: str, jsonComponentText: str) -> str:
	if(len(jsonText) > 2):
		jsonObject = json.loads(jsonText)
		jsonObject.append(json.loads(jsonComponentText))
		return json.dumps(jsonObject)
	else:
		return json.dumps([json.loads(jsonComponentText)])

