import json
import requests
import shutil
from pathlib import Path
from src.config.paths import DATA_DIR

PATCH_VERSION_URL = "https://ddragon.leagueoflegends.com/api/versions.json"
CHAMPION_DATA_URL = "https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/champion.json"
CHAMPION_ICON_URL = "https://ddragon.leagueoflegends.com/cdn/{patch}/img/champion/{filename}"

DDDRAGON_DIR = DATA_DIR / "ddragon"
ICON_DIR = DDDRAGON_DIR / "icons"
RAW_DIR = DDDRAGON_DIR / "raw"


def fetch_latest_patch() -> str:
    r = requests.get(PATCH_VERSION_URL, timeout=10)
    r.raise_for_status()
    return r.json()[0]


def fetch_champion_json(patch: str) -> dict:
    url = CHAMPION_DATA_URL.format(patch=patch)
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def save_raw_json(patch: str, data: dict) -> None:
    path = RAW_DIR / patch / "ddragon_champions.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def download_champion_icon(patch: str, icon_dir: Path, filename: str) -> None:
    url = CHAMPION_ICON_URL.format(patch=patch, filename=filename)
    filepath = icon_dir / filename
    if filepath.exists():
        return

    r = requests.get(url, timeout=10)
    r.raise_for_status()
    filepath.write_bytes(r.content)


def update_ddragon(keep_only_latest: bool = True) -> str:
    ICON_DIR.mkdir(parents=True, exist_ok=True)

    patch = fetch_latest_patch()

    if keep_only_latest:
        for p in ICON_DIR.iterdir():
            if p.is_dir() and p.name != patch:
                shutil.rmtree(p)

    patch_icon_dir = ICON_DIR / patch
    patch_icon_dir.mkdir(parents=True, exist_ok=True)

    champ_json = fetch_champion_json(patch)
    save_raw_json(patch, champ_json)

    for champ_data in champ_json["data"].values():
        filename = champ_data["image"]["full"]
        download_champion_icon(patch, patch_icon_dir, filename)

    return patch
