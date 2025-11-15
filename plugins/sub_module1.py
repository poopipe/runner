from runner.libs.types import PluginError
from runner.plugin_libs.types import PluginResult

def plugin_main()->PluginResult:
    result = PluginResult(__name__, {"my_key":"my_value"})
    raise ValueError(f"something awful has happened")
    return result

