import pygame, sys, os
import pprint
import importlib
import math
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from random import randint


class Zombie:
    def __init__(self, height, width, textures, x, y, angle, life, speed):
        self.textures = textures
        self.height = height
        self.width = width
        self.x = x
        self.y = y
        self.angle = angle
        self.running = False
        self.move = False
        self.animation = 'idle'
        self.taking_hit = False
        self.life = life
        self.died = False
        self.action = False
        self.speed = speed
        self.move = False
        self.action_begin = 0
        self.action_time = 0
        self.max_life = life


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

    def update(self, player, boxes):
        if not self.died:
            if(self.life < 0):
                player.score += self.max_life / 20
                self.died = True

            if (pygame.time.get_ticks()-self.action_begin)/1000 > self.action_time:
                self.getRandomAction()

            if self.playerOnSight(player):
                self.action = "follow"
                self.action_time = 10


            dx = self.x - player.x
            dy = self.y - player.y
            player_distance = (dx**2 + dy**2)**0.5
            angle_to_zombie = (int(player.angle + math.atan2(dx, dy)/3.1415*180.0) % 360) - 270
            on_player_sight = (angle_to_zombie < +player.gun.accuracy+5 and angle_to_zombie > -player.gun.accuracy) or (angle_to_zombie > -45 and angle_to_zombie < +45 and player_distance < 200)
            if (on_player_sight and player.shootTiming()):
                self.x = self.x - player.gun.knockback*math.cos((self.angle-185) * 3.1415 / 180);
                self.y = self.y - player.gun.knockback*math.sin((self.angle-185) * 3.1415 / 180);
                self.life -= player.gun.damage
                self.taking_hit = True
                self.action = "follow"
            else:
                self.taking_hit = False
            
            if self.action == "follow":
                self.running = True
                self.move = True
                dx = player.x - self.x
                dy = player.y - self.y
                angle_to_player = -(int(math.atan2(dx, dy)/3.1415*180.0) % 360)+90
                self.angle = angle_to_player-180

            if self.move:
                speed = self.speed
                if self.running:
                    speed = speed*2
                x_ahead = -speed*math.cos(self.angle*3.1415/180)
                y_ahead = -speed*math.sin(self.angle*3.1415/180)
                if(player_distance>30 and not self.boxColision(boxes, x_ahead, y_ahead)):
                    self.x += x_ahead
                    self.y += y_ahead

            if self.action == "move":
                self.move = True
                self.animation = "move"

            if self.action =="idle":
                self.move = False
                self.animation = "idle"

            if player_distance < 31:
                self.animation = "attack"
                player.takeHit()
            else:
                self.animation = "move"


            if self.action == "turn_rigth":
                self.angle += 1

            if self.action == "turn_left":
                self.angle -= 1


    def getRandomAction(self):
        actions = ["move", "turn_rigth", "turn_left", "idle"]
        self.action = actions[randint(0,3)]
        self.action_begin = pygame.time.get_ticks()
        self.action_time = 3
        self.running = False 

    def playerOnSight(self, player):
        dx = player.x - self.x;
        dy = player.y - self.y;
        distance = (dy**2 + dx**2)**0.5
        angle_to_player = (self.angle + math.atan2(dx, dy)/3.1415*180.0 + 90) % 360
        cond = (angle_to_player < 45 or angle_to_player > 315) and distance < 500
        return cond


    def render(self, clock, player):
        rand_angle = 0
        if not self.died:
            rand_angle = randint(0, 360)
            animation = self.textures['zombie'][self.animation]
            glPushMatrix()
            glTranslatef(self.x, self.y, 0)
            glRotatef(self.angle,0,0,1)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);
            glEnable(GL_BLEND);
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);


            # Ajuste no tamanho das texturas
            gambiarra = 0
            if self.animation == "attack":
                gambiarra = 30
            if self.animation == "move":
                gambiarra = 30

            glBindTexture(GL_TEXTURE_2D, animation[clock % len(animation)])
            glBegin(GL_QUADS)
            glTexCoord(0, 0)
            glVertex( (self.width+gambiarra)/2.,  (self.height+gambiarra)/2., 0)
            glTexCoord(0, 1)
            glVertex( (self.width+gambiarra)/2., -(self.height+gambiarra)/2., 0)
            glTexCoord(1, 1)
            glVertex(-(self.width+gambiarra)/2., -(self.height+gambiarra)/2., 0)
            glTexCoord(1, 0)
            glVertex(-(self.width+gambiarra)/2.,  (self.height+gambiarra)/2., 0)
            glEnd()
            glBindTexture(GL_TEXTURE_2D, 0)
            glPopMatrix()
        
        if self.taking_hit or self.died:
            glPushMatrix()
            glTranslatef(self.x, self.y, 0)
            glRotatef(rand_angle,0,0,1)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);
            glEnable(GL_BLEND);
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
            glBindTexture(GL_TEXTURE_2D, self.textures['the_floor']['the_floor'][0])
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