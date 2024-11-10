import pvp_damage.damage as dmg
from pvp_damage.models import pokemon as pkm
from pvp_damage.models.constants import BuffDebuff
from pvp_damage.models.moves import Move, get_move_by_name
from pvp_damage.utils import groupby, highest_defense, lowest_defense, rank1, sort_attack, sort_defense


def compute_vs_defender(name: str, opponent_name: str, move_name: str, attacker_buff: BuffDebuff = 0):
    attacker = pkm.get_species(name)
    opponent = pkm.get_species(opponent_name)
    opponent_ivs = dmg.compute_iv_possibilities(opponent, 1500).values()

    opponent_rank1 = rank1(opponent_ivs)
    opponent_mindef = lowest_defense(opponent_ivs)
    opponent_maxdef = highest_defense(opponent_ivs)

    if attacker_buff > 0:
        attacker_printed = f"{name} (+{attacker_buff})"
    elif attacker_buff < 0:
        attacker_printed = f"{name} (-{attacker_buff})"
    else:
        attacker_printed = name

    print()
    print(f"----- {attacker_printed} vs. {opponent_name} -----")

    move = get_move_by_name(move_name)

    print(f"vs. min defense ({opponent_mindef.defense_stat:.2f})")
    dmg.compute_breakpoints(attacker, opponent_mindef, move, 1500, attacker_buff=attacker_buff)

    print()
    print(f"vs. rank 1 ({opponent_rank1.defense_stat:.2f})")
    dmg.compute_breakpoints(attacker, opponent_rank1, move, 1500, attacker_buff=attacker_buff)

    print()
    print(f"vs. max defense ({opponent_maxdef.defense_stat:.2f})")
    dmg.compute_breakpoints(attacker, opponent_maxdef, move, 1500, attacker_buff=attacker_buff)


# compute_vs_defender("Primeape", "Clodsire", "Karate Chop")
# compute_vs_defender("Primeape", "Annihilape", "Karate Chop")
# compute_vs_defender("Primeape", "Feraligatr", "Karate Chop")
compute_vs_defender("Primeape", "Serperior", "Karate Chop")

# against annihilape?
# compute_vs_defender("Feraligatr", "Annihilape", claw)

# what about when boosted one?
# compute_vs_defender("Annihilape", "Clodsire", counter, attacker_buff=+1)
# compute_vs_defender("Annihilape", "Clodsire", counter, attacker_buff=+2)

# compute_vs_defender("Annihilape", "Annihilape", counter)
# compute_vs_defender("Annihilape", "Annihilape", counter, attacker_buff=+1)
# compute_vs_defender("Annihilape", "Annihilape", counter, attacker_buff=+2)


# mirror, special case
def compute_ape_mirror():
    ape = pkm.get_species("Annihilape")
    clodsire = pkm.get_species("Clodsire")
    counter = get_move_by_name("Counter")

    # first, find the apes that hit the clodsire breakpoint
    clod_ivs = dmg.compute_iv_possibilities(clodsire, 1500).values()
    clod_ranges = dmg.compute_breakpoints(ape, highest_defense(clod_ivs), counter, 1500)
    clod_killers = sort_defense(clod_ranges.ranges_all[5])

    print()
    print(f"We have {len(clod_killers)} Annihilapes that hit the breakpoint on max defense Clodsire")
    print(f"Defense range: {clod_killers[0].defense_stat:.2f} - {clod_killers[-1].defense_stat:.2f}")
    print()

    # then, consider how much damage our ape can do to each of these apes
    print("Against the lowest defense Ape among the Clodsire killers ...")
    dmg.compute_breakpoints(ape, lowest_defense(clod_killers), counter, 1500)

    print("Against the highest defense Ape among the Clodsire killers ...")
    dmg.compute_breakpoints(ape, highest_defense(clod_killers), counter, 1500)


# compute_ape_mirror()
