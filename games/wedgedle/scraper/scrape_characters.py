from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import re

URL = "https://swgoh.gg/characters/"

ALIGNMENT_MAP = {
    "1": "Neutral",
    "2": "Light",
    "3": "Dark"
}

def scrape_characters():
    # headers = {
    #     "User-Agent": (
    #         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    #         "AppleWebKit/537.36 (KHTML, like Gecko) "
    #         "Chrome/120.0.0.0 Safari/537.36"
    #     )
    # }
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    # }
    # response = requests.get(URL, headers=headers)
    # response.raise_for_status()

    print("beginning scrape")
    # with sync_playwright() as p:
    #     browser = p.chromium.launch(headless=True)
    #     page = browser.new_page()

    #     page.goto(URL, timeout=60000)
    #     page.wait_for_selector(".unit-card-grid__cell")

    #     html = page.content()
    #     browser.close()
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

        page.goto(URL, wait_until="networkidle", timeout=60000)
        print(page.title())

        page.wait_for_selector(
            ".unit-card-grid__cell",
            timeout=60000
        )

        html = page.content()
        browser.close()

    print("finished scrape; beginning parse")
    soup = BeautifulSoup(html, "html.parser")

    characters = []

    cells = soup.select(".unit-card-grid__cell")

    for cell in cells:
        name = cell.get("data-unit-name", "").strip()
        tags = cell.get("data-unit-tags", "")
        factions = [t.strip() for t in tags.split(",") if t.strip()]

        link = cell.select_one("a[href]")
        # unit_url = "https://swgoh.gg" + link["href"] if link else None
        unit_id = link["href"].strip("/").split("/")[-1] if link else None

        card = cell.select_one(".unit-card")
        alignment = None
        if card:
            match = re.search(r"unit-card--alignment-(\d)", " ".join(card.get("class", [])))
            if match:
                alignment = ALIGNMENT_MAP.get(match.group(1))

        role = None
        cats = cell.select_one(".unit-card__cats")
        if cats:
            role = cats.get_text(strip=True).split("•")[0].strip()

        image_url = None
        portrait = cell.select_one(".character-portrait")
        if portrait:
            style = portrait.get("style", "")
            match = re.search(r"url\((.*?)\)", style)
            if match:
                image_url = match.group(1)

        character = {
            "id": unit_id,
            "name": name,
            "alignment": alignment,
            "role": role,
            "factions": factions,
            "image_url": image_url
            # "unit_url": unit_url
        }

        print("Scraped: ", character["name"])
        characters.append(character)

    return characters


if __name__ == "__main__":
    data = scrape_characters()

    with open("characters_raw.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Scraped {len(data)} characters.")
