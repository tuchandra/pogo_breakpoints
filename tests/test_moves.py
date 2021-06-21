import pytest

from pvp_damage.constants import Effectiveness, PokemonType
from pvp_damage.moves import (
    get_charged_move,
    get_charged_move_by_id,
    get_fast_move,
    get_fast_move_by_id,
    get_move_effectiveness,
    get_type_effectiveness,
)


@pytest.mark.parametrize(
    ["name", "energy", "power", "turns"],
    [
        ("Incinerate", 20, 15, 5),
        ("Vine Whip", 8, 5, 2),
        ("Volt Switch", 16, 12, 4),
        ("Water Gun", 3, 3, 1),
        ("Transform", 0, 0, 3),
        ("Lock On", 5, 1, 1),
        ("Lick", 3, 3, 1),
        ("Fury Cutter", 4, 2, 1),
        ("Counter", 7, 8, 2),
        ("Shadow Claw", 8, 6, 2),
    ],
)
def test_get_fast_move(name: str, energy: int, power: int, turns: int):
    move = get_fast_move(name)
    assert move.energy == energy
    assert move.power == power
    assert move.turns == turns


@pytest.mark.parametrize(
    ["name", "energy", "power"],
    [
        ("Shadow Sneak", 45, 50),
        ("Skull Bash", 75, 130),
        ("Stone Edge", 55, 100),
        ("Superpower", 40, 85),
        ("Surf", 40, 65),
        ("Tri Attack", 50, 65),
        ("Twister", 45, 45),
        ("Water Pulse", 60, 70),
        ("Sludge Wave", 65, 110),
        ("Leaf Blade", 35, 70),
        ("Iron Head", 50, 70),
        ("Ice Punch", 40, 55),
        ("Hydro Cannon", 40, 80),
        ("Frenzy Plant", 45, 100),
        ("Wild Charge", 45, 100),
        ("Focus Blast", 75, 150),
    ],
)
def test_get_charged_move(name: str, energy: int, power: int):
    move = get_charged_move(name)
    assert move.energy == energy
    assert move.power == power


@pytest.mark.parametrize(
    ["move_id", "energy", "power", "turns"],
    [
        ("INCINERATE", 20, 15, 5),
        ("VINE_WHIP", 8, 5, 2),
        ("VOLT_SWITCH", 16, 12, 4),
        ("WATER_GUN", 3, 3, 1),
        ("TRANSFORM", 0, 0, 3),
        ("LOCK_ON", 5, 1, 1),
        ("LICK", 3, 3, 1),
        ("FURY_CUTTER", 4, 2, 1),
        ("COUNTER", 7, 8, 2),
        ("SHADOW_CLAW", 8, 6, 2),
    ],
)
def test_get_fast_move_by_id(move_id: str, energy: int, power: int, turns: int):
    move = get_fast_move_by_id(move_id)
    assert move.energy == energy
    assert move.power == power
    assert move.turns == turns


@pytest.mark.parametrize(
    ["move_id", "energy", "power"],
    [
        ("SHADOW_SNEAK", 45, 50),
        ("SKULL_BASH", 75, 130),
        ("STONE_EDGE", 55, 100),
        ("SUPER_POWER", 40, 85),
        ("SURF", 40, 65),
        ("TRI_ATTACK", 50, 65),
        ("TWISTER", 45, 45),
        ("WATER_PULSE", 60, 70),
        ("SLUDGE_WAVE", 65, 110),
        ("LEAF_BLADE", 35, 70),
        ("IRON_HEAD", 50, 70),
        ("ICE_PUNCH", 40, 55),
        ("HYDRO_CANNON", 40, 80),
        ("FRENZY_PLANT", 45, 100),
        ("WILD_CHARGE", 45, 100),
        ("FOCUS_BLAST", 75, 150),
    ],
)
def test_get_charged_move_by_id(move_id: str, energy: int, power: int):
    move = get_charged_move_by_id(move_id)
    assert move.energy == energy
    assert move.power == power


@pytest.mark.parametrize(
    ["attacker", "defender", "output"],
    [
        (PokemonType.normal, PokemonType.ghost, Effectiveness.immune),
        (PokemonType.normal, PokemonType.rock, Effectiveness.not_very_effective),
        (PokemonType.normal, PokemonType.steel, Effectiveness.not_very_effective),
        (PokemonType.normal, PokemonType.fighting, Effectiveness.default),
        (PokemonType.normal, PokemonType.grass, Effectiveness.default),
        (PokemonType.normal, PokemonType.electric, Effectiveness.default),
        (PokemonType.normal, PokemonType.normal, Effectiveness.default),
        (PokemonType.normal, PokemonType.fire, Effectiveness.default),
        (PokemonType.normal, PokemonType.dark, Effectiveness.default),
        (PokemonType.normal, PokemonType.bug, Effectiveness.default),
        (PokemonType.grass, PokemonType.rock, Effectiveness.super_effective),
        (PokemonType.grass, PokemonType.water, Effectiveness.super_effective),
        (PokemonType.grass, PokemonType.ground, Effectiveness.super_effective),
        (PokemonType.grass, PokemonType.flying, Effectiveness.not_very_effective),
        (PokemonType.grass, PokemonType.bug, Effectiveness.not_very_effective),
        (PokemonType.grass, PokemonType.grass, Effectiveness.not_very_effective),
        (PokemonType.fire, PokemonType.water, Effectiveness.not_very_effective),
        (PokemonType.fire, PokemonType.rock, Effectiveness.not_very_effective),
        (PokemonType.fire, PokemonType.steel, Effectiveness.super_effective),
        (PokemonType.fire, PokemonType.grass, Effectiveness.super_effective),
        (PokemonType.electric, PokemonType.bug, Effectiveness.default),
        (PokemonType.electric, PokemonType.dark, Effectiveness.default),
        (PokemonType.electric, PokemonType.ghost, Effectiveness.default),
        (PokemonType.electric, PokemonType.fighting, Effectiveness.default),
        (PokemonType.electric, PokemonType.electric, Effectiveness.not_very_effective),
        (PokemonType.electric, PokemonType.grass, Effectiveness.not_very_effective),
        (PokemonType.electric, PokemonType.water, Effectiveness.super_effective),
        (PokemonType.electric, PokemonType.flying, Effectiveness.super_effective),
        (PokemonType.electric, PokemonType.ground, Effectiveness.immune),
        (PokemonType.dragon, PokemonType.fairy, Effectiveness.immune),
        (PokemonType.dragon, PokemonType.dragon, Effectiveness.super_effective),
        (PokemonType.dragon, PokemonType.normal, Effectiveness.default),
        (PokemonType.dragon, PokemonType.ghost, Effectiveness.default),
    ],
)
def test_type_effectiveness(attacker: PokemonType, defender: PokemonType, output: Effectiveness):
    assert get_type_effectiveness(attacker, defender) == output


@pytest.mark.parametrize(
    ["attacker", "defender", "output"],
    [
        (PokemonType.electric, {PokemonType.dragon, PokemonType.ground}, 0.625 ** 3),
        (PokemonType.electric, {PokemonType.ground, PokemonType.grass}, 0.625 ** 3),
        (PokemonType.water, {PokemonType.ground, PokemonType.grass}, 1),
        (PokemonType.water, {PokemonType.ice, PokemonType.grass}, 0.625),
        (PokemonType.dragon, {PokemonType.fairy, PokemonType.normal}, 0.625 ** 2),
        (PokemonType.dark, {PokemonType.ghost, PokemonType.dark}, 1),
        (PokemonType.dark, {PokemonType.ghost}, 1.6),
    ],
)
def test_move_effectiveness(attacker: PokemonType, defender: set[PokemonType], output: float):
    assert get_move_effectiveness(attacker, defender) == output
