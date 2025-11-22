import numpy
from runner.plugin_libs.types import PluginMatResult, PluginResult


def plugin_main() -> PluginMatResult:
    return PluginMatResult(__name__, numpy.ndarray([4, 4, 3]))
