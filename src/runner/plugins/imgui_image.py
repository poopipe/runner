from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

from imgui_bundle import imgui

from moderngl import (
    CULL_FACE,
    DEPTH_TEST,
    Attribute,
    Framebuffer,
    Program,
    Uniform,
    Varying,
)
from moderngl_window.context.base import WindowConfig
from moderngl_window import geometry
from moderngl_window.integrations.imgui_bundle import ModernglWindowRenderer
from moderngl_window.opengl.vao import VAO

from pyglm.glm import mat4, translate, perspective, radians, vec3, quat


def get_program_uniforms(prog: Program) -> list[Uniform]:
    """get uniforms from moderngl Program"""
    return [prog.get(x, 0) for x in prog if isinstance(prog.get(x, 0), Uniform)]


def get_program_varyings(prog: Program) -> list[Varying]:
    """get uniforms from moderngl Program"""
    return [prog.get(x, 0) for x in prog if isinstance(prog.get(x, 0), Varying)]


def get_program_attributes(prog: Program) -> list[Attribute]:
    """get uniforms from moderngl Program"""
    return [prog.get(x, 0) for x in prog if isinstance(prog.get(x, 0), Attribute)]


@dataclass()
class NodeWindow:
    """the individual rendery windows"""

    name: str
    parameters: dict[str, Any]
    fbo: Framebuffer
    vao: VAO
    prog: Program
    prog_uniforms: list[Uniform] = field(default_factory=list)
    prog_varyings: list[Varying] = field(default_factory=list)
    prog_attributes: list[Attribute] = field(default_factory=list)

    def __post_init__(self) -> None:

        # These can be set here - that's just initialisation
        self.prog["m_camera"].write(mat4())
        self.prog["m_proj"].write(perspective(radians(75), 1.0, 1, 100))

        # set uniforms etc. we do it here in case we need to override the others
        for key, value in self.parameters.items():
            self.prog[key].value = value

        self.prog_uniforms = get_program_uniforms(self.prog)
        self.prog_varyings = get_program_varyings(self.prog)
        self.prog_attributes = get_program_attributes(self.prog)


class WindowEvents(WindowConfig):
    gl_version = (3, 3)
    title = "imgui Integration"
    resource_dir = (Path(__file__).parent).resolve()
    aspect_ratio = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        imgui.create_context()
        self.wnd.ctx.error
        self.imgui = ModernglWindowRenderer(self.wnd)

        self.node_windows: list[NodeWindow] = [
            NodeWindow(
                "one",
                {"color": (1.0, 0.0, 0.0, 1.0)},
                self.ctx.framebuffer(
                    color_attachments=self.ctx.texture((512, 512), 4),
                    depth_attachment=self.ctx.depth_texture((512, 512)),
                ),
                geometry.cube(size=(2, 2, 2)),
                self.load_program("cube_simple.glsl"),
            ),
            NodeWindow(
                "two",
                {"color": (0.0, 1.0, 0.0, 1.0)},
                self.ctx.framebuffer(
                    color_attachments=self.ctx.texture((512, 512), 4),
                    depth_attachment=self.ctx.depth_texture((512, 512)),
                ),
                geometry.quad_2d(size=(2, 2)),
                self.load_program("cube_simple2.glsl"),
            ),
        ]

        # register framebuffer color textures with imgui
        for node_window in self.node_windows:
            self.imgui.register_texture(node_window.fbo.color_attachments[0])
            print([x.name for x in node_window.prog_uniforms])
            print([x.name for x in node_window.prog_varyings])
            print([x.name for x in node_window.prog_attributes])

    def on_render(self, time: float, frametime: float):
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
            # self.cube.render(self.prog)

        # Render UI to screen
        self.wnd.use()
        self.render_ui()

    def render_ui(self):
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

        # imgui.show_demo_window()
        """
        imgui.begin("Custom window", True)
        imgui.text("Bar")
        imgui.text_colored(imgui.ImVec4(0.2, 1.0, 0.0, 1.0), "Eggs")
        imgui.end()
        """

        for node_window in self.node_windows:
            # Create window with the framebuffer image
            imgui.begin(node_window.name, True)
            # Create an image control by passing in the OpenGL texture ID (glo)
            # and pass in the image size as well.
            # The texture needs to he registered using register_texture for this to work
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
    WindowEvents.run()
