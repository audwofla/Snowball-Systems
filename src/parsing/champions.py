from lupa import LuaRuntime
from pathlib import Path
from src.config.paths import DATA_DIR

def lua_to_py(obj):
    if hasattr(obj, "items"):
        return {lua_to_py(k): lua_to_py(v) for k, v in obj.items()}
    return obj

def parse_champions_lua() -> dict:
    path = DATA_DIR / "fandom_api" / "raw" / "champions.lua"

    lua = LuaRuntime(unpack_returned_tuples=True)
    table = lua.execute(path.read_text(encoding="utf-8"))
    py_data = lua_to_py(table)

    champions = {}

    for champ_name, champ_data in py_data.items():
        champ_id = champ_data.get("id")
        if not champ_id:
            continue

        aram = champ_data.get("stats", {}).get("aram")
        if not aram:
            continue

        champions[champ_id] = {
            "name": champ_name,
            "aram": aram
        }

    return champions