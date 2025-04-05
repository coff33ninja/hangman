# main.py
import pygame
from config import WIDTH, HEIGHT, FPS
from game_logic import HangmanGame, load_words
from ui_manager import UIManager
from powerup_manager import PowerUpManager
from time import time
from theme_manager import ThemeManager
from voice_input import VoiceInput
from ai_manager import AIManager
from threading import Thread

try:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Hangman by DJ")
    clock = pygame.time.Clock()  # Corrected to pygame.time.Clock()
except Exception as e:
    print(f"Error initializing Pygame: {e}")
    exit(1)

game_mode = "name_input"  # Start with the name input screen
player_name = ""  # Store the player's name
difficulty = 1
game = None
theme_manager = ThemeManager()
Thread(target=theme_manager.generate_themes_async).start()  # Generate themes in a separate thread
ui = UIManager(screen, theme_manager)
Thread(target=ui.load_theme_assets_async).start()  # Load theme assets in a separate thread
voice_input = VoiceInput()
ai_manager = AIManager()  # Initialize AIManager with training data support
words = load_words(ai_manager=ai_manager)  # Train AI on loaded words
paused = False

start_time = time()
time_limit = 60  # 60 seconds for timed mode

player_turn = None

def start_word_guess():
    global game, game_mode, start_time
    game = HangmanGame("word_guess", difficulty)
    game.power_ups = PowerUpManager()
    game_mode = "word_guess"
    start_time = time()
    ui.create_game_buttons(
        use_hint=lambda: handle_hint(),
        use_reveal_letter=lambda: handle_power_up("reveal_letter"),
        use_extra_attempt=lambda: handle_power_up("extra_attempt"),
    )

def start_riddle_time():
    global game, game_mode, start_time
    game = HangmanGame("riddle_time", difficulty)
    game.power_ups = PowerUpManager()
    game_mode = "riddle_time"
    start_time = time()
    ui.create_game_buttons(
        use_hint=lambda: handle_hint(),
        use_reveal_letter=lambda: handle_power_up("reveal_letter"),
        use_extra_attempt=lambda: handle_power_up("extra_attempt"),
    )

def set_difficulty(level):
    global difficulty
    difficulty = level
    print(f"Difficulty set to {level}")

def handle_hint():
    hint = game.provide_hint()
    if hint:
        print(f"Hint: {hint}")
        ui.update_hint(hint)

def handle_word_meaning(word):
    """
    Fetch and display the meaning of a word using AIManager.
    """
    meaning = ai_manager.lookup_word_meaning(word)
    print(f"Meaning: {meaning}")

def handle_power_up(power_up):
    if game.use_power_up(power_up):
        print(f"Used power-up: {power_up}")

def handle_voice_guess():
    guess = voice_input.get_voice_input()
    if guess and guess.isalpha():
        game.guess_letter(guess[0])

def toggle_pause():
    global paused
    paused = not paused

def show_achievements():
    global game_mode
    game_mode = "achievements"

def change_theme():
    available_themes = theme_manager.get_available_themes()
    current_index = available_themes.index(theme_manager.current_theme)
    next_index = (current_index + 1) % len(available_themes)
    theme_manager.load_theme(available_themes[next_index])
    ui.load_theme_assets()

def create_menu_buttons():
    ui.create_menu_buttons(start_word_guess, start_riddle_time, set_difficulty, show_achievements, change_theme)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            ui.handle_button_click(event)
            # Handle confirm button on name input screen
            if game_mode == "name_input" and ui.buttons:
                if ui.buttons[0].is_clicked(event) and player_name.strip():
                    game_mode = "menu"
                    create_menu_buttons()
            # Handle play again button
            if game_mode == "game_over" and ui.buttons:
                if ui.buttons[0].is_clicked(event):
                    game_mode = "menu"
                    create_menu_buttons()
        elif event.type == pygame.KEYDOWN:
            if game_mode == "name_input":
                # Handle typing for the player's name
                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif len(player_name) < 15 and event.unicode.isprintable():
                    player_name += event.unicode
            elif game_mode in ["word_guess", "riddle_time"]:
                # Allow typing guesses during gameplay
                if event.unicode.isalpha() and len(event.unicode) == 1:
                    guessed_letter = event.unicode.upper()
                    game.guess_letter(guessed_letter)
            if event.key == pygame.K_p:
                toggle_pause()

    if paused:
        ui.draw_pause_screen()
        continue

    # Update game state
    if game_mode in ["word_guess", "riddle_time"]:
        if game.check_win():
            game.track_player_stats(player_name, win=True)
            game_mode = "game_over"
            ui.draw_game_over(game, win=True)
        elif game.check_lose() or (time() - start_time > time_limit):
            game.track_player_stats(player_name, win=False)
            game_mode = "game_over"
            ui.draw_game_over(game, win=False)

    # Draw
    if game_mode == "name_input":
        ui.draw_name_input(player_name)
    elif game_mode == "menu":
        ui.draw_menu()
    elif game_mode in ["word_guess", "riddle_time"]:
        time_left = max(0, time_limit - int(time() - start_time))
        ui.draw_game(game)
        ui.draw_timer(time_left)
        ui.draw_buttons()
    elif game_mode == "game_over":
        ui.draw_game_over(game, win=False)
    elif game_mode == "achievements":
        ui.draw_achievements(game.achievements_manager.achievements)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()