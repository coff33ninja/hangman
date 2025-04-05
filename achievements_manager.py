import json

class AchievementsManager:
    def __init__(self):
        self.achievements = {}

    def generate_default_achievements(self):
        """
        Generate default achievements if they do not exist.
        """
        default_achievements = {
            "first_win": {"description": "Win your first game!", "unlocked": False},
            "no_hints": {"description": "Win a game without using hints.", "unlocked": False},
            "streak_5": {"description": "Win 5 games in a row.", "unlocked": False},
        }
        for key, value in default_achievements.items():
            if key not in self.achievements:
                self.achievements[key] = value

    def save_achievements(self, filepath="data/achievements.json"):
        with open(filepath, "w") as f:
            json.dump(self.achievements, f)

    def load_achievements(self, filepath="data/achievements.json"):
        try:
            with open(filepath, "r") as f:
                self.achievements.update(json.load(f))
        except FileNotFoundError:
            self.generate_default_achievements()  # Generate defaults if file not found
