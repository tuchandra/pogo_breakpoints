import json
from pathlib import Path
from typing import Any

import httpx


def get_gamemaster() -> dict[str, Any]:
    """
    Fetches the gamemaster from PVPoke's Github and returns it as a dict.
    Start with base.json, then merge in pokemon.json and moves.json; those are stored
    separately upstream (probably for clearer diffs?), but it's easier for us to keep
    it all together.
    """

    github = "https://raw.githubusercontent.com/pvpoke/pvpoke/master/src/data/gamemaster/"

    base: dict[str, Any] = httpx.get(github + "base.json").raise_for_status().json()
    base["pokemon"] = httpx.get(github + "pokemon.json").raise_for_status().json()
    base["moves"] = httpx.get(github + "moves.json").raise_for_status().json()

    return base


if __name__ == "__main__":
    Path("data/gamemaster.json").write_text(json.dumps(get_gamemaster(), indent=2))
