from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .constants import GAMEMASTER, TYPE_MATCHUPS, Effectiveness, PokemonType


class FastMove(BaseModel):
    move_id: str
    name: str
    type: PokemonType
    power: int = Field(ge=0, le=20)
    energy: int = Field(ge=0, le=20)
    turns: int = Field(ge=1, le=5)
    model_config = ConfigDict(frozen=True)

    def __repr__(self) -> str:
        return f"{self.name} ({self.type.value}; {self.power} power, {self.energy} energy, {self.turns} turns)"


class ChargedMove(BaseModel):
    move_id: str
    name: str
    type: PokemonType
    power: int
    energy: int
    model_config = ConfigDict(frozen=True)

    def __repr__(self) -> str:
        return f"{self.name} ({self.type.value}; {self.power} power, {self.energy} energy)"


type Move = FastMove | ChargedMove


class Moveset(BaseModel):
    fast: FastMove
    charged: tuple[ChargedMove, ChargedMove | None]


def get_fast_move(move_name: str) -> FastMove:
    if not (maybe_move := _FAST_NAME_LOOKUP.get(move_name)):
        raise ValueError(f"Problem getting fast move: {move_name}")

    return maybe_move


def get_charged_move(move_name: str) -> ChargedMove:
    if not (maybe_move := _CHARGED_NAME_LOOKUP.get(move_name)):
        raise ValueError(f"Problem getting charged move: {move_name}")

    return maybe_move


def get_move_by_name(move_name: str) -> Move:
    maybe_fast = _FAST_NAME_LOOKUP.get(move_name)
    maybe_charged = _CHARGED_NAME_LOOKUP.get(move_name)

    if maybe_fast and maybe_charged:
        raise ValueError(f"Somehow got two moves?! {maybe_fast}, {maybe_charged}")

    if maybe_fast:
        return maybe_fast

    if maybe_charged:
        return maybe_charged

    raise ValueError(f"Problem getting move: {move_name}")


def get_fast_move_by_id(move_id: str) -> FastMove:
    if not (maybe_move := _FAST_ID_LOOKUP.get(move_id)):
        raise ValueError(f"Problem getting fast move: {move_id}")

    return maybe_move


def get_charged_move_by_id(move_id: str) -> ChargedMove:
    if not (maybe_move := _CHARGED_ID_LOOKUP.get(move_id)):
        raise ValueError(f"Problem getting charged move: {move_id}")

    return maybe_move


def get_type_effectiveness(attack: PokemonType, defense: PokemonType) -> Effectiveness:
    """
    Get the effectiveness of one type on another (single) type.
    """

    if defense in TYPE_MATCHUPS[attack].super_effective_on:
        return Effectiveness.super_effective
    if defense in TYPE_MATCHUPS[attack].resisted_by:
        return Effectiveness.not_very_effective
    if defense in TYPE_MATCHUPS[attack].double_resisted_by:
        return Effectiveness.immune

    return Effectiveness.default


def get_move_effectiveness(attack: PokemonType, defender: Iterable[PokemonType]) -> float:
    """
    Get the effectiveness of an attack type on a defender (which can have two types).
    e.g,. Electric is triple-resisted by Ground/Dragon.
    """

    multiplier = 1
    for defense_type in defender:
        effectiveness = get_type_effectiveness(attack, defense_type)
        multiplier *= effectiveness.value

    return multiplier


def _load_moves_from_gamemaster(gamemaster: Any) -> tuple[list[FastMove], list[ChargedMove]]:
    """
    Fast moves and charged moves are represented with the same structure, except
    fast moves have energyGain > 0 and energy = 0, and charged moves have the
    opposite. ('energy' is an energy cost to use the move.)
    """
    all_moves = gamemaster["moves"]
    fast_moves = [
        FastMove(
            move_id=move["moveId"],
            name=move["name"],
            type=PokemonType(move["type"]),
            power=move["power"],
            energy=move["energyGain"],
            turns=int(move["cooldown"]) // 500,
        )
        for move in all_moves
        if (move["energyGain"] or move["moveId"] == "TRANSFORM")
    ]
    fast_moves.append(
        # Some GM entires have Struggle as a placeholder for Pokemon without fast move data.
        # Struggle is actually a charged move, which is inconvenient ... so toss a placeholder here.
        FastMove(
            move_id="STRUGGLE",
            name="Struggle",
            type=PokemonType("normal"),
            power=0,
            energy=0,
            turns=1,
        )
    )
    charged_moves = [
        ChargedMove(
            move_id=move["moveId"],
            name=move["name"],
            type=PokemonType(move["type"]),
            power=move["power"],
            energy=move["energy"],
        )
        for move in all_moves
        if move["energy"]
    ]

    return fast_moves, charged_moves


FAST_MOVES, CHARGED_MOVES = _load_moves_from_gamemaster(GAMEMASTER)
_FAST_NAME_LOOKUP = {move.name: move for move in FAST_MOVES}
_FAST_ID_LOOKUP = {move.move_id: move for move in FAST_MOVES}
_CHARGED_NAME_LOOKUP = {move.name: move for move in CHARGED_MOVES}
_CHARGED_ID_LOOKUP = {move.move_id: move for move in CHARGED_MOVES}
