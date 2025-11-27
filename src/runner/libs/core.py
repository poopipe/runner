"""
core code:  plugin loading etc..
"""

from dataclasses import dataclass
from inspect import Signature, signature
from itertools import chain
from pathlib import Path
from types import ModuleType
from typing import Any, Callable
from multiprocessing import Pool
from multipledispatch import dispatch
from importlib import import_module

from runner import PACKAGE_PATH, PLUGIN_PATH
from runner.plugin_libs.types import PluginDictResult, PluginResult


#
# Exceptions
class PluginError(Exception):
    """
    wrapper class for exceptions raised while running a plugin

    should not be used in a plugin, plugins should raise builtin/other custom exceptions
    which are caught and wrapped in a PluginError by the plugin runner

    self.plugin is a reference to the loaded plugin module - this lets us inform the user
    of which bit shit the bed without crashing the main app

    """

    def __init__(self, message: Exception, plugin: ModuleType):
        self.plugin = plugin
        print(self.plugin)
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.plugin.__name__}: {self.message}"


class InvalidModule(Exception):
    pass


#
# types
@dataclass
class Plugin:
    """
    data pertaining to location of plugin - so it can be listed/loaded etc.
    """

    name: str
    external: bool
    path: Path


@dataclass()
class PluginInfo:
    """
    data about plugin used for typing of nodes
    inputs: list of tuples representing (name, type, default value) for each arg
    """

    name: str
    inputs: list[tuple[str, Any, Any]]
    output: Any


#
# Plugin handling functions
def load_plugin(name) -> ModuleType:
    """load a module from disk/env/whatever"""
    # TODO: this needs to support on disk locations
    #       and installed packages
    mod = import_module(f"runner.plugins.{name}")
    return mod


def get_plugin_name(p: Path):
    """return polite name for plugin"""
    return p.stem


def get_plugins() -> list[Plugin]:
    """gather list of python files in specified locations"""
    external_paths = list(PLUGIN_PATH.glob("*.py"))
    internal_paths = list((PACKAGE_PATH / "plugins").glob("*.py"))

    external_plugins = [Plugin(get_plugin_name(x), True, x) for x in external_paths]
    internal_plugins = [Plugin(get_plugin_name(x), False, x) for x in internal_paths]
    excluded_names = ["__init__"]

    all_plugins = [
        x
        for x in (internal_plugins + external_plugins)
        if x.name.lower() not in [y.lower() for y in excluded_names]
    ]
    return all_plugins


def inspect_plugin(plugin: Plugin) -> PluginInfo:
    """
    look inside a module,
    determine whether it's plugin shaped.
    if so, return a PluginInfo object
    """

    loaded_module: ModuleType = load_plugin(plugin.name)
    # bail if we cannot find plugin_main()
    if not hasattr(loaded_module, "plugin_main"):
        raise InvalidModule(f"{plugin.name} does not contain plugin_main() function")

    # bail if we find plugin main but it's not a function
    plugin_main: Callable = getattr(loaded_module, "plugin_main")
    if not isinstance(plugin_main, Callable):
        raise InvalidModule(f"{plugin.name}.plugin_main() is not callable")

    #  get function signature
    plugin_main_signature: Signature = signature(plugin_main)

    # bail if  plugin_main() returns something that isn't a PluginResult type
    # TODO: consider disallowing plugins that don't return anything
    #       this only exists to allow support for display_result plugin at present
    return_type: type = plugin_main_signature.return_annotation

    # None gives us empty, as does missing annotation
    if not return_type is Signature.empty:
        # check return type is valid
        if not issubclass(return_type, PluginResult):
            if not isinstance(return_type, PluginResult):
                raise InvalidModule(
                    f"{plugin.name}.plugin_main() must return a PluginResult or one of its subclasses"
                )

    # get arg data, these become inputs
    inputs: list[tuple[str, Any, Any]] = []
    for k, v in plugin_main_signature.parameters.items():
        inputs.append((k, v.annotation, v.default))

    return PluginInfo(plugin.name, inputs, return_type)


#
#    overloads for run_plugin()
#    the type checker gets angry but have faith
#
@dispatch(str, PluginResult)
def run_plugin(name: str, input: PluginResult) -> PluginResult:
    """run this when input is a PluginResult"""
    plugin = load_plugin(name)

    try:
        result = plugin.plugin_main(input)
        return result

    except Exception as e:
        raise PluginError(e, plugin)


@dispatch(str)
def run_plugin(name: str) -> PluginResult:
    """run this when there is no input"""
    plugin = load_plugin(name)
    try:
        result = plugin.plugin_main()
        return result

    except Exception as e:
        raise PluginError(e, plugin)


@dispatch(str, list)
def run_plugin(name: str, input: list[Any]) -> PluginResult:
    """run async when data is a list"""
    plugin = load_plugin(name)

    try:
        # async version
        pool = Pool()
        results = pool.map_async(plugin.plugin_main, input).get()
        result_data = {results.index(x): x for x in results}

        # unpack the data from our pool results into a standard PluginResult
        data_values: list[Any] = [list(x.data.values()) for x in result_data.values()]
        flattened_data_values = list(chain.from_iterable(data_values))
        plugin_result_data = {
            flattened_data_values.index(x): x for x in flattened_data_values
        }
        return PluginDictResult(plugin.__name__, plugin_result_data)

    except Exception as e:
        raise PluginError(e, plugin)


if __name__ == "__main__":
    plugins = [x for x in get_plugins()]
    for plugin in plugins:
        print(plugin.name)
        plugin_info = inspect_plugin(plugin)
        for input in plugin_info.inputs:
            print(input[1].__name__)
        print("")
