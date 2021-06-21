import json
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel

STAB_BONUS = 1.2
SHADOW_ATTACK_MULT = 1.2
SHADOW_DEF_MULT = 5 / 6


class Effectiveness(Enum):
    super_effective = 1.6
    not_very_effective = 0.625
    immune = 0.625 * 0.625
    default = 1


class PokemonType(Enum):
    normal = "normal"
    fire = "fire"
    water = "water"
    electric = "electric"
    grass = "grass"
    ice = "ice"
    fighting = "fighting"
    poison = "poison"
    ground = "ground"
    flying = "flying"
    psychic = "psychic"
    bug = "bug"
    rock = "rock"
    ghost = "ghost"
    dragon = "dragon"
    dark = "dark"
    steel = "steel"
    fairy = "fairy"


CP_MULTIPLIERS = {
    # https://docs.google.com/spreadsheets/d/1akMTElC3mStmbRNXI8a4J94YmwJuvia0DiVV_l1W9h0/
    1: 0.0939999967813491,
    1.5: 0.135137430784308,
    2: 0.166397869586944,
    2.5: 0.192650914456886,
    3: 0.215732470154762,
    3.5: 0.236572655026622,
    4: 0.255720049142837,
    4.5: 0.273530381100769,
    5: 0.290249884128570,
    5.5: 0.306057381335773,
    6: 0.321087598800659,
    6.5: 0.335445032295077,
    7: 0.349212676286697,
    7.5: 0.362457748778790,
    8: 0.375235587358474,
    8.5: 0.387592411085168,
    9: 0.399567276239395,
    9.5: 0.411193549517250,
    10: 0.422500014305114,
    10.5: 0.432926413410414,
    11: 0.443107545375824,
    11.5: 0.453059953871985,
    12: 0.462798386812210,
    12.5: 0.472336077786704,
    13: 0.481684952974319,
    13.5: 0.490855810259008,
    14: 0.499858438968658,
    14.5: 0.508701756943992,
    15: 0.517393946647644,
    15.5: 0.525942508771329,
    16: 0.534354329109191,
    16.5: 0.542635762230353,
    17: 0.550792694091796,
    17.5: 0.558830599438087,
    18: 0.566754519939422,
    18.5: 0.574569148039264,
    19: 0.582278907299041,
    19.5: 0.589887911977272,
    20: 0.597400009632110,
    20.5: 0.604823657502073,
    21: 0.612157285213470,
    21.5: 0.619404110566050,
    22: 0.626567125320434,
    22.5: 0.633649181622743,
    23: 0.640652954578399,
    23.5: 0.647580963301656,
    24: 0.654435634613037,
    24.5: 0.661219263506722,
    25: 0.667934000492096,
    25.5: 0.674581899290818,
    26: 0.681164920330047,
    26.5: 0.687684905887771,
    27: 0.694143652915954,
    27.5: 0.700542893277978,
    28: 0.706884205341339,
    28.5: 0.713169102333341,
    29: 0.719399094581604,
    29.5: 0.725575616972598,
    30: 0.731700003147125,
    30.5: 0.734741011137376,
    31: 0.737769484519958,
    31.5: 0.740785574597326,
    32: 0.743789434432983,
    32.5: 0.746781208702482,
    33: 0.749761044979095,
    33.5: 0.752729105305821,
    34: 0.755685508251190,
    34.5: 0.758630366519684,
    35: 0.761563837528228,
    35.5: 0.764486065255226,
    36: 0.767397165298461,
    36.5: 0.770297273971590,
    37: 0.773186504840850,
    37.5: 0.776064945942412,
    38: 0.778932750225067,
    38.5: 0.781790064808426,
    39: 0.784636974334716,
    39.5: 0.787473583646825,
    40: 0.790300011634826,
    40.5: 0.792803950958807,
    41: 0.795300006866455,
    41.5: 0.797803921486970,
    42: 0.800300002098083,
    42.5: 0.802803892322847,
    43: 0.805299997329711,
    43.5: 0.807803863460723,
    44: 0.810299992561340,
    44.5: 0.812803834895026,
    45: 0.815299987792968,
    45.5: 0.817803806620319,
    46: 0.820299983024597,
    46.5: 0.822803778631297,
    47: 0.825299978256225,
    47.5: 0.827803750922782,
    48: 0.830299973487854,
    48.5: 0.832803753381377,
    49: 0.835300028324127,
    49.5: 0.837803755931569,
    50: 0.840300023555755,
    50.5: 0.842803729034748,
    51: 0.845300018787384,
    51.5: 0.847803702398935,
    52: 0.850300014019012,
    52.5: 0.852803676019539,
    53: 0.855300009250640,
    53.5: 0.857803649892077,
    54: 0.860300004482269,
    54.5: 0.862803624012168,
    55: 0.865299999713897,
}


class OneTypeMatchups(BaseModel):
    super_effective_on: set[PokemonType]
    resisted_by: set[PokemonType]
    double_resisted_by: set[PokemonType]


TYPE_MATCHUPS: dict[PokemonType, OneTypeMatchups] = {
    # attacker: OneTypeMatchups(
    #   super_effective_on = set[PokemonType],
    #   resisted_by = set[PokemonType],
    #   double_resisted_by = set[PokemonType],
    # )
    PokemonType.normal: OneTypeMatchups(
        super_effective_on=set(),
        resisted_by={PokemonType.rock, PokemonType.steel},
        double_resisted_by={PokemonType.ghost},
    ),
    PokemonType.fighting: OneTypeMatchups(
        super_effective_on={
            PokemonType.dark,
            PokemonType.ice,
            PokemonType.normal,
            PokemonType.rock,
            PokemonType.steel,
        },
        resisted_by={
            PokemonType.bug,
            PokemonType.fairy,
            PokemonType.flying,
            PokemonType.poison,
            PokemonType.psychic,
        },
        double_resisted_by={PokemonType.ghost},
    ),
    PokemonType.flying: OneTypeMatchups(
        super_effective_on={PokemonType.bug, PokemonType.fighting, PokemonType.grass},
        resisted_by={PokemonType.electric, PokemonType.rock, PokemonType.steel},
        double_resisted_by=set(),
    ),
    PokemonType.poison: OneTypeMatchups(
        super_effective_on={PokemonType.fairy, PokemonType.grass},
        resisted_by={
            PokemonType.ghost,
            PokemonType.ground,
            PokemonType.poison,
            PokemonType.rock,
        },
        double_resisted_by={PokemonType.steel},
    ),
    PokemonType.ground: OneTypeMatchups(
        super_effective_on={
            PokemonType.electric,
            PokemonType.fire,
            PokemonType.poison,
            PokemonType.rock,
            PokemonType.steel,
        },
        resisted_by={PokemonType.bug, PokemonType.grass},
        double_resisted_by={PokemonType.flying},
    ),
    PokemonType.rock: OneTypeMatchups(
        super_effective_on={
            PokemonType.bug,
            PokemonType.fire,
            PokemonType.flying,
            PokemonType.ice,
        },
        resisted_by={PokemonType.fighting, PokemonType.ground, PokemonType.steel},
        double_resisted_by=set(),
    ),
    PokemonType.bug: OneTypeMatchups(
        super_effective_on={PokemonType.dark, PokemonType.grass, PokemonType.psychic},
        resisted_by={
            PokemonType.fairy,
            PokemonType.fighting,
            PokemonType.fire,
            PokemonType.flying,
            PokemonType.ghost,
            PokemonType.poison,
            PokemonType.steel,
        },
        double_resisted_by=set(),
    ),
    PokemonType.ghost: OneTypeMatchups(
        super_effective_on={PokemonType.ghost, PokemonType.psychic},
        resisted_by={PokemonType.dark},
        double_resisted_by={PokemonType.normal},
    ),
    PokemonType.steel: OneTypeMatchups(
        super_effective_on={PokemonType.fairy, PokemonType.ice, PokemonType.rock},
        resisted_by={
            PokemonType.electric,
            PokemonType.fire,
            PokemonType.steel,
            PokemonType.water,
        },
        double_resisted_by=set(),
    ),
    PokemonType.fire: OneTypeMatchups(
        super_effective_on={
            PokemonType.bug,
            PokemonType.grass,
            PokemonType.ice,
            PokemonType.steel,
        },
        resisted_by={PokemonType.dragon, PokemonType.fire, PokemonType.rock, PokemonType.water},
        double_resisted_by=set(),
    ),
    PokemonType.water: OneTypeMatchups(
        super_effective_on={PokemonType.fire, PokemonType.ground, PokemonType.rock},
        resisted_by={PokemonType.dragon, PokemonType.grass, PokemonType.water},
        double_resisted_by=set(),
    ),
    PokemonType.grass: OneTypeMatchups(
        super_effective_on={PokemonType.ground, PokemonType.rock, PokemonType.water},
        resisted_by={
            PokemonType.bug,
            PokemonType.dragon,
            PokemonType.fire,
            PokemonType.flying,
            PokemonType.grass,
            PokemonType.poison,
            PokemonType.steel,
        },
        double_resisted_by=set(),
    ),
    PokemonType.electric: OneTypeMatchups(
        super_effective_on={PokemonType.flying, PokemonType.water},
        resisted_by={PokemonType.dragon, PokemonType.electric, PokemonType.grass},
        double_resisted_by={PokemonType.ground},
    ),
    PokemonType.psychic: OneTypeMatchups(
        super_effective_on={PokemonType.fighting, PokemonType.poison},
        resisted_by={PokemonType.psychic, PokemonType.steel},
        double_resisted_by={PokemonType.dark},
    ),
    PokemonType.ice: OneTypeMatchups(
        super_effective_on={
            PokemonType.dragon,
            PokemonType.flying,
            PokemonType.grass,
            PokemonType.ground,
        },
        resisted_by={PokemonType.fire, PokemonType.ice, PokemonType.steel, PokemonType.water},
        double_resisted_by=set(),
    ),
    PokemonType.dragon: OneTypeMatchups(
        super_effective_on={PokemonType.dragon},
        resisted_by={PokemonType.steel},
        double_resisted_by={PokemonType.fairy},
    ),
    PokemonType.dark: OneTypeMatchups(
        super_effective_on={PokemonType.ghost, PokemonType.psychic},
        resisted_by={PokemonType.dark, PokemonType.fairy, PokemonType.fighting},
        double_resisted_by=set(),
    ),
    PokemonType.fairy: OneTypeMatchups(
        super_effective_on={PokemonType.dark, PokemonType.dragon, PokemonType.fighting},
        resisted_by={PokemonType.fire, PokemonType.poison, PokemonType.steel},
        double_resisted_by=set(),
    ),
}


def _load_gamemaster() -> Any:
    with open(Path("data/gamemaster.json")) as f:
        gamemaster = json.load(f)

    return gamemaster


GAMEMASTER = _load_gamemaster()
