import pygame
import random

pygame.init()

white = (255, 255, 255)
black = (0, 0, 0)
button_color = (100, 100, 255)
w_width, w_height = 800, 600

screen = pygame.display.set_mode((w_width, w_height))
pygame.display.set_caption("Menu Example")

class TunnelSprite(pygame.sprite.Sprite):
    def __init__(self, images, pos):
        super().__init__()
        self.images = images
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=pos)
        self.animation_timer = 0
        self.animation_speed = 150

    def update(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

sprite_images = [
    pygame.image.load("player_up1.png").convert_alpha(),
    pygame.image.load("player_up2.png").convert_alpha(),
    pygame.image.load("player_up3.png").convert_alpha(),
    pygame.image.load("player_up4.png").convert_alpha()
]
tunnel_sprite = TunnelSprite(sprite_images, (w_width // 2, w_height // 2))
sprite_group = pygame.sprite.Group(tunnel_sprite)

class MatrixTunnel:
    def __init__(self, width, height, depth=50):
        self.width = width
        self.height = height
        self.depth = depth
        self.characters = [self.create_character() for _ in range(1000)]

    def create_character(self):
        return [
            random.uniform(-self.width / 2, self.width / 2),
            random.uniform(-self.height / 2, self.height / 2),
            random.uniform(1, self.depth),
            random.choice(['0', '1'])
        ]

    def update_and_draw(self, screen):
        center_x, center_y = self.width // 2, self.height // 2
        for character in self.characters:
            character[2] -= 0.5
            if character[2] <= 0.1:
                character[:] = self.create_character()

            k = 128 / character[2]
            x = int(character[0] * k + center_x)
            y = int(character[1] * k + center_y)
            size = max(12, int((1 - character[2] / self.depth) * 24))
            color = (0, random.randint(160, 255), 0)

            if 0 <= x < self.width and 0 <= y < self.height:
                font = pygame.font.SysFont("arial", size)
                text_surface = font.render(character[3], True, color)
                screen.blit(text_surface, (x, y))

def draw_text(screen, text, font, color, pos):
    render = font.render(text, True, color)
    rect = render.get_rect(center=pos)
    screen.blit(render, rect)

def white_fade_in(screen, duration=1000):
    clock = pygame.time.Clock()
    fade_surface = pygame.Surface((w_width, w_height))
    fade_surface.fill(white)
    alpha = 255
    fade_speed = 255 / (duration / 16)

    while alpha > 0:
        fade_surface.set_alpha(int(alpha))
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        clock.tick(60)
        alpha -= fade_speed

def draw_glitch_text(screen, text, base_font, pos, colors=None):
    if colors is None:
        colors = [(0, random.randint(160, 255), 0) for _ in range(3)]

    offsets = [(-3, 0), (3, 0), (0, 0)]
    for color, offset in zip(colors, offsets):
        render = base_font.render(text, True, color)
        glitched_pos = (pos[0] + offset[0] + random.randint(-2, 2),
                        pos[1] + offset[1] + random.randint(-2, 2))
        screen.blit(render, render.get_rect(center=glitched_pos))

def draw_glitch_button(screen, text, font, pos, button_rect, hover=False):
    if hover:
        draw_glitch_text(screen, text, font, pos, colors=[(0, 255, 0), (0, 200, 0), (0, 255, 0)])
    else:
        draw_text(screen, text, font, white, pos)

def show_menu(screen):
    font = pygame.font.SysFont("arial", 30, bold=True)
    clock = pygame.time.Clock()
    button_width, button_height = 140, 40
    button_x = w_width // 2 - button_width // 2
    button_y = int(w_height * 0.75)
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    tunnel = MatrixTunnel(w_width, w_height)

    # Load background image here
    background_image = pygame.image.load("matrix_road.png").convert()
    background_image = pygame.transform.scale(background_image, (w_width, w_height))

    while True:
        screen.blit(background_image, (0, 0))
        tunnel.update_and_draw(screen)

        title_font = pygame.font.SysFont("arial", 70, bold=True)
        draw_glitch_text(screen, "PYTH-ON-BUG", title_font, (w_width // 2, 100))

        button_pos = button_rect.center
        mouse_pos = pygame.mouse.get_pos()
        hover = button_rect.collidepoint(mouse_pos)

        draw_glitch_button(screen, "Start Game", font, button_pos, button_rect, hover)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    white_fade_in(screen)
                    return "dialogue"

        sprite_group.draw(screen)
        dt = clock.tick(60)
        sprite_group.update(dt)
        pygame.display.flip()
