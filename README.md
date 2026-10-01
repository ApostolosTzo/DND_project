# D&D RPG

A browser-based Dungeons & Dragons-style RPG. Features a world map, dungeon crawling, turn-based combat, character progression with a flexible skill point system, and NPC shops.

It runs two ways: as a **Flask web app** (Python backend) or as a **static Progressive Web App** that installs to your phone/desktop and plays fully offline.

## Current Features

- **Character creation** — choose race (Human/Elf/Dwarf/Halfling) and class (Fighter/Rogue/Wizard/Cleric), stats rolled via 4d6-drop-lowest
- **Forgiving start** — every class gets +5 base HP and a full pack of 15 Healing Potions
- **Loot** — kills pay 40% more XP and 60% more gold
- **Turn-based combat** — attack, use items, or flee against level-scaled enemies (no fleeing in dungeon)
- **9 enemy types** — Zombie, Skeleton, Spider, Wolf, Goblin, Slime, Ghost, plus Demon Lord and Elder Dragon (bosses only)
- **Skill point leveling** — 1 skill point per level, 5 points on levels 4/8/12/…, freely distribute across all 6 stats
- **Stat effects** — STR (melee damage), DEX (ranged/finesse damage + AC), CON (max HP), INT/WIS/CHA (placeholder)
- **Equipment with stat bonuses** — weapons and armor can boost STR/DEX/CON/INT, affecting damage, AC, and HP
- **AC calculation** — light (DEX), medium (DEX capped at 2), heavy (no DEX), shield (+2)
- **NPC shops** — 5 NPCs: Potion Merchant, Weaponsmith, Armorer, Archer, Wizard; availability varies by location. Tap an item to expand an inline panel showing what it gives you (damage, properties, stat bonuses, AC change) with a one-tap **Buy** button
- **Interactive world map** — an illustrated map with forests, mountains, a river and curved roads; clickable nodes to travel between Town, Village 1, Village 2, and Dungeon
- **Monster portraits** — original hand-drawn SVG for all 9 monsters; they lurch when hit and distort as they lose HP
- **30+ items** — weapons, armors, shields, potions, scrolls, magical items
- **Interactive world map** — clickable nodes to travel between Town, Village 1, Village 2, and Dungeon
- **10-floor dungeon** — progressive enemy scaling, potion merchant on floor 5, boss fight on floor 10
- **Boss encounters** — Demon Lord and Elder Dragon only appear on dungeon floor 10
- **Multi-save JSON system** — save/load with overwrite confirmation
- **Combat item grouping** — duplicate items shown as "Name xN" in combat inventory

## How to Run

### Option A - Static PWA (no server, works on GitHub Pages)

```bash
python -m http.server 8000
```

Then open **http://localhost:8000**. All game logic runs in the browser, so any static host works — including GitHub Pages.

### Option B - Flask app (Python backend)

```bash
pip install flask
python game_server.py
```

OR

(Windows Python Launcher)
```bash
py -m pip install flask
py ./game_server.py
```

Then open **http://localhost:5000** in your browser.

## Install as an App (PWA)

The static version is a full PWA: it caches itself for offline play and can be installed to a home screen / desktop.

1. Deploy the repo to GitHub Pages: **Settings → Pages → Source: Deploy from a branch → Branch: `main` / `root`**.
   All asset paths are relative, so it works both at `https://<user>.github.io/` and `https://<user>.github.io/<repo>/`.
2. Open the site in a browser (it must be HTTPS — GitHub Pages is automatically).
3. **Android / Chrome:** menu → *Add to Home screen*. **iOS / Safari:** Share → *Add to Home Screen*. **Desktop Chrome/Edge:** install icon in the address bar.
4. Launch it — it works with no connection, and saves persist in the browser (localStorage).

> **Saves are device-local.** Each browser on each device keeps its own characters — a save is not synced or backed up. It survives closing the app, rebooting and being offline, but it is **wiped** by "Clear cookies and site data" (and by uninstalling the app on Android), and it does not follow you to another device or browser.

Files that make it a PWA:

| File | Purpose |
|---|---|
| `manifest.json` | App name, colours, display mode, icon set |
| `sw.js` | Service worker: pre-caches the app, serves it offline |
| `icons/` | 192 / 512 / maskable / apple-touch icons (placeholders) |

### Replacing the placeholder icon

The current icons are generated placeholders (gold diamond on the dark theme colour). Overwrite these files with your own art, keeping the same names and sizes:

```
icons/icon-192.png           # 192x192
icons/icon-512.png           # 512x512
icons/icon-maskable-512.png   # 512x512, art inside the middle 80% circle
icons/apple-touch-icon.png   # 180x180
```

After changing them, bump `CACHE_VERSION` in `sw.js` (e.g. `dnd-pwa-v2`) so returning visitors pick up the new icons.

## Controls

Click the on-screen buttons to navigate. No keyboard input needed.

Keyboard shortcuts (desktop, optional): `1`–`9` pick an option directly, `↑`/`↓` move the highlight and `Enter` selects it.

## Character Options

Stats are rolled first with **4d6-drop-lowest** (each stat lands on 3–18), then the race bonus is applied on top.

### Races

| Race | STR | DEX | CON | INT | WIS | CHA | Description |
|---|---|---|---|---|---|---|---|
| Human | +1 | +1 | +1 | +1 | +1 | +1 | Versatile and ambitious |
| Elf | — | +2 | — | +1 | — | — | Graceful and perceptive |
| Dwarf | +1 | — | +2 | — | — | — | Tough and resilient |
| Halfling | — | +2 | — | — | — | +1 | Lucky and nimble |

### Classes

| Class | Base HP | HP per level | Primary stat | Starting weapon | Starting armor | Potions |
|---|---|---|---|---|---|---|
| Fighter | 15 | +4 | STR | Longsword (+1 STR) | Chainmail (medium) | 15 × Healing Potion |
| Rogue | 13 | +3 | DEX | Dagger (+1 DEX) | Leather (light) | 15 × Healing Potion |
| Wizard | 11 | +2 | INT | Magic Staff | *none* | 15 × Healing Potion |
| Cleric | 13 | +3 | WIS | Mace (+1 STR) | Plate (heavy) | 15 × Healing Potion |

Every class begins with a **full pack of 15 Healing Potions**, so the first monster is a warm-up rather than a coin flip.

### Starting health and armour class

| Class | HP at level 1 | AC range | AC formula |
|---|---|---|---|
| Fighter | 15 + CON mod | 14 – 16 | `14 + min(DEX mod, 2)` — Chainmail is medium, DEX capped at +2 |
| Rogue | 13 + CON mod | 8 – 17 | `11 + DEX mod` — Leather is light, and the Dagger's +1 DEX counts |
| Wizard | 11 + CON mod | 7 – 16 | `10 + DEX mod` — no armour, so full DEX applies |
| Cleric | 13 + CON mod | 17 (flat) | `17` — Plate is heavy, DEX is ignored |

`CON mod = floor((CON - 10) / 2)` and `DEX mod = floor((DEX - 10) / 2)`.
A CON point raises max HP **and heals you to full** when you spend it.

### What each stat does

| Stat | Effect | Formula |
|---|---|---|
| **STR** | Melee attack rolls & damage | `STR mod` added to the attack roll and to damage |
| **DEX** | Ranged/finesse attack & damage, **Armour Class** | See the AC formulas above |
| **CON** | **Max HP** | Each CON modifier point adds `+1 HP per level` |
| **INT** | *No effect yet* — reserved for Wizard spells | — |
| **WIS** | *No effect yet* — reserved for Cleric spells | — |
| **CHA** | *No effect yet* | — |

### Levelling

| Event | Effect |
|---|---|
| XP to reach the next level | `level × 100` |
| HP on level up | class HP per level **+2 per CON modifier point**, then healed to full |
| Gold on level up | `new level × 10` |
| Skill points | +1 per level, **+5 extra** on levels 4, 8, 12, … |
| Spending a skill point | +1 to any stat; CON also raises max HP and heals to full |

### Combat rewards

Kills pay out **40% more XP and 60% more gold** than the original tuning (the multipliers are `XP_REWARD_MULTIPLIER = 1.4` and `GOLD_REWARD_MULTIPLIER = 1.6` in `enemy.py` / `js/enemy.js`, so you can retune in one place).

| Monster | Base XP | Base gold | XP at Lv.1 | Gold at Lv.1 | XP at Lv.5 | Gold at Lv.5 |
|---|---|---|---|---|---|---|
| Goblin | 30 | 8 | 21 | 12 | 105 | 64 |
| Spider | 50 | 4 | 35 | 6 | 175 | 32 |
| Slime | 40 | 3 | 28 | 4 | 140 | 24 |
| Zombie / Skeleton / Wolf | 50 | 5 – 6 | 35 | 8 – 9 | 175 | 40 – 48 |
| Ghost | 80 | 10 | 56 | 16 | 280 | 80 |
| Demon Lord (boss) | 200 | 50 | 140 | 80 | 700 | 400 |
| Elder Dragon (boss) | 250 | 80 | 175 | 128 | 875 | 640 |

`XP = base XP × level ÷ 2 × 1.4`, `gold = base gold × level × 1.6`, both rounded to whole numbers. Clearing the dungeon still adds a flat **+500 gold / +500 XP** boss bonus on floor 10.

### Equipment stat bonuses

| Item | Bonus |
|---|---|
| Longsword, Battle Axe, War Hammer, Mace, Flail, Spear, Quarterstaff | +1 STR |
| Greatsword | +2 STR |
| Rapier, Dagger, Shortbow, Longbow, Crossbow, Hand Crossbow | +1 DEX |
| Studded Leather | +1 DEX |
| Arcane Staff | +1 INT |
| Wizard Robe | +9 INT ⚠️ |
| Dragon Scale | +8 CON ⚠️ |

> ⚠️ Those last two look like typos in the item data (+9 INT / +8 CON instead of +1). They are reproduced exactly as the game data has them, so Wizard Robe adds +4 to INT's modifier and Dragon Scale adds +4 CON per level. Worth fixing in `items.py` **and** `js/items.js`.

### Colour palette

| Role | Colour |
|---|---|
| Page background | `#0b0b0c` near-black |
| Panels, cards, log | `#151517` / `#1e1e21` / `#0e0e0f` dark grey |
| Borders and dividers | `#2e2e33` |
| Body text | `#d6d6d6` light grey |
| Muted text (log, hints) | `#8a8a8a` |
| **Gold** — titles, borders, XP bar, map town | `#c9a84c` (hover `#dbb95c`) |
| **Emerald** — HP bar, map villages, village labels | `#2fbf71` (light `#5fd39a`) |
| Red — enemy HP bar and danger states | `#c0392b` / `#e74c3c` |

The nine monster portraits keep their own colours (they are creatures, not chrome), and the PWA theme colour, manifest background and app icons all use the same near-black `#0b0b0c`.

## Tech Stack

- Python 3
- Flask
- JSON save files
- Vanilla JavaScript (static PWA build)
- Service Worker + Web App Manifest (offline / installable)
- SVG (world map)

## Project Structure

```
DND_project/
├── index.html           # PWA client (static build, GitHub Pages entry point)
├── manifest.json        # Web app manifest (name, icons, colours)
├── sw.js                # Service worker (offline cache)
├── .nojekyll            # Tells GitHub Pages not to run Jekyll
├── js/                  # Game logic ported from Python, runs in the browser
│   ├── dice.js          # Dice roller (NdX+Y)
│   ├── items.js         # Weapons, armor, shields, potions
│   ├── enemy.js         # Enemy templates, bosses, scaling
│   ├── player.js        # Character creation, stats, leveling
│   ├── shop.js          # NPC shop definitions
│   ├── world_map.js     # Locations and connections
│   ├── saves.js         # Save/load (localStorage instead of JSON files)
│   └── game.js          # Game state machine (port of game_server.py)
├── icons/               # PWA icons (placeholder art)
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
│   └── index.html       # Browser UI for the Flask build
└── saves/               # Save files directory (Flask build only)
```

The Python files power the Flask build (`python game_server.py`); `js/` is a port of them so the same game runs as a static PWA. Change both when you change game rules.

## Planned Features

- Quest system (objectives and rewards)
- Crafting system (craft from enemy drops)
- More items, races, classes
- Skills in combat (special abilities)
- Sell back items to shops
- Difficulty scaling options
