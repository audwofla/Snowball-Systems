import json
from pathlib import Path
from pprint import pprint
from src.config.paths import DATA_DIR


BASE_DIR = Path(__file__).resolve().parents[1]

def parse_ddragon_basic_json(patch):
    path = DATA_DIR / "ddragon" / "raw" / patch / "ddragon_champions.json"
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    champions = {}

    for champ in data["data"].values():
        champ_id = int(champ["key"])

        champions[champ_id] = {
            "id": champ_id,
            "key": champ["id"],
            "name": champ["name"],
            "tags": champ.get("tags", [])

        }

    return champions

