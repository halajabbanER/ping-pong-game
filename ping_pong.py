import pygame
import sys
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ping Pong Game")
clock = pygame.time.Clock()

# Colors
white = (255, 255, 255)
black = (0, 0, 0) 
red = (255, 0, 0)
blue = (0, 0, 255)
orange = (255, 165, 0)
green = (0, 128, 0)
yellow = (255, 255, 0)
purple = (128, 0, 128)
light_blue = (173, 216, 230)  # Freeze color

# Fonts
score_font = pygame.font.SysFont("PressStart2P.ttf", 50, bold=True)
status_font = pygame.font.SysFont("PressStart2P.ttf", 40)
big_font = pygame.font.SysFont("Arial", 40, bold=True)
font = pygame.font.Font(None, 70)
font_title = pygame.font.Font(None, 50)
font_timer = pygame.font.Font(None, 40)

# Sounds
try:
    pygame.mixer.music.load("GM.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"Music not found or failed to load: {e}")

try:
    goal_sound = pygame.mixer.Sound("goal.wav")
    goal_sound.set_volume(0.7)
except Exception as e:
    print(f"Goal sound not found(goal.wav): {e}")
    goal_sound = None

try:
    hit_sound = pygame.mixer.Sound("hit.wav")
    hit_sound.set_volume(0.5)
except Exception as e:
    print(f"Hit sound not found(hit.wav): {e}")
    hit_sound = None

try:
    reward_sound = pygame.mixer.Sound("reward.MP3")
    reward_sound.set_volume(0.8)
except Exception as e:
    print(f"reward sound not found(reward.MP3): {e}")
    reward_sound = None

# Background images
try:
    background = pygame.image.load("masa.jpg")
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill(black)

try:
    main_menu_bg = pygame.image.load("resim.jpg")
    main_menu_bg = pygame.transform.scale(main_menu_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    main_menu_bg = None

# Game Elements
BALL_SIZE = 30
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 100
ball = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, BALL_SIZE, BALL_SIZE)
ball_speed = [5, 5]

second_ball = None
second_ball_speed = [0, 0]

paddle1 = pygame.Rect(50, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle2 = pygame.Rect(SCREEN_WIDTH - 60, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle1_speed = 0
paddle2_speed = 0

# Game State
score1 = 0
score2 = 0
max_score = 7
game_over = False
winner = ""
paused = False
music_started = False
countdown_start = pygame.time.get_ticks()
show_countdown = True
start_time = pygame.time.get_ticks()
elapsed_time = 0

# Rewards and freeze
reward_message = ""
reward_timer = 0
REWARD_DURATION = 3000
reward_effect_timer = 0
reward_active = False

paddle1_frozen = False
paddle2_frozen = False
paddle1_frozen_time = 0
paddle2_frozen_time = 0
FREEZE_DURATION = 3000
paddle1_original_height = paddle1.height
paddle2_original_height = paddle2.height

# New: Game State control
main_menu = True
show_results = False
match_history = []

PLAYER1 = 1
PLAYER2 = 2

def reset_ball(direction=PLAYER1):
    if direction == PLAYER1:
        ball.center = (paddle1.right + BALL_SIZE // 2 + 5, SCREEN_HEIGHT // 2)
    else:
        ball.center = (paddle2.left - BALL_SIZE // 2 - 5, SCREEN_HEIGHT // 2)
    ball_speed[0] = 5 * (1 if direction == PLAYER1 else -1)
    ball_speed[1] = 5

def apply_reward(player):
    global reward_message, reward_timer, reward_effect_timer, reward_active
    global paddle1_frozen, paddle2_frozen, paddle1_frozen_time, paddle2_frozen_time
    global second_ball, second_ball_speed

    reward_options = ["Enlarge", "Shrink Opponent", "Freeze Opponent", "Second Ball"]
    reward = random.choice(reward_options)
    reward_message = f"Player {player} Reward: {reward}"
    reward_timer = pygame.time.get_ticks()
    reward_effect_timer = pygame.time.get_ticks()
    reward_active = True

    if reward_sound:
        reward_sound.play()

    if reward == "Enlarge":
        if player == PLAYER1:
            paddle1.height = 150
        else:
            paddle2.height = 150
    elif reward == "Shrink Opponent":
        if player == PLAYER1:
            paddle2.height = 60
        else:
            paddle1.height = 60
    elif reward == "Freeze Opponent":
        now = pygame.time.get_ticks()
        if player == PLAYER1:
            paddle2_frozen = True
            paddle2_frozen_time = now
        else:
            paddle1_frozen = True
            paddle1_frozen_time = now
    elif reward == "Second Ball":
        if not second_ball:
            second_ball = ball.copy()
            second_ball_speed = [-ball_speed[0], ball_speed[1]]

def move_ball(b, speed):
    global score1, score2, game_over, winner, second_ball

    b.x += speed[0]
    b.y += speed[1]

    if b.top <= 0 or b.bottom >= SCREEN_HEIGHT:
        speed[1] *= -1

    if b.colliderect(paddle1) or b.colliderect(paddle2):
        speed[0] *= -1
        if hit_sound:
            hit_sound.play()

    if b.left <= 0:
        score2 += 1
        if goal_sound: goal_sound.play()
        apply_reward(PLAYER2)
        if b == ball:
            reset_ball(PLAYER1)
        else:
            second_ball = None

    elif b.right >= SCREEN_WIDTH:
        score1 += 1
        if goal_sound: goal_sound.play()
        apply_reward(PLAYER1)
        if b == ball:
            reset_ball(PLAYER2)
        else:
            second_ball = None

    if score1 >= max_score:
        game_over = True
        winner = "Player 1"
        match_history.append(f"Player 1 won {score1} : {score2}")
    elif score2 >= max_score:
        game_over = True
        winner = "Player 2"
        match_history.append(f"Player 2 won {score1} : {score2}")

def update_game():
    move_ball(ball, ball_speed)
    if second_ball:
        move_ball(second_ball, second_ball_speed)

def reset_rewards():
    global reward_active, paddle1_frozen, paddle2_frozen
    now = pygame.time.get_ticks()

    if reward_active and now - reward_effect_timer > REWARD_DURATION:
        paddle1.height = paddle1_original_height
        paddle2.height = paddle2_original_height
        reward_active = False

    if paddle1_frozen and now - paddle1_frozen_time > FREEZE_DURATION:
        paddle1_frozen = False
    if paddle2_frozen and now - paddle2_frozen_time > FREEZE_DURATION:
        paddle2_frozen = False

def draw():
    global show_countdown
    screen.blit(background, (0, 0))

    color1 = light_blue if paddle1_frozen else blue
    color2 = light_blue if paddle2_frozen else red

    s = pygame.Surface((paddle1.width, paddle1.height), pygame.SRCALPHA)
    s.fill((*color1, 180))
    screen.blit(s, (paddle1.x, paddle1.y))
    pygame.draw.rect(screen, color1, paddle1, 3)

    s2 = pygame.Surface((paddle2.width, paddle2.height), pygame.SRCALPHA)
    s2.fill((*color2, 180))
    screen.blit(s2, (paddle2.x, paddle2.y))
    pygame.draw.rect(screen, color2, paddle2, 3)  

    pygame.draw.ellipse(screen, yellow, ball)
    if second_ball:
        pygame.draw.ellipse(screen, purple, second_ball)

    game_title_text = big_font.render("Ping Pong Game", True, black)
    screen.blit(game_title_text, (SCREEN_WIDTH//2 - game_title_text.get_width()//2, 10))

    name1 = status_font.render("Player 1", True, color1)
    name2 = status_font.render("Player 2", True, color2)
    
    score_text = score_font.render(f"{score1} : {score2}", True, orange)
    y_pos = game_title_text.get_height() + 40
    screen.blit(name1, (100, y_pos))
    screen.blit(name2, (SCREEN_WIDTH - 220, y_pos))
    screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, y_pos))

    time_text = font_timer.render(f"Time: {elapsed_time//60:02}:{elapsed_time%60:02}", True, red)
    screen.blit(time_text, (10, 10))

    if reward_message and pygame.time.get_ticks() - reward_timer < REWARD_DURATION:
        reward_text = status_font.render(reward_message, True, purple)
        screen.blit(reward_text, (SCREEN_WIDTH//2 - reward_text.get_width()//2, SCREEN_HEIGHT - 40))

    if show_countdown:
        cd = 3 - (pygame.time.get_ticks() - countdown_start) // 1000
        if cd <= 0:
            show_countdown = False
        else:
            cd_text = str(cd)
            cd_text_surface = big_font.render(cd_text, True, green)
            screen.blit(cd_text_surface, (SCREEN_WIDTH // 2 - cd_text_surface.get_width() // 2, SCREEN_HEIGHT // 2 - cd_text_surface.get_height() // 2))

    if paused and not game_over:
        pause_text = big_font.render("PAUSED", True, yellow)
        screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2 - 100))

    if game_over:
        win_text = big_font.render(f"{winner} Wins", True, yellow)
        screen.blit(win_text, (SCREEN_WIDTH//2 - win_text.get_width()//2, SCREEN_HEIGHT//2 - 100))

        play_again_btn = pygame.Rect(SCREEN_WIDTH//2 - 220, SCREEN_HEIGHT//2 + 50, 200, 50)
        pygame.draw.rect(screen, green, play_again_btn)
        text = status_font.render("PLAY AGAIN", True, white)
        screen.blit(text, (play_again_btn.centerx - text.get_width() // 2, play_again_btn.centery - text.get_height() // 2))
        
        main_menu_btn = pygame.Rect(SCREEN_WIDTH//2 + 20, SCREEN_HEIGHT//2 + 50, 200, 50)
        pygame.draw.rect(screen, green, main_menu_btn)
        text = status_font.render("MAIN MENU", True, white)
        screen.blit(text, (main_menu_btn.centerx - text.get_width() // 2, main_menu_btn.centery - text.get_height() // 2))
        
    pygame.display.flip()

def draw_main_menu():
    if main_menu_bg:
        screen.blit(main_menu_bg, (0, 0))
    else:
        screen.fill(black)

    title_text = font_title.render("PING PONG GAME", True, red)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))

    start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 300, 200, 60)
    results_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 400, 200, 60)
    quit_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 500, 200, 60)

    pygame.draw.rect(screen, orange, start_button)
    pygame.draw.rect(screen, green, results_button)
    pygame.draw.rect(screen, purple , quit_button)

    start_text = big_font.render("START", True, white)
    results_text = big_font.render("RESULTS", True, white)
    quit_text = big_font.render("QUIT", True, white)

    screen.blit(start_text, (start_button.centerx - start_text.get_width() // 2, start_button.centery - start_text.get_height() // 2))
    screen.blit(results_text, (results_button.centerx - results_text.get_width() // 2, results_button.centery - results_text.get_height() // 2))
    screen.blit(quit_text, (quit_button.centerx - quit_text.get_width() // 2, quit_button.centery - quit_text.get_height() // 2))

    pygame.display.flip()
    return start_button, results_button, quit_button

def draw_results():
    screen.fill(black)
    title_text = big_font.render("MATCH HISTORY", True, white)
    screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 30))

    y = 100
    for match in match_history[-10:]:  # Show last 10 results
        text = status_font.render(match, True, white)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y))
        y += 40

    back_button = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50)
    pygame.draw.rect(screen, blue, back_button)
    back_text = big_font.render("BACK", True, white)
    screen.blit(back_text, (back_button.centerx - back_text.get_width() // 2, back_button.centery - back_text.get_height() // 2))

    pygame.display.flip()
    return back_button

# Reset game function
def reset_game():
    global score1, score2, game_over, winner, paused, second_ball
    score1 = 0
    score2 = 0
    game_over = False
    winner = ""
    paused = False
    second_ball = None
    reset_ball(PLAYER1)

# Main loop
running = True
while running:
    clock.tick(60)
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if main_menu:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                start_button, results_button, quit_button = draw_main_menu()
                if start_button.collidepoint(mx, my):
                    main_menu = False
                    reset_game()
                    countdown_start = pygame.time.get_ticks()
                    show_countdown = True
                    start_time = pygame.time.get_ticks()
                elif results_button.collidepoint(mx, my):
                    main_menu = False
                    show_results = True
                elif quit_button.collidepoint(mx, my):
                    running = False

        elif show_results:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                back_button = draw_results()
                if back_button.collidepoint(mx, my):
                    show_results = False
                    main_menu = True

        else:  # In game or game over
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    paddle1_speed = -7 if not paddle1_frozen else 0
                elif event.key == pygame.K_s:
                    paddle1_speed = 7 if not paddle1_frozen else 0
                elif event.key == pygame.K_UP:
                    paddle2_speed = -7 if not paddle2_frozen else 0
                elif event.key == pygame.K_DOWN:
                    paddle2_speed = 7 if not paddle2_frozen else 0
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_ESCAPE:
                    main_menu = True
                    show_results = False

            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_w, pygame.K_s):
                    paddle1_speed = 0
                elif event.key in (pygame.K_UP, pygame.K_DOWN):
                    paddle2_speed = 0

            if game_over and event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                play_again_btn = pygame.Rect(SCREEN_WIDTH//2 - 220, SCREEN_HEIGHT//2 + 50, 200, 50)
                main_menu_btn = pygame.Rect(SCREEN_WIDTH//2 + 20, SCREEN_HEIGHT//2 + 50, 200, 50)
                if play_again_btn.collidepoint(mx, my):
                    reset_game()
                elif main_menu_btn.collidepoint(mx, my):
                    main_menu = True

    if not main_menu and not show_results:
        if not paused and not game_over and not show_countdown:
            # Move paddles
            if not paddle1_frozen:
                paddle1.y += paddle1_speed
            if not paddle2_frozen:
                paddle2.y += paddle2_speed

            # Keep paddles in screen
            if paddle1.top < 0:
                paddle1.top = 0
            if paddle1.bottom > SCREEN_HEIGHT:
                paddle1.bottom = SCREEN_HEIGHT
            if paddle2.top < 0:
                paddle2.top = 0
            if paddle2.bottom > SCREEN_HEIGHT:
                paddle2.bottom = SCREEN_HEIGHT

            update_game()
            reset_rewards()

        draw()

    elif main_menu:
        draw_main_menu()

    elif show_results:
        draw_results()

pygame.quit()
sys.exit()
