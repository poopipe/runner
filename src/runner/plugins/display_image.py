import struct
import moderngl


def plugin_main():
    # TODO: this needs to take a PluginMatResult eventually
    #
    # TODO:
    #       we want this to render the data found in the incoming PluginMatResult to an image/buffer
    #       we also want a bunch of other things like this that take the incoming data and process it
    #       i think i need to do this with compute shaders or something which will be a whole load of fun
    #       i suspect that spinning up a new context every time is a shit idea but maybe it isn't

    gl_context = moderngl.create_context(standalone=True)

    program = gl_context.program(
        vertex_shader="""
        #version 330
        //output values for shader - end up in buffer
        out float value;
        out float product;

        void main(){
            value = gl_VertexID;
            product = gl_VertexID * gl_VertexID;
        }
        """,
        # define which output varyings to capture in our buffer
        varyings=("value", "product"),
    )

    NUM_VERTICES = 10

    # create empty vertex array
    vao = gl_context.vertex_array(program, [])

    # create buffer with spaace for 20 32bit floats
    buffer = gl_context.buffer(reserve=NUM_VERTICES * 8)

    # start a transforms with buffer as destination
    vao.transform(buffer, vertices=NUM_VERTICES)

    # unpack the 20 float values from the buffer (copy from gpu memory to system memory)
    # reading from buffer will cause a sync (python program stalls until shader is done)
    data = struct.unpack("20f", buffer.read())
    for i in range(0, 20, 2):
        print("value = {}, product = {}".format(*data[i : i + 2]))


if __name__ == "__main__":
    plugin_main()
