import json
import os
import requests

RAW_PATH = "characters_raw.json"
OUTPUT_PATH = "characters.json"
IMAGE_DIR = "data/images"

FACTIONS_TO_REMOVE = {
    "Leader",
    "Fleet Commander",
    "Order 66 Raid",
    "Galactic Legend"
}

def slugify(char_id):
    return char_id.lower().replace("-", "_")

def download_image(url, filename):
    os.makedirs(IMAGE_DIR, exist_ok=True)
    path = os.path.join(IMAGE_DIR, filename)

    if os.path.exists(path):
        return path

    resp = requests.get(url, timeout=20)
    resp.raise_for_status()

    with open(path, "wb") as f:
        f.write(resp.content)

    return path

def transform_character(raw):
    factions = raw.get("factions", [])

    leader = "Leader" in factions
    crew_member = "Fleet Commander" in factions

    cleaned_factions = [
        f for f in factions if f not in FACTIONS_TO_REMOVE
    ]

    char_id = slugify(raw["id"])
    image_filename = f"{char_id}.webp"

    # Download image
    image_path = download_image(raw["image_url"], image_filename)

    return {
        "id": char_id,
        "name": raw["name"],
        "aliases": [],            # manual for now
        "image": image_path,
        "alignment": raw["alignment"],
        "role": raw["role"],
        "factions": cleaned_factions,
        "crew_member": crew_member,
        "leader": leader,
        "release_date": None      # manual for now
    }

def main():
    with open(RAW_PATH, "r", encoding="utf-8") as f:
        raw_chars = json.load(f)

    transformed = [transform_character(c) for c in raw_chars]

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(transformed, f, indent=2)

    print(f"Saved {len(transformed)} characters")

if __name__ == "__main__":
    main()
