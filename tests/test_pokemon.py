from math import floor

import pytest

from pvp_damage.models.constants import PokemonType, IVs, Stats
from pvp_damage.models.pokemon import Pokemon, get_species, get_species_by_id


@pytest.mark.parametrize(
    ["name", "types", "one_fast_move", "one_charged_move"],
    [
        ("Stunfisk (Galarian)", {"ground", "steel"}, "Mud Shot", "Earthquake"),
        ("Stunfisk", {"electric", "ground"}, "Mud Shot", "Discharge"),
        ("Talonflame", {"fire", "flying"}, "Incinerate", "Brave Bird"),
        ("Dewgong", {"ice", "water"}, "Ice Shard", "Icy Wind"),
        ("Nidoqueen", {"poison", "ground"}, "Poison Jab", "Earth Power"),
        ("Beedrill", {"poison", "bug"}, "Poison Jab", "Drill Run"),
        ("Yveltal", {"dark", "flying"}, "Snarl", "Hurricane"),
        ("Mewtwo", {"psychic"}, "Psycho Cut", "Thunderbolt"),
    ],
)
def test_get_species(name: str, types: set[str], one_fast_move: str, one_charged_move: str):
    pokemon = get_species(name)
    assert pokemon.name == name
    assert not pokemon.is_shadow

    for pokemon_type in types:
        assert PokemonType(pokemon_type) in pokemon.types

    assert one_fast_move in {move.name for move in pokemon.fast_moves}
    assert one_charged_move in {move.name for move in pokemon.charged_moves}


@pytest.mark.parametrize(
    ["name", "types", "one_fast_move", "one_charged_move"],
    [
        ("Nidoqueen", {"poison", "ground"}, "Poison Jab", "Earth Power"),
        ("Beedrill", {"poison", "bug"}, "Poison Jab", "Drill Run"),
        ("Mewtwo", {"psychic"}, "Psycho Cut", "Thunderbolt"),
    ],
)
def test_get_species_shadows(name: str, types: set[str], one_fast_move: str, one_charged_move: str):
    pokemon = get_species(name, as_shadow=True)
    assert pokemon.name == name
    assert pokemon.is_shadow

    for pokemon_type in types:
        assert PokemonType(pokemon_type) in pokemon.types

    assert one_fast_move in {move.name for move in pokemon.fast_moves}
    assert one_charged_move in {move.name for move in pokemon.charged_moves}


@pytest.mark.parametrize(
    ["id", "types", "one_fast_move", "one_charged_move"],
    [
        ("stunfisk_galarian", {"ground", "steel"}, "Mud Shot", "Earthquake"),
        ("stunfisk", {"electric", "ground"}, "Mud Shot", "Discharge"),
        ("talonflame", {"fire", "flying"}, "Incinerate", "Brave Bird"),
        ("dewgong", {"ice", "water"}, "Ice Shard", "Icy Wind"),
        ("nidoqueen", {"poison", "ground"}, "Poison Jab", "Earth Power"),
        ("beedrill", {"poison", "bug"}, "Poison Jab", "Drill Run"),
        ("yveltal", {"dark", "flying"}, "Snarl", "Hurricane"),
        ("mewtwo", {"psychic"}, "Psycho Cut", "Thunderbolt"),
        # shadows too
        ("machamp_shadow", {"fighting"}, "Counter", "Rock Slide"),
        ("nidoqueen_shadow", {"poison", "ground"}, "Poison Jab", "Poison Fang"),
        ("victreebel_shadow", {"grass", "poison"}, "Razor Leaf", "Leaf Tornado"),
        ("sealeo_shadow", {"ice", "water"}, "Powder Snow", "Body Slam"),
    ],
)
def test_get_species_by_id(id: str, types: set[str], one_fast_move: str, one_charged_move: str):
    pokemon = get_species_by_id(id)

    # Shadows do not have _shadow in the species name, and instead have is_shadow = True
    if "_shadow" in id:
        id = id.replace("_shadow", "")
        assert pokemon.is_shadow

    assert pokemon.id == id
    for pokemon_type in types:
        assert PokemonType(pokemon_type) in pokemon.types

    assert one_fast_move in {move.name for move in pokemon.fast_moves}
    assert one_charged_move in {move.name for move in pokemon.charged_moves}


@pytest.mark.parametrize(
    ["species_name", "level", "ivs", "stats", "cp"],
    [
        # these test cases come from pokemon I have + calcy IV + gostadium rank checker
        ("Dialga", 40, (15, 15, 13), (229, 178, 172), 4020),
        ("Dialga", 50, (15, 15, 13), (243, 189, 183), 4545),
        ("Garchomp", 50, (13, 14, 13), (230, 173, 211), 4418),
        ("Garchomp", 40, (13, 14, 13), (216, 163, 199), 3908),
        ("Mewtwo", 50, (15, 15, 15), (264, 165, 192), 4724),
        ("Mewtwo", 35, (15, 15, 15), (239, 150, 174), 3880),
        ("Dragonite", 50, (15, 15, 14), (233, 178, 187), 4278),
        ("Dragonite", 40, (15, 15, 14), (219, 168, 176), 3784),
        ("Electabuzz", 11, (5, 4, 7), (89, 71, 75), 661),
        ("Unown", 20, (14, 11, 15), (89, 60, 89), 659),
        ("Bagon", 20, (14, 15, 15), (88, 64, 85), 656),
    ],
)
def test_pokemon_stats(species_name: str, level: int, ivs: IVs, stats: Stats, cp: int):
    species = get_species(species_name)
    pokemon = Pokemon(
        species=species,
        ivs=ivs,
        level=level,
    )

    attack_stat, defense_stat, stamina_stat = stats
    assert attack_stat == floor(pokemon.attack_stat)
    assert defense_stat == floor(pokemon.defense_stat)
    assert stamina_stat == floor(pokemon.stamina_stat)
    assert pokemon.cp == cp
