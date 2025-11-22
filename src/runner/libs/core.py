"""
core code:  plugin loading etc..
"""

from importlib import import_module
from itertools import chain
from types import ModuleType
from typing import Any
from multiprocessing import Pool
from multipledispatch import dispatch

from runner.libs.types import PluginError
from runner.plugin_libs.types import PluginDictResult, PluginResult


def load_plugin(name) -> ModuleType:
    """load a module from disk/env/whatever"""
    # TODO: this needs to support on disk locations
    #       and installed packages
    mod = import_module(f"runner.plugins.{name}")
    return mod


""" overloads for run_plugin() 
    the type checker gets angry but have faith
"""


@dispatch(str, PluginResult)
def run_plugin(name: str, input: PluginResult) -> PluginResult:
    """run this when input is a PluginResult"""
    plugin = load_plugin(name)
    result = plugin.plugin_main(input)
    return result

    """
    try:
        result = plugin.plugin_main(input)
        return result

    except Exception as e:
        raise PluginError(e, plugin)
    """


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
