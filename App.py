import OpenGL, PIL, pygame, numpy, pyrr, math, sys, os

from OpenGL.GL import *
from PIL import Image
from pyrr import Matrix44, Matrix33, Vector4, Vector3, Quaternion

VERT_DATA = numpy.array([0.5, 0.5, 0.0,
                         0.5, -0.5, 0.0,
                        -0.5, -0.5, 0.0,
                        -0.5, 0.5, 0.0],
                        dtype="float32")

COLOR_DATA = numpy.array([1.0, 0.0, 0.0, 1.0,
                          0.0, 1.0, 0.0, 1.0,
                          0.0, 0.0, 1.0, 1.0,
                          0.0, 1.0, 1.0, 1.0],
                          dtype="float32")

TEXTURE_COORD_DATA = numpy.array([1.0, 1.0,
                                  1.0, 0.0,
                                  0.0, 0.0,
                                  0.0, 1.0],
                                 dtype="float32")

INDICES = numpy.array([0, 1, 3,
                       1, 2, 3],
                       dtype="int32")

WINDOW_WIDTH=1280
WINDOW_HEIGHT=720


class Shader:
    def __init__(self, frag_path, vert_path):
        self.id = glCreateProgram()
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)

        with open(frag_path, "r") as vert_file:
            vert_source = vert_file.read()
        with open(vert_path, "r") as frag_file:
            frag_source = frag_file.read()

        glShaderSource(vertex_shader, vert_source)
        glShaderSource(fragment_shader, frag_source)

        glCompileShader(vertex_shader)
        if not glGetShaderiv(vertex_shader, GL_COMPILE_STATUS):
            info_log = glGetShaderInfoLog(vertex_shader)
            print ("Compilation Failure for " + vertex_shader + " shader:\n" + info_log)

        glCompileShader(fragment_shader)
        if not glGetShaderiv(fragment_shader, GL_COMPILE_STATUS):
            info_log = glGetShaderInfoLog(fragment_shader)
            print ("Compilation Failure for " + fragment_shader + " shader:\n" + info_log)

        glAttachShader(self.id, vertex_shader)
        glAttachShader(self.id, fragment_shader)

        glLinkProgram(self.id)

        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

    def bind(self):
        glUseProgram(self.id)

    def unbind(self):
        glUseProgram(0)


class VertexBuffer:
    def __init__(self, data):
        self.id = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.id)
        glBufferData(GL_ARRAY_BUFFER, data, GL_STATIC_DRAW)

    def delete(self):
        glDeleteBuffers(1, self.id)

    def bind(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.id)

    def unbind(self):
        glBindBuffer(GL_ARRAY_BUFFER, 0)

class VertexArray:
    def __init__(self):
        self.id = glGenVertexArrays(1)

    def delete(self):
        glDeleteVertexArrays(1, self.id)

    def add_buffer(self, index, count, vb):
        self.bind() 
        vb.bind()
        glEnableVertexAttribArray(index)
        glVertexAttribPointer(index, count, GL_FLOAT, GL_FALSE, 0, None)

    def bind(self):
        glBindVertexArray(self.id)

    def unbind(self):
        glBindVertexArray(0)

class IndexBuffer():
    def __init__(self, indices):
        self.id = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.id)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices, GL_STATIC_DRAW)

    def bind(self):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.id)

    def unbind(self):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

class Texture():
    def __init__(self, path):
        self.id = glGenTextures(1)
        tex = pygame.image.load(path)
        tex_surface = pygame.image.tostring(tex, 'RGBA')
        tex_width, tex_height = tex.get_size()
        glBindTexture(GL_TEXTURE_2D, self.id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, tex_width, tex_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_surface) 
        glBindTexture(GL_TEXTURE_2D, 0)

    def delete(self):
        glDeleteTextures(1, self.id) 

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.id)

    def unbind(self):
        glBindTexture(GL_TEXTURE_2D, 0)

class GLProgram:
    def __init__(self):
        self.shader = Shader("VertexShader.shader", "FragmentShader.shader")
        self.va = VertexArray()

        self.vb_positions = VertexBuffer(VERT_DATA)
        self.va.add_buffer(0, 3, self.vb_positions)

        self.vb_texture = VertexBuffer(TEXTURE_COORD_DATA)
        self.va.add_buffer(1, 2, self.vb_texture)

        self.ib = IndexBuffer(INDICES)

        self.texture = Texture("./textures/the_floor/the_floor/crate_1.png")

        model = {
            'translation': [0.0, 0.0, 0.0],
            'rotation':    [0.0, 0.0, 0.0],
            'scale':       [1.0, 1.0, 1.0]
        }
        view = {
            'position': [0.0, 0.0, 6.0],
            'target':   [0.0, 0.0, 0.0],
            'up':       [0.0, 1.0, 0.0]
        }
        projection = {
            'fovy':   45.0, 
            'aspect': WINDOW_WIDTH/WINDOW_HEIGHT,
            'near':   0.1,
            'far':    200.0,
            'dtype':  None 
        }

        self.mvp = self.mvp(model, view, projection)

    def mvp(self, model, view, projection):
        trans_matrix = numpy.transpose(pyrr.matrix44.create_from_translation(model['translation']))
        rot_matrix = numpy.transpose(pyrr.matrix44.create_from_x_rotation(model['rotation'][0]))
        rot_matrix = numpy.transpose(pyrr.matrix44.create_from_y_rotation(model['rotation'][1]))
        rot_matrix = numpy.transpose(pyrr.matrix44.create_from_z_rotation(model['rotation'][2]))
        scale_matrix = numpy.transpose(pyrr.matrix44.create_from_scale(model['scale'] ))
        model_matrix = numpy.matmul(numpy.matmul(trans_matrix,rot_matrix),scale_matrix)

        view_matrix = numpy.transpose(pyrr.matrix44.create_look_at(
            numpy.array(view['position'], dtype="float32"),
            numpy.array(view['target'],   dtype="float32"),
            numpy.array(view['up'],       dtype="float32")
        ))

        proj_matrix = numpy.transpose(pyrr.matrix44.create_perspective_projection(
            projection['fovy'],
            projection['aspect'],
            projection['near'],
            projection['far'],
            projection['dtype']
        ))

        m = numpy.matmul(numpy.matmul(proj_matrix,view_matrix),model_matrix) 
        return numpy.transpose(m)

    def display(self):
        glEnable(GL_DEPTH_TEST)

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.shader.bind()
        self.texture.bind()

        # Transparency
        glEnable(GL_BLEND)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) 

        texture_uniform = glGetUniformLocation(self.shader.id, "the_texture")
        glUniform1i(texture_uniform, 0)

        trans_uniform = glGetUniformLocation(self.shader.id, "mvp")
        glUniformMatrix4fv(trans_uniform, 1, GL_FALSE, self.mvp)

        self.va.bind()

        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        self.shader.unbind()


def main():
    pygame.init()
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.display.set_caption("3D Graphics")
    pygame.display.set_mode((1280, 720), pygame.DOUBLEBUF | pygame.OPENGL)
    clock = pygame.time.Clock()
    gl = GLProgram()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        clock.tick(60)
        gl.display()
        pygame.display.flip()

if __name__ == "__main__":
    main()