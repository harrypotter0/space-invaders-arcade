#! /usr/bin/env python

import os, sys, pygame
from pygame.locals import *
import objects
import config as c
import numpy  as np

def where_alive(elist):
  """
  
  """
  alive = []
  for enemy in elist:
    if enemy.isAlive and enemy.state == 0:
      alive.append(enemy)
  return alive, len(alive)

def index_alive(lista):
  """
  Check if elements in a list are alive.
  Return a list of the indices of those who are alive,
  and a Boolean stating if any is alive.
  """
  alive = []
  for i in range(len(lista)):
    if lista[i].isAlive:
      alive.append(i)
  return alive, len(alive) > 0

def where_ammo(lista):
  avail = []
  for element in range( len(lista) ):
    if not lista[element].isAlive:
      avail.append(element)
  return avail, len(avail)

def plot_text(font, texto, screen, position, color):
  the_text = font.render( texto.strip(), True, color )
  rect = the_text.get_rect()
  rect.midtop = position
  screen.blit(the_text, rect)

def hit( left, bottom, right, top, left2, bottom2, right2=None, top2=None ):
  # 6 params > bullet
  if not right2: right2 = left2   
  if not top2: top2 = bottom2 - 4

  if (left <= right2  and right  >= left2 and 
      top  <= bottom2 and bottom >= top2  ):
    return True
  else:
      return False

def hit(rect, rect2):
  if (rect[0] <= rect2[2] and rect[2] >= rect2[0] and 
      rect[3] <= rect2[1] and rect[1] >= rect2[3] ):
    return True
  else:
    return False

def loadscores(scorefile, nscores, nlevs):
  player = np.zeros((nlevs, nscores), '|S3')
  scores = np.zeros((nlevs, nscores), int)
  file = open(scorefile, "r")
  lines = file.readlines()
  file.close()

  k = 0
  for i in np.arange(nlevs):
    for j in np.arange(nscores):
      player[i,j], scores[i,j] = lines[k].strip().split()
      player[i,j] = player[i,j].ljust(3)
      k += 1
  return player, scores

def savescores(players, scores, scorefile):
  nlevs, nscores = np.shape(players)
  file = open(scorefile, "w")
  for i in np.arange(nlevs):
    for j in np.arange(nscores):
      file.write(players[i,j] + " " + str(scores[i,j]) + "\n")
  file.close()

def updatescores(initials, hiscore, level, players, scores, scorefile):
  # find position
  newpos = np.where(scores[level-1] < hiscore)[0][0]
  # shift positions
  for pos in np.arange(len(scores[level-1])-1, newpos, step=-1):
    scores [level-1, pos] = scores [level-1, pos-1]
    players[level-1, pos] = players[level-1, pos-1]        
  # place new hi score
  scores [level-1, newpos] = hiscore
  players[level-1, newpos] = initials
  # save to file
  savescores(players, scores, scorefile)

class State:
  """
  Generic game state class that can handle events and display itself
  on a given surface.
  """
  level  = 1
  option = 1
  n_options = 5
  fps = 0
  pygame.font.init()
  font_fps = pygame.font.SysFont(None, c.font_size_fps)

  def handle(self, event):
    """
    Default event handling only deals with quitting.
    """
    if event.type == QUIT:
        sys.exit()
    if event.type == KEYDOWN:
      if event.key == K_ESCAPE:
        sys.exit()
      if event.key == K_LEFT:
        pass
      if event.key == K_RIGHT:
        pass
      if event.key == K_SPACE:
        pass
      if event.key == K_x:
        pass
      if event.key == K_c:
        pass

    if event.type == KEYUP:
      if event.key == K_LEFT:
        pass
      if event.key == K_RIGHT:
        pass
      if event.key == K_SPACE:
        pass
      if event.key == K_x:
        pass
      if event.key == K_c:
        pass

  def display(self, screen):
    """
    Used to display the State after it has already been displayed
    once. The default behavior is to do nothing.
    """
    # The background:
    screen.blit(game.background, game.bg_rect)

    # The stars:
    game.stars_y = (game.stars_y + game.stars_v*0.2) % c.screen_size[1]
    for i in range(c.n_stars):
      game.stars_x[i] = game.stars_x[i] if not game.stars_v[i] else \
                     game.stars_x[i] + 0.1*int((np.random.rand()-0.5)*2.1)
      pygame.draw.aaline(screen, c.color_stars,
                         (int(game.stars_x[i]), int(game.stars_y[i])),
                         (int(game.stars_x[i]), int(game.stars_y[i])))
    # Plot fps:
    plot_text(self.font_fps, "%i fps" % self.fps, screen,
              c.fps_position, c.font_color_fps)


class Play(State):
  enemigos = []

  def __init__(self, level=1, stage=1):
    self.waiting = True
    self.time_waiting = c.waiting_time/2
    self.stage = stage
    self.level = level
    self.n_enemies = c.total_enemies
    self.font_wait = pygame.font.Font(c.font, c.wait_size)
    # Create hero
    self.hero = objects.starship(level)

    # Create enemies
    del self.enemigos[:]
    for i in range(c.total_enemies):
      self.enemigos.append(objects.enemy1(i))

    # probabilities
    self.pb_release_time  = 0.0
    self.pb_release_kills = 0.0

    # stage and score
    self.font_ss = pygame.font.Font(c.font, c.font_size_ss)

  def restart(self, level=1, stage=1):
    self.stage = stage
    self.level = level
    self.n_enemies = c.total_enemies

    for i in range(self.n_enemies):
      if(np.random.rand() < 0.035*(self.stage + self.level - 5) ):
        # if(random.rand() < 0.5 ):
        self.enemigos[i] = objects.enemy2(i) 
      else:
        self.enemigos[i] = objects.enemy1(i)

      self.pb_release_time  = 0.0
      self.pb_release_kills = 0.0    

    if stage == 1:
      self.hero = objects.starship(level)
      for i in range(self.n_enemies):
        self.enemigos[i] = objects.enemy1(i) 

  def update(self, game):
    if not self.waiting:
      self.release_enemy()
      for enemigo in self.enemigos:
        enemigo.shoot(5e-4 * (self.level + (self.stage-1) +
                             (c.total_enemies - self.n_enemies) ))
      self.check_hits()
      self.check_catch()

    # Update hero
    self.hero.update()

    # Update enemy
    for enemigo in self.enemigos:
      enemigo.update()

    # Go to next state
    if self.hero.lives == 0:
      game.nextState = GameOver(game.score, self.level)
      game.score = 0

    if self.n_enemies == 0 and not self.waiting:
      self.waiting = True
      self.time_waiting = c.waiting_time

    if self.time_waiting >= 0:
      if self.time_waiting == c.waiting_time*3/4:
        self.restart(self.level, self.stage + 1)
      if self.time_waiting == 0:
        self.waiting = False
      self.time_waiting -= 1

  def display(self, screen):
    State.display(self, screen)

    # plot stage message
    if self.waiting and self.time_waiting < c.waiting_time/2:
      plot_text(self.font_wait, "STAGE %i" % self.stage, screen,
                c.wait_position, c.wait_color)

    # plot score and stage
    plot_text(self.font_ss, "stage: %i" % self.stage, screen,
              c.stage_position, c.font_color_ss)
    plot_text(self.font_ss, "score: %i" % game.score, screen,
              c.score_position, c.font_color_ss)

    # Plot hero and enemies:
    self.hero.draw(screen)
    for enemigo in self.enemigos:
      enemigo.draw(screen)

    pygame.display.flip()

  def handle(self, event, screen):
    State.handle(self, event)

    # Pressing
    if event.type == KEYDOWN:
      if event.key == K_LEFT:
        if self.hero.isAlive:
          self.hero.dv = -c.velocity
          self.hero.moving_l = True

      if event.key == K_RIGHT:
        if self.hero.isAlive:
          self.hero.dv = c.velocity
          self.hero.moving_r = True

      if event.key == K_SPACE and not self.waiting:
        if not self.hero.hold and self.hero.isAlive:
          avail, n_avail = where_ammo(self.hero.ammo)
          if n_avail > 0:
            self.hero.ammo[avail[0]] = objects.bullet(self.hero.x[4],
                                                      self.hero.y[4])
            self.hero.hold = True
            self.hero.ammo_holded = avail[0]

      if event.key == K_x and not self.waiting:
        if self.hero.isAlive:
          for j in range(c.n_bombs):
            if (self.hero.special[0][j].isAlive     and
                self.hero.special[0][j].status == 1 ):
              self.hero.special[0][j].changeStatus(2)

      if (event.key == K_c and not self.waiting):
        if self.hero.isAlive:
          b = False
          for t in [2, 1]:
            for j in range(c.n_bombs):
              if (self.hero.special[1][j].isAlive     and
                  self.hero.special[1][j].status == t ):
                if b: 
                  break
                self.hero.special[1][j].changeStatus(
                                             self.hero.special[1][j].status + 1)
                b = True
      if event.key == K_RETURN:
        print 'save!'
        pygame.image.save(screen, 'screencap.png')
    # Releasing
    if event.type == KEYUP:
      if event.key == K_LEFT:
        if self.hero.isAlive: 
          self.hero.dv =  c.velocity if self.hero.moving_r else 0
          self.hero.moving_l = False

      if event.key == K_RIGHT:
        if self.hero.isAlive:
          self.hero.dv = -c.velocity if self.hero.moving_l else 0
          self.hero.moving_r = False

      if event.key == K_SPACE:
        if(self.hero.hold):
          self.hero.hold = False
          self.hero.ammo[self.hero.ammo_holded].hooked = False

      if event.key == K_x:
        pass
      if event.key == K_c:
        pass

  def release_enemy(self):
    if np.random.rand() < (self.pb_release_time + self.pb_release_kills):
      vivos, n_vivos = where_alive(self.enemigos)
      self.enemigos[int(np.random.rand()*n_vivos)].state = 1
    if self.pb_release_time < 0.0038 and self.pb_release_kills > 0.0011:
      self.pb_release_time += 0.000001

  def create_bomb(self, pos_x, pos_y):
    i = int(np.random.rand()*c.type_bombs)
    for j in range(c.n_bombs):
      if not self.hero.special[i][j].isAlive and np.random.rand() < 0.15:
        if   i == 0:
          self.hero.special[i][j] = objects.laser(pos_x, pos_y)
        elif i == 1:
          self.hero.special[i][j] = objects.cluster(pos_x, pos_y)
        else:
          self.hero.special[i][j] = objects.rocket(pos_x, pos_y)
        break

  def check_hits(self):
    # hero bullets to enemies:
    vivos, are_they = index_alive(self.hero.ammo)
    for i in vivos:
      malditos, estan_vivos = index_alive(self.enemigos)
      for j in malditos:
        if hit( self.enemigos[j].get_rect(),
               self.hero.ammo[i].get_rect()):
          self.hero.ammo[i].isAlive = False
          self.enemigos[j].kill()
          game.score += 100
          self.n_enemies -= 1
          self.pb_release_kills = 6e-4 * (c.total_enemies -
                                          self.n_enemies)
          self.create_bomb(self.hero.ammo[i].x, self.hero.ammo[i].y)
          if self.n_enemies == 0:
            pass
          break

    # Enemy bullets hits hero:
    if self.hero.isAlive and not self.hero.invincible:
      for i in range(c.total_enemies):
        balas, are_they = index_alive(self.enemigos[i].ammo)
        for j in balas:
          if not are_they:
            break
          if hit(self.enemigos[i].ammo[j].get_rect(), self.hero.get_rect()) or \
             hit(self.enemigos[i].ammo[j].get_rect(), self.hero.get_rect(True)):
            self.hero.kill()
            self.enemigos[i].ammo[j].isAlive = False

    # Collision:   
    for i in range(c.total_enemies):  
      if (self.enemigos[i].isAlive and self.hero.isAlive and
          not self.hero.invincible):
        if (hit(self.enemigos[i].get_rect(), self.hero.get_rect())     or
            hit(self.enemigos[i].get_rect(), self.hero.get_rect(True)) ):
          self.enemigos[i].kill()
          self.hero.kill()
          game.score += 100
          self.hero.stop()
          self.n_enemies -= 1
          self.pb_release_kills = 6e-4 * (c.total_enemies - self.n_enemies)
          if self.n_enemies == 0:
            pass
          break

    for i in range(c.type_bombs): # type bomb
      for j in range(c.n_bombs):
        if self.hero.special[i][j].isAlive:
          malditos, estan_vivos = index_alive(self.enemigos)
          for k in malditos:
            if self.hero.special[i][j].checkHit(self.enemigos[k].get_rect()):
              # enemigos[k].x[1], enemigos[k].x[4],
              # enemigos[k].y[2], enemigos[k].y[0]):
              self.enemigos[k].kill()
              game.score += 100
              self.n_enemies -= 1
              self.pb_release_kills = 6e-4 * (c.total_enemies - self.n_enemies)

  def check_catch(self):   # hero catches bombs
    for i in range(c.type_bombs):
      for j in range(c.n_bombs):
        if (self.hero.special[i][j].isAlive     and
            self.hero.special[i][j].status == 0 ):                        
          if hit(self.hero.special[i][j].get_rect(), self.hero.get_rect()) or \
             hit(self.hero.special[i][j].get_rect(), self.hero.get_rect(True)):
            game.score += 20
            if self.hero.special[i][abs(j-1)].status != 1:
              # catch it
              self.hero.special[i][j].changeStatus(1)
            else:
              # catch it but don't add it:
              self.hero.special[i][j].y = 480


class Paused(State):
  def __init__(self, lev_names=False):
    self.finished = 0  # Has the user ended the pause?
    self.clickbox = [] # clickable boxes
    self.texts    = [] # texts
    self.textbox  = [] # text boxes
    self.scoretxt = [] # score texts
    self.scorebox = []
    self.initials = "" # Initials for new hi-score
    font_title = pygame.font.Font(c.font, c.font_startUp_title)
    font_score = pygame.font.Font(c.font, c.font_score)
    font_body  = pygame.font.Font(c.font, c.font_score)

    for i in np.arange(len(self.text_big)):
      self.texts.append(font_title.render(self.text_big[i].strip(),
                                          True, c.color_text))
      r = self.texts[i].get_rect()
      r.topleft = (c.title_x_pos + c.title_deltaX[i],
                   c.title_y_pos + c.title_deltaY[i])
      self.textbox.append(r)
      if self.rectangle[i]:
        r = r.inflate(6,4)
        self.clickbox.append(r)

    for i in np.arange(len(self.text)):
      self.texts.append(font_body.render(self.text[i].strip(),
                                         True, c.color_text))
      r = self.texts[i].get_rect()
      r.topleft = c.texto_x_pos, c.texto_y_pos + i*c.texto_deltaY
      self.textbox.append(r)

    # Scores:
    if lev_names != False:
      stext = [""]
      for i in np.arange(len(lev_names)):
        stext[0] += str(lev_names[i]).ljust(15, " ")
      for i in np.arange(len(game.players[0])):
        stext.append("")
        for j in np.arange(len(lev_names)):
          stext[-1] += (game.players[j,i] + "   " +
                        str(game.scores[j,i]).rjust(7, " ") + "  ")

      for i in np.arange(len(stext)):
        self.scoretxt.append(font_score.render(stext[i].strip(),
                                           True, c.color_score))
        r = self.scoretxt[i].get_rect()
        r.topleft = c.scorex, c.scorey + i*c.scoredy
        self.scorebox.append(r)

  def handle(self, event, screen):
    State.handle(self, event)
    if event.type in [MOUSEBUTTONDOWN]:
      mpx, mpy = pygame.mouse.get_pos() # mouse position
      for b in np.arange(len(self.clickbox)):
        if (mpx > self.clickbox[b].left  and
            mpx < self.clickbox[b].right and
            mpy > self.clickbox[b].top   and
            mpy < self.clickbox[b].bottom ):
          self.finished = b + 1

    if event.type in [KEYDOWN]:
      if event.key == K_DOWN:
        self.option = min(self.option + 1, self.n_options)
      if event.key == K_UP:
        self.option = max(self.option - 1, 1) 
      if event.key == K_RETURN:
        self.finished = 1
        if self.newhiscore:
          updatescores(self.initials.ljust(3), self.score, self.level,
                       game.players, game.scores, c.scorefile)

      if self.newhiscore  and  97 <= event.key <= 122: # [a, ..., z]
        ind = len(self.text_big) - 1
        font_title = pygame.font.Font(c.font, c.font_startUp_title)
        self.initials += pygame.key.name(event.key).upper()
        self.text_big[ind] = self.text_big[ind].replace("_",
                            pygame.key.name(event.key).upper(), 1)

        self.texts[ind] = font_title.render(self.text_big[ind],
                                            True, c.color_text)
        r = self.texts[ind].get_rect()
        r.topleft = (c.title_x_pos + c.title_deltaX[ind],
                     c.title_y_pos + c.title_deltaY[ind])
        self.textbox[ind] = r
        if len(self.initials) == 3:
          self.newhiscore = False
          updatescores(self.initials, self.score, self.level,
                       game.players, game.scores, c.scorefile)

  def update(self, game):
    pass

  def display(self, screen):
    State.display(self, screen)

    # Draw clickable boxes:
    for b in np.arange(len(self.clickbox)):
      pygame.draw.rect(screen, c.color_text, self.clickbox[b], 1)

    # Draw texts:
    for i in np.arange(len(self.texts)):
      screen.blit(self.texts[i], self.textbox[i])

    # Draw texts:
    for i in np.arange(len(self.scoretxt)):
      screen.blit(self.scoretxt[i], self.scorebox[i])

    # Cursor
    font_body = pygame.font.Font(c.font, c.font_score)
    texto = font_body.render(c.cursor, True, c.color_text)
    r = texto.get_rect()
    r.topleft = c.cursor_x_pos, c.cursor_y_pos + self.option*c.texto_deltaY
    screen.blit(texto, r)

    # Display all the changes:
    pygame.display.flip()


class GameOver(Paused):
  def __init__(self, score, level):
    self.n_options = 2
    self.text_big  = ["Play again? ", "Final Score: %i"%score]
    self.rectangle = [False,          False]
    self.text     = ["Yeah", "Nope"]
    self.newhiscore = False
    # compare current score to hiscores
    if np.any(score > game.scores[level-1]):
      self.text_big.extend(["New High Score,",
                            "Type your initials: _ _ _"])
      self.rectangle.extend([False, False])
      self.newhiscore = True
      self.score = score
      self.level = level
    Paused.__init__(self)

  def update(self, game):
    if self.finished:
      if self.option == 2: 
        sys.exit()
      else:                
        game.nextState = StartUp()


class StartUp(Paused):
  def __init__(self):
    self.n_options = 3
    self.text_big  = ["CHOOSE LEVEL:", "Start", "High Scores"]
    self.rectangle = [False,            True,   True]
    self.text      = ["Easy", "Normal", "Hard"]
    self.newhiscore = False
    Paused.__init__(self)

  def update(self, game):
    if   self.finished == 1:
      game.nextState = Play(level=self.option, stage=1)
    elif self.finished == 2:
      game.nextState = Scores(self.text)


class Scores(Paused):
  def __init__(self, lev_names):
    self.n_options = 1
    self.text_big  = ["High Scores:"]
    self.rectangle = [False]
    self.text      = ["return"]
    self.newhiscore = False
    Paused.__init__(self, lev_names)

  def update(self, game):
    if self.finished:         
      game.nextState = StartUp()

class Game:
  """
  Game object that takes care of the main event loop, including
  changing between the different game states.
  """

  def __init__(self, *args):
    # Get the directory where the game and the images are located:
    path = os.path.abspath(args[0])
    dir = os.path.split(path)[0]
    # Move to that directory (so that the image files may be
    # opened later on):
    os.chdir(dir)
    # Start with no state:
    self.state = None
    # Move to StartUp in the first event loop iteration:
    self.nextState = StartUp()
    self.background = None
    self.bg_rect = None
    self.score = 0

    # The background stars:
    # Set the position:
    self.stars_x = np.random.rand(c.n_stars)*c.screen_size[0]
    self.stars_y = np.random.rand(c.n_stars)*c.screen_size[1]
    # Set the velocity:
    self.stars_v = np.zeros(c.n_stars)
    for i in np.arange(c.n_stars):
      self.stars_v[i] = int(0.5 + np.random.uniform()*c.stars_vel)

    # Read scores:
    nscores = 3
    nlevs   = 3
    scores  = np.zeros((nlevs, nscores))
    if not os.path.isfile(c.scorefile):
      players = np.array([["AAA","BBB","CCC"], ["AAA","BBB","CCC"],
                          ["AAA","BBB","CCC"]])
      scores = np.array([[0,0,0], [0,0,0], [0,0,0]])
      savescores(players, scores, c.scorefile)

    self.players, self.scores = loadscores(c.scorefile, nscores, nlevs)

  def run(self):
    """
    This method sets things in motion.  It performs some vital
    initialization tasks, and enters the main event loop.
    """
    pygame.init()

    # Decide whether to display the game in a window or to use the
    # full screen:
    flag = 0 # Default (window) mode
    
    if c.full_screen:
      flag = FULLSCREEN # Full screen mode
    screen_size = c.screen_size
    screen = pygame.display.set_mode(screen_size, flag)

    self.background = pygame.image.load(c.background_image).convert()
    self.background = pygame.transform.rotate(self.background, 180)
    self.background = pygame.transform.smoothscale(self.background,
                                                   (809, 456) )

    self.bg_rect = self.background.get_rect()

    pygame.display.set_caption("Potter's Space Invaders")
    pygame.mouse.set_visible(True)

    # The main loop:
    while True:
      start_time = pygame.time.get_ticks()

      # (1) If nextState has been changed, move to the new state, and
      # display it (for the first time):
      if self.state != self.nextState:
        self.state = self.nextState

      # (2) Delegate the event handling to the current state:
      for event in pygame.event.get():
        self.state.handle(event, screen)

      # (3) Update the current state:
      self.state.update(self)

      # (4) Display the current state:
      self.state.display(screen)
       
      delta_time = pygame.time.get_ticks() - start_time
      if delta_time < c.time_speed:
        pygame.time.wait(c.time_speed - delta_time)
      self.state.fps = 1000/(pygame.time.get_ticks()-start_time)

if __name__ == '__main__':
  game = Game(*sys.argv)
  game.run()
