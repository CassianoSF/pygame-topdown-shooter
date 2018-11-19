import pygame, sys, os
import pprint
import importlib
import math
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


class GameObject:
    def __init__(self, height, width, texture, x, y, angle):
        self.height = height
        self.width = width
        self.texture = texture
        self.x = x
        self.y = y
        self.angle = angle
        self.key_states = list(map(lambda x :0, list(range(500))))

    def render(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.angle,0,0,1)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBegin(GL_QUADS)
        glTexCoord(0, 0)
        glVertex( self.width/2.,  self.height/2., 0)
        glTexCoord(0, 1)
        glVertex( self.width/2., -self.height/2., 0)
        glTexCoord(1, 1)
        glVertex(-self.width/2., -self.height/2., 0)
        glTexCoord(1, 0)
        glVertex(-self.width/2.,  self.height/2., 0)
        glEnd()
        glBindTexture(GL_TEXTURE_2D, 0)
        glPopMatrix()

    def render_floor(self):
        glPushMatrix()
        glRotatef(self.angle,0,0,1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBegin(GL_QUADS)
        glTexCoord(0, 0)
        glVertex( self.width/2.,  self.height/2., 0)
        glTexCoord(0, 200)
        glVertex( self.width/2., -self.height/2., 0)
        glTexCoord(200, 200)
        glVertex(-self.width/2., -self.height/2., 0)
        glTexCoord(200, 0)
        glVertex(-self.width/2.,  self.height/2., 0)
        glEnd()
        glBindTexture(GL_TEXTURE_2D, 0)
        glPopMatrix()
