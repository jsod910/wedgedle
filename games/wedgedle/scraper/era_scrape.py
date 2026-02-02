import json
import re
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

BASE_URL = "https://swgoh.gg/units/"
CHARACTERS_FILE = "characters_raw.json"

ERA_MAP = {
  0: "Legacy",
  1: "Apprentices",
  2: "Cavalry",
  3: "Revenge of the Sith",
  4: "Piracy",
  5: "Ships and Bounties",
  6: "10th Anniversary"
}


def extract_release_era(html):
    """
    Finds release_era_0x* in the HTML and returns the mapped era name.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Find all category links
    links = soup.select("a[href*='cat=release_era_']")

    for link in links:
        text = link.get_text(strip=True)

        match = re.search(r"release_era_(\d+)", text)
        if match:
            era_number = int(match.group(1))
            return ERA_MAP.get(era_number, "Unknown")

    return "Unknown"


def main():
    with open(CHARACTERS_FILE, "r", encoding="utf-8") as f:
        characters = json.load(f)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        page = context.new_page()

        for idx, character in enumerate(characters, start=1):
            char_id = character.get("id")
            if not char_id:
                continue

            url = f"{BASE_URL}{char_id}/"
            print(f"[{idx}/{len(characters)}] Fetching {url}")

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)

                page.wait_for_timeout(2000)

                # page.wait_for_selector(".unit-card-grid-cell")

                html = page.content()
                era = extract_release_era(html)

                character["era"] = era
                print(f"  → Era: {era}")

                # polite delay to avoid Cloudflare suspicion
                # time.sleep(1.5)

            except Exception as e:
                print(f"  ❌ Failed for {char_id}: {e}")
                character["era"] = "Unknown"

        browser.close()

    # Write updated data back to file
    with open(CHARACTERS_FILE, "w", encoding="utf-8") as f:
        json.dump(characters, f, indent=2)

    print("✅ Finished updating character eras")


if __name__ == "__main__":
    main()
