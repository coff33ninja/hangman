import json
from transformers import pipeline
from collections import Counter
from content_manager import fetch_word_definition

class AIManager:
    def __init__(self, training_file="data/training_data.json"):
        """
        Initialize the AI manager with pre-trained models and training data file.
        """
        self.text_generator = None
        self.text_rephraser = None
        self.letter_frequency = Counter("etaoinshrdlcumwfgypbvkjxqz")  # English letter frequency
        self.training_file = training_file
        self.training_data = {"riddles": [], "definitions": []}

        try:
            self.text_generator = pipeline("text-generation", model="gpt2")
            self.text_rephraser = pipeline("text2text-generation", model="t5-small")
        except Exception as e:
            print(f"AI models could not be loaded: {e}")
            print("AI-powered features will be disabled.")

        self.load_training_data()

    def load_training_data(self):
        """
        Load existing training data from the training file.
        """
        try:
            with open(self.training_file, "r") as f:
                self.training_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("No existing training data found. Starting fresh.")

    def save_training_data(self):
        """
        Save the current training data to the training file.
        """
        try:
            with open(self.training_file, "w") as f:
                json.dump(self.training_data, f, indent=4)
        except IOError as e:
            print(f"Error saving training data: {e}")

    def suggest_next_letter(self, word, guessed_letters):
        """
        Suggest the next letter to guess based on letter frequency and unguessed letters.
        """
        unguessed = [letter for letter in word if letter not in guessed_letters]
        if unguessed:
            return max(unguessed, key=lambda letter: self.letter_frequency[letter])
        return None

    def rephrase_riddle(self, riddle):
        """
        Rephrase a riddle using a transformer model.
        """
        if self.text_rephraser:
            try:
                result = self.text_rephraser(f"Rephrase: {riddle}")  # Keep this as an f-string since it has a placeholder
                return result[0]["generated_text"]
            except Exception as e:
                print(f"Error rephrasing riddle: {e}")
        return riddle

    def generate_hint(self, word):
        """
        Generate a hint for the word using a transformer model.
        """
        if self.text_generator:
            try:
                result = self.text_generator(
                    f"Hint for the word '{word}':",
                    max_length=50,
                    truncation=True
                )
                return result[0]["generated_text"]
            except Exception:
                pass
        return f"The word has {len(word)} letters."

    def generate_riddle(self, word):
        """
        Generate a riddle for a given word using a transformer model.
        """
        if self.text_generator:
            try:
                result = self.text_generator(
                    f"Create a riddle for the word '{word}':",
                    max_length=50,
                    truncation=True
                )
                riddle = result[0]["generated_text"]
                self.training_data["riddles"].append({"word": word, "riddle": riddle})
                self.save_training_data()
                return riddle
            except Exception:
                pass
        return f"I am something you call a '{word}'. What am I?"

    def lookup_word_meaning(self, word):
        """
        Use the dictionary API to fetch the meaning of a word and save it to training data.
        """
        definition_data = fetch_word_definition(word)
        if definition_data and "definitions" in definition_data:
            self.training_data["definitions"].append(definition_data)
            self.save_training_data()
            definitions = definition_data["definitions"]
            if definitions:
                return f"{word.capitalize()} ({definitions[0]['partOfSpeech']}): {definitions[0]['definition']}"
        return f"Could not find a definition for '{word}'."
