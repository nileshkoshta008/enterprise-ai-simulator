import json
import os
from datetime import datetime

LOG_FILE = "logs.jsonl"
LEADERBOARD_FILE = "leaderboard.json"

class AnalyticsTracker:
    @staticmethod
    def log_step(email_id: str, action: dict, reward: float, reasoning: str = ""):
        """
        Logs a single episode step linearly to JSONL.
        """
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "email_id": email_id,
                "action": action,
                "reward": reward,
                "reasoning": reasoning
            }
            with open(LOG_FILE, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except:
            # Skip logging if filesystem is read-only (Vercel)
            pass

    @staticmethod
    def update_leaderboard(model_name: str, avg_score: float):
        """
        Maintains descending ranking of models.
        """
        data = []
        if os.path.exists(LEADERBOARD_FILE):
            try:
                with open(LEADERBOARD_FILE, "r") as f:
                    data = json.load(f)
            except:
                pass

        try:
            # Update or Insert
            found = False
            for entry in data:
                if entry["model"] == model_name:
                    # Update if better
                    if avg_score > entry["score"]:
                        entry["score"] = avg_score
                    found = True
                    break
            
            if not found:
                data.append({"model": model_name, "score": avg_score})
                
            # Sort descending
            data.sort(key=lambda x: x["score"], reverse=True)
            
            with open(LEADERBOARD_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except:
            pass

    @staticmethod
    def get_leaderboard():
        """Reads and returns leaderboard data."""
        if not os.path.exists(LEADERBOARD_FILE):
            return []
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                return json.load(f)
        except:
            return []
