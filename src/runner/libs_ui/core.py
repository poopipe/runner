from pathlib import Path
from re import T
from imgui_bundle import imgui
from moderngl import CULL_FACE, DEPTH_TEST

from moderngl_window import create_window_config_instance, run_window_config_instance
from moderngl_window.context.base.window import WindowConfig
from moderngl_window.integrations.imgui_bundle import ModernglWindowRenderer
from numpy import core

from runner.libs.utils import get_plugins


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

        if imgui.tree_node("tree##1"):
            # TODO:
            #       we need a library pallette that lists plugin files
            #       a workspace that shows each plugin selected, in the order they were added
            #       a button that runs the plugins in sequencee, passing data from previous to next
            #       Things to consider:
            #           input/output types - will need to find this out from  the plugin
            #           start and end nodes probably want to be templated based on job type
            #           distinction between image and data nodes (probably - could just be the input/output types)
            #       Later:
            #           make it a node graph (maybe, arguably user can just pack and unpack data in the plugins)

            plugins = get_plugins()
            internal_plugins = [x for x in plugins if x.external == False]
            external_plugins = [x for x in plugins if x.external == True]

            if imgui.tree_node("builtins"):
                for plugin in internal_plugins:
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
                for plugin in external_plugins:
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

            imgui.tree_pop()

        imgui.render()
        self.imgui.render(imgui.get_draw_data())

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
