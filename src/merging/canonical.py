import json
from pathlib import Path


def merge_champion_data(
    ddragon_basic: dict,
    fandom_champions: dict,
    fandom_aram_modifiers: dict,
    patch: str,  
):
    merged = {}

    for champ_id, ddragon_info in ddragon_basic.items():
        name = ddragon_info["name"]

        lua_info = fandom_champions.get(champ_id, {})
        aram_mods = lua_info.get("aram", {}) if lua_info else {}

        spell_changes = fandom_aram_modifiers.get(name, {})
        entry = {
            "id": champ_id,
            "key": ddragon_info["key"],
            "name": name,
            "tags": ddragon_info.get("tags", [])
        }

        if aram_mods:
            entry["aram_mods"] = aram_mods

        if spell_changes and any(
            spell_changes.get(k) for k in ["P", "Q", "W", "E", "R"]
        ):
            entry["spell_changes"] = spell_changes

        merged[champ_id] = entry

    snapshot = {
        "patch": patch,
        "champions": merged,
    }

    output_path = Path(f"data/canonical/{patch}.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)

    return output_path