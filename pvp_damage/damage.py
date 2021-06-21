from math import floor

from pvp_damage.constants import SHADOW_ATTACK_MULT, SHADOW_DEF_MULT, STAB_BONUS
from pvp_damage.moves import Move, get_move_effectiveness
from pvp_damage.pokemon import Pokemon, PokemonSpecies


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
