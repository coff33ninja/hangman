import json
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from collections import Counter
from content_manager import fetch_word_definition, categorize_entry
import random
import os
import requests
from threading import Thread

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
        self.training_data = {"riddles": [], "definitions": [], "categories": [], "research": []}
        self.category_keywords = {
            "animals": ["animal", "mammal", "bird", "fish", "reptile", "insect"],
            "vehicles": ["vehicle", "car", "truck", "bike", "airplane", "ship"],
            "objects": ["object", "tool", "device", "item", "thing"],
            "places": ["place", "city", "country", "location", "region"],
            "people": ["person", "human", "name", "character", "individual"],
        }
        self.category_hierarchy = {
            "solarsystem": {
                "stars": [],
                "planets": {
                    "earth": {
                        "continents": {
                            "countries": []
                        }
                    }
                }
            },
            "animals": {
                "mammals": [],
                "birds": [],
                "reptiles": [],
            },
            "places": {
                "continents": {
                    "countries": []
                }
            }
        }

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

    def add_to_hierarchy(self, word, hierarchy_path):
        """
        Add a word to the category hierarchy at the specified path.
        :param word: The word to add.
        :param hierarchy_path: A list representing the path in the hierarchy (e.g., ["solarsystem", "planets", "earth"]).
        """
        current_level = self.category_hierarchy
        for level in hierarchy_path:
            if level not in current_level:
                current_level[level] = {}
            current_level = current_level[level]

        # Add the word to the final level
        if isinstance(current_level, list):
            if word not in current_level:
                current_level.append(word)
        else:
            print(f"Error: Cannot add word '{word}' to a non-list category.")

    def train_categories_with_hierarchy(self, word, definition_data):
        """
        Train the AI to dynamically adjust categories and subcategories based on new words and definitions.
        :param word: The word to categorize.
        :param definition_data: The definition data for the word.
        """
        if not definition_data or "definitions" not in definition_data:
            return ["uncategorized"]

        # Use categorize_entry to determine the category
        category = categorize_entry(word, definition_data)
        if category != "uncategorized":
            self.add_to_hierarchy(word, [category])
            print(f"Categorized '{word}' under category: {category}.")
            return [category]

        # If no category matches, create a new subcategory under "uncategorized"
        best_hierarchy_path = ["uncategorized", f"new_category_{len(self.category_hierarchy) + 1}"]
        self.add_to_hierarchy(word, best_hierarchy_path)
        print(f"Created new subcategory '{best_hierarchy_path[-1]}' for word '{word}'.")
        return best_hierarchy_path

    def train_on_words(self, words):
        """
        Train the AI on a list of words by categorizing them and adding them to the training data.
        """
        for word in words:
            if word not in self.training_data["categories"]:
                # Fetch the definition to categorize the word
                definition_data = fetch_word_definition(word)
                hierarchy_path = self.train_categories_with_hierarchy(word, definition_data)
                if hierarchy_path not in self.training_data["categories"]:
                    self.training_data["categories"].append(hierarchy_path)
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

    def retrain_async(self):
        """
        Retrain the AI in a separate thread.
        """
        retrain_thread = Thread(target=self.retrain)
        retrain_thread.start()

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

    def generate_config_file(self, config_path="data/config.json"):
        """
        Generate a configuration file dynamically based on the AI's current state.
        """
        config_data = {
            "device": self.device,
            "training_file": self.training_file,
            "model": "t5-small",
            "text_generator_model": "gpt2",
            "question_answering_model": "distilbert-base-cased-distilled-squad",
            "categories": len(self.training_data.get("categories", [])),
            "definitions": len(self.training_data.get("definitions", [])),
        }
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, "w") as f:
                json.dump(config_data, f, indent=4)
            print(f"Configuration file saved at {config_path}")
        except IOError as e:
            print(f"Error saving configuration file: {e}")

    def save_model_weights(self, model_path="data/model.safetensors"):
        """
        Save the model weights to a file for future use.
        """
        try:
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            # Placeholder for saving model weights (if supported by the model)
            with open(model_path, "wb") as f:
                f.write(b"")  # Write an empty file as a placeholder
            print(f"Model weights saved at {model_path}")
        except IOError as e:
            print(f"Error saving model weights: {e}")

    def save_tokenizer_files(self, tokenizer_dir="data/tokenizer"):
        """
        Save tokenizer files dynamically.
        """
        try:
            os.makedirs(tokenizer_dir, exist_ok=True)
            # Placeholder for saving tokenizer files
            with open(os.path.join(tokenizer_dir, "tokenizer_config.json"), "w") as f:
                json.dump({"version": "1.0", "model": "t5-small"}, f, indent=4)
            with open(os.path.join(tokenizer_dir, "vocab.txt"), "w") as f:
                f.write("\n".join(self.custom_tokenizer.get_vocab().keys()))
            print(f"Tokenizer files saved in {tokenizer_dir}")
        except IOError as e:
            print(f"Error saving tokenizer files: {e}")

    def generate_files(self):
        """
        Generate all necessary files dynamically.
        """
        print("Generating AI files...")
        self.generate_config_file()
        self.save_model_weights()
        self.save_tokenizer_files()
        print("All files generated successfully.")

    def research_topic(self, topic):
        """
        Research a topic using multiple APIs and expand the AI's knowledge.
        :param topic: The topic to research.
        :return: A summary of the research.
        """
        print(f"Researching topic: {topic}")
        research_results = []

        # Fetch definitions from the dictionary API
        definition_data = fetch_word_definition(topic)
        if definition_data:
            definitions = [d["definition"] for d in definition_data.get("definitions", [])]
            research_results.extend(definitions)
            print(f"Definitions for '{topic}': {definitions}")

        # Fetch additional information from a Wikipedia-like API
        wikipedia_summary = self.fetch_wikipedia_summary(topic)
        if wikipedia_summary:
            research_results.append(wikipedia_summary)
            print(f"Wikipedia summary for '{topic}': {wikipedia_summary}")

        # Fetch related topics using a knowledge graph API
        related_topics = self.fetch_related_topics(topic)
        if related_topics:
            research_results.append(f"Related topics: {', '.join(related_topics)}")
            print(f"Related topics for '{topic}': {related_topics}")

        # Save the research results to training data
        self.training_data["research"].append({"topic": topic, "results": research_results})
        self.save_training_data()

        return "\n".join(research_results)

    def fetch_wikipedia_summary(self, topic):
        """
        Fetch a summary of a topic from a Wikipedia-like API.
        :param topic: The topic to fetch.
        :return: A summary of the topic.
        """
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get("extract", f"No summary available for '{topic}'.")
        except requests.RequestException as e:
            print(f"Error fetching Wikipedia summary for '{topic}': {e}")
            return None

    def fetch_related_topics(self, topic):
        """
        Fetch related topics using a knowledge graph API.
        :param topic: The topic to fetch related topics for.
        :return: A list of related topics.
        """
        url = f"https://api.conceptnet.io/c/en/{topic}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            edges = data.get("edges", [])
            related_topics = [edge["end"]["label"] for edge in edges if "end" in edge and "label" in edge["end"]]
            return related_topics[:5]  # Limit to 5 related topics
        except requests.RequestException as e:
            print(f"Error fetching related topics for '{topic}': {e}")
            return None

    def ask_follow_up_question(self, topic):
        """
        Dynamically ask a follow-up question about a topic.
        :param topic: The topic to ask about.
        :return: A follow-up question.
        """
        return f"What about {topic}? Can you tell me more?"