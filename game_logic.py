import random

import json

import hashlib  # Reintroduced for daily challenge

from datetime import date  # Reintroduced for daily challenge

from config import DIFFICULTY_ATTEMPTS, HINTS_PER_GAME

from content_manager import (
    load_words,
    load_riddles,
    fetch_online_riddles,
    fetch_word_definition,
)

from ai_manager import AIManager

from powerup_manager import PowerUpManager


class AchievementsManager:

    def __init__(self):
        """

        Initialize achievements with their conditions and statuses.

        """

        self.achievements = {
            "first_win": {"description": "Win your first game!", "unlocked": False},
            "no_hints": {
                "description": "Win a game without using hints.",
                "unlocked": False,
            },
            "streak_5": {"description": "Win 5 games in a row.", "unlocked": False},
        }

    def check_achievements(self, game_state):
        """

        Check and unlock achievements based on the current game state.

        """

        if game_state["win"] and not self.achievements["first_win"]["unlocked"]:

            self.achievements["first_win"]["unlocked"] = True

        if game_state["win"] and game_state["hints_used"] == 0:

            self.achievements["no_hints"]["unlocked"] = True

        if game_state["streak"] >= 5:

            self.achievements["streak_5"]["unlocked"] = True

    def get_unlocked_achievements(self):
        """

        Return a list of unlocked achievements.

        """

        return [key for key, value in self.achievements.items() if value["unlocked"]]


class HangmanGame:

    def __init__(self, mode="word_guess", difficulty=1):
        """

        Initialize the game with a mode and difficulty level.

        Modes: 'word_guess', 'riddle_time'

        Difficulty: 1 (6 attempts), 2 (9 attempts), 3 (13 attempts)

        """

        self.mode = mode

        self.difficulty = difficulty

        self.attempts_left = DIFFICULTY_ATTEMPTS[difficulty]

        self.hint_count = HINTS_PER_GAME

        self.guessed_letters = set()

        self.hangman_stage = 0

        self.max_stages = {1: 6, 2: 9, 3: 13}

        self.words = load_words()

        self.riddles = load_riddles()

        self.riddles.update(fetch_online_riddles())  # Fetch online riddles

        self.power_ups = PowerUpManager()

        self.ai_manager = AIManager()

        self.achievements_manager = AchievementsManager()

        self.current_definition = None

        self.reset_game()

    def reset_game(self):
        """

        Reset game state with a new word or riddle.

        """

        if self.mode == "word_guess":

            category = random.choice(list(self.words.keys()))

            self.current_word = random.choice(self.words[category])

            self.current_riddle = None

            self.current_definition = fetch_word_definition(self.current_word)

        else:  # riddle_time

            category = random.choice(list(self.riddles.keys()))

            if category == "ai_generated":

                self.current_word = random.choice(self.words["default"])

                self.current_riddle = self.ai_manager.generate_riddle(self.current_word)

            else:

                self.current_riddle, self.current_word = random.choice(
                    self.riddles[category]
                )

            self.current_definition = None

        self.guessed_letters.clear()

        self.attempts_left = DIFFICULTY_ATTEMPTS[self.difficulty]

        self.hangman_stage = 0

    def guess_letter(self, letter):
        """

        Process a letter guess. Returns True if correct, False if incorrect or invalid.

        """

        letter = letter.upper()

        if letter in self.guessed_letters or len(letter) != 1 or not letter.isalpha():

            return False

        self.guessed_letters.add(letter)

        if self.mode == "word_guess" and letter not in self.current_word:

            self.attempts_left -= 1

            self.hangman_stage = min(
                self.hangman_stage + 1, self.max_stages[self.difficulty]
            )

            return False

        elif self.mode == "riddle_time" and letter not in self.current_word:

            self.attempts_left -= 1

            self.hangman_stage = min(
                self.hangman_stage + 1, self.max_stages[self.difficulty]
            )

            return False

        return True

    def track_player_stats(self, player_name, win):
        """

        Track player stats for wins and losses.

        """

        from score_manager import ScoreManager

        score_manager = ScoreManager()

        score = 100 if win else 0  # Example scoring logic

        score_manager.add_score(player_name, score)

    def get_display_word(self):
        """

        Return the word with guessed letters revealed and others as underscores.

        """

        return " ".join(
            letter if letter in self.guessed_letters else "_"
            for letter in self.current_word
        )

    def provide_hint(self):
        """

        Provide a hint: either a letter, definition, or AI-generated hint.

        Returns the hint or None.

        """

        if self.hint_count <= 0:

            return None

        if self.mode == "word_guess":

            if self.current_definition and random.random() < 0.5:

                self.hint_count -= 1

                return f"Definition: {self.current_definition}"

            else:

                self.hint_count -= 1

                return self.ai_manager.generate_hint(self.current_word)

        elif self.mode == "riddle_time":

            self.hint_count -= 1

            return self.ai_manager.rephrase_riddle(self.current_riddle)

        return None

    def check_win(self):
        """

        Check if the player has won by guessing all letters.

        """

        return all(letter in self.guessed_letters for letter in self.current_word)

    def check_lose(self):
        """

        Check if the player has lost by running out of attempts.

        """

        return self.attempts_left <= 0

    def get_game_state(self):
        """

        Return the current game state as a dictionary.

        """

        return {
            "mode": self.mode,
            "difficulty": self.difficulty,
            "attempts_left": self.attempts_left,
            "guessed_letters": list(self.guessed_letters),
            "current_word": self.current_word,
            "current_riddle": self.current_riddle,
        }

    def save_game_state(self, filepath="data/game_state.json"):
        """

        Save the current game state to a file.

        """

        state = self.get_game_state()

        try:

            with open(filepath, "w") as f:

                json.dump(state, f)

        except IOError as e:

            print(f"Error saving game state: {e}")

    def load_game_state(self, filepath="data/game_state.json"):
        """

        Load the game state from a file.

        """

        try:

            with open(filepath, "r") as f:

                state = json.load(f)

                self.mode = state["mode"]

                self.difficulty = state["difficulty"]

                self.attempts_left = state["attempts_left"]

                self.guessed_letters = set(state["guessed_letters"])

                self.current_word = state["current_word"]

                self.current_riddle = state["current_riddle"]

        except (IOError, json.JSONDecodeError) as e:

            print(f"Error loading game state: {e}")

    def get_daily_challenge(self):
        """

        Generate a daily challenge word or riddle based on the current date.

        """

        seed = hashlib.md5(str(date.today()).encode()).hexdigest()

        random.seed(seed)

        if self.mode == "word_guess":

            category = random.choice(list(self.words.keys()))

            return random.choice(self.words[category])

        elif self.mode == "riddle_time":

            category = random.choice(list(self.riddles.keys()))

            return random.choice(self.riddles[category])

        return None
