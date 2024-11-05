
import re;

_match_lr = re.compile("(?i)(([._\-|:][lr])|[._\-|:\s]?(right|left))$")

def get_nna_name(target_id: str) -> str:
	split = target_id.split('$', 1)
	return split[len(split) - 1]

def get_symmetry(name: str) -> tuple[str, str]:
	match = _match_lr.search(name)
	if(match):
		return (name[:match.start()], match.group())
	else:
		return (name, "")
