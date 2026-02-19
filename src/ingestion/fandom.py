import requests
from pathlib import Path
from src.config.paths import DATA_DIR

API_URL = "https://leagueoflegends.fandom.com/api.php"
HEADERS = {"User-Agent": "Aram Modifiers Bot/1.0"}

FANDOM_RAW_DIR = DATA_DIR / "fandom_api" / "raw"
FANDOM_RAW_DIR.mkdir(parents=True, exist_ok=True)

def save_raw(filename: str, content: str) -> Path:
    path = FANDOM_RAW_DIR / filename
    path.write_text(content, encoding="utf-8")
    return path

def fetch_data(title: str) -> str:
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "titles": title,
        "origin": "*",
    }

    r = requests.get(API_URL, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()

    data = r.json()
    page = data["query"]["pages"][0]

    if "missing" in page:
        raise ValueError(f"Page not found: {title}")

    revs = page.get("revisions")
    if not revs:
        raise ValueError(f"No revisions/content available for: {title}")

    return revs[0]["slots"]["main"]["content"]

def update_fandom() -> None:
    champ_content = fetch_data("Module:ChampionData/data")
    aram_content = fetch_data("Template:Map_changes/data/aram")

    save_raw("champions.lua", champ_content)
    save_raw("aram_modifiers.wikitext", aram_content)
