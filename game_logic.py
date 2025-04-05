import random

import json

import hashlib  # Reintroduced for daily challenge

from datetime import date  # Reintroduced for daily challenge

from time import time

from config import DIFFICULTY_ATTEMPTS, HINTS_PER_GAME

from content_manager import (
    load_words,
    load_riddles,
    fetch_online_riddles,
    fetch_word_definition,  # Ensure this is used
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

    def save_achievements(self, filepath="data/achievements.json"):
        """

        Save the achievements to a file.

        """

        try:
            with open(filepath, "w") as f:
                json.dump(self.achievements, f)
        except IOError as e:
            print(f"Error saving achievements: {e}")

    def load_achievements(self, filepath="data/achievements.json"):
        """

        Load the achievements from a file.

        """

        try:
            with open(filepath, "r") as f:
                self.achievements = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading achievements: {e}")

    def generate_default_achievements(self):
        """

        Ensure default achievements exist.

        """
        if not self.achievements:
            self.achievements = {
                "first_win": {"description": "Win your first game!", "unlocked": False},
                "no_hints": {
                    "description": "Win a game without using hints.",
                    "unlocked": False,
                },
                "streak_5": {"description": "Win 5 games in a row.", "unlocked": False},
            }


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

        self.achievements_manager.load_achievements()

        self.achievements_manager.generate_default_achievements()  # Ensure defaults exist

        self.current_definition = None

        self.time_limit = 60 - (difficulty - 1) * 10  # 60s easy, 50s med, 40s hard

        self.start_time = None

        self.reset_game()

    def reset_game(self):
        """

        Reset game state with a new word or riddle.

        """
        if self.mode == "word_guess":
            # Use AI-generated word if available
            self.current_word = self.ai_manager.generate_word()
            if not self.current_word:
                category = random.choice(list(self.words.keys()))
                self.current_word = random.choice(self.words[category])
            self.current_riddle = None

            # Use fetch_word_definition for training and gameplay
            definition_data = fetch_word_definition(self.current_word)
            if definition_data:
                self.ai_manager.training_data["definitions"].append(definition_data)
                self.ai_manager.save_training_data()
            self.current_definition = definition_data

            self.ai_manager.learn_from_riddles(self.riddles)  # Learn from riddles dynamically
            self.ai_manager.retrain()  # Retrain the AI with new vocabulary

        elif self.mode == "riddle_time":

            category = random.choice(list(self.riddles.keys()))

            if category == "ai_generated":

                self.current_word = random.choice(self.words["default"])

                self.current_riddle = self.ai_manager.generate_riddle(self.current_word)

            else:

                self.current_riddle, self.current_word = random.choice(
                    self.riddles[category]
                )

            self.current_definition = None

            self.ai_manager.learn_from_riddles(self.riddles)  # Learn from riddles dynamically
            self.ai_manager.retrain()  # Retrain the AI with new vocabulary

        self.guessed_letters.clear()

        self.attempts_left = DIFFICULTY_ATTEMPTS[self.difficulty]

        self.hangman_stage = 0

        self.start_time = time()

        self.ai_manager.generate_files()  # Save AI state dynamically

    def get_time_left(self):
        """

        Get the remaining time for the current game.

        """

        if self.start_time:
            return max(0, self.time_limit - int(time() - self.start_time))
        return self.time_limit

    def start_two_player(self, player1_word):
        """

        Start a two-player game with a word provided by Player 1.

        """

        self.mode = "word_guess"
        self.current_word = player1_word.upper()
        self.current_riddle = None
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

        self.achievements_manager.check_achievements({
            "win": win,
            "hints_used": HINTS_PER_GAME - self.hint_count,
            "streak": 5,  # Example streak logic
        })
        self.achievements_manager.save_achievements()

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
            filtered_data = self.ai_manager.training_data.get("filtered_data", {}).get(self.current_word, {})
            if filtered_data:
                self.hint_count -= 1
                return f"Hint: {random.choice(filtered_data.get('definitions', [{'definition': 'No hints available.'}]))['definition']}"
            else:
                self.hint_count -= 1
                return "No hints available."

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

    def ask_ai_question(self):
        """
        Ask the AI a question and get its answer.
        """
        question = input("Ask the AI a question: ")
        answer = self.ai_manager.answer_question(question)
        print(f"AI's answer: {answer}")

    def ai_asks_question(self):
        """
        Let the AI ask a question and check the player's answer.
        """
        question = self.ai_manager.ask_question()
        print(f"AI asks: {question}")
        player_answer = input("Your answer: ")
        correct_answer = self.ai_manager.answer_question(question)
        if player_answer.lower() == correct_answer.lower():
            print("Correct!")
        else:
            print(f"Wrong! The correct answer was: {correct_answer}")

    def research_word(self, word):
        """
        Research a word and display the results.
        """
        research_results = self.ai_manager.research_topic(word)
        print(f"Research results for '{word}':\n{research_results}")

    def fetch_word_examples(self):
        """
        Fetch example sentences for the current word.
        """
        if self.current_word:
            examples = self.ai_manager.fetch_word_examples(self.current_word)
            if examples:
                print(f"Examples for '{self.current_word}': {examples}")
            else:
                print(f"No examples found for '{self.current_word}'.")

    def fetch_word_synonyms(self):
        """
        Fetch synonyms for the current word.
        """
        if self.current_word:
            synonyms = self.ai_manager.fetch_word_synonyms(self.current_word)
            if synonyms:
                print(f"Synonyms for '{self.current_word}': {synonyms}")
            else:
                print(f"No synonyms found for '{self.current_word}'.")
