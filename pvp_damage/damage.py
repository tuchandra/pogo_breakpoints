import itertools
from collections.abc import Iterable, Mapping
from math import floor, sqrt

from pydantic import BaseModel

from pvp_damage.models.constants import (
    CP_MULTIPLIERS,
    MAX_CPM,
    SHADOW_ATTACK_MULT,
    SHADOW_DEF_MULT,
    STAB_BONUS,
    BuffDebuff,
    IVs,
    stat_modifier,
)
from pvp_damage.models.moves import Move, get_move_effectiveness
from pvp_damage.models.pokemon import Pokemon, PokemonSpecies
from pvp_damage.utils import format_defense_range, groupby, sort_attack


class DamageRanges(BaseModel):
    min_damage: int
    max_damage: int

    ranges: Mapping[int, tuple[Pokemon, Pokemon]]
    ranges_all: Mapping[int, set[Pokemon]]

    rank1: Pokemon | None = None
    damage_rank1: int | None = None


def is_stab(move: Move, pokemon: PokemonSpecies) -> bool:
    return move.type in pokemon.types


def calculate_damage(
    move: Move,
    attacker: Pokemon,
    defender: Pokemon,
    *,
    attacker_buff: BuffDebuff = 0,
    defender_buff: BuffDebuff = 0,
) -> int:
    # type effectiveness, stab
    stab_bonus = STAB_BONUS if is_stab(move, attacker.species) else 1
    type_effectiveness = get_move_effectiveness(move.type, defender.species.types)
    multipliers = stab_bonus * type_effectiveness

    # shadow effects and buff/debuff
    effective_attack = (
        attacker.attack_stat * (SHADOW_ATTACK_MULT if attacker.species.is_shadow else 1) * stat_modifier(attacker_buff)
    )
    effective_defense = (
        defender.defense_stat * (SHADOW_DEF_MULT if defender.species.is_shadow else 1) * stat_modifier(defender_buff)
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


def compute_bulkpoints(
    attacker: Pokemon,
    defender: PokemonSpecies | Iterable[Pokemon],
    move: Move,
    cp_limit: int,
) -> DamageRanges:
    """
    Compute the damage that a given attacker does to all possible defenders of a
    given species. This assumes that all the defenders are powered up to the max
    level possible (including best buddy / level 51 where applicable).

    defender: either a `PokemonSpecies` (we will check over all IVs) or an iterable of
    `Pokemon` (we will check over the provided candidates).
    """

    if isinstance(defender, PokemonSpecies):
        iv_table = compute_iv_possibilities(defender, cp_limit)
        defenders = sorted(iv_table.values(), key=lambda mon: mon.defense_stat)
    else:
        defenders = sorted(defender, key=lambda mon: mon.defense_stat)

    lowest_defense, *_, highest_defense = defenders
    highest_stat_product = sorted(defenders, key=lambda mon: mon.stat_product)[-1]

    # first, check if the min and max damage are different at all
    min_damage = calculate_damage(move, attacker, highest_defense)
    max_damage = calculate_damage(move, attacker, lowest_defense)
    if min_damage == max_damage:
        print(
            f"The given {attacker.species.name} ({attacker.ivs}, level {attacker.level}) will always do {min_damage} damage to these {len(defenders)} {defenders[0].species.name}. "
            + "There are no bulkpoints."
        )
        return DamageRanges(
            min_damage=min_damage,
            max_damage=max_damage,
            ranges={min_damage: (lowest_defense, highest_defense)},
            ranges_all={min_damage: set(defenders)},
            rank1=highest_stat_product,
            damage_rank1=min_damage,
        )

    # otherwise, brute force the bulkpoints by computing the damage
    damage_rank1 = calculate_damage(move, attacker, highest_stat_product)
    damage_vs_all = {defender: calculate_damage(move, attacker, defender) for defender in defenders}
    damage_partition: dict[int, set[Pokemon]] = {damage: set() for damage in range(min_damage, max_damage + 1)}
    for mon, damage in damage_vs_all.items():
        damage_partition[damage].add(mon)

    print(f"{attacker.species.full_name} using {move}; CP {attacker.cp} (level {attacker.level}, {attacker.ivs})")
    print(
        f"vs. {defenders[0].species.full_name} ({format_defense_range(defenders)}); rank 1 {highest_stat_product.defense_stat:.2f} def)"
    )

    ranges: dict[int, tuple[Pokemon, Pokemon]] = {}
    ranges_all: dict[int, set[Pokemon]] = {}
    for damage in range(min_damage, max_damage + 1):
        lowest, *_, highest = sorted(damage_partition[damage], key=lambda mon: mon.defense_stat)
        ranges[damage] = (lowest, highest)
        ranges_all[damage] = damage_partition[damage]

        percent = len(damage_partition[damage]) / len(defenders) * 100
        print(f"- {damage}: {percent:.2f}% of IVs; {format_defense_range([lowest, highest])}")

    return DamageRanges(
        min_damage=min_damage,
        max_damage=max_damage,
        ranges=ranges,
        ranges_all=ranges_all,
        rank1=highest_stat_product,
        damage_rank1=damage_rank1,
    )


def compute_breakpoints(
    attacker_species: PokemonSpecies,
    defender: Pokemon,
    move: Move,
    cp_limit: int,
    *,
    attacker_buff: BuffDebuff = 0,
) -> DamageRanges:
    """
    Compute the damage that all possible attackers will do to a given defender.
    This assumes all attackers are powered up to the max level possible (including
    best buddy / level 51), but maybe we can turn this off later.

    Use case: finding which attackers will do at least X damage to e.g., the rank 1
    Clodsire.
    """

    iv_table = compute_iv_possibilities(attacker_species, cp_limit)
    attackers = sort_attack(iv_table.values())

    lowest_attack, *_, highest_attack = attackers

    # first, check if the min and max damage are different at all
    min_damage = calculate_damage(move, lowest_attack, defender, attacker_buff=attacker_buff)
    max_damage = calculate_damage(move, highest_attack, defender, attacker_buff=attacker_buff)
    if min_damage == max_damage:
        print(f"- {min_damage} damage guaranteed (no breakpoints)")
        return DamageRanges(
            min_damage=min_damage,
            max_damage=max_damage,
            ranges={min_damage: (lowest_attack, highest_attack)},
            ranges_all={min_damage: set(attackers)},
        )

    # sort by attack, then partition damage vs. the defender
    damage_partition: dict[int, set[Pokemon]] = {damage: set() for damage in range(min_damage, max_damage + 1)}
    by_attack = groupby(attackers, lambda mon: mon.attack_stat)
    for _stat, attackers_with_this_stat in by_attack.items():
        attacker = attackers_with_this_stat[0]
        damage = calculate_damage(move, attacker, defender, attacker_buff=attacker_buff)
        damage_partition[damage].update(attackers_with_this_stat)

        # For debugging - print every distinct attack value.
        # print(f"Attack {stat:.3f} (level {attacker.level:.1f} & {attacker.attack_iv:2d} IV) | {damage} damage")

    print(
        f"{attacker_species.full_name} ({lowest_attack.attack_stat:.3f} - {highest_attack.attack_stat:.3f}) using {move}"
    )
    print(f"vs. {defender.species.full_name} ({defender.ivs}, level {defender.level})")

    ranges: dict[int, tuple[Pokemon, Pokemon]] = {}
    ranges_all: dict[int, set[Pokemon]] = {}
    for damage, mons in sorted(damage_partition.items(), key=lambda x: x[0]):
        lowest, *_, highest = sorted(mons, key=lambda mon: mon.attack_stat)
        ranges[damage] = (lowest, highest)
        ranges_all[damage] = mons

        percent = len(mons) / len(iv_table) * 100
        print(f"- {damage}: {percent:.2f}% of IVs; atk: {lowest.attack_stat:.3f} - {highest.attack_stat:.3f}")

    return DamageRanges(
        min_damage=min_damage,
        max_damage=max_damage,
        ranges=ranges,
        ranges_all=ranges_all,
    )
