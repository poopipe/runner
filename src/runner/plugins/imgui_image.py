from pathlib import Path

from imgui_bundle import imgui

from moderngl import CULL_FACE, DEPTH_TEST
from moderngl_window.context.base import WindowConfig
from moderngl_window import geometry
from moderngl_window.integrations.imgui_bundle import ModernglWindowRenderer

from pyglm.glm import mat4, translate, vec3, quat

from runner.libs_gl.types import NodeWindow


class MainWindow(WindowConfig):
    """top level app window"""

    gl_version = (3, 3)
    title = "imgui Integration"
    resource_dir = (Path(__file__).parent).resolve()
    aspect_ratio = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        imgui.create_context()
        self.wnd.ctx.error
        self.imgui = ModernglWindowRenderer(self.wnd)

        self.node_windows: list[NodeWindow] = []
        # register framebuffer color textures with imgui
        for node_window in self.node_windows:
            self.imgui.register_texture(node_window.fbo.color_attachments[0])

    def add_node_window(self, name: str):
        """adds a node window - no idea why but this can't be called externally to the window"""
        self.node_windows.append(
            NodeWindow(
                name,
                {"color": (1.0, 0.0, 0.0, 1.0)},
                self.ctx.framebuffer(
                    color_attachments=self.ctx.texture((256, 256), 4),
                    depth_attachment=self.ctx.depth_texture((256, 256)),
                ),
                geometry.cube(size=(2, 2, 2)),
                self.load_program("cube_simple.glsl"),
            )
        )
        for node_window in self.node_windows:
            self.imgui.register_texture(node_window.fbo.color_attachments[0])

    def on_render(self, time: float, frame_time: float):
        # Rotate/move cube
        rotation = mat4(quat(vec3(time, time, time)))
        translation = translate(vec3(0.0, 0.0, -3.5))
        model = translation * rotation
        self.ctx.enable(DEPTH_TEST | CULL_FACE)

        for node_window in self.node_windows:
            # Render cube to offscreen texture / fbo
            node_window.fbo.use()
            node_window.fbo.clear()
            node_window.prog["m_model"].write(model)
            node_window.vao.render(node_window.prog)

        # Render UI to screen
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

        # toolbox
        imgui.set_next_window_pos((0, 0))
        imgui.set_next_window_size((256, 1024))
        imgui.begin("toolbox", False)
        imgui.text("toolbox")

        if imgui.button("add node", (240, 32)):
            self.add_node_window("ass")
        imgui.end()
        #

        # imgui.show_demo_window()
        """
        imgui.begin("Custom window", True)
        imgui.text("Bar")
        imgui.text_colored(imgui.ImVec4(0.2, 1.0, 0.0, 1.0), "Eggs")
        imgui.end()
        """

        imgui.text(f"frame time: {frame_time:.3f}")

        for node_window in self.node_windows:
            # Create window with the framebuffer image
            imgui.begin(node_window.name, True)
            # Create an image control by passing in the OpenGL texture ID (glo)
            # and pass in the image size as well.
            imgui.image(node_window.fbo.color_attachments[0].glo, node_window.fbo.size)
            imgui.end()

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
    MainWindow.run()
