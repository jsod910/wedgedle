from enum import Enum
from datetime import date
import copy
import json
import hashlib
from pathlib import Path

from utils.reset_time import get_game_day_index

GAME_START_DATE = date(2026,1,1)
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "ships.json";


# feedback
class Result(Enum):
    CORRECT = "correct"
    PARTIAL = "partial"
    INCORRECT = "incorrect"
    HIGHER = "higher"
    LOWER = "lower"

class ShipdleGame:
    def __init__(self):
        self.ships = self._load_ships()
        self.lookup = self._build_lookup()

    def _load_ships(self):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def _build_lookup(self):
        lookup = {}
        
        for ship in self.ships:
            canonical = ship["name"]
            lookup[self.normalize(canonical)] = canonical

            for alias in ship.get("aliases", []):
                lookup[self.normalize(alias)] = canonical
 
        return lookup
    
    def get_ship(self, name):
        for ship in self.ships:
            if ship["name"] == name:
                return ship
            
        return None

    def normalize(self, name):
        return name.strip().lower()

    def get_daily_ship(self):
        day_index = get_game_day_index(GAME_START_DATE)

        if day_index < 0:
            day_index = 0
        
        hash_input = f"shipdle-{day_index}".encode("utf-8")
        digest = hashlib.sha256(hash_input).hexdigest()

        idx = int(digest, 16) % len(self.ships)
        return self.ships[idx]
    
    def give_feedback(self, guess, target):
        feedback = {}

        if guess["alignment"] == target["alignment"]:
            feedback["alignment"] = Result.CORRECT
        else:
            feedback["alignment"] = Result.INCORRECT

        if guess["role"] == target["role"]:
            feedback["role"] = Result.CORRECT
        else:
            feedback["role"] = Result.INCORRECT

        if set(guess["factions"]) == set(target["factions"]):
            feedback["factions"] = Result.CORRECT
        elif set(guess["factions"]) & set(target["factions"]):
            feedback["factions"] = Result.PARTIAL
        else:
            feedback["factions"] = Result.INCORRECT

        if guess["crew_members"] == target["crew_members"]:
            feedback["crew_members"] = Result.CORRECT
        elif guess["crew_members"] > target["crew_members"]:
            feedback["crew_members"] = Result.LOWER
        else:
            feedback["crew_members"] = Result.HIGHER

        if guess["release_date"] == target["release_date"]:
            feedback["release_date"] = Result.CORRECT
        elif guess["release_date"] > target["release_date"]:
            feedback["release_date"] = Result.LOWER
        elif guess["release_date"] < target["release_date"]:
            feedback["release_date"] = Result.HIGHER
        
        return feedback
    
    def check_answer(self, guess_id, target_id):
        if target_id == guess_id:
            return True

        return False 
    
    def check_guess(self, guess_name):
        target = self.get_daily_ship()

        user_input = self.normalize(guess_name)
        if user_input not in self.lookup:
            return {
                "valid": False,
                "error": "Unknown Character"       
        }
        
        canonical = self.lookup[user_input]
        guess = self.get_ship(canonical)

        correct_guess = self.check_answer(guess["id"], target["id"])
        feedback = self.give_feedback(guess, target)

        return {
            "valid": True,
            "correct_guess": correct_guess,
            "result": {k: v.value for k, v in feedback.items()},
            "guess_info": {
                "name": canonical,
                "info": copy.deepcopy(guess)
            }
        }

    def search_ships(self, query, limit=8):
        q = self.normalize(query)
        if not q:
            return []
        
        matches = []
        for ship in self.ships:
            if q in ship["name"].lower():
                matches.append({
                    "name": ship["name"],
                    "image": ship["image"],
                    "alignment": ship["alignment"]
                })
        
        return matches[:limit]
    
    # for preloading images (not used rn)
    def get_images(self):
        images = []
        for ship in self.ships:
            images.append(ship["image"])
        return images

def run_test():
    game = ShipdleGame()

    print("Guess the ship")
    num_guesses = 4

    while num_guesses > 0:
        print(f"Guesses Remaining: {num_guesses}")
        user_input = input("Enter ship name: ")

        feedback = game.check_guess(user_input)
        if feedback["valid"] == False:
            print("Not a valid ship\n")
            continue

        num_guesses -= 1
        print(f"Guess: {feedback['guess_info']['name']}")
        
        for attr,result in feedback["result"].items():
            print(f"{attr}: {result}\n")

        if all(r=="correct" for r in feedback["result"].values()):
            print("You Win!")
            return
    
    print("Out of Guesses")
    print(f"The answer was: {game.get_daily_ship()['name']}")
        
if __name__ == "__main__":
    run_test()