import pygame, numpy, pyrr, math, os, string
from OpenGL.GL import *
from Shader import Shader
from Object import Object
from VertexBuffer import VertexBuffer
from VertexArray import VertexArray
from IndexBuffer import IndexBuffer
from Texture import Texture

WINDOW_WIDTH=1280
WINDOW_HEIGHT=720

class App:
    def __init__(self):
        cube = Object("../res/cube.obj")

        print(cube.vertices)
        print(cube.tex_map)
        print(cube.indices)

        self.texture = Texture("../textures/the_floor/the_floor/crate_1.png")
        self.shader = Shader("VertexShader.shader", "FragmentShader.shader")
        self.va1 = VertexArray()
        self.vb_box_1 = VertexBuffer(cube.vertices)
        self.va1.add_buffer(0, 3, self.vb_box_1)
        self.vb_texture = VertexBuffer(cube.tex_map)
        self.va1.add_buffer(1, 3, self.vb_texture)
        self.ib = IndexBuffer(cube.indices)

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

    def mount_mvp(self, model, view, projection):
        trans_matrix = numpy.transpose(pyrr.matrix44.create_from_translation(model['translation']))
        rot_matrix_x = numpy.transpose(pyrr.matrix44.create_from_x_rotation(model['rotation'][0]))
        rot_matrix_y = numpy.transpose(pyrr.matrix44.create_from_y_rotation(model['rotation'][1]))
        rot_matrix_z = numpy.transpose(pyrr.matrix44.create_from_z_rotation(model['rotation'][2]))
        rot_matrix   = numpy.matmul(numpy.matmul(rot_matrix_x, rot_matrix_y),rot_matrix_z)
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

        self.mvp = self.motion(self.model, self.view, self.projection)
        self.shader.add_uniform_matrix_4f("mvp", self.mvp)
        self.draw(self.va1, self.ib, self.texture, self.shader)


    def motion(self, model, view, projection):
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
        return self.mount_mvp(model, view, projection)

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