from transformers import pipeline
from collections import Counter

class AIManager:
    def __init__(self):
        """
        Initialize the AI manager with pre-trained models.
        """
        self.text_generator = None
        self.text_rephraser = None
        self.letter_frequency = Counter("etaoinshrdlcumwfgypbvkjxqz")  # English letter frequency

        try:
            self.text_generator = pipeline("text-generation", model="gpt2")
            self.text_rephraser = pipeline("text2text-generation", model="t5-small")
        except Exception as e:  # Replaced PipelineException with Exception
            print(f"AI models could not be loaded: {e}")
            print("AI-powered features will be disabled.")

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
                result = self.text_rephraser(f"Rephrase: {riddle}")
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
                    truncation=True  # Explicitly enable truncation
                )
                return result[0]["generated_text"]
            except Exception as e:
                print(f"Error generating hint: {e}")
        return "No hint available."

    def generate_riddle(self, word):
        """
        Generate a riddle for a given word using a transformer model.
        """
        if self.text_generator:
            try:
                result = self.text_generator(
                    f"Create a riddle for the word '{word}':",
                    max_length=50,
                    truncation=True  # Explicitly enable truncation
                )
                return result[0]["generated_text"]
            except Exception as e:
                print(f"Error generating riddle: {e}")
        return f"What is related to '{word}'?"
