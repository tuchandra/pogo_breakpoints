import itertools
from math import floor, sqrt

from pvp_damage.models.constants import (
    CP_MULTIPLIERS,
    MAX_CPM,
    SHADOW_ATTACK_MULT,
    SHADOW_DEF_MULT,
    STAB_BONUS,
    IVs,
)
from pvp_damage.models.moves import Move, get_move_effectiveness
from pvp_damage.models.pokemon import Pokemon, PokemonSpecies
from pvp_damage.models.leagues import League


def is_stab(move: Move, pokemon: PokemonSpecies) -> bool:
    return move.type in pokemon.types


def calculate_damage(
    move: Move,
    attacker: Pokemon,
    defender: Pokemon,
) -> int:
    # type effectiveness, stab
    stab_bonus = STAB_BONUS if is_stab(move, attacker.species) else 1
    type_effectiveness = get_move_effectiveness(move.type, defender.species.types)
    multipliers = stab_bonus * type_effectiveness

    # shadow effects
    effective_attack = attacker.attack_stat * (
        SHADOW_ATTACK_MULT if attacker.species.is_shadow else 1
    )
    effective_defense = defender.defense_stat * (
        SHADOW_DEF_MULT if defender.species.is_shadow else 1
    )

    # these are magic numbers, yes; they appear in the damage formula this way
    # 1.3 is a multiplier that only appears in PVP (not PVE); 0.5 is just there
    damage = (0.5 * 1.3 * effective_attack / effective_defense * multipliers * move.power) + 1
    return floor(damage)


def find_max_level_for_league(species: PokemonSpecies, ivs: IVs, cp_limit: int) -> Pokemon:
    """
    For a given league, find the max level that a given species with given IVs can be
    to still be eligible for the league. The formula is -

    cp = floor[ 0.1 * sqrt(att^2 * dfn * sta) ]
    (we ignore the floor except for the edge case at the bottom of this func)

    And att, dfn, sta are each cpm * (base stat + IV), where cpm is the CP multiplier.
    The (base stat + IV) - for a given species & IV combination - is constant.
    So if we want the CP below some threshold, we must find the maximal cpm such that
    the CP stays below CP_MAX.

    cp = 0.1 * cpm^2 * sqrt[(base att + iv)^2 * (base dfn + iv) * (base sta + iv)] <= CP_MAX

    and can compute cpm^2 < 10 * CP_MAX / sqrt(...), then get the maximal cpm, and
    therefore level.
    """

    att = species.attack + ivs[0]
    dfn = species.defense + ivs[1]
    sta = species.stamina + ivs[2]
    stat_product = sqrt(att * att * dfn * sta)

    cpm_2 = 10 * cp_limit / stat_product
    cpm_limit = sqrt(cpm_2)

    # check for level 51 first (we'd get StopIteration otherwise)
    if cpm_limit > MAX_CPM:
        return Pokemon(species=species, level=51, ivs=ivs)

    # otherwise, find first entry in CP_MULTIPLIERS that _passes_ our target CP multiplier
    level = next(level for (level, cpm) in CP_MULTIPLIERS.items() if cpm >= cpm_limit)

    # there's an edge case where the found CP multiplier (which is larger than our max)
    # could still be within the CP threshold, just because of the floor in the CP calculation.
    # check if this happens (it's rare) - but otherwise decrement the found level by 0.5
    # to get the level that's WITHIN the CP limit.
    computed_cp = 0.1 * CP_MULTIPLIERS[level] ** 2 * stat_product
    if floor(computed_cp) > cp_limit:
        level -= 0.5

    return Pokemon(species=species, level=level, ivs=ivs)


def compute_iv_possibilities(species: PokemonSpecies, cp_limit: int) -> dict[IVs, Pokemon]:
    """
    Given a Pokemon species and a league (CP limit), compute - for every IV combination - what the
    maximal level is for the Pokemon to stay under the CP limit. This returns a mapping
    from IV combinations to Pokemon instances.
    """

    iv_combinations = itertools.product(range(16), range(16), range(16))
    out = {ivs: find_max_level_for_league(species, ivs, cp_limit) for ivs in iv_combinations}

    return out


def compute_attacker_damage(
    attacker: Pokemon,
    defender: PokemonSpecies,
    move: Move,
    cp_limit: int,
) -> None:
    """
    Compute the damage that a given attacker does to all possible defenders of a
    given species. This assumes that all the defenders are powered up to the max
    level possible (including best buddy / level 51 where applicable).
    """

    all_defenders = compute_iv_possibilities(defender, cp_limit)
    all_defenders = sorted(all_defenders.values(), key=lambda mon: mon.defense_stat)
    min_defense_mon = all_defenders[0]
    max_defense_mon = all_defenders[1]

    # first, check if the min and max damage are different at all
    min_damage = calculate_damage(move, attacker, max_defense_mon)
    max_damage = calculate_damage(move, attacker, min_defense_mon)
    if min_damage == max_damage:
        return

    # otherwise, find the bulkpoints and just compute the damage
    damage_vs_all = {
        defender: calculate_damage(move, attacker, defender) for defender in all_defenders
    }

    print(damage_vs_all)

    # find the point where damage changes

    ...
