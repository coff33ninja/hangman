import os
import json
import torch
from ai_manager import AIManager
from threading import Thread

class TeachEnglish:
    def __init__(self, ai_manager=None, model_file="data/english_model.pth", components_file="data/core_language_components.json"):
        """
        Initialize the TeachEnglish package with an AIManager instance and model file.
        """
        self.ai_manager = ai_manager or AIManager()
        self.training_data_folder = "data/english_training"
        self.model_file = model_file
        self.language_components = self.load_language_components(components_file)
        os.makedirs(self.training_data_folder, exist_ok=True)

        # Initialize or load the model
        self.model = self.initialize_model()

    def initialize_model(self):
        """
        Initialize or load the dynamic model for language learning.
        """
        if os.path.exists(self.model_file):
            print(f"Loading model from {self.model_file}...")
            return torch.load(self.model_file)
        else:
            print("Initializing a new model...")
            return {"words": {}, "categories": {}, "interactions": [], "language_components": {}}

    def save_model(self):
        """
        Save the current model to the model file.
        """
        torch.save(self.model, self.model_file)
        print(f"Model saved to {self.model_file}")

    def fetch_and_save_word_data(self, word):
        """
        Fetch definitions, synonyms, examples, and related topics for a word and save them.
        Train the AI on additional data from researched sentences.
        """
        print(f"Fetching data for word: {word}")
        try:
            word_data = self.ai_manager.research_rampage(word, depth=3)
            print(f"Research rampage completed for '{word}': {word_data}")

            # Save to file
            filepath = os.path.join(self.training_data_folder, f"{word}.json")
            with open(filepath, "w") as f:
                json.dump(word_data, f, indent=4)
            print(f"Data for '{word}' saved to {filepath}")

            # Train the AI on the processed data
            self.ai_manager.train_on_research_rampage()

            # Train on additional sentences from research
            sentences = word_data.get("examples", [])
            for sentence in sentences:
                self.ai_manager.process_and_research_data(sentence)

            # Trigger dynamic retraining
            self.ai_manager.dynamic_retrain()

        except Exception as e:
            print(f"Error during research for '{word}': {e}")

    def train_language_component(self, component, data):
        """
        Train the AI on a specific language component (e.g., grammar, vocabulary).
        """
        print(f"Training on language component: {component}")
        if component not in self.model["language_components"]:
            self.model["language_components"][component] = []

        self.model["language_components"][component].extend(data)
        self.save_model()

    def run_training_drill(self, words):
        """
        Run a training drill for a list of words.
        """
        print("Starting training drill...")
        threads = []
        for word in words:
            thread = Thread(target=self.fetch_and_save_word_data, args=(word,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
        print("Training drill completed.")

    def teach_word(self, word):
        """
        Teach a word by displaying its definitions, synonyms, examples, and related topics.
        """
        if word not in self.model["words"]:
            print(f"No data found for '{word}'. Fetching data...")
            self.fetch_and_save_word_data(word)

        word_data = self.model["words"].get(word, {})
        print(f"Teaching word: {word}")
        print(f"Definitions: {word_data.get('definitions', [])}")
        print(f"Synonyms: {word_data.get('synonyms', [])}")
        print(f"Examples: {word_data.get('examples', [])}")
        print(f"Related Topics: {word_data.get('related_topics', [])}")

    def dynamic_interaction(self, question):
        """
        Handle dynamic interactions by analyzing the question and providing a response.
        """
        print(f"Processing question: {question}")
        response = self.ai_manager.answer_question(question)
        print(f"AI's response: {response}")

        # Log the interaction for future training
        self.model["interactions"].append({"question": question, "response": response})
        self.save_model()

    def load_language_components(self, filepath):
        """
        Load predefined language components from a JSON file.
        """
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Language components file not found or invalid: {filepath}")
            return {}

    def train_core_language_components(self):
        """
        Train the AI on core language components using the predefined file.
        """
        for component, data in self.language_components.items():
            print(f"Training on language component: {component}")
            self.train_language_component(component, data["topics"])

if __name__ == "__main__":
    # Example usage
    teach_english = TeachEnglish()
    words_to_train = ["serendipity", "ephemeral", "resilience"]
    teach_english.run_training_drill(words_to_train)

    # Teach a specific word
    teach_english.teach_word("serendipity")

    # Train on core language components
    teach_english.train_core_language_components()

    # Dynamic interaction
    teach_english.dynamic_interaction("What does 'resilience' mean?")
