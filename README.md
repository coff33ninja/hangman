# Hangman AI Game - README

Welcome to the **Hangman AI Game**, a reimagined twist on the classic word-guessing game. This project combines traditional gameplay with advanced AI-driven features, dynamic themes, and interactive UI elements to create a modern and engaging experience.

---

## 🎮 Features

### 🧠 Game Modes
- **Word Guess**: Classic Hangman gameplay with enhanced visuals and dynamic word lists.
- **Riddle Time**: Solve riddles instead of guessing random words. Riddles are sourced from both local files and online APIs.
- **Two-Player Mode**: One player provides a word, and the other guesses it.

### 📊 Difficulty Levels
- Easy, Medium, Hard – Adjusts word complexity, number of guesses, and time limits.

### 🧩 AI-Powered Enhancements
- **AI-Generated Words and Riddles**: The AI dynamically generates words and riddles for gameplay.
- **Dynamic Learning**: The AI learns from riddles and words during gameplay and updates its knowledge base.
- **Research Topics**: Ask the AI about a topic, and it will provide information or research it dynamically.
- **Fallback Responses**: If the AI cannot find detailed information, it provides related knowledge or a graceful fallback response.

### 🌐 Online/Offline Content Support
- Dynamically loads words and riddles from local storage or online APIs.
- Fetches definitions, synonyms, and examples for words using dictionary APIs.

### 🎨 Dynamic Themes
- **Theme Manager**: Switch between themes dynamically (e.g., "Default", "Spooky").
- **Custom Assets**: Each theme includes unique backgrounds, fonts, sounds, and Hangman images.

### 🏆 Achievements
- **Track Progress**: Unlock achievements like "First Win" or "Win Without Hints."
- **Reset Achievements**: Reset all achievements to start fresh.

### ⚡ Power-Ups
- **Hints**: Reveal a letter or get a definition.
- **Extra Attempts**: Gain additional chances to guess.
- **Reveal Letter**: Automatically reveal a letter in the word.

### ⏲️ Timer UI
- Time-based gameplay for added challenge.

### 🎨 Visual Progression
- The Hangman visually builds with each incorrect guess using sprite-based graphics.

### 🧱 Modular Structure
- Extensible managers for riddles, power-ups, themes, and AI.

---

## 🌐 APIs Used

This project uses the following APIs to enhance gameplay and AI functionality. We extend our gratitude to the providers of these APIs for their valuable services:

1. **[Dictionary API](https://dictionaryapi.dev/)**
   - Provides definitions, synonyms, antonyms, and example sentences for words.
   - Used for generating hints, categorizing words, and enhancing the AI's knowledge base.

2. **[Riddles API](https://riddles-api.vercel.app/)**
   - Supplies random riddles for the "Riddle Time" game mode.
   - Dynamically fetches riddles to keep the gameplay fresh and engaging.

3. **[Wikipedia API](https://www.mediawiki.org/wiki/API:Main_page)**
   - Fetches summaries and information about topics for the AI's research functionality.
   - Used to provide detailed answers to user queries.

4. **[ConceptNet API](https://conceptnet.io/)**
   - Provides related topics and semantic relationships for words and concepts.
   - Used for fallback responses and expanding the AI's knowledge graph.

---

## 🧠 AI Reasoning

The AI in this project is designed to enhance the classic Hangman game by introducing dynamic, intelligent, and interactive features.

### Dynamic Learning and Adaptation
- **Reasoning**: Static word lists and riddles can become repetitive. By allowing the AI to learn from user interactions, external APIs, and dynamically generated data, the game remains fresh and challenging.
- **Implementation**:
  - Dynamic word categorization using dictionary definitions.
  - Training on riddles and words during gameplay.
  - Periodic retraining to incorporate new knowledge.

### Intelligent Responses
- **Reasoning**: Players may ask the AI questions about words, riddles, or topics. The AI needs to provide meaningful answers, even if it has limited knowledge.
- **Implementation**:
  - Thinking and gathering states to indicate whether the AI is processing existing knowledge or performing research.
  - Fallback responses to provide related knowledge or graceful error handling.

### Dynamic Topic Management
- **Reasoning**: Topics and their associated data should be persistently stored and logically organized to improve the AI's knowledge base.
- **Implementation**:
  - Dynamic file and folder management for topics.
  - Logical naming strategies for topics (e.g., `topic.subtopic.detail`).

### Enhanced Gameplay Features
- **Reasoning**: Traditional Hangman gameplay can be improved with AI-powered features like hints, riddles, and dynamic word generation.
- **Implementation**:
  - AI-generated words and riddles.
  - Hints and definitions provided by the AI.
  - Power-ups like revealing letters or gaining extra attempts.

### Asynchronous Operations
- **Reasoning**: Blocking operations can make the game unresponsive. By using threading, the AI can perform tasks in the background without interrupting gameplay.
- **Implementation**:
  - Threading for research, retraining, and asset generation.
  - Callbacks to pass results from asynchronous operations back to the main thread.

---

## 🧱 File Structure Overview

```
hangman/
├── assets/                 # Theme assets (images, sounds, fonts)
│   ├── themes/             # Theme folders (e.g., default, spooky)
│   ├── images/             # Hangman images for different stages
│   ├── sounds/             # Sound effects for themes
├── data/                   # Game data
│   ├── words.txt           # Word list
│   ├── riddles_easy.txt    # Easy riddles
│   ├── riddles_medium.txt  # Medium riddles
│   ├── riddles_hard.txt    # Hard riddles
│   ├── topics/             # Dynamically saved topics
│   ├── achievements.json   # Saved achievements
│   ├── training_data.json  # AI training data
├── ai_manager.py           # AI logic and training
├── ai_gui.py               # PyQt6-based AI Training Assistant
├── asset_manager.py        # Asset generation and management
├── content_manager.py      # Word and riddle loading logic
├── game_logic.py           # Core game logic
├── theme_manager.py        # Theme management
├── ui_manager.py           # Pygame UI logic
├── main.py                 # Main entry point
├── achievements_manager.py # Achievements management
└── README.md               # Project documentation
```

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Required libraries:
  - `pygame`
  - `PyQt6`
  - `torch`
  - `transformers`
  - `requests`
  - `Pillow`

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/DRAGOHN/hangman.git
   cd hangman
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python main.py
   ```

---

## 🎮 How to Play

1. **Start the Game**:
   - Run `main.py` to launch the game.
   - Enter your name and proceed to the main menu.

2. **Choose a Mode**:
   - Select "Word Guess" or "Riddle Time" from the main menu.
   - Set the difficulty level (Easy, Medium, Hard).

3. **Gameplay**:
   - Guess letters or solve riddles within the allowed attempts.
   - Use power-ups like hints or extra attempts to improve your chances.

4. **Game Over**:
   - View the result and the correct word.
   - Choose to play again or return to the main menu.

5. **AI Training Assistant**:
   - Run `ai_gui.py` to interact with the AI.
   - Ask questions, research topics, and manage training data.

---

## 📅 Roadmap

### Current Features
- [x] Core game modes (Word Guess, Riddle Time)
- [x] Difficulty levels and word loading
- [x] Theme and power-up systems
- [x] AI-powered hints and dynamic learning

### Planned Features
- [ ] **Voice Interaction with AI**
  - Extend the `VoiceInput` class to handle complex commands like asking for hints, explaining riddles, or interacting with the AI.
- [ ] **Dynamic Riddle Generation**
  - Allow players to select categories or themes, and dynamically generate riddles using GPT-based models.
- [ ] **AI-Powered Hints**
  - Add context-aware hints, such as synonyms, related words, or partial definitions.
- [ ] **Learning Mode**
  - Add a mode where players can learn new words or riddles, with definitions, synonyms, and example usage displayed after each game.
- [ ] **AI Chat Companion**
  - Add a chatbot-like companion that players can interact with during the game for tips, trivia, or general knowledge.
- [ ] **Dynamic Difficulty Adjustment**
  - Use AI to adjust difficulty based on player performance, such as increasing attempts for struggling players or providing harder riddles for advanced players.
- [ ] **Multiplayer AI Mode**
  - Add an AI opponent that competes against the player in guessing words or solving riddles.
- [ ] **Custom Themes and Assets**
  - Allow players to upload custom themes, including Hangman images, sounds, and fonts, and validate them for integration.
- [ ] **Leaderboard and Statistics**
  - Add a leaderboard to track player scores, streaks, and achievements. Display it in the main menu or after each game.
- [ ] **Story Mode**
  - Add a narrative-driven mode where players progress through levels with increasing difficulty, unlocking new challenges and story elements.
- [ ] **AI-Generated Categories**
  - Use NLP or clustering algorithms to dynamically create new categories for words and riddles.
- [ ] **Educational Integration**
  - Add a mode for vocabulary building or language learning, with support for multiple languages using dictionary APIs.
- [ ] **AI-Powered Game Narrator**
  - Add a text-to-speech narrator to guide players through the game, narrate riddles, and provide hints dynamically.
- [ ] **Daily Challenges with AI Insights**
  - Enhance the daily challenge feature with AI-generated trivia or insights about the challenge.
- [ ] **AI-Driven Game Analytics**
  - Use AI to analyze player behavior and provide insights, such as common mistakes, strengths, and areas for improvement.

---

## 💡 Contribution & Feedback

Want to add a new mode? Submit a riddle pack? Bring your AI flavor to the game? Pull requests and ideas are welcome! Open an issue or contact me for collaborations.

---

## 🎤 Final Word

Hangman has grown up. No longer just a stickman on a rope — it's an AI playground of puns, puzzles, and possibility. Whether you're teaching or learning new words, challenging a friend to riddle duels, or exploring the AI's knowledge, this project has something for everyone.

**Ready to code the next clue? Let's hang.**

---

© 2025 DJ – Powered by Python, caffeine, and late-night "Eureka!" moments.

