###Libraries
import pygame
import random
import time
import math
import os
import neat
import json
import pickle

###Constant variables
#Open Files
with open ("config_constant_vars.json", "r") as cfg:
  config = json.load(cfg)
with open ("simulation_constant_vars.json", "r") as cfg:
  sim_config = json.load(cfg)

#screen
BACKROUND = (0, 0, 150) #achtergrond kleur is blauw

#colours
WHITE = (255, 255, 255)
RED = (220, 0, 0)
YELLOW = (255, 190, 0)
GREEN = (0, 220, 0)

#Fonts
pygame.init() #Nodig voor font, anders error
font = pygame.font.SysFont("Arial", 30, True, False)
font2 = pygame.font.SysFont("Arial", 40, True, False)
GAME_OVER = pygame.font.SysFont("Times new Roman", 60, True, False)
SCORE_ARIAL = pygame.font.SysFont("Arial", 20, True, False)

#player
CENTER_X = config["window"]["x"] // 2 #x en y positie midden van scherm
CENTER_Y = config["window"]["y"] // 2 

###Global list and variables
#screen
Fullscreen = False
frames_drawn = 0 #counts frames drawn this second

#time 
Global_cycle_timer = 0.01 #Houd bij hoe lang elke cycle van de main loop duurt
Cycle_time_start = 0 #Houd het begin tijdstip van de cycle bij
Endtime = 0 #tijd in s
current_second = int(time.time()) #Used for draw frames

#Object storage
Bubble_list = list() #Deze list bevat alle objects van class Bubble
Player_list = list() #Bevat object spelers, waarschijnlijk 2

###Functions   
def create_bubble():
  if random.randint(0, int(config["bubble"]["BUB_CHANCE"]/Global_cycle_timer)) == 0: #maakt kans afhankelijk van de verstreken tijd
    if random.randint(0, config["bubble"]["SPEED_POWERUP_CHANCE"]) == 0:
      Bubble_list.append(Bubble(True))  
    else:  
      Bubble_list.append(Bubble(False))

def move_all():
  for i in range(len(Bubble_list)-1, -1, -1): #loops achteruit om errors te voorkomen  
    if Bubble_list[i].x_cord < -config["bubble"]["GAP"]: 
      del Bubble_list[i]
    else:
      Bubble_list[i].move_bubble()

  Player_list[0].move_player()
  Player_list[0].collision_and_score()
  Player_list[1].move_computer(Player_list[0].x_cord, Player_list[0].y_cord, Player_list[0].speed)
  Player_list[1].collision_and_score()

def draw_frame():
  global current_second
  global frames_drawn
  if int(time.time()) != current_second:
    current_second = int(time.time())
    frames_drawn = 0
  
  frac_second = time.time() - current_second #decimalen achter seconden
  if frac_second * config["window"]["FRAMES_PER_SECOND"] > frames_drawn:
    #draw frame
    frames_drawn = frames_drawn + 1
    screen.fill(BACKROUND) #clear het scherm
    
    #draw bubbles
    for i in range(len(Bubble_list)):
      Bubble_list[i].draw_bubble()
    
    #draw player and score
    for i in range(len(Player_list)):
      Player_list[i].draw_player()
      Player_list[i].blit_score()
    
    #draw time
    Game_time = int(Endtime - time.time())
    if Game_time < 5: #Make the number go flashy
      if Game_time % 2 == 1:
        text = font.render(str(Game_time), 1, (255, 255, 255))
        screen.blit(text, (CENTER_X, 10))
      else:
        text = font2.render(str(Game_time), 1, (255, 0, 0))
        screen.blit(text, (CENTER_X, 10)) 
    else: #blit time as standard
      text = font.render(str(Game_time), 1, (255, 255, 255))
      screen.blit(text, (CENTER_X, 10))
  
    pygame.display.flip() #Update pygame window

def sort_player_score():
  #sorteerd objecten op basis van score, hoog --> laag
  Player_list.sort(key=lambda x: x.score, reverse=True)

def screenformat():
  keys = pygame.key.get_pressed()
  if keys[pygame.K_h]:
    global Fullscreen
    if Fullscreen:
      Fullscreen = False
      screen = pygame.display.set_mode((config["window"]["x"], config["window"]["y"])) #Creër het scherm
    else:
      Fullscreen = True
      screen = pygame.display.set_mode(((config["window"]["x"], config["window"]["y"])), pygame.FULLSCREEN) #Creër het scherm
    pygame.time.delay(1)

###Classes    
class Bubble():
  def __init__(self, is_speed_powerup):
    self.x_cord = config["window"]["x"] + config["bubble"]["GAP"] #x cord ligt een stukje buiten scherm
    self.y_cord = random.randint(0, config["window"]["y"]) #y cord is random hoogte in scherm
    self.radius = random.randint(config["bubble"]["MIN_BUB_RADIUS"], config["bubble"]["MAX_BUB_RADIUS"]) #random groote bel
    self.speed = random.randint(config["bubble"]["MIN_BUB_SPEED"],config["bubble"]["MAX_BUB_SPEED"]) #random snelheid
    self.speed_powerup = is_speed_powerup

  def move_bubble(self):
    self.x_cord = self.x_cord - (self.speed * Global_cycle_timer)
    #beweegt bel naar links afhankelijk van de tijd die er is verstreken in vergelijking met de vorige keer dat de bel is bewogen

  def draw_bubble(self):
    if self.speed_powerup:
      pygame.draw.circle(screen, GREEN, (int(self.x_cord),int(self.y_cord)), self.radius, 0)
    else:
      pygame.draw.circle(screen, WHITE, (int(self.x_cord),int(self.y_cord)), self.radius, 1) 

class Player():
  """Deze class wordt gedeeld door Computer en Human_Player, in het programma heeft het verder niet zijn eigen alleenstaande objecten """
  x_cord = CENTER_X
  y_cord = CENTER_Y
  radius = config["player"]["PLAYER_RADIUS"]
  speed = config["player"]["PLAYER_SPEED"]
  score = 0

  def __init__(self, colour, score_x, score_y):
    self.colour = colour
    self.score_x = score_x #x en y cord van de tekst die geblit word 
    self.score_y = score_y

  def draw_player(self):
    pygame.draw.circle(screen, self.colour, (int(self.x_cord), int(self.y_cord)), self.radius, 1) #tekent gekleurde cirkel rond driehoek
    #3 variabelen zijn de punten van de driehoek, links is grofweg 2/3 radius
    top_left = (self.x_cord - (2 * (self.radius)) / 3, self.y_cord - (2 * (self.radius)) / 3)
    bottom_left = (self.x_cord - (2 * (self.radius)) / 3, self.y_cord + (2 * (self.radius)) / 3)
    mid_right = (self.x_cord + self.radius, self.y_cord)
    pygame.draw.polygon(screen, self.colour,(top_left, bottom_left, mid_right))

  def get_score(self, bub):
    return int(bub.radius + int(bub.speed / config["player"]["SPEED_SCORE_MODIFIER"])) 

  def collision_and_score(self):
    for i in range(len(Bubble_list) -1, -1, -1): #loopt achterwaarts door list anders index error
      distance = math.sqrt((Bubble_list[i].x_cord - self.x_cord)**2 + (Bubble_list[i].y_cord - self.y_cord)**2) #Stelling pythagoras om afstand tussen bel en player te krijgen
      if distance < (Bubble_list[i].radius + self.radius):
        self.score = self.score + self.get_score(Bubble_list[i])
        
        if Bubble_list[i].speed_powerup: #Als speed powerup
          self.speed = self.speed + config["bubble"]["SPEED_POWERUP_MODIFIER"]

        del Bubble_list[i]

  def blit_score(self): 
    score_text = SCORE_ARIAL.render("Score ", False, self.colour)   
    score_num_text = SCORE_ARIAL.render(str(self.score), False, WHITE)
    
    #Bepaald zo de lengte van de text, rect is (x1, y1, x2, y2) neem de 3de waarde
    x_length_score_text = score_text.get_rect()[2] 
    x_length_score_num_text = score_num_text.get_rect()[2]

    #Blit wordt zo gedaan dat text score_x pixels heeft tenopzichte zijkant scherm
    if self.score_x < CENTER_X:
      screen.blit(score_text, (self.score_x, self.score_y))
      screen.blit(score_num_text, (self.score_x + x_length_score_text, self.score_y))
    else:
      screen.blit(score_text, (self.score_x - x_length_score_text - x_length_score_num_text, self.score_y))
      screen.blit(score_num_text, (self.score_x - x_length_score_num_text, self.score_y))

class Computer(Player):
  def __init__(self, colour, score_x, score_y, genome, net):
    super().__init__(colour, score_x, score_y)
    self.genome = genome
    self.net = net

  def run_network(self, opp_x_cord, opp_y_cord, opp_speed):
    see_gap = 20
    d_list = list() #lijst wordt gebruikt als input netwerk
    temp_list = Bubble_list.copy()
    for i in range(len(temp_list) -1, -1, -1):
      if temp_list[i].x_cord < -see_gap or temp_list[i].x_cord > config["window"]["x"] + see_gap:
        del temp_list[i] 
      elif temp_list[i].speed_powerup and len(d_list) < sim_config["ai"]["MAX_BUB_INPUT"] - 1:
        d_list.append(temp_list[i])
        del temp_list[i]
    d_list.sort(key=lambda b: self.cal_distance(b.x_cord, b.y_cord))
    temp_list.sort(key=lambda b: self.cal_distance(b.x_cord, b.y_cord))
    d_list.extend(temp_list[:sim_config["ai"]["MAX_BUB_INPUT"] - len(d_list)])

    for i in range(len(d_list)):
      pygame.draw.line(screen, GREEN, (self.x_cord, self.y_cord), (d_list[i].x_cord, d_list[i].y_cord), 1)
    
    f_list = [self.x_cord, self.y_cord, self.speed, opp_x_cord, opp_y_cord, opp_speed]
    for i in range(sim_config["ai"]["MAX_BUB_INPUT"]):
      if i < len(d_list):
        f_list.append(d_list[i].x_cord)
        f_list.append(d_list[i].y_cord)
        f_list.append(d_list[i].speed)
        f_list.append(d_list[i].radius)
        f_list.append(int(d_list[i].speed_powerup))
        f_list.append(self.get_score(d_list[i]))
      else:
        for j in range(6):
          f_list.append(0)
      
    output = self.net.activate(tuple(f_list))
    return output

  def move_computer(self, opp_x_cord, opp_y_cord, opp_speed):
    output = self.run_network(opp_x_cord, opp_y_cord, opp_speed)
    
    if output[0] > 0.5:
      self.x_cord = self.x_cord + (self.speed * Global_cycle_timer)
    elif output[1] > 0.5:
      self.x_cord = self.x_cord - (self.speed * Global_cycle_timer)

    if output[2] > 0.5:
      self.y_cord = self.y_cord + (self.speed * Global_cycle_timer)
    elif output[3] > 0.5:
      self.y_cord = self.y_cord - (self.speed * Global_cycle_timer)

    #Border
    if self.x_cord < 0:
      self.x_cord = 0
    elif self.x_cord > config["window"]["x"]:
      self.x_cord = config["window"]["x"]
    #Bottom and top connected
    if self.y_cord < 0:
      self.y_cord = config["window"]["y"]
    elif self.y_cord > config["window"]["y"]:
      self.y_cord = 0
    #Speed decrease 
    if self.speed > config["player"]["PLAYER_SPEED"]:
      self.speed = self.speed - config["bubble"]["SPEED_DECREASE"] * Global_cycle_timer
    else:
      self.speed = config["player"]["PLAYER_SPEED"]

  def cal_distance(self, bub_x, bub_y):
    """Calculates distance from player to bubble with a bias for bubbles in front of player """
    back_bias = 2
    side_bias = 1.4
    if bub_x - self.x_cord < 0:
      distance = math.sqrt(((bub_x - self.x_cord)*back_bias)**2 + ((bub_y - self.y_cord)*side_bias)**2)
    else:
      distance = math.sqrt((bub_x - self.x_cord)**2 + ((bub_y - self.y_cord)*side_bias)**2)  
    return int(distance)

class Human_Player(Player):
  """Dit is de class voor de speler zelf, het inherit draw, collision en blit score uit de sub class Player """
  def __init__(self, colour, score_x, score_y, up, down, left, right):
    super().__init__(colour, score_x, score_y) #pass arguments to subclass
    self.key_up = up
    self.key_down = down
    self.key_left = left
    self.key_right = right

  def move_player(self):
    pygame.event.pump() #Nodig, anders is input player verneukt
    keys = pygame.key.get_pressed() #Neemd een list van alle keys
    if keys[self.key_up]: #Checkt of gegeven key in list ingedrukt is
      self.y_cord = self.y_cord - (self.speed * Global_cycle_timer) #beweegt speler afhankelijk van tijd
    if keys[self.key_down]:
      self.y_cord = self.y_cord + (self.speed * Global_cycle_timer)
    if keys[self.key_left]:
      self.x_cord = self.x_cord - (self.speed * Global_cycle_timer)
    if keys[self.key_right]:
      self.x_cord = self.x_cord + (self.speed * Global_cycle_timer)
    #Border
    if self.x_cord < 0:
      self.x_cord = 0
    elif self.x_cord > config["window"]["x"]:
      self.x_cord = config["window"]["x"]
    #Bottom and top connected
    if self.y_cord < 0:
      self.y_cord = config["window"]["y"]
    elif self.y_cord > config["window"]["y"]:
      self.y_cord = 0
    #Speed decrease 
    if self.speed > config["player"]["PLAYER_SPEED"]:
      self.speed = self.speed - config["bubble"]["SPEED_DECREASE"] * Global_cycle_timer
    else:
      self.speed = config["player"]["PLAYER_SPEED"]

def Game_PvE(genome, config_ai):
  ###Setup code
  Player_list.append(Human_Player(RED, 10, 10, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d))
  for _, g in genome:
    net = neat.nn.FeedForwardNetwork.create(g, config_ai)
    Player_list.append(Computer(YELLOW, config["window"]["x"] - 10, 10, g, net))

  global screen
  if Fullscreen:
      screen = pygame.display.set_mode(((config["window"]["x"], config["window"]["y"])), pygame.FULLSCREEN)  #Creër het scherm
  else:
      screen = pygame.display.set_mode((config["window"]["x"], config["window"]["y"]))
  screen.fill(BACKROUND)

  global Endtime 
  Endtime = time.time() + config["time"]["GAME_DURATION"]
  ###Main Program
  while time.time() < Endtime:
    Cycle_time_start = time.time() #Houd nu begintijd cycle bij
    
    create_bubble()
    move_all()
    draw_frame()
    screenformat()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
      pygame.quit()
      exit()
    
    pygame.display.flip()
    time.sleep(0.0001) 
    global Global_cycle_timer
    Global_cycle_timer = time.time() - Cycle_time_start #Update cycle time van loop

start_time = time.time()

def replay_genome(config_path, genome_path="ai_file.pickle"):
    # Load requried NEAT config
    config_ai = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Unpickle saved winner
    with open(genome_path, "rb") as f:
        genome = pickle.load(f)

    # Convert loaded genome into required data structure
    genome = [(1, genome)]

    # Call game with only the loaded genome
    Game_PvE(genome, config_ai)

start_time = time.time()

if __name__ == "__main__":
  local_dir = os.path.dirname(__file__) #File directory
  config_path = os.path.join(local_dir, "ai_config_file.txt") 
  AI_path = os.path.join(local_dir, "ai_file.pickle") 
  replay_genome(config_path, AI_path)
  
print("Time of sim run", time.time() - start_time)
