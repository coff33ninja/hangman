# ui_manager.py
import pygame
from config import WIDTH, HEIGHT, WHITE, BLACK, GRAY

class Button:
    def __init__(self, x, y, width, height, text, font, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.action = action

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, color, self.rect)
        text_surface = self.font.render(self.text, True, BLACK)
        screen.blit(
            text_surface,
            (
                self.rect.x + (self.rect.width - text_surface.get_width()) // 2,
                self.rect.y + (self.rect.height - text_surface.get_height()) // 2,
            ),
        )

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

class UIManager:
    def __init__(self, screen, theme_manager):
        """
        Initialize UI with screen, preloaded assets, and theme manager.
        """
        self.screen = screen
        self.theme_manager = theme_manager
        self.font = pygame.font.SysFont(None, int(HEIGHT * 0.05))  # Dynamic font size
        self.small_font = pygame.font.SysFont(None, int(HEIGHT * 0.03))
        self.image_sets = {
            1: [
                pygame.image.load(f"assets/images/level1_stage{i}.png")
                for i in range(7)
            ],
            2: [
                pygame.image.load(f"assets/images/level2_stage{i}.png")
                for i in range(10)
            ],
            3: [
                pygame.image.load(f"assets/images/level3_stage{i}.png")
                for i in range(14)
            ],
        }
        self.last_hint = None
        self.buttons = []
        pygame.mixer.init()
        self.bg_music = None
        self.correct_sound = None
        self.wrong_sound = None
        self.load_theme_assets()

    def load_theme_assets(self):
        """
        Load theme-specific assets including sounds.
        """
        theme = self.theme_manager.current_theme
        self.bg_music = pygame.mixer.Sound(self.theme_manager.get_asset("sounds") + "/background.wav")
        self.correct_sound = pygame.mixer.Sound(self.theme_manager.get_asset("sounds") + "/correct.wav")
        self.wrong_sound = pygame.mixer.Sound(self.theme_manager.get_asset("sounds") + "/wrong.wav")
        self.bg_music.play(loops=-1)

    def play_sound(self, correct):
        """
        Play sound effect based on correctness.
        """
        (self.correct_sound if correct else self.wrong_sound).play()

    def draw_game(self, game):
        """
        Draw the current game state, including hints and incorrect guesses.
        """
        self.screen.fill(WHITE)
        # Draw Hangman
        hangman_img = self.image_sets[game.difficulty][game.hangman_stage]
        img_width, img_height = hangman_img.get_size()
        self.screen.blit(hangman_img, ((WIDTH - img_width) // 2, int(HEIGHT * 0.1)))

        # Draw riddle (if applicable)
        if game.current_riddle:
            self.draw_wrapped_text(game.current_riddle, self.font, BLACK, int(HEIGHT * 0.4), line_spacing=10)

        # Draw word
        word_text = self.font.render(game.get_display_word(), True, BLACK)
        self.screen.blit(word_text, ((WIDTH - word_text.get_width()) // 2, int(HEIGHT * 0.5)))

        # Draw incorrect guesses
        incorrect_guesses = [letter for letter in game.guessed_letters if letter not in game.current_word]
        incorrect_text = self.small_font.render(f"Incorrect: {', '.join(incorrect_guesses)}", True, (255, 0, 0))
        self.screen.blit(incorrect_text, (int(WIDTH * 0.1), int(HEIGHT * 0.7)))

        # Draw attempts and hints
        attempts_text = self.font.render(f"Attempts: {game.attempts_left}", True, BLACK)
        hints_text = self.font.render(f"Hints: {game.hint_count}", True, BLACK)
        self.screen.blit(attempts_text, (int(WIDTH * 0.1), int(HEIGHT * 0.8)))
        self.screen.blit(hints_text, (int(WIDTH * 0.7), int(HEIGHT * 0.8)))

        # Draw last hint (if any)
        if self.last_hint:
            hint_text = self.small_font.render(self.last_hint, True, GRAY)
            self.screen.blit(hint_text, ((WIDTH - hint_text.get_width()) // 2, int(HEIGHT * 0.9)))

        # Draw buttons
        self.draw_buttons()

    def draw_wrapped_text(self, text, font, color, y_start, line_spacing=5):
        """
        Draw text wrapped to fit within the screen width.
        """
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if font.size(test_line)[0] <= WIDTH * 0.8:  # Check if the line fits within 80% of the screen width
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        y = y_start
        for line in lines:
            line_surface = font.render(line, True, color)
            self.screen.blit(line_surface, ((WIDTH - line_surface.get_width()) // 2, y))
            y += font.get_height() + line_spacing

    def draw_game_over(self, game, win):
        """
        Draw the game over screen with the final word and play again option.
        """
        self.screen.fill(WHITE)
        result_text = "You Win!" if win else "You Lose!"
        result_color = (0, 255, 0) if win else (255, 0, 0)
        result_surface = self.font.render(result_text, True, result_color)
        self.screen.blit(result_surface, ((WIDTH - result_surface.get_width()) // 2, int(HEIGHT * 0.3)))

        # Show the word with color styles
        word_color = (0, 255, 0) if win else (255, 0, 0)
        word_surface = self.font.render(f"The word was: {game.current_word}", True, word_color)
        self.screen.blit(word_surface, ((WIDTH - word_surface.get_width()) // 2, int(HEIGHT * 0.4)))

        # Play again button
        play_again_button = Button(
            WIDTH // 2 - 100, int(HEIGHT * 0.6), 200, 50, "Play Again", self.font, GRAY, WHITE, action=None
        )
        play_again_button.draw(self.screen)
        self.buttons = [play_again_button]  # Replace buttons with only the play again button

    def draw_menu(self):
        """
        Draw the main menu.
        """
        self.screen.fill(WHITE)
        menu_text = self.font.render("Select an option:", True, BLACK)
        self.screen.blit(menu_text, ((WIDTH - menu_text.get_width()) // 2, int(HEIGHT * 0.1)))
        # Draw buttons
        self.draw_buttons()

    def draw_pause_screen(self):
        """
        Draw the pause screen.
        """
        self.screen.fill(GRAY)
        pause_text = self.font.render("Game Paused. Press any key to continue.", True, BLACK)
        self.screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()

    def update_hint(self, hint):
        """
        Update the last hint displayed.
        """
        self.last_hint = hint if hint else self.last_hint
        if hint:
            hint_text = self.small_font.render(hint, True, GRAY)
            self.screen.blit(hint_text, ((WIDTH - hint_text.get_width()) // 2, int(HEIGHT * 0.9)))
        else:
            self.last_hint = None

    def draw_timer(self, time_left):
        """
        Draw the countdown timer on the screen.
        """
        color = (255, 0, 0) if time_left < 10 else BLACK
        timer_text = self.font.render(f"Time Left: {time_left}s", True, color)
        self.screen.blit(timer_text, (WIDTH - 200, 50))

    def draw_power_up_buttons(self, power_ups):
        """
        Draw power-up buttons with their remaining counts.
        """
        x, y = int(WIDTH * 0.05), HEIGHT - int(HEIGHT * 0.15)
        for power_up, count in power_ups.items():
            button_text = self.small_font.render(f"{power_up} ({count})", True, BLACK)
            self.screen.blit(button_text, (x, y))
            x += int(WIDTH * 0.15)

    def draw_achievements(self, achievements):
        """
        Draw the achievements screen.
        """
        self.screen.fill(WHITE)
        y = int(HEIGHT * 0.1)
        for achievement, details in achievements.items():
            status = "Unlocked" if details["unlocked"] else "Locked"
            text = self.font.render(f"{details['description']} - {status}", True, BLACK)
            self.screen.blit(text, (int(WIDTH * 0.05), y))
            y += int(HEIGHT * 0.05)

    def create_menu_buttons(self, start_word_guess, start_riddle_time, set_difficulty, show_achievements, change_theme):
        """
        Create buttons for the main menu.
        """
        button_width = int(WIDTH * 0.2)
        button_height = int(HEIGHT * 0.1)
        spacing = int(HEIGHT * 0.05)
        self.buttons = [
            Button(WIDTH // 2 - button_width // 2, int(HEIGHT * 0.3), button_width, button_height, "Word Guess", self.font, GRAY, WHITE, start_word_guess),
            Button(WIDTH // 2 - button_width // 2, int(HEIGHT * 0.3) + button_height + spacing, button_width, button_height, "Riddle Time", self.font, GRAY, WHITE, start_riddle_time),
            Button(WIDTH // 2 - button_width // 2, int(HEIGHT * 0.3) + 2 * (button_height + spacing), button_width, button_height, "Easy", self.font, GRAY, WHITE, lambda: set_difficulty(1)),
            Button(WIDTH // 2 - button_width // 2, int(HEIGHT * 0.3) + 3 * (button_height + spacing), button_width, button_height, "Medium", self.font, GRAY, WHITE, lambda: set_difficulty(2)),
            Button(WIDTH // 2 - button_width // 2, int(HEIGHT * 0.3) + 4 * (button_height + spacing), button_width, button_height, "Hard", self.font, GRAY, WHITE, lambda: set_difficulty(3)),
            Button(WIDTH // 2 - button_width // 2, int(HEIGHT * 0.3) + 5 * (button_height + spacing), button_width, button_height, "Achievements", self.font, GRAY, WHITE, show_achievements),
            Button(WIDTH // 2 - button_width // 2, int(HEIGHT * 0.3) + 6 * (button_height + spacing), button_width, button_height, "Change Theme", self.font, GRAY, WHITE, change_theme),
        ]

    def create_game_buttons(self, use_hint, use_reveal_letter, use_extra_attempt):
        """
        Create buttons for gameplay actions.
        """
        button_width = int(WIDTH * 0.2)
        button_height = int(HEIGHT * 0.1)
        self.buttons = [
            Button(int(WIDTH * 0.1), HEIGHT - button_height - int(HEIGHT * 0.05), button_width, button_height, "Hint", self.font, GRAY, WHITE, use_hint),
            Button(int(WIDTH * 0.4), HEIGHT - button_height - int(HEIGHT * 0.05), button_width, button_height, "Reveal Letter", self.font, GRAY, WHITE, use_reveal_letter),
            Button(int(WIDTH * 0.7), HEIGHT - button_height - int(HEIGHT * 0.05), button_width, button_height, "Extra Attempt", self.font, GRAY, WHITE, use_extra_attempt),
        ]

    def draw_buttons(self):
        """
        Draw all buttons on the screen.
        """
        for button in self.buttons:
            button.draw(self.screen)

    def handle_button_click(self, event):
        """
        Handle button clicks.
        """
        for button in self.buttons:
            if button.is_clicked(event) and button.action:
                button.action()

    def draw_name_input(self, current_name):
        """
        Draw the screen for entering the player's name.
        """
        self.screen.fill(WHITE)
        title_text = self.font.render("Enter Your Name:", True, BLACK)
        self.screen.blit(title_text, ((WIDTH - title_text.get_width()) // 2, int(HEIGHT * 0.3)))

        # Display the current name being typed
        name_surface = self.font.render(current_name, True, BLACK)
        pygame.draw.rect(self.screen, GRAY, (WIDTH // 2 - 150, int(HEIGHT * 0.4), 300, 50))
        self.screen.blit(name_surface, ((WIDTH - name_surface.get_width()) // 2, int(HEIGHT * 0.4) + 10))

        # Draw a "Confirm" button
        confirm_button = Button(
            WIDTH // 2 - 100, int(HEIGHT * 0.6), 200, 50, "Confirm", self.font, GRAY, WHITE, action=None
        )
        confirm_button.draw(self.screen)
        self.buttons = [confirm_button]  # Replace buttons with only the confirm button