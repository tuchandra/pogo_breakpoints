from math import floor, sqrt
from typing import Any

from pydantic import BaseModel, Field

from .constants import CP_MULTIPLIERS, GAMEMASTER, IVs, PokemonType, Stats
from .moves import (
    ChargedMove,
    FastMove,
    Moveset,
    get_charged_move_by_id,
    get_fast_move_by_id,
)


class PokemonSpecies(BaseModel):
    number: int
    id: str
    name: str
    types: frozenset[PokemonType]
    attack: float
    defense: float
    stamina: float
    fast_moves: frozenset[FastMove]
    charged_moves: frozenset[ChargedMove]
    is_shadow: bool = False

    class Config:
        frozen = True

    def __eq__(self, other: Any):
        if isinstance(other, PokemonSpecies):
            return all(getattr(self, x) == getattr(other, x) for x in self.__fields__)
        return super().__eq__(other)

    def cp(self, level: float, att_iv: int, def_iv: int, sta_iv: int):
        attack, defense, stamina = (
            self.attack + att_iv,
            self.defense + def_iv,
            self.stamina + sta_iv,
        )
        return 0.1 * (CP_MULTIPLIERS[level] ** 2) * attack * sqrt(defense * stamina)


class Pokemon(BaseModel):
    species: PokemonSpecies
    level: float = Field(ge=1, le=51, multiple_of=0.5)
    ivs: IVs = Field(ge=0, le=15)
    moveset: Moveset | None = None

    @property
    def attack_iv(self) -> int:
        return self.ivs[0]

    @property
    def defense_iv(self) -> int:
        return self.ivs[1]

    @property
    def stamina_iv(self) -> int:
        return self.ivs[2]

    @property
    def cpm(self) -> float:
        return CP_MULTIPLIERS[self.level]

    @property
    def attack_stat(self) -> float:
        return (self.species.attack + self.attack_iv) * self.cpm

    @property
    def defense_stat(self) -> float:
        return (self.species.defense + self.defense_iv) * self.cpm

    @property
    def stamina_stat(self) -> float:
        return (self.species.stamina + self.stamina_iv) * self.cpm

    @property
    def stats(self) -> Stats:
        return (self.attack_stat, self.defense_stat, self.stamina_stat)

    @property
    def stat_product(self) -> float:
        return self.attack_stat * self.defense_stat * int(self.stamina_stat)

    @property
    def cp(self) -> int:
        return max(
            10,
            floor(0.1 * sqrt(self.attack_stat * self.attack_stat * self.defense_stat * self.stamina_stat)),
        )

    class Config:
        frozen = True


def get_species(species_name: str, as_shadow: bool = False) -> PokemonSpecies:
    if not (maybe_mon := _POKEMON_LOOKUP.get(species_name)):
        raise ValueError(f"Species not found: {species_name}")

    if as_shadow:
        maybe_mon = PokemonSpecies(**(dict(maybe_mon) | {"is_shadow": True}))

    return maybe_mon


def get_species_by_id(species_id: str) -> PokemonSpecies:
    is_shadow = "_shadow" in species_id
    species_id = species_id.replace("_shadow", "")

    if not (maybe_mon := _POKEMON_ID_LOOKUP.get(species_id)):
        raise ValueError(f"Species not found: {species_id}")

    if is_shadow:
        maybe_mon = PokemonSpecies(**(dict(maybe_mon) | {"is_shadow": True}))

    return maybe_mon


def _load_pokemon_from_gamemaster(gamemaster: Any) -> list[PokemonSpecies]:
    all_pokemon = gamemaster["pokemon"]
    non_shadow_pokemon = [
        mon
        for mon in all_pokemon
        if ("shadow" not in mon["speciesId"]) and ("_xs" not in mon["speciesId"]) and ("_xl" not in mon["speciesId"])
    ]
    pokemon = [
        PokemonSpecies(
            number=pokemon["dex"],
            id=pokemon["speciesId"],
            name=pokemon["speciesName"],
            types=frozenset(PokemonType(t) for t in pokemon["types"] if t != "none"),
            attack=pokemon["baseStats"]["atk"],
            defense=pokemon["baseStats"]["def"],
            stamina=pokemon["baseStats"]["hp"],
            fast_moves=frozenset(get_fast_move_by_id(move) for move in pokemon["fastMoves"]),
            charged_moves=frozenset(get_charged_move_by_id(move) for move in pokemon["chargedMoves"]),
        )
        for pokemon in non_shadow_pokemon
    ]

    return pokemon


POKEMON = _load_pokemon_from_gamemaster(GAMEMASTER)
_POKEMON_LOOKUP = {pokemon.name: pokemon for pokemon in POKEMON}
_POKEMON_ID_LOOKUP = {pokemon.id: pokemon for pokemon in POKEMON}
