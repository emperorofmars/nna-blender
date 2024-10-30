import bpy
import re
import functools

def getJsonFromTargetingObject(targetingObject: bpy.types.Object) -> str:
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

def serializeJsonToTargetingObject(targetingObject: bpy.types.Object, json: str):
	clearTargetingObject(targetingObject)
	remainingJsonBytes = str.encode(json) # get actual bytes
	lineNr = 0
	while(len(remainingJsonBytes) > 0):
		line = remainingJsonBytes[0:61-len(str(lineNr))]
		remainingJsonBytes = remainingJsonBytes[len(line):]
		addLineToTargetingObject(targetingObject, line.decode(), lineNr)
		lineNr += 1

def clearTargetingObject(object: bpy.types.Object):
	for child in object.children:
		bpy.data.objects.remove(child)

def addLineToTargetingObject(targetingObject: bpy.types.Object, line: str, lineNr: int):
	originalSelectedObject = bpy.context.active_object
	bpy.ops.object.empty_add()
	nnaObject = bpy.context.active_object
	nnaObject.name = "$" + str(lineNr) + "$" + line
	nnaObject.parent = targetingObject
	bpy.context.view_layer.objects.active = originalSelectedObject
