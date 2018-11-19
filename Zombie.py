import pygame, sys, os
import pprint
import importlib
import math
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


class Zombie:
    def __init__(self, height, width, textures, x, y, angle):
    	self.textures = textures
        self.height = height
        self.width = width
        self.x = x
        self.y = y
        self.angle = angle
        self.attacking = False
        self.running = False
        self.move = False
        self.animation = 'idle'

    def render(self, clock, player):
    	animation = self.textures['zombie'][self.animation]
    	glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.angle,0,0,1)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);


        # # Ajuste no tamanho das texturas
        # gambiarra = 0
        # if(self.gun == "knife" and self.animation == "meleeattack"):
        #     glTranslatef(0.01*40,-0.45*40, 0)
        #     gambiarra = 6.2

        # if(self.gun == "flashlight" and self.animation == "meleeattack"):
        #     glTranslatef(-0.1*40, 0.2*40, 0)
        #     gambiarra = 2.2

        # if(self.gun == "handgun" and self.animation == "meleeattack"):
        #     glTranslatef(0.2*40,-0.2*40, 0)
        #     gambiarra = 3.2

        # if((self.gun == "rifle" or self.gun == "shotgun") and self.animation == "meleeattack" ):
        #     glTranslatef(0*40, 0*40, 0)
        #     gambiarra = 8



        glBindTexture(GL_TEXTURE_2D, animation[clock % len(animation)])
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
    	pass