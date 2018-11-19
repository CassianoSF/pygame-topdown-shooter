import pygame, sys, os
import pprint
import importlib

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from GameObject import GameObject 
from Player import Player 
from Zombie import Zombie 


pp = pprint.PrettyPrinter(indent=4)

def ap(s):
    pp.pprint(s)

def updateGame():
    pass

def load_texture(texture_url):
    tex_id = glGenTextures(1)
    tex = pygame.image.load(texture_url)
    tex_surface = pygame.image.tostring(tex, 'RGBA')
    tex_width, tex_height = tex.get_size()
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0);
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tex_width, tex_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_surface)
    glBindTexture(GL_TEXTURE_2D, 0)
    return tex_id

def loadTextures():
    textures = {}
    for p in os.listdir("./textures/"):
        textures[p] = {}
        for pp in os.listdir("./textures/" + p):
            textures[p][pp] = list(range(len(os.listdir("./textures/" + p + "/" + pp))))
            print(textures[p][pp])
            for ppp in os.listdir("./textures/" + p + "/" + pp):
                print(ppp)
                textures[p][pp][int(ppp[-6:-4].replace("_", ""))] = load_texture("./textures/" + p + "/" + pp + "/" + ppp)
    return textures

def hundleEvent(event, player):
    if event.type == pygame.MOUSEBUTTONDOWN:
        player.hundleMouseDown(event)
    if event.type == pygame.MOUSEBUTTONUP:
        player.hundleMouseUp(event)
    if event.type == pygame.MOUSEMOTION:
        player.hundleMouseMove(event)
    if event.type == pygame.KEYDOWN:
        player.hundleKeyDown(event)
    if event.type == pygame.KEYUP:
        player.hundleKeyUp(event)
    if event.type == pygame.QUIT:
        pygame.quit()
        quit()

def initDisplay():
    window_size = width, height = (1366, 768)
    pygame.init()
    pygame.display.set_mode(window_size, OPENGL | DOUBLEBUF)
    glEnable(GL_TEXTURE_2D)
    glMatrixMode(GL_PROJECTION)
    glOrtho(60, width, height, 1, -60, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glClearColor(0,0,0,1);

if __name__ == "__main__":
    initDisplay()
    textures = loadTextures()
    floor =   GameObject(100000, 100000, textures['the_floor']['the_floor'][2], 0,  0,   0)
    box1 =    GameObject(200,    200,    textures['the_floor']['the_floor'][1], 0,  0,   45)
    player =      Player(100,    100,    textures,                              0,  0,   0)
    zombie =      Zombie(100,    100,    textures,                              0,  100, 100)

    while True:
        [hundleEvent(event, player) for event in pygame.event.get()]
        clock = pygame.time.get_ticks() / 50
        glLoadIdentity()
        glClear(GL_COLOR_BUFFER_BIT)
        glTranslatef(1366/2-player.x,768/2-player.y,50)
        if(player.shooting and clock%2):
            glTranslatef(3,3,0)

        floor.render_floor()
        box1.render()
        player.render(clock)
        player.update()
        zombie.render(clock, player)
        pygame.display.flip()