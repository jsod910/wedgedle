import json
from pathlib import Path

# Paths
RAW_PATH = Path("characters_raw.json")
MAIN_PATH = Path("../static/data/characters.json")

def main():
    # Load raw scraped data
    with open(RAW_PATH, "r", encoding="utf-8") as f:
        raw_characters = json.load(f)

    # Load main characters file
    with open(MAIN_PATH, "r", encoding="utf-8") as f:
        characters = json.load(f)

    # Build lookup from raw data by id
    raw_by_id = {
        char["name"]: char
        for char in raw_characters
        if "name" in char and "era" in char
    }

    updated = 0
    missing = 0

    for char in characters:
        char_id = char.get("name")

        if char_id in raw_by_id:
            # Add era
            char["era"] = raw_by_id[char_id]["era"]
            updated += 1
        else:
            missing += 1

        # Remove release_date if present
        if "release_era" in char:
            del char["release_era"]

    # Write updated characters.json
    with open(MAIN_PATH, "w", encoding="utf-8") as f:
        json.dump(characters, f, indent=2, ensure_ascii=False)

    print(f"✅ Updated era for {updated} characters")
    print(f"⚠️  Missing era for {missing} characters")

if __name__ == "__main__":
    main()
