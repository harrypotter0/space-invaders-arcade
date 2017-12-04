import pygame, os
import numpy  as np
import config as c

class enemy():
  def __init__(self, pos):
    """
    Initialize object
    """
    # Position ID:
    self.position = pos
    # X,Y coordinates of the enemy vertices:
    self.x = np.array([75, 72, 77, 83, 88, 85, 83, 77])
    self.y = np.array([37, 32, 27, 27, 32, 37, 35, 35])
    # Shift to set initial position in screen:
    self.x += 40*(pos % 7)
    self.y += 30*((pos+7)/7)

    self.isAlive = True
    self.state = 0         # In formation (0) or released (1)
    self.dying_time = 6*10 # Time showing 'kaboom' message
    self.di = 0.15  # Fractional movement in formation
    self.k0 = 0.0   # Cumulative movement in formation
    self.k1 = 0     # Number of movement in same direction in formation

    self.sound_expl = pygame.mixer.Sound(c.explosion)
    # X direcction:
    self.dx = -1 if np.random.uniform() < 0.5 else 1
    # Text during death:
    font = pygame.font.Font(None, c.font_size_enemy)
    self.texto = font.render(c.death_msg.strip(), True, self.color)
    self.r = self.texto.get_rect()
    # Initiallize ammo:
    self.ammo = []
    for i in np.arange(self.n_ammo):
      self.ammo.append(bullet())

  def checkLimits(self):
    """
    Check if enemy is out of the screen boundaries:
    """
    # Left limit exeeded:
    if   self.x[4] < -1:
      self.x -=  self.x[4] - 1
      self.dx = -self.dx
    # Right limit exeeded:
    elif self.x[1] > c.screen_size[0] + 1:
      self.x -= self.x[1] - (c.screen_size[0] + 1)
      self.dx = -self.dx

  def update(self):
    """
    Update position
    
    During formation: add the fractional movement (k1) into k0 until k0 
    abs(k0) >= 1.  After 10 movements in the same direction, reverse the
    direction.
    """
    if self.isAlive:
      if   self.state == 0: # In formation
        self.k0 += self.di # charge k0 till get over 1
        if np.abs(self.k0) >= 1:
          self.x += int(self.k0) # Move
          self.k1 += 1      # Count the movements
          self.k0  = 0.0    # Reset k0
          if self.k1 == 10: # Change direction
            self.di = -self.di
            self.k1 -= self.k1

      elif self.state == 1: # Free movement
        if np.random.uniform() >= 0.98: # Change direction
          self.dx =-self.dx
        self.x += self.dx
        self.y += 1
        self.checkLimits()
        if self.y[2] > 450:
          self.y -= 466

    for weapon in self.ammo:
      if weapon.isAlive:
        weapon.move()

  def shoot(self, prob):
    """
    Determine if enemy will shoot and cretate the bullet in case of.

    Parameters:
    -----------
    prob: Probability of shooting
    """
    for i in np.arange(self.n_ammo):
      if self.isAlive and not self.ammo[i].isAlive:
        if np.random.uniform() < prob:
          # Initialize bullet at given position:
          self.ammo[i] = bullet((self.x[2] + self.x[3])/2, self.y[0] + 4)
          self.ammo[i].hooked = False

  def draw(self, screen):
    """
    Draw the enemy related graphs:
    """
    # Draw the enemy:
    if   self.isAlive:        
      pygame.draw.polygon(screen, self.color, zip(self.x, self.y), 1)
    # Draw 'Kaboom' message:
    elif self.dying_time > 0: 
      self.dying_time -= 1
      self.r.midtop = (self.x[1] + self.x[4])/2,  (self.y[2] + self.y[0])/2
      screen.blit(self.texto, self.r)
    # Draw the bullets:
    for weapon in self.ammo:    
      if weapon.isAlive:
        weapon.drawBullet(screen, c.bullet_color)
 
  def get_rect(self):
    return self.x[1], self.y[0], self.x[4], self.y[2]

  def kill(self):
    channel_exp = self.sound_expl.play()
    if channel_exp is not None:
      channel_exp.set_volume(0.7, 0.7)
    self.isAlive = False


class enemy1(enemy):
  def __init__(self, pos):
    self.n_ammo = 1
    self.color  = c.color_enemy1
    enemy.__init__(self, pos)


class enemy2(enemy):
  def __init__(self, pos):
    self.n_ammo = 2
    self.color  = c.color_enemy2
    enemy.__init__(self, pos)

  def shoot(self, prob):
    """
    Determine if enemy will shoot and cretate the bullet in case of.
    """
    for i in np.arange(self.n_ammo):
      if self.isAlive and not self.ammo[i].isAlive:
        if np.random.uniform() < prob:
          # Initialize bullet at given position:
          self.ammo[i] = bullet(self.x[1 + i*4], self.y[0] + 4)
          self.ammo[i].hooked = False


class starship:
  def __init__(self, nivel):
    self.x = np.array([193, 193, 193, 198, 200, 202, 207, 207, 207])
    self.y = np.array([424, 419, 423, 421, 410, 421, 423, 419, 424])
    self.dv = 0
    self.moving_l = False
    self.moving_r = False
    self.level = 6 - nivel
    self.lives = self.level
    self.isAlive = True
    self.hold = False
    self.ammo_holded = 0
    self.isdead = 6*12
    self.invincible = 0

    self.ammo =[[] for i in range(self.level)] # List of empty lists
    for i in range(len(self.ammo)):
      self.ammo[i] = bullet()

    self.special = [[[] for j in range(c.n_bombs)] for i in range(c.type_bombs)]
    for   i in range(c.type_bombs):
      for j in range(c.n_bombs):
        self.special[i][j] = bomb()

    font = pygame.font.Font(None, c.font_size_hero)
    self.texto = font.render(c.death_msg_hero.strip(),
                             True, c.color_hero)
    self.r = self.texto.get_rect()
    self.sound_doh = pygame.mixer.Sound(c.doh)

  def update(self):
    self.x += self.dv
    self.checkLimits()
    for i in range(len(self.ammo)):
      self.ammo[i].move(self.x[4])
    for   i in range(c.type_bombs):
      for j in range(c.n_bombs):
        self.special[i][j].move(self.x[4])

    if not self.isAlive:
      self.isdead -= 1
      self.r.midtop = self.x[4] - 5, 420
      if self.isdead == 0: # revive
        self.isdead = 6*12
        self.lives -= 1
        self.invincible = 3*12
        if self.lives != 0:
          self.isAlive = True

    if self.invincible > 0:
      self.invincible -= 1

  def stop(self):
    self.dv = 0
    self.moving_l = False
    self.moving_r = False

  def draw(self, screen):
    if self.isAlive:
      pygame.draw.polygon(screen, c.color_hero, zip(self.x, self.y), 1)
    else:
      screen.blit(self.texto, self.r)

    for weapon in self.ammo:
      if weapon.isAlive:
        weapon.drawBullet(screen)

    for i in range(c.type_bombs):
      for j in range(c.n_bombs):
        self.special[i][j].drawBomb(screen)

    for i in range(self.lives-1):
      pygame.draw.polygon(screen, c.color_hero,
                          zip(c.lives_x + i*c.delta_liv, c.lives_y), 1)

    # plot hit area
    # rec = self.get_rect()
    # pygame.draw.rect(screen, (255,255,255), (rec[0], rec[3], \
    #                     rec[2]-rec[0], rec[1]-rec[3]), 1)
    # rec = self.get_rect(True)
    # pygame.draw.rect(screen, (255,255,255), (rec[0], rec[3], \
    #                     rec[2]-rec[0], rec[1]-rec[3]), 1)

  def checkLimits(self):
    if self.x[0] < 1:
      self.x = np.array([1, 1, 1, 5, 8, 11, 15, 15, 15])
      self.stop()
    elif self.x[8] > c.screen_size[0]:
      self.x = np.array([385, 385, 385, 389, 392, 395, 399, 399, 399])
      self.stop()

  def kill(self):
    channel_doh = self.sound_doh.play()
    if channel_doh is not None:
      channel_doh.set_volume(0.4, 0.4)
    self.stop()
    self.hold = False
    self.ammo[self.ammo_holded].hooked = False
    self.isAlive = False

  def get_rect(self, lower=False):
    if not lower:
      return self.x[3], self.y[3], self.x[5], self.y[4]
    else:
      return self.x[0], self.y[0], self.x[8], self.y[1]


class bullet:
  def __init__(self, pos_x=-10, pos_y=-10):
    self.x = pos_x
    self.y = pos_y
    self.isAlive = True if not pos_x == -10 else False
    self.hooked = True

  def move(self, pos_x=None):
    if pos_x == None: # enemy
      self.y += 5
    else:             # hero
      if not self.hooked:
        self.y -= 5
      else:
        self.x = pos_x

    if self.y > c.screen_size[1] or self.y < 0:
      self.isAlive = False

  def drawBullet(self, screen, color=c.color_bullet ):
    pygame.draw.line(screen, color, (self.x, self.y), (self.x, self.y-5))

  def get_rect(self):
    return self.x, self.y, self.x , self.y - 4


class bomb:
  def __init__(self, pos_x=-1, pos_y=-1):
    self.x = pos_x
    self.y = pos_y
    self.isAlive = True if not pos_x == -1 else False
    self.status = 0 

  def move(self, pos_x):
    if self.status == 0: # Falling
      self.y += 2 
      if self.y > 450:
        self.isAlive = False 

    if self.status == 1: # Caught
      self.x = pos_x 
      self.y = 410 

  # def checkHit(x1, x2, y1, y2):
  #     return False

  # def checkHit(x1, x2, y1, y2, g):
  #     return False 

  # def drawBomb(Graphics g):
  #     if self.status == 0:
  #         g.drawRect(self.x-4, self.y-7, 8, 8) 

  def drawBomb(self, screen, color=c.color_bomb):
    if self.status == 0:
      pygame.draw.rect(screen, color, (self.x-4, self.y-7, 9, 9), 1)

  def changeStatus(self, i):
    self.status = i 

  def get_rect(self):
    return self.x-4, self.y+2, self.x+5, self.y-7


class laser(bomb):
  def __init__(self, pos_x, pos_y):
    bomb.__init__(self, pos_x, pos_y) 
    self.age    = 0 
    self.length = 2 
    self.sound = pygame.mixer.Sound(c.laser)
    font = pygame.font.Font(None, c.font_size_bomb)
    self.texto = font.render(("L").strip(), True, c.color_laser)
    self.r = self.texto.get_rect()

  def changeStatus(self, i):
    bomb.changeStatus(self, i) 
    if i == 3:
      self.length = 300 
      channel_laser = self.sound.play()
      if channel_laser is not None:
        channel_laser.set_volume(0.4, 0.4)

  def move(self, pos_x):
    bomb.move(self, pos_x) 
    if self.status == 2:
      self.age += 1 
      self.length = self.age/4 
      self.x = pos_x
      if self.age > 30:
        self.changeStatus(3)

    if self.status == 3:
      self.age += 1
      self.y -= 30
      if self.age > 50:
        self.status = -1
        self.isAlive = False

  def drawBomb(self, screen, color=c.color_laser):
    bomb.drawBomb(self, screen, color)
    if self.status == 0:
      self.r.midbottom = self.x-1, self.y+2
      screen.blit(self.texto, self.r)

    if self.status == 1:
      self.r.midtop = 310, 30
      screen.blit(self.texto, self.r)

    if self.status == 2 or self.status == 3:
      screen.fill( c.color_laser, 
                  (self.x-1, self.y-self.length-1, 2, self.length) )

  def check_hit(self, x1, y2, x2, y1):
    if self.status == 2 or self.status == 3:
      if (self.x-1 <= x2 and x1 <= self.x+1 and
          self.y-2 >= y1 and y2 >= self.y-self.length-1):
         self.changeStatus(3) 
         return True
    return False
  
  def checkHit(self, rect):
    return self.check_hit(rect[0],rect[1],rect[2],rect[3])


class rocket(bomb):
  def __init__(self, pos_x, pos_y):
    bomb.__init__(self, pos_x, pos_y)
    font = pygame.font.Font(None, c.font_size_hero)
    self.texto = font.render(("R").strip(), True, c.color_bomb)
    self.r = self.texto.get_rect()

  def move(self, pos_x):
    bomb.move(self, pos_x)
      
  def drawBomb(self, screen, color=c.color_bomb):
    if self.status == 0:
      pygame.draw.rect(screen, color, (self.x-4, self.y-7, 8, 8)) 
      self.r.midtop = self.x-2, self.y
      screen.blit(self.texto, self.r)

    if self.status == 1:
      self.r.midtop = 330, 30
      screen.blit(self.texto, self.r)

    if self.status == 2:
      pass
     
  def check_hit(self, x1, y2, x2, y1):
    return False

  def checkHit(self, rect):
    return self.check_hit(rect[0],rect[1],rect[2],rect[3])


class cluster(bomb):
  def __init__(self, pos_x, pos_y):
    bomb.__init__(self, pos_x, pos_y) 
    self.radius = 1 
    self.sound_blast = pygame.mixer.Sound(c.blast)
    self.sound_throw = pygame.mixer.Sound(c.bombfall)
    font = pygame.font.Font(None, c.font_size_bomb)
    self.texto = font.render(("C"), True, c.color_cluster)
    self.r = self.texto.get_rect()

  def changeStatus(self, i):
    bomb.changeStatus(self, i) 
    if i == 2:
      channel_throw = self.sound_throw.play()
      if channel_throw is not None:
        channel_throw.set_volume(0.4, 0.4)
    if i == 3:
      self.sound_throw.stop() 
      channel_blast = self.sound_blast.play()
          
  def move(self, pos_x):
    bomb.move(self, pos_x) 
    if self.status == 2:
      self.y -= 2 
      if self.y < 0:
        self.isAlive = False 

    if self.status == 3:
      self.radius += 1 

      if self.radius > 45:
        self.status = -1 
        self.isAlive = False 

  def drawBomb(self, screen, color=c.color_cluster):
    bomb.drawBomb(self, screen, color)
    if self.status == 0:
      self.r.midbottom = self.x, self.y+2
      screen.blit(self.texto, self.r)

    if self.status == 1:
      self.r.midtop = 320, 30
      screen.blit(self.texto, self.r)

    if self.status == 2:
      pygame.draw.ellipse(screen, c.color_cluster,
                         (self.x-1, self.y-3, 5, 6), 1 )

    if self.status == 3:
      pygame.draw.circle(screen, c.color_cluster, (self.x, self.y),
                         (self.radius/2 + 2), 3)
      pygame.draw.circle(screen, c.color_cluster, (self.x, self.y),
                         (self.radius/5 + 2), 2)
      
  def check_hit(self, x1, y2, x2, y1):
    if self.status == 2:
      if (self.x-1 <= x2 and self.x+1 >= x1 and
          self.y+3 >= y1 and self.y-2 <= y2 ):
        self.changeStatus(3) 
        return True 

    if self.status == 3:  
      if self.x < x1:
        if self.y < y1 or self.y > y2:
          if ((self.y-y1)**2 + (self.x-x1)**2 <= (self.radius/2.0)**2 or
              (self.y-y2)**2 + (self.x-x1)**2 <= (self.radius/2.0)**2 ):
            return True 
        elif self.x + self.radius/2.0 >= x1:
          return True 

      elif self.x <= x2:
        if ((self.y + self.radius/2.0 >  y1 and 
             self.y - self.radius/2.0 <= y1) or
            (self.y + self.radius/2.0 >  y2 and
             self.y - self.radius/2.0 <= y2) ):
          return True

      else:
        if self.y < y1 or self.y > y2:
          if ((self.y-y1)**2 + (self.x-x2)**2 <= (self.radius/2.0)**2 or
              (self.y-y2)**2 + (self.x-x2)**2 <= (self.radius/2.0)**2 ):
            return True 
            
        elif self.x - self.radius/2.0 <= x2:
          return True

    return False

  def checkHit(self, rect):
    return self.check_hit(rect[0], rect[1], rect[2], rect[3])
