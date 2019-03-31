from OpenGL.GL import *

class VertexBuffer:
    def __init__(self, data):
        self.id = glGenBuffers(1)
        self.size = len(data)
        glBindBuffer(GL_ARRAY_BUFFER, self.id)
        glBufferData(GL_ARRAY_BUFFER, data, GL_STATIC_DRAW)

    def delete(self):
        glDeleteBuffers(1, self.id)

    def bind(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.id)

    def unbind(self):
        glBindBuffer(GL_ARRAY_BUFFER, 0)
