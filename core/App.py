import pygame, numpy, pyrr, math, os, string
from OpenGL.GL import *
from Shader import Shader
from Object import Object
from VertexBuffer import VertexBuffer
from VertexArray import VertexArray
from IndexBuffer import IndexBuffer
from Texture import Texture

VERT_DATA_1 = numpy.array([
                        -2.0, -2.0,  2.0,
                         2.0, -2.0,  2.0,
                        -2.0,  2.0,  2.0,
                         2.0,  2.0,  2.0,
                        -2.0,  2.0, -2.0,
                         2.0,  2.0, -2.0,
                        -2.0, -2.0, -2.0,
                         2.0, -2.0, -2.0
                           #  1.0,  1.0, 1.0,
                           #  1.0, -1.0, 1.0,
                           # -1.0, -1.0, 1.0,
                           # -1.0,  1.0, 1.0,

                           #  1.0,  1.0, -1.0,
                           #  1.0, -1.0, -1.0,
                           # -1.0, -1.0, -1.0,
                           # -1.0,  1.0, -1.0
                        ],
                        dtype="float32")

VERT_DATA_2 = numpy.array([0.5, 0.5, 0.0,
                         0.5, -0.5, 0.0,
                        -0.5, -0.5, 0.0,
                        -0.5, 0.5, 0.0],
                        dtype="float32")


TEXTURE_COORD_DATA = numpy.array([
                                0.0, 0.0, 0.0,
                                1.0, 0.0, 0.0,
                                0.0, 1.0, 0.0,
                                1.0, 1.0, 0.0


                                ],
                                 dtype="float32")

INDICES_1 = numpy.array([

                        0, 1, 2,
                        2, 1, 3,
                        2, 3, 4,
                        4, 3, 5,
                        4, 5, 6,
                        6, 5, 7,
                        6, 7, 0,
                        0, 7, 1,
                        1, 7, 3,
                        3, 7, 5,
                        6, 0, 4,
                        4, 0, 2

                         # 0, 1, 3,
                         # 1, 2, 3,
                         # 2, 7, 3,
                         # 2, 7, 6,
                         # 0, 3, 4,
                         # 7, 4, 3,
                         # 0, 1, 5,
                         # 0, 5, 4,
                         # 2, 5, 6,
                         # 1, 5, 2,
                         # 4, 6, 7,
                         # 4, 5, 6




                        ],
                       dtype="int32")

INDICES_2 = numpy.array([0, 1, 3,
                       1, 2, 3],
                       dtype="int32")

WINDOW_WIDTH=1280
WINDOW_HEIGHT=720

g_model = {
    'translation': [0.0, 0.0, 0.0],
    'rotation':    [0.0, 0.0, 0.0],
    'scale':       [1.0, 1.0, 1.0]
}
g_view = {
    'position': [0.0, 0.0, 12.0],
    'target':   [0.0, 0.0, 0.0],
    'up':       [0.0, 1.0, 0.0]
}
g_projection = {
    'fovy':   45.0, 
    'aspect': WINDOW_WIDTH/WINDOW_HEIGHT,
    'near':   0.1,
    'far':    200.0,
    'dtype':  None 
}

class App:
    def __init__(self):

        cube = Object("../res/suzanne.obj")
        cube.vertices
        cube.indices
        cube.tex_map
        cube.normals

        self.shader = Shader("VertexShader.shader", "FragmentShader.shader")

        self.va1 = VertexArray()
        self.vb_box_1 = VertexBuffer(cube.vertices)
        self.va1.add_buffer(0, 3, self.vb_box_1)
        self.vb_texture = VertexBuffer(cube.tex_map)
        self.va1.add_buffer(1, 3, self.vb_texture)
        self.ib = IndexBuffer(cube.indices)

        
        # self.va1 = VertexArray()
        # self.vb_box_1 = VertexBuffer(VERT_DATA_1)
        # self.va1.add_buffer(0, 3, self.vb_box_1)
        # self.vb_texture = VertexBuffer(TEXTURE_COORD_DATA)
        # self.va1.add_buffer(1, 3, self.vb_texture)
        # self.ib = IndexBuffer(INDICES_1)

        # self.va2 = VertexArray()
        # self.vb_box_2 = VertexBuffer(VERT_DATA_2)
        # self.va2.add_buffer(0, 3, self.vb_box_2)
        # self.vb_texture = VertexBuffer(TEXTURE_COORD_DATA)
        # self.va2.add_buffer(1, 2, self.vb_texture)
        # self.ib = IndexBuffer(INDICES_2)

        self.texture = Texture("../textures/the_floor/the_floor/crate_1.png")

        self.model = {
            'translation': [0.0, 0.0, 0.0],
            'rotation':    [0.0, 0.0, 0.0],
            'scale':       [1.0, 1.0, 1.0]
        }
        self.view = {
            'position': [0.0, 0.0, 12.0],
            'target':   [0.0, 0.0, 0.0],
            'up':       [0.0, 1.0, 0.0]
        }
        self.projection = {
            'fovy':   45.0, 
            'aspect': WINDOW_WIDTH/WINDOW_HEIGHT,
            'near':   0.1,
            'far':    200.0,
            'dtype':  None 
        }
        self.mvp = self.mount_mvp(self.model, self.view, self.projection)
        self.key_state = list(map(lambda x :0, list(range(500))))

    def mount_mvp(self, model, view, projection):
        trans_matrix = numpy.transpose(pyrr.matrix44.create_from_translation(model['translation']))
        rot_matrix_x = numpy.transpose(pyrr.matrix44.create_from_x_rotation(model['rotation'][0]))
        rot_matrix_y = numpy.transpose(pyrr.matrix44.create_from_y_rotation(model['rotation'][1]))
        rot_matrix_z = numpy.transpose(pyrr.matrix44.create_from_z_rotation(model['rotation'][2]))
        rot_matrix = numpy.matmul(numpy.matmul(rot_matrix_x, rot_matrix_y),rot_matrix_z)
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

    def draw(self, va, ib, texture, shader):
        shader.bind()
        texture.bind()
        va.bind()
        ib.bind()
        glDrawElements(GL_TRIANGLES, va.size, GL_UNSIGNED_INT, None)
        shader.unbind()

    def render(self):
        glEnable(GL_DEPTH_TEST)

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Transparency
        glEnable(GL_BLEND)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) 

        self.shader.add_uniform_1i("the_texture", 0)

        
        self.move()
        self.mvp = self.mount_mvp(self.model, self.view, self.projection)

        self.shader.add_uniform_matrix_4f("mvp", self.mvp)
        self.draw(self.va1, self.ib, self.texture, self.shader)

        # self.shader.add_uniform_matrix_4f("mvp", self.mvp)
        # self.draw(self.va2, self.ib, self.texture, self.shader)


    def move(self):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_UP]:
            self.model['rotation'][0] -= 0.03
        if pressed[pygame.K_DOWN]:
            self.model['rotation'][0] += 0.03
        if pressed[pygame.K_LEFT]:
            self.model['rotation'][2] -= 0.03
        if pressed[pygame.K_RIGHT]:
            self.model['rotation'][2] += 0.03
        if pressed[pygame.K_a]:
            self.model['rotation'][1] -= 0.03
        if pressed[pygame.K_d]:
            self.model['rotation'][1] += 0.03
        if pressed[pygame.K_w]:
            self.view['position'][2] -= 0.1
        if pressed[pygame.K_s]:
            self.view['position'][2] += 0.1

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

def main():
    pygame.init()
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.display.set_caption("APP")
    pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
    clock = pygame.time.Clock()
    app = App()

    while True:
        [app.handle_event(event) for event in pygame.event.get()]

        clock.tick(60)
        app.render()
        pygame.display.flip()

if __name__ == "__main__":
    main()