# D&D RPG

A browser-based Dungeons & Dragons-style RPG built with Flask. Features a world map, dungeon crawling, turn-based combat, character progression with a flexible skill point system, and NPC shops.

## Current Features

- **Character creation** — choose race (Human/Elf/Dwarf/Halfling) and class (Fighter/Rogue/Wizard/Cleric), stats rolled via 4d6-drop-lowest
- **Turn-based combat** — attack, use items, or flee against level-scaled enemies (no fleeing in dungeon)
- **9 enemy types** — Zombie, Skeleton, Spider, Wolf, Goblin, Slime, Ghost, plus Demon Lord and Elder Dragon (bosses only)
- **Skill point leveling** — 1 skill point per level, 5 points on levels 4/8/12/…, freely distribute across all 6 stats
- **Stat effects** — STR (melee damage), DEX (ranged/finesse damage + AC), CON (max HP), INT/WIS/CHA (placeholder)
- **Equipment with stat bonuses** — weapons and armor can boost STR/DEX/CON/INT, affecting damage, AC, and HP
- **AC calculation** — light (DEX), medium (DEX capped at 2), heavy (no DEX), shield (+2)
- **NPC shops** — 5 NPCs: Potion Merchant, Weaponsmith, Armorer, Archer, Wizard; availability varies by location
- **30+ items** — weapons, armors, shields, potions, scrolls, magical items
- **Interactive world map** — clickable nodes to travel between Town, Village 1, Village 2, and Dungeon
- **10-floor dungeon** — progressive enemy scaling, potion merchant on floor 5, boss fight on floor 10
- **Boss encounters** — Demon Lord and Elder Dragon only appear on dungeon floor 10
- **Multi-save JSON system** — save/load with overwrite confirmation
- **Combat item grouping** — duplicate items shown as "Name xN" in combat inventory

## How to Run

```bash
pip install flask
python game_server.py
```

Then open **http://localhost:5000** in your browser.

## Controls

Click the on-screen buttons to navigate. No keyboard input needed.

## Tech Stack

- Python 3
- Flask
- JSON save files
- SVG (world map)

## Project Structure

```
DND_project/
├── game_server.py       # Flask web server (all game logic)
├── enemy.py             # Enemy templates, bosses, scaling
├── player.py            # Character creation, stats, leveling
├── items.py             # Weapons, armor, shields, potions
├── shop.py              # NPC shop definitions
├── world_map.py         # Location definitions and connections
├── dice.py              # Dice rolling engine
├── save_load.py         # Multi-save JSON system
├── inventory.py         # Inventory management (terminal, unused)
├── combat.py            # Combat (terminal, unused)
├── ui.py                # Terminal UI utilities (kept for imports)
├── PROGRESS.md          # Development changelog and analysis
├── templates/
│   └── index.html       # Browser UI
└── saves/               # Save files directory
```

## Planned Features

- Quest system (objectives and rewards)
- Crafting system (craft from enemy drops)
- More items, races, classes
- Skills in combat (special abilities)
- Sell back items to shops
- Difficulty scaling options
