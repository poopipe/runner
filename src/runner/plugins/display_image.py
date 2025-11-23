import moderngl
import numpy as np

from PIL import Image


class GLProcessor:
    def __init__(self) -> None:
        self.context: moderngl.Context = moderngl.create_context(standalone=True)
        self.vertex_shader: str = self._vertex_shader()
        self.fragment_shader: str = self._fragment_shader()
        self.program: moderngl.Program = self.context.program(
            self.vertex_shader, self.fragment_shader
        )
        self.vbo: moderngl.Buffer = self._vertex_buffer()
        self.vao: moderngl.VertexArray = self._vertex_array()
        self.fbo: moderngl.Framebuffer = self._frame_buffer()

        print(f"{type(self.fbo)}")

    def _vertex_shader(self) -> str:
        s: str = """
        #version 330

        in vec2 in_vert;
        in vec3 in_color;

        out vec3 v_color;

        void main() {
            v_color = in_color;
            gl_Position = vec4(in_vert, 0.0, 1.0);
        }
        """
        return s

    def _fragment_shader(self) -> str:
        s = """
        #version 330

        in vec3 v_color;
        out vec3 f_color;

        void main() {
            f_color = v_color;
        }
        """
        return s

    def _vertex_buffer(self) -> moderngl.Buffer:
        x = np.linspace(-1.0, 1.0, 50)
        y = np.random.rand(50) - 0.5
        r = np.zeros(50)
        g = np.ones(50)
        b = np.zeros(50)

        vertices = np.dstack([x, y, r, g, b])
        return self.context.buffer(vertices.astype("f4").tobytes())

    def _vertex_array(self):
        return self.context.vertex_array(self.program, self.vbo, "in_vert", "in_color")

    def _frame_buffer(self) -> moderngl.Framebuffer:
        return self.context.framebuffer(
            color_attachments=[self.context.texture((512, 512), 3)]
        )

    def execute(self) -> None:
        self.fbo.use()
        self.fbo.clear(0.0, 0.0, 0.0, 1.0)
        self.vao.render(moderngl.LINE_STRIP)

    def show(self) -> None:
        Image.frombytes(
            "RGB",
            self.fbo.size,
            self.fbo.color_attachments[0].read(),
            "raw",
            "RGB",
            0,
            -1,
        ).show()


glp = GLProcessor()
glp.execute()
glp.show()
'''
ctx = moderngl.create_context(standalone=True)

prog = ctx.program(
    vertex_shader="""
        #version 330

        in vec2 in_vert;
        in vec3 in_color;

        out vec3 v_color;

        void main() {
            v_color = in_color;
            gl_Position = vec4(in_vert, 0.0, 1.0);
        }
    """,
    fragment_shader="""
        #version 330

        in vec3 v_color;

        out vec3 f_color;

        void main() {
            f_color = v_color;
        }
    """,
)

x = np.linspace(-1.0, 1.0, 50)
y = np.random.rand(50) - 0.5
r = np.zeros(50)
g = np.ones(50)
b = np.zeros(50)

vertices = np.dstack([x, y, r, g, b])

vbo = ctx.buffer(vertices.astype("f4").tobytes())
vao = ctx.vertex_array(prog, vbo, "in_vert", "in_color")

fbo = ctx.framebuffer(color_attachments=[ctx.texture((512, 512), 3)])
fbo.use()
fbo.clear(0.0, 0.0, 0.0, 1.0)
vao.render(moderngl.LINE_STRIP)

Image.frombytes(
    "RGB", fbo.size, fbo.color_attachments[0].read(), "raw", "RGB", 0, -1
).show()
'''
