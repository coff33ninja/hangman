import json
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from collections import Counter
from content_manager import fetch_word_definition, categorize_entry  # Ensure categorize_entry is used
import random  # Ensure random is used
import os
import requests
from threading import Thread
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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
            self.training_data = {"riddles": [], "definitions": [], "categories": [], "research": []}
            self.save_training_data()  # Create an empty training data file

        # Ensure all required keys are present
        self.training_data.setdefault("riddles", [])
        self.training_data.setdefault("definitions", [])
        self.training_data.setdefault("categories", [])
        self.training_data.setdefault("research", [])

    def save_training_data(self):
        """
        Save the current training data to the training file.
        """
        try:
            with open(self.training_file, "w") as f:
                json.dump(self.training_data, f, indent=4)
        except IOError as e:
            print(f"Error saving training data: {e}")

    def retrain(self):
        """
        Retrain the AI dynamically based on the updated training data.
        """
        print("Retraining AI with updated vocabulary...")
        # Placeholder for actual retraining logic
        print(f"Training data now contains {len(self.training_data['categories'])} words.")

    def retrain_async(self):
        """
        Retrain the AI in a separate thread.
        """
        retrain_thread = Thread(target=self.retrain)
        retrain_thread.start()

    def generate_files(self):
        """
        Generate all necessary files dynamically.
        """
        print("Generating AI files...")
        self.generate_config_file()
        self.save_model_weights()
        self.save_tokenizer_files()
        print("All files generated successfully.")

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

    def research_language_factors(self, word):
        """
        Research language-based factors for a word and dynamically learn from the results.
        :param word: The word to research.
        :return: A summary of the research.
        """
        research_results = []

        # Fetch definitions, synonyms, and examples
        definition_data = fetch_word_definition(word)
        if definition_data:
            research_results.append(f"Definitions: {', '.join(d['definition'] for d in definition_data['definitions'])}")
            research_results.append(f"Synonyms: {', '.join(d['synonyms'] for d in definition_data['definitions'] if d['synonyms'])}")
            research_results.append(f"Examples: {', '.join(d['example'] for d in definition_data['definitions'] if d['example'])}")
            self.training_data["definitions"].append(definition_data)

        # Fetch etymology and related topics
        wikipedia_summary = self.fetch_wikipedia_summary(word)
        if wikipedia_summary:
            research_results.append(f"Etymology: {wikipedia_summary}")

        related_topics = self.fetch_related_topics(word)
        if related_topics:
            research_results.append(f"Related Topics: {', '.join(related_topics)}")

        # Save the research results
        self.training_data["research"].append({"word": word, "results": research_results})
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
            self.training_data["categories"].append(category)
            print(f"Categorized '{word}' under category: {category}.")
            return [category]

        # If no category matches, create a new subcategory under "uncategorized"
        new_category = f"new_category_{random.randint(1000, 9999)}"  # Use random for unique category names
        self.training_data["categories"].append(new_category)
        print(f"Created new category '{new_category}' for word '{word}'.")
        return [new_category]

    def train_on_words(self, words):
        """
        Train the AI on a list of words by categorizing them and adding them to the training data.
        """
        for word in words:
            if word not in self.training_data["categories"]:
                # Fetch the definition to categorize the word
                definition_data = fetch_word_definition(word)
                self.train_categories_with_hierarchy(word, definition_data)
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
        return random.choice(self.training_data["categories"]).upper()  # Use random to select a category

    def fetch_word_synonyms(self, word):
        """
        Fetch synonyms for a word using the dictionary API.
        :param word: The word to fetch synonyms for.
        :return: A list of synonyms.
        """
        definition_data = fetch_word_definition(word)
        if definition_data and "definitions" in definition_data:
            synonyms = [
                synonym
                for definition in definition_data["definitions"]
                for synonym in definition.get("synonyms", [])
            ]
            return list(set(synonyms))  # Remove duplicates
        return []

    def fetch_word_examples(self, word):
        """
        Fetch example sentences for a word using the dictionary API.
        :param word: The word to fetch examples for.
        :return: A list of example sentences.
        """
        definition_data = fetch_word_definition(word)
        if definition_data and "definitions" in definition_data:
            examples = [
                definition.get("example", "")
                for definition in definition_data["definitions"]
                if "example" in definition
            ]
            return [example for example in examples if example]  # Filter out empty examples
        return []

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
            # Dynamically build context from training data
            context = "\n".join(
                [
                    f"Definition: {definition.get('definition', '')}"
                    for definition in self.training_data.get("definitions", [])
                ] + [
                    f"Synonyms: {', '.join(definition.get('synonyms', []))}"
                    for definition in self.training_data.get("definitions", [])
                    if definition.get("synonyms")
                ] + [
                    f"Related Topics: {', '.join(entry.get('results', []))}"
                    for entry in self.training_data.get("research", [])
                ]
            )
            if not context:
                return "I don't have enough information to answer that question."

        try:
            result = self.question_answering_model(question=question, context=context)
            return result["answer"]
        except Exception as e:
            print(f"Error answering question: {e}")
            return "I couldn't find an answer to that question."

    def filter_and_reference_data(self, word):
        """
        Filter and reference data for a word, including definitions, synonyms, examples, and related topics.
        :param word: The word to process.
        :return: A dictionary containing filtered and referenced data.
        """
        filtered_data = {}

        # Fetch definitions
        definition_data = fetch_word_definition(word)
        if definition_data:
            filtered_data["definitions"] = [
                {
                    "partOfSpeech": d.get("partOfSpeech", ""),
                    "definition": d.get("definition", ""),
                    "example": d.get("example", ""),
                }
                for d in definition_data.get("definitions", [])
            ]

        # Fetch synonyms
        synonyms = self.fetch_word_synonyms(word)
        filtered_data["synonyms"] = synonyms

        # Fetch examples
        examples = self.fetch_word_examples(word)
        filtered_data["examples"] = examples

        # Fetch related topics
        related_topics = self.fetch_related_topics(word)
        filtered_data["related_topics"] = related_topics

        # Reference each component dynamically
        filtered_data["references"] = {
            "nouns": [w for w in word.split() if w.isalpha()],
            "acronyms": [w for w in word.split() if w.isupper()],
            "verbs": [w for w in word.split() if w.endswith("ing")],  # Example heuristic
        }

        return filtered_data

    def train_on_filtered_data(self, word):
        """
        Train the AI on filtered and referenced data for a word.
        :param word: The word to train on.
        """
        filtered_data = self.filter_and_reference_data(word)
        self.training_data["filtered_data"] = self.training_data.get("filtered_data", {})
        self.training_data["filtered_data"][word] = filtered_data
        self.save_training_data()
        print(f"Trained on filtered data for '{word}'.")