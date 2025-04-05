import json
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from collections import Counter
from content_manager import fetch_word_definition, categorize_entry, append_word_to_file, save_topic_to_file  # Ensure categorize_entry is used
import random  # Ensure random is used
import os
import requests
from threading import Thread
import logging
import time  # Ensure time is used for rate limiting

# Initialize logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class AIManager:
    def __init__(self, training_file="data/training_data.json", predefined_words_file="data/predefined_words.json"):
        """
        Initialize the AI manager with pre-trained models, training data file, and predefined words file.
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
        self.predefined_words = self.load_predefined_words(predefined_words_file)
        self.memory = {"short_term": {}, "long_term": {}}  # Add memory system

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

    def load_predefined_words(self, filepath):
        """
        Load predefined words and their data from a JSON file.
        :param filepath: Path to the predefined words file.
        :return: A dictionary of predefined words and their data.
        """
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Predefined words file not found or invalid: {filepath}")
            return {}

    def load_symbols(self, filepath="data/symbols.json"):
        """
        Load symbols and their functions from a JSON file.
        :param filepath: Path to the symbols.json file.
        :return: A dictionary of symbols and their functions.
        """
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Symbols file not found or invalid: {filepath}")
            # Provide a fallback for basic symbols
            return {
                "?": {"name": "Question Mark", "function": "Indicates a question or inquiry."},
                "!": {"name": "Exclamation Mark", "function": "Expresses strong emotion or emphasis."},
                ".": {"name": "Period", "function": "Marks the end of a declarative sentence."}
            }

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

    def dynamic_retrain(self):
        """
        Dynamically retrain the AI based on newly acquired data.
        """
        print("Dynamically retraining AI...")
        # Combine short-term and long-term memory for retraining
        combined_data = {**self.memory["short_term"], **{k: v["data"] for k, v in self.memory["long_term"].items()}}
        self.training_data["dynamic_memory"] = combined_data
        self.retrain()

    def update_memory(self, word, data):
        """
        Update the AI's memory with new data for a word.
        Frequently accessed words are moved to long-term memory.
        """
        # Add to short-term memory
        self.memory["short_term"][word] = data

        # If the word is accessed frequently, move it to long-term memory
        if word in self.memory["long_term"]:
            self.memory["long_term"][word]["access_count"] += 1
        else:
            self.memory["long_term"][word] = {"data": data, "access_count": 1}

        # Forget less relevant data from short-term memory
        if len(self.memory["short_term"]) > 100:  # Limit short-term memory size
            least_used = min(self.memory["short_term"], key=lambda w: self.memory["long_term"].get(w, {}).get("access_count", 0))
            del self.memory["short_term"][least_used]

    def retrieve_memory(self, word):
        """
        Retrieve data for a word from memory.
        """
        if word in self.memory["short_term"]:
            return self.memory["short_term"][word]
        if word in self.memory["long_term"]:
            self.memory["long_term"][word]["access_count"] += 1
            return self.memory["long_term"][word]["data"]
        return None

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
            filtered_data["definitions"] = definition_data.get("definitions", [])
            filtered_data["examples"] = [
                definition.get("example", "") for definition in definition_data.get("definitions", []) if "example" in definition
            ]
            filtered_data["synonyms"] = [
                synonym for definition in definition_data.get("definitions", []) for synonym in definition.get("synonyms", [])
            ]
            filtered_data["antonyms"] = [
                antonym for definition in definition_data.get("definitions", []) for antonym in definition.get("antonyms", [])
            ]
            filtered_data["related_topics"] = definition_data.get("related_topics", [])

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

    def process_and_research_data(self, data):
        """
        Process and research data by breaking it into components and researching each part.
        :param data: The input data (e.g., a sentence, word, or paragraph).
        :return: A dictionary containing research results for each component.
        """
        research_results = {}

        # Break down data into words and sentences
        words = data.split()
        sentences = data.split(". ")

        # Research each word
        research_results["words"] = {}
        for word in words:
            word_data = self.filter_and_reference_data(word)
            research_results["words"][word] = word_data

        # Research each sentence
        research_results["sentences"] = {}
        for sentence in sentences:
            sentence_data = {
                "grammar_analysis": self.analyze_grammar(sentence),
                "vocabulary_analysis": self.analyze_vocabulary(sentence),
                "spelling_analysis": self.analyze_spelling(sentence),
                "punctuation_analysis": self.analyze_punctuation(sentence),
            }
            research_results["sentences"][sentence] = sentence_data

        # Save research results to training data
        self.training_data["research_results"] = self.training_data.get("research_results", {})
        self.training_data["research_results"].update(research_results)
        self.save_training_data()

        return research_results

    def analyze_grammar(self, sentence):
        """
        Analyze the grammar of a sentence.
        :param sentence: The sentence to analyze.
        :return: A dictionary containing grammar analysis results.
        """
        # Placeholder for grammar analysis logic
        return {"syntax": "Analyzed syntax", "parts_of_speech": "Analyzed parts of speech"}

    def analyze_vocabulary(self, sentence):
        """
        Analyze the vocabulary of a sentence.
        :param sentence: The sentence to analyze.
        :return: A dictionary containing vocabulary analysis results.
        """
        # Placeholder for vocabulary analysis logic
        return {"word_meanings": "Analyzed word meanings", "contextual_usage": "Analyzed contextual usage"}

    def analyze_spelling(self, sentence):
        """
        Analyze the spelling of a sentence.
        :param sentence: The sentence to analyze.
        :return: A dictionary containing spelling analysis results.
        """
        # Placeholder for spelling analysis logic
        return {"phonetic_spelling": "Analyzed phonetic spelling", "spelling_rules": "Analyzed spelling rules"}

    def analyze_punctuation(self, sentence):
        """
        Analyze the punctuation of a sentence.
        :param sentence: The sentence to analyze.
        :return: A dictionary containing punctuation analysis results.
        """
        # Placeholder for punctuation analysis logic
        return {"end_punctuation": "Analyzed end punctuation", "internal_punctuation": "Analyzed internal punctuation"}

    def train_on_research_results(self):
        """
        Train the AI on the research results stored in the training data.
        """
        research_results = self.training_data.get("research_results", {})
        for word, word_data in research_results.get("words", {}).items():
            self.train_on_filtered_data(word)
        for sentence, sentence_data in research_results.get("sentences", {}).items():
            # Placeholder for training on sentence-level data
            pass

        print("AI trained on research results.")

    def research_rampage(self, word, depth=3, visited=None):
        """
        Perform a recursive research rampage on a word or concept.
        :param word: The word or concept to research.
        :param depth: The maximum depth of recursive research.
        :param visited: A set of already visited words to avoid infinite loops.
        :return: A dictionary containing the research results.
        """
        if visited is None:
            visited = set()

        # Stop recursion if depth is exceeded or word is already visited
        if depth <= 0 or word in visited:
            return {}

        print(f"Researching: {word} (Depth: {depth})")
        visited.add(word)

        # Check memory before fetching new data
        memory_data = self.retrieve_memory(word)
        if memory_data:
            print(f"Retrieved '{word}' from memory.")
            return memory_data

        # Fetch initial data for the word
        research_results = self.filter_and_reference_data(word)

        # Save the research results
        self.training_data["research_results"] = self.training_data.get("research_results", {})
        self.training_data["research_results"][word] = research_results
        self.save_training_data()

        # Update memory with new data
        self.update_memory(word, research_results)

        # Save the word to words.txt
        category = categorize_entry(word, research_results)
        append_word_to_file(word, category)

        # Save related terms as a topic
        topic_data = {
            "word": word,
            "definitions": research_results.get("definitions", []),
            "examples": research_results.get("examples", []),
            "synonyms": research_results.get("synonyms", []),
            "antonyms": research_results.get("antonyms", []),
            "related_topics": research_results.get("related_topics", []),
        }
        save_topic_to_file(word, topic_data)

        # Extract related terms for recursive research
        related_terms = set()

        # Add synonyms, antonyms, and related topics
        for meaning in research_results.get("definitions", []):
            related_terms.update(meaning.get("synonyms", []))
            related_terms.update(meaning.get("antonyms", []))

        related_terms.update(research_results.get("related_topics", []))

        # Add words from examples
        for example in research_results.get("examples", []):
            related_terms.update(example.split())

        # Filter out already visited words
        related_terms = {term.lower() for term in related_terms if term.lower() not in visited}

        # Recursively research each related term
        for term in related_terms:
            time.sleep(0.5)  # Add delay to avoid hitting API rate limits
            self.research_rampage(term, depth=depth - 1, visited=visited)

        return research_results

    def process_and_categorize_data(self, word, data):
        """
        Process and categorize the data gathered during research.
        :param word: The word being processed.
        :param data: The data gathered for the word.
        """
        print(f"Processing and categorizing data for '{word}'...")

        # Categorize definitions by part of speech
        categorized_definitions = {}
        for definition in data.get("definitions", []):
            part_of_speech = definition.get("partOfSpeech", "unknown")
            categorized_definitions.setdefault(part_of_speech, []).append(definition["definition"])

        # Link related terms (synonyms, antonyms, related topics)
        linked_terms = {
            "synonyms": data.get("synonyms", []),
            "antonyms": data.get("antonyms", []),
            "related_topics": data.get("related_topics", []),
        }

        # Save categorized and linked data
        self.training_data["processed_data"] = self.training_data.get("processed_data", {})
        self.training_data["processed_data"][word] = {
            "categorized_definitions": categorized_definitions,
            "linked_terms": linked_terms,
            "examples": data.get("examples", []),
        }

        print(f"Data for '{word}' categorized and saved.")

    def train_on_research_rampage(self):
        """
        Train the AI on research results from a rampage.
        """
        print("Training on research rampage results...")
        research_results = self.training_data.get("research", [])
        new_research_results = []  # Temporary list to avoid modifying during iteration

        for result in research_results:
            word = result.get("word")
            data = result.get("results", {})
            if word and data:
                print(f"Training on filtered data for '{word}'.")
                self.train_on_filtered_data(word)
                new_research_results.append(result)

        # Replace the old research results with the updated list
        self.training_data["research"] = new_research_results
        self.save_training_data()

    def learn_from_riddles(self, riddles):
        """
        Learn from riddles by processing their answers and training the AI.
        :param riddles: A dictionary of riddles categorized by difficulty or topic.
        """
        print("Learning from riddles...")
        for category, riddle_list in riddles.items():
            for riddle, answer in riddle_list:
                # Process the answer
                answer_data = self.filter_and_reference_data(answer)
                if answer_data:
                    # Save the processed data
                    self.training_data["riddles"].append({
                        "riddle": riddle,
                        "answer": answer,
                        "data": answer_data
                    })
                    print(f"Learned from riddle: {riddle} -> {answer}")

        # Save the updated training data
        self.save_training_data()

    def research_topic(self, topic):
        """
        Research a topic by fetching definitions, synonyms, examples, and related topics.
        :param topic: The topic to research.
        :return: A summary of the research.
        """
        print(f"Researching topic: {topic}")
        symbols = self.load_symbols()

        # Check if the topic is a symbol
        if topic in symbols:
            symbol_data = symbols[topic]
            return f"Symbol: {topic}\nName: {symbol_data['name']}\nFunction: {symbol_data['function']}\nExamples: {', '.join(symbol_data['examples'])}"

        # Proceed with regular research if not a symbol
        research_results = self.research_rampage(topic, depth=3)
        if not research_results:
            return f"No information found for '{topic}'."
        return research_results