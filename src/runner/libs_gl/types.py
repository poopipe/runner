from dataclasses import dataclass, field
from typing import Any

from moderngl import Framebuffer, Program, Uniform, Varying, Attribute
from moderngl_window.opengl.vao import VAO
from pyglm.glm import mat4, perspective, radians

from runner.libs_gl.utils import (
    get_program_uniforms,
    get_program_varyings,
    get_program_attributes,
)


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
