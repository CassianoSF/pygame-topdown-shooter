import pygame, sys, os
import pprint
import importlib
import math
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


class Player:
    def __init__(self, height, width, textures, x, y, angle):
        self.textures = textures
        self.height = height
        self.width = width
        self.x = x
        self.y = y
        self.angle = angle
        self.key_states = list(map(lambda x :0, list(range(500))))
        self.shooting = False
        self.attacking = False
        self.running = False
        self.move = False
        self.reloading = False
        self.animation = 'idle'
        self.gun = 'knife'



    def rotate(angle):
        self.angle = angle

    def move(x, y):
        self.x = x
        self.y = y

    def render(self, clock):
        if(self.shooting and self.gun in ['handgun', 'shotgun', 'rifle'] and clock % 2):
            glPushMatrix()
            glTranslatef(self.x, self.y, 0)
            glRotatef(self.angle+180,0,0,1)
            glBindTexture(GL_TEXTURE_2D, self.textures['shoot']['shoot'][0])
            glBegin(GL_QUADS);
            glTexCoord2f(0.0, 0.0);
            glVertex2f(  30, -10);
            glTexCoord2f(0.0, 1.0);
            glVertex2f(  30, 60);
            glTexCoord2f(1.0, 1.0);
            glVertex2f(  120, 60);
            glTexCoord2f(1.0, 0.0);
            glVertex2f(  120, -10);
            glEnd();
            glPopMatrix()


        animation = self.textures[self.gun][self.animation]
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.angle,0,0,1)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);


        # Ajuste no tamanho das texturas
        gambiarra = 0
        if(self.gun == "knife" and self.animation == "meleeattack"):
            glTranslatef(0.01*40,-0.45*40, 0)
            gambiarra = 6.2

        if(self.gun == "flashlight" and self.animation == "meleeattack"):
            glTranslatef(-0.1*40, 0.2*40, 0)
            gambiarra = 2.2

        if(self.gun == "handgun" and self.animation == "meleeattack"):
            glTranslatef(0.2*40,-0.2*40, 0)
            gambiarra = 3.2

        if((self.gun == "rifle" or self.gun == "shotgun") and self.animation == "meleeattack" ):
            glTranslatef(0*40, 0*40, 0)
            gambiarra = 8



        glBindTexture(GL_TEXTURE_2D, animation[clock % len(animation)])
        glBegin(GL_QUADS)
        glTexCoord(0, 0)
        glVertex( (self.width+gambiarra*4)/2.,  (self.height+gambiarra*4)/2., 0)
        glTexCoord(0, 1)
        glVertex( (self.width+gambiarra*4)/2., -(self.height+gambiarra*4)/2., 0)
        glTexCoord(1, 1)
        glVertex(-(self.width+gambiarra*4)/2., -(self.height+gambiarra*4)/2., 0)
        glTexCoord(1, 0)
        glVertex(-(self.width+gambiarra*4)/2.,  (self.height+gambiarra*4)/2., 0)
        glEnd()
        glBindTexture(GL_TEXTURE_2D, 0)
        glPopMatrix()

    def hundleMouseDown(self, event):
        if(event.button == 1):
            self.shooting = True
        if(event.button == 3):
            self.attacking = True

    def hundleMouseUp(self, event):
        if(event.button == 1):
            self.shooting = False
        if(event.button == 3):
            self.attacking = False

    def hundleMouseMove(self, event):
        x = event.pos[0]-400
        y = event.pos[1]-300
        self.angle = -math.atan2(x, y)/3.1415*180.0 - 90;
        

    def update(self):
        if(self.reloading and self.gun in ['handgun', 'shotgun', 'rifle']):
            self.animation = 'reload'
        elif(self.shooting and self.gun in ['handgun', 'shotgun', 'rifle']):
            self.animation = 'shoot'
        elif(self.attacking):
            self.animation = 'meleeattack'
        elif(self.move):
            self.animation = 'move'
        else:
            self.animation = 'idle'
        keys_down = self.key_states[38] + self.key_states[39] + self.key_states[40] + self.key_states[25]
        speed = 2
        if(keys_down):
            self.move = True
        if(keys_down > 1):
            speed = 2*0.7
        if(self.key_states[50]):
            speed = speed * 2
        if(self.key_states[39]): 
            self.y += speed
        if(self.key_states[25]): 
            self.y -= speed
        if(self.key_states[38]): 
            self.x -= speed
        if(self.key_states[40]): 
            self.x += speed

    def hundleKeyDown(self, event):
        self.key_states[event.scancode] = 1
        if(self.key_states[10]):
            self.gun = 'knife'
        if(self.key_states[11]):
            self.gun = 'handgun'
        if(self.key_states[12]):
            self.gun = 'shotgun'
        if(self.key_states[13]):
            self.gun = 'rifle'
        if(self.key_states[41]):
            self.gun = 'flashlight'

    def hundleKeyUp(self, event):
        self.key_states[event.scancode] = 0



