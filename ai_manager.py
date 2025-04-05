import json
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from collections import Counter
from content_manager import fetch_word_definition
import random

class AIManager:
    def __init__(self, training_file="data/training_data.json"):
        """
        Initialize the AI manager with pre-trained models and training data file.
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Device set to use {self.device}")
        self.text_generator = None
        self.text_rephraser = None
        self.text_classifier = None
        self.synonym_generator = None
        self.custom_tokenizer = None
        self.custom_model = None
        self.question_answering_model = None
        self.letter_frequency = Counter("etaoinshrdlcumwfgypbvkjxqz")  # English letter frequency
        self.training_file = training_file
        self.training_data = {"riddles": [], "definitions": [], "categories": []}

        try:
            self.text_generator = pipeline("text-generation", model="gpt2", device=0 if self.device == "cuda" else -1)
            self.text_rephraser = pipeline("text2text-generation", model="t5-small", device=0 if self.device == "cuda" else -1)
            self.text_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=0 if self.device == "cuda" else -1)
            self.synonym_generator = pipeline("text2text-generation", model="t5-small", device=0 if self.device == "cuda" else -1)
            self.custom_tokenizer = AutoTokenizer.from_pretrained("t5-small")
            self.custom_model = AutoModelForSeq2SeqLM.from_pretrained("t5-small").to(self.device)
            self.question_answering_model = pipeline("question-answering", model="distilbert-base-cased-distilled-squad", device=0 if self.device == "cuda" else -1)
        except Exception as e:
            print(f"AI models could not be loaded: {e}")
            print("AI-powered features will be limited.")

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
            self.save_training_data()  # Create an empty training data file

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
        if self.custom_tokenizer and self.custom_model:
            try:
                inputs = self.custom_tokenizer(f"Rephrase: {riddle}", return_tensors="pt", max_length=512, truncation=True)
                outputs = self.custom_model.generate(inputs.input_ids, max_length=50, num_beams=5, early_stopping=True)
                return self.custom_tokenizer.decode(outputs[0], skip_special_tokens=True)
            except Exception as e:
                print(f"Error rephrasing riddle: {e}")
        return riddle

    def generate_hint(self, word):
        """
        Generate a hint for the word using a transformer model.
        """
        if self.custom_tokenizer and self.custom_model:
            try:
                inputs = self.custom_tokenizer(f"Hint for the word '{word}':", return_tensors="pt", max_length=512, truncation=True)
                outputs = self.custom_model.generate(inputs.input_ids, max_length=50, num_beams=5, early_stopping=True)
                return self.custom_tokenizer.decode(outputs[0], skip_special_tokens=True)
            except Exception as e:
                print(f"Error generating hint: {e}")
        return f"The word has {len(word)} letters."

    def generate_riddle(self, word):
        """
        Generate a riddle for a given word using a transformer model.
        """
        if self.custom_tokenizer and self.custom_model:
            try:
                inputs = self.custom_tokenizer(f"Create a riddle for the word '{word}':", return_tensors="pt", max_length=512, truncation=True)
                outputs = self.custom_model.generate(inputs.input_ids, max_length=50, num_beams=5, early_stopping=True)
                riddle = self.custom_tokenizer.decode(outputs[0], skip_special_tokens=True)
                self.training_data["riddles"].append({"word": word, "riddle": riddle})
                self.save_training_data()
                return riddle
            except Exception as e:
                print(f"Error generating riddle: {e}")
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

    def classify_word(self, word, candidate_labels):
        """
        Classify a word into one of the candidate labels using zero-shot classification.
        """
        if self.text_classifier:
            try:
                result = self.text_classifier(word, candidate_labels)
                return result["labels"][0]  # Return the top label
            except Exception as e:
                print(f"Error classifying word: {e}")
        return "uncategorized"

    def generate_synonyms(self, word):
        """
        Generate synonyms for a word using a transformer model.
        """
        if self.custom_tokenizer and self.custom_model:
            try:
                inputs = self.custom_tokenizer(f"Generate synonyms for: {word}", return_tensors="pt", max_length=512, truncation=True)
                outputs = self.custom_model.generate(inputs.input_ids, max_length=50, num_beams=5, early_stopping=True)
                return self.custom_tokenizer.decode(outputs[0], skip_special_tokens=True).split(", ")
            except Exception as e:
                print(f"Error generating synonyms: {e}")
        return []

    def train_on_words(self, words):
        """
        Train the AI on a list of words by adding them to the training data.
        """
        for word in words:
            if word not in self.training_data["categories"]:
                self.training_data["categories"].append(word)
        self.save_training_data()

    def generate_word(self):
        """
        Generate a new word based on the training data.
        """
        if not self.training_data["categories"]:
            print("No training data available to generate words.")
            return None

        # Use the text generator to create a new word-like output
        if self.text_generator:
            try:
                prompt = "Generate a new word based on training data:"
                result = self.text_generator(prompt, max_length=10, num_return_sequences=1, do_sample=True)
                generated_text = result[0]["generated_text"].strip()
                # Filter out non-alphabetic characters and return the word
                return ''.join(filter(str.isalpha, generated_text)).upper()
            except Exception as e:
                print(f"Error generating word: {e}")
        return random.choice(self.training_data["categories"]).upper()

    def learn_from_riddles(self, riddles):
        """
        Learn from riddles by extracting words and fetching their definitions.
        :param riddles: A dictionary of riddles categorized by difficulty or type.
        """
        new_words = set()
        for category, riddle_list in riddles.items():
            for riddle, answer in riddle_list:
                # Add the answer to the vocabulary
                new_words.add(answer.upper())
                # Split the riddle into words and add them to the vocabulary
                new_words.update(word.upper() for word in riddle.split())

        # Fetch definitions for new words and update training data
        for word in new_words:
            if word not in self.training_data["categories"]:
                definition_data = fetch_word_definition(word)
                if definition_data:
                    self.training_data["definitions"].append(definition_data)
                    self.training_data["categories"].append(word)
                    print(f"Learned new word: {word} with definition: {definition_data}")
                else:
                    print(f"Failed to fetch definition for: {word}")

        # Save the updated training data
        self.save_training_data()

    def retrain(self):
        """
        Retrain the AI dynamically based on the updated training data.
        """
        print("Retraining AI with updated vocabulary...")
        # Example: Use the text generator to fine-tune on new data (if supported)
        # This is a placeholder for actual retraining logic, which depends on the model's capabilities.
        # For now, we simply acknowledge the updated training data.
        print(f"Training data now contains {len(self.training_data['categories'])} words.")

    def answer_question(self, question, context=None):
        """
        Answer a question based on the provided context or training data.
        :param question: The question to answer.
        :param context: The context to use for answering the question. If None, use training data.
        :return: The answer to the question.
        """
        if not self.question_answering_model:
            return "Question-answering model is not available."

        if not context:
            # Use definitions from training data as context
            context = " ".join(
                [definition["definition"] for definition in self.training_data.get("definitions", [])]
            )

        try:
            result = self.question_answering_model(question=question, context=context)
            return result["answer"]
        except Exception as e:
            print(f"Error answering question: {e}")
            return "I couldn't find an answer to that question."

    def ask_question(self):
        """
        Dynamically generate a question based on the training data.
        :return: A generated question.
        """
        if not self.training_data["categories"]:
            return "I don't have enough data to ask a question."

        # Example: Ask about a random word from the training data
        word = random.choice(self.training_data["categories"])
        return f"What is the meaning of the word '{word}'?"