# Coalition Demands

EU5 mod, on the Steam Workshop: https://steamcommunity.com/sharedfiles/filedetails/?id=3824375558

Coalitions take back what you conquered instead of humiliating you: a Return Conquests peace treaty gives recent
conquests back to the countries they were taken from (members, neighbours under a truce, destroyed countries brought
back), frees recent vassals and takes off the antagonism those conquests caused. Rivals, near hegemons and the Emperor
may join coalitions, the strongest member leads the war, and Dissolve Coalition removes 75% of the losers' antagonism.
Settings in the Community Mod Framework mod menu (required).

## Files

- `src/`: the mod's own files, copied as they are.
- `build.py`: builds the local mod folder (`Documents/Paradox Interactive/Europa Universalis V/mod/coalition_demands`):
  copies `src/`, patches the game files the mod changes (the `PATCHES` table; the build stops if a game patch changed
  one of them), writes the localization and the metadata.
- `description.txt`: the Workshop description.
- `make_cover.py`: builds `cover.png` (the Workshop preview) from `cover_full.png` (in the page's gallery).
