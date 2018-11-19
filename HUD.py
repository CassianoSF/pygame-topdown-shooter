import pygame, sys, os
import pprint
import importlib
import math
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


class HUD:
    def __init__(self):
        self.font = pygame.font.Font('./boston_traffic.ttf', 50)
        self.text = ''

    def setText(self, text):
        self.text = text

    def render(self, screen, x, y):
        
        tex_id = glGenTextures(1)
        textsurface = self.font.render(self.text, False, (1, 1, 1, 1))
        tex = pygame.image.tostring(textsurface, 'RGBA')
        tex_width, tex_height = textsurface.get_size()
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0);
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tex_width, tex_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex)
        glBindTexture(GL_TEXTURE_2D, 0)

        glPushMatrix()
        glTranslatef(x, y+300, 0)
        glRotatef(180,0,0,1)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glBegin(GL_QUADS)
        glTexCoord(0, 0)
        glVertex( tex_width/2.,  tex_height/2., 0)
        glTexCoord(0, 1)
        glVertex( tex_width/2., -tex_height/2., 0)
        glTexCoord(1, 1)
        glVertex(-tex_width/2., -tex_height/2., 0)
        glTexCoord(1, 0)
        glVertex(-tex_width/2.,  tex_height/2., 0)
        glEnd()
        glBindTexture(GL_TEXTURE_2D, 0)
        glPopMatrix()