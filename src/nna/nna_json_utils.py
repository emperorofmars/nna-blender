import json
import bpy
import re
from . import nna_tree_utils

def get_json_from_target_id(target_id: str) -> str:
	return get_json_from_targeting_object(nna_tree_utils.find_nna_targeting_object(target_id))

def get_json_from_targeting_object(targeting_object: bpy.types.Object) -> str:
	list = []
	for child in targeting_object.children:
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


def serialize_json_to_target_id(target_id: str, json_text: str):
	serialize_json_to_targeting_object(nna_tree_utils.find_nna_targeting_object(target_id), json_text)

def serialize_json_to_targeting_object(targetingObject: bpy.types.Object, json_text: str):
	clear_targeting_object(targetingObject)
	remainingJsonCharacters = json_text # get actual bytes
	line_nr = 0
	while(len(remainingJsonCharacters) > 0):
		line, consumed_length = _build_unique_line(remainingJsonCharacters, line_nr)
		remainingJsonCharacters = remainingJsonCharacters[consumed_length:]
		_add_line_to_targeting_object(targetingObject, line)
		line_nr += 1

def _construct_line(line_string: str, line_nr: int, unique: int) -> str:
	if(unique > 0):
		return "$" + str(line_nr) + "." + str(unique) + "$" + line_string
	else:
		return "$" + str(line_nr) + "$" + line_string

def _get_line_meta_length(line_nr: int, unique: int) -> int:
	if(unique > 0): return len("$$" + str(line_nr))+len("." + str(unique))
	else: return len("$$" + str(line_nr))

def _build_unique_line(remaining_string: str, line_nr: int) -> tuple[str, int]:
	line_len_offset = 0
	unique = 0
	line = _construct_line(remaining_string[: 63 - _get_line_meta_length(line_nr, 0) - line_len_offset], line_nr, unique)
	while(len(str.encode(line)) > 63 or bpy.data.objects.get(line)):
		if(len(str.encode(line)) > 63): line_len_offset += 1 # account for multi byte characters
		if(bpy.data.objects.get(line)): unique += 1 # account for blenders object name uniqueness requirement
		line = _construct_line(remaining_string[: 63 - _get_line_meta_length(line_nr, 0) - line_len_offset], line_nr, unique)
	return (line, 63 - _get_line_meta_length(line_nr, 0) - line_len_offset)

def _add_line_to_targeting_object(targetingObject: bpy.types.Object, line: str):
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


def get_component_from_json(json_text: str, component_index: int) -> str:
	jsonObject = json.loads(json_text)
	return json.dumps(jsonObject[component_index])

def add_component_to_json(json_text: str, json_component_text: str) -> str:
	if(len(json_text) > 2):
		jsonObject = json.loads(json_text)
		jsonObject.append(json.loads(json_component_text))
		return json.dumps(jsonObject)
	else:
		return json.dumps([json.loads(json_component_text)])

def replace_component_in_json(json_text: str, json_component_text: str, component_index: int) -> str:
	jsonObject = json.loads(json_text)
	jsonObject[component_index] = json.loads(json_component_text)
	return json.dumps(jsonObject)

def remove_component_from_json(json_text: str, component_index: int) -> str:
	jsonObject = json.loads(json_text)
	del(jsonObject[component_index])
	return json.dumps(jsonObject)


def get_component_json(target_id: str, component_index: int) -> str:
	json_text = get_json_from_target_id(target_id)
	return get_component_from_json(json_text, component_index)

def get_component_dict(target_id: str, component_index: int) -> dict:
	json_text = get_json_from_target_id(target_id)
	return json.loads(get_component_from_json(json_text, component_index))

def add_component(target_id: str, json_component_text: str):
	json_text = get_json_from_target_id(target_id)
	json_text = add_component_to_json(json_text, json_component_text)
	serialize_json_to_target_id(target_id, json_text)

def replace_component(target_id: str, json_component_text: str, component_index: int):
	json_text = get_json_from_target_id(target_id)
	json_text = replace_component_in_json(json_text, json_component_text, component_index)
	serialize_json_to_target_id(target_id, json_text)

def remove_component(target_id: str, component_index: int):
	json_text = get_json_from_target_id(target_id)
	json_text = remove_component_from_json(json_text, component_index)
	serialize_json_to_target_id(target_id, json_text)

