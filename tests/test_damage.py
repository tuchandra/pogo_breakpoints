from typing import TypedDict

import pytest

from pvp_damage.constants import PokemonType
from pvp_damage.damage import calculate_damage, is_stab
from pvp_damage.moves import ChargedMove, FastMove, Move, get_fast_move
from pvp_damage.pokemon import Pokemon, PokemonSpecies, get_species


@pytest.fixture
def mock_moves() -> dict[str, Move]:
    _fast_move_type = TypedDict(
        "_fast_move_type", {"move_id": str, "power": int, "energy": int, "turns": int}
    )
    default_fast: _fast_move_type = {"move_id": "any", "power": 4, "energy": 4, "turns": 4}

    _charged_move_type = TypedDict(
        "_charged_move_type", {"move_id": str, "power": int, "energy": int}
    )
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
        "Dynamic Punch": ChargedMove(
            name="Dynamic Punch", type=PokemonType.fighting, **default_charged
        ),
        "Shadow Ball": ChargedMove(name="Shadow Ball", type=PokemonType.ghost, **default_charged),
        "Shadow Punch": ChargedMove(name="Shadow Punch", type=PokemonType.ghost, **default_charged),
        "Flame Wheel": ChargedMove(name="Flame Wheel", type=PokemonType.fire, **default_charged),
        "Flame Charge": ChargedMove(name="Flame Charge", type=PokemonType.fire, **default_charged),
        "Thunder": ChargedMove(name="Thunder", type=PokemonType.electric, **default_charged),
        "Thunder Punch": ChargedMove(
            name="Thunder Punch", type=PokemonType.electric, **default_charged
        ),
        "Ice Punch": ChargedMove(name="Ice Punch", type=PokemonType.ice, **default_charged),
        "Dragon Claw": ChargedMove(name="Dragon Claw", type=PokemonType.dragon, **default_charged),
        "Iron Head": ChargedMove(name="Iron Head", type=PokemonType.steel, **default_charged),
    }


@pytest.fixture
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
    ["move_name", "pokemon_name", "expected"],
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
