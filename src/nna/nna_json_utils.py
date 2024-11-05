import json
import bpy
import re
from . import nna_tree_utils

def get_json_from_targetname(targetObjectName: str) -> str:
	return get_json_from_targeting_object(nna_tree_utils.find_nna_targeting_object(targetObjectName))

def get_json_from_targeting_object(targetingObject: bpy.types.Object) -> str:
	list = []
	for child in targetingObject.children:
		m1 = re.match("^\$[0-9]+\$.+", child.name)
		m2 = re.match("^\$[0-9]+.[0-9]+\$.+", child.name)
		if(m1):
			nnaNumIdx = child.name.index('$', 1)
			list.append((int(child.name[1:nnaNumIdx]), child.name[nnaNumIdx + 1:]))
		if(m2):
			nnaNumIdx = child.name.index('.', 0)
			nnaStartIdx = child.name.index('$', 1)
			list.append((int(child.name[1:nnaNumIdx]), child.name[nnaStartIdx + 1:]))
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
	serialize_json_to_targeting_object(nna_tree_utils.find_nna_targeting_object(targetObjectName), json)

def serialize_json_to_targeting_object(targetingObject: bpy.types.Object, json: str):
	clear_targeting_object(targetingObject)
	remainingJsonCharacters = str(json) # get actual bytes
	line_nr = 0
	while(len(remainingJsonCharacters) > 0):
		line, line_len = build_unique_line(remainingJsonCharacters, line_nr)
		remainingJsonCharacters = remainingJsonCharacters[line_len:]
		add_line_to_targeting_object(targetingObject, line, line_nr)
		line_nr += 1

def build_unique_line(remaining_string: str, line_nr: int) -> tuple[str, int]:
	line_len = 61
	unique = 0
	line = ""
	if(unique > 0):
		line = "$" + str(line_nr) + "." + str(unique) + "$" + remaining_string[0:line_len-len(str(line_nr))-len("." + str(unique))]
	else:
		line = "$" + str(line_nr) + "$" + remaining_string[0:line_len-len(str(line_nr))-len("." + str(unique))]
	while(len(str.encode(line)) > 63 or bpy.data.objects.get(line)): # account for multi byte characters
		if(len(str.encode(line)) > 63): line_len -= 1
		if(bpy.data.objects.get(line)): unique += 1
		if(unique > 0):
			line = "$" + str(line_nr) + "." + str(unique) + "$" + remaining_string[0:line_len-len(str(line_nr))-len("." + str(unique))]
		else:
			line = "$" + str(line_nr) + "$" + remaining_string[0:line_len-len(str(line_nr))]
	if(unique > 0):
		return (line, line_len-len(str(line_nr))-len("." + str(unique)))
	else:
		return (line, line_len-len(str(line_nr)))

def add_line_to_targeting_object(targetingObject: bpy.types.Object, line: str, lineNr: int):
	originalSelectedObject = bpy.context.active_object
	bpy.ops.object.empty_add()
	nnaObject = bpy.context.active_object
	nnaObject.name = line
	nnaObject.parent = targetingObject
	bpy.context.view_layer.objects.active = originalSelectedObject


def clear_targeting_object(object: bpy.types.Object):
	for child in object.children:
		bpy.data.objects.remove(child)

def remove_targeting_object(object: bpy.types.Object):
	for child in object.children:
		bpy.data.objects.remove(child)
	bpy.data.objects.remove(object)


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

