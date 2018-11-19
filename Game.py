#====================================================================================#
# Credits: Cassiano Franco and Jhonatan Oliveira                                     #
#====================================================================================#
# Topdown Shooter is a version 2 of a OpenGl game builded for academic purposes      #
# The first version was being implemented on C++                                     #
# until developers realize that life is too short for it                             #
#====================================================================================#
# The game have a topdown 2D view, the camera follows the player                     #
# The player can be controled by A,S,D,W keys and run when Shift is pressed          #
# To aim use mouse pointer                                                           #
# To shoot press Left Mouse Button                                                   #
# To meleeattack press Right Mouse Button                                            #
# The Mobs are zombies that follows the player on sight or radomly moves             #
# The guns are changed pressing 1, 2, 3, 4 or F                                      #
# The knife is a powerful melee weapon : can be selected on key 1                    #
# The handgun is a fast reloading gun  : can be selected on key 2                    #
# The shotgun is a kickass zombie gun  : can be selected on key 3                    #
# The rifle is a destroyer machinegun  : can be selected on key 4                    #
# The flashlight is just a flashligh   : can be selected on key F                    #
# The map have boxes that colides with the player and zombies(use them wisely)       #
#====================================================================================#
# Things implemented:                                                                #
# Texture loads from png                                                             #
# Animation frames                                                                   #
# Several colision including playerOnSight, boxColision, takeHit and on_player_sight #
# Keyboard and Mouse controls                                                        #
# Time Handle                                                                        #
# Sounds                                                                             #
# HUD                                                                                #
# Rank Score                                                                         #
#====================================================================================#

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
menu = False

def ap(s):
    pp.pprint(s)

def updateGame():
    pass

def load_texture(texture_url):
    tex_id = glGenTextures(1)                        # generate unique texture id
    tex = pygame.image.load(texture_url)             # load png file 
    tex_surface = pygame.image.tostring(tex, 'RGBA') # serialize imgae
    tex_width, tex_height = tex.get_size()           # get texture size
    glBindTexture(GL_TEXTURE_2D, tex_id)             # bind an id to texture
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR) # Texture params for visuzalization
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR) # Texture params for visuzalization
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)         # Texture params for visuzalization
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)          # Texture params for visuzalization
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tex_width, tex_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_surface) # load serialized image to opengl
    glBindTexture(GL_TEXTURE_2D, 0) # reset texture binding
    return tex_id

def loadTextures():
    textures = {}
    # iterate through texure folders and load texture files
    for p in os.listdir("./textures/"):
        textures[p] = {}
        for pp in os.listdir("./textures/" + p):
            textures[p][pp] = list(range(len(os.listdir("./textures/" + p + "/" + pp))))
            for ppp in os.listdir("./textures/" + p + "/" + pp):
                textures[p][pp][int(ppp[-6:-4].replace("_", ""))] = load_texture("./textures/" + p + "/" + pp + "/" + ppp)
    return textures


# destinate events for respective player functions
def handleEvent(event, player, player_name, sound):
    if event.type == pygame.MOUSEBUTTONDOWN:
        player.handleMouseDown(event)
    if event.type == pygame.MOUSEBUTTONUP:
        player.handleMouseUp(event)
    if event.type == pygame.MOUSEMOTION:
        player.handleMouseMove(event)
    if event.type == pygame.KEYDOWN:
        print(event)
        if event.key == 27:
            menu = True;
        if player.life < 0:
            if event.key != 304:
                if event.key == 13:
                    print("ESCREVEU")
                    file = open('scores', 'w')
                    file.write(player_name.text + "-" + str(player.score))
                    file.close
                    print("ESCREVEU")
                if event.key == 8 and player_name.text != "":
                    pygame.mixer.Channel(0).play(sound['pump'])
                    name = player_name.text[:-1]
                elif event.key <= 128:
                    pygame.mixer.Channel(0).play(sound['shot'])
                    name = player_name.text + str(unichr(event.key))
                player_name.setText(name)
        player.handleKeyDown(event)
    if event.type == pygame.KEYUP:
        player.handleKeyUp(event)
    if event.type == pygame.QUIT:
        pygame.quit()
        quit()

def initDisplay():
    window_size = width, height = (1000, 768)                             # size of pygamge window
    pygame.init()                                                         # initialize pygame
    screen = pygame.display.set_mode(window_size, OPENGLBLIT | DOUBLEBUF) # initialize pygame window and set display mode
    glEnable(GL_TEXTURE_2D)                                               # Enable Texture 2D
    glMatrixMode(GL_PROJECTION)                                           # Set Matrix mode for projection
    glOrtho(60, width, height, 1, -60, 1)                                 # Set perspective close to isometric
    glMatrixMode(GL_MODELVIEW)                                            # Set Matrix mode for model view
    glLoadIdentity()                                                      # Reset Matrix
    glClearColor(0,0,0,1);                                                # Set default color
    return screen                                                         # return pygame screen

def loadSounds():
    sound = {}
    sound['shot'] = pygame.mixer.Sound('./sounds/shotgun_shot.wav')
    sound['reload'] = pygame.mixer.Sound('./sounds/shotgun_reload.wav')
    sound['pump'] = pygame.mixer.Sound('./sounds/shotgun_pump.wav')
    pygame.mixer.music.load('./theme.mp3')
    pygame.mixer.music.play() # Play theme soundtrack
    return sound
    

if __name__ == "__main__":
    screen = initDisplay()    # Screen Initialization
    textures = loadTextures() # Texture Load
    pygame.mixer.init(frequency = 44100, size = -16, channels = 1, buffer = 2**12)  # Initilize sound mixer
    pygame.font.init()        # Pygame font initialization
    sound = loadSounds()      # Sound Load

    #=======================#
    # Objects instantiation #
    #=======================#
    
    #                Gun(name,         damage,rate,reload_time,cap,bullets,accuracy,price,available)
    flashlight =     Gun("flashlight", 10,    1,   0,          1,  1,      180,     0,     True,  50)
    knife =          Gun("knife",      34,    1,   0,          1,  1,      180,     0,     True,  50)
    handgun =        Gun("handgun",    25,    3,   2,          8,  8,      10,      100,   False, 20)
    shotgun =        Gun("shotgun",    50,    1,   6,          4,  4,      20,      1000,  False, 100)
    rifle =          Gun("rifle",      20,    9,   4,          25, 25,     5,       10000, False, 20)
    inventory = {
        'flashlight': flashlight,
        'knife': knife,
        'handgun': handgun,
        'shotgun': shotgun,
        'rifle': rifle
    }
    
    #           Zombie(height, width, textures,  x,                  y,                 angle,          life, speed)
    zombies =  [Zombie(100,    100,   textures,  randint(200,2000),  randint(200,2000), randint(0,360), 100,  5.5) for i in range(20)]
    zombies += [Zombie(100,    100,   textures,  randint(200,2000), -randint(200,2000), randint(0,360), 100,  5.5) for i in range(20)]
    zombies += [Zombie(100,    100,   textures, -randint(200,2000), -randint(200,2000), randint(0,360), 100,  5.5) for i in range(20)]
    zombies += [Zombie(100,    100,   textures, -randint(200,2000),  randint(200,2000), randint(0,360), 100,  5.5) for i in range(20)]

    #         GameObject( height, width, texture,                               x,  y,   angle)
    floor =   GameObject(100000, 100000, textures['the_floor']['the_floor'][2], 0,  0,   10)
    #          GameObject(height, width, texture,                                x,                 y,                  angle)
    boxes =  [ GameObject(200,    200,   textures['the_floor']['the_floor'][1],  randint(200,5000),  randint(200,5000), randint(0, 360)) for i in range(100)]
    boxes += [ GameObject(200,    200,   textures['the_floor']['the_floor'][1],  randint(200,5000), -randint(200,5000), randint(0, 360)) for i in range(100)]
    boxes += [ GameObject(200,    200,   textures['the_floor']['the_floor'][1], -randint(200,5000), -randint(200,5000), randint(0, 360)) for i in range(100)]
    boxes += [ GameObject(200,    200,   textures['the_floor']['the_floor'][1], -randint(200,5000),  randint(200,5000), randint(0, 360)) for i in range(100)]

    player = Player(100, 100, textures, 0,  0, 0, inventory, 5, sound) # May be the player

    hud = HUD() # Heads-Up-Display
    player_name = HUD() # Heads-Up-Display
    score = HUD()


    #===========#
    # Main Loop #
    #===========#
    while True:
        [handleEvent(event, player, player_name, sound) for event in pygame.event.get()]
        
        glLoadIdentity()             # Reset Marix
        glClear(GL_COLOR_BUFFER_BIT) # Clear color buffer


        # Check for dead zombies, player life and set HUD content
        dead_zombies = 0
        for zombie in zombies:
            if zombie.died:
                dead_zombies+=1

        if(player.life>0):
            score.setText("SCORE: "+str(player.score))
            hud.setText("ammo: "+ str(player.gun.bullets) + "-"+ str(player.gun.cap)  + "  ---  " + "life: " + str(player.life))
        elif hud.text[0:9] != "GAME OVER":
            hud.setText("GAME OVER")
        if dead_zombies == 80:
            for zombie in zombies:
                zombie.max_life = zombie.max_life*2
                zombie.life = zombie.max_life
                zombie.speed = zombie.speed+1
                zombie.died = False

        clock = pygame.time.get_ticks() / 50             # Set frame lenght for animations
        glTranslatef(1000/2-player.x,768/2-player.y,50)  # Translate camera to player position
        if(player.shooting and player.shootTiming()):    # Screen shake on shoot 
            glTranslatef(3,3,0)

        #=====================#
        # Render game objects #
        #=====================#
        floor.render_floor()
        player.render(clock)
        if(player.life>0):
            player.update(boxes)
        for box in boxes:
            box.render()
        for zombie in zombies:
            zombie.render(clock, player)
            zombie.update(player, boxes)
        hud.render(screen, player.x, player.y)
        if player.life <= 0:
            player_name.render(screen, player.x, player.y-300)
        
        score.render(screen, player.x, player.y-600)
        # Show rendered objects on screen
        pygame.display.flip()
