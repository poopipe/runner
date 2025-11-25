from pathlib import Path
from imgui_bundle import imgui
from moderngl import CULL_FACE, DEPTH_TEST

from moderngl import Context
from moderngl_window import create_window_config_instance, run_window_config_instance
from moderngl_window.context.base.window import WindowConfig
from moderngl_window.integrations.imgui_bundle import ModernglWindowRenderer


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

    AppWindow.run()
