import json
import bpy
import re
from . import nna_utils_tree


def get_json_from_target_id(target_id: str) -> str:
	"""Parses the numbered Json lines from the targeting object based on the `target_id`."""
	return get_json_from_targeting_object(nna_utils_tree.find_nna_targeting_object(target_id))

def get_json_from_targeting_object(targeting_object: bpy.types.Object) -> str:
	"""Parses the numbered Json lines from its child objects."""
	list = []
	for child in targeting_object.children:
		m1 = re.match(r"^\$[0-9]+\$.+", child.name)
		m2 = re.match(r"^\$[0-9]+.[0-9]+\$.+", child.name)
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
	"""Serializes the Json text into a targeting object based on the `target_id`. Any previous Json text will be removed."""
	serialize_json_to_targeting_object(nna_utils_tree.find_nna_targeting_object(target_id), json_text)

def serialize_json_to_targeting_object(targetingObject: bpy.types.Object, json_text: str):
	"""Serializes the Json text into a targeting object. Any previous Json text will be removed."""
	_clear_targeting_object(targetingObject)
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


def remove_targeting_object(object: bpy.types.Object):
	"""Remove a NNA targeting object, including all of its children (Json lines)."""
	_clear_targeting_object(object)
	bpy.data.objects.remove(object)

def _clear_targeting_object(object: bpy.types.Object):
	for child in object.children:
		bpy.data.objects.remove(child)


def get_component(target_id: str, component_index: int) -> dict:
	return json.loads(get_json_from_target_id(target_id))[component_index]

def add_component(target_id: str, json_component: dict):
	json_text = get_json_from_target_id(target_id)
	if(len(json_text) > 2):
		json_object = json.loads(json_text)
		json_object.append(json_component)
		serialize_json_to_target_id(target_id, json.dumps(json_object))
	else:
		serialize_json_to_target_id(target_id, json.dumps([json_component]))

def replace_component(target_id: str, json_component: dict, component_index: int):
	json_object = json.loads(get_json_from_target_id(target_id))
	json_object[component_index] = json_component
	serialize_json_to_target_id(target_id, json.dumps(json_object))

def remove_component(target_id: str, component_index: int):
	json_object = json.loads(get_json_from_target_id(target_id))
	del(json_object[component_index])
	serialize_json_to_target_id(target_id, json.dumps(json_object))


def validate_component_text(json_text: str) -> dict:
	try:
		json_component = json.loads(json_text)
	except Exception as e:
		return { "success": False, "error": str(e) }
	ret = validate_component(json_component)
	if(ret):
		return { "success": False, "error": ret }
	else:
		return { "success": True, "value": json_component }

def validate_component(json_component: dict) -> str | None:
	if(type(json_component) != dict):
		return "Invalid NNA Json! Not an object"
	if(not json_component["t"]):
		return "Invalid NNA Json! Must be an object with a \"t\" property"
	return None


def validate_component_list_text(json_text: str) -> dict:
	try:
		json_component_list = json.loads(json_text)
	except ValueError as e:
		return { "success": False, "error": str(e) }
	ret = validate_component_list(json_component_list)
	if(ret):
		return { "success": False, "error": ret }
	else:
		return { "success": True, "value": json_component_list }


def validate_component_list(json_component_list: list) -> str | None:
	if(type(json_component_list) != list):
		return "Invalid NNA Json! Not an object"
	for json_component in json_component_list:
		err = validate_component(json_component)
		if(err):
			return err
	return None
