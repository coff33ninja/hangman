import os
import json
import torch
from ai_manager import AIManager
from content_manager import fetch_word_definition
from threading import Thread

class TeachEnglish:
    def __init__(self, ai_manager=None, model_file="data/english_model.pth"):
        """
        Initialize the TeachEnglish package with an AIManager instance and model file.
        """
        self.ai_manager = ai_manager or AIManager()
        self.training_data_folder = "data/english_training"
        self.model_file = model_file
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
        """
        print(f"Fetching data for word: {word}")
        word_data = {}

        # Fetch definitions
        definition_data = fetch_word_definition(word)
        if definition_data:
            word_data["definitions"] = definition_data.get("definitions", [])
            print(f"Definitions for '{word}': {word_data['definitions']}")

        # Fetch synonyms and examples
        synonyms = self.ai_manager.fetch_word_synonyms(word)
        examples = self.ai_manager.fetch_word_examples(word)
        word_data["synonyms"] = synonyms
        word_data["examples"] = examples
        print(f"Synonyms for '{word}': {synonyms}")
        print(f"Examples for '{word}': {examples}")

        # Fetch related topics
        related_topics = list(set(self.ai_manager.fetch_related_topics(word)))  # Remove duplicates
        word_data["related_topics"] = related_topics
        print(f"Related topics for '{word}': {related_topics}")

        # Save to file
        filepath = os.path.join(self.training_data_folder, f"{word}.json")
        with open(filepath, "w") as f:
            json.dump(word_data, f, indent=4)
        print(f"Data for '{word}' saved to {filepath}")

        # Update the model dynamically
        self.model["words"][word] = word_data
        self.save_model()

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

    def train_core_language_components(self):
        """
        Train the AI on core language components.
        """
        grammar_data = [
            "Syntax: Sentence structure and word order.",
            "Parts of Speech: Nouns, verbs, adjectives, adverbs.",
            "Tenses: Past, present, future forms.",
            "Agreement: Subject-verb consistency.",
            "Morphology: Word formation (prefixes, suffixes, root words).",
            "Semantics: Meaning of words and sentences.",
            "Pragmatics: Language use in context, including implied meanings.",
        ]
        vocabulary_data = [
            "Word Meanings: Definitions and usage.",
            "Synonyms, Antonyms, Homonyms: Expanding word variety.",
            "Contextual Usage: How words change meaning depending on context.",
            "Idiomatic Expressions: Phrases like 'kick the bucket' or 'under the weather'.",
            "Collocations: Words that commonly pair together (e.g., 'make a decision').",
            "Register and Tone: Formal vs. informal language distinctions.",
        ]
        spelling_data = [
            "Phonetic Spelling: Sound-to-letter correspondence.",
            "Spelling Rules: Patterns like 'i before e except after c'.",
            "Exceptions: Irregular spellings (e.g., 'through', 'thought').",
            "Homophones: Words that sound the same but differ in meaning (e.g., 'their' vs. 'there').",
        ]
        punctuation_data = [
            "End Punctuation: Periods, question marks, exclamation points.",
            "Internal Punctuation: Commas, semicolons, colons.",
            "Quotation and Possession: Quotation marks and apostrophes.",
            "Connectors: Hyphens, dashes, parentheses for clarity and structure.",
        ]
        reading_comprehension_data = [
            "Main Ideas and Details: Identifying key points and supporting information.",
            "Inferences: Drawing conclusions from implied meanings.",
            "Text Structure: Understanding narrative, expository, or persuasive formats.",
            "Critical Analysis: Evaluating arguments, themes, and motifs.",
        ]
        writing_data = [
            "Sentence Construction: Variety and complexity in sentence forms.",
            "Paragraphs: Coherence, topic sentences, and transitions.",
            "Essay Writing: Introduction, body, conclusion structure.",
            "Styles: Narrative, descriptive, expository, persuasive, argumentative.",
            "Creative Writing: Poetry, stories, and imaginative expression.",
            "Editing: Proofreading and refining written work.",
        ]
        cultural_context_data = [
            "Cultural Norms: Etiquette, values, and traditions tied to the language.",
            "Historical Influence: Events shaping language development.",
            "Proverbs and Sayings: Culturally specific expressions.",
            "Identity: Language’s role in regional or ethnic identity.",
        ]

        self.train_language_component("Grammar", grammar_data)
        self.train_language_component("Vocabulary", vocabulary_data)
        self.train_language_component("Spelling", spelling_data)
        self.train_language_component("Punctuation", punctuation_data)
        self.train_language_component("Reading Comprehension", reading_comprehension_data)
        self.train_language_component("Writing", writing_data)
        self.train_language_component("Cultural Context", cultural_context_data)

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
