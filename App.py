import OpenGL, PIL, pygame, numpy, pyrr, math, sys, os

from OpenGL.GL import *
from PIL import Image
from pyrr import Matrix44, Vector4, Vector3, Quaternion

VERT_DATA = numpy.array([1.5, 1.5, 0.0,
                         1.5, -1.5, 0.0,
                        -1.5, -1.5, 0.0,
                        -1.5, 1.5, 0.0],
                        dtype="float32")

COLOR_DATA = numpy.array([1.0, 0.0, 0.0, 1.0,
                          0.0, 1.0, 0.0, 1.0,
                          0.0, 0.0, 1.0, 1.0,
                          0.0, 1.0, 1.0, 1.0],
                          dtype="float32")

TEXTURE_COORD_DATA = numpy.array([1.0, 1.0,
                                  1.0, -1.0,
                                 -1.0, -1.0,
                                 -1.0, 1.0],
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
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
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
        self.mvp_matrix = self.projection()
        self.gl_buffers()
        self.cube_model_matrix, self.cube_view_matrix, self.cube_proj_matrix = self.gl_translate(Vector3([1.0, 1.0, 1.0]), 45.0, Vector3([0.5, 0.5, 0.5]))
        self.cube_mvp = self.gl_translate3(Vector3([1.0, 1.0, 1.0]), -45.0, Vector3([0.5, 0.5, 0.5]))

    def gl_texture(self, texture_path):
        return 0

    def gl_buffers(self):
        self.va = VertexArray()

        self.vb_positions = VertexBuffer(VERT_DATA)
        self.va.add_buffer(0, 3, self.vb_positions)

        self.vb_texture = VertexBuffer(TEXTURE_COORD_DATA)
        self.va.add_buffer(1, 2, self.vb_texture)

        self.ib = IndexBuffer(INDICES)

        self.texture = Texture("./textures/the_floor/the_floor/floor_2.png")

    def projection(self):
        scale_matrix = pyrr.matrix44.create_from_scale(Vector3([1, 1, 1]))
        rot_matrix = Matrix44.identity()
        trans_matrix = pyrr.matrix44.create_from_translation(Vector3([1, 1, 0]))

        model_matrix = scale_matrix * rot_matrix * trans_matrix
        view_matrix = pyrr.matrix44.create_look_at(
            numpy.array([4, 3, 3]), 
            numpy.array([1, 1, 0]), 
            numpy.array([0, 1, 0])
        )
        proj_matrix = pyrr.matrix44.create_perspective_projection_matrix(45.0, 1280/720, 0.1, 1000.0)
        mvp_matrix = proj_matrix * view_matrix * model_matrix

        return mvp_matrix

    def gl_translate(self, translation, rotation, scale):
        trans_matrix = pyrr.matrix44.create_from_translation(translation)
        rot_matrix = numpy.transpose(pyrr.matrix44.create_from_y_rotation(rotation))
        scale_matrix = numpy.transpose(pyrr.matrix44.create_from_scale(scale))

        model_matrix = scale_matrix * rot_matrix * trans_matrix
        view_matrix = pyrr.matrix44.create_look_at(
            numpy.array([2.0, 2.0, 3.0], dtype="float32"),
            numpy.array([0.0, 0.0, 0.0], dtype="float32"),
            numpy.array([0.0, 1.0, 0.0], dtype="float32")
        )
        proj_matrix = pyrr.matrix44.create_perspective_projection(45.0, WINDOW_WIDTH/WINDOW_HEIGHT, 0.1, 200.0)

        return model_matrix, view_matrix, proj_matrix

    def gl_translate2(self, translation, rotation, scale):
        trans_matrix = pyrr.matrix44.create_from_translation(translation)
        rot_matrix = pyrr.matrix44.create_from_y_rotation(rotation)
        scale_matrix = pyrr.matrix44.create_from_scale(scale)

        model_matrix = numpy.matmul(numpy.matmul(scale_matrix,rot_matrix),trans_matrix)
        view_matrix = pyrr.matrix44.create_look_at(
            numpy.array([2.0, 2.0, 3.0], dtype="float32"),
            numpy.array([0.0, 0.0, 0.0], dtype="float32"),
            numpy.array([0.0, 1.0, 0.0], dtype="float32")
        )
        proj_matrix = pyrr.matrix44.create_perspective_projection(45.0, WINDOW_WIDTH/WINDOW_HEIGHT, 0.1, 200.0)
        m = numpy.matmul(numpy.matmul(model_matrix,view_matrix),proj_matrix) 

        return m

    def gl_translate3(self, translation, rotation, scale):
        trans_matrix = numpy.transpose(pyrr.matrix44.create_from_translation(translation))
        rot_matrix = numpy.transpose(pyrr.matrix44.create_from_y_rotation(rotation))
        scale_matrix = numpy.transpose(pyrr.matrix44.create_from_scale(scale))

        model_matrix = numpy.matmul(numpy.matmul(trans_matrix,rot_matrix),scale_matrix)
        view_matrix = numpy.transpose(pyrr.matrix44.create_look_at(
            numpy.array([2.0, 2.0, 3.0], dtype="float32"),
            numpy.array([0.0, 0.0, 0.0], dtype="float32"),
            numpy.array([0.0, 1.0, 0.0], dtype="float32"))
        )
        proj_matrix = numpy.transpose(pyrr.matrix44.create_perspective_projection(45.0, WINDOW_WIDTH/WINDOW_HEIGHT, 0.1, 200.0))
        m = numpy.matmul(numpy.matmul(proj_matrix,view_matrix),model_matrix) 

        return numpy.transpose(m)

    def display(self):
        glEnable(GL_DEPTH_TEST)

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.shader.bind()
        self.texture.bind()

        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

        texture_uniform = glGetUniformLocation(self.shader.id, "the_texture")
        glUniform1i(texture_uniform, 0)

        trans_uniform = glGetUniformLocation(self.shader.id, "mvp")
        glUniformMatrix4fv(trans_uniform, 1, GL_FALSE, self.cube_mvp)
        model_location = glGetUniformLocation(self.shader.id, "model")
        glUniformMatrix4fv(model_location, 1, GL_FALSE, self.cube_model_matrix)
        view_location = glGetUniformLocation(self.shader.id, "view")
        glUniformMatrix4fv(view_location, 1, GL_FALSE, self.cube_view_matrix)
        proj_location = glGetUniformLocation(self.shader.id, "proj")
        glUniformMatrix4fv(proj_location, 1, GL_FALSE, self.cube_proj_matrix)

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