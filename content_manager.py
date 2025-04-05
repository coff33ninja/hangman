# content_manager.py

import random
import requests
import os
import json
import time


def categorize_entry(entry, dictionary_data):
    """
    Categorize an entry (word or riddle answer) based on its dictionary definition.
    :param entry: The word or answer to categorize.
    :param dictionary_data: The dictionary data fetched for the entry.
    :return: A category string (e.g., 'animals', 'vehicles', etc.).
    """
    if not dictionary_data or "definitions" not in dictionary_data:
        return "uncategorized"

    definitions = dictionary_data["definitions"]
    keywords = {
        "animals": ["animal", "mammal", "bird", "fish", "reptile", "insect"],
        "vehicles": ["vehicle", "car", "truck", "bike", "airplane", "ship"],
        "objects": ["object", "tool", "device", "item", "thing"],
        "places": ["place", "city", "country", "location", "region"],
        "people": ["person", "human", "name", "character", "individual"],
    }

    for category, category_keywords in keywords.items():
        for definition in definitions:
            if any(keyword in definition["definition"].lower() for keyword in category_keywords):
                return category

    return "uncategorized"


def load_words(filepath="data/words.txt", ai_manager=None):
    """
    Load words from a file into a dictionary by category.
    Dynamically categorize words using the dictionary API.
    Optionally train the AI on the loaded words.
    """
    words = {"default": ["PYTHON", "GAME", "HANGMAN"]}  # Ensure a default category exists
    all_words = []  # Collect all words for AI training
    try:
        with open(filepath, "r") as f:
            for line in f:
                try:
                    category, word = line.strip().split(",", 1)
                    word = word.upper()
                    dictionary_data = fetch_word_definition(word)
                    dynamic_category = categorize_entry(word, dictionary_data)
                    words.setdefault(dynamic_category, []).append(word)
                    all_words.append(word)
                except ValueError:
                    print(f"Malformed line in words file: {line}")
    except FileNotFoundError:
        print(f"Words file not found. Using default words: {words['default']}")

    # Dynamically include topics from the topics folder
    topics_folder = "data/topics"
    if os.path.exists(topics_folder):
        for topic_file in os.listdir(topics_folder):
            if topic_file.endswith(".json"):
                topic_name = topic_file.replace("_", " ").replace(".json", "")
                with open(os.path.join(topics_folder, topic_file), "r") as f:
                    topic_data = json.load(f)
                    words[topic_name] = topic_data.get("results", [])

    # Train the AI on the loaded words
    if ai_manager:
        ai_manager.train_on_words(all_words)

    return {category: random.sample(words, len(words)) for category, words in words.items()}


def load_riddles(difficulty=None, difficulty_files=None):
    """
    Load riddles from separate files for each difficulty level.
    Dynamically categorize riddle answers using the dictionary API.
    """
    if difficulty_files is None:
        difficulty_files = {
            "easy": "data/riddles_easy.txt",
            "medium": "data/riddles_medium.txt",
            "hard": "data/riddles_hard.txt",
        }

    riddles = {}
    for level, filepath in difficulty_files.items():
        try:
            with open(filepath, "r") as f:
                for line in f:
                    try:
                        riddle, answer = line.strip().split(",", 1)
                        answer = answer.upper()
                        dictionary_data = fetch_word_definition(answer)
                        dynamic_category = categorize_entry(answer, dictionary_data)
                        riddles.setdefault(dynamic_category, []).append((riddle, answer))
                    except ValueError:
                        print(f"Malformed line in {filepath}: {line}")
        except FileNotFoundError:
            print(f"Riddles file not found: {filepath}")

    if difficulty:
        return riddles.get(difficulty, [])
    return riddles


def fetch_online_riddles(num_riddles=5, filepath="data/riddles.txt"):
    """
    Fetch random riddles from riddles-api.vercel.app and store them in riddles_<difficulty>.txt.
    Categorize riddles based on the number of words in the answer.
    """
    riddles = []
    try:
        for _ in range(min(num_riddles, 10)):  # Limit to avoid overloading free API
            response = requests.get("https://riddles-api.vercel.app/random", timeout=5)
            if response.status_code == 200:
                data = response.json()
                riddle = data["riddle"]
                answer = data["answer"].upper()
                riddles.append((riddle, answer))
            else:
                print(f"Riddle API Error: {response.status_code}")
                break
    except requests.RequestException as e:
        print(f"Riddle API Network Error: {e}")

    if not riddles:  # Fallback
        riddles = [("What is always running but never moves?", "CLOCK")]

    # Categorize riddles dynamically
    categorized_riddles = {"easy": [], "medium": [], "hard": []}
    for riddle, answer in riddles:
        word_count = len(answer.split())
        if word_count == 1:
            category = "easy"
        elif 5 <= word_count <= 10:
            category = "medium"
        else:
            category = "hard"
        categorized_riddles[category].append((riddle, answer))

    for category, riddles_list in categorized_riddles.items():
        try:
            with open(f"data/riddles_{category}.txt", "a") as f:
                for riddle, answer in riddles_list:
                    f.write(f"{riddle},{answer}\n")
        except IOError as e:
            print(f"Error writing riddles to file for {category}: {e}")

    return categorized_riddles


def fetch_word_definition(word):
    """
    Fetch the definition of a word from the dictionary API.
    :param word: The word to look up.
    :return: A dictionary containing the word's definition, synonyms, and example usage.
    """
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            definitions = []
            for meaning in data[0].get("meanings", []):
                for definition in meaning.get("definitions", []):
                    definitions.append({
                        "partOfSpeech": meaning.get("partOfSpeech", ""),
                        "definition": definition.get("definition", ""),
                        "example": definition.get("example", ""),
                        "synonyms": definition.get("synonyms", []),
                        "antonyms": definition.get("antonyms", []),
                    })
            return {
                "word": data[0].get("word", ""),
                "phonetics": data[0].get("phonetics", []),
                "definitions": definitions,
            }
    except requests.exceptions.HTTPError as e:
        if response.status_code == 429:
            print("Rate limit exceeded. Retrying after delay...")
            time.sleep(1)  # Delay before retrying
        elif response.status_code == 404:
            print(f"Word '{word}' not found in dictionary.")
        else:
            print(f"HTTP error for '{word}': {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching definition for '{word}': {e}")
    return None