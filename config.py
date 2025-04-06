# config.py

# Screen settings
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)

# Game settings
DIFFICULTY_ATTEMPTS = {1: 6, 2: 9, 3: 13}  # Attempts per difficulty level
HINTS_PER_GAME = 2
MAX_POWER_UPS = {"reveal_letter": 3, "extra_attempt": 3}

# AI and timer settings
AI_GENERATED_RIDDLES = True

# Configurable TIMER_LIMIT based on difficulty
TIMER_LIMITS = {1: 30, 2: 60, 3: 90}  # Timer limits for different difficulty levels
