import pygame, sys, os
import pprint
import importlib
import math
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


class HUD:
    def __init__(self, player):
        self.font = pygame.font.SysFont('./boston_traffic.ttf', 10)
        self.player = player 

    def render(self, screen):
        ammo = str(self.player.gun.bullets)
        textsurface = self.font.render(ammo, True, (1, 1, 1))
        screen.blit(textsurface,(0,0))
