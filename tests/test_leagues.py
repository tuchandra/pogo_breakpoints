import pytest

from pvp_damage.models.leagues import GREAT_LEAGUE, ULTRA_LEAGUE
from pvp_damage.models.pokemon import get_species


@pytest.mark.parametrize(
    ("name", "shadow", "expected_present"),
    [
        # regular non-shadows
        ("Azumarill", False, True),
        ("Bastiodon", False, True),
        ("Talonflame", False, True),
        ("Stunfisk (Galarian)", False, True),
        ("Venusaur", False, True),
        ("Jellicent", False, True),
        ("Registeel", False, True),
        ("Charjabug", False, True),
        ("Carbink", False, True),
        # shadows not in meta
        ("Azumarill", True, False),
        ("Bastiodon", True, False),
        ("Talonflame", True, False),
        # shadow in meta
        ("Victreebel", True, True),
        ("Gligar", True, True),
        ("Swampert", True, True),
        # fell from meta between 2021 and now
        ("Nidoqueen", True, False),
        ("Wigglytuff", False, False),
        ("Hypno", False, False),
        ("Hypno", True, False),
        ("Galvantula", False, False),
        ("Mew", False, False),
    ],
)
def test_great_league(name: str, shadow: bool, expected_present: bool):
    great_species = [item[0] for item in GREAT_LEAGUE.meta]
    species = get_species(name, shadow)

    assert (species in great_species) is expected_present


@pytest.mark.parametrize(
    ("name", "shadow", "expected_present"),
    [
        # no GL pokemon
        ("Azumarill", False, False),
        ("Bastiodon", False, False),
        ("Wigglytuff", False, False),
        ("Stunfisk (Galarian)", False, False),
        # regular pokemon
        ("Talonflame", False, True),
        ("Venusaur", False, True),
        ("Registeel", False, True),
        ("Cobalion", False, True),
        ("Giratina (Altered)", False, True),
        ("Jellicent", False, True),
        # these shadows aren't there
        ("Registeel", True, False),
        ("Venusaur", True, False),
        ("Cradily", True, False),
        # these shadows are
        ("Swampert", True, True),
        ("Dragonite", True, True),
        # fell from meta between 2021 and now
        ("Abomasnow", True, False),
        ("Abomasnow", False, False),
        ("Melmetal", False, False),
    ],
)
def test_ultra_league(name: str, shadow: bool, expected_present: bool):
    ultra_species = [item[0] for item in ULTRA_LEAGUE.meta]
    species = get_species(name, shadow)

    assert (species in ultra_species) is expected_present
