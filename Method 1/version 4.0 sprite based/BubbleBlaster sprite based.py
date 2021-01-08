###Libraries
import pygame
import random
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
with open ("animation_constant_vars.json", "r") as cfg:
  anim_config = json.load(cfg)

#screen
BACKROUND = (0, 0, 150) #achtergrond kleur is blauw

#colours
WHITE = (255, 255, 255)
RED = (220, 0, 0)
YELLOW = (255, 190, 0)
GREEN = (0, 220, 0)

#player
CENTER_X = config["window"]["x"] // 2 #x en y positie midden van scherm
CENTER_Y = config["window"]["y"] // 2 

########################################################################################

###Functions
def create_bubble():
  """This function randomly creates new bubbles and powerups at the right side of the screen.
  If a bubble moves of the (left side) screen, it will be destroyed"""
  if random.randint(0, int(config["bubble"]["BUB_CHANCE"] * config["time"]["TICKS_PER_SECOND"])) == 0: #maakt kans afhankelijk van de verstreken tijd
    if random.randint(0, config["bubble"]["SPEED_POWERUP_CHANCE"]) == 0:
      Powerup_group.add(Speed_Powerup(SPEED_POWERUP_ANIMATION, True))
    else:  
      Bubble_list.append(Bubble())
  
  for i in range(len(Bubble_list)-1, -1, -1): #loops achteruit om errors te voorkomen  
    if Bubble_list[i].x_cord < -config["bubble"]["GAP"]: 
      del Bubble_list[i]
  
  for powerup in Powerup_group:
    if powerup.x_cord < -config["bubble"]["GAP"]:
      Powerup_group.remove(powerup)
        
def load_animation(folder_path, scale=None):
  #Get all images from folder and put them in order in a list
  #images need to be numbered (image one is "1.png")
  images = list()
  folder_list = os.listdir(folder_path)
  folder_list.sort(key=lambda n: int(n[:-4]))
  if scale == None:
    for filename in folder_list:
      img = pygame.image.load(os.path.join(folder_path,filename)).convert_alpha()
      if img is not None:
        images.append(img)
  else:
    for filename in folder_list:
      img = pygame.transform.scale(pygame.image.load(os.path.join(folder_path,filename)), scale)
      img = img.convert_alpha()
      if img is not None:
        images.append(img)
  return images

###Classes
class Background():
  def __init__(self, animation):
    super().__init__()
    self.animation = animation
    self.current_background = 0
    self.image = self.animation[self.current_background]

    self.animation_speed = anim_config["background"]["ANIMATION_SPEED"] / config["time"]["TICKS_PER_SECOND"]

  def blit_background(self):
    self.current_background = self.current_background + self.animation_speed
    if len(self.animation) <= self.current_background:
      if len(self.animation) * 2 - 2 <= self.current_background:
        self.current_background = 0
        blink_sprite = 0
      else:
        blink_sprite = len(self.animation) - self.current_background - 2
    else:
      blink_sprite = self.current_background
    self.image = self.animation[int(blink_sprite)]
    screen.blit(self.image, (0, 0))
       
class Score_Boord(pygame.sprite.Sprite):
  def __init__(self, colour, x, y):
    super().__init__()
    self.x = x
    self.y = y
    self.base = pygame.Surface((90, 20))
    self.base = self.base.convert_alpha()
    self.base.fill((0, 0, 0, 0))
    self.base.blit(SCORE_ARIAL.render("Score ", False, colour), (0, 0))
    self.image = self.base.copy()

    self.rect = self.image.get_rect()
    self.rect.center = [self.x, self.y]

  def update_score(self, score):
    num_pos = (50, 0)
    self.image = self.base.copy()
    self.image.blit(SCORE_ARIAL.render(str(score), False, WHITE), num_pos)
    
    
class Particle_Effect(pygame.sprite.Sprite):
  """This is an animation that will only be played once ad a fixed position
   (like a bubble exploding) """
  def __init__(self, x, y, animation, animation_speed, sound_effect=None, cut=0):
    super().__init__()
    self.animation = animation
    self.current_sprite = 0
    self.image = self.animation[self.current_sprite]

    self.animation_speed = animation_speed / config["time"]["TICKS_PER_SECOND"]

    self.rect = self.image.get_rect()
    self.rect.center = [x, y]
    
    if sound_effect != None:
      sound_effect.play() #the sound effect is played once, as a part of the particle effect

    if cut > 0:
      self.total_frames = len(self.animation) - cut
      self.animation_speed = self.animation_speed / 2
    else:
      self.total_frames = len(self.animation)
      
  def update(self):
    self.current_sprite = self.current_sprite + self.animation_speed

    if self.total_frames <= self.current_sprite:
      self.current_sprite = 0
      Particle_group.remove(self)
    
    self.image = self.animation[int(self.current_sprite)]

class Bubble():
  def __init__(self):
    self.x_cord = config["window"]["x"] + config["bubble"]["GAP"] #x cord ligt een stukje buiten scherm
    self.y_cord = random.randint(0, config["window"]["y"]) #y cord is random hoogte in scherm
    self.radius = random.randint(config["bubble"]["MIN_BUB_RADIUS"], config["bubble"]["MAX_BUB_RADIUS"]) #random groote bel
    self.speed = random.randint(config["bubble"]["MIN_BUB_SPEED"],config["bubble"]["MAX_BUB_SPEED"]) #random snelheid

  def move_bubble(self):
    self.x_cord = self.x_cord - (self.speed / config["time"]["TICKS_PER_SECOND"])
    #beweegt bel naar links afhankelijk van de tijd die er is verstreken in vergelijking met de vorige keer dat de bel is bewogen

  def draw_bubble(self):
    pygame.draw.circle(screen, WHITE, (int(self.x_cord),int(self.y_cord)), self.radius, 1) 

class Speed_Powerup(pygame.sprite.Sprite, Bubble):
  def __init__(self, powerup_animation, blink=False):
    super().__init__()
    Bubble.__init__(self)
    self.powerup_sprites = powerup_animation
    self.blink = blink 
    self.current_sprite = 0
    self.image = self.powerup_sprites[self.current_sprite]

    self.animation_speed = anim_config["speed_powerup"]["ANIMATION_SPEED"] / config["time"]["TICKS_PER_SECOND"]

    self.rect = self.image.get_rect()
    self.rect.center = [self.x_cord, self.y_cord]

    self.radius = config["bubble"]["SPEED_POWERUP_RADIUS"]
    
  def update(self):
    self.move_bubble()
    self.rect.center = [self.x_cord, self.y_cord]

    self.current_sprite = self.current_sprite + self.animation_speed
    if self.blink:
      if len(self.powerup_sprites) <= self.current_sprite:
        if len(self.powerup_sprites) * 2 - 2 <= self.current_sprite:
          self.current_sprite = 0
          blink_sprite = 0
        else:
          blink_sprite = len(self.powerup_sprites) - self.current_sprite - 2
      else:
        blink_sprite = self.current_sprite
      self.image = self.powerup_sprites[int(blink_sprite)]
    else:
      if len(self.powerup_sprites) <= self.current_sprite:
        self.current_sprite = 0
      self.image = self.powerup_sprites[int(self.current_sprite)]
    
class Player(pygame.sprite.Sprite):
  x_cord = CENTER_X
  y_cord = CENTER_Y
  radius = config["player"]["PLAYER_RADIUS"]
  speed = config["player"]["PLAYER_SPEED"]
  score = 0

  moving = True

  def __init__(self, idle_animation_folder, moving_animation_folder, colour, score_x, score_y):
    super().__init__()
    self.idle_sprites = load_animation(idle_animation_folder)
    self.moving_sprites = load_animation(moving_animation_folder)
    self.current_sprite = 0
    self.image = self.idle_sprites[self.current_sprite]
    
    self.animation_speed = anim_config["player"]["ANIMATION_SPEED"] / config["time"]["TICKS_PER_SECOND"]

    self.rect = self.image.get_rect()
    self.rect.center = [self.x_cord  - self.radius, self.y_cord]

    self.score_boord = Score_Boord(colour, score_x, score_y)
    Score_group.add(self.score_boord)

  def _allignImage(self):
    #The sprite is 30 by 60 pixels, the submarine itself takes up the right half of the images
    #Therefore the center of the images needs to be left of the center of the hitbox
    self.rect.center = [int(self.x_cord - self.radius), int(self.y_cord)]

  def update(self):
    ###Calculate sprite
    self._allignImage()
    self.current_sprite = self.current_sprite + self.animation_speed
    
    if self.moving: #Do moving animation
      if len(self.moving_sprites) <= self.current_sprite:
        self.current_sprite = 0
      self.image = self.moving_sprites[int(self.current_sprite)]

    else: #Do Idle animation
      if len(self.idle_sprites) <= self.current_sprite:
        self.current_sprite = 0
      self.image = self.idle_sprites[int(self.current_sprite)]

    #Makes a call to inheriting class
    self.player_logic()

  def get_score(self, bub):
    return int(bub.radius + int(bub.speed / config["player"]["SPEED_SCORE_MODIFIER"])) 

  def collision_and_score(self):
    for i in range(len(Bubble_list) -1, -1, -1): #loopt achterwaarts door list anders index error
      distance = math.sqrt((Bubble_list[i].x_cord - self.x_cord)**2 + (Bubble_list[i].y_cord - self.y_cord)**2) #Stelling pythagoras om afstand tussen bel en player te krijgen
      if distance < (Bubble_list[i].radius + self.radius):
        self.score = self.score + self.get_score(Bubble_list[i])
        self.score_boord.update_score(self.score)

        if Bubble_list[i].radius > 20:
          Particle_group.add(Particle_Effect(Bubble_list[i].x_cord, Bubble_list[i].y_cord, BUBBLE_EXPLOSIAN_ANIMATION, anim_config["bubble"]["EXPLOSIAN_ANIMATION_SPEED"], POP_SOUND, 0))
        else:
                    Particle_group.add(Particle_Effect(Bubble_list[i].x_cord, Bubble_list[i].y_cord, BUBBLE_EXPLOSIAN_ANIMATION, anim_config["bubble"]["EXPLOSIAN_ANIMATION_SPEED"], POP_SOUND, 2)) 
        
        del Bubble_list[i]

    for powerup in Powerup_group:
      distance = math.sqrt((powerup.x_cord - self.x_cord)**2 + (powerup.y_cord - self.y_cord)**2)
      if distance < (powerup.radius + self.radius):
        self.score = self.score + self.get_score(powerup)
        self.score_boord.update_score(self.score)
        self.speed = self.speed + config["bubble"]["SPEED_POWERUP_MODIFIER"]

        Particle_group.add(Particle_Effect(powerup.x_cord, powerup.y_cord, RADIOACTIVE_SIGN_ANIMATION, anim_config["speed_powerup"]["SIGN_ANIMATION_SPEED"]))
        #To Do, add sound effect
                           
        Powerup_group.remove(powerup)


class Computer(Player):
  def __init__(self, idle_animation_folder, moving_animation_folder, colour, score_x, score_y, genome, net):
    super().__init__(idle_animation_folder, moving_animation_folder, colour, score_x, score_y)
    self.genome = genome
    self.net = net

  def player_logic(self):
    for player in Player_group: #get the values from human player 
      if isinstance(player, Player):
        opp_x_cord, opp_y_cord, opp_speed = player.x_cord, player.y_cord, player.speed
        
    self._move_computer(opp_x_cord, opp_y_cord, opp_speed)
    self.collision_and_score()

  def run_network(self, opp_x_cord, opp_y_cord, opp_speed):
    d_list = list() #lijst wordt gebruikt als input netwerk

    for powerup in Powerup_group:
      d_list.append(powerup)
    
    d_list.sort(key=lambda b: self._cal_distance(b.x_cord, b.y_cord))
    if len(d_list) > sim_config["ai"]["MAX_BUB_INPUT"]:
      d_list = d_list[:sim_config["ai"]["MAX_BUB_INPUT"]]

    temp_list = Bubble_list.copy()

    for i in range(len(temp_list) -1, -1, -1):
      if temp_list[i].x_cord < - sim_config["ai"]["SEE_GAP"] or temp_list[i].x_cord > config["window"]["x"] + sim_config["ai"]["SEE_GAP"]:
        del temp_list[i] 

    temp_list.sort(key=lambda b: self._cal_distance(b.x_cord, b.y_cord))
    d_list.extend(temp_list[:sim_config["ai"]["MAX_BUB_INPUT"] - len(d_list)])

    f_list = [self.x_cord, self.y_cord, self.speed, opp_x_cord, opp_y_cord, opp_speed]
    for i in range(sim_config["ai"]["MAX_BUB_INPUT"]):
      if i < len(d_list):
        f_list.append(d_list[i].x_cord)
        f_list.append(d_list[i].y_cord)
        f_list.append(d_list[i].speed)
        f_list.append(d_list[i].radius)
        if isinstance(d_list[i], Speed_Powerup):
          f_list.append(1)
        else:
          f_list.append(0)
        f_list.append(self.get_score(d_list[i]))
      else:
        for j in range(6):
          f_list.append(0)
      
    output = self.net.activate(tuple(f_list))
    return output

  def _move_computer(self, opp_x_cord, opp_y_cord, opp_speed):
    output = self.run_network(opp_x_cord, opp_y_cord, opp_speed)
    
    self.moving = False
    if output[0] > 0.5:
      self.x_cord = self.x_cord + (self.speed / config["time"]["TICKS_PER_SECOND"])
      self.moving = True
    if output[1] > 0.5:
      self.x_cord = self.x_cord - (self.speed / config["time"]["TICKS_PER_SECOND"])
      self.moving = True
    if output[2] > 0.5:
      self.y_cord = self.y_cord + (self.speed / config["time"]["TICKS_PER_SECOND"])
      self.moving = True
    if output[3] > 0.5:
      self.y_cord = self.y_cord - (self.speed / config["time"]["TICKS_PER_SECOND"])
      self.moving = True

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
      self.speed = self.speed - config["bubble"]["SPEED_DECREASE"] / config["time"]["TICKS_PER_SECOND"]
    else:
      self.speed = config["player"]["PLAYER_SPEED"]

  def _cal_distance(self, bub_x, bub_y):
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
  def __init__(self, idle_animation_folder, moving_animation_folder, colour, score_x, score_y, up, down, left, right):
    super().__init__(idle_animation_folder, moving_animation_folder, colour, score_x, score_y) #pass arguments to subclass
    self.key_up = up
    self.key_down = down
    self.key_left = left
    self.key_right = right
  
  def player_logic(self):
    self._move()
    self.collision_and_score()

  def _move(self):
    self.moving = False
    if keys[self.key_up]: #Checkt of gegeven key in list ingedrukt is
      self.y_cord = self.y_cord - (self.speed / config["time"]["TICKS_PER_SECOND"])
      self.moving = True
    if keys[self.key_down]:
      self.y_cord = self.y_cord + (self.speed / config["time"]["TICKS_PER_SECOND"])
      self.moving = True
    if keys[self.key_left]:
      self.x_cord = self.x_cord - (self.speed / config["time"]["TICKS_PER_SECOND"])
      self.moving = True
    if keys[self.key_right]:
      self.x_cord = self.x_cord + (self.speed / config["time"]["TICKS_PER_SECOND"])
      self.moving = True
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
      self.speed = self.speed - config["bubble"]["SPEED_DECREASE"] / config["time"]["TICKS_PER_SECOND"]
    else:
      self.speed = config["player"]["PLAYER_SPEED"]
    
########################################################################################

def Game_PvE(genome, config_ai):
  ###Setup code
  pygame.init()

  global clock
  clock = pygame.time.Clock()

  global screen
  screen = pygame.display.set_mode((config["window"]["x"], config["window"]["y"]))

  global keys
  keys = pygame.key.get_pressed()

  #Sprite groups
  global Bubble_list, Powerup_group, Player_group, Particle_group, Score_group
  Bubble_list = list()
  Powerup_group = pygame.sprite.Group()
  Player_group = pygame.sprite.Group()
  Particle_group = pygame.sprite.Group()
  Score_group = pygame.sprite.Group()
  
  #Graphics
  global SPEED_POWERUP_ANIMATION, BUBBLE_EXPLOSIAN_ANIMATION, RADIOACTIVE_SIGN_ANIMATION
  SPEED_POWERUP_ANIMATION = load_animation(os.path.join("Sprites", "Speed_powerup animation", "Radioactive barrel"))
  BUBBLE_EXPLOSIAN_ANIMATION = load_animation(os.path.join("Sprites", "Particle effects", "Bubble explosian animation"))
  RADIOACTIVE_SIGN_ANIMATION = load_animation(os.path.join("Sprites", "Particle effects", "Radioactive sign animation"))
  
  global time_font, GAME_OVER, SCORE_ARIAL
  time_font = pygame.font.SysFont("Arial", 30, True, False)
  GAME_OVER = pygame.font.SysFont("Times new Roman", 60, True, False)
  SCORE_ARIAL = pygame.font.SysFont("Arial", 20, True, False)

  #Background
  Background_animation = Background(load_animation(os.path.join("Sprites", "Background animation"), (config["window"]["x"], config["window"]["y"])))
  
  #Sounds
  global POP_SOUND
  POP_SOUND = pygame.mixer.Sound(os.path.join("Sound", "Bubble_pop.wav"))
  POP_SOUND.set_volume(0.25)
  
  #Players
  temp_animation = os.path.join("Sprites", "Player animation")
  Player_group.add(Human_Player(os.path.join(temp_animation, "Red player", "Idle animation"), os.path.join(temp_animation, "Red player", "Moving animation"), RED, 55, 15, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d))

  for _, g in genome:
    net = neat.nn.FeedForwardNetwork.create(g, config_ai)
    Player_group.add(Computer(os.path.join(temp_animation, "Yellow player", "Idle animation"), os.path.join(temp_animation, "Yellow player", "Moving animation"), YELLOW, config["window"]["x"] - 55, 15, g, net))
  
  ###Main Game Loop
  """The main game is tick based, every tick the game state is calculated and a frame is drawn 
  pygame manages the time between each tick. 
  The game has a certain number of ticks, therefore a for loop is used"""
  for ticks in range(config["time"]["TICKS_PER_SECOND"] * config["time"]["GAME_DURATION"]):
    clock.tick(config["time"]["TICKS_PER_SECOND"])
    pygame.event.pump()
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        exit()

    create_bubble()

    Player_group.update()
    Powerup_group.update()
    for bub in Bubble_list:
      bub.move_bubble()
    Particle_group.update()

    Background_animation.blit_background()
    Powerup_group.draw(screen)
    for bub in Bubble_list:
      bub.draw_bubble()
    Particle_group.draw(screen)
    Player_group.draw(screen)
    Score_group.draw(screen)

    #Count down clock
    Game_time = 1 + int((config["time"]["TICKS_PER_SECOND"] * config["time"]["GAME_DURATION"] - ticks) / 60) 
    screen.blit(time_font.render(str(Game_time), 1, (255, 255, 255)), (CENTER_X, 10))
                           
    pygame.display.flip()


########################################################################################

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

if __name__ == "__main__":
  local_dir = os.path.dirname(__file__) #File directory
  config_path = os.path.join(local_dir, "ai_config_file.txt") 
  AI_path = os.path.join(local_dir, "ai_file.pickle") 
  replay_genome(config_path, AI_path)
