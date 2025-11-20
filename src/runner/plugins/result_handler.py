from runner.plugin_libs.types import PluginResult

def plugin_main(data:PluginResult):
    print("result_handler_main")
    print(f"__{data.name}__")
    for k, v in data.data.items(): 
        print(f"{str(k).ljust(32)}: {str(v)}")
