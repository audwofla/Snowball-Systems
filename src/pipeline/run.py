from pathlib import Path
from src.config.paths import DATA_DIR
from src.ingestion.ddragon import update_ddragon, fetch_latest_patch
from src.ingestion.fandom import update_fandom
from src.parsing.ddragon import parse_ddragon_basic_json
from src.parsing.champions import parse_champions_lua
from src.parsing.aram_modifiers import parse_aram_modifiers
from src.merging.canonical import merge_champion_data

def run_pipeline():
    latest_patch = fetch_latest_patch()
    patch_dir = DATA_DIR / "ddragon" / "raw" / latest_patch

    if patch_dir.exists():
        print(f"Patch {latest_patch} already downloaded. Skipping ingestion.")
        patch = latest_patch
    else:
        print(f"New patch detected: {latest_patch}")
        update_fandom()
        patch = update_ddragon(keep_only_latest=True)

    print("Parsing data...")
    ddragon_basic = parse_ddragon_basic_json(patch)
    champions_lua = parse_champions_lua()
    aram_changes = parse_aram_modifiers()

    print("Merging...")
    canonical = merge_champion_data(
        ddragon_basic,
        champions_lua,
        aram_changes
    )

    return patch, canonical
