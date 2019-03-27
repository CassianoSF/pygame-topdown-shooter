from OpenGL.GL import *

class IndexBuffer():
    def __init__(self, indices):
        self.id = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.id)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices, GL_STATIC_DRAW)

    def bind(self):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.id)

    def unbind(self):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)