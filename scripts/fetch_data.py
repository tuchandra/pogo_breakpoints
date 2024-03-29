import json
from pathlib import Path
from typing import Any, Literal

import httpx


def get_gamemaster() -> dict[str, Any]:
    """
    Fetches the gamemaster from PVPoke's Github and returns it as a dict.

    Start with base.json, then merge in pokemon.json and moves.json; those are stored
    separately upstream (probably for clearer diffs?), but it's easier for us to keep
    it all together.

    Run this script to update gamemaster.json when new Pokemon are released, moves are
    updated, or the season shifts.
    """

    github = "https://raw.githubusercontent.com/pvpoke/pvpoke/master/src/data/gamemaster/"

    base: dict[str, Any] = httpx.get(github + "base.json").raise_for_status().json()
    base["pokemon"] = httpx.get(github + "pokemon.json").raise_for_status().json()
    base["moves"] = httpx.get(github + "moves.json").raise_for_status().json()

    return base


def get_leagues(league: Literal["great", "ultra", "master"]) -> dict[str, Any]:
    """Fetch data for Great / Ultra / Master league."""

    github = "https://raw.githubusercontent.com/pvpoke/pvpoke/master/src/data/groups/"

    return httpx.get(github + f"{league}.json").raise_for_status().json()


if __name__ == "__main__":
    Path("data/gamemaster.json").write_text(json.dumps(get_gamemaster(), indent=2))

    for league in ("great", "ultra", "master"):
        Path(f"data/{league}.json").write_text(json.dumps(get_leagues(league), indent=2))
