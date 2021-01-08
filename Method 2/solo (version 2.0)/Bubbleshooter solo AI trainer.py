###Libraries
import random
import time
import math
import os
import neat
import concurrent.futures
import json
import pickle

###Constant variables
#Open Files
with open ("config_constant_vars.json", "r") as cfg:
  config = json.load(cfg)
with open ("simulation_constant_vars.json", "r") as cfg:
  sim_config = json.load(cfg)

#player
CENTER_X = config["window"]["x"] // 2 #x en y positie midden van scherm
CENTER_Y = config["window"]["y"] // 2 

###Global list and variables
#Object storage
Player_list = list() #Bevat object spelers, waarschijnlijk 2

###Classes    
class Bubble():
  def __init__(self, speed_powerup):
    self.x_cord = config["window"]["x"] + config["bubble"]["GAP"] #x cord ligt een stukje buiten scherm
    self.y_cord = random.randint(0, config["window"]["y"]) #y cord is random hoogte in scherm
    self.radius = random.randint(config["bubble"]["MIN_BUB_RADIUS"], config["bubble"]["MAX_BUB_RADIUS"]) #random groote bel
    self.speed = random.randint(config["bubble"]["MIN_BUB_SPEED"],config["bubble"]["MAX_BUB_SPEED"]) #random snelheid
    self.speed_powerup = speed_powerup

  def move_bubble(self):
    self.x_cord = self.x_cord - (self.speed * sim_config["time"]["TIMESTEP"])
    #beweegt bel naar links afhankelijk van de tijd die er is verstreken in vergelijking met de vorige keer dat de bel is bewogen

class Computer():
  x_cord = CENTER_X
  y_cord = CENTER_Y
  radius = config["player"]["PLAYER_RADIUS"]
  speed = config["player"]["PLAYER_SPEED"]
  score = 0

  def __init__(self, genome, net):
    self.genome = genome
    self.net = net

  def run_network(self, Bubble_list):
    d_list = list() #lijst wordt gebruikt als input netwerk
    temp_list = Bubble_list.copy()
    for i in range(len(temp_list) -1, -1, -1):
      if temp_list[i].x_cord < - sim_config["ai"]["SEE_GAP"] or temp_list[i].x_cord > config["window"]["x"] + sim_config["ai"]["SEE_GAP"]:
        del temp_list[i] 
      elif temp_list[i].speed_powerup and len(d_list) < sim_config["ai"]["MAX_BUB_INPUT"] - 1:
        d_list.append(temp_list[i])
        del temp_list[i]
    d_list.sort(key=lambda b: self.cal_distance(b.x_cord, b.y_cord))
    temp_list.sort(key=lambda b: self.cal_distance(b.x_cord, b.y_cord))
    d_list.extend(temp_list[:sim_config["ai"]["MAX_BUB_INPUT"] - len(d_list)])

    f_list = [self.x_cord, self.y_cord, self.speed]
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

  def move_computer(self, Bubble_list):
    output = self.run_network(Bubble_list)
    
    if output[0] > 0.5:
      self.x_cord = self.x_cord + (self.speed * sim_config["time"]["TIMESTEP"])
    elif output[1] > 0.5:
      self.x_cord = self.x_cord - (self.speed * sim_config["time"]["TIMESTEP"])

    if output[2] > 0.5:
      self.y_cord = self.y_cord + (self.speed * sim_config["time"]["TIMESTEP"])
    elif output[3] > 0.5:
      self.y_cord = self.y_cord - (self.speed * sim_config["time"]["TIMESTEP"])
    
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
      self.speed = self.speed - config["bubble"]["SPEED_DECREASE"] * sim_config["time"]["TIMESTEP"]
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

  def get_score(self, bub):
    return int(bub.radius + int(bub.speed / config["player"]["SPEED_SCORE_MODIFIER"])) 

  def collision_and_score(self, Bubble_list):
    for i in range(len(Bubble_list) -1, -1, -1): #loopt achterwaarts door list anders index error
      distance = math.sqrt((Bubble_list[i].x_cord - self.x_cord)**2 + (Bubble_list[i].y_cord - self.y_cord)**2) #Stelling pythagoras om afstand tussen bel en player te krijgen
      if distance < (Bubble_list[i].radius + self.radius):
        self.score = self.score + self.get_score(Bubble_list[i])
        
        if Bubble_list[i].speed_powerup: #Als speed powerup
          self.speed = self.speed + config["bubble"]["SPEED_POWERUP_MODIFIER"]

        del Bubble_list[i]

class Match():
  def __init__(self, play_one, play_list):
    self.Bubble_list = list()
    self.play_one = play_one
    self.play_list = play_list 

  def create_bubble(self):
    if random.randint(0, int(config["bubble"]["BUB_CHANCE"]/ sim_config["time"]["TIMESTEP"])) == 0: #maakt kans afhankelijk van de verstreken tijd
      if random.randint(0, config["bubble"]["SPEED_POWERUP_CHANCE"]) == 0:
        self.Bubble_list.append(Bubble(True))  
      else:  
        self.Bubble_list.append(Bubble(False))

  def move_all(self):
    for i in range(len(self.Bubble_list)-1, -1, -1): #loops achteruit om errors te voorkomen  
      if self.Bubble_list[i].x_cord < -config["bubble"]["GAP"]: 
        del self.Bubble_list[i]
      else:
        self.Bubble_list[i].move_bubble()

    self.play_list[self.play_one].move_computer(self.Bubble_list)
    self.play_list[self.play_one].collision_and_score(self.Bubble_list)

###Functions   

def Game(match):
  match.play_list[match.play_one].score = 0

  Simtime = int(config["time"]["GAME_DURATION"] / sim_config["time"]["TIMESTEP"])
  ###Main Program
  for j in range(Simtime):    
    match.create_bubble()
    match.move_all()

  return (match.play_one, match.play_list[match.play_one].score)

def Simulation(genomes, config_ai):
  ###Setup code
  for _, g in genomes:
    net = neat.nn.FeedForwardNetwork.create(g, config_ai)
    g.fitness = 0
    Player_list.append(Computer(g, net))

  for _ in range(1, sim_config["sim"]["MAX_GAMES"] + 1):
    """Elke AI speelt een X aantal games in zijn eentje"""
    match_list = []
    for i in range(len(Player_list)):
      match_list.append(Match(i, Player_list))

    with concurrent.futures.ProcessPoolExecutor() as executor: #multiprocessing
      results = executor.map(Game, match_list)
      
      for result in results:
        play_one, score_one = result
        Player_list[play_one].genome.fitness = Player_list[play_one].genome.fitness + score_one / sim_config["sim"]["MAX_GAMES"]
    
  for i in range(len(Player_list)-1 , -1 ,-1):
    [Player_list[i].net].pop()
    [Player_list[i].genome].pop()
    Player_list.pop(i)

def run(config_path):
  config_ai = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
  if input("Type start_over if you want to retrain the AI:") == "start_over":
    print("Starting over...")
    time.sleep(0.5)
    pop = neat.Population(config_ai)
  else:
    print("Continueing progress...")
    time.sleep(0.5)
    pop = neat.Checkpointer.restore_checkpoint("neat_checkpoint.pickle")
  #Geeft statestieken van population
  pop.add_reporter(neat.StdOutReporter(True)) 
  stats = neat.StatisticsReporter()
  pop.add_reporter(stats)
  #Saves elke generatie
  checkpoint_path = os.path.join("checkpoints", "neat_checkpoint.pickle")
  pop.add_reporter(neat.Checkpointer(1, None, checkpoint_path)) #test

  winner = pop.run(Simulation, sim_config["sim"]["GENERATIONS"])
  with open('ai_file.pickle', 'wb') as f:
    pickle.dump(winner, f)

start_time = time.time()

if __name__ == "__main__":
  local_dir = os.path.dirname(__file__) #File directory
  config_path = os.path.join(local_dir, "ai_config_file.txt") 
  run(config_path)

print("Time of sim run", time.time() - start_time)

