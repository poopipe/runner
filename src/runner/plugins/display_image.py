import moderngl
import numpy as np

from PIL import Image

'''
#EXAMPLE CODE


# Source - https://stackoverflow.com/a
# Posted by Grimmy
# Retrieved 2025-11-25, License - CC BY-SA 4.0

import moderngl
from array import array
from PIL import Image

ctx = moderngl.create_context(standalone=True)
framebuffer_size = (512, 512)

texture1 = ctx.texture((2, 2), 3, array('B', [200, 0, 0] * 4))
texture2 = ctx.texture((2, 2), 3, array('B', [0, 200, 0] * 4))

fbo = ctx.framebuffer(
    ctx.renderbuffer(framebuffer_size),
    ctx.depth_renderbuffer(framebuffer_size),
)

program = ctx.program(
    vertex_shader="""
    #version 330

    in vec2 in_pos;
    in vec2 in_uv;
    out vec2 uv;

    void main() {
        gl_Position = vec4(in_pos, 0.0, 1.0);
        uv = in_uv;
    }
    """,
    fragment_shader="""
    #version 330

    uniform sampler2D texture0;
    out vec4 fragColor;
    in vec2 uv;

    void main() {
        fragColor = texture(texture0, uv);
    }
    """,
)

buffer1 = ctx.buffer(array('f',
    [
        # pos xy    uv
        -0.75,  0.75, 1.0, 0.0,
        -0.75, -0.75, 0.0, 0.0,
         0.75,  0.75, 1.0, 1.0,
         0.75, -0.75, 1.0, 0.0,
    ]
))

buffer2 = ctx.buffer(array('f',
    [
        # pos xy    uv
        -0.5,  0.5, 1.0, 0.0,
        -0.5, -0.5, 0.0, 0.0,
         0.5,  0.5, 1.0, 1.0,
         0.5, -0.5, 1.0, 0.0,
    ]
))


vao1 = ctx.vertex_array(program, [(buffer1, '2f 2f', 'in_pos', 'in_uv')])
vao2 = ctx.vertex_array(program, [(buffer2, '2f 2f', 'in_pos', 'in_uv')])

# --- Render ---
# Make a loop here if you need to render multiple passes

fbo.use()
fbo.clear()

# draw quad with red texture
texture1.use()
vao1.render(mode=moderngl.TRIANGLE_STRIP)

# draw quad with green texture
texture2.use()
vao2.render(mode=moderngl.TRIANGLE_STRIP)

ctx.finish()

img = Image.frombytes('RGB', fbo.size, fbo.read())
img.save('output.png')

'''


class GLProcessor:
    """create context/buffers and all that jazz, methods to execute shaders and display result"""

    def __init__(self, in_buffer: moderngl.Framebuffer | None = None) -> None:
        self.context: moderngl.Context = moderngl.create_context(standalone=True)
        self.vertex_shader: str = self._vertex_shader()
        self.fragment_shader: str = self._fragment_shader()
        self.program: moderngl.Program = self.context.program(
            self.vertex_shader, self.fragment_shader
        )

        # input (optional)
        self.in_fbo: moderngl.Framebuffer | None = in_buffer

        self.vbo: moderngl.Buffer = self._vertex_buffer()
        self.vao: moderngl.VertexArray = self._vertex_array()
        self.fbo: moderngl.Framebuffer = self._frame_buffer()

        # output (filled on execute)
        self.out_fbo: moderngl.Framebuffer | None = None

    def _vertex_shader(self) -> str:
        s: str = """
        #version 430

        in vec3 in_vertex;
        in vec2 in_uv;

        uniform vec2  in_scale;

        out vec2 v_uv;

        void main() {
          v_uv = in_uv;
          gl_Position = vec4(in_vertex, 1.0);
        }
        """
        return s

    def _fragment_shader(self) -> str:
        s = """
        #version 430

        layout (location = 0) out vec4 out_color;

        in vec2 v_uv;        
        
        uniform sampler2D Texture0;
        
        void main() {

            vec4 tex = texture(Texture0, v_uv);
            out_color = tex;
            //out_color += vec4(v_uv.x, v_uv.y, 0.0f, 1.0f) + vec4(tex.xyx * 0.01, 1.0);
        }
 
        """
        return s

    def _get_vertex_array(self, data_arrays):
        arrays = zip(*data_arrays)
        unpacked = []
        for element in arrays:
            [unpacked.append(x) for x in element]
        return np.array([x for y in unpacked for x in y], dtype=np.float32)

    def _vertex_buffer(self) -> moderngl.Buffer:
        vertex_positions = [
            # first triangle
            [1.0, 1.0, -1.0],
            [1.0, -1.0, -1.0],
            [-1.0, 1.0, -1.0],
            # second triangle
            [1.0, -1.0, -1.0],
            [-1.0, -1.0, -1.0],
            [-1.0, 1.0, -1.0],
        ]

        vertex_texcoords = [
            # first triangle
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 0.0],
            # second triangle
            [1.0, 1.0],
            [0.0, 1.0],
            [0.0, 0.0],
        ]

        # build vertex buffer based on input
        vertices = self._get_vertex_array([vertex_positions, vertex_texcoords])
        return self.context.buffer(vertices.tobytes())

    def _vertex_array(self):
        return self.context.vertex_array(self.program, self.vbo, "in_vertex", "in_uv")

    def _frame_buffer(self) -> moderngl.Framebuffer:
        fbo: moderngl.Framebuffer = self.context.framebuffer(
            color_attachments=[self.context.texture((512, 512), 4)]
        )
        return fbo

    def execute(self) -> None:
        print(f"{self.fbo.color_attachments[0].components=}")

        # TODO: This is not correctly converting the incoming framebuffer into a texture
        #       I am very confused

        # if we have an input
        if self.in_fbo:
            # create a texture from the input fbo
            in_fbo_tex: moderngl.Texture = self.context.texture(
                self.in_fbo.color_attachments[0].size,
                self.in_fbo.color_attachments[0].components,
                self.in_fbo.color_attachments[0].read(),
            )

            # create an fbo from the texture
            new_fbo: moderngl.Framebuffer = self.context.framebuffer(
                color_attachments=in_fbo_tex
            )
            # bind texture to program
            self.program["Texture0"] = 0
            new_fbo.use()
            self.fbo = new_fbo

        # render it
        self.fbo.use()
        # self.fbo.clear(0.0, 0.0, 0.0, 1.0)
        self.vao.render()
        self.out_fbo = self.fbo

        # this is our output
        print(f"{self.out_fbo.color_attachments[0]=}")

    def show(self, buffer: moderngl.Framebuffer | None) -> None:
        if not buffer:
            return None
        # display out_buffer
        img = Image.frombytes(
            "RGBA",
            buffer.size,
            buffer.color_attachments[0].read(),
            "raw",
            "RGBA",
            0,
            -1,
        )
        print(img.has_transparency_data)
        img.show()


# passing the framebuff
glp_0 = GLProcessor()
glp_0.execute()

# pass fbo into the next one
glp = GLProcessor(in_buffer=glp_0.out_fbo)
glp.show(glp.in_fbo)
glp.execute()
# looks like data isnt being pssed through properly
glp.show(glp.out_fbo)
