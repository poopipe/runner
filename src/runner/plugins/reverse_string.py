from runner.plugin_libs.types import PluginDictResult


def plugin_main(s: str) -> PluginDictResult:
    l = "".join(list(s)[::-1])
    return PluginDictResult(__name__, {"_": l})
