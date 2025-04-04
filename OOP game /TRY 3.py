import pygame
import random

pygame.init()

# Window Setup
w_width, w_height = 800, 600
BG_color = (50, 50, 50)
screen = pygame.display.set_mode((w_width, w_height))
pygame.display.set_caption("Sample Version Game")

# Font
font = pygame.font.Font(None, 36)

# Sprite Class (with image support and animation)
class Sprite(pygame.sprite.Sprite):
    def __init__(self, x, y, right_images, left_images, down_images, up_images):
        super().__init__()

        # Store all the animation frames for different directions
        self.right_sprites = [pygame.image.load(img) for img in right_images]
        self.left_sprites = [pygame.image.load(img) for img in left_images]
        self.down_sprites = [pygame.image.load(img) for img in down_images]
        self.up_sprites = [pygame.image.load(img) for img in up_images]

        self.current_sprite = 0
        self.image = self.right_sprites[self.current_sprite]  # Default to right animation
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = 5
        self.animation_speed = 0.25
        self.is_animating = False
        self.current_direction = "right"  # Default direction is right

    def update(self):
        # Movement
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # Keep inside screen
        self.rect.x = max(0, min(w_width - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(w_height - self.rect.height, self.rect.y))

        # Animation (only animate when moving)
        if self.velocity.x != 0 or self.velocity.y != 0:
            self.is_animating = True
        else:
            self.is_animating = False

        # Set animation frames based on direction
        if self.is_animating:
            if self.velocity.x > 0:
                self.current_direction = "right"
            elif self.velocity.x < 0:
                self.current_direction = "left"
            elif self.velocity.y > 0:
                self.current_direction = "down"
            elif self.velocity.y < 0:
                self.current_direction = "up"

            # Handle the animation frames based on direction
            if self.current_direction == "right":
                self.update_animation(self.right_sprites)
            elif self.current_direction == "left":
                self.update_animation(self.left_sprites)
            elif self.current_direction == "down":
                self.update_animation(self.down_sprites)
            elif self.current_direction == "up":
                self.update_animation(self.up_sprites)
        else:
            # When idle, show the first sprite based on direction
            if self.current_direction == "right":
                self.image = self.right_sprites[0]
            elif self.current_direction == "left":
                self.image = self.left_sprites[0]
            elif self.current_direction == "down":
                self.image = self.down_sprites[0]
            elif self.current_direction == "up":
                self.image = self.up_sprites[0]

    def update_animation(self, sprites):
        self.current_sprite += self.animation_speed
        if self.current_sprite >= len(sprites):
            self.current_sprite = 0
        self.image = sprites[int(self.current_sprite)]



# Player & Enemy Images
right_images = ["player_right1.png", "player_right2.png", "player_right3.png", "player_right4.png"]
left_images = ["player_left1.png", "player_left2.png", "player_left3.png", "player_left4.png"]
down_images = ["player_down1.png", "player_down2.png", "player_down3.png", "player_down4.png"]
up_images = ["player_up1.png", "player_up2.png", "player_up3.png", "player_up4.png"]

enemy_images = ["enemy1.png", "enemy2.png", "enemy3.png", "enemy4.png"]

#for the enemy
class Enemy(Sprite):
    def __init__(self, x, y, images):
        # Initialize with the same images for all directions (it doesn't need to change directions)
        super().__init__(x, y, images, images, images, images)
        self.velocity = pygame.math.Vector2(0, 0)  # No movement, stays in place
        self.speed = 0  # No speed, since it's not moving
        self.current_direction = "right"  # Set a default direction for animation
        self.is_animating = True  # Ensure animation runs even if not moving

    def update(self):
        # No movement logic here, just run the animation
        self.update_animation(self.right_sprites)  # Update the animation frames (loop)

# Player & Enemy
player = Sprite(100, 300, right_images, left_images, down_images, up_images)
enemy = Enemy(500, 300, enemy_images)

sprites = pygame.sprite.Group()
sprites.add(player, enemy)

# Game State Variables
player_health = 100
enemy_health = 100
in_combat = False
player_turn = True
in_encounter = False
choice_made = False

show_cursor = False
pygame.mouse.set_visible(show_cursor)

questions = [
    {"question": "What is 2 + 2?", "answer": "4", "damage": 20},
    {"question": "What is the capital of France?", "answer": "Paris", "damage": 20},
    {"question": "What is 3 * 5?", "answer": "15", "damage": 20},
]

def draw_health_bars():
    pygame.draw.rect(screen, (255, 0, 0), (50, 50, player_health * 2, 20))
    screen.blit(font.render(f"Player Hp: {player_health} ", True, (255, 255, 255)), (50, 20))
    pygame.draw.rect(screen, (255, 0, 0), (550, 50, enemy_health * 2, 20))
    screen.blit(font.render(f"Enemy Hp: {enemy_health} ", True, (255, 255, 255)), (550, 20))

def check_battle_ends():
    global in_combat
    if player_health <= 0:
        screen.blit(font.render("Player Lost: Press Esc to Quit", True, (255, 255, 255)), (250, 300))
        pygame.display.flip()
        return True
    if enemy_health <= 0:
        screen.blit(font.render("Enemy Lost: Press Esc to Quit", True, (255, 255, 255)), (250, 300))
        pygame.display.flip()
        return True
    return False

def draw_encounter_screen():
    screen.blit(font.render("An enemy is near! Choose an action:", True, (255, 255, 255)), (250, 200))
    screen.blit(font.render("Press F to Fight", True, (255, 255, 255)), (250, 250))
    screen.blit(font.render("Press R to Run", True, (255, 255, 255)), (250, 300))

def ask_question():
    global player_health, enemy_health, player_turn
    question = random.choice(questions)
    screen.blit(font.render(question["question"], True, (255, 255, 255)), (250, 400))
    pygame.display.flip()

    answer = None
    while not answer:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_4 and question["answer"] == "4":
                    enemy_health -= question["damage"]
                    answer = True
                elif event.key == pygame.K_4:
                    player_health -= question["damage"]
                    answer = True
                elif event.key == pygame.K_p and question["answer"] == "Paris":
                    enemy_health -= question["damage"]
                    answer = True
                elif event.key == pygame.K_p:
                    player_health -= question["damage"]
                    answer = True
                elif event.key == pygame.K_1 and question["answer"] == "15":
                    enemy_health -= question["damage"]
                    answer = True
                elif event.key == pygame.K_1:
                    player_health -= question["damage"]
                    answer = True

def combat():
    global player_turn
    if player_turn:
        ask_question()
        player_turn = False
    else:
        pygame.time.delay(500)
        damage = random.randint(10, 20)
        player_health -= damage
        player_turn = True

def is_near(rect1, rect2, distance):
    dx = rect1.centerx - rect2.centerx
    dy = rect1.centery - rect2.centery
    return (dx * dx + dy * dy) ** 0.5 < distance

# GAME LOOP
running = True
while running:
    screen.fill(BG_color)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                show_cursor = not show_cursor
                pygame.mouse.set_visible(show_cursor)

            if in_combat:
                if player_turn and event.key == pygame.K_SPACE:
                    combat()

            if in_encounter:
                if event.key == pygame.K_f and not choice_made:
                    in_combat = True
                    in_encounter = False
                    player.rect.topleft = (100, 400)
                    enemy.rect.topleft = (600, 400)
                    choice_made = True
                elif event.key == pygame.K_r and not choice_made:
                    in_encounter = False
                    choice_made = True

            # Movement control (velocity)
            if not in_combat and not in_encounter:
                if event.key == pygame.K_w:
                    player.velocity.y = -player.speed
                if event.key == pygame.K_s:
                    player.velocity.y = player.speed
                if event.key == pygame.K_a:
                    player.velocity.x = -player.speed
                if event.key == pygame.K_d:
                    player.velocity.x = player.speed

        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_w, pygame.K_s]:
                player.velocity.y = 0
            if event.key in [pygame.K_a, pygame.K_d]:
                player.velocity.x = 0

    if in_combat and check_battle_ends():
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False
        continue

    # Enemy detects the player
    if not in_combat and not in_encounter and is_near(player.rect, enemy.rect, 150):  # Increased range
        in_encounter = True
        choice_made = False
        player.velocity = pygame.math.Vector2(0, 0)

    if in_encounter:
        draw_encounter_screen()

    sprites.update()
    sprites.draw(screen)

    if in_combat:
        draw_health_bars()

    pygame.display.flip()
    pygame.time.delay(30)

pygame.quit()
