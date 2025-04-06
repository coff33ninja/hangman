import json
import uuid
import sqlite3
import os  # Import os to check for database existence

class ScoreManager:
    def __init__(self, filepath="data/scores.json", db_path="data/scores.db"):
        self.filepath = filepath
        self.db_path = db_path
        self.scores = self.load_scores()
        self.hardware_id = self.get_hardware_id()

    def get_hardware_id(self):
        """
        Generate or retrieve a unique hardware ID.
        """
        try:
            return str(uuid.getnode())  # Use MAC address as hardware ID
        except Exception:
            return str(uuid.uuid4())  # Fallback to random UUID

    def load_scores(self):
        try:
            with open(self.filepath, "r") as f:
                return json.load(f)["scores"]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_scores(self):
        with open(self.filepath, "w") as f:
            json.dump({"scores": self.scores}, f)

    def add_score(self, player_name, score):
        self.scores.append({"name": player_name, "score": score, "hardware_id": self.hardware_id})
        # Sort scores and handle ties
        self.scores = sorted(self.scores, key=lambda x: x["score"], reverse=True)
        top_scores = self.scores[:10]
        # Include ties
        self.scores = [s for s in self.scores if s["score"] >= top_scores[-1]["score"]]
        self.save_scores()

    def get_top_scores(self):
        return self.scores

    def setup_database(self):
        """
        Setup SQLite database for score tracking.
        """
        if not os.path.exists(self.db_path):  # Check if the database already exists
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT,
                    score INTEGER,
                    hardware_id TEXT
                )
            """)
            conn.commit()
            conn.close()

    def add_score_to_db(self, player_name, score):
        """
        Add a score to the SQLite database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(""" 
            INSERT INTO scores (player_name, score, hardware_id)
            VALUES (?, ?, ?)
        """, (player_name, score, self.hardware_id))
        conn.commit()
        conn.close()

    def get_top_scores_from_db(self, limit=10):
        """
        Retrieve top scores from the SQLite database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(""" 
            SELECT player_name, score FROM scores
            ORDER BY score DESC
            LIMIT ?
        """, (limit,))
        scores = cursor.fetchall()
        conn.close()
        return scores
