import pygame, sys, os
import pprint
import importlib
import math
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from random import randint

class Player:
    def __init__(self, height, width, textures, x, y, angle, inventory, speed, sound):
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
        self.gun = inventory['knife']
        self.inventory = inventory
        self.life = 100;
        self.reload_begin=0;
        self.last_shoot=0;
        self.speed = speed
        self.sound = sound
        self.score = 0

    def render(self, clock):
        if(self.shooting and self.shootTiming()):

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


        animation = self.textures[self.gun.name][self.animation]
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.angle,0,0,1)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);


        # Ajuste no tamanho das texturas
        gambiarra = 0
        if(self.gun.name == "knife" and self.animation == "meleeattack"):
            glTranslatef(0.01*40,-0.45*40, 0)
            gambiarra = 6.2

        if(self.gun.name == "flashlight" and self.animation == "meleeattack"):
            glTranslatef(-0.1*40, 0.2*40, 0)
            gambiarra = 2.2

        if(self.gun.name == "handgun" and self.animation == "meleeattack"):
            glTranslatef(0.2*40,-0.2*40, 0)
            gambiarra = 3.2

        if((self.gun.name == "rifle" or self.gun.name == "shotgun") and self.animation == "meleeattack" ):
            glTranslatef(0*40, 0*40, 0)
            gambiarra = 8

        glBindTexture(GL_TEXTURE_2D, animation[int(clock % len(animation))])
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

    def update(self, boxes):
        if(self.reloading and self.gun.name in ['handgun', 'shotgun', 'rifle']):
            reload_seconds=(pygame.time.get_ticks()-self.reload_begin)
            if reload_seconds>self.gun.reload_time*1000:
                self.reloading = False
                self.gun.bullets = self.gun.cap
            self.animation = 'reload'
        elif(self.shooting and self.gun.name in ['handgun', 'shotgun', 'rifle'] and self.shootTiming()):
            self.animation = 'shoot'
        elif(self.attacking):
            self.animation = 'meleeattack'
        elif(self.move):
            self.animation = 'move'
        else:
            self.animation = 'idle'
        keys_down = self.key_states[38] + self.key_states[39] + self.key_states[40] + self.key_states[25]
        speed = self.speed
        if(keys_down):
            self.move = True

        if(keys_down > 1):
            speed = speed * 0.7

        if(self.key_states[50]):
            speed = speed * 2

        if(self.key_states[39]): 
            if not self.boxColision(boxes, 0, +speed):
                self.y += speed

        if(self.key_states[25]): 
            if not self.boxColision(boxes, 0, -speed):
                self.y -= speed

        if(self.key_states[38]): 
            if not self.boxColision(boxes, -speed, 0):
                self.x -= speed

        if(self.key_states[40]): 
            if not self.boxColision(boxes, +speed, 0):
                self.x += speed

    def boxColision(self, boxes, x_ahead, y_ahead):
        for box in boxes:
            dx = box.x - self.x - x_ahead;
            dy = box.y - self.y - y_ahead;
            distance = (dy**2 + dx**2)**0.5
            angle_to = -(box.angle - math.atan2(dx, dy)/3.1415*180.0) % 360
            if((angle_to>135 and angle_to<225) or (angle_to>0 and angle_to<45) or (angle_to>315 and angle_to<360)):
                if distance <= (box.height/2.0)*(1.2+0.4*abs(math.sin(angle_to*3.1415/180))):
                    return True
            else:
                if distance <= (box.height/2.0)*(1.2+0.4*abs(math.cos(angle_to*3.1415/180))):
                    return True;
        return False;

    def shootTiming(self):
        if self.gun.name in ['handgun', 'shotgun', 'rifle']:
            if not self.reloading and self.gun.bullets == 0:
                self.reloading = True
                self.reload_begin = pygame.time.get_ticks()
                pygame.mixer.Channel(1).play(self.sound['reload'])
            if self.reloading or not self.shooting:
                return False
            interval = pygame.time.get_ticks()-self.last_shoot
            if (interval > 1000/self.gun.rate):
                self.gun.bullets -= 1
                self.last_shoot=pygame.time.get_ticks()
                return True
                # pygame.mixer.Channel(0).play(self.sound)
            if(interval<40):
                pygame.mixer.Channel(0).play(self.sound['shot'])
                return True
            else:
                pygame.mixer.Channel(2).play(self.sound['pump'])


    def takeHit(self):
        self.life -= 1
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotatef(randint(0, 360),0,0,1)
        glColor4f(0,0,0,0.4)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        glBindTexture(GL_TEXTURE_2D, self.textures['the_floor']['the_floor'][0])
        glBegin(GL_QUADS)
        glTexCoord(0, 0)
        glVertex( 100/2.,  100/2., 0)
        glTexCoord(0, 1)
        glVertex( 100/2., -100/2., 0)
        glTexCoord(1, 1)
        glVertex(-100/2., -100/2., 0)
        glTexCoord(1, 0)
        glVertex(-100/2.,  100/2., 0)
        glEnd()
        glBindTexture(GL_TEXTURE_2D, 0)
        glPopMatrix()


    def handleKeyDown(self, event):
        print(event)
        if self.life>0:
            self.key_states[event.scancode] = 1
            if(self.key_states[10]):
                self.gun = self.inventory['knife']
                self.reloading = False
                self.animation = "idle"
            if(self.key_states[11]):
                self.gun = self.inventory['handgun']
                self.reloading = False
            if(self.key_states[12]):
                self.gun = self.inventory['shotgun']
                self.reloading = False
            if(self.key_states[13]):
                self.gun = self.inventory['rifle']
                self.reloading = False
            if(self.key_states[41]):
                self.gun = self.inventory['flashlight']
                self.reloading = False
                self.animation = "idle"
            if(self.key_states[27]):
                self.reloading = True
                self.reload_begin = pygame.time.get_ticks()
                pygame.mixer.Channel(1).play(self.sound['reload'])

    def handleKeyUp(self, event):
        if self.life>0:
            self.key_states[event.scancode] = 0

    def handleMouseDown(self, event):
        if self.life>0:
            if(event.button == 1):
                self.shooting = True
                if self.gun.name in ['rifle', 'shotgun', 'handgun'] and self.gun.bullets > 0:
                    self.gun.bullets -=1
                self.last_shoot = pygame.time.get_ticks()
            if(event.button == 3):
                self.attacking = True

    def handleMouseUp(self, event):
        if self.life>0:
            if(event.button == 1):
                self.shooting = False
            if(event.button == 3):
                self.attacking = False

    def handleMouseMove(self, event):
        if self.life>0:
            x = event.pos[0]-400
            y = event.pos[1]-300
            self.angle = -math.atan2(x, y)/3.1415*180.0 - 90;