from .src.nna.nna_registry import NNAOperatorType
from .src.nna.nna_twist_component import AddNNATwistComponentOperator
from . import auto_load

auto_load.init()


def register():
	auto_load.register()


def unregister():
	auto_load.unregister()
