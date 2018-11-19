#===============================================================================================
# Credits: Cassiano Franco and Jhonatan Oliveira
#==============================================================================================
# Topdown Shooter is a version 2 of a OpenGl game builded for academic purposes
# The first version was being implemented on C++ 
# until developers realize that life is too short for it

# The game have a topdown 2D view, the camera follows the player 
# The player can be controled by A,S,D,W keys and run when Shift is pressed
# To aim use mouse pointer
# To shoot press Left Mouse Button
# To meleeattack press Right Mouse Button
# The Mobs are zombies that follows the player on sight or radomly moves
# The guns are changed pressing 1, 2, 3, 4 or F
# The knife is a powerful melee weapon : can be selected on key 1
# The handgun is a fast reloading gun  : can be selected on key 2
# The shotgun is a kickass zombie gun  : can be selected on key 3
# The rifle is a destroyer machinegun  : can be selected on key 4
# The flashlight is just a flashligh   : can be selected on key F
# The map have boxes that colides with the player and zombies(use them wisely)

# Things implemented:
# Texture loads from png
# Animation frames
# Several colision including playerOnSight, boxColision, takeHit and on_player_sight 
# Keyboard and Mouse controls

import pygame, sys, os
import pprint
import importlib

from random import randint
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from GameObject import GameObject 
from Player import Player 
from Zombie import Zombie  
from Gun import Gun  
from HUD import HUD  


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
    window_size = width, height = (1000, 768)
    pygame.init()
    screen = pygame.display.set_mode(window_size, OPENGLBLIT | DOUBLEBUF)
    glEnable(GL_TEXTURE_2D)
    glMatrixMode(GL_PROJECTION)
    glOrtho(60, width, height, 1, -60, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glClearColor(0,0,0,1);
    glBlitFramebuffer(0, 0, width, height, 0, 0, width, height, GL_COLOR_BUFFER_BIT, GL_NEAREST);
    return screen

if __name__ == "__main__":
    screen = initDisplay()
    textures = loadTextures()

    #                Gun(name,         damage,rate,reload_time,cap,bullets,accuracy,price,available)
    flashlight =     Gun("flashlight", 10,    1,   0,          1,  1,      180,     0,     True, 5)
    knife =          Gun("knife",      34,    1,   0,          1,  1,      180,     0,     True, 5)
    handgun =        Gun("handgun",    25,    3,   2,          8,  8,      10,      100,   False, 5)
    shotgun =        Gun("shotgun",    50,    1,   6,          2,  2,      20,      1000,  False, 40)
    rifle =          Gun("rifle",      50,    9,   3,          20, 9999,     5,       10000, False, 5)
    inventory = {
        'flashlight': flashlight,
        'knife': knife,
        'handgun': handgun,
        'shotgun': shotgun,
        'rifle': rifle
    }

                # Zombie(height, width, textures, x, y,   angle, life, speed)
    zombies = [Zombie(100,    100,   textures, 0, randint(200,5000), randint(200,5000), 1000, 2.5) for i in range(50)]
    zombies += [Zombie(100,    100,   textures, 0, randint(200,5000), -randint(200,5000), 1000, 2.5) for i in range(50)]
    zombies += [Zombie(100,    100,   textures, 0, -randint(200,5000), -randint(200,5000), 1000, 2.5) for i in range(50)]
    zombies += [Zombie(100,    100,   textures, 0, -randint(200,5000), randint(200,5000), 1000, 2.5) for i in range(50)]

    floor =   GameObject(100000, 100000, textures['the_floor']['the_floor'][2], 0,  0,   0)

    boxes = [ GameObject(200, 200, textures['the_floor']['the_floor'][1], randint(200,5000), randint(200,5000), randint(0, 360)) for i in range(100)]
    boxes += [ GameObject(200, 200, textures['the_floor']['the_floor'][1], randint(200,5000), -randint(200,5000), randint(0, 360)) for i in range(100)]
    boxes += [ GameObject(200, 200, textures['the_floor']['the_floor'][1], -randint(200,5000), -randint(200,5000), randint(0, 360)) for i in range(100)]
    boxes += [ GameObject(200, 200, textures['the_floor']['the_floor'][1], -randint(200,5000), randint(200,5000), randint(0, 360)) for i in range(100)]

    GameObject(200, 200, textures['the_floor']['the_floor'][1], 300, 300, 45)

    pygame.mixer.init(frequency = 44100, size = -16, channels = 1, buffer = 2**12) 
    sound = {}
    sound['shot'] = pygame.mixer.Sound('./sounds/shotgun_shot.wav')
    sound['reload'] = pygame.mixer.Sound('./sounds/shotgun_reload.wav')
    sound['pump'] = pygame.mixer.Sound('./sounds/shotgun_pump.wav')
    
    pygame.mixer.music.load('./theme.mp3')
    pygame.mixer.music.play()
    player =      Player(100, 100, textures, 0,  0, 0, inventory, 5, sound)
    hud = HUD(player)
    while True:
        [hundleEvent(event, player) for event in pygame.event.get()]
        clock = pygame.time.get_ticks() / 50
        glLoadIdentity()
        glClear(GL_COLOR_BUFFER_BIT)
        glTranslatef(1000/2-player.x,768/2-player.y,50)
        if(player.shooting and player.shootTiming()):
            glTranslatef(3,3,0)

        floor.render_floor()
        player.render(clock)
        player.update(boxes)
        for box in boxes:
            box.render()
        for zombie in zombies:
            zombie.render(clock, player)
            zombie.update(player, boxes)
        hud.render(screen)
        pygame.display.flip()