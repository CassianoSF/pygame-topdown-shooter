from OpenGL.GL import *
import pygame

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