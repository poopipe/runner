from pathlib import Path
from runner import PACKAGE_PATH, PLUGIN_PATH
from runner.libs.types import Plugin

print(f"{PLUGIN_PATH=}")


def get_plugin_name(p: Path):
    """return polite name for plugin"""
    # TODO: eventually, look in the plugin and find a declaration for it
    return p.stem


def get_plugins() -> list[Plugin]:
    """gather list of python files in specified locations"""
    # TODO: we will need to  look in the plugin files to ensure that there is a plugin_main()
    #       eventually
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
