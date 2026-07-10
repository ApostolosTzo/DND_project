# D&D Terminal Game

A work-in-progress Dungeons & Dragons-style RPG that runs in the terminal (Python) or in a browser (Flask).

## Project Status

This project is **under active development**. Expect frequent changes, incomplete features, and rough edges.

## Current Features

- **Character creation** — choose race (Human/Elf/Dwarf/Halfling) and class (Fighter/Rogue/Wizard/Cleric), stats rolled via 4d6-drop-lowest
- **Turn-based combat** — attack, use items, or flee against level-scaled enemies
- **7 enemy types** — Zombie, Skeleton, Spider, Wolf, Goblin, Slime, Ghost (levels 1–100)
- **Leveling system** — XP-based leveling with stat boosts every 4 levels
- **Equipment** — weapons and armor with AC calculation (light/medium/heavy)
- **NPC shops** — 5 shops: Potion Merchant, Weaponsmith, Armorer, Archer, Wizard
- **30+ items** — weapons, armors, shields, potions, scrolls, magical items
- **Item stat bonuses** — equipment can boost STR, DEX, CON, INT, etc., affecting damage, AC, and HP
- **Save/Load** — multi-save JSON system with overwrite protection
- **World map** — visual SVG map showing town, villages, and dungeon connections (browser version)

## Planned Features

- **Dungeon floors** — each dungeon has multiple floors with enemies, final floor has a boss
- **Interactive map locations** — clickable towns, villages, and dungeons
- **Quest system** — quest lines with objectives and rewards
- **Quest system** — quest lines with objectives and rewards
- **Crafting system** — craft items using drops from enemies
- **More items** — expanded weapons, armors, potions, and materials
- **More races & classes** — additional character options
- **Skills in combat** — special abilities and skill actions
- **More potions** — variety of consumables beyond healing

## How to Run

### Terminal version

```bash
py main.py
```

### Browser version

```bash
pip install flask
py run_server.py
```

Then open **http://localhost:5000** in your browser.

## Controls (Terminal)

- **Arrow keys** (↑/↓) — navigate menus
- **Enter** — select option
- **Typed input** — character name, save names

## Tech Stack

- Python 3
- Flask (web version)
- JSON save files

## Project Structure

```
DND_project/
├── main.py              # Terminal entry point
├── game_server.py       # Flask web server
├── run_server.py        # Server launcher
├── player.py            # Character creation, stats, leveling
├── combat.py            # Turn-based combat
├── enemy.py             # Enemy templates and scaling
├── items.py             # Weapons, armor, potions
├── inventory.py         # Inventory management
├── shop.py              # NPC shops
├── dice.py              # Dice rolling engine
├── save_load.py         # Multi-save JSON system
├── ui.py                # Terminal UI utilities
├── templates/
│   └── index.html       # Browser UI
└── saves/               # Save files
```
