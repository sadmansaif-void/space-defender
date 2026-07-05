#Pre-req
import pygame
import time
import os
import random
pygame.init()
pygame.font.init()

#Set up the window, background, font, sound and caption
FPS = 60
WIDTH , HEIGHT = 650 , 650
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
FONT = pygame.font.SysFont("comicsans",30)
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH,HEIGHT))
pygame.display.set_caption("Space Defender")

#Event management

LIFE_GONE = pygame.USEREVENT + 1 
HIGH_SCORE = pygame.USEREVENT + 2

#Set player attributes
PLAYER_WIDTH , PLAYER_HEIGHT = 50, 50
PLAYER_IMAGE = pygame.transform.scale(pygame.image.load(os.path.join("assets" , "pixel_ship_yellow.png")), (PLAYER_WIDTH, PLAYER_HEIGHT))
PLAYER_LIFE_IMAGE = pygame.transform.scale(pygame.image.load(os.path.join("assets" , "pixel_ship_red_small.png")), (18, 18))
PLAYER_SPAWN_X , PLAYER_SPAWN_Y = WIDTH/2 - PLAYER_IMAGE.get_width()/2 , HEIGHT - PLAYER_IMAGE.get_height() - 13 #Health bar height +5
PLAYER_VEL = 8
PLAYER_BULLET_VEL = 16
PLAYER_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets" , "pixel_laser_yellow.png")), (50,50))


#Enemy attributes
ENEMY_WIDTH , ENEMY_HEIGHT = 40,40
ENEMY_VEL = 3
ENEMY_BULLET_VEL = 14
ENEMY_LIST = ["red", "green", "blue"] 
RED_ENEMY = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png")), (ENEMY_WIDTH,ENEMY_HEIGHT)), 180) 
BLUE_ENEMY = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png")), (ENEMY_WIDTH,ENEMY_HEIGHT)), 180)
GREEN_ENEMY = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png")), (ENEMY_WIDTH,ENEMY_HEIGHT)), 180)
RED_ENEMY_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets" , "pixel_laser_red.png")), (40,40))
BLUE_ENEMY_LASER = ENEMY_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets" , "pixel_laser_blue.png")), (40,40))
GREEN_ENEMY_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets" , "pixel_laser_green.png")), (40,40))


class Laser:
    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def move(self , vel):
        self.y += vel

    def draw(self,window):
        window.blit(self.img, (self.x, self.y))

    def offscreen(self):
        return self.y + self.img.get_height() <= 0 or self.y >= HEIGHT

    def collision(self,obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 9
    def __init__(self, x, y, health = 100):
        self.x = x
        self.y =y
        self.health = health
        self.ship_img = None
        self.laser = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter =0
        elif self.cool_down_counter>0:
            self.cool_down_counter +=1       


    def shoot(self):
        if self.cool_down_counter == 0:
            self.lasers.append(Laser(self.x, self.y, self.laser))
            self.cool_down_counter = 1


    def move_laser(self, vel,obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.offscreen():
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -=10
                self.lasers.remove(laser)    


                
    def width(self):
        return self.ship_img.get_width()    

    def height(self):
        return self.ship_img.get_height()

class Player(Ship):
    score = 0
    def __init__(self, x, y, health =100):
        super().__init__(x , y,health)
        self.ship_img = PLAYER_IMAGE
        self.laser = PLAYER_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health


    def move_laser(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.offscreen():
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        Player.score +=20
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def healthbar(self, window):
        pygame.draw.rect(window, "red",(self.x,self.y+ self.height() + 5, self.width(),8))
        pygame.draw.rect(window, "green",(self.x,self.y+ self.height() + 5, self.health*self.width()/100,8))                    
                       

class Enemy(Ship):
    COLOR_MAP = {
        "red" : (RED_ENEMY,RED_ENEMY_LASER),
        "blue" : (BLUE_ENEMY,BLUE_ENEMY_LASER),
        "green" : (GREEN_ENEMY,GREEN_ENEMY_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self):
        self.y += ENEMY_VEL
        if random.randint(0, 2*FPS) == 1 and self.x + self.width() + 7*ENEMY_VEL <=WIDTH:
            self.x += 7*ENEMY_VEL
        if random.randint(0, 2*FPS) == 8 and self.x - 7*ENEMY_VEL>=0:
            self.x -= 7*ENEMY_VEL    

            


def main():
    high_score = 0
    with open("SCORE.txt" , "r") as file:
        line = file.readline()
        if line.strip():
            high_score = int(line.rstrip())        
    run = True
    levels = 0
    lives = 5
    enemies = []
    wave_length = 5
    
    clock = pygame.time.Clock()

    player_ship = Player(PLAYER_SPAWN_X , PLAYER_SPAWN_Y)
    
    def re_draw():
        score_text = FONT.render(f"SCORE : {Player.score}",1,"white")
        high_score_text = FONT.render(f"HIGH SCORE : {high_score}",1,"white")
        level_text = FONT.render(f"LEVEL : {levels}", 1, "white")
        WIN.blit(BG,(0,0))
        for enemy in enemies:
            enemy.draw(WIN)   
        player_ship.draw(WIN)
        player_ship.healthbar(WIN)
        for life in range(lives):
            WIN.blit(PLAYER_LIFE_IMAGE, (life*18 , level_text.get_height()))
        WIN.blit(level_text, (0,0))
        WIN.blit(score_text, (WIDTH-score_text.get_width(),0))
        WIN.blit(high_score_text, (WIDTH-high_score_text.get_width(),score_text.get_height() +2 ))        
        pygame.display.update()


    while run:
        clock.tick(FPS)
        if len(enemies) == 0:
            levels += 1
            wave_length += 5
            for i in range(wave_length):
                spawn_x, spawn_y= (random.randrange(ENEMY_WIDTH,WIDTH- 2*ENEMY_WIDTH, ENEMY_WIDTH),random.randrange(-levels*HEIGHT,-ENEMY_HEIGHT,ENEMY_HEIGHT))
                color = random.choice(ENEMY_LIST)
                enemies.append(Enemy(spawn_x,spawn_y, color))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == LIFE_GONE:
                lives -=1            


        keys = pygame.key.get_pressed()
               
        player_movement(keys, player_ship)
        player_ship.move_laser(-PLAYER_BULLET_VEL, enemies)
        handle_enemy(enemies, player_ship)    


        re_draw()

        if lives <=0 or player_ship.health<=0:
            loosing_text = FONT.render(f"GAME OVER", 1, "red")
            WIN.blit(loosing_text, (WIDTH/2 - loosing_text.get_width()/2, HEIGHT/2 - loosing_text.get_height()/2))
            if Player.score >= high_score:
                high_score_label = FONT.render(f"NEW HIGH SCORE",1,"yellow")
                WIN.blit(high_score_label, (WIDTH/2 - high_score_label.get_width()/2,HEIGHT/2 +loosing_text.get_height() - high_score_label.get_height()/2))
            pygame.display.update()
            pygame.time.delay(5000)
            run = False
    if Player.score >= high_score:
        with open("SCORE.txt", "w") as file:
            line = file.write(str(Player.score))                      
    pygame.quit()        




def player_movement(keys, player_ship):

    if keys[pygame.K_LEFT] and player_ship.x - PLAYER_VEL >= 0:
        player_ship.x -= PLAYER_VEL
    if keys[pygame.K_RIGHT] and player_ship.x+ player_ship.width() + PLAYER_VEL <=WIDTH :
        player_ship.x += PLAYER_VEL
    if keys[pygame.K_DOWN] and player_ship.y+ player_ship.height() + 13  + PLAYER_VEL <=HEIGHT :
        player_ship.y += PLAYER_VEL
    if keys[pygame.K_UP] and player_ship.y + PLAYER_VEL >= 2*HEIGHT/3 :
        player_ship.y -= PLAYER_VEL
    if keys[pygame.K_SPACE]:
        player_ship.shoot()                   

def handle_enemy(enemies,player):
    for enemy in enemies [:]:
        enemy.move()
        enemy.move_laser(ENEMY_BULLET_VEL, player)
        if random.randrange(0, 3*FPS) ==1:
            enemy.shoot()

        if collide(enemy, player):
            player.health -=10
            enemies.remove(enemy)
            Player.score +=10    

        elif enemy.y >= HEIGHT:
            pygame.event.post(pygame.event.Event(LIFE_GONE))
            enemies.remove(enemy)
            


def collide(obj1, obj2):
    offset_x = obj2.x -obj1.x
    offset_y = obj2.y -obj1.y
    return obj1.mask.overlap(obj2.mask , (offset_x,offset_y)) != None 

    


if __name__ == "__main__":
    main()