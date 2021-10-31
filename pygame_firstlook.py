import pygame_textinput
import pygame
import pickle
import csv  

from os import path

from pygame import image
from pygame import draw
from pygame.event import pump
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000
score = 0

total_time = 0
elapsed_time = 0

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')

#define fonts
font_score = pygame.font.SysFont('Bauhaus 93', 30)
font = pygame.font.SysFont('Bauhaus 93', 70)
font_download = pygame.font.SysFont('Bauhaus 93', 25)

#define colours
white = (255, 255, 255)
blue = (0, 0, 255)
black = (0,0,0)
#define game variables
tile_size = 50
game_over = 0
main_menu = True
Login_menu = True
level = 0
max_levels = 7
user_id = 0
score_updated = False



#load images
sun_img = pygame.image.load('img/sun.png')
bg_img = pygame.image.load('img/sky.png')
restart_image = pygame.image.load('img/restart_btn.png')
start_image = pygame.image.load('img/start_btn.png')
exit_image = pygame.image.load('img/exit_btn.png')
download_image = pygame.image.load('img/download_btn.png')

#functies


def draw_leaderboard_csv():
    header = ['Name', 'Score', 'Time Elapsed']
    data = sqlconnection.GetLeaderboard()
    with open('countries.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        # write the header
        writer.writerow(header)
        # write the data
        writer.writerow(data)

def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img,(x, y))

def draw_leaderbord():
    leaderboard_y_value = 0
    data = sqlconnection.GetLeaderboard()
    draw_text("Leaderbord (Top 5): ", font, blue, (screen_width // 2) - 300, (screen_height // 2) - 450)
    for value in data:
        time = (value[0] + " | Score: " + str(value[1]) + " - "  + str(value[2]))      
        leaderboard_y_value += 50
        draw_text(time, font_score, blue, (screen_width // 2) - 250 , ((screen_height // 2) - 400) +  leaderboard_y_value)

def reset_level(level):
    player.reset(100,screen_height - 130)
    sprite_group.empty()
    exit_group.empty()
    coin_group.empty()
    #het inladen van de data (dynamisch)
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
        world = World(world_data)
    return world



# Class definen
## ___init___ => is de constructur v/d classe
# door self.xxx te gebruiker en toe te wijzen wordt er automatisch ook een variabele aangemaakt


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/platform.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y


    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


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

class TextBox():
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
        self.last_game_ended = 0
        self.reset(x, y)

    def update(self, game_over, level):
        walk_cooldown = 7
        dx = 0
        dy = 0
        col_thresh = 20
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

            #check for collision with platforms
            for platform in platform_group:
                #collision in the x direction
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                #collision in the y direction
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #check if below platform
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    #check if above platform
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.is_on_platform = False
                        dy = 0
                    #move sideways with the platform
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
                #toon gameover wanneer player dood is
                draw_text('GAME OVER!', font, blue, (screen_width // 2) - 185, (screen_height // 2) + 50)
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

class Coin(pygame.sprite.Sprite):
     def __init__(self,x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/coin.png')
        self.image = pygame.transform.scale(img, (tile_size,tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

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
                if tile == 4:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 5:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + 25)
                    sprite_group.add(lava)
                if tile == 7:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
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
coin_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()

restart_button = Button(screen_width // 2 - 50, screen_height // 2 - 15, restart_image)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_image)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_image)
login_entered_button = Button(screen_width // 2 - 150, screen_height // 2 + 150, start_image)
download_csv_button = Button(screen_width // 2 + 100, screen_height // 2 + 150, pygame.transform.scale(download_image, (40,40)))
# Create TextInput-object
textinput = pygame_textinput.TextInputVisualizer()


#import database connection file (objecten etc)
import sqlconnection


world = reset_level(level)


    
run = True
while run:


    clock.tick(fps)
    screen.blit(bg_img, (0, 0))
    screen.blit(sun_img, (100, 100))
    if main_menu == True:
      draw_leaderbord()
      if start_button.draw():
          main_menu = False     
      if exit_button.draw():
          run = False
    else:
        if Login_menu == True:      
            draw_text('Naam speler: ', font, blue, (screen_width // 2) - 215 , (screen_height // 2) - 200)    
            # toon de textinput op het scherm
            screen.blit(textinput.surface, ((screen_height // 2) - 75, (screen_height // 2)))
            if login_entered_button.draw() or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                user_id = sqlconnection.CreateUser(textinput.value)
                Login_menu = False
        else:
            world.draw()
            if game_over == 0:
                platform_group.update()
                sprite_group.update()
                #score counter          
                if pygame.sprite.spritecollide(player, coin_group, True):
                    score += 1
                draw_text('X ' + str(score), font_score, white, tile_size - 10, 10)

            sprite_group.draw(screen)
            exit_group.draw(screen)
            coin_group.draw(screen)
            platform_group.draw(screen)

            game_over = player.update(game_over, level)

            if game_over == -1:
                draw_text('SCORE: ' + str(score), font, blue, (screen_width // 2) - 150 , (screen_height // 2) - 100)    
                if score_updated == False:
                    
                    #bereken de tijd dat de speler gespeeld heeft dit level
                    now = pygame.time.get_ticks()
                    time_elapsed = now - player.last_game_ended
                    player.last_game_ended = now
                    sqlconnection.UpdateScoreboard(user_id, score, time_elapsed)
                    score_updated = True
                draw_leaderbord()
                draw_text('download leaderboard', font_download, black, (screen_width // 2) - 150 , (screen_height // 2) + 150)
                if download_csv_button.draw():
                        draw_leaderboard_csv()
                if restart_button.draw(): #tekent EN return de actie van de button (clicked of niet)
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0
                    score_updated = False

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
                    draw_text('YOU WIN!', font, blue, (screen_width // 2) - 140, screen_height // 2)
                    if score_updated == False:
                        #bereken de tijd dat de speler gespeeld heeft dit level
                        now = pygame.time.get_ticks()
                        time_elapsed = now - player.last_game_ended
                        player.last_game_ended = now
                        sqlconnection.UpdateScoreboard(user_id, score, time_elapsed)
                        score_updated = True
                    if restart_button.draw(): #tekent EN return de actie van de button (clicked of niet)
                        level = 0
                        world_data = []
                        world = reset_level(level)
                        game_over = 0
                        score_updated == False
                        score = 0




    events = pygame.event.get()
    # Feed it with events every frame
    textinput.update(events)
    for event in events:
        
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()