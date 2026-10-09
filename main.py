import pygame
import sys
import random
import json
import math
from pathlib import Path


pygame.init()


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

BACKGROUND_COLOUR = (15, 23, 42)
SNAKE_COLOUR = (0, 255, 140)
SNAKE_HEAD_COLOUR = (100, 255, 190)
FOOD_COLOUR = (255, 80, 100)
TEXT_COLOUR = (235, 245, 242)


screen = pygame.display.set_mode(
    (WINDOW_WIDTH, WINDOW_HEIGHT)
)

pygame.display.set_caption("Snake Game")


clock = pygame.time.Clock()

font = pygame.font.SysFont(
    "Arial",
    30
)


snake_size = 20
score = 0
high_score_file = Path(__file__).with_name("snake_high_score.json")

snake_body = [
    (200, 200),
    (180, 200),
    (160, 200),
    (140, 200)
]


direction_x = snake_size
direction_y = 0
next_direction_x = direction_x
next_direction_y = direction_y
turn_locked = False


def load_high_score():
    try:
        with high_score_file.open("r", encoding="utf-8") as score_file:
            score_data = json.load(score_file)
        return max(0, int(score_data.get("high_score", 0)))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return 0


def save_high_score():
    try:
        with high_score_file.open("w", encoding="utf-8") as score_file:
            json.dump({"high_score": high_score}, score_file, indent=2)
    except OSError:
        pass


high_score = load_high_score()

# Fixed star positions keep the background consistent between frames.
star_generator = random.Random(12)
background_stars = [
    (
        star_generator.randrange(8, WINDOW_WIDTH - 8),
        star_generator.randrange(8, WINDOW_HEIGHT - 8),
        star_generator.choice((1, 1, 1, 2)),
        star_generator.randrange(75, 175),
        star_generator.random() * 6.28
    )
    for _ in range(95)
]


def create_food_position():
    while True:
        food_x = random.randrange(
            0,
            WINDOW_WIDTH,
            snake_size
        )

        food_y = random.randrange(
            0,
            WINDOW_HEIGHT,
            snake_size
        )

        food_position = (food_x, food_y)

        if food_position not in snake_body:
            return food_position


food_x, food_y = create_food_position()


MOVE_EVENT = pygame.USEREVENT

# The original used 120 ms. A larger delay makes the snake move more slowly.
MOVE_DELAY = 170
pygame.time.set_timer(MOVE_EVENT, MOVE_DELAY)


def reset_game():
    global snake_body, direction_x, direction_y
    global next_direction_x, next_direction_y, turn_locked
    global food_x, food_y, score, game_over

    snake_body = [
        (200, 200),
        (180, 200),
        (160, 200),
        (140, 200)
    ]
    direction_x = snake_size
    direction_y = 0
    next_direction_x = direction_x
    next_direction_y = direction_y
    turn_locked = False
    score = 0
    food_x, food_y = create_food_position()
    game_over = False


def draw_background_details():
    # A subtle star field preserves the original dark, minimal appearance.
    detail_surface = pygame.Surface(
        (WINDOW_WIDTH, WINDOW_HEIGHT),
        pygame.SRCALPHA
    )

    current_time = pygame.time.get_ticks() / 1000

    for star_x, star_y, star_size, star_brightness, twinkle_offset in background_stars:
        twinkle = int(24 * (1 + math.sin(current_time * 1.8 + twinkle_offset)))
        brightness = min(210, star_brightness + twinkle)

        pygame.draw.circle(
            detail_surface,
            (190, 220, 255, brightness),
            (star_x, star_y),
            star_size
        )

        # A few brighter stars receive a small four-point sparkle.
        if star_size == 2 and brightness > 170:
            sparkle_colour = (205, 235, 255, brightness // 2)
            pygame.draw.line(
                detail_surface,
                sparkle_colour,
                (star_x - 3, star_y),
                (star_x + 3, star_y)
            )
            pygame.draw.line(
                detail_surface,
                sparkle_colour,
                (star_x, star_y - 3),
                (star_x, star_y + 3)
            )

    screen.blit(detail_surface, (0, 0))


running = True
game_over = False


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_over and event.key in (pygame.K_RETURN, pygame.K_r):
                reset_game()

            elif not game_over and not turn_locked:
                if event.key in (pygame.K_UP, pygame.K_w) and direction_y == 0:
                    next_direction_x = 0
                    next_direction_y = -snake_size
                    turn_locked = True

                elif event.key in (pygame.K_DOWN, pygame.K_s) and direction_y == 0:
                    next_direction_x = 0
                    next_direction_y = snake_size
                    turn_locked = True

                elif event.key in (pygame.K_LEFT, pygame.K_a) and direction_x == 0:
                    next_direction_x = -snake_size
                    next_direction_y = 0
                    turn_locked = True

                elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction_x == 0:
                    next_direction_x = snake_size
                    next_direction_y = 0
                    turn_locked = True

        if event.type == MOVE_EVENT and not game_over:
            direction_x = next_direction_x
            direction_y = next_direction_y
            turn_locked = False

            head_x, head_y = snake_body[0]

            new_head = (
                head_x + direction_x,
                head_y + direction_y
            )

            ate_food = new_head == (food_x, food_y)
            body_to_check = snake_body if ate_food else snake_body[:-1]

            hit_wall = not (
                0 <= new_head[0] < WINDOW_WIDTH
                and 0 <= new_head[1] < WINDOW_HEIGHT
            )
            hit_body = new_head in body_to_check

            if hit_wall or hit_body:
                game_over = True

                if score > high_score:
                    high_score = score
                    save_high_score()
            else:
                snake_body.insert(0, new_head)

                if ate_food:
                    score += 10
                    food_x, food_y = create_food_position()

                    if score > high_score:
                        high_score = score
                else:
                    snake_body.pop()

    screen.fill(BACKGROUND_COLOUR)
    draw_background_details()

    pygame.draw.rect(
        screen,
        FOOD_COLOUR,
        (
            food_x,
            food_y,
            snake_size,
            snake_size
        )
    )

    for index, segment in enumerate(snake_body):
        segment_x, segment_y = segment

        if index == 0:
            colour = SNAKE_HEAD_COLOUR
        else:
            colour = SNAKE_COLOUR

        pygame.draw.rect(
            screen,
            colour,
            (
                segment_x,
                segment_y,
                snake_size,
                snake_size
            )
        )

    if game_over:
        game_over_text = font.render(
            f"Game Over - Score: {score}",
            True,
            TEXT_COLOUR
        )
        restart_text = font.render(
            "Press Enter or R to restart",
            True,
            TEXT_COLOUR
        )

        screen.blit(
            game_over_text,
            game_over_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 22)
            )
        )
        screen.blit(
            restart_text,
            restart_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 22)
            )
        )

    pygame.display.update()

    clock.tick(60)


save_high_score()
pygame.quit()
sys.exit()
