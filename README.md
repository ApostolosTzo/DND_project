# D&D RPG

A browser-based Dungeons & Dragons-style RPG. Features a world map, dungeon crawling, turn-based combat, character progression with a flexible skill point system, and NPC shops.

It runs two ways: as a **Flask web app** (Python backend) or as a **static Progressive Web App** that installs to your phone/desktop and plays fully offline. That means the same game exists twice in this repo — once in Python, once in JavaScript. [Why both exist](#why-there-are-two-builds) explains where that came from and what it means for you.

## Why there are two builds

This repo contains **one game, implemented twice**:

| | Python build | JavaScript build |
|---|---|---|
| Files | `*.py` in the root | `js/*.js` |
| Needs a server | **Yes** — Flask runs on a machine | **No** — pure static files |
| Runs at | `http://localhost:5000` | `https://dnd-project-ekf.pages.dev` |
| Installs to a phone | No | **Yes**, as a Progressive Web App |
| Plays offline | Only while the server is running | **Yes**, fully |
| Saves go | JSON files in `saves/` | `localStorage` in the browser |
| This is | the development build | **the deployed game** |

### Why it ended up this way

The game started as a Python console project, then grew a Flask server so it could run in a browser. The natural next step was to put it online and install it on a phone.

**That is where the split happened.** Static hosts — Cloudflare Pages, and GitHub Pages before it — can only serve files. They cannot run Python. A site like that has no backend, so a Flask app cannot be deployed there at all; it would need a separate paid server that stays running.

So the game logic was **ported once into JavaScript**. `js/game.js` is `game_server.py` running in the browser, `js/items.js` is `items.py`, and so on. Same rules, same numbers, same catalogue — just no server. Each file is named after the Python file it replaces, and its first line says so:

```js
// items.py - Weapon / Armor / Item definitions, catalog and starting gear.
```

| JavaScript | Replaces | Lines |
|---|---|---|
| `js/game.js` | `game_server.py` — the whole state machine | 1177 |
| `js/items.js` | `items.py` — the catalogue | 319 |
| `js/player.js` | `player.py` — stats, equipment, off-hand rules | 257 |
| `js/enemy.js` | `enemy.py` — monsters, damage types, status effects | 251 |
| `js/shop.js` | `shop.py` — NPC stock and prices | 155 |
| `js/saves.js` | `save_load.py` — multi-save | 97 |
| `js/quests.js` | `quests.py` | 64 |
| `js/dice.js` | `dice.py` | 46 |
| `js/world_map.js` | `world_map.py` | 36 |

`index.html` loads those nine files with `<script>` tags in that order, then draws the game on screen.

### Why keep the Python version at all?

Three reasons, in order of importance:

1. **The Python build is where changes are easiest to make and test.** It runs with one command and no browser involved, which makes it the quickest place to try a rule out.
2. **It is a working fallback.** If the browser build ever breaks badly, `py ./game_server.py` still gives you the whole game in a browser tab.
3. **It is the original.** Half the design decisions in `PROGRESS.md` were made against it, so keeping it means the history of the game stays readable.

The JavaScript build is the one that ships, but the Python is maintained alongside it rather than abandoned.

### The cost: changes must be made twice

This is the real cost of the arrangement, and it is worth understanding before you edit anything. **A change to the game rules usually needs writing in both places.** Add a sword in `items.py` and it does not exist in the game anyone plays.

The dangerous cases are silent rather than loud. A shop listing an item the catalogue doesn't define does not crash — a guard turns it into *"That item is not available."* and the player just cannot buy the thing. A new stat that only exists in Python is a stat that silently does nothing in the deployed game.

Because of this, every change is checked with a **parity script** that compares all 114 items field by field between `items.py` and `js/items.js`, plus both shop definitions and both location graphs. Any drift is reported as a list of differences rather than failing on the first one.

### Which one should you edit?

**Both.** See [Working on the Code](#working-on-the-code) for the specific files to touch. The short version:

| You want to change | Edit |
|---|---|
| An item or its stats | `items.py` **and** `js/items.js` |
| What an NPC sells | `shop.py` **and** `js/shop.js` |
| A monster or a damage rule | `enemy.py` **and** `js/enemy.js` |
| Stats, HP, AC, equipping | `player.py` **and** `js/player.js` |
| A quest | `quests.py` **and** `js/quests.js` |
| The map | `world_map.py` **and** `js/world_map.js` |
| How a fight resolves | `game_server.py` **and** `js/game.js` |
| How the screen looks | `index.html` **and** `templates/index.html` |
| Offline caching | `sw.js` only — the Python build has no offline mode |

> **Always bump `CACHE_VERSION` in `sw.js` after editing anything in `js/`.** Those files are cached cache-first by the service worker, so without a bump returning players — your phone — keep running the old code even after the new one has deployed. That single line is the whole update mechanism for game-code changes.

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
- **Stat effects** — STR (melee damage), DEX (ranged/finesse damage, AC, poison chance), CON (max HP), INT (burn damage, freeze duration). WIS/CHA are still placeholders
- **Equipment with stat bonuses** — weapons and armor can boost STR/DEX/CON/INT, affecting damage, AC, and HP
- **AC calculation** — light (DEX), medium (DEX capped at 2), heavy (no DEX), shield (+2)
- **Damage types matter** — slashing, bludgeoning, piercing, fire, ice, lightning, dark, force and poison. Every monster is weak to some (x1.5) and resists others (x0.5)
- **Two hands** — a two-handed weapon needs both, so it cannot be paired with a shield; it also hits harder (Longsword +1, Greatsword +1, Maul +2). A one-handed weapon frees the off-hand for a shield or a second weapon
- **Elemental weapons** — fire sets the target alight for 2 rounds (INT scales), ice freezes it solid so it loses its turn (INT scales the duration), poison has a DEX-scaled chance to land and ticks until the monster dies
- **NPC shops** — 6 NPCs: Potion Merchant, Weaponsmith, Armorer, Shield Smith, Archer, Wizard; availability varies by location. Tap an item to expand an inline panel showing what it gives you (damage, properties, stat bonuses, AC change) with a one-tap **Buy** button. Potions add a quantity stepper (1/5/10/20/Max)
- **A Shield Smith** — all 11 shields are sold by one dedicated NPC and nowhere else
- **Interactive world map** — an illustrated map with forests, mountains, a river and curved roads; clickable nodes to travel between Town, Village 1, Village 2, and Dungeon. It gets out of the way while you fight
- **Mobile-friendly UI** — single-column layout, big tap targets and safe-area padding on phones
- **114 items** — 50 weapons, 49 armors/shields, 5 potion tiers, scrolls, magical items and quest materials
- **10-floor dungeon** — progressive enemy scaling, potion merchant on floor 5, boss fight on floor 10
- **Boss encounters** — Demon Lord and Elder Dragon only appear on dungeon floor 10
- **Multi-save system** — save/load with overwrite confirmation; JSON files in the Flask build, `localStorage` in the PWA
- **Combat item list** — every item you carry is listed during a fight, strongest healing potion first and quest drops included; unusable ones are greyed out
- **Five potion tiers** — 9 / 20 / 100 / 300 / 800 HP, the last three unlocking at levels 15, 35 and 70
- **Inventory panels** — tapping an item shows its stats and an Equip or Use button instead of using it on the spot
- **Top-left back button** — every screen's Back/Close lives in the corner rather than at the bottom of the list

## How to Run

### Option A — the PWA (static, no server)

```bash
python -m http.server 8000
```

Then open **http://localhost:8000**. All game logic runs in the browser, so
any static host works — this one is deployed on **Cloudflare Pages**.

### Option B — Flask app (Python backend)

```bash
py -m pip install flask     # once
py ./game_server.py
```

Then open **http://localhost:5000** in your browser.

> Use the **`py`** launcher, not a bare `python`. On Windows, `python` on `PATH`
> is often a different interpreter (an MSYS2 build here) that has no pip and no
> Flask, which fails with `ModuleNotFoundError: No module named 'flask'`. If you
> prefer the plain command, install Flask into whatever `python` resolves to and
> make sure that's a full CPython, not the MSYS2 one.

## Deploying (Cloudflare Pages)

The live game:

```
https://dnd-project-ekf.pages.dev
```

It is a **Cloudflare Pages** project connected to this repository through the
Pages GitHub App, so **every push to `main` redeploys automatically** — there is
nothing to publish by hand.

There is no build step. Cloudflare serves the **repository root** as-is, because
`index.html` lives there:

| Setting | Value |
|---|---|
| Framework preset | *None* |
| Build command | *(leave empty)* |
| Build output directory | `/` |
| Production branch | `main` |

Because the output directory is the repo root, the Python backend (`*.py`) is
published along with the game. That has always been the case and is harmless, but
it does mean the Flask source is readable at, for example, `/items.py`.

All asset paths are relative (`./js/...`, `icons/...`), so the site works unchanged
from a domain root or a project subdomain. HTTPS is automatic; a custom domain can
be attached under the project's **Custom domains** tab.

### Cache headers

`_headers` tells Cloudflare not to sit on the service worker or the app shell:

```
/sw.js
  Cache-Control: no-cache
/index.html
  Cache-Control: no-cache
/icons/*
  Cache-Control: public, max-age=86400
```

Pages already revalidates assets by default, so this is a guarantee rather than a
fix — but if the CDN ever handed a browser a pinned old `sw.js`, no push you ever
made would reach that player. Note that Pages consumes this file rather than
serving it: requesting `/_headers` returns the app shell.

### After you push

Cloudflare takes about a minute to build. Players then pick the new version up the
next time they open the app — the service worker swaps caches as soon as it sees a
changed `sw.js`.

> **Bump `CACHE_VERSION` in `sw.js` whenever you change anything under `js/`.**
> Those files are served cache-first, so without a bump the browser keeps running
> the old game code even after the new HTML arrives. That one line is the entire
> update mechanism.

## Install as an App (PWA)

The deployed site is a full PWA: it caches itself for offline play and can be installed to a home screen / desktop.

1. Open the Cloudflare Pages URL above (HTTPS is automatic).
2. **Android / Chrome:** menu — *Add to Home screen*. **iOS / Safari:** Share — *Add to Home Screen*. **Desktop Chrome/Edge:** install icon in the address bar.
3. Launch it — it works with no connection, and saves persist in the browser (localStorage).

> **Saves are device-local.** Each browser on each device keeps its own characters — a save is not synced or backed up. It survives closing the app, rebooting and being offline, but it is **wiped** by "Clear cookies and site data" (and by uninstalling the app on Android), and it does not follow you to another device or browser.

Files that make it a PWA:

| File | Purpose |
|---|---|
| `manifest.json` | App name, colours, display mode, icon set |
| `sw.js` | Service worker: pre-caches the app, serves it offline |
| `_headers` | Cache-control rules for Cloudflare Pages |
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
| **DEX** | Ranged/finesse attack & damage, **Armour Class**, poison chance | See the AC formulas above; poison lands `20% + 3% per DEX`, max 60% |
| **CON** | **Max HP** | Each CON modifier point adds `+1 HP per level` |
| **INT** | Burn damage, freeze duration; *also* reserved for Wizard spells | `burn = 1d4 + max(0, INT mod)`, frozen 2 rounds at INT 15+ |
| **WIS** | *No effect yet* — reserved for Cleric spells | — |
| **CHA** | *No effect yet* | — |

### Damage types

Every weapon has a damage type, and every monster reacts to it. A hit against a
weakness does **x1.5** damage, against a resistance **x0.5**.

| Monster | Weak to (x1.5) | Resists (x0.5) |
|---|---|---|
| Zombie | slashing, piercing | bludgeoning, force |
| Skeleton | bludgeoning, piercing | slashing, fire |
| Spider | fire, ice | piercing |
| Wolf | piercing | bludgeoning |
| Goblin | slashing | ice |
| Slime | fire, ice | bludgeoning, piercing, slashing |
| Ghost | force, ice | piercing, slashing |
| Demon Lord | ice, piercing | fire, dark, force |
| Elder Dragon | piercing, poison | fire, slashing |

Three types also inflict a lasting effect when the hit lands:

| Element | Effect | Length | Damage |
|---|---|---|---|
| fire | Burning — damage every round | 2 rounds | `1d4 + max(0, INT mod)` per round |
| ice | Frozen — the monster loses its whole turn | 1 round, 2 at INT 15+ | — |
| poison | Damage every round | **until it dies** | `max(1, DEX mod)` per round |

Fire and ice ride along on any weapon whose damage type is fire or ice (Frost
Staff, Ember Blade, Lampada); poison needs a poison weapon (Venom Dagger, Plasma
Wand), and the chance of it landing scales with your DEX.

### Two hands

A two-handed weapon needs both hands, so it cannot be paired with a shield. It
also hits harder, with a bonus keyed to its damage dice:

| Weapon | Damage | Two-handed bonus |
|---|---|---|
| Longsword | 1d8 slashing | **+1** |
| Greatsword | 2d6 slashing | **+1** |
| Maul | 2d10 bludgeoning | **+2** |
| Dagger | 1d4 piercing | — (one-handed) |

Equip a one-handed weapon and the off-hand frees up for a shield or a second
one-handed weapon. Equipping a two-handed weapon sends whatever was in the
off-hand back to your bag rather than dropping it.

> The Fighter's starting Longsword is two-handed, so a new Fighter cannot equip a
> shield until it switches to a one-handed weapon.

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

### Healing potions

| Potion | Restores | Unlocks at | Price |
|---|---|---|---|
| Healing Potion | 9 HP | level 1 | 15g |
| Greater Healing Potion | 20 HP | level 5 | 50g |
| Superior Healing Potion | 100 HP | level 15 | 300g |
| Grand Healing Potion | 300 HP | level 35 | 1500g |
| Ultimate Healing Potion | 800 HP | level 70 | 8000g |

All five are sold by the Potion Merchant. In the shop, potions get a quantity
stepper (1 / 5 / 10 / 20 / Max); every other item is a single tap.

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
├── index.html           # PWA client (static build, Cloudflare Pages entry point)
├── manifest.json        # Web app manifest (name, icons, colours)
├── sw.js                # Service worker (offline cache)
├── _headers             # Cloudflare Pages cache-control rules
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

The Python files power the Flask build (`py ./game_server.py`); `js/` is a port of them so the same game runs as a static PWA. The reasoning is in [Why there are two builds](#why-there-are-two-builds) — change both when you change game rules.

## Working on the Code

This repo holds **two implementations of one game** (see
[Why there are two builds](#why-there-are-two-builds)), so a few rules keep them
honest:

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
- Skills and spells in combat (INT and WIS now drive elemental weapons; both are otherwise still placeholders)
- Off-hand attacks — a second weapon currently gives AC and stats but no extra attack
- Status effects on the player — fire, ice and poison only work on monsters for now
- Sell back items to shops
- Difficulty scaling options
- Possibly: a minimum starting-HP floor or a heal between fights — see the death-rate table in `PROGRESS.md`
