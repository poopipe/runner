from importlib import import_module
from types import ModuleType
from runner.libs.types import PluginError
from runner.plugin_libs.types import PluginResult


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

def main()->None:
    
    print("starting runner")
    try:
        result = run_plugin("sub_module1")
        result = run_plugin("sub_module2", result)
        run_plugin("result_handler", result)
    except PluginError as e:
        print(f"Plugin has shit the bed:\n{e}")

if __name__ == "__main__":
    main()
