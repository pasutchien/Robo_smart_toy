import pygame
import sys
import time
import random
import serial
import math
pygame.init()
ser = serial.Serial('COM3', 9600)
received = ''
needsetup = True
available_players = set()


size = width, height = 480, 320
line_spacing = 30
line_thickness = 5

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
yellow = (255, 255, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

screen = pygame.display.set_mode(size)

mediumFont = pygame.font.Font("OpenSans-Regular.ttf", 28)
largeFont = pygame.font.Font("OpenSans-Regular.ttf", 40)
moveFont = pygame.font.Font("OpenSans-Regular.ttf", 60)

user = None
minigame = None

countdown_time = 300  # 5 minutes in seconds
minigame0_time = 31
minigame1_time = 21
updated_time = 0
time_to_play_minigame = 0
start_transition = 0
last_updated = 0
streak = 0
current_minigame = 1
frequency = [10,8,6,4]
# minigame 0 click

set_minigame0_count = 100
user_minigame0_count = 0
last_updated_mng0 = 0


# minigame 1 2-way toggle switch
player_blue_switch = 0
player_green_switch = 1
player_yellow_switch = 1
player_red_switch = 1

set_blue_switch = 1
set_green_switch = 1
set_yellow_switch = 1
set_red_switch = 1

#minigame 2 sin graph
value = 0
answer = 0
finished_time_minigame_2 = 0
finished_minigame_2 = False

#minigame 3
last_updated_mng3 = 0
finished = False
finished_time = 0
mng3_lose = False

print("serial.__version__ = {}".format(serial.__version__))
correct_blue = (player_blue_switch == set_blue_switch)
correct_green = (player_green_switch == set_green_switch)
correct_yellow = (player_yellow_switch == set_yellow_switch)
correct_red = (player_red_switch == set_red_switch)

colors_code = {"red": "1", "blue" : "2" , "green": "3", "yellow" :4}

# Draw toggle switches
#draw switch for minigame 1
def maprange( a, b, s):
    (a1, a2), (b1, b2) = a, b
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_obj, text_rect)
def draw_switches_initially():
    positions = {
        "red": (0.8*(60 + (0*133.33)), 0.8*(((height - line_spacing * 4) - 50)/2)),
        "blue": (0.8*(60 + (1*133.33)), 0.8*(((height - line_spacing * 4) - 50)/2)),
        "green": (0.8*(60 + (2*133.33)), 0.8*(((height - line_spacing * 4) - 50)/2)),
        "yellow": (0.8*(60 + (3*133.33)), 0.8*(((height - line_spacing * 4) - 50)/2))
    }
    for color in ["red", "blue", "green", "yellow"]:
        state = globals()[f"player_{color}_switch"]
        image_path = f"minigame1/{color}_{'up' if state else 'down'}.png"
        image = pygame.image.load(image_path).convert_alpha()
        resized_image = pygame.transform.scale(image, (image.get_width() // 2.5, image.get_height() // 2.5))
        screen.blit(resized_image, positions[color])
def draw_sin_graph(surface, x_offset, y_offset, width, height, answer, value,color=white, thickness=2, ):
    points = []
    for x in range(width):
        # Calculate y-coordinate for each x-coordinate using the sine function
        y = 0.5*(abs(answer-value)*(math.sin(math.radians(x / width * 360)) * (height / 2)))
        # Scale and shift the coordinates to fit inside the box
        x_scaled = x + x_offset
        y_scaled = int(y + y_offset)
        points.append((x_scaled, y_scaled))
    
    # Draw the graph
    pygame.draw.lines(surface, color, False, points, thickness)
#draw switch status (circle)
def draw_switch_status_circles():
    color_switch_positions = {
        "red": (0.8*(100 + (0 * 133.33)), 0.8*(((height - line_spacing * 4) + 150) / 2)),
        "blue": (0.8*(100 + (1 * 133.33)), 0.8*(((height - line_spacing * 4) + 150) / 2)),
        "green": (0.8*(100 + (2 * 133.33)), 0.8*(((height - line_spacing * 4) + 150) / 2)),
        "yellow": (0.8*(100 + (3 * 133.33)), 0.8*(((height - line_spacing * 4) + 150) / 2))
    }

    switch_status = {
        "red": correct_red,
        "blue": correct_blue,
        "green": correct_green,
        "yellow": correct_yellow
    }

    for color, position in color_switch_positions.items():
        status = switch_status[color]
        status_color = green if status else red
        circle_position = (position[0], (position[1] + 60))  # Adjust position as necessary
        pygame.draw.circle(screen, status_color, circle_position, 15)
class playerRed:
    def __init__(self,switch,potentio):
        if switch == "1sh":
            self.current_switch = 1
        else:
            self.current_switch = 0
        self.current_potentio = potentio
    def update(self, received):
        if received == '1s':
            if self.current_switch == 1:
                self.current_switch = 0
            else:
                self.current_switch = 1
        if '1p' in received:
            self.current_potentio = received
class playerBlue:
    def __init__(self,switch,potentio):
        if switch == "2sh":
            self.current_switch = 1
        else:
            self.current_switch = 0
        self.current_potentio = potentio
    def update(self, received):
        if received == '2s':
            if self.current_switch == 1:
                self.current_switch = 0
            else:
                self.current_switch = 1
        if '2p' in received:
            self.current_potentio = received
class playerGreen:
    def __init__(self,switch,potentio):
        if switch == "3sh":
            self.current_switch = 1
        else:
            self.current_switch = 0
        self.current_potentio = potentio
    def update(self, received):
        if received == '3s':
            if self.current_switch == 1:
                self.current_switch = 0
            else:
                self.current_switch = 1
        if '3p' in received:
            self.current_potentio = received
class playerYellow:
    def __init__(self,switch,potentio):
        if switch == "4sh":
            self.current_switch = 1
        else:
            self.current_switch = 0
        self.current_potentio = potentio
    def update(self, received):
        if received == '4s':
            if self.current_switch == 1:
                self.current_switch = 0
            else:
                self.current_switch = 1
        if '4p' in received:
            self.current_potentio = received

class Button(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, color):
        super().__init__()
        self.sprites = []
        if color == 'grey':
            original_image = pygame.image.load(f'button/grey/grey.gif')
            self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2.5, original_image.get_height() // 2.5)))
        else:
            for i in range(9):  # Assuming you have example0.gif to example12.5.gif
                original_image = pygame.image.load(f'button/{color}/frame_{i}_delay-0.01s.gif')
                self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2.5, original_image.get_height() // 2.5)))
        #original_image = pygame.image.load(f'button/{color}/{color}.jpg')
        self.index = 0  # Index to track which sprite to display    
        self.image = self.sprites[self.index]
        if color == "grey":
            self.correct = True
        else:
            self.correct = False

        self.check = str(colors_code[color])+'b'
        self.rect = self.image.get_rect(center=(pos_x, pos_y))
    

    def update(self):
        self.index = (self.index + 1) % len(self.sprites)  # Cycle through sprites
        self.image = self.sprites[self.index]
        if self.correct == True:
            self.sprites = []
            original_image = pygame.image.load(f'button/grey/grey.gif')
            self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2.5, original_image.get_height() // 2.5)))
        #time.sleep(0.2.5)
class Joy(pygame.sprite.Sprite):
    def __init__(self,pos_x,pos_y,color,position):
        super().__init__()
        self.sprites = []
        if color == 'grey':
            original_image = pygame.image.load(f'joy/grey/grey.gif')
            self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2.5, original_image.get_height() // 2.5)))
        
        else:
            for i in range(11):  # Assuming you have example0.gif to example12.gif
                if position == 'u':
                    pos = 'up'
                elif position == 'd':
                    pos = 'down'
                elif position == 'l':
                    pos = 'left'
                else:
                    pos = 'right'
                if i < 10:
                    original_image = pygame.image.load(f'joy/{color}/{pos}/frame_0{i}_delay-0.01s.gif')
                else:
                    original_image = pygame.image.load(f'joy/{color}/{pos}/frame_{i}_delay-0.01s.gif')
                self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2.5, original_image.get_height() // 2.5)))
        self.index = 0  # Index to track which sprite to display
        self.image = self.sprites[self.index]
        self.rect = self.image.get_rect(center=(pos_x, pos_y))
        if color == 'red':
            self.correct = True
        elif color == 'grey':
            self.correct = True
        else:
            self.correct = False
        self.check = str(colors_code[color]) + 'j' + position


    def update(self):
        self.index = (self.index + 1) % len(self.sprites)  # Cycle through sprites
        self.image = self.sprites[self.index]
        if self.correct == True:
            self.sprites = []
            original_image = pygame.image.load(f'joy/grey/grey.gif')
            self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2.5, original_image.get_height() // 2.5)))
        #time.sleep(0.2.5)
class Potentio(pygame.sprite.Sprite):
    def __init__(self,pos_x,pos_y,color,position):
        super().__init__()
        self.sprites = []
        if color == 'grey':
            original_image = pygame.image.load(f'potentio/grey/grey.gif')
            self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2.5, original_image.get_height() // 2.5)))
        else:
            if position == 'l' or position == 'h':
                if position == 'l':
                    text = 'right'
                else:
                    text = 'left'
                for i in range(11):  # Assuming you have example0.gif to example12.gif
                    if i < 10:
                        original_image = pygame.image.load(f'potentio/{color}/{text}/frame_0{i}_delay-0.01s.gif')
                    else:
                        original_image = pygame.image.load(f'potentio/{color}/{text}/frame_{i}_delay-0.01s.gif')
                    self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2.5, original_image.get_height() // 2.5)))
            else:
                original_image = pygame.image.load(f'potentio/{color}/mid/{color[0]}mid.png')
                self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2.5, original_image.get_height() // 2.5)))
        self.index = 0  # Index to track which sprite to display
        self.image = self.sprites[self.index]
        self.rect = self.image.get_rect(center=(pos_x, pos_y))
        if color == 'grey':
            self.correct = True
        else:
            self.correct = False
        self.check = str(colors_code[color]) + 'p' + position

    def update(self):
        self.index = (self.index + 1) % len(self.sprites)  # Cycle through sprites
        self.image = self.sprites[self.index]
        if self.correct == True:
            self.sprites = []
            original_image = pygame.image.load(f'potentio/grey/grey.gif')
            self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2.5, original_image.get_height() // 2.5)))
        #time.sleep(0.2.5)
class Switch(pygame.sprite.Sprite):
    def __init__(self,pos_x,pos_y,color):
        super().__init__()
        self.sprites = []
        if color == 'grey':
            original_image = pygame.image.load(f'switch/grey/grey.gif')
            self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2.5, original_image.get_height() // 2.5)))
        else:
            for i in range(16):  # Assuming you have example0.gif to example12.5.gif
                if i < 10:
                    original_image = pygame.image.load(f'switch/{color}/frame_0{i}_delay-0.01s.gif')
                else:
                    original_image = pygame.image.load(f'switch/{color}/frame_{i}_delay-0.01s.gif')
                self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2.5, original_image.get_height() // 2.5)))
        self.index = 0  # Index to track which sprite to display
        self.image = self.sprites[self.index]
        self.rect = self.image.get_rect(center=(pos_x, pos_y))
        if color == 'grey':
            self.correct = True
        else:
            self.correct = False
        self.check = str(colors_code[color]) + 's'
        
        
    def update(self):
        self.index = (self.index + 1) % len(self.sprites)  # Cycle through sprites
        self.image = self.sprites[self.index]
        #time.sleep(0.2)
        if self.correct == True:
            self.sprites = []
            original_image = pygame.image.load(f'switch/grey/grey.gif')
            self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2.5, original_image.get_height() // 2.5)))
class Bomb(pygame.sprite.Sprite):
    def __init__(self,pos_x,pos_y):
        super().__init__()
        self.sprites = []
        for i in range(23):
            if i < 10:
                original_image = pygame.image.load(f'minigame3/frame_0{i}_delay-0.03s.gif')
            else:
                original_image = pygame.image.load(f'minigame3/frame_{i}_delay-0.03s.gif')
            self.sprites.append(original_image)
        self.index = 0
        self.image = self.sprites[self.index]
        self.rect = self.image.get_rect(center=(pos_x, pos_y))
    def update(self):
        self.index = (self.index + 1) % len(self.sprites) 
        self.image = self.sprites[self.index]
class Monster(pygame.sprite.Sprite):
    def __init__(self,pos_x,pos_y):
        super().__init__()
        self.sprites = []
        for i in range(13):
            if i < 10:
                original_image = pygame.image.load(f'minigame0/frame_0{i}_delay-0.01s.gif')
            else:
                original_image = pygame.image.load(f'minigame0/frame_{i}_delay-0.01s.gif')
            self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width()//1.5, original_image.get_height()//1.5 )))
        self.index = 0
        self.image = self.sprites[self.index]
        self.rect = self.image.get_rect(center=(pos_x, pos_y))
    def update(self):
        self.index = (self.index + 1) % len(self.sprites) 
        self.image = self.sprites[self.index]

monster = Monster(width // 2 , height // 2.1)
all_sprites_mng0 = pygame.sprite.Group([monster])
def random_input(available_players):

    sprite = []
    color = list(available_players)
    for i in range(4):
        random_color = random.choice(color)
        if random_color == 'red':
            item = [0,2,3]
            random_item = random.choice(item)
        elif random_color == 'yellow':
            item = [0,3]
            random_item = random.choice(item)
        elif random_color == 'green':
            item = [0,1,2]
            random_item = random.choice(item)
        else:
            random_item = random.randint(0,3)
        if random_item == 0:
            button = Button(0.8*(100 + (i*133.33)), 1.2*(((height - line_spacing * 4) - 10)/2),random_color)
            sprite.append(button)
        if random_item == 1:
            positions = ['l','r','u','d']
            random_position = random.randint(0,3)
            joy = Joy(0.8*(100 + (i*133.33)), 1.2*(((height - line_spacing * 4) - 10)/2),random_color,positions[random_position])
            sprite.append(joy)
        if random_item == 2:
            positions = ['l','m','h']
            random_position = random.randint(0,2)
            potentio = Potentio(0.8*(100 + (i*133.33)), 1.2*(((height - line_spacing * 4) - 10)/2),random_color,positions[random_position])
            sprite.append(potentio)
        if random_item == 3:
            switch = Switch(0.8*(100 + (i*133.33)), 1.2*(((height - line_spacing * 4) - 10)/2),random_color)
            sprite.append(switch)
    
    return sprite
def random_minigame3():
    sprite_mng3 = []
    color = list(available_players)
    positions = ['l','r','u','d']
    for i in range(4):
        random_color = random.choice(color)
        random_position = random.choice(positions)
        color.remove(random_color)
        if i == 0:
            joy = Joy(45, 45,random_color,random_position)
        elif i == 1:
            joy = Joy(width-45, 45,random_color,random_position)
        elif i == 2:
            joy = Joy(45, height-45,random_color,random_position)
        else:
            joy = Joy(width - 45, height-45,random_color,random_position)
        sprite_mng3.append(joy)
        if not color:
            color = list(available_players)
    return sprite_mng3


def random_minigame():
    random_number = random.randint(0, 1)
    return random_number
time.sleep(3)
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ser.close()
            sys.exit()

    screen.fill(black)
    if user == 'win':
        #you win
        draw_text('You Win!', largeFont, red, screen, width // 2, height // 3)
        
        # Load the image (do this once, at the beginning of your script)
        playagain_image = pygame.image.load('playagainred.png')
        playagain_image = pygame.transform.scale(playagain_image, (200, 50))  # Scale the image to the size of the button

        # Define the button rectangle
        try_again_button = pygame.Rect(width // 2 - 100, height // 2, 200, 50)

        # Draw the button (you can skip drawing the rectangle if you only want to show the image)
        # pygame.draw.rect(screen, green, try_again_button)
        
        # Draw the image
        screen.blit(playagain_image, (try_again_button.x, try_again_button.y))

        needsetup = True
        
        if ser.in_waiting > 0:
            received = ser.readline().decode('utf-8').rstrip()
            if received[1] == 'b':
                user = None  # Reset the game state   
                time.sleep(3)

    # Let user choose a player.
    elif user is None:
#--------------------------receive initial state of each joy---------------------------
        if needsetup:
            ser.write("Need set up\n".encode())
        if ser.in_waiting > 0:
            received = ser.readline().decode('utf-8').rstrip()
            print(received)
            if received:
                if received[0] == "!":
                    received = received[1:]
                    players = received[:-1].split('/')
                    # print(players)
                    players = [player.strip() for player in players]
                    for player in players:
                        items = player.split(' ') #assume switch first then potentio
                        if items[0][0] == '1':
                            playerred = playerRed(items[0],items[1])
                            available_players.add("red")
                        if items[0][0] == '2':
                            playerblue = playerBlue(items[0],items[1])
                            available_players.add("blue")
                        if items[0][0] == '3':
                            playergreen = playerGreen(items[0],items[1])
                            available_players.add("green")
                        if items[0][0] == '4':
                            playeryellow = playerYellow(items[0],items[1])
                            available_players.add("yellow")
                else:
                    if received[1] == 'b':
                        user = "in"  # Assuming user chooses "X" as their symbol
                        ai_turn = True  # Now it's AI's turn
                        life = 4
                        start_time = time.time()
                        change_input =  True
                        start = 0
                        updated_time = time.time()
                        last_updated = time.time()
                        needsetup = False
                        sprite = random_input(available_players)
                        all_sprites = pygame.sprite.Group(sprite)
                        print(available_players)
                        streak = 0
                        current_minigame = 0
                        time_to_play_minigame = 0
        start_image = pygame.image.load('start.png')
        scaled_width = 240  # Adjust the width as needed
        scaled_height = 160  # Adjust the height as needed
        start_image = pygame.transform.scale(start_image, (scaled_width, scaled_height))

        # Calculate position to center the image on the screen
        button_x = (width - scaled_width) // 2
        button_y = (height - scaled_height) // 2

        # Create a rect for the start button (optional, for collision detection)
        start_button = pygame.Rect(button_x, button_y, scaled_width, scaled_height)
        screen.blit(start_image, (button_x, button_y))


    elif user == 'lose':
        screen.fill(black)
        draw_text('You lose!', largeFont, red, screen, width // 2, height // 3)
        
        # Load the image (do this once, at the beginning of your script)
        playagain_image = pygame.image.load('playagain.png')
        playagain_image = pygame.transform.scale(playagain_image, (200, 50))  # Scale the image to the size of the button

        # Define the button rectangle
        try_again_button = pygame.Rect(width // 2 - 100, height // 2, 200, 50)

        # Draw the button (you can skip drawing the rectangle if you only want to show the image)
        # pygame.draw.rect(screen, green, try_again_button)
        
        # Draw the image
        screen.blit(playagain_image, (try_again_button.x, try_again_button.y))
        needsetup = True
        if ser.in_waiting > 0:
            received = ser.readline().decode('utf-8').rstrip()
            if received[1] == 'b':
                user = None  # Reset the game state   
                time.sleep(3)

    else:
    # Display countdown timer
        if minigame == None:
            for i in range(4):
                if sprite[i].correct == False:
                    break
            if isinstance(sprite[i],Potentio):
                if sprite[i].check[0] == '1':
                    if playerred.current_potentio == sprite[i].check:
                        sprite[i].correct = True
                elif sprite[i].check[0] == '2':
                    if playerblue.current_potentio == sprite[i].check:
                        sprite[i].correct = True
                elif sprite[i].check[0] == '3':
                    if playergreen.current_potentio == sprite[i].check:
                        sprite[i].correct = True
                else:
                    if playeryellow.current_potentio == sprite[i].check:
                        sprite[i].correct = True
            if ser.inWaiting():
                received = ser.readline().decode('utf-8').rstrip() 
                if received[0] == '1':
                    playerred.update(received)
                if received[0] == '2':
                    playerblue.update(received)
                if received[0] == '3':
                    playergreen.update(received)
                if received[0] == '4':
                    playeryellow.update(received)
                if sprite:               
                    if not isinstance(sprite[i],Potentio):
                        if isinstance(sprite[i],Joy):
                            if len(received) >= 3:
                                if received[2] == 'n':
                                    received = received[:-1]
                                    received = received + 'ul'
                                if received[2] == 'e':
                                    received = received[:-1]
                                    received = received + 'ur'
                                if received[2] == 'w':
                                    received = received[:-1]
                                    received = received + 'dl'
                                if received[2] == 's':
                                    received = received[:-1]
                                    received = received + 'dr'            
                                print(received)
                                if sprite[i].check in received:
                                    sprite[i].correct = True
                        else:
                            if sprite[i].check == received:
                                sprite[i].correct = True            
                    
                    
            elapsed_time = (time.time() - start_time) - time_to_play_minigame
            interval = time.time() - updated_time
            if int(elapsed_time - start) == 1:
                change_input = True
            remaining_time = max(0, countdown_time - elapsed_time) 
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            countdown_text = mediumFont.render(f"{minutes:02}:{seconds:02}", True, white)
            screen.blit(countdown_text, (10, 10))  # Display at top left corner
            
            life_text = mediumFont.render("Life:", True, white)
            life_text_rect = life_text.get_rect(topright=(width - 180, 10))
            screen.blit(life_text, life_text_rect)
            for i in range(life):
                pygame.draw.circle(screen, red, (width - 30 - i * 40, 32), 10)
        
            colors = ['red','blue','green','yellow']
            for i in range(4):
                color = colors[i]
                if i < current_minigame:
                    line = pygame.image.load(f'wire/blank.png')
                    line_rect = line.get_rect()
                    line_rect.midbottom = (width//2,375+i*25)
                    screen.blit(line, line_rect)
                else:
                    line = pygame.image.load(f'wire/{color[0]}_wire.png')
                    line_rect = line.get_rect()
                    line_rect.midbottom = (width//2,375+i*25)
                    screen.blit(line, line_rect)
            if life == 0 or remaining_time <= 0:#lose
                user = 'lose'
                
            if sprite[0].correct and sprite[1].correct and sprite[2].correct and sprite[3].correct:
                sprite = random_input(available_players)
                all_sprites = pygame.sprite.Group(sprite)
                change_input = False
                start = elapsed_time
                streak += 1
            elif elapsed_time - start >= frequency[current_minigame] and change_input == True:
                sprite = random_input(available_players)
                all_sprites = pygame.sprite.Group(sprite)
                change_input = False
                start = elapsed_time
                life -= 1
                streak = 0
            if time.time() - last_updated > 0.2:
                all_sprites.update()
                last_updated = time.time()
            all_sprites.draw(screen)
            if streak == 5: 
                minigame = -999
                #time.sleep(1)
                start_transition = time.time()
                user_minigame0_count = 0
                player_blue_switch = 0
                player_green_switch = 0
                player_yellow_switch = 0
                player_red_switch = 0
                streak = 0

 
        if minigame == -999:
            if ser.inWaiting():
                received = ser.readline().decode('utf-8').rstrip() 
                if received[0] == '1':
                    playerred.update(received)
                if received[0] == '2':
                    playerblue.update(received)
                if received[0] == '3':
                    playergreen.update(received)
                if received[0] == '4':
                    playeryellow.update(received)
            elapsed_time = time.time() - start_transition
            #RIght it here
            remaining_time = max(0, 4 - elapsed_time) 
            font = pygame.font.Font(None, 36)  # Choose a font and size
            text = font.render(f"Starting minigame in {int(remaining_time)}", True, white)  # Render the text
            text_rect = text.get_rect(center=(width // 2, height // 2))
            screen.blit(text, text_rect)

            if remaining_time <= 0:
                #minigame = current_minigame
                minigame = current_minigame
                colors = ["red","yellow","green","blue"]
                if minigame == 0:
                    last_updated_mng0 = time.time()
                if minigame == 1:
                    for color in colors:
                        number = random.randint(0,1)
                        globals()[f"set_{color}_switch"] = number
                    correct_blue = (player_blue_switch == set_blue_switch)
                    correct_green = (player_green_switch == set_green_switch)
                    correct_yellow = (player_yellow_switch == set_yellow_switch)
                    correct_red = (player_red_switch == set_red_switch)
                finished = False
                if minigame == 2:
                    answer = random.randint(0,255)
                    ser.write("minigame2\n".encode())
                    finished_minigame_2 = False
                time_to_play_minigame += elapsed_time
                start_minigame_time = time.time()
                if minigame == 3:
                    mng3_lose = False
                    sprites_mng3 = random_minigame3()
                    bomb = Bomb(width//2, height//2)
                    sprites_mng3.append(bomb)
                    all_sprites_mng3 = pygame.sprite.Group(sprites_mng3)
                    last_updated_mng3 = time.time()
                    
                    
        
        
        if minigame == 0:
            elapsed_time = time.time() - start_minigame_time
            remaining_time = max(0, minigame0_time - elapsed_time)
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            countdown_text = mediumFont.render(f"{minutes:02}:{seconds:02}", True, white)
            screen.blit(countdown_text, (10, 10))  # Display at top left corner

            # Display user and set minigame 0 counts
            text_color = (255,255,255)
            font = pygame.font.Font(None, 40)
            count_text = f"{user_minigame0_count} / {set_minigame0_count}"
            count_surface = font.render(count_text, True, text_color)
            count_rect = count_surface.get_rect()
            count_rect.center = (width // 2, (height // 2) +100)
            
            screen.blit(count_surface, count_rect)

            #button_icon = pygame.image.load('grey.png')  # Replace "path" with the actual path
            #scaled_button_icon = pygame.transform.scale(button_icon, (width // 3, height // 2.5))  # Adjust the scaling factor as needed
            # Set the position of the button icon
            #button_icon_rect = scaled_button_icon.get_rect()
            #button_icon_rect.center = (width // 2 - 100, height // 2.1)  # Adjust the position as needed
            # Blit the scaled button icon onto the screen
            #screen.blit(scaled_button_icon, button_icon_rect)
            if ser.inWaiting():
                received = ser.readline().decode('utf-8').rstrip() 
                if received[0] == '1':
                    playerred.update(received)
                if received[0] == '2':
                    playerblue.update(received)
                if received[0] == '3':
                    playergreen.update(received)
                if received[0] == '4':
                    playeryellow.update(received)
                if received[1] == 'b':
                    user_minigame0_count += 1
                if user_minigame0_count >= set_minigame0_count:
                    ser.write("win0\n".encode())
                    minigame = None
                    updated_time = time.time()
                    time_to_play_minigame += elapsed_time
                    current_minigame += 1

            # Handle mouse events
            if time.time() - last_updated_mng0 >= 0.2:
                all_sprites_mng0.update()
                last_updated_mng0 = time.time()
            if remaining_time <= 0: #lose
                minigame = None
                updated_time = time.time()
                life -= 1
                time_to_play_minigame += elapsed_time
            all_sprites_mng0.draw(screen)


        if minigame == 1:
            ser.write("minigame1\n".encode())

            elapsed_time = time.time() - start_minigame_time
            remaining_time = max(0, minigame1_time - elapsed_time)
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            countdown_text = mediumFont.render(f"{minutes:02}:{seconds:02}", True, white)
            screen.blit(countdown_text, (10, 10))  # Display at top left corner
            if ser.inWaiting():
                received = ser.readline().decode('utf-8').rstrip() 
                print(received)
                if received[0] == '1':
                    playerred.update(received)
                if received[0] == '2':
                    playerblue.update(received)
                if received[0] == '3':
                    playergreen.update(received)
                if received[0] == '4':
                    playeryellow.update(received)
                if received[0] == '@':
                    received = received[1:]
                    players = received.split('/')
                    players = [player.strip() for player in players]
                    for player in players:
                        if player == '1sh':
                            player_red_switch = 1
                        elif player == '1sl':
                            player_red_switch = 0
                        if player == '2sh':
                            player_blue_switch = 1
                        elif player == '2sl':
                            player_blue_switch = 0
                        if player == '3sh':
                            player_green_switch = 1
                        elif player == '3sl':
                            player_green_switch = 0
                        if player == '4sh':
                            player_yellow_switch = 1
                        elif player == '4sl':
                            player_yellow_switch = 0
    
            for color in ["red","blue","green","yellow"]:
                if color not in available_players:
                    globals()[f"player_{color}_switch"] = globals()[f"set_{color}_switch"]
            globals()[f"player_green_switch"]= globals()[f"set_green_switch"]
            correct_blue = (player_blue_switch == set_blue_switch)
            correct_green = (player_green_switch == set_green_switch)
            correct_yellow = (player_yellow_switch == set_yellow_switch)
            correct_red = (player_red_switch == set_red_switch)


            draw_switches_initially()
            draw_switch_status_circles()
            # Check if all switches are correctly toggled
            if correct_blue  and correct_green and correct_yellow and correct_red and finished == False:
                # All switches match, mini-game completed
                finished_time = time.time()
                finished = True

            if time.time()-finished_time > 0.2 and finished == True:
                ser.write("win1\n".encode())
                minigame = None
                updated_time = time.time()
                time_to_play_minigame += elapsed_time
                finished = False
                current_minigame += 1
            if remaining_time <= 0:
                minigame = None
                updated_time = time.time()
                life -=1
                time_to_play_minigame += elapsed_time
                finished = False
   
    
        if minigame == 2:
            CENTER_X, CENTER_Y = width // 2, height // 2
            print("answer" + str(answer))
            # Draw the box
            box_width = 480
            box_height = 100 # input value right here (put this )
            box_x, box_y = CENTER_X - box_width // 2, (CENTER_Y - box_height // 2) - 100
            if ser.in_waiting > 0:
                received = ser.readline().decode('utf-8').rstrip()
                print("received = "+ received)
                if received != '' and received[0] == '#' and finished_minigame_2 == False: #ต้องมี sign
                    received = received[1:-1]
                    value = 0 
                    players = received.split('/')
                    # print(players)
                    players = [player.strip() for player in players]
                    for player in players:
                        temp = int(player[2:])
                        if player[0] == 1:
                            if temp < 341:
                                u = '1pl'
                            elif temp > 682:
                                u = '1ph'
                            else:
                                u = '1pm'
                            playerred.update(u)
                        elif player[0] == 2:
                            if temp < 341:
                                u = '2pl'
                            elif temp > 682:
                                u = '2ph'
                            else:
                                u = '2pm' 
                            playerblue.update(u)
                        elif player[0] == 3:
                            if temp < 341:
                                u = '3pl'
                            elif temp > 682:
                                u = '3ph'
                            else:
                                u = '3pm' 
                            playergreen.update(u)
                        elif player[0] == 4:
                            if temp < 341:
                                u = '4pl'
                            elif temp >682:
                                u = '4ph'
                            else:
                                u = '4pm'
                            playeryellow.update(u)         
                        temp = maprange((0,1023),(0,255),temp)
                        print(temp)
                        value += int(temp)
                    value = value/len(players)
            


            elapsed_time = time.time() - start_minigame_time
            remaining_time = max(0, minigame1_time - elapsed_time)
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            countdown_text = mediumFont.render(f"{minutes:02}:{seconds:02}", True, white)
            screen.blit(countdown_text, (10, 10))  # Display at top left corner


            # pygame.draw.rect(screen, black, (box_x, box_y, box_width, box_height), 2)
#def draw_sin_graph(surface, x_offset, y_offset, width, height, answer, value,color=white, thickness=2, ):

            # Draw the sin graph inside the box
            draw_sin_graph(screen, box_x, CENTER_Y, box_width, box_height, answer,value,white) # box_width and box_height are the dimension of sin graph

            if answer == value and finished_minigame_2 == False:
                finished_time_minigame_2 = time.time()
                finished_minigame_2 = True

            if time.time() - finished_time_minigame_2 >= 1 and finished_minigame_2 == True:
                ser.write("win2\n".encode())
                minigame = None
                updated_time = time.time()
                time_to_play_minigame += elapsed_time
                current_minigame += 1  
                ser.write("end2\n".encode())
                finished_minigame_2 = False
    
            if remaining_time <= 0: #lose
                minigame = None
                updated_time = time.time()
                life -= 1
                time_to_play_minigame += elapsed_time
                ser.write("end2\n".encode())
                finished_minigame_2 = False
        if minigame == 3:
            elapsed_time = time.time() - start_minigame_time
            remaining_time = max(0, minigame1_time - elapsed_time)
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            # countdown_text = mediumFont.render(f"{minutes:02}:{seconds:02}", True, white)
            # screen.blit(countdown_text, (width // 2 - 145, 20))  # Display at top left corner
            
            CENTER_X, CENTER_Y = width // 2, height // 2
            
            
            # Define positions for each Joy color
            joy_positions = {
                "red": (45, 45), # Top left
                "yellow": (width - 45, 45),  # Top right
                "green": (45, height - 45),  # Bottom left
                "blue": (width - 45, height - 45)  # Bottom right
            }
            #joy = Joy(100 + (i*133.33), ((height - line_spacing * 4) - 10)/2,color[random_color])
            
            #idk what to call this
            # for colour, position in joy_positions.items():
            #     # Check the state of each switch to determine which image to load
            #     globals()[f"joy_{color}"] = Joy((position[0], position[1])/2,color[colour])
            if ser.inWaiting():
                received = ser.readline().decode('utf-8').rstrip() 
                if received[0] == '1':
                    playerred.update(received)
                if received[0] == '2':
                    playerblue.update(received)
                if received[0] == '3':
                    playergreen.update(received)
                if received[0] == '4':
                    playeryellow.update(received)
                if sprites_mng3:               
                    for i in range(0,len(sprites_mng3)-1):
                        if received[1] == 'j':
                            if received[2] == 'n':
                                received = received[:-1]
                                received = received + 'dr'
                            if received[2] == 'e':
                                received = received[:-1]
                                received = received + 'dl'
                            if received[2] == 'w':
                                received = received[:-1]
                                received = received + 'ur'
                            if received[2] == 's':
                                received = received[:-1]
                                received = received + 'ul'            
                            if received[2] == 'u':
                                received = received[:-1]
                                received = received + 'd'
                            if received[2] == 'd':
                                received = received[:-1]
                                received = received + 'u'
                            if received[2] == 'l':
                                received = received[:-1]
                                received = received + 'r'
                            if received[2] == 'r':
                                received = received[:-1]
                                received = received + 'l'
                            if sprites_mng3[i].check in received:
                                sprites_mng3[i].correct = True
            
            # Load and display Joy sprites at defined positions
            if time.time() - last_updated_mng3 >= 0.2:
                all_sprites_mng3.update()
                last_updated_mng3 = time.time()
            if sprites_mng3[0].correct and sprites_mng3[1].correct and sprites_mng3[2].correct and sprites_mng3[3].correct and mng3_lose == False:
                ser.write("win3\n".encode())
                minigame = None
                updated_time = time.time()
                time_to_play_minigame += elapsed_time
                current_minigame += 1  
                mng3_lose = False
                user = 'win'
            if sprites_mng3[4].index == 14 and mng3_lose == False:
                sprites_mng3[0].correct = True
                sprites_mng3[1].correct = True
                sprites_mng3[2].correct = True
                sprites_mng3[3].correct = True
                mng3_lose = True
            if mng3_lose and sprites_mng3[4].index == 22:
                minigame = None
                updated_time = time.time()
                life -=1
                time_to_play_minigame += elapsed_time
                finished = False
   

            all_sprites_mng3.draw(screen)
    # Update the screen
    mirrored_screen = pygame.transform.flip(screen, False, True)
    screen.blit(mirrored_screen, (0, 0))

    pygame.display.flip()
    


#เพิ่ม Speed หลังจบ minigame (checked)
#ปุ่ม Start
#หน้า Victory ปุ่ม Play again
#หน้า lose ปุ่ม retry
#การเริ่มเกม (กดปุ่ม) (checked)