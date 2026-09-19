import json
import os

SAVE_FILE = "save_data.json"

class SaveManager:
    def __init__(self, filepath: str = None):
        if filepath is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.filepath = os.path.join(base_dir, SAVE_FILE)
        else:
            self.filepath = filepath

    def has_save(self) -> bool:
        return os.path.exists(self.filepath)

    def save_game(self, data: dict) -> bool:
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def load_game(self) -> dict | None:
        if not self.has_save():
            return None
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading game: {e}")
            return None

    def delete_save(self) -> bool:
        if self.has_save():
            try:
                os.remove(self.filepath)
                return True
            except Exception as e:
                print(f"Error deleting save: {e}")
                return False
        return False

save_manager = SaveManager()
