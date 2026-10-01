# D&D RPG

A browser-based Dungeons & Dragons-style RPG. Features a world map, dungeon crawling, turn-based combat, character progression with a flexible skill point system, and NPC shops.

It runs two ways: as a **Flask web app** (Python backend) or as a **static Progressive Web App** that installs to your phone/desktop and plays fully offline.

## Current Features

- **Character creation** — choose race (Human/Elf/Dwarf/Halfling) and class (Fighter/Rogue/Wizard/Cleric), stats rolled via 4d6-drop-lowest
- **Forgiving start** — every class gets +5 base HP and a full pack of 15 Healing Potions
- **Loot** — kills pay 40% more XP and 60% more gold
- **Selling** — sell any item to any NPC for 20% under the shop price; the game warns you before you sell your last weapon or armour
- **Repeatable quests** — three randomly-named quest givers in Town trade gold and XP for monster materials
- **Monster drops** — 7 materials dropped by the creatures that carry them (used for quests)
- **Turn-based combat** — attack, use items, or flee against level-scaled enemies (no fleeing in dungeon)
- **Running combat log** — every exchange stays in the chat, so you can read back through a whole fight
- **9 enemy types** — Zombie, Skeleton, Spider, Wolf, Goblin, Slime, Ghost, plus Demon Lord and Elder Dragon (bosses only)
- **Monster portraits** — original hand-drawn SVG for all 9 monsters; they lurch when hit and distort as they lose HP
- **Skill point leveling** — 1 skill point per level, 5 points on levels 4/8/12/…, freely distribute across all 6 stats
- **Stat effects** — STR (melee damage), DEX (ranged/finesse damage + AC), CON (max HP), INT/WIS/CHA (placeholder)
- **Equipment with stat bonuses** — weapons and armor can boost STR/DEX/CON/INT, affecting damage, AC, and HP
- **AC calculation** — light (DEX), medium (DEX capped at 2), heavy (no DEX), shield (+2)
- **NPC shops** — 5 NPCs: Potion Merchant, Weaponsmith, Armorer, Archer, Wizard; availability varies by location. Tap an item to expand an inline panel showing what it gives you (damage, properties, stat bonuses, AC change) with a one-tap **Buy** button
- **Interactive world map** — an illustrated map with forests, mountains, a river and curved roads; clickable nodes to travel between Town, Village 1, Village 2, and Dungeon. It gets out of the way while you fight
- **Mobile-friendly UI** — single-column layout, big tap targets and safe-area padding on phones
- **109 items** — 48 weapons, 49 armors/shields, potions, scrolls, magical items and quest materials
- **10-floor dungeon** — progressive enemy scaling, potion merchant on floor 5, boss fight on floor 10
- **Boss encounters** — Demon Lord and Elder Dragon only appear on dungeon floor 10
- **Multi-save system** — save/load with overwrite confirmation; JSON files in the Flask build, `localStorage` in the PWA
- **Combat item grouping** — duplicate items shown as "Name xN" in combat inventory

## How to Run

### Static PWA (no server, works on GitHub Pages)

```bash
python -m http.server 8000
```

Then open **http://localhost:8000**. All game logic runs in the browser, so any static host works — including GitHub Pages.





> Use the **`py`** launcher, not a bare `python`. On Windows, `python` on `PATH`
> is often a different interpreter (an MSYS2 build here) that has no pip and no
> Flask, which fails with `ModuleNotFoundError: No module named 'flask'`. If you
> prefer the plain command, install Flask into whatever `python` resolves to and
> make sure that's a full CPython, not the MSYS2 one.

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

After changing them, bump `CACHE_VERSION` in `sw.js` (e.g. `dnd-pwa-v5`) so returning visitors pick up the new icons.

> The cached files include everything under `js/`, and those are served **cache-first**. Bump `CACHE_VERSION` whenever you change `js/*.js` — otherwise players keep running the old game code even though the HTML updates.

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

### Selling items

Every NPC buys items at **20% under the cheapest price that item sells for** (`SELL_RATIO = 0.8` in `shop.py` / `js/shop.js` — change it in one place to retune).

- Open any shop and switch to the **Sell** tab; equipped gear is listed too, marked *(equipped)*
- The price shown is what you will actually receive
- **Quest materials cannot be sold** — they are only worth turning in
- Selling your **last weapon** or **last piece of armour** pops a warning with **Continue / Cancel**, because you will be left with nothing equipped
- Selling equipped gear recomputes your AC and max HP immediately

### Monster drops

Kills drop quest materials (75% chance, 1–3 pieces). `DROPS` in `enemy.py` / `js/enemy.js`:

| Monster | Drops |
|---|---|
| Goblin | Metal Fragments |
| Spider | Web String |
| Slime | Slime Ball |
| Zombie | Rotten Flesh |
| Skeleton | Bone |
| Wolf | Fur |
| Ghost | Plasma |
| Demon Lord / Elder Dragon | *nothing yet* — ideas below |

### Quests (Town only)

Three quest givers stand in Town, with **randomly generated names** each new run (e.g. *Nell the Wandering Scribe*). Every quest is **repeatable**: accept it once, then hand in as many batches as you like.

| Quest giver | Wants | Pays |
|---|---|---|
| Alchemist | Plasma ×8 | 260g, 140 XP |
| Alchemist | Slime Ball ×8 | 220g, 120 XP |
| Bone Collector | Bone ×10 | 300g, 160 XP |
| Bone Collector | Rotten Flesh ×8 | 200g, 110 XP |
| Trapper | Fur ×10 | 280g, 150 XP |
| Trapper | Web String ×8 | 210g, 115 XP |
| Trapper | Metal Fragments ×10 | 320g, 170 XP |

Flow: **Town → Quests → pick an NPC → [Accept]** → kill the right monsters → **return to the same NPC** → `[Turn in]`. Quest XP can level you up; if it does, you finish allocating points back at the NPC rather than being dropped in Town.

### Boss drop ideas (not implemented)

For when you decide what the bosses should drop:

| Boss | Idea | Why it fits |
|---|---|---|
| Demon Lord | **Demon Heart** — +3 CON, one-shot quest item | A trophy-tier quest material nobody else can farm |
| Demon Lord | **Obsidian Shard** — craft-only (for later) | Fits your "no crafting yet" rule; pure loot |
| Demon Lord | **Hellfire Core** — weapon that adds fire damage | Consumable-looking, feeds a magic-weapon line |
| Elder Dragon | **Dragon Scale** — already an armour in the catalogue | Reuse existing item instead of adding one |
| Elder Dragon | **Ancient Coin Hoard** — 1000–1500g | Straight gold sink-reward for the hardest fight |
| Elder Dragon | **Breath of the Wyrm** — single-use fireball scroll | Turns the boss into the source of a powerful consumable |

The hook already exists: add the item to `ITEMS`, map it in `DROPS`, and (if it is a quest material) add a quest. No new code needed.

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
│   ├── items.js         # Weapons, armor, shields, potions, quest materials
│   ├── enemy.js         # Enemy templates, bosses, scaling, drops
│   ├── player.js        # Character creation, stats, leveling
│   ├── quests.js        # Quest givers and quest definitions
│   ├── shop.js          # NPC shop definitions + sell prices
│   ├── world_map.js     # Locations and connections
│   ├── saves.js         # Save/load (localStorage instead of JSON files)
│   └── game.js          # Game state machine (port of game_server.py)
├── icons/               # PWA icons (placeholder art)
├── game_server.py       # Flask web server (all game logic)
├── run_server.py        # Alternative launcher: py run_server.py
├── quests.py            # Repeatable quest givers (Town only)
├── enemy.py             # Enemy templates, bosses, scaling, drops
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

The Python files power the Flask build (`py ./game_server.py`); `js/` is a port of them so the same game runs as a static PWA. Change both when you change game rules.

## Working on the Code

This repo holds **two implementations of one game**, so a few rules keep them honest:

| Rule | Why |
|---|---|
| Change game rules in **both** `*.py` and `js/*.js` | The Flask build and the PWA build ship side by side; a one-sided change makes them disagree |
| New items: define in `items.py` **and** `js/items.js`, sell in `shop.py` **and** `js/shop.js` | If a shop lists an item the catalogue doesn't define, `create_item()` returns `None`, `None` lands in the inventory and the inventory/shop screen throws. A guard turns this into a harmless *"That item is not available."*, but the right fix is to add it to all four files |
| Quests live in `quests.py` **and** `js/quests.js`; drops in `DROPS` in `enemy.py` **and** `js/enemy.js` | Same duplication — both files must agree or the two builds diverge |
| The world map lives in `world_map.py` **and** `js/world_map.js` | Both builds read location coordinates and connections from them |
| Bump `CACHE_VERSION` in `sw.js` when `js/*.js` changes | Those files are cached cache-first; without a bump, returning players keep the old code |
| `templates/index.html` and the root `index.html` both contain the map renderer | The renderer is self-contained (its CSS sits in an SVG `<style>` block) so the block can be copied between them verbatim — keep them in step |

`PROGRESS.md` is the running changelog: what changed, why, the bug chains, and post-mortems.

## Planned Features

- **Export / import saves** so characters can be backed up and moved between devices
- Quest system (objectives and rewards)
- Crafting system (craft from enemy drops)
- More items, races, classes
- Skills and spells in combat (INT/WIS are currently placeholders)
- Sell back items to shops
- Difficulty scaling options
- Possibly: a minimum starting-HP floor or a heal between fights — see the death-rate table in `PROGRESS.md`
