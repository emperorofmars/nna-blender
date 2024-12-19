from enum import StrEnum
import re;

_match_lr = re.compile("(?i)(([._\-|:][lr])|[._\-|:\s]?(right|left))$")
_match_l = re.compile("(?i)(([._\-|:]l)|[._\-|:\s]?left)$")
_match_r = re.compile("(?i)(([._\-|:]r)|[._\-|:\s]?right)$")

class SymmetrySide(StrEnum):
	Both = "both",
	Left = "left",
	Right = "right",


def get_nna_name(target_id: str, split_char = ';') -> str:
	split = target_id.split(split_char)
	return split[len(split) - 1]

def construct_nna_id(current_target_id: str, new_target_name: str, split_char = ';') -> str:
	current_split = current_target_id.split(split_char)
	ret = ""
	if(len(current_split) > 1):
		for part in current_split[0:len(current_split) - 1]:
			ret += part + split_char
	ret += new_target_name

	print(current_target_id)
	print(new_target_name)
	print(ret)
	return ret

def get_side_suffix(name: str) -> tuple[str, str]:
	match = _match_lr.search(name)
	if(match):
		return (name[:match.start()], match.group())
	else:
		return (name, "")

def detect_side(name: str) -> SymmetrySide:
	if(_match_l.search(name)): return SymmetrySide.Left
	elif(_match_r.search(name)): return SymmetrySide.Right
	else: return SymmetrySide.Both
