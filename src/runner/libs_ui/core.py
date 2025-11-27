from inspect import Signature
from pathlib import Path
from imgui_bundle import ImVec2, imgui
from moderngl import CULL_FACE, DEPTH_TEST

from moderngl_window.context.base.window import WindowConfig
from moderngl_window.integrations.imgui_bundle import ModernglWindowRenderer

from runner.libs.core import PluginInfo, get_plugins, inspect_plugin


class AppWindow(WindowConfig):
    gl_version: tuple[int, int] = (4, 3)
    title: str = "runner"
    resource_dir = (Path(__file__).parent).resolve()
    aspect_ratio = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        imgui.create_context()
        self.wnd.ctx.error
        self.imgui = ModernglWindowRenderer(self.wnd)
        self.plugins = get_plugins()
        self.internal_plugins = [x for x in self.plugins if x.external == False]
        self.external_plugins = [x for x in self.plugins if x.external == True]
        self.internal_plugin_info = [inspect_plugin(x) for x in self.internal_plugins]

    def on_render(self, time: float, frame_time: float):
        # rotate/move cube
        self.ctx.enable(DEPTH_TEST | CULL_FACE)

        # render ui to screen
        self.wnd.use()
        self.render_ui(frame_time)

    def render_ui(self, frame_time: float):
        """Render the UI"""
        imgui.new_frame()
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):
                clicked_quit, selected_quit = imgui.menu_item(
                    "Quit", "Cmd+Q", False, True
                )

                if clicked_quit:
                    exit(1)

                imgui.end_menu()
            imgui.end_main_menu_bar()

        """
        you were cleaning up plugins/imgui_docking and trying to work out how to make this  UI have docking

        you probably want to implement the node graph that comes with imgui_bundle for the flow graph window in anticipation  of this turning into a node-editor


        """

        # TODO:
        #       figure out how to select a thing in the plugin window and add it to
        #       a specific location in the flow graph
        #       use case:
        #           we start with:
        #               getlist > sortlist > displayresult
        #           we add reverselist at index 2:
        #               getlist > sortlist > reverselist > displayresult
        #   -
        #       Add a button that runs the plugins in sequence, passing data from previous to next
        #   -
        #       Later:
        #           make it a node graph (maybe, arguably user can just pack and unpack data in the plugins)

        # create plugin window
        self.create_plugin_window()

        # create graph view
        self.create_flow_graph()

        imgui.render()

        self.imgui.render(imgui.get_draw_data())

    def create_plugin_window(self):
        imgui.begin("Plugins")
        if imgui.tree_node("builtins"):
            for plugin in self.internal_plugins:
                node_flags = (
                    imgui.TreeNodeFlags_.span_avail_width.value
                    | imgui.TreeNodeFlags_.leaf.value
                )
                imgui.tree_node_ex(
                    f"{plugin.name}",
                    node_flags,
                    f"node {plugin.name}",
                )
                imgui.tree_pop()
            imgui.tree_pop()
            imgui.spacing()

        if imgui.tree_node("user"):
            for plugin in self.external_plugins:
                node_flags = (
                    imgui.TreeNodeFlags_.span_avail_width.value
                    | imgui.TreeNodeFlags_.leaf.value
                )
                imgui.tree_node_ex(
                    f"{plugin.name}",
                    node_flags,
                    f"node {plugin.name}",
                )
                imgui.tree_pop()
            imgui.tree_pop()
            imgui.spacing()

        imgui.end()

    def create_flow_graph_item(
        self, plugin_id: int, plugin_info: PluginInfo, flags: int
    ):
        """
        create item in flow_graph.  currently displays type info about inputs and outputs
        """
        if imgui.tree_node(f"{plugin_info.name}"):
            for input_id, input in enumerate(plugin_info.inputs):
                name = input[0]
                type = input[1].__name__
                default = input[2] if not input[2] is Signature.empty else None

                input_str = f"{type}"
                input_str = f"{'input'.ljust(10)}{input_str.ljust(8)}{name.ljust(8)}"
                if default:
                    input_str = f"{input_str}{default.ljust(8)}"

                imgui.tree_node_ex(f"{input_id}", flags, input_str)
                imgui.tree_pop()

            output_type = (
                plugin_info.output
                if not plugin_info.output is Signature.empty
                else None
            )
            output_str = f"{'output:'.ljust(10)}"
            if output_type:
                output_str = f"{output_str}{output_type.__name__}"

            imgui.tree_node_ex(
                f"{plugin_id}",
                flags,
                f"{output_str}",
            )
            imgui.tree_pop()
            imgui.tree_pop()

    def create_flow_graph(self):
        """
        eventually:
            stack up queue of jobs selected in the plugin list
            check that output type and input type of consecutive jobs work (not clear if this will be possible)
            re-order or otherwise edit job list
            highlight currently running job
            support load and save of flow graphs

        """

        leaf_flags: int = (
            imgui.TreeNodeFlags_.span_avail_width.value
            | imgui.TreeNodeFlags_.leaf.value
        )

        imgui.begin("Flow Graph")
        imgui.begin_list_box("steps", ImVec2(500, 300))
        # enumerate this cos im sure we'll need an ID later
        for plugin_id, plugin_info in enumerate(self.internal_plugin_info):
            self.create_flow_graph_item(plugin_id, plugin_info, leaf_flags)

        imgui.end_list_box()
        imgui.end()

    def on_resize(self, width: int, height: int):
        self.imgui.resize(width, height)

    def on_key_event(self, key, action, modifiers):
        self.imgui.key_event(key, action, modifiers)

    def on_mouse_position_event(self, x, y, dx, dy):
        self.imgui.mouse_position_event(x, y, dx, dy)

    def on_mouse_drag_event(self, x, y, dx, dy):
        self.imgui.mouse_drag_event(x, y, dx, dy)

    def on_mouse_scroll_event(self, x_offset, y_offset):
        self.imgui.mouse_scroll_event(x_offset, y_offset)

    def on_mouse_press_event(self, x, y, button):
        self.imgui.mouse_press_event(x, y, button)

    def on_mouse_release_event(self, x: int, y: int, button: int):
        self.imgui.mouse_release_event(x, y, button)

    def on_unicode_char_entered(self, char):
        self.imgui.unicode_char_entered(char)


if __name__ == "__main__":
    # moderngl-window WindowConfigs are basically black boxes as far as
    # poking them from the outside goes
    # .run() is a blocking call so we can't touch it until it stops
    # so all manipulation has to occur within the window class
    pass
    # AppWindow.run()
