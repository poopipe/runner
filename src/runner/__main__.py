"""
This thing runs plugin scripts in a sequence

It has:
    standardised result format plugin_libs.types.PluginResult
    option to run plugins in parallel on content of a PluginResult

It will have:
    plugin api
    it might have to get a ui and i dont think it can be a tui

How I want it to work:
    use a plugin to define initial input
    while stillgotpluginstoprocess:
        use a plugin to process input supplied by previous step
    use a plugin to display / store output

consider a node graph
consider making this process image data
can i opengl???

"""

from runner import PLUGIN_PATH
from runner.libs.types import PluginError
from runner.plugin_libs.types import PluginResult
from runner.libs.core import run_plugin


def get_input_list() -> list[str]:
    result = ["ass", "butt", "car", "dongle"]
    return result


def main() -> None:
    result = run_plugin("reverse_string", get_input_list())
    run_plugin("result_handler", result)
    print("\n")
    result = run_plugin("make_image")
    run_plugin("result_handler", result)


if __name__ == "__main__":

    from runner.libs_ui import core

    core.AppWindow.run()

    # main()
