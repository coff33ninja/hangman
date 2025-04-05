# Hangman AI Game - README

Welcome to the **Hangman AI Game** — a reimagined twist on the classic word-guessing game, infused with powerful AI-driven features, dynamic gameplay modes, and a modular design to build upon.

---

## 🎮 Current Features

### 🧠 Game Modes
- **Word Guess** – Classic Hangman with enhanced visuals and dynamic word lists.
- **Riddle Time** – Solve riddles instead of guessing random words. Riddle content supports both local and online sources.

### 📊 Difficulty Levels
- Easy, Medium, Hard – changes word complexity and number of guesses.

### 🧩 AI & Smart Hints
- **AIManager** provides context-aware hints (e.g., definitions, letter frequency analysis, synonyms).

### 🌐 Online/Offline Content Support
- Dynamically loads words and riddles from local storage or online APIs.

### 🎨 Visual Progression
- The Hangman visually builds with each incorrect guess using sprite-based graphics.

### ⏲️ Timer UI
- Time-based gameplay for added challenge.

### 🧱 Modular Structure
- Extensible managers for riddles, power-ups, themes, and AI.

---

## 🚀 Advanced Features (In Progress or Planned)

### 🛠️ Game Enhancements
- **PowerUps** – Add extra lives, reveal letters, or freeze the timer.
- **Themes** – Visual customization of the game interface (dark mode, fun styles, etc.).
- **Scorekeeping & Achievements** – Track progress and unlock badges.
- **Multiplayer Support** – Online/local multiplayer modes for competitive/co-op play.

### 🤖 AI Enhancements
- **Adaptive Difficulty** – Game learns from the player and adjusts difficulty.
- **AI Chat Persona** – In-game assistant providing gameplay tips and banter (Paimon/Zhongli-style personas).
- **Contextual Hint Learning** – AI learns from gameplay to improve hint accuracy.

### 🌍 External Integration
- **Dictionary APIs** – Fetch definitions, examples, and more.
- **Image APIs** – Visual hints or theme images.
- **Translation APIs** – Multilingual support for riddles and words.

---

## 🧠 Future AI & Gameplay Ideas

### 1. **Voice Interaction with AI**
- Guess letters or ask for hints with voice commands.
- Uses `SpeechRecognition` + AI for NLP.

### 2. **Dynamic Riddle Generation**
- AI generates new riddles on-demand based on categories.

### 3. **AI-Powered Hints**
- Partial definitions, synonyms, or word associations.

### 4. **Learning Mode**
- Teaches new words post-game with definitions, synonyms, and progress tracking.

### 5. **AI Chat Companion**
- A friendly chatbot that chats about riddles or guides gameplay.

### 6. **Dynamic Difficulty Adjustment**
- Learns player performance and adjusts game mechanics.

### 7. **Multiplayer AI Mode**
- Compete against an AI player who makes guesses too.

### 8. **Custom Themes & Assets**
- Players can upload and use their own backgrounds, sprites, fonts, etc.

### 9. **Leaderboard & Stats**
- Tracks top players, longest streaks, highest scores, etc.

### 10. **Story Mode**
- Narrative-based progression tied into riddles or categories.

### 11. **AI-Generated Categories**
- NLP used to group words/riddles into creative new categories.

### 12. **Educational Integration**
- Mode for teaching vocabulary, riddles, or even language learning.

### 13. **AI-Powered Game Narrator**
- Text-to-speech narrator reads game text, riddles, or guides you.

### 14. **Daily Challenges with AI Insights**
- AI-curated daily riddle/word + bonus facts or trivia.

### 15. **AI-Driven Game Analytics**
- Insight into player habits, strengths, and improvement paths.

---

## 🧱 File Structure Overview
```
project/
├── main.py                  # Main game loop and screen control
├── assets/                  # Visual/audio/game assets
├── data/                    # Words, riddles, player stats, and config
├── managers/                # Modular logic managers (AI, themes, powerups, etc.)
├── components/              # UI and game elements (timer, buttons, etc.)
└── utils/                   # Helper functions (text wrap, image loader, etc.)
```

---

## 💡 Contribution & Feedback
Want to add a new mode? Submit a riddle pack? Bring your AI flavor to the game? Pull requests and ideas are welcome! Open an issue or contact me for collaborations.

---

## ⚙️ Requirements
- Python 3.10+
- Pygame
- Requests
- Internet Access

---

## 📅 Roadmap
- [x] Core game modes (Word, Riddle)
- [x] Difficulty levels and word loading
- [x] Theme and power-up systems
- [ ] Multiplayer logic
- [ ] AI Persona integration
- [ ] Story mode with riddle progression
- [ ] Leaderboard + stats tracking
- [ ] Dynamic category learning

---

## 🎤 Final Word
Hangman has grown up. No longer just a stickman on a rope — it's an AI playground of puns, puzzles, and possibility. Whether you're teaching or learning new words, challenging a friend to riddle duels, this project has legs. Long, shadowy, code-drenched legs.

**Ready to code the next clue? Let's hang.**

---

© 2025 DJ – Powered by Python, caffeine, and late-night "Eureka!" moments.

