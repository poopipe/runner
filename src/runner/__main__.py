from importlib import import_module
from types import ModuleType
from typing import Any
from runner.libs.types import PluginError
from runner.plugin_libs.types import PluginResult
from itertools import chain

def load_plugin(name) -> ModuleType :
    mod = import_module(f"plugins.{name}")
    return mod

def run_plugin(name, *args, **kwargs) -> PluginResult:
    print(f"run plugin {name}")
    plugin = load_plugin(name)
    try:
        result = plugin.plugin_main(*args, **kwargs)
        return result

    except Exception as e:
        raise PluginError(e, plugin)

def run_plugin_parallel(name,data, processes:int|None=None) -> PluginResult:
    """run a plugin on a list of items, collate the results and return"""
    from multiprocessing import Pool
    print(f"run plugin {name}")
    plugin = load_plugin(name)

    try:
        # async version 
        pool = Pool(processes=processes)
        results = pool.map_async(plugin.plugin_main, data).get()
        result_data = {results.index(x):x for x in results}
        
        # unpack the data from our pool results into a standard PluginResult
        data_values:list[Any] = [list(x.data.values()) for x in result_data.values()]
        flattened_data_values = list(chain.from_iterable(data_values))
        plugin_result_data = {flattened_data_values.index(x) : x for x in flattened_data_values}

        return PluginResult(plugin.__name__, plugin_result_data)

    except Exception as e:
        raise PluginError(e, plugin)

def get_input_list()->list[str]:
    result = [
        "ass",
        "butt",
        "car",
        "dongle"
    ]
    return result


def main()->None:
    
    print("starting runner")
    try:
        result = run_plugin_parallel("reverse_string", get_input_list())
        run_plugin("result_handler", result)   
    except PluginError as e:
        print(f"Plugin has shit the bed:\n{e}")

if __name__ == "__main__":
    main()
