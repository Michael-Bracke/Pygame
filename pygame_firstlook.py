import pygame
import pickle
from os import path

from pygame import image
from pygame.event import pump
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000


screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')

#define game variables
tile_size = 50
game_over = 0
main_menu = True
level = 0
max_levels = 7

#load images
sun_img = pygame.image.load('img/sun.png')
bg_img = pygame.image.load('img/sky.png')
restart_image = pygame.image.load('img/restart_btn.png')
start_image = pygame.image.load('img/start_btn.png')
exit_image = pygame.image.load('img/exit_btn.png')

#functies

def reset_level(level):
    player.reset(100,screen_height - 130)
    sprite_group.empty()
    exit_group.empty()
    #het inladen van de data (dynamisch)
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
        world = World(world_data)
    return world

# Class definen
## ___init___ => is de constructur v/d classe
# door self.xxx te gebruiker en toe te wijzen wordt er automatisch ook een variabele aangemaakt
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False
    def draw(self):
        action = False
        #krijg muis positie
        pos = pygame.mouse.get_pos()

        #check muispunt collsion
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False: #linker muisknop INGEDRUKT
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0: #linker muisknop LOSGELATEN
            self.clicked = False

        #de button zelf plaatsen
        screen.blit(self.image, self.rect)
        return action

class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over, level):
        walk_cooldown = 7
        dx = 0
        dy = 0
        if game_over == 0:
            

            #reageer op de key presses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] == True and self.jumped == False and self.is_on_platform == False: 
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT] == True : 
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT] == True : 
                dx += 5
                self.counter += 1
                self.direction = 1
            #counter reset
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.image_index = 0
                if self.direction == 1:         
                    self.image = self.images_right[self.image_index]
                if self.direction == -1:   
                    self.image = self.images_left[self.image_index]
            #de animatie 
            
            if self.counter > walk_cooldown:
                self.counter = 0
                self.image_index += 1
                if self.image_index >= len(self.images_right):
                    self.image_index = 0  
                if self.direction == 1:         
                    self.image = self.images_right[self.image_index]
                if self.direction == -1:   
                    self.image = self.images_left[self.image_index]

            #voeg zwaartekracht toe
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            #bereken nieuwe positie
    
            #kijk of hij ergens tegen zou botsen (indien niet, ga verder, anders beweeg je niet.)
            self.is_on_platform = True 


            #update de player zijn coordinaten indien verder gaan
            for tile in world.tile_list:
                #controleer y direction
                #door gebruik te maken van dx en dy, creer je eerst eigenlijk een 'temp' rectangle
                #check for collision in x direction
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                #als deze temp rectangle een botsing maakt, mag je dus niet verder
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #controleer of onder de grond (jumping)
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    #controleer of boven de grond (falling)
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.is_on_platform = False

            #controle voor botsting met enemies
            if pygame.sprite.spritecollide(self, sprite_group, False):
                game_over = -1 #DEAD

            #controle voor het deurtje naar volgende level
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1 #NEXT LEVEL


            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
                self.image = self.dead_image
                if self.rect.y > 200:
                    self.rect.y -= 5

        #teken de effectieve player op het scherm
        screen.blit(self.image, self.rect)
        return game_over
    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.image_index = 0
        self.counter = 0
        
        for num in range(1,5):
            img_right = pygame.image.load(f'img/guy{num}.png')
            img_right  = pygame.transform.scale(img_right, (40,80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)

        self.image = self.images_right[self.image_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.dead_image = pygame.image.load('img/ghost.png')
        self.is_on_platform = True

class Enemy(pygame.sprite.Sprite):
    def __init__(self,x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/blob.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1 
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter = 0

class Exit(pygame.sprite.Sprite):
     def __init__(self,x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/exit.png')
        self.image = pygame.transform.scale(img, (tile_size,tile_size * 1.5))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y 

class Lava(pygame.sprite.Sprite):
     def __init__(self,x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/lava.png')
        self.image = pygame.transform.scale(img, (tile_size,tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class World():
    def __init__(self, data): 
        self.tile_list = []

        #load images
        dirt_img = pygame.image.load('img/dirt.png')
        grass_img = pygame.image.load('img/grass.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    sprite_group.add(blob)
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + 25)
                    sprite_group.add(lava)
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - 20)
                    exit_group.add(exit)

                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            pygame.draw.rect(screen, (255,255,255), tile[1], 2)

player = Player(100, screen_height - 130)
sprite_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()



restart_button = Button(screen_width // 2 - 50, screen_height // 2 - 15, restart_image)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_image)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_image)
#import database connection file (objecten etc)
import sqlconnection

sqlconnection.printScoreboard()

world = reset_level(level)


    
run = True
while run:
    clock.tick(fps)

    screen.blit(bg_img, (0, 0))
    screen.blit(sun_img, (100, 100))
    if main_menu == True:
      if start_button.draw():
          main_menu = False     
      if exit_button.draw():
          run = False
    else:
        world.draw()
        if game_over == 0:
            sprite_group.update()

        sprite_group.draw(screen)
        exit_group.draw(screen)

        game_over = player.update(game_over, level)

        if game_over == -1:
            if restart_button.draw(): #tekent EN return de actie van de button (clicked of niet)
                world_data = []
                world = reset_level(level)
                game_over = 0

        if game_over == 1:       
            level += 1
            if level <= max_levels:
                #reset het level
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                #einde van het spel, boven level 7
                #toon restart button
                if restart_button.draw(): #tekent EN return de actie van de button (clicked of niet)
                    level = 0
                    world_data = []
                    world = reset_level(level)
                    game_over = 0





    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()