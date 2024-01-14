import json
from pathlib import Path

from pydantic import BaseModel

from .moves import Moveset, get_charged_move_by_id, get_fast_move_by_id
from .pokemon import PokemonSpecies, get_species_by_id


class League(BaseModel):
    name: str
    max_cp: int
    meta: list[tuple[PokemonSpecies, Moveset]]


def _get_meta_from_file(name: str) -> list[tuple[PokemonSpecies, Moveset]]:
    p = Path("data") / f"{name}.json"
    data = json.loads(p.read_text())

    meta_list: list[tuple[PokemonSpecies, Moveset]] = []
    for item in data:
        species = get_species_by_id(item["speciesId"])
        if item.get("shadowType") == "shadow":
            species = PokemonSpecies(**(dict(species) | {"is_shadow": True}))

        fast = get_fast_move_by_id(item["fastMove"])
        charged = [get_charged_move_by_id(move) for move in item["chargedMoves"]]
        meta_list.append((species, Moveset(fast=fast, charged=charged)))  # pyright: ignore[reportGeneralTypeIssues]

    return meta_list


GREAT_LEAGUE = League(name="Great League", max_cp=1500, meta=_get_meta_from_file("great"))
ULTRA_LEAGUE = League(name="Ultra League", max_cp=2500, meta=_get_meta_from_file("ultra"))
MASTER_LEAGUE = League(name="Master League", max_cp=10_000, meta=_get_meta_from_file("master"))
