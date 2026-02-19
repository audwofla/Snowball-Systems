from src.pipeline.run import run_pipeline

if __name__ == "__main__":
    patch, canonical = run_pipeline()
    print(f"Built champion dataset for patch {patch}")

    for champ in canonical.values():
        if champ.get("spell_changes"):
            print("\nSample champion with changes:")
            from pprint import pprint

            pprint(champ, sort_dicts=False)
            break