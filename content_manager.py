# content_manager.py

import random

import requests





def load_words(filepath="data/words.txt"):

    """

    Load words from a file into a dictionary by category.

    Format: category,word (e.g., animals,lion)

    """

    words = {"default": ["PYTHON", "GAME", "HANGMAN"]}  # Ensure a default category exists

    try:

        with open(filepath, "r") as f:

            for line in f:

                try:

                    category, word = line.strip().split(",", 1)

                    words.setdefault(category, []).append(word.upper())

                except ValueError:

                    print(f"Malformed line in words file: {line}")

    except FileNotFoundError:

        print(f"Words file not found. Using default words: {words['default']}")

    return {category: random.sample(words, len(words)) for category, words in words.items()}





def load_riddles(difficulty_files=None):

    """

    Load riddles from separate files for each difficulty level.

    If no files are provided, default to 'data/riddles.txt'.

    """

    if difficulty_files is None:

        difficulty_files = {

            "easy": "data/riddles_easy.txt",

            "medium": "data/riddles_medium.txt",

            "hard": "data/riddles_hard.txt",

        }



    riddles = {}

    for difficulty, filepath in difficulty_files.items():

        try:

            with open(filepath, "r") as f:

                for line in f:

                    try:

                        riddle, answer = line.strip().split(",", 1)

                        riddles.setdefault(difficulty, []).append((riddle, answer.upper()))

                    except ValueError:

                        print(f"Malformed line in {filepath}: {line}")

        except FileNotFoundError:

            print(f"Riddles file not found: {filepath}")

    return riddles





def fetch_online_riddles(num_riddles=5, filepath="data/riddles.txt"):

    """

    Fetch random riddles from riddles-api.vercel.app and store them in riddles.txt.

    Categorize riddles based on the length of the answer.

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



    # Categorize and store riddles in riddles.txt

    try:

        with open(filepath, "a") as f:

            for riddle, answer in riddles:

                word_count = len(answer.split())

                if word_count > 5:

                    category = "hard"

                elif 1 <= word_count <= 5:

                    category = "medium"

                else:

                    category = "easy"

                f.write(f"{category},{riddle},{answer}\n")

    except IOError as e:

        print(f"Error writing riddles to file: {e}")



    return {"online": riddles}





def fetch_word_definition(word):

    """

    Fetch a definition for a word from dictionaryapi.dev.

    Returns the first definition or a fallback message.

    """

    try:

        response = requests.get(

            f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.lower()}", timeout=5

        )

        if response.status_code == 200:

            data = response.json()

            return data[0]["meanings"][0]["definitions"][0]["definition"]

        else:

            print(f"Dictionary API Error: {response.status_code}")

    except requests.RequestException as e:

        print(f"Dictionary API Network Error: {e}")

    return "No definition available."