from typing import TypedDict

import pytest

from pvp_damage.damage import (
    calculate_damage,
    compute_attacker_damage,
    compute_iv_possibilities,
    find_max_level_for_league,
    is_stab,
)
from pvp_damage.models.constants import IVs, PokemonType
from pvp_damage.models.moves import ChargedMove, FastMove, Move, get_fast_move, get_move_by_name
from pvp_damage.models.pokemon import Pokemon, PokemonSpecies, get_species


@pytest.fixture()
def mock_moves() -> dict[str, Move]:
    _fast_move_type = TypedDict("_fast_move_type", {"move_id": str, "power": int, "energy": int, "turns": int})  # noqa: UP013
    default_fast: _fast_move_type = {"move_id": "any", "power": 4, "energy": 4, "turns": 4}

    _charged_move_type = TypedDict("_charged_move_type", {"move_id": str, "power": int, "energy": int})  # noqa: UP013
    default_charged: _charged_move_type = {"move_id": "any", "power": 4, "energy": 4}

    return {
        # fast
        "Counter": FastMove(name="Counter", type=PokemonType.fighting, **default_fast),
        "Shadow Claw": FastMove(name="Shadow Claw", type=PokemonType.ghost, **default_fast),
        "Incinerate": FastMove(name="Incinerate", type=PokemonType.fire, **default_fast),
        "Spark": FastMove(name="Spark", type=PokemonType.electric, **default_fast),
        "Ice Shard": FastMove(name="Ice Shard", type=PokemonType.ice, **default_fast),
        "Dragonbreath": FastMove(name="Dragonbreath", type=PokemonType.dragon, **default_fast),
        "Metal Claw": FastMove(name="Metal Claw", type=PokemonType.steel, **default_fast),
        # charged moves
        "Dynamic Punch": ChargedMove(name="Dynamic Punch", type=PokemonType.fighting, **default_charged),
        "Shadow Ball": ChargedMove(name="Shadow Ball", type=PokemonType.ghost, **default_charged),
        "Shadow Punch": ChargedMove(name="Shadow Punch", type=PokemonType.ghost, **default_charged),
        "Flame Wheel": ChargedMove(name="Flame Wheel", type=PokemonType.fire, **default_charged),
        "Flame Charge": ChargedMove(name="Flame Charge", type=PokemonType.fire, **default_charged),
        "Thunder": ChargedMove(name="Thunder", type=PokemonType.electric, **default_charged),
        "Thunder Punch": ChargedMove(name="Thunder Punch", type=PokemonType.electric, **default_charged),
        "Ice Punch": ChargedMove(name="Ice Punch", type=PokemonType.ice, **default_charged),
        "Dragon Claw": ChargedMove(name="Dragon Claw", type=PokemonType.dragon, **default_charged),
        "Iron Head": ChargedMove(name="Iron Head", type=PokemonType.steel, **default_charged),
    }


@pytest.fixture()
def mock_species() -> dict[str, PokemonSpecies]:
    def make_species(name: str, types: set[str]) -> PokemonSpecies:
        return PokemonSpecies(
            id="",
            name=name,
            types={PokemonType(t) for t in types},
            number=12,
            attack=0,
            defense=0,
            stamina=0,
            fast_moves=set(),
            charged_moves=set(),
        )

    return {
        "Machamp": make_species("Machamp", {"fighting"}),
        "Haunter": make_species("Haunter", {"ghost", "poison"}),
        "Giratina (Altered)": make_species("Giratina (Altered)", {"ghost", "dragon"}),
        "Eevee": make_species("Eevee", {"normal"}),
        "Blaziken": make_species("Blaziken", {"fire", "fighting"}),
        "Spheal": make_species("Spheal", {"water", "ice"}),
        "Swampert": make_species("Swampert", {"water", "ground"}),
        "Muk (Alolan)": make_species("Muk (Alolan)", {"dark", "poison"}),
        "Stunfisk (Galarian)": make_species("Stunfisk (Galarian)", {"ground", "steel"}),
        "Stunfisk": make_species("Stunfisk", {"ground", "electric"}),
        "Cherrim (Sunshine)": make_species("Cherrim (Sunshine)", {"grass"}),
    }


@pytest.mark.parametrize(
    ("move_name", "pokemon_name", "expected"),
    [
        # charged moves
        ("Dynamic Punch", "Machamp", True),
        ("Shadow Ball", "Machamp", False),
        ("Shadow Ball", "Giratina (Altered)", True),
        ("Shadow Ball", "Spheal", False),
        ("Flame Charge", "Blaziken", True),
        ("Dynamic Punch", "Blaziken", True),
        ("Iron Head", "Swampert", False),
        ("Ice Punch", "Swampert", False),
        # fast moves
        ("Metal Claw", "Swampert", False),
        ("Metal Claw", "Stunfisk (Galarian)", True),
        ("Metal Claw", "Stunfisk", False),
        ("Incinerate", "Stunfisk", False),
        ("Incinerate", "Blaziken", True),
        ("Spark", "Blaziken", False),
        ("Spark", "Stunfisk", True),
    ],
)
def test_is_stab(
    mock_moves: dict[str, Move],
    mock_species: dict[str, PokemonSpecies],
    move_name: str,
    pokemon_name: str,
    expected: bool,
):
    move = mock_moves[move_name]
    species = mock_species[pokemon_name]
    assert is_stab(move, species) == expected


def test_dialga_mirror_breakpoint():
    # Dialga breakpoints are the most famous in all of PVP.
    # Level 41 hundo Dialga will do 5 damage against each other in the mirror.
    dialga_41_hundo = Pokemon(species=get_species("Dialga"), level=41, ivs=(15, 15, 15))
    assert calculate_damage(get_fast_move("Dragon Breath"), dialga_41_hundo, dialga_41_hundo) == 5

    # Level 40 14atk dialga fails to reach a breakpoint in the mirror
    dialga_14atk = Pokemon(species=get_species("Dialga"), level=40, ivs=(14, 15, 15))
    dialga_hundo = Pokemon(species=get_species("Dialga"), level=40, ivs=(15, 15, 15))
    assert calculate_damage(get_fast_move("Dragon Breath"), dialga_14atk, dialga_hundo) == 4
    assert calculate_damage(get_fast_move("Dragon Breath"), dialga_hundo, dialga_hundo) == 5

    # Level 41 hundo dialga reaches a bulkpoint against level 40 hundo
    assert calculate_damage(get_fast_move("Dragon Breath"), dialga_hundo, dialga_41_hundo) == 4


def test_garchomp_gunfisk_breakpoint():
    # the 8/0/1 garchomp should reach 5 mud shot damage against Galarian Stunfisk
    # https://pbs.twimg.com/media/E25ahuTWYAUfj5q?format=jpg&name=4096x4096
    garchomp_attack = Pokemon(species=get_species("Garchomp"), level=14.5, ivs=(8, 0, 1))
    garchomp_high_rank = Pokemon(species=get_species("Garchomp"), level=14, ivs=(0, 15, 15))
    gunfisk = Pokemon(species=get_species("Stunfisk (Galarian)"), level=26.5, ivs=(4, 15, 6))

    # these are auxilliary tests but good to make sure
    assert garchomp_attack.cp <= 1500
    assert garchomp_high_rank.cp <= 1500
    assert gunfisk.cp <= 1500

    assert calculate_damage(get_fast_move("Mud Shot"), garchomp_attack, gunfisk) == 5
    assert calculate_damage(get_fast_move("Mud Shot"), garchomp_high_rank, gunfisk) == 4


def test_garchomp_umbreon_breakpoint():
    # the 2/11/13 garchomp should reach 9 dragon tail damage against UL umbreon
    # https://pbs.twimg.com/media/E25ahuTWYAUfj5q?format=jpg&name=4096x4096
    garchomp_attack = Pokemon(species=get_species("Garchomp"), level=23.5, ivs=(2, 11, 13))
    garchomp_high_rank = Pokemon(species=get_species("Garchomp"), level=23.5, ivs=(0, 14, 13))
    umbreon = Pokemon(species=get_species("Umbreon"), level=51, ivs=(15, 15, 15))

    # these are auxilliary tests but good to make sure
    assert garchomp_attack.cp <= 2500
    assert garchomp_high_rank.cp <= 2500
    assert umbreon.cp <= 2500

    assert calculate_damage(get_fast_move("Dragon Tail"), garchomp_attack, umbreon) == 9
    assert calculate_damage(get_fast_move("Dragon Tail"), garchomp_high_rank, umbreon) == 8


def test_gallade_garchomp_breakpoint():
    # the 0/15/1 garchomp should reduce damage from gallade's confusion
    # https://pbs.twimg.com/media/E25ahuTWYAUfj5q?format=jpg&name=4096x4096
    garchomp_defense = Pokemon(species=get_species("Garchomp"), level=24, ivs=(0, 15, 1))
    garchomp_high_rank = Pokemon(species=get_species("Garchomp"), level=23.5, ivs=(0, 14, 13))
    gallade = Pokemon(species=get_species("Gallade"), level=30.5, ivs=(0, 12, 15))

    # these are auxilliary tests but good to make sure
    assert garchomp_defense.cp <= 2500
    assert garchomp_high_rank.cp <= 2500
    assert gallade.cp <= 2500

    assert calculate_damage(get_fast_move("Confusion"), gallade, garchomp_defense) == 16
    assert calculate_damage(get_fast_move("Confusion"), gallade, garchomp_high_rank) == 17


def test_altaria_breakpoints():
    # the 8/6/2 altaria reaches 4 damage against Whiscash, 3 vs. cress, 5 vs. Kingdra
    # https://pbs.twimg.com/media/E1R8U7RUYAcB1Or?format=jpg&name=4096x4096
    altaria_attack = Pokemon(species=get_species("Altaria"), level=29, ivs=(8, 6, 2))
    altaria_rk1 = Pokemon(species=get_species("Altaria"), level=29, ivs=(0, 14, 15))
    whiscash = Pokemon(species=get_species("Whiscash"), level=28, ivs=(0, 14, 13))
    cresselia = Pokemon(species=get_species("Cresselia"), level=20, ivs=(2, 15, 13))
    kingdra = Pokemon(species=get_species("Kingdra"), level=21.5, ivs=(0, 15, 13))

    assert calculate_damage(get_fast_move("Dragon Breath"), altaria_attack, whiscash) == 4
    assert calculate_damage(get_fast_move("Dragon Breath"), altaria_rk1, whiscash) == 3

    assert calculate_damage(get_fast_move("Dragon Breath"), altaria_attack, cresselia) == 3
    assert calculate_damage(get_fast_move("Dragon Breath"), altaria_rk1, cresselia) == 2

    assert calculate_damage(get_fast_move("Dragon Breath"), altaria_attack, kingdra) == 5
    assert calculate_damage(get_fast_move("Dragon Breath"), altaria_rk1, kingdra) == 4


def test_more_altaria_breakpoints():
    # the 9/1/8 altaria reaches 5 damage against Swampert, 2 against non-XL azu
    # https://pbs.twimg.com/media/E1R8U7RUYAcB1Or?format=jpg&name=4096x4096
    altaria_attack = Pokemon(species=get_species("Altaria"), level=29, ivs=(9, 1, 8))
    altaria_rk1 = Pokemon(species=get_species("Altaria"), level=29, ivs=(0, 14, 15))
    swampert = Pokemon(species=get_species("Swampert"), level=19, ivs=(0, 14, 14))
    azumarill = Pokemon(species=get_species("Azumarill"), level=39.5, ivs=(9, 15, 14))

    assert calculate_damage(get_fast_move("Dragon Breath"), altaria_attack, swampert) == 4
    assert calculate_damage(get_fast_move("Dragon Breath"), altaria_rk1, swampert) == 3

    assert calculate_damage(get_fast_move("Dragon Breath"), altaria_attack, azumarill) == 2
    assert calculate_damage(get_fast_move("Dragon Breath"), altaria_rk1, azumarill) == 1


def test_serperior_great_breakpoints():
    # 1/14/1 serperior lowers venusaur's vine whip from 3 to 2
    # also does 6 damage against XL azu and high rank Dewgong
    # https://pbs.twimg.com/media/Eyi6zCmU8AAtjpC?format=jpg&name=4096x4096
    serperior_defense = Pokemon(species=get_species("Serperior"), level=29, ivs=(1, 14, 1))
    serperior_rk1 = Pokemon(species=get_species("Serperior"), level=25.5, ivs=(0, 10, 15))
    venusaur = Pokemon(species=get_species("Venusaur"), level=21, ivs=(0, 14, 11))

    assert calculate_damage(get_fast_move("Vine Whip"), venusaur, serperior_defense) == 2
    assert calculate_damage(get_fast_move("Vine Whip"), venusaur, serperior_rk1) == 3

    azumarill = Pokemon(species=get_species("Azumarill"), level=46, ivs=(0, 15, 12))
    assert calculate_damage(get_fast_move("Vine Whip"), serperior_defense, azumarill) == 6
    assert calculate_damage(get_fast_move("Vine Whip"), serperior_rk1, azumarill) == 5

    dewgong = Pokemon(species=get_species("Dewgong"), level=29.5, ivs=(0, 12, 15))
    assert calculate_damage(get_fast_move("Vine Whip"), serperior_defense, dewgong) == 6
    assert calculate_damage(get_fast_move("Vine Whip"), serperior_rk1, dewgong) == 5


def test_serperior_ultra_breakpoints():
    # hundo UL serperior does more damage against lapras
    # https://pbs.twimg.com/media/Eyi6zCmU8AAtjpC?format=jpg&name=4096x4096
    serperior_hundo = Pokemon(species=get_species("Serperior"), level=47.5, ivs=(15, 15, 15))
    serperior_rk1 = Pokemon(species=get_species("Serperior"), level=50, ivs=(10, 14, 15))
    lapras = Pokemon(species=get_species("Lapras"), level=43, ivs=(0, 13, 15))

    assert calculate_damage(get_fast_move("Vine Whip"), serperior_hundo, lapras) == 7
    assert calculate_damage(get_fast_move("Vine Whip"), serperior_rk1, lapras) == 6


@pytest.mark.parametrize(
    ("species_name", "cp_limit", "level"),
    [
        # great league
        ("Abomasnow", 1500, 22),
        ("Stunfisk", 1500, 24),
        ("Umbreon", 1500, 24.5),
        ("Azumarill", 1500, 36),
        ("Venusaur", 1500, 19),
        ("Pelipper", 1500, 24.5),
        ("Raichu (Alolan)", 1500, 22.5),
        ("Galvantula", 1500, 23.5),
        # ultra league
        ("Gallade", 2500, 28),
        ("Venusaur", 2500, 34),
        ("Empoleon", 2500, 30),
        ("Machamp", 2500, 28.5),
        ("Abomasnow", 2500, 44.5),
        ("Talonflame", 2500, 50),
        ("Stunfisk (Galarian)", 2500, 51),
        # silly tests for master league
        ("Abomasnow", 10000, 51),
        ("Dialga", 10000, 51),
        ("Mewtwo", 10000, 51),
        ("Eevee", 10000, 51),
        ("Unfezant", 10000, 51),
    ],
)
def test_find_hundos_for_league(species_name: str, cp_limit: int, level: float):
    """
    Tests for find_max_level_for_league, but using hundos only - since those are
    easiest to parameterize and compute.
    """

    species = get_species(species_name)
    ivs = (15, 15, 15)
    mon = find_max_level_for_league(species, ivs, cp_limit)

    # test that the mon is the right level & within the CP limit
    assert mon.level == level
    assert mon.cp <= cp_limit

    # test that this is _maximal_ CP (that the next level exceeds the limit)
    if level < 51:
        half_level_higher = Pokemon(species=species, level=level + 0.5, ivs=(15, 15, 15))
        assert half_level_higher.cp > cp_limit


@pytest.mark.parametrize(
    ("species_name", "ivs", "level", "cp"),
    [
        ("Charizard", (0, 13, 15), 35, 2500),
        ("Roserade", (4, 15, 15), 31.5, 2499),
        ("Machamp", (1, 13, 15), 31, 2499),
        ("Swampert", (13, 10, 12), 30.5, 2498),
        ("Roserade", (10, 13, 14), 30.5, 2498),
        ("Sirfetch'd", (6, 9, 10), 32.5, 2497),
        ("Venusaur", (15, 13, 15), 34.5, 2494),
        ("Nidoqueen", (8, 14, 14), 43.5, 2493),
        ("Golem (Alolan)", (11, 6, 15), 31.5, 2491),
        ("Gengar", (0, 15, 15), 34, 2488),
        ("Gyarados", (3, 15, 14), 27, 2486),
        ("Crustle", (11, 15, 14), 40, 2485),
        ("Empoleon", (3, 14, 5), 35, 2483),
        ("Gallade", (6, 14, 11), 29.5, 2481),
    ],
)
def test_find_max_level_ultra(species_name: str, ivs: IVs, level: float, cp: int):
    """
    Tests for find_max_level_for_league, using Pokemon out of my UL collection in PoGo.
    """

    species = get_species(species_name)
    cp_limit = 2500
    mon = find_max_level_for_league(species, ivs, cp_limit)

    # test that the mon is the right level & CP
    assert mon.level == level
    assert mon.cp == cp

    # test that this is _maximal_ CP (that the next level exceeds the limit)
    half_level_higher = Pokemon(species=species, level=level + 0.5, ivs=(15, 15, 15))
    assert half_level_higher.cp > cp_limit


@pytest.mark.parametrize(
    ("species_name", "ivs", "level", "cp"),
    [
        ("Ninetales", (5, 11, 9), 25, 1500),
        ("Machamp", (2, 8, 15), 18.5, 1500),
        ("Skarmory", (10, 12, 13), 26, 1500),
        ("Talonflame", (1, 15, 10), 26, 1499),
        ("Gengar", (1, 12, 13), 19.5, 1499),
        ("Drifblim", (3, 11, 12), 24, 1499),
        ("Victreebel", (5, 12, 12), 23, 1499),
        ("Perrserker", (15, 8, 14), 22.5, 1499),
        ("Azumarill", (10, 14, 15), 39, 1499),
        ("Jellicent", (5, 5, 14), 24.5, 1499),
        ("Pelipper", (10, 12, 9), 26, 1499),
        ("Roserade", (4, 15, 14), 18.5, 1499),
        ("Cradily", (0, 15, 8), 26.5, 1498),
    ],
)
def test_find_max_level_great(species_name: str, ivs: IVs, level: float, cp: int):
    """
    Tests for find_max_level_for_league, using Pokemon out of my GL collection in PoGo.
    """

    species = get_species(species_name)
    cp_limit = 1500
    mon = find_max_level_for_league(species, ivs, cp_limit)

    # test that the mon is the right level & CP
    assert mon.level == level
    assert mon.cp == cp

    # test that this is _maximal_ CP (that the next level exceeds the limit)
    half_level_higher = Pokemon(species=species, level=level + 0.5, ivs=(15, 15, 15))
    assert half_level_higher.cp > cp_limit


def test_compute_iv_possibilities_azu():
    """
    Tests for compute_iv_possibilities, using Great League Azumarill of different IVs.
    We don't parameterize this test because it's (much) faster to call
    compute_iv_possibilities once.
    """

    ivs_and_levels = [
        ((15, 15, 15), 36),
        ((15, 15, 14), 36),
        ((15, 12, 11), 37),
        ((9, 15, 14), 39.5),
        ((10, 15, 10), 39.5),
        ((8, 15, 15), 40),  # nasty edge case
        ((8, 14, 14), 40),
        ((8, 14, 13), 40.5),
        ((6, 14, 14), 41.5),
        ((2, 12, 15), 44.5),
        ((0, 15, 15), 45.5),
        ((2, 8, 8), 47),
        ((1, 8, 8), 47.5),
        ((0, 8, 8), 48.5),
        ((0, 4, 4), 50),
        ((0, 0, 0), 51),
    ]

    azu = get_species("Azumarill")
    all_ivs = compute_iv_possibilities(azu, 1500)

    assert len(all_ivs) == 16**3

    for ivs, level in ivs_and_levels:
        mon = all_ivs[ivs]
        assert mon.level == level

        # test that this is _maximal_ CP (that the next level exceeds the limit)
        if level < 51:
            half_level_higher = Pokemon(species=azu, level=level + 0.5, ivs=ivs)
            assert half_level_higher.cp > 1500


def test_compute_iv_possibilities_alt():
    """
    Tests for compute_iv_possibilities, using Great League Altaria of different IVs.
    """

    ivs_and_levels = [
        ((0, 15, 15), 28.5),
        ((0, 14, 15), 29),
        ((0, 15, 8), 29.5),
        ((0, 7, 15), 29.5),
        ((0, 7, 9), 30),
        ((0, 7, 5), 30.5),
        ((1, 3, 3), 31),
        ((1, 1, 1), 31.5),
        ((0, 0, 0), 32.5),
    ]

    alt = get_species("Altaria")
    all_ivs = compute_iv_possibilities(alt, 1500)

    assert len(all_ivs) == 16**3

    for ivs, level in ivs_and_levels:
        mon = all_ivs[ivs]
        assert mon.level == level

        # test that this is _maximal_ CP (that the next level exceeds the limit)
        if level < 51:
            half_level_higher = Pokemon(species=alt, level=level + 0.5, ivs=ivs)
            assert half_level_higher.cp > 1500


def test_compute_attacker_damage():
    """Not really sure how to test this ..."""

    serp = get_species("Serperior")
    my_serp = Pokemon(species=serp, level=50, ivs=(15, 15, 15))

    swamp = get_species("Swampert")
    compute_attacker_damage(my_serp, swamp, get_move_by_name("Vine Whip"), 2500)
