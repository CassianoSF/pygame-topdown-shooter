from OpenGL.GL import *

class VertexArray:
    def __init__(self):
        self.id = glGenVertexArrays(1)
        self.size = 0

    def delete(self):
        glDeleteVertexArrays(1, self.id)

    def add_buffer(self, index, size, vb):
        self.bind() 
        vb.bind()
        self.size += vb.size
        glEnableVertexAttribArray(index)
        glVertexAttribPointer(index, size, GL_FLOAT, GL_FALSE, 0, None)

    def bind(self):
        glBindVertexArray(self.id)

    def unbind(self):
        glBindVertexArray(0)
