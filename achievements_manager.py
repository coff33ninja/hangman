import json

class AchievementsManager:
    def save_achievements(self, filepath="data/achievements.json"):
        with open(filepath, "w") as f:
            json.dump(self.achievements, f)

    def load_achievements(self, filepath="data/achievements.json"):
        try:
            with open(filepath, "r") as f:
                self.achievements.update(json.load(f))
        except FileNotFoundError:
            pass
