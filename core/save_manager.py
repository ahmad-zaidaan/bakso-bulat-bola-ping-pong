import json
import os


class SaveManager:
    def __init__(self, filename: str = "save_data.json"):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.filepath = os.path.join(base_dir, filename)

    def has_save(self) -> bool:
        return os.path.exists(self.filepath)

    def load_game(self) -> dict | None:
        if not self.has_save():
            return None
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading save file: {e}")
            return None

    def save_game(self, data: dict) -> bool:
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def delete_save(self):
        if self.has_save():
            try:
                os.remove(self.filepath)
            except Exception as e:
                print(f"Error deleting save file: {e}")


save_manager = SaveManager()
