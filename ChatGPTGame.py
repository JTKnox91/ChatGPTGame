import pygame
from pygame.locals import *
import pygame.mixer
import random
import sys


"""
PYGAME INITIALIATION
"""
pygame.init()
pygame.mixer.init()

pygame.display.set_caption("TrumpRunner v2")
pygame.mixer.music.load("theme.mp3")

"""
CONSTANTS
"""
# Window dimensions
WIDTH, HEIGHT = 640, 480

# Limits the rendering speed.
FRAME_RATE = 60 #fps

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Fonts
GAME_OVER_FONT = pygame.font.SysFont(None, 60)
SCORE_FONT = pygame.font.SysFont(None, 24)
HIGH_SCORE_FONT = pygame.font.SysFont(None, 24, bold=True)
USER_HIGH_SCORE_FONT = pygame.font.SysFont(None, 28, bold=True)
RESTART_FONT = pygame.font.SysFont(None, 24)

"""
GLOBAL VARIABLES
"""

# Pygame Interfaces. Should only be initialized once.
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Game State
player = None # The Player Sprite
game_over = None # Boolean whether the game is running or over
level = 0 #The Current game level
high_score_input = None # The high_score_input object for 

# Sprite Groups
all_sprites = None
falling_objects = None
shooting_objects = None
building_objects = None

"""
SPRITE CLASSES
"""

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.image = pygame.image.load("player.png")
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.centery = HEIGHT - 50  # Start lower on the screen
        self.speed = 5
        self.shooting = False  # Track if shooting key is pressed
        self.building = False  # Track if building key is pressed
        self.score = 0
        self.powerup_count = 0
        self.buildmargin = 0

        # Add the sprite to apropriate groups upon instantiation
        all_sprites.add(self)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            self.rect.x -= self.speed
        if keys[K_RIGHT]:
            self.rect.x += self.speed
        if keys[K_UP]:
            self.rect.y -= self.speed
        if keys[K_DOWN]:
            self.rect.y += self.speed

        # Keep the player within the screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        
        # Shoot the coin when 'a' key is pressed down
        if keys[K_a] and not self.shooting:
            self.shoot()
            self.shooting = True

        # Reset shooting flag when 'a' key is released
        if not keys[K_a] and self.shooting:
            self.shooting = False

        # Build wall when 'b' key is pressed down
        if keys[K_b] and not self.building:
            self.build()
            self.building = True

        # Reset build wall flag when 'b' key is released
        if not keys[K_b] and self.building:
            self.building = False
    
    def shoot(self):
        shooting_object = ShootingObject(self.rect.centerx, self.rect.top)
        shooting_objects.add(shooting_object)
        self.score -= 50  #  Each shot costs 50 score points
    
    def build(self):
        #if self.powerup_count > 0:
            self.powerup_count -= 1  #  Each wall costs 1 powerup
            buildawall_sound = pygame.mixer.Sound("buildawall.mp3")
            buildawall_sound.set_volume(.4)
            buildawall_sound.play()
            self.buildmargin += 4
            for i in range (10):
                building_object = BuildingObject(i*WIDTH/10 + 30 + self.buildmargin, HEIGHT)
                building_objects.add(building_object)

class ShootingObject(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(ShootingObject, self).__init__()
        self.image = pygame.image.load("coin.png")
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 5

        # Add the sprite to appropriate groups upon instantiation
        all_sprites.add(self)
        shooting_objects.add(self)

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()  # Remove the shooting object if it goes off the screen

        # Check for collisions with falling objects
        self.collisions = pygame.sprite.spritecollide(self, falling_objects, False)
        for obj in self.collisions:
            if isinstance(obj, FallingDocumentsObject):
                
                # Play the sound effect
                fired_sound = pygame.mixer.Sound("fired.mp3")
                fired_sound.set_volume(.4)
                fired_sound.play()
                
                #remove falling object and shooting object
                obj.kill()
                self.kill()

class BuildingObject(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(BuildingObject, self).__init__()
        self.image = pygame.image.load("wall.png")
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 5

        # Add the sprite to appropriate groups upon instantiation
        all_sprites.add(self)
        building_objects.add(self)

    def update(self):
        if self.rect.y > 100:
            self.rect.y -= self.speed
            self.rect.x += random.randint(-1,1)
        if self.rect.bottom < 0:
            self.kill()  # Remove the shooting object if it goes off the screen

        # Check for collisions with falling objects
        self.collisions = pygame.sprite.spritecollide(self, falling_objects, False)
        for obj in self.collisions:
            if isinstance(obj, FallingDocumentsObject):
                
                # Play the sound effect
                fired_sound = pygame.mixer.Sound("wall.mp3")
                fired_sound.set_volume(.4)
                fired_sound.play()
                
                #remove falling object and shooting object
                obj.kill()
                self.kill()

class FallingObject(pygame.sprite.Sprite):
    """
    Creates a uniformly sized falling object sprite from an image file.
    The falling speed will be a random int between 1-5, unless specificied.

    Treat this superclass as abstract, and only call the subclasses directly.
    """

    def __init__(self, image_path, speed=random.randint(1, 5)):
        super(FallingObject, self).__init__()
        image = pygame.image.load(image_path)  # Load the specified image
        self.image = pygame.transform.scale(image, (40, 40))  # Resize the image if needed
        self.speed = speed

        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = -self.rect.height
        
        # Add the sprite to apropriate groups upon instantiation
        falling_objects.add(self)
        all_sprites.add(self)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()  # Remove the object when it goes off the screen

class FallingMoneyObject(FallingObject):
    """ Subclass of `FallingObject` for the 'money' sprite. """
    def __init__(self):
        super(FallingMoneyObject, self).__init__("money.png")

class FallingDocumentsObject(FallingObject):
    """ Subclass of `FallingObject` for the 'document' sprite. """
    def __init__(self):
        super(FallingDocumentsObject, self).__init__("documents.png")

class FallingPowerUpObject(FallingObject):
    """
    Subclass of `FallingObject` for the 'power-up' sprite.
    
    Note the speed is always maxed out to make it special.
    """
    def __init__(self):
        super(FallingPowerUpObject, self).__init__("coin.png", 5)


"""
NON-SPRITE CLASSES
"""
class HighScoreInput():
    """
    A class to contain and manage the state of the highscore input.

    TODO: Figure out how to make this draw all of its parts
    """
    def __init__(self):
        self.__cursor_timer = 0
        self.__max_letters = 3
        self.initials = ""

    def write_letter(self, letter):
        if len(self.initials) < self.__max_letters:
            self.initials += letter.upper()

    def backspace(self):
        if len(self.initials) > 0:
            self.initials = self.initials[:-1]

    def is_not_empty(self):
        return len(self.initials) > 0
        
    def update(self):
        """
        Updates the blinking high_score_input visibility.
        
        If called once per frame, high_score_input blink will cycle on/off once per second.
        """
        self.__cursor_timer += 1
        if self.__cursor_timer > FRAME_RATE:
            self.__cursor_timer = 0

    def is_cursor_visible(self):
        """
        Whether the blinking cursor whould be displayed
        
        False during the back-half of the blink cycle, or if the max characters are reached.
        """
        return len(self.initials) < self.__max_letters and self.__cursor_timer < FRAME_RATE / 2

"""
UTILITIES
"""

def create_random_falling_object(difficulty=50):
    """
    Randomly returns either a `FallingMoneyObject` or a `FallingDocumentsObject`.
    
    `difficulty` should be a number between 0-100 and represents the percentage
    chance of returning a `FallingDocumentsObject`.
    """
    if (difficulty > random.randrange(0, 100)):
        return FallingDocumentsObject()
    else:
        return FallingMoneyObject()

def load_high_scores():
    high_scores = []
    try:
        with open("high_scores.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                score, initials = line.strip().split(",")
                high_scores.append({"score": int(score), "initials": initials.upper()})
    except FileNotFoundError:
        pass
    return high_scores

def update_high_scores(new_score, new_initialis):
    high_scores = load_high_scores()
    high_scores.append({"score": new_score, "initials": new_initialis})
    high_scores.sort(key=lambda x: x["score"], reverse=True)
    high_scores = high_scores[:5]  # Keep only the top 5 scores
    with open("high_scores.txt", "w") as file:
        for entry in high_scores:
            file.write(f"{entry['score']},{entry['initials']}\n")

# Draw the powerup inidcator
def draw_powerup_indicator():
    power_up_image = pygame.image.load("coin.png")
    power_up_image = pygame.transform.scale(power_up_image, (30, 30))
    power_up_spacing = 5
    for i in range(player.powerup_count):
        power_up_x = WIDTH - (i + 1) * (power_up_image.get_width() + power_up_spacing)
        power_up_y = power_up_spacing * 2
        screen.blit(power_up_image, (power_up_x, power_up_y))

def is_score_high_enough(high_scores, player_score):
    if player_score <= 0:
        return False
    if len(high_scores) < 5:
        return True
    return int(player.score) > int(high_scores[-1]['score'])

def restart_game():
    """
        Reset everything except for the screen and the clock itself

        Should be called at the start of every new game.
    """
    global all_sprites, falling_objects, shooting_objects, building_objects
    global player, game_over, level, high_score_input

    pygame.mixer.music.play()  # Start music at beginning then play on loop.

    # Empty then reset sprite Groups
    if all_sprites is not None:
        all_sprites.empty()
    if falling_objects is not None:
        falling_objects.empty()
    if shooting_objects is not None:
        shooting_objects.empty()
    if building_objects is not None:
        building_objects.empty()

    # Do this before re-creating sprites, as they will auto add themselves.
    all_sprites = pygame.sprite.Group()
    falling_objects = pygame.sprite.Group()
    shooting_objects = pygame.sprite.Group()
    building_objects = pygame.sprite.Group()

    player = Player()
    game_over = False
    level = 0
    high_score_input = HighScoreInput() # Should set to None after initials are saved

"""
GAME LOOP
"""
restart_game()

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
                    
        elif game_over:
            if event.type == KEYDOWN and event.key == K_SPACE:
                restart_game();

            elif event.type == KEYDOWN and high_score_input is not None:
                if event.key == K_RETURN:
                    # Save initials and update high scores
                    if high_score_input.is_not_empty():
                        update_high_scores(player.score, high_score_input.initials)
                        high_score_input = None # To prevent future edits
                elif event.key == K_BACKSPACE:
                    high_score_input.backspace()
                else:
                    high_score_input.write_letter(event.unicode)

    if not game_over:

        # Add falling falling_objects
        object_chance = random.randint(1, 100)
        
        if object_chance <= 5:
            # TODO: Use the `difficulty` parameter (based on the time passed, perhaps)
            #Level ideas:
            #One gold coin falls
            #Money falls
            #Money and documents begin to fall
            #More documents
            #less random documents (maybe add some diagonal shapes which will force user side-to-side)


            #Level Timing:
            #0:03 Super Easy Mode
            #0:21 Baby Mode
            #0:39 Easy Mode
            #0:53 Normal Mode
            #1:02 Left Hand Workout Mode
            #1:08 Hard Mode
            #1:14 Right Hand Workout mode
            #1:20 Right Hand Workout mode+
            #1:26 Dual Hand Challenge Mode
            #1:38 Tetris Mode
            #1:51 Extra Russian Mode
            #2:08 Advanced Tetris Mode
            #2:13 Tetris Master Mode
            #2:20 Tetris Master Mode+
            #2:25 Deceptive Mode
            #2:35 Elite Mode
            #2:47 Champion Mode
            #2:56 Ultra Mega Death Mode+++
            #3:03 Apocalypse Mode
            #3:09 ?!?!??!?!!??!? Mode
            #3:23 END

            create_random_falling_object()

        all_sprites.update()

        # Spawn power-ups
        if player.score % 1000 == 0:
            new_power_up = FallingPowerUpObject()

        # Check for collisions with falling falling_objects
        collisions = pygame.sprite.spritecollide(player, falling_objects, True)
        for obj in collisions:
            if isinstance(obj, FallingDocumentsObject):
                game_over = True
                #TODO: Early Return
            if isinstance(obj, FallingMoneyObject):
                player.score += 100
                #TODO: I'm not sure why the shooting object kills the money
            if isinstance(obj, FallingPowerUpObject):
                #TODO: Give this a better name.
                player.powerup_count += 1

        # Increase the score
        player.score += 1

    screen.fill(BLACK)

    # Draw sprites
    all_sprites.draw(screen)

    if game_over:
        pygame.mixer.music.stop()  # Stop the music if the game is over
        
        game_over_text = GAME_OVER_FONT.render("Game Over", True, YELLOW)
        game_over_text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        restart_text = RESTART_FONT.render("Press SPACE to restart", True, WHITE)
        restart_text_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))

        screen.blit(game_over_text, game_over_text_rect)
        screen.blit(restart_text, restart_text_rect)

        # Load the high scores from file
        high_scores = load_high_scores()

        # Draw the old high scores
        high_scores_text = HIGH_SCORE_FONT.render("HIGH SCORES:", True, WHITE)
        high_scores_text_rect = high_scores_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 75))
        screen.blit(high_scores_text, high_scores_text_rect)

        y_offset = 0
        for i, entry in enumerate(high_scores):
            ranking = f"#{i+1}"  # Calculate the ranking
            old_initials = entry["initials"]
            old_score = entry["score"]
            high_score_text = SCORE_FONT.render(f"{ranking}: {old_initials}: {old_score}", True, WHITE)
            high_score_text_rect = high_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 105 + y_offset))
            screen.blit(high_score_text, high_score_text_rect)
            y_offset += 28

        # Check if the player achieved a new high score,
        # if so (and they haven't already saved it), draw the input box for initials
        if high_score_input is not None and is_score_high_enough(high_scores, player.score):
            input_rect = pygame.Rect(300, 250, 45, 32) # Position of the input box
                       
            high_score_label = GAME_OVER_FONT.render("HIGH SCORE!", True, WHITE)
            high_score_label_rect = high_score_label.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
            screen.blit(high_score_label, high_score_label_rect)

            pygame.draw.rect(screen, WHITE, input_rect, 2)
            initials_text = SCORE_FONT.render(high_score_input.initials, True, WHITE)
            screen.blit(initials_text, input_rect.move(5, 8))

            # Draw the blinking high_score_input if the length of initials is less than 3
            if high_score_input.is_cursor_visible():
                high_score_input_rect = pygame.Rect(input_rect.x + initials_text.get_width() + 2, input_rect.y + input_rect.height // 2 - 10, 12, input_rect.height - 14)
                pygame.draw.rect(screen, WHITE, high_score_input_rect)
            
            # Update the cursor timer
            high_score_input.update()
        else:
            # Set to None to avoid looping through old scores next frame
            high_score_input = None

    # Draw the score
    score_text = SCORE_FONT.render(f"Score: {player.score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Draw the level
    level_text = SCORE_FONT.render(f"Level: {level}", True, WHITE)
    screen.blit(level_text, (13, 30))

    draw_powerup_indicator()

    pygame.display.flip()
    clock.tick(FRAME_RATE)
