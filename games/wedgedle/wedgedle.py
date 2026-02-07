
from enum import Enum
from datetime import date
import copy
import json
import hashlib
from pathlib import Path
import random
from uuid import uuid4

from utils.reset_time import get_game_day_index

GAME_START_DATE = date(2026,1,1)
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "characters.json";

# feedback
class Result(Enum):
    CORRECT = "correct"
    PARTIAL = "partial"
    INCORRECT = "incorrect"
    HIGHER = "higher"
    LOWER = "lower"

games = {}

class WedgedleGame:
    def __init__(self):
        self.characters = self._load_characters()
        self.lookup = self._build_lookup()

    def _load_characters(self):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def _build_lookup(self):
        lookup = {}
        
        for char in self.characters:
            canonical = char["name"]
            lookup[self.normalize(canonical)] = canonical

            for alias in char.get("aliases", []):
                lookup[self.normalize(alias)] = canonical
 
        return lookup

    def get_character(self, name):
        for char in self.characters:
            if char["name"] == name:
                return char
            
        return None
    
    def get_target(self, mode, game_id):
        if mode == "daily":
            return self.get_daily_character()
        elif mode == "unlimited":
            return self.get_character(games[game_id])
        return {}

    def normalize(self, name):
        return name.strip().lower()

    def get_daily_character(self):
        day_index = get_game_day_index(GAME_START_DATE)

        if day_index < 0:
            day_index = 0
        
        hash_input = f"wedgedle-{day_index}".encode("utf-8")
        digest = hashlib.sha256(hash_input).hexdigest()

        idx = int(digest, 16) % len(self.characters)
        return self.characters[idx]

    def start_unlimited_game(self):
        game_id = uuid4().hex
        target = random.choice(self.characters)

        target_name = target["name"]
        games[game_id] = target_name
        return game_id

    # compare fields of guess and target
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

        if guess["crew_member"] == target["crew_member"]:
            feedback["crew_member"] = Result.CORRECT
        else:
            feedback["crew_member"] = Result.INCORRECT
        
        if guess["leader"] == target["leader"]:
            feedback["leader"] = Result.CORRECT
        else:
            feedback["leader"] = Result.INCORRECT
        
        # if guess["era"] == target["era"]:
        #     feedback["era"] = Result.CORRECT
        # else:
        #     feedback["era"] = Result.INCORRECT

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

    # core functionality
    def check_guess(self, guess_name, mode, game_id):
        # target = self.get_daily_character()
        target = self.get_target(mode, game_id)

        user_input = self.normalize(guess_name)
        if user_input not in self.lookup:
            return {
                "valid": False,
                "error": "Unknown Character"       
        }
        
        canonical = self.lookup[user_input]
        guess = self.get_character(canonical)

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

    def search_characters(self, query, limit=8):
        q = self.normalize(query)
        if not q:
            return []
        
        matches = []
        for char in self.characters:
            if q in char["name"].lower():
                matches.append({
                    "name": char["name"],
                    "image": char["image"],
                    "alignment": char["alignment"]
                })
        
        return matches[:limit]
    
    def get_images(self):
        images = []
        for char in self.characters:
            # images.append({
            #     "id": char["id"],
            #     "image": char["image"]
            # })
            images.append(char["image"])
        return images

    # test harness
    # def run_test():
    #     target_name = get_daily_characters(CHARACTERS)
    #     target = CHARACTERS[target_name]
    #     # LOOKUP = build_lookup(CHARACTERS,ALIASES)

    #     print("Guess the SWGOH character!")

    #     num_guesses = 3
    #     while num_guesses > 0:
    #         print("Guesses Remaining: ", num_guesses)
    #         user_input = normalize(input("Enter character name: "))
    #         if user_input not in LOOKUP:
    #             print("Invalid character.")
    #             continue

    #         num_guesses -= 1
    #         print("You Guessed: ", LOOKUP[user_input])
    #         guess = CHARACTERS[LOOKUP[user_input]]
    #         feedback = give_feedback(guess, target)

    #         for attr, result in feedback.items():
    #             print(f"{attr}: {result.value}")

    #         if all(r == Result.CORRECT for r in feedback.values()):
    #             print("You Win!")
    #             break
            
    # if __name__ == "__main__":
    #     run_test()