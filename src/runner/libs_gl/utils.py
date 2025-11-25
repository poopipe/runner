from moderngl import Program, Uniform, Varying, Attribute


def get_program_uniforms(prog: Program) -> list[Uniform]:
    """get uniforms from moderngl Program"""
    return [prog.get(x, 0) for x in prog if isinstance(prog.get(x, 0), Uniform)]


def get_program_varyings(prog: Program) -> list[Varying]:
    """get uniforms from moderngl Program"""
    return [prog.get(x, 0) for x in prog if isinstance(prog.get(x, 0), Varying)]


def get_program_attributes(prog: Program) -> list[Attribute]:
    """get uniforms from moderngl Program"""
    return [prog.get(x, 0) for x in prog if isinstance(prog.get(x, 0), Attribute)]
