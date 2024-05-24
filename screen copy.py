import pygame
import sys
import time
import random
import serial

pygame.init()
ser = serial.Serial('COM3', 9600)
received = ''
needsetup = True
available_players = set()

size = width, height = 600, 400
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
# minigame 0 click
set_minigame0_count = 20
user_minigame0_count = 0


# minigame 1 2-way toggle switch
player_blue_switch = 0
player_green_switch = 1
player_yellow_switch = 1
player_red_switch = 1

set_blue_switch = 1
set_green_switch = 1
set_yellow_switch = 1
set_red_switch = 1

finished = False
finished_time = 0


correct_blue = (player_blue_switch == set_blue_switch)
correct_green = (player_green_switch == set_green_switch)
correct_yellow = (player_yellow_switch == set_yellow_switch)
correct_red = (player_red_switch == set_red_switch)

colors_code = {"red": "1", "blue" : "2" , "green": "3", "yellow" :4}
# Draw toggle switches
#draw switch for minigame 1
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_obj, text_rect)
def draw_switches_initially():
    positions = {
        "blue": (60 + (0*133.33), ((height - line_spacing * 4) - 50)/2),
        "green": (60 + (1*133.33), ((height - line_spacing * 4) - 50)/2),
        "yellow": (60 + (2*133.33), ((height - line_spacing * 4) - 50)/2),
        "red": (60 + (3*133.33), ((height - line_spacing * 4) - 50)/2)
    }
    for color in ["blue", "green", "yellow", "red"]:
        state = globals()[f"player_{color}_switch"]
        image_path = f"minigame1/{color}_{'up' if state else 'down'}.png"
        image = pygame.image.load(image_path).convert_alpha()
        resized_image = pygame.transform.scale(image, (image.get_width() // 2, image.get_height() // 2))
        screen.blit(resized_image, positions[color])

#draw switch status (circle)
def draw_switch_status_circles():
    color_switch_positions = {
        "red": (100 + (0 * 133.33), ((height - line_spacing * 4) + 150) / 2),
        "yellow": (100 + (1 * 133.33), ((height - line_spacing * 4) + 150) / 2),
        "green": (100 + (2 * 133.33), ((height - line_spacing * 4) + 150) / 2),
        "blue": (100 + (3 * 133.33), ((height - line_spacing * 4) + 150) / 2)
    }

    switch_status = {
        "red": (player_red_switch == set_red_switch),
        "yellow": (player_yellow_switch == set_yellow_switch),
        "green": (player_green_switch == set_green_switch),
        "blue": (player_blue_switch == set_blue_switch)
    }

    for color, position in color_switch_positions.items():
        status = switch_status[color]
        status_color = green if status else red
        circle_position = (position[0], position[1] + 60)  # Adjust position as necessary
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
            self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2, original_image.get_height() // 2)))
        else:
            for i in range(9):  # Assuming you have example0.gif to example12.gif
                original_image = pygame.image.load(f'button/{color}/frame_{i}_delay-0.01s.gif')
                self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2, original_image.get_height() // 2)))
        #original_image = pygame.image.load(f'button/{color}/{color}.jpg')
        self.index = 0  # Index to track which sprite to display
        self.image = self.sprites[self.index]
        if color == "grey":
            self.correct = True
        else:
            self.correct = False

        self.check = colors_code[color]+'b'
        self.rect = self.image.get_rect(center=(pos_x, pos_y))
    

    def update(self):
        self.index = (self.index + 1) % len(self.sprites)  # Cycle through sprites
        self.image = self.sprites[self.index]
        if self.correct == True:
            self.sprites = []
            original_image = pygame.image.load(f'button/grey/grey.gif')
            self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2, original_image.get_height() // 2)))
        #time.sleep(0.2)
class Joy(pygame.sprite.Sprite):
    def __init__(self,pos_x,pos_y,color,position):
        super().__init__()
        self.sprites = []
        if color == 'grey':
            original_image = pygame.image.load(f'joy/grey/grey.gif')
            self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2, original_image.get_height() // 2)))
        
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
                self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2, original_image.get_height() // 2)))
        self.index = 0  # Index to track which sprite to display
        self.image = self.sprites[self.index]
        self.rect = self.image.get_rect(center=(pos_x, pos_y))
        if color == 'grey':
            self.correct = True
        else:
            self.correct = False
        self.check = colors_code[color] + 'j' + position


    def update(self):
        self.index = (self.index + 1) % len(self.sprites)  # Cycle through sprites
        self.image = self.sprites[self.index]
        if self.correct == True:
            self.sprites = []
            original_image = pygame.image.load(f'joy/grey/grey.gif')
            self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2, original_image.get_height() // 2)))
        #time.sleep(0.2)
class Potentio(pygame.sprite.Sprite):
    def __init__(self,pos_x,pos_y,color,position):
        super().__init__()
        self.sprites = []
        if color == 'grey':
            original_image = pygame.image.load(f'potentio/grey/grey.gif')
            self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2, original_image.get_height() // 2)))
        else:
            for i in range(24):  # Assuming you have example0.gif to example12.gif
                if i < 10:
                    original_image = pygame.image.load(f'potentio/{color}/frame_0{i}_delay-0.01s.gif')
                else:
                    original_image = pygame.image.load(f'potentio/{color}/frame_{i}_delay-0.01s.gif')
                self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2, original_image.get_height() // 2)))
        self.index = 0  # Index to track which sprite to display
        self.image = self.sprites[self.index]
        self.rect = self.image.get_rect(center=(pos_x, pos_y))
        if color == 'grey':
            self.correct = True
        else:
            self.correct = False
        self.check = colors_code[color] + 'p' + position

    def update(self):
        self.index = (self.index + 1) % len(self.sprites)  # Cycle through sprites
        self.image = self.sprites[self.index]
        if self.correct == True:
            self.sprites = []
            original_image = pygame.image.load(f'joy/grey/grey.gif')
            self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2, original_image.get_height() // 2)))
        #time.sleep(0.2)
class Switch(pygame.sprite.Sprite):
    def __init__(self,pos_x,pos_y,color):
        super().__init__()
        self.sprites = []
        if color == 'grey':
            original_image = pygame.image.load(f'switch/grey/grey.gif')
            self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2, original_image.get_height() // 2)))
        else:
            for i in range(16):  # Assuming you have example0.gif to example12.gif
                if i < 10:
                    original_image = pygame.image.load(f'switch/{color}/frame_0{i}_delay-0.01s.gif')
                else:
                    original_image = pygame.image.load(f'switch/{color}/frame_{i}_delay-0.01s.gif')
                self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2, original_image.get_height() // 2)))
        self.index = 0  # Index to track which sprite to display
        self.image = self.sprites[self.index]
        self.rect = self.image.get_rect(center=(pos_x, pos_y))
        if color == 'grey':
            self.correct = True
        else:
            self.correct = False
        self.check = colors_code[color] + 's'
        
        
    def update(self):
        self.index = (self.index + 1) % len(self.sprites)  # Cycle through sprites
        self.image = self.sprites[self.index]
        #time.sleep(0.2)
        if self.correct == True:
            self.sprites = []
            original_image = pygame.image.load(f'joy/grey/grey.gif')
            self.sprites.append(pygame.transform.scale(original_image, (original_image.get_width() // 2, original_image.get_height() // 2)))
# for i in range(4):
#     button = Button(100 + (i*133.33), ((height - line_spacing * 4) - 10)/2)
#     sprite.append(button)

def random_input(available_players):
    color = available_players
    sprite = ["button","joy","potentio","switch"]
    
    #sprite = [button,joy,potentio,switch]
    for i in range(4):
        random_color = random.randint(0,len(available_players)-1)
        if i == 0:
            button = Button(100 + (i*133.33), ((height - line_spacing * 4) - 10)/2,color[random_color])
            sprite[i] = button
        if i == 1:
            positions = ['l','r','u','d']
            random_position = random.randint(0,3)
            joy = Joy(100 + (i*133.33), ((height - line_spacing * 4) - 10)/2,color[random_color],positions[random_position])
            sprite[i] = joy
        if i == 2:
            positions = ['l','m','h']
            random_position = random.randint(0,2)
            potentio = Potentio(100 + (i*133.33), ((height - line_spacing * 4) - 10)/2,color[random_color],positions[random_position])
            sprite[i] = potentio
        if i == 3:
            switch = Switch(100 + (i*133.33), ((height - line_spacing * 4) - 10)/2,color[random_color])
            sprite[i] = switch
    return sprite
def random_minigame():
    random_number = random.randint(0, 1)
    return random_number
sprite = random_input()
all_sprites = pygame.sprite.Group(sprite)

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ser.close()
            sys.exit()

    screen.fill(black)

    # Let user choose a player.
    if user is None:
#--------------------------receive initial state of each joy---------------------------
        if needsetup:
            ser.write("Need set up\n".encode())
        if ser.inWaiting():
            received = ser.readline().decode('utf-8').rstrip() 
            players = received.split('/')
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
        start_button = pygame.Rect(200, 150, 200, 100)
        pygame.draw.rect(screen, white, start_button)

        start_text = mediumFont.render("START", True, black)
        start_text_rect = start_text.get_rect(center=start_button.center)
        screen.blit(start_text, start_text_rect)

        mouse_pos = pygame.mouse.get_pos()
        if start_button.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:  # Check if left mouse button is clicked
                user = "in"  # Assuming user chooses "X" as their symbol
                ai_turn = True  # Now it's AI's turn
                life = 4
                start_time = time.time()
                change_input =  True
                start = 0
                updated_time = time.time()
                last_updated = time.time()
                needsetup = False

    elif user == 'lose':
        screen.fill(black)
        draw_text('You Lose', largeFont, red, screen, width // 2, height // 3)
        try_again_button = pygame.Rect(width // 2 - 100, height // 2, 200, 50)
        pygame.draw.rect(screen, green, try_again_button)
        draw_text('Try Again', mediumFont, black, screen, width // 2, height // 2 + 25)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if try_again_button.collidepoint(mouse_pos):
                    user = None  # Reset the game state   
    else:
    # Display countdown timer
        if minigame == None:
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
                for i in range(4):
                    if i == 2:
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
                    if i == 1:
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
        

            pygame.draw.line(screen, red, (0, height - line_spacing * 1), (width, height - line_spacing * 1), line_thickness)
            pygame.draw.line(screen, yellow, (0, height - line_spacing * 2), (width, height - line_spacing * 2), line_thickness)
            pygame.draw.line(screen, green, (0, height - line_spacing * 3), (width, height - line_spacing * 3), line_thickness)
            pygame.draw.line(screen, blue, (0, height - line_spacing * 4), (width, height - line_spacing * 4), line_thickness)
            
            if life == 0 or remaining_time <= 0:#lose
                user = 'lose'
                
            if sprite[0].correct and sprite[1].correct and sprite[2].correct and sprite[3].correct:
                sprite = random_input(available_players)
                all_sprites = pygame.sprite.Group(sprite)
                change_input = False
                start = elapsed_time
            elif elapsed_time - start >= 5 and change_input == True:
                sprite = random_input(available_players)
                all_sprites = pygame.sprite.Group(sprite)
                change_input = False
                start = elapsed_time
                life -= 1
            if time.time() - last_updated > 0.2:
                all_sprites.update()
                last_updated = time.time()
            all_sprites.draw(screen)
            if interval >= 5: #deaw plien
                minigame = -999
                #time.sleep(1)
                start_transition = time.time()
                user_minigame0_count = 0
                player_blue_switch = 0
                player_green_switch = 0
                player_yellow_switch = 0
                player_red_switch = 0

 
        if minigame == -999:
            elapsed_time = time.time() - start_transition
            #RIght it here
            remaining_time = max(0, 4 - elapsed_time) 
            font = pygame.font.Font(None, 36)  # Choose a font and size
            text = font.render(f"Starting minigame in {int(remaining_time)}", True, white)  # Render the text
            text_rect = text.get_rect(center=(width // 2, height // 2))
            screen.blit(text, text_rect)

            if remaining_time <= 0:
                minigame = 1
                colors = ["red","yellow","green","blue"]
                if minigame == 1:
                    for color in colors:
                        number = random.randint(0,1)
                        globals()[f"set_{color}_switch"] = number
                    correct_blue = (player_blue_switch == set_blue_switch)
                    correct_green = (player_green_switch == set_green_switch)
                    correct_yellow = (player_yellow_switch == set_yellow_switch)
                    correct_red = (player_red_switch == set_red_switch)
                finished = False

                time_to_play_minigame += elapsed_time
                start_minigame_time = time.time()

        
        
        if minigame == 0:
            elapsed_time = time.time() - start_minigame_time
            remaining_time = max(0, minigame0_time - elapsed_time)
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            countdown_text = mediumFont.render(f"{minutes:02}:{seconds:02}", True, white)
            screen.blit(countdown_text, (10, 10))  # Display at top left corner

            # Display user and set minigame 0 counts
            text_color = (255, 255, 255)
            font = pygame.font.Font(None, 100)
            count_text = f"{user_minigame0_count} / {set_minigame0_count}"
            count_surface = font.render(count_text, True, text_color)
            count_rect = count_surface.get_rect()
            count_rect.topleft = (width // 2 + 20, height // 2 - count_surface.get_height() // 2)
            screen.blit(count_surface, count_rect)

            button_icon = pygame.image.load("/home/pasutchien/roboproject/299643.png")  # Replace "path" with the actual path
            scaled_button_icon = pygame.transform.scale(button_icon, (width // 3, height // 3))  # Adjust the scaling factor as needed
            # Set the position of the button icon
            button_icon_rect = scaled_button_icon.get_rect()
            button_icon_rect.center = (width // 2 - 100, height // 2)  # Adjust the position as needed
            # Blit the scaled button icon onto the screen
            screen.blit(scaled_button_icon, button_icon_rect)
            if ser.inWaiting():
                received = ser.readline().decode('utf-8').rstrip() 
                if received[1] == 'b':
                    user_minigame0_count += 1
                if user_minigame0_count >= set_minigame0_count:
                    minigame = None
                    updated_time = time.time()
                    time_to_play_minigame += elapsed_time

            # Handle mouse events

            if remaining_time <= 0: #lose
                minigame = None
                updated_time = time.time()
                life -= 1
                time_to_play_minigame += elapsed_time
 


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
            color_switch_positions = {
                "red": (60 + (0*133.33), ((height - line_spacing * 4) - 50)/2),
                "yellow": (60 + (1*133.33), ((height - line_spacing * 4) - 50)/2),
                "green": (60 + (2*133.33), ((height - line_spacing * 4) - 50)/2),
                "blue": (60 + (3*133.33), ((height - line_spacing * 4) - 50)/2)
            }
    
            # Load images for color switches based on the current switch state
            # color_switch_images = {}
            # for color in ["red", "yellow", "green", "blue"]:
            #     # Check the state of each switch to determine which image to load
            #     if globals()[f"player_{color}_switch"] == 0:
            #         image_path = f"minigame1/{color}_down.png"  # Use down image if switch state is 0
            #     else:
            #         image_path = f"minigame1/{color}_up.png"    # Use up image if switch state is 1
        
            #     original_image = pygame.image.load(image_path).convert_alpha()
            #     resized_image = pygame.transform.scale(original_image, (original_image.get_width() // 2, original_image.get_height() // 2))
            #     color_switch_images[color] = resized_image
    
            # After loading images, you would then draw them at their respective positions
            # Assuming you have a dictionary or method to get the correct positions
            # for color, image in color_switch_images.items():
            #     position = color_switch_positions[color]  # Assume positions are predefined somewhere
            #     screen.blit(image, position)

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
                minigame = None
                updated_time = time.time()
                time_to_play_minigame += elapsed_time
                finished = False
            if remaining_time <= 0:
                minigame = None
                updated_time = time.time()
                life -=1
                time_to_play_minigame += elapsed_time
                finished = False
   



    # Update the screen
    pygame.display.flip()
    