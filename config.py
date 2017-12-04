from numpy import array
# If the game is too fast or too slow, try to modify the speed
# variables.

# Change these to use other images in the game:
background_image = './aux/ngc1300_hst_big.jpg'

# Fonts:
font = './aux/ProFontWindows.ttf'

# Sounds:
explosion = './aux/explosion.wav'
doh       = './aux/doh.wav'
laser     = './aux/laser.wav'
blast     = './aux/blast.wav'
bombfall  = './aux/bombfall.wav'

# General appearance:
screen_size = 400, 456
background_color = 0, 0, 0
bg_size = 800, 456
margin = 30
full_screen = 0
bullet_color = 255, 255, 255
# Background stars:
n_stars = 100  # Number
stars_vel = 4  # Maximum velocity
color_stars = 255, 255, 255 # Color: white

# Textos
font_size = 48
font_startUp_title = 18
font_startUp = 20
color_text = 210, 210, 210
title_x_pos  =  99
title_y_pos  = 120
title_deltaY =   0, 140, 180, 200
title_deltaX =   0,   5,   5,   5  
texto_x_pos  = 129
texto_y_pos  = 145
texto_deltaY =  20
cursor_x_pos = 105
cursor_y_pos = 125
cursor = ">>"

# stage and score font
waiting_time = int(58*2.5)
wait_size = 25
wait_color = 0, 0, 255
wait_position = screen_size[0]/2, screen_size[1]/2

scorex  =  30
scorey  = 250
scoredy =  20
color_score = 255, 255, 255
font_score = 15

# stage and score font
font_size_ss = 13
font_color_ss = 255, 255, 255
stage_position = 43, 9
score_position = 340, 15

# hi scores
scorefile = "hiscores.txt"

# frames per second
time_speed = 17
font_size_fps = 18
font_color_fps = 255, 0, 0
fps_position = 30, 440

# Enemy config
total_enemies = 28
font_size_enemy = 18
death_msg = 'Kaboom!'
color_enemy1 = 0, 255, 0
color_enemy2 = 0, 0, 255

# Hero config
velocity = 3
type_bombs = 2
n_bombs = 2
color_hero    = 255,   0,   0
color_bullet  = 255, 255,   0
color_bomb    = 255, 104,  31
color_laser   =   0, 191, 255
color_cluster = 255, 215,   0
font_size_hero = 18
font_size_bomb = 12
death_msg_hero = 'Kaboom!'
lives_x = array( [20, 20, 20, 23, 25, 27, 30, 30, 30] )
lives_y = array( [35, 32, 34, 33, 26, 33, 34, 32, 35] )
delta_liv = 15
	
