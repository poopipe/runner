from runner.plugin_libs.types import PluginListResult

"""
Plugins must:
    have a plugin_main()
    use type annotation for plugin_main()s return type

Plugins shoud:
    use type annotations for args 


"""


def plugin_main(a: str, b: str, c: str = "poop") -> PluginListResult:
    result = ["ass", "butt", "car", "dongle"]
    return PluginListResult(__file__, result)
