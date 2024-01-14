# Pokemon GO PVP breakpoint calculator
This is a program for *efficiently* computing breakpoints and bulkpoints in Pokemon GO PVP.

**What are breakpoints/bulkpoints?** ...

Computing these efficiently is challenging. There are lots of dimensions of possibilities:
 - attacker species, level, and IVs
 - defender species, level, and IVs
 - CP limit (except in Master)
 - fast move choice
 - stat buffs and debuffs

This project considers stat buffs & debuffs to be out of scope.
This project also fixes analyses to _either_ one attacker _or_ one defender.

**What about PVPoke?** PVPoke is fantastic. I love using it.
I referred to its [source code](https://github.com/pvpoke/pvpoke/) a lot, studying how it computed damage and implemented different Pokemon's data.
I owe a lot to its creator, Empoleon_Dynamite, and I'm grateful for this.

With all that said - PVPoke is really only a good fit for one-to-one breakpoint analyses.
In a given battle, it can tell you if the attacker is near an attack breakpoint - if the attacker can do extra fast move damage.
Likewise, it can tell you if the defender being slightly bulkier would *reduce* fast move damage.

But that's only good for one attacker vs. one defender.
PVPoke isn't really built to let us ask questions like:
 - What IVs should my Jellicent have to reach bulkpoints against the top 20 ULP Pokemon?
 - What IVs should my Altaria have to do extra Dragonbreath damage against the GL meta?

**Being able to compute these efficiently is the goal of this project.**

**How much does this matter?
I'll also say that these aren't _really_ that important overall.
Breakpoints matter a LOT in Master League, where having perfect IVs is practically a requirement.
But in the other leagues they're far less relevant.
Nonetheless, for one-turn fast moves (like Dragonbreath they can make a big difference, and on
Community Day it can be useful to know which IV spreads to look for.

## Development
This project uses Python 3.12 and manages dependencies with Poetry.

- Install dependencies: `poetry install`
- Run tests: `(poetry run) pytest`
- Update the gamemaster file: `(poetry run) python scripts/fetch_data.py`
