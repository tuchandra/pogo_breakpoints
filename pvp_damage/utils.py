from collections.abc import Callable, Iterable

from pvp_damage.models.pokemon import Pokemon


def highest_attack(pokemons: Iterable[Pokemon]) -> Pokemon:
    return max(pokemons, key=lambda mon: mon.attack_stat)


def highest_defense(pokemons: Iterable[Pokemon]) -> Pokemon:
    return max(pokemons, key=lambda mon: mon.defense_stat)


def highest_stamina(pokemons: Iterable[Pokemon]) -> Pokemon:
    return max(pokemons, key=lambda mon: mon.stamina_stat)


def lowest_attack(pokemons: Iterable[Pokemon]) -> Pokemon:
    return min(pokemons, key=lambda mon: mon.attack_stat)


def lowest_defense(pokemons: Iterable[Pokemon]) -> Pokemon:
    return min(pokemons, key=lambda mon: mon.defense_stat)


def lowest_stamina(pokemons: Iterable[Pokemon]) -> Pokemon:
    return min(pokemons, key=lambda mon: mon.stamina_stat)


def format_attack_range(pokemons: Iterable[Pokemon]) -> str:
    lowest = f"{lowest_attack(pokemons).attack_stat:.2f}"
    highest = f"{highest_attack(pokemons).attack_stat:.2f}"

    return f"{lowest} - {highest} attack"


def format_defense_range(pokemons: Iterable[Pokemon]) -> str:
    lowest = f"{lowest_defense(pokemons).defense_stat:.2f}"
    highest = f"{highest_defense(pokemons).defense_stat:.2f}"

    return f"{lowest} - {highest} defense"


def format_stamina_range(pokemons: Iterable[Pokemon]) -> str:
    lowest = f"{lowest_stamina(pokemons).stamina_stat:d}"
    highest = f"{highest_stamina(pokemons).stamina_stat:d}"

    return f"{lowest} - {highest} stamina"


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
