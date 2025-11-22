from multipledispatch import dispatch

from runner.plugin_libs.types import PluginDictResult, PluginMatResult, PluginResult


@dispatch(PluginMatResult)
def plugin_main(data: PluginMatResult):
    print("result_handler mat")
    print(f"__{data.name}__")
    print(data.data)


@dispatch(PluginDictResult)
def plugin_main(data: PluginDictResult):
    print("result_handler dict")
    print(f"__{data.name}__")
    for k, v in data.data.items():
        print(f"{str(k).ljust(32)}: {str(v)}")
