# content_manager.py

import random
import requests
import os
import json
import time  # Reintroduced for delay handling
import re  # Import regex for sanitizing filenames


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
            time.sleep(0.5)  # Add delay between API calls to avoid rate limits
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
    Fetch the definition of a word using multiple APIs as fallbacks.
    :param word: The word to look up.
    :return: A dictionary containing the word's definition, synonyms, and example usage.
    """
    # Ensure the input is a single word
    if not word.isalpha():
        print(f"Skipping unsupported input: '{word}'")
        return None

    # Primary API: DictionaryAPI
    url_primary = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    try:
        response = requests.get(url_primary, timeout=5)
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
    except requests.exceptions.RequestException as e:
        print(f"Primary API failed for '{word}': {e}")

    # Fallback API 1: Datamuse API
    url_datamuse = f"https://api.datamuse.com/words?sp={word}&md=d"
    try:
        response = requests.get(url_datamuse, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data:
            definitions = [{"definition": entry.get("defs", [""])[0]} for entry in data if "defs" in entry]
            return {
                "word": word,
                "definitions": definitions,
                "phonetics": [],
            }
    except requests.exceptions.RequestException as e:
        print(f"Datamuse API failed for '{word}': {e}")

    # Fallback API 2: Wordnik API (requires API key)
    api_key_wordnik = "YOUR_WORDNIK_API_KEY"  # Replace with your Wordnik API key
    url_wordnik = f"https://api.wordnik.com/v4/word.json/{word}/definitions?api_key={api_key_wordnik}"
    try:
        response = requests.get(url_wordnik, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data:
            definitions = [{"definition": entry.get("text", "")} for entry in data]
            return {
                "word": word,
                "definitions": definitions,
                "phonetics": [],
            }
    except requests.exceptions.RequestException as e:
        print(f"Wordnik API failed for '{word}': {e}")

    # Fallback API 3: Oxford Dictionaries API (requires API key)
    app_id_oxford = "YOUR_OXFORD_APP_ID"  # Replace with your Oxford App ID
    app_key_oxford = "YOUR_OXFORD_APP_KEY"  # Replace with your Oxford App Key
    url_oxford = f"https://od-api.oxforddictionaries.com/api/v2/entries/en-us/{word}"
    headers_oxford = {"app_id": app_id_oxford, "app_key": app_key_oxford}
    try:
        response = requests.get(url_oxford, headers=headers_oxford, timeout=5)
        response.raise_for_status()
        data = response.json()
        if "results" in data:
            definitions = []
            for lexical_entry in data["results"][0].get("lexicalEntries", []):
                for entry in lexical_entry.get("entries", []):
                    for sense in entry.get("senses", []):
                        definitions.append({
                            "definition": sense.get("definitions", [""])[0],
                            "example": sense.get("examples", [{}])[0].get("text", ""),
                        })
            return {
                "word": word,
                "definitions": definitions,
                "phonetics": [],
            }
    except requests.exceptions.RequestException as e:
        print(f"Oxford API failed for '{word}': {e}")

    # If all APIs fail
    print(f"All APIs failed for '{word}'.")
    return None


def append_word_to_file(word, category, filepath="data/words.txt"):
    """
    Append a new word to the words.txt file under the specified category.
    :param word: The word to add.
    :param category: The category of the word.
    :param filepath: The path to the words.txt file.
    """
    try:
        with open(filepath, "a") as f:
            f.write(f"{category},{word.upper()}\n")
        print(f"Added word '{word}' to category '{category}' in {filepath}.")
    except IOError as e:
        print(f"Error appending word to file: {e}")


def save_topic_to_file(topic_name, data, folder="data/topics"):
    """
    Save a topic's data to a JSON file in the topics folder.
    :param topic_name: The name of the topic.
    :param data: The data to save.
    :param folder: The folder where topic files are stored.
    """
    os.makedirs(folder, exist_ok=True)
    # Sanitize the filename by replacing invalid characters with underscores
    sanitized_name = re.sub(r'[<>:"/\\|?*]', '_', topic_name)
    filepath = os.path.join(folder, f"{sanitized_name}.json")
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Saved topic '{topic_name}' to {filepath}.")
    except IOError as e:
        print(f"Error saving topic to file: {e}")