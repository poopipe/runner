from runner.plugin_libs.types import PluginResult

def plugin_main(data:PluginResult)->PluginResult:
    print("sub_module2_main")
    result = PluginResult(__name__, {})

    for k, v in data.data.items():
        result.data[k] =  [str(x).upper() for x in v]

    return result

