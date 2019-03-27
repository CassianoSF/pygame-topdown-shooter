import pygame, numpy, pyrr, math, os, string
from OpenGL.GL import *
from Shader import Shader
from Object import Object
from VertexBuffer import VertexBuffer
from VertexArray import VertexArray
from IndexBuffer import IndexBuffer
from Texture import Texture

VERT_DATA = numpy.array([0.5, 0.5, 0.0,
                         0.5, -0.5, 0.0,
                        -0.5, -0.5, 0.0,
                        -0.5, 0.5, 0.0],
                        dtype="float32")

VERT_DATA_2 = numpy.array([-0.5, -0.5, 0.0,
                         -0.5, -1.5, 0.0,
                        -1.5, -1.5, 0.0,
                        -1.5, -0.5, 0.0],
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



class App:
    def __init__(self):

        cube = Object("cube.obj")

        self.shader = Shader("VertexShader.shader", "FragmentShader.shader")
        
        self.va1 = VertexArray()
        self.vb_box_1 = VertexBuffer(VERT_DATA)
        self.va1.add_buffer(0, 3, self.vb_box_1)
        self.vb_texture = VertexBuffer(TEXTURE_COORD_DATA)
        self.va1.add_buffer(1, 2, self.vb_texture)
        self.ib = IndexBuffer(INDICES)

        self.va2 = VertexArray()
        self.vb_box_2 = VertexBuffer(VERT_DATA_2)
        self.va2.add_buffer(0, 3, self.vb_box_2)
        self.vb_texture = VertexBuffer(TEXTURE_COORD_DATA)
        self.va2.add_buffer(1, 2, self.vb_texture)
        self.ib = IndexBuffer(INDICES)

        self.texture = Texture("./textures/the_floor/the_floor/crate_1.png")

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

    def render(self):
        self.move()
        self.mvp = self.mount_mvp(self.model, self.view, self.projection)
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

        self.va1.bind()

        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        self.va2.bind()

        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        self.shader.unbind()


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