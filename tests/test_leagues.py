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
        ("Wigglytuff", False, True),
        ("Hypno", False, True),
        ("Mew", False, True),
        ("Galvantula", False, True),
        # shadows not in meta
        ("Azumarill", True, False),
        ("Bastiodon", True, False),
        ("Talonflame", True, False),
        # shadow in meta
        ("Hypno", True, True),
        ("Victreebel", True, True),
        ("Machamp", True, True),
        ("Nidoqueen", True, True),
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
        # regular pokemon
        ("Talonflame", False, True),
        ("Venusaur", False, True),
        ("Registeel", False, True),
        ("Melmetal", False, True),
        ("Giratina (Altered)", False, True),
        # these pokemon mostly in premier
        ("Jellicent", False, False),
        ("Stunfisk (Galarian)", False, False),
        # these shadows aren't there
        ("Registeel", True, False),
        ("Venusaur", True, False),
        ("Cradily", True, False),
        ("Swampert", True, False),
        # these shadows are
        ("Machamp", True, True),
        ("Abomasnow", True, True),
    ],
)
def test_ultra_league(name: str, shadow: bool, expected_present: bool):
    ultra_species = [item[0] for item in ULTRA_LEAGUE.meta]
    species = get_species(name, shadow)

    assert (species in ultra_species) is expected_present
