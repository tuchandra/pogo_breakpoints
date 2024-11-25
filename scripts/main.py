from dataclasses import dataclass

import pvp_damage.damage as dmg
from pvp_damage.models import pokemon as pkm
from pvp_damage.models.constants import BuffDebuff
from pvp_damage.models.moves import get_move_by_name
from pvp_damage.utils import (
    format_attack_range,
    format_defense_range,
    highest_defense,
    lowest_defense,
    rank1,
    sort_defense,
)


@dataclass
class Battler:
    name: str
    buff: BuffDebuff = 0
    shadow: bool = False

    def __str__(self) -> str:
        name = f"{self.name} (Shadow)" if self.shadow else self.name

        if self.buff > 0:
            return f"{name} (+{self.buff})"
        if self.buff < 0:
            return f"{name} (-{self.buff})"

        return name


def compute_vs_defender(attacker: Battler, defender: Battler, move_name: str):
    attacker_species = pkm.get_species(attacker.name, as_shadow=attacker.shadow)
    defender_species = pkm.get_species(defender.name, as_shadow=defender.shadow)
    defender_ivs = dmg.compute_iv_possibilities(defender_species, 1500).values()

    defender_rank1 = rank1(defender_ivs)
    defender_mindef = lowest_defense(defender_ivs)
    defender_maxdef = highest_defense(defender_ivs)

    print()
    print(f"----- {attacker} using {move_name} vs. {defender} -----")

    move = get_move_by_name(move_name)

    print(f"vs. min defense ({defender_mindef.defense_stat:.2f})")
    dmg.compute_breakpoints(attacker_species, defender_mindef, move, 1500, attacker_buff=attacker.buff)

    print()
    print(f"vs. rank 1 ({defender_rank1.defense_stat:.2f})")
    dmg.compute_breakpoints(attacker_species, defender_rank1, move, 1500, attacker_buff=attacker.buff)

    print()
    print(f"vs. max defense ({defender_maxdef.defense_stat:.2f})")
    dmg.compute_breakpoints(attacker_species, defender_maxdef, move, 1500, attacker_buff=attacker.buff)


ariados = Battler("Ariados")

# compute_vs_defender(Battler(name="Primeape"), ariados, "Karate Chop")
# compute_vs_defender(Battler(name="Toxapex"), ariados, "Poison Jab")


# compute_vs_defender(ariados, Battler(name="Guzzlord"), "Poison Sting")
# compute_vs_defender(ariados, Battler(name="Greninja"), "Poison Sting")
# compute_vs_defender(ariados, Battler(name="Abomasnow"), "Poison Sting")
# compute_vs_defender(ariados, Battler(name="Feraligatr", shadow=True), "Poison Sting")

# compute_vs_defender("Primeape", "Clodsire", "Karate Chop")
# compute_vs_defender("Primeape", "Annihilape", "Karate Chop")
# compute_vs_defender("Primeape", "Feraligatr", "Karate Chop")
# compute_vs_defender("Primeape", "Greninja", "Karate Chop")
# compute_vs_defender("Primeape", "Ariados", "Karate Chop")
# compute_vs_defender("Primeape", "Serperior", "Karate Chop")


# compute_vs_defender("Annihilape", "Serperior", "Counter")
# compute_vs_defender("Annihilape", "Ariados", "Counter")
# compute_vs_defender("Serperior", "Annihilape", "Vine Whip")

# against annihilape?
# compute_vs_defender("Feraligatr", "Annihilape", claw)

# what about when boosted one?
# compute_vs_defender("Annihilape", "Clodsire", counter, attacker_buff=+1)
# compute_vs_defender("Annihilape", "Clodsire", counter, attacker_buff=+2)

# compute_vs_defender("Annihilape", "Annihilape", counter)
# compute_vs_defender("Annihilape", "Annihilape", counter, attacker_buff=+1)
# compute_vs_defender("Annihilape", "Annihilape", counter, attacker_buff=+2)


def pex_vs_ariados():
    pex = pkm.get_species("Toxapex")
    poison_jab = get_move_by_name("Poison Jab")

    # Default IV Toxapex: 4 / 11 / 14
    # Rank 1 Toxapex: 0 / 15 / 15
    pex_ivs = dmg.compute_iv_possibilities(pex, 1500)
    default = pex_ivs[(4, 11, 14)]
    rank1 = pex_ivs[(0, 15, 15)]

    # Of the Ariados that have >= 127.8 attack, how much defense do
    # we need to get the bulkpoint against these Toxapex?
    ariados = pkm.get_species("Ariados")
    ariados_ivs = dmg.compute_iv_possibilities(ariados, 1500)
    viable_ariados = {ivs: mon for ivs, mon in ariados_ivs.items() if mon.attack_stat >= 127.18}

    print("Rank 1 Toxapex vs. high-ish attack Ariados")
    dmg.compute_bulkpoints(rank1, viable_ariados.values(), poison_jab, 1500)

    print()
    print("1/13/8 Toxapex vs. high-ish attack Ariados")
    dmg.compute_bulkpoints(pex_ivs[(1, 13, 8)], viable_ariados.values(), poison_jab, 1500)

    print()
    print("3/12/15 Toxapex vs. high-ish attack Ariados")
    dmg.compute_bulkpoints(pex_ivs[(3, 12, 15)], viable_ariados.values(), poison_jab, 1500)

    print()
    print("Default IV Toxapex vs. high-ish attack Ariados")
    dmg.compute_bulkpoints(default, viable_ariados.values(), poison_jab, 1500)


# pex_vs_ariados()


def squag_vs_ariados():
    quag = pkm.get_species("Quagsire", as_shadow=True)
    mudshot = get_move_by_name("Mud Shot")

    # Default IV Quag: 4 / 14 / 10
    # Rank 1 Quag: 0 / 15 / 14
    quag_ivs = dmg.compute_iv_possibilities(quag, 1500)
    default = quag_ivs[(4, 14, 10)]
    rank1 = quag_ivs[(0, 15, 14)]

    # Of the Ariados that have >= 127.18 attack, how much defense do
    # we need to get the bulkpoint against these Quag?
    ariados = pkm.get_species("Ariados")
    ariados_ivs = dmg.compute_iv_possibilities(ariados, 1500)
    viable_ariados = {ivs: mon for ivs, mon in ariados_ivs.items() if mon.attack_stat >= 127.18}

    print("Rank 1 S-Quag vs. high-ish attack Ariados")
    dmg.compute_bulkpoints(rank1, viable_ariados.values(), mudshot, 1500)

    print()
    print("Default IV S-Quag vs. high-ish attack Ariados")
    dmg.compute_bulkpoints(default, viable_ariados.values(), mudshot, 1500)


squag_vs_ariados()


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
    print(f"Defense range: {format_defense_range(clod_killers)}")
    print()

    # then, consider how much damage our ape can do to each of these apes
    # (that is, assuming our opponent is using a Clod-slayer)
    print("Against the defense Clodsire-killer, we can ...")
    dmg.compute_breakpoints(ape, lowest_defense(clod_killers), counter, 1500)

    print()
    print("Against the highest defense Clodsire-killer, we can ...")
    dmg.compute_breakpoints(ape, highest_defense(clod_killers), counter, 1500)


# compute_ape_mirror()


def compute_ape_serperior_bulkpoints():
    ape = pkm.get_species("Annihilape")
    clod = pkm.get_species("Clodsire")
    serp = pkm.get_species("Serperior")
    counter = get_move_by_name("Counter")
    vine_whip = get_move_by_name("Vine Whip")

    # first, get the clod-slayer apes
    clod_ivs = dmg.compute_iv_possibilities(clod, 1500).values()
    clod_ranges = dmg.compute_breakpoints(ape, highest_defense(clod_ivs), counter, 1500)
    clod_killers = sort_defense(clod_ranges.ranges_all[5])

    print()
    print(f"We have {len(clod_killers)} Clodsire-slayers that hit the breakpoint on max defense Clodsire")
    print(f"({format_attack_range(clod_killers)}; {format_defense_range(clod_killers)})")

    # and how much damage Serperior can do to each of these apes
    serp_ivs = dmg.compute_iv_possibilities(serp, 1500)
    rank1_serp = rank1(serp_ivs.values())
    slight_attack_serp = serp_ivs[5, 14, 15]

    # what defense would we need to get the bulkpoint against the rank1 serp?
    # can any of the clod-slayers do it? no.
    dmg.compute_bulkpoints(rank1_serp, clod_killers, vine_whip, 1500)

    # what about the bulkpoint in general? vs. rank 1 and slgiht attack weight
    dmg.compute_bulkpoints(rank1_serp, ape, vine_whip, 1500)
    dmg.compute_bulkpoints(slight_attack_serp, ape, vine_whip, 1500)


# compute_ape_serperior_bulkpoints()
