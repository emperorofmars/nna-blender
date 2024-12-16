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

def get_symmetry(name: str) -> tuple[str, str]:
	match = _match_lr.search(name)
	if(match):
		return (name[:match.start()], match.group())
	else:
		return (name, "")

def detect_side(name: str) -> SymmetrySide:
	if(_match_l.search(name)): return SymmetrySide.Left
	elif(_match_r.search(name)): return SymmetrySide.Right
	else: return SymmetrySide.Both
