import pygame
import sys
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
asset_path = os.getenv("ASSET_PATH")

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
GREEN = (0, 255, 0)

# Set up screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("KAIKEN")

# Fonts
font = pygame.font.Font(None, 74)
font_small = pygame.font.Font(None, 36)

# Game Modes
MODES = ["Arcade", "Adventure", "Team Battle", "Tournament"]

def load_asset(filename):
    return pygame.image.load(os.path.join(asset_path + '/images', filename))

# Character assets (portraits and sprites)
character_portraits = [f"character_{i}.png" for i in range(1, 9)]
character_sprites   = [f"character_{i}_sprite.png" for i in range(1, 9)]
character_portrait_images = [load_asset(char) for char in character_portraits]
character_sprite_images   = [load_asset(char) for char in character_sprites]
import random

victory_dialogs = [
    "I never doubted my strength for a second!",
    "Another battle, another triumph!",
    "Don't feel bad, I was destined to win.",
    "I walk the path of victory!",
    "It was over before it began.",
    "Maybe next time, you'll put up a fight.",
    "Victory is sweet, isn't it?",
    "The winds of fate were on my side today!",
    "I'm just getting started.",
    "Your defeat was inevitable.",
    "Too easy! I'm barely breaking a sweat.",
    "I live for moments like this.",
    "Better luck next time, friend.",
    "All hail the champion!",
    "I won’t apologize for greatness.",
    "Even the stars couldn't save you.",
    "Looks like I came out on top again.",
    "You fought bravely. Just not bravely enough.",
    "And that’s how it’s done!",
    "I'll savor this victory for a while.",
    "Your defeat is my delight.",
    "A champion never rests!",
    "Next time, try harder!",
    "Maybe you underestimated me?",
    "I was born to win!",
    "Another notch on my belt.",
    "Victory isn't everything, it's the only thing.",
    "Behold true skill!",
    "A lion among lambs.",
    "Is that all you've got?"
]

# Reflect bottom row for player during battle
player_portraits_battle = character_portrait_images[:]
for i in range(4, 8):
    player_portraits_battle[i] = pygame.transform.flip(player_portraits_battle[i], True, False)

# Reflect top row for AI during battle
ai_portraits_battle = character_portrait_images[:]
for i in range(0, 4):
    ai_portraits_battle[i] = pygame.transform.flip(ai_portraits_battle[i], True, False)

# Load audio
pygame.mixer.music.load(os.path.join(asset_path + '/sounds', "epic_theme.mp3"))
pygame.mixer.music.play(-1)

# Load backgrounds
backgrounds = [f"background_{i}.png" for i in range(1, 5)]
background_images = [pygame.transform.scale(load_asset(bg), (SCREEN_WIDTH, SCREEN_HEIGHT)) for bg in backgrounds]

# Timer for Battle Scene
battle_timer = 60

# Game State
game_state = "title"
selected_mode = None
selected_character = None
selected_character_sprite = None
computer_character = None
computer_character_sprite = None
cursor_index = 0
character_index = 0
background_image = None
health_player = 100
health_computer = 100
player_score = 0
computer_score = 0

# Animation variables
animation_index = 0
animation_timer = 0
ANIMATION_SPEED = 5

# Attack data dictionary
attack_data = {
    1: {  # Kai
        "basic_img": "character_1_atk1.png",  # small fireball
        "basic_damage": 1,
        "mid_img":   "character_1_atk2.png",  # two fireballs, 2 dmg each
        "mid_damage": 2,
        "ult_img":   "character_1_atk3.png",  # large fireball, 8 dmg
        "ult_damage": 8
    },
    2: {  # Amy
        "basic_img": "character_2_atk1.png",
        "basic_damage": 1,
        "mid_img":   "character_2_atk2.png",
        "mid_damage": 2,
        "ult_img":   "character_2_atk3.png",  # 8 pink orbs
        "ult_damage": 2  # each orb 2 dmg
    },
    3: {  # Drifter
        "basic_img": "character_3_atk1.png",
        "basic_damage": 1,
        "mid_img":   "character_3_atk2.png",  # random-moving tornado
        "mid_damage": 2,
        "ult_img":   "character_3_atk3.png",  # two tornadoes
        "ult_damage": 2
    },
    4: {  # Stella
        "basic_img": "character_4_atk1.png",
        "basic_damage": 1,
        "mid_img":   "character_4_atk2.png",
        "mid_damage": 0,
        "ult_img":   "character_4_atk3.png",  # blizzard
        "ult_damage": 1
    },
    5: {  # Ken
        "basic_img": "character_5_atk1.png",
        "basic_damage": 1,
        "mid_img":   "character_5_atk2.png",  # medium beam
        "mid_damage": 2,
        "ult_img":   "character_5_atk3.png",  # forcefield
        "ult_damage": 0
    },
    6: {  # Dianna
        "basic_img": "character_6_atk1.png",
        "basic_damage": 1,
        "mid_img":   "character_6_atk2.png",  # heal 3
        "mid_damage": -3,  # negative = healing
        "ult_img":   "character_6_atk3.png",  # heal 6
        "ult_damage": -6
    },
    7: {  # Gaia
        "basic_img": "character_7_atk1.png",
        "basic_damage": 1,
        "mid_img":   "character_7_atk2.png",
        "mid_damage": 0,
        "ult_img":   "character_7_atk3.png",  # orbiting boulders
        "ult_damage": 4
    },
    8: {  # Clide
        "basic_img": "character_8_atk1.png",
        "basic_damage": 1,
        "mid_img":   "character_8_atk2.png",
        "mid_damage": 2,
        "ult_img":   "character_8_atk3.png",  # 3 homing black fireballs
        "ult_damage": 4
    }
}

# Load & scale the attack images
for char_id in attack_data:
    # Basic
    attack_data[char_id]["basic_surface"] = pygame.transform.scale(
        load_asset(attack_data[char_id]["basic_img"]), (40, 40)
    )
    # Mid
    attack_data[char_id]["mid_surface"] = pygame.transform.scale(
        load_asset(attack_data[char_id]["mid_img"]), (50, 50)
    )
    # Ultimate
    attack_data[char_id]["ult_surface"] = pygame.transform.scale(
        load_asset(attack_data[char_id]["ult_img"]), (60, 60)
    )

# Title Screen
def title_screen():
    screen.fill(BLACK)
    title_logo = load_asset('titlelogo_no_background.png')
    title_logo = pygame.transform.scale(title_logo, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(title_logo, (0, 0))
    start_text = font_small.render("Press SPACE to Start", True, RED)
    current_time = pygame.time.get_ticks()
    if (current_time // 1000) % 2 == 0:
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))
    pygame.display.flip()

# Mode Selection Screen
def mode_selection_screen():
    main_menu_image = load_asset('mainmenu.png')
    main_menu_image = pygame.transform.scale(main_menu_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(main_menu_image, (0, 0))
    mode_text = font.render("Select Mode", True, WHITE)
    screen.blit(mode_text, (SCREEN_WIDTH // 2 - mode_text.get_width() // 2, 50))
    
    for index, mode in enumerate(MODES):
        color = WHITE if index != cursor_index else RED
        mode_option = font_small.render(mode, True, color)
        screen.blit(mode_option, (100, 150 + index * 50))
    
    pygame.display.flip()

# Character Selection Screen
def character_selection_screen():
    screen.fill(BLACK)
    character_text = font.render("Select Character", True, WHITE)
    screen.blit(character_text, (SCREEN_WIDTH // 2 - character_text.get_width() // 2, 50))
    
    for index, char_image in enumerate(character_portrait_images):
        x = 100 + (index % 4) * 150
        y = 200 + (index // 4) * 200
        if index == character_index:
            pygame.draw.rect(screen, RED, (x - 5, y - 5, char_image.get_width() + 10, char_image.get_height() + 10), 3)
        screen.blit(char_image, (x, y))
    
    pygame.display.flip()

# Portrait Animation
def character_portrait_animation():
    for i in range(50):
        screen.fill(BLACK)
        x_player = -character_portrait_images[character_index].get_width() + i * 16
        x_computer = SCREEN_WIDTH - i * 16
        screen.blit(character_portrait_images[character_index], (x_player, 200))
        computer_idx = character_portrait_images.index(computer_character)
        flipped_computer_portrait = pygame.transform.flip(character_portrait_images[computer_idx], True, False)
        screen.blit(flipped_computer_portrait, (x_computer, 200))
        pygame.display.flip()
        pygame.time.delay(20)
    screen.fill(WHITE)
    pygame.display.flip()
    pygame.time.delay(100)

def draw_health_bars():
    health_bar_length_player = int(200 * (health_player / 100))
    health_bar_length_computer = int(200 * (health_computer / 100))
    pygame.draw.rect(screen, GREEN, (50, 50, health_bar_length_player, 20))
    pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH - 250, 50, health_bar_length_computer, 20))

# Projectile & Effects
projectiles = []
active_effects = []  # screen-wide or special effects

# Player Attack Tracking
basic_cooldown_tracker = 0
mid_cooldown_tracker = 0
charging_ultimate = False
ultimate_charge_start_time = 0
got_hit_during_charge = False
ULTIMATE_CHARGE_TIME = 5.0

# AI Attack Tracking
ai_basic_cooldown_tracker = 0
ai_mid_cooldown_tracker = 0
ai_charging_ultimate = False
ai_ultimate_charge_start_time = 0
ai_got_hit_during_charge = False
AI_ULTIMATE_CHARGE_TIME = 5.0

# Functions that handle collisions and effect logic
def check_projectile_collisions():
    global health_player, health_computer, projectiles
    global got_hit_during_charge, ai_got_hit_during_charge

    for projectile in projectiles[:]:
        # Collision with player or computer?
        if projectile['owner'] == 'player':
            # Collide with computer
            comp_rect = pygame.Rect(computer_position[0], computer_position[1],
                                    computer_character_sprite['right'][0].get_width(),
                                    computer_character_sprite['right'][0].get_height())
            if projectile['rect'].colliderect(comp_rect):
                if projectile in projectiles:
                    dmg = projectile.get('damage', 1)
                    if dmg > 0:
                        health_computer = max(0, health_computer - dmg)
                    else:
                        # negative damage => healing player
                        health_player = min(100, health_player - dmg)
                    projectiles.remove(projectile)

        else:  # projectile['owner'] == 'computer'
            # Collide with player
            player_rect = pygame.Rect(player_position[0], player_position[1],
                                      selected_character_sprite['right'][0].get_width(),
                                      selected_character_sprite['right'][0].get_height())
            if projectile['rect'].colliderect(player_rect):
                if projectile in projectiles:
                    dmg = projectile.get('damage', 1)
                    if is_player_invulnerable():
                        # If there's a Ken forcefield or something in effect for the player, skip damage
                        pass
                    else:
                        health_player = max(0, health_player - dmg)
                        got_hit_during_charge = True  # cancels player's charge
                    projectiles.remove(projectile)

        # Offscreen
        if projectile['rect'].x > SCREEN_WIDTH or projectile['rect'].x < 0:
            if projectile in projectiles:
                projectiles.remove(projectile)

def is_player_invulnerable():
    """Check if the player is currently invulnerable due to an active effect (Ken's forcefield)."""
    current_time = time.time()
    for effect in active_effects:
        if effect['type'] == 'ken_forcefield' and current_time - effect['start_time'] < effect['duration']:
            return True
    return False

def is_computer_invulnerable():
    """Similarly, if the AI is Ken and the effect is active, skip damage."""
    current_time = time.time()
    for effect in active_effects:
        if effect['type'] == 'ken_forcefield_ai' and current_time - effect['start_time'] < effect['duration']:
            return True
    return False

# Create AI logic
import math  # Needed for distance calculation
import random
import time

# AI Attack Tracking (global or properly scoped)
ai_basic_cooldown_tracker = 0
ai_mid_cooldown_tracker = 0
ai_charging_ultimate = False
ai_ultimate_charge_start_time = 0
ai_got_hit_during_charge = False
AI_ULTIMATE_CHARGE_TIME = 5.0

# Example AI movement speed
ai_speed = 3

def ai_logic(ai_char_id):
    """
    AI tries to maintain a certain range from the player (e.g. 150-300 pixels).
    If too close, it backs off; if too far, it moves closer. Otherwise, it may strafe a bit.
    Also randomly does basic, mid, or ultimate attacks.
    """
    global ai_basic_cooldown_tracker, ai_mid_cooldown_tracker
    global ai_charging_ultimate, ai_ultimate_charge_start_time, ai_got_hit_during_charge
    global computer_position

    # 1. AI movement
    dx = player_position[0] - computer_position[0]
    dy = player_position[1] - computer_position[1]
    distance = math.sqrt(dx*dx + dy*dy)

    min_dist = 150
    max_dist = 300

    # If too close, back away
    if distance < min_dist:
        if dx < 0:
            computer_position[0] += ai_speed
        else:
            computer_position[0] -= ai_speed

        if dy < 0:
            computer_position[1] += ai_speed
        else:
            computer_position[1] -= ai_speed

    # If too far, move closer
    elif distance > max_dist:
        if dx < 0:
            computer_position[0] -= ai_speed
        else:
            computer_position[0] += ai_speed

        if dy < 0:
            computer_position[1] -= ai_speed
        else:
            computer_position[1] += ai_speed

    else:
        # Within "ideal" range, AI might do random strafe
        if random.random() < 0.01:
            computer_position[1] += random.choice([-10, 10])

    # Boundary checks (prevent AI from leaving screen)
    if computer_position[0] < 0:
        computer_position[0] = 0
    if computer_position[0] > SCREEN_WIDTH - computer_character_sprite['right'][0].get_width():
        computer_position[0] = SCREEN_WIDTH - computer_character_sprite['right'][0].get_width()
    if computer_position[1] < 0:
        computer_position[1] = 0
    if computer_position[1] > SCREEN_HEIGHT - computer_character_sprite['right'][0].get_height():
        computer_position[1] = SCREEN_HEIGHT - computer_character_sprite['right'][0].get_height()

    # 2. AI Attack logic
    current_time = time.time()

    # If AI is charging ultimate
    if ai_charging_ultimate:
        if ai_got_hit_during_charge:
            ai_charging_ultimate = False
            ai_ultimate_charge_start_time = 0
            ai_got_hit_during_charge = False
        else:
            elapsed = current_time - ai_ultimate_charge_start_time
            if elapsed >= AI_ULTIMATE_CHARGE_TIME:
                # Ultimate triggers
                ai_charging_ultimate = False
                do_ultimate_attack(ai_char_id, owner='computer')
                ai_ultimate_charge_start_time = 0
                ai_got_hit_during_charge = False
        return  # Skip random attack logic if charging

    # If not charging ultimate, roll random chance for each attack
    roll = random.random()

    # ~10% chance for basic attack
    if roll < 0.10:
        do_basic_attack(ai_char_id, owner='computer')

    # ~5% chance for mid attack (requires 4s cooldown)
    elif roll < 0.15:
        if current_time - ai_mid_cooldown_tracker >= 4.0:
            do_mid_attack(ai_char_id, owner='computer')
            ai_mid_cooldown_tracker = current_time

    # ~1% chance to start charging ultimate
    elif roll < 0.16:
        ai_charging_ultimate = True
        ai_ultimate_charge_start_time = current_time
        ai_got_hit_during_charge = False


def do_basic_attack(char_id, owner='player'):
    """
    Owner='player' or 'computer'.
    Uses attack_data to create a projectile. 
    If the character is facing left or right, we can guess direction by positions.
    For AI, let's assume it always faces the player if player is to the left, etc.
    """
    attack_surf   = attack_data[char_id]["basic_surface"]
    attack_damage = attack_data[char_id]["basic_damage"]
    
    if owner == 'player':
        # Are we facing left or right?
        if player_position[0] > computer_position[0]:
            # facing left
            flipped_img = pygame.transform.flip(attack_surf, True, False)
            rect = pygame.Rect(player_position[0],
                               player_position[1],
                               flipped_img.get_width(),
                               flipped_img.get_height())
            projectiles.append({
                'rect': rect,
                'image': flipped_img,
                'direction': 'left',
                'damage': attack_damage,
                'owner': 'player'
            })
        else:
            # facing right
            rect = pygame.Rect(player_position[0],
                               player_position[1],
                               attack_surf.get_width(),
                               attack_surf.get_height())
            projectiles.append({
                'rect': rect,
                'image': attack_surf,
                'direction': 'right',
                'damage': attack_damage,
                'owner': 'player'
            })
    else:  # AI
        # Face towards player
        ai_x, ai_y = computer_position
        if ai_x < player_position[0]:
            # AI is facing right
            rect = pygame.Rect(ai_x, ai_y, attack_surf.get_width(), attack_surf.get_height())
            projectiles.append({
                'rect': rect,
                'image': attack_surf,
                'direction': 'right',
                'damage': attack_damage,
                'owner': 'computer'
            })
        else:
            # AI facing left
            flipped_img = pygame.transform.flip(attack_surf, True, False)
            rect = pygame.Rect(ai_x, ai_y, flipped_img.get_width(), flipped_img.get_height())
            projectiles.append({
                'rect': rect,
                'image': flipped_img,
                'direction': 'left',
                'damage': attack_damage,
                'owner': 'computer'
            })

def do_mid_attack(char_id, owner='player'):
    """
    Spawns mid-attack logic: multiple projectiles or healing, etc.
    """
    mid_surf   = attack_data[char_id]["mid_surface"]
    mid_damage = attack_data[char_id]["mid_damage"]

    if owner == 'player':
        # If healing (Dianna), just heal player
        if char_id == 6 and mid_damage < 0:
            global health_player
            health_player = min(100, health_player - mid_damage)
        else:
            # Otherwise spawn 2 projectiles offset
            offsets = [-10, 10]
            if player_position[0] > computer_position[0]:
                # facing left
                flipped_img = pygame.transform.flip(mid_surf, True, False)
                for offset in offsets:
                    rect = pygame.Rect(player_position[0],
                                       player_position[1] + offset,
                                       flipped_img.get_width(),
                                       flipped_img.get_height())
                    projectiles.append({
                        'rect': rect,
                        'image': flipped_img,
                        'direction': 'left',
                        'damage': mid_damage,
                        'owner': 'player'
                    })
            else:
                # facing right
                for offset in offsets:
                    rect = pygame.Rect(player_position[0],
                                       player_position[1] + offset,
                                       mid_surf.get_width(),
                                       mid_surf.get_height())
                    projectiles.append({
                        'rect': rect,
                        'image': mid_surf,
                        'direction': 'right',
                        'damage': mid_damage,
                        'owner': 'player'
                    })
    else:  # AI
        # If Dianna AI (char_id=6) has mid-damage < 0 => heal AI
        global health_computer
        if char_id == 6 and mid_damage < 0:
            health_computer = min(100, health_computer - mid_damage)
        else:
            # AI spawns 2 projectiles
            offsets = [-10, 10]
            ai_x, ai_y = computer_position
            if ai_x < player_position[0]:
                # facing right
                for offset in offsets:
                    rect = pygame.Rect(ai_x, ai_y + offset, mid_surf.get_width(), mid_surf.get_height())
                    projectiles.append({
                        'rect': rect,
                        'image': mid_surf,
                        'direction': 'right',
                        'damage': mid_damage,
                        'owner': 'computer'
                    })
            else:
                # facing left
                flipped_img = pygame.transform.flip(mid_surf, True, False)
                for offset in offsets:
                    rect = pygame.Rect(ai_x, ai_y + offset, flipped_img.get_width(), flipped_img.get_height())
                    projectiles.append({
                        'rect': rect,
                        'image': flipped_img,
                        'direction': 'left',
                        'damage': mid_damage,
                        'owner': 'computer'
                    })

def do_ultimate_attack(char_id, owner='player'):
    """
    Spawns the ultimate effect: large projectile, full-screen effect, or healing.
    """
    ult_surf   = attack_data[char_id]["ult_surface"]
    ult_damage = attack_data[char_id]["ult_damage"]
    global health_player, health_computer

    if owner == 'player':
        if char_id == 4:
            # Stella's full screen blizzard
            active_effects.append({
                'type': 'stella_blizzard',
                'start_time': time.time(),
                'duration': 4.0
            })
        elif char_id == 5:
            # Ken's 4-second forcefield (player invulnerable)
            active_effects.append({
                'type': 'ken_forcefield',
                'start_time': time.time(),
                'duration': 4.0
            })
        elif char_id == 6:
            # Dianna heal
            health_player = min(100, health_player - ult_damage)  # negative => +6
        else:
            # By default, spawn a big projectile
            if player_position[0] > computer_position[0]:
                flipped_img = pygame.transform.flip(ult_surf, True, False)
                r = pygame.Rect(player_position[0], player_position[1],
                                flipped_img.get_width(), flipped_img.get_height())
                projectiles.append({
                    'rect': r,
                    'image': flipped_img,
                    'direction': 'left',
                    'damage': ult_damage,
                    'owner': 'player'
                })
            else:
                r = pygame.Rect(player_position[0], player_position[1],
                                ult_surf.get_width(), ult_surf.get_height())
                projectiles.append({
                    'rect': r,
                    'image': ult_surf,
                    'direction': 'right',
                    'damage': ult_damage,
                    'owner': 'player'
                })

    else:  # AI
        if char_id == 4:
            # Stella Blizzard, but for AI
            active_effects.append({
                'type': 'stella_blizzard',
                'start_time': time.time(),
                'duration': 4.0
            })
        elif char_id == 5:
            # Ken Forcefield for AI
            active_effects.append({
                'type': 'ken_forcefield_ai',
                'start_time': time.time(),
                'duration': 4.0
            })
        elif char_id == 6:
            # Dianna heal AI
            health_computer = min(100, health_computer - ult_damage)
        else:
            # Spawn big projectile
            ai_x, ai_y = computer_position
            if ai_x < player_position[0]:
                # facing right
                r = pygame.Rect(ai_x, ai_y, ult_surf.get_width(), ult_surf.get_height())
                projectiles.append({
                    'rect': r,
                    'image': ult_surf,
                    'direction': 'right',
                    'damage': ult_damage,
                    'owner': 'computer'
                })
            else:
                flipped_img = pygame.transform.flip(ult_surf, True, False)
                r = pygame.Rect(ai_x, ai_y, flipped_img.get_width(), flipped_img.get_height())
                projectiles.append({
                    'rect': r,
                    'image': flipped_img,
                    'direction': 'left',
                    'damage': ult_damage,
                    'owner': 'computer'
                })

def battle_screen():
    global battle_timer, animation_index, animation_timer
    global health_player, health_computer, player_score, computer_score, game_state
    global charging_ultimate, ultimate_charge_start_time, got_hit_during_charge
    global ai_charging_ultimate, ai_got_hit_during_charge, ai_ultimate_charge_start_time
    global active_effects
    screen.fill(BLACK)
    screen.blit(background_image, (0, 0))

    # Timer
    timer_text = font_small.render(f"Time Left: {battle_timer}", True, WHITE)
    screen.blit(timer_text, (SCREEN_WIDTH // 2 - timer_text.get_width() // 2, 10))

    # Player animation
    if animation_timer == 0:
        animation_index = (animation_index + 1) % 3

    # Choose sprite for player
    if keys[pygame.K_a]:
        current_sprite = selected_character_sprite['left'][animation_index]
    elif keys[pygame.K_d]:
        current_sprite = selected_character_sprite['right'][animation_index]
    else:
        if player_position[0] > computer_position[0]:
            current_sprite = selected_character_sprite['left'][0]
        else:
            current_sprite = selected_character_sprite['right'][0]
    screen.blit(current_sprite, player_position)

    # Player name text box
    box_outline = pygame.Surface((64, 34))
    box_outline.fill(BLACK)
    screen.blit(box_outline, (player_position[0] - 2, player_position[1] - 60))

    box_surface = pygame.Surface((60, 30))
    box_surface.fill(RED)
    screen.blit(box_surface, (player_position[0], player_position[1] - 58))

    arrow_text_player = font_small.render("P1", True, WHITE)
    screen.blit(arrow_text_player, (player_position[0] + 10, player_position[1] - 50))

    # Player & Computer portraits
    scaled_player_portrait = pygame.transform.scale(selected_character, (selected_character.get_width() // 2, selected_character.get_height() // 2))
    scaled_computer_portrait = pygame.transform.flip(
        pygame.transform.scale(computer_character, (computer_character.get_width() // 2, computer_character.get_height() // 2)), True, False
    )
    screen.blit(scaled_player_portrait, (10, 10))
    screen.blit(scaled_computer_portrait, (SCREEN_WIDTH - scaled_computer_portrait.get_width() - 10, 10))

    # Computer animation
    if computer_position[0] > player_position[0]:
        comp_sprite = computer_character_sprite['left'][animation_index]
    else:
        comp_sprite = computer_character_sprite['right'][animation_index]
    screen.blit(comp_sprite, computer_position)

    # Computer text box
    comp_outline = pygame.Surface((64, 34))
    comp_outline.fill(BLACK)
    screen.blit(comp_outline, (computer_position[0] - 2, computer_position[1] - 60))

    comp_box = pygame.Surface((60, 30))
    comp_box.fill(BLUE)
    screen.blit(comp_box, (computer_position[0], computer_position[1] - 58))

    arrow_text_computer = font_small.render("COM1", True, WHITE)
    arrow_text_computer = pygame.transform.scale(arrow_text_computer, (50, 20))
    screen.blit(arrow_text_computer, (computer_position[0] + 5, computer_position[1] - 50))

    # Update timer
    animation_timer = (animation_timer + 1) % ANIMATION_SPEED

    # Move projectiles
    for projectile in projectiles:
        if projectile['direction'] == 'right':
            projectile['rect'].x += 10
        else:
            projectile['rect'].x -= 10

    # Collisions
    check_projectile_collisions()

    # Draw projectiles
    for projectile in projectiles:
        screen.blit(projectile['image'], projectile['rect'])

    # Active effects
    current_time = time.time()
    new_effects = []
    for effect in active_effects:
        if current_time - effect['start_time'] < effect['duration']:
            # Apply effect
            if effect['type'] == 'stella_blizzard':
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(76)
                overlay.fill((0, 0, 255))
                screen.blit(overlay, (0, 0))
                # Could cause damage or slow to the opponent each second
                # For demonstration, do minor damage each second to both? Or just the opponent?
                # Example: once per second to the opponent
                if int(current_time * 10) % 10 == 0:
                    if effect.get('owner', 'player') == 'player':
                        if not is_computer_invulnerable():
                            health_computer = max(0, health_computer - 1)
                    else:
                        if not is_player_invulnerable():
                            health_player = max(0, health_player - 1)
            elif effect['type'] == 'ken_forcefield':
                # Player is invulnerable; visually maybe draw a transparent circle or outline
                pass
            elif effect['type'] == 'ken_forcefield_ai':
                # AI is invulnerable
                pass
            new_effects.append(effect)
        else:
            # effect ended
            pass
    active_effects = new_effects

    draw_health_bars()

    # Round end checks
    round_over = False
    if health_player == 0 or health_computer == 0:
        round_over = True
        winner_text = "Player Wins!" if health_player > health_computer else "Computer Wins!"
        if health_player > health_computer:
            player_score += 1
        else:
            computer_score += 1

        winner_display = font.render(winner_text, True, WHITE)
        screen.blit(winner_display, (SCREEN_WIDTH // 2 - winner_display.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.delay(3000)

    # Timer countdown
    if pygame.time.get_ticks() % 1000 < 17:
        battle_timer -= 1

    if battle_timer <= 0 or round_over:
        if not round_over:
            # determine winner by health
            winner_text = "Player Wins!" if health_player > health_computer else "Computer Wins!"
            if health_player > health_computer:
                player_score += 1
            else:
                computer_score += 1

            winner_display = font.render(winner_text, True, WHITE)
            screen.blit(winner_display, (SCREEN_WIDTH // 2 - winner_display.get_width() // 2, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            pygame.time.delay(3000)

        # Check match victory
        if player_score == 3 or computer_score == 3:
            final_winner = "Player" if player_score == 3 else "Computer"
            final_winner_image = selected_character if player_score == 3 else computer_character
            screen.fill(BLACK)
            screen.blit(final_winner_image, (SCREEN_WIDTH // 2 - final_winner_image.get_width() // 2,
                                             SCREEN_HEIGHT // 2 - final_winner_image.get_height() // 2))
            final_winner_text = font.render(f"{final_winner} Wins!", True, WHITE)
            screen.blit(final_winner_text, (SCREEN_WIDTH // 2 - final_winner_text.get_width() // 2, 100))
            

            pygame.display.flip()
            pygame.time.delay(5000)
            # Reset
            player_score = 0
            computer_score = 0
            game_state = "character_selection"
            return

        # Otherwise new round
        health_player = 100
        health_computer = 100
        battle_timer = 60
        player_position[0], player_position[1] = 150, 300
        computer_position[0], computer_position[1] = 550, 300
        projectiles.clear()
        active_effects.clear()
        # Reset all charging states
        charging_ultimate = False
        ultimate_charge_start_time = 0
        got_hit_during_charge = False
        ai_charging_ultimate = False
        ai_ultimate_charge_start_time = 0
        ai_got_hit_during_charge = False

    pygame.display.flip()

# Main Loop
clock = pygame.time.Clock()
running = True
player_position = [150, 300]
computer_position = [550, 300]
player_speed = 5

current_character_id = 1  # set after selection
ai_character_id = 1       # set after selection

while running:
    clock.tick(FPS)
    screen.fill(BLACK)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Title -> Mode Selection
        if game_state == "title":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_state = "mode_selection"

        elif game_state == "mode_selection":
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_w, pygame.K_UP]:
                    cursor_index = (cursor_index - 1) % len(MODES)
                elif event.key in [pygame.K_s, pygame.K_DOWN]:
                    cursor_index = (cursor_index + 1) % len(MODES)
                elif event.key == pygame.K_RETURN:
                    selected_mode = MODES[cursor_index]
                    game_state = "character_selection"

        elif game_state == "character_selection":
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_a, pygame.K_LEFT]:
                    character_index = (character_index - 1) % len(character_portrait_images)
                elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                    character_index = (character_index + 1) % len(character_portrait_images)
                elif event.key == pygame.K_RETURN:
                    selected_character = character_portrait_images[character_index]
                    current_character_id = character_index + 1
                    selected_character_sprite = {
                        'left': [
                            pygame.transform.scale(load_asset(f"character_{current_character_id}_sprite_facing_left{i}.png"),
                                                   (selected_character.get_width(), selected_character.get_height()))
                            for i in range(1, 4)
                        ],
                        'right': [
                            pygame.transform.scale(load_asset(f"character_{current_character_id}_sprite_facing_right{i}.png"),
                                                   (selected_character.get_width(), selected_character.get_height()))
                            for i in range(1, 4)
                        ]
                    }

                    # AI random
                    computer_index = random.randint(0, len(character_portrait_images) - 1)
                    computer_character = character_portrait_images[computer_index]
                    ai_character_id = computer_index + 1
                    computer_character_sprite = {
                        'left': [
                            pygame.transform.scale(load_asset(f"character_{ai_character_id}_sprite_facing_left{i}.png"),
                                                   (computer_character.get_width(), computer_character.get_height()))
                            for i in range(1, 4)
                        ],
                        'right': [
                            pygame.transform.scale(load_asset(f"character_{ai_character_id}_sprite_facing_right{i}.png"),
                                                   (computer_character.get_width(), computer_character.get_height()))
                            for i in range(1, 4)
                        ]
                    }

                    background_image = random.choice(background_images)
                    character_portrait_animation()
                    game_state = "battle"

        elif game_state == "battle":
            if event.type == pygame.KEYDOWN:
                # Basic Attack (H)
                if event.key == pygame.K_h:
                    do_basic_attack(current_character_id, owner='player')

                # Mid Attack (J)
                elif event.key == pygame.K_j:
                    now = time.time()
                    if now - mid_cooldown_tracker >= 4.0:
                        do_mid_attack(current_character_id, owner='player')
                        mid_cooldown_tracker = now

                # Ultimate Attack (K) - start charging
                elif event.key == pygame.K_k:
                    if not charging_ultimate:
                        charging_ultimate = True
                        ultimate_charge_start_time = time.time()
                        got_hit_during_charge = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_k:
                    # Cancel charge if released early
                    charging_ultimate = False
                    ultimate_charge_start_time = 0
                    got_hit_during_charge = False

    # If player is charging ultimate
    if game_state == "battle" and charging_ultimate:
        if got_hit_during_charge:
            charging_ultimate = False
            ultimate_charge_start_time = 0
            got_hit_during_charge = False
        else:
            elapsed = time.time() - ultimate_charge_start_time
            if elapsed >= ULTIMATE_CHARGE_TIME:
                # Fire ultimate
                charging_ultimate = False
                do_ultimate_attack(current_character_id, owner='player')
                ultimate_charge_start_time = 0
                got_hit_during_charge = False

    # AI logic
    if game_state == "battle":
        ai_logic(ai_character_id)

    # Player movement
    if game_state == "battle":
        if keys[pygame.K_a] and player_position[0] > 0:
            player_position[0] -= player_speed
        if keys[pygame.K_d] and player_position[0] < SCREEN_WIDTH - selected_character_sprite['right'][0].get_width():
            player_position[0] += player_speed
        if keys[pygame.K_w] and player_position[1] > 0:
            player_position[1] -= player_speed
        if keys[pygame.K_s] and player_position[1] < SCREEN_HEIGHT - selected_character_sprite['right'][0].get_height():
            player_position[1] += player_speed

    # Render based on state
    if game_state == "title":
        title_screen()
    elif game_state == "mode_selection":
        mode_selection_screen()
    elif game_state == "character_selection":
        character_selection_screen()
    elif game_state == "battle":
        battle_screen()

    pygame.display.flip()

# Quit
pygame.quit()
sys.exit()
