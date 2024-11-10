from collections.abc import Callable, Iterable, Sequence

from pvp_damage.models.pokemon import Pokemon


def highest_attack(pokemons: Iterable[Pokemon]) -> Pokemon:
    return max(pokemons, key=lambda mon: mon.attack_stat)


def highest_defense(pokemons: Iterable[Pokemon]) -> Pokemon:
    return max(pokemons, key=lambda mon: mon.defense_stat)


def highest_stamina(pokemons: Iterable[Pokemon]) -> Pokemon:
    return max(pokemons, key=lambda mon: mon.stamina_stat)


def sort_attack(pokemons: Iterable[Pokemon]) -> list[Pokemon]:
    return sorted(pokemons, key=lambda mon: mon.attack_stat)


def sort_defense(pokemons: Iterable[Pokemon]) -> list[Pokemon]:
    return sorted(pokemons, key=lambda mon: mon.defense_stat)


def sort_stamina(pokemons: Iterable[Pokemon]) -> list[Pokemon]:
    return sorted(pokemons, key=lambda mon: mon.stamina_stat)


def rank1(pokemons: Iterable[Pokemon]) -> Pokemon:
    return max(pokemons, key=lambda mon: mon.stat_product)


def groupby(iterable: Iterable[Pokemon], key: Callable[[Pokemon], float]) -> dict[float, list[Pokemon]]:
    out: dict[float, list[Pokemon]] = {}
    for mon in sorted(iterable, key=key):
        key_val = key(mon)
        if key_val not in out:
            out[key_val] = []
        out[key_val].append(mon)

    return out
