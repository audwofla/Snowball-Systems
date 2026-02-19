from pathlib import Path
import re
from pprint import pprint
from src.config.paths import DATA_DIR


TEMPLATE_RE = re.compile(r"\{\{([^{}]|\{[^{}]*\})*\}\}")

def extract_champions(text: str) -> str:
    start_marker = "<!--Champions-->"
    start = text.find(start_marker)
    if start == -1:
        raise ValueError("Start marker not found")

    start += len(start_marker)
    end = text.find("<!--", start)
    return (text[start:] if end == -1 else text[start:end]).strip()

def expand_range(value: str) -> str:
    """
    Expands wiki shorthand:
      "6 to 14"    -> "6 / 8 / 10 / 12 / 14"   (default 5 ranks)
      "2 to 4 3"   -> "2 / 3 / 4"              (explicit 3 ranks)
      Supports floats too.
    """
    m = re.match(
        r"^\s*(\d+(?:\.\d+)?)\s+to\s+(\d+(?:\.\d+)?)(?:\s+(\d+))?\s*$",
        value,
    )
    if not m:
        return value

    start = float(m.group(1))
    end = float(m.group(2))
    ranks = int(m.group(3)) if m.group(3) else 5

    if ranks < 2:
        return str(int(start) if start.is_integer() else start)

    step = (end - start) / (ranks - 1)
    values = [start + step * i for i in range(ranks)]

    formatted = []
    for v in values:
        if abs(v - round(v)) < 1e-9:
            formatted.append(str(int(round(v))))
        else:
            formatted.append(f"{v:.4f}".rstrip("0").rstrip("."))

    return " / ".join(formatted)

def template_to_values(template_text: str) -> str:
    inner = template_text[2:-2]
    parts = [p.strip() for p in inner.split("|")]
    params = parts[1:]

    vals = []
    for p in params:
        if "=" in p:
            continue
        if p:
            vals.append(expand_range(p))  # <-- expand ranges here

    return " ".join(vals)

def flatten_templates(text: str) -> str:
    while True:
        new = TEMPLATE_RE.sub(lambda m: template_to_values(m.group(0)), text)
        if new == text:
            return text
        text = new

def strip_bold_italics(text: str) -> str:
    text = re.sub(r"'''''(.*?)'''''", r"\1", text)
    text = re.sub(r"'''(.*?)'''", r"\1", text)
    text = re.sub(r"''(.*?)''", r"\1", text)
    return text

def build_champion_dict(text: str) -> dict:
    ABILITY_ORDER = ["P", "Q", "W", "E", "R"]

    champ_dict = {}
    current_champ = None
    current_ability = None

    lines = text.splitlines()
    header_re = re.compile(r"^\|(.+?)\s+([A-Z])\s*=")

    for line in lines:
        line = line.strip()

        header_match = header_re.match(line)
        if header_match:
            current_champ = header_match.group(1).strip()
            current_ability = header_match.group(2).strip()

            if current_ability == "I":
                current_ability = "P"

            if current_champ not in champ_dict:
                champ_dict[current_champ] = {ability: [] for ability in ABILITY_ORDER}

            continue

        if line.startswith("*") and current_champ and current_ability:
            champ_dict[current_champ][current_ability].append(line.lstrip("* ").strip())

    return champ_dict

def parse_aram_modifiers():
    path = DATA_DIR / "fandom_api" / "raw" / "aram_modifiers.wikitext"
    raw = path.read_text(encoding="utf-8")
    champions_text = extract_champions(raw)

    champions_text = flatten_templates(champions_text)
    champions_text = strip_bold_italics(champions_text)
    champions_text = re.sub(r"[ \t]+", " ", champions_text)
    champions_text = re.sub(r"\n{3,}", "\n\n", champions_text).strip()

    champ_dict = build_champion_dict(champions_text)

    return champ_dict

