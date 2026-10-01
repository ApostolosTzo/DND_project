# DND Terminal Game - Progress Tracker

## File Structure

```
DND_project/
├── main.py              # Entry point, menus, game loop (terminal)
├── player.py            # Player class, character creation, leveling
├── items.py             # Weapon, Armor, Item classes + ITEMS dict
├── inventory.py         # Inventory screen, equip/use items
├── shop.py              # NPC shops with buy system
├── combat.py            # Turn-based combat system
├── enemy.py             # Enemy templates, generation, scaling
├── dice.py              # Dice roller (d4-d20)
├── ui.py                # Arrow-key menu, input, screen clears (terminal)
├── save_load.py         # Multi-save JSON system
├── game_server.py       # NEW - Flask server, web API endpoints
├── run_server.py        # NEW - Server launcher (py run_server.py)
├── PROGRESS.md          # This file
├── templates/
│   └── index.html       # NEW - HTML/CSS/JS browser UI
└── saves/               # Save files directory
```

## Features by File

### main.py
- Main menu: New Game, Load Game, Quit
- Load Game lists all saves with name/class/level
- Game loop: Inventory, Shop, Fight, Save, Quit
- On death: returns to main menu

### player.py
- Character creation: Name → Race → Class → Stats → Gear
- Races: Human (+1 all), Elf (+2 DEX, +1 INT), Dwarf (+2 CON, +1 STR), Halfling (+2 DEX, +1 CHA)
- Classes: Fighter (HP 10), Rogue (HP 8), Wizard (HP 6), Cleric (HP 8)
- Stats: 4d6-drop-lowest, race bonuses applied
- Starting gear per class (weapon + armor + 3x Healing Potion)
- Equipment system: weapon, armor, shield slots
- AC calculation: light (DEX), medium (DEX max 2), heavy (no DEX), shield (+2)
- Gold tracking: add_gold(), spend_gold()
- XP system: xp_to_next = level * 100, auto level-up on XP gain
- Level up: HP increase (Fighter +4, Rogue/Cleric +3, Wizard +2), full heal, gold reward
- Every 4 levels: stat boost menu (pick +1 to any stat)
- CON increase at stat boost: +1 extra HP
- Autosave at level 4/8/12/... (if current_save is set)
- current_save tracks which file was loaded for autosave overwrite

### items.py
- Weapon class: name, damage_dice, damage_type, properties, category
- Armor class: name, base_ac, armor_type, dex_limit, properties, category
- Item class: name, description, effect, category
- ITEMS dict: 5 weapons, 6 armors/shields, 1 item
- Weapons: Longsword(1d8), Shortbow(1d6), Dagger(1d4), Magic Staff(1d6), Mace(1d6)
- Armors: Leather(11/light), Chainmail(14/medium), Plate(17/heavy), Titanium(18/heavy), Dragon Scale(19/heavy), Shield(+2)
- Items: Healing Potion (restores 9 HP)
- STARTING_GEAR: per-class weapon/armor/3 potions
- get_item() + create_item() (create returns fresh instances)

### inventory.py
- Shows equipped gear at top
- Storage section with quantity tracking (x3, x2, etc.)
- Select weapon/armor → equip (swap with current)
- Select Healing Potion → drink (heals 9, removes one)
- Filters out equipped items from storage list

### shop.py
- 4 NPC shops: Potion Merchant, Weaponsmith, Armorer, Arcane Vendor
- Level-locked items (Plate Lv.4+, Titanium Lv.7+, Dragon Scale Lv.10+)
- Shows gold + "Your Storage" column with quantity counts
- Buy flow: select item → type quantity → confirm
- Checks gold before purchase

### combat.py
- Turn-based: Player action → Enemy action
- Player actions: Attack, Use Item, Flee
- Attack: d20 + proficiency + STR/DEX mod vs enemy AC
- Hit → weapon damage + mod (min 1)
- Enemy attack: d20 + (level//2 + 2) vs player AC
- Flee: d20 >= 10 to escape, fail = enemy attacks
- Use Item: opens inventory during combat, enemy attacks after
- On kill: gold drop + XP reward
- On death: return False to main
- Combat screen shows both combatants' stats

### enemy.py
- 7 enemy templates: Zombie, Skeleton, Spider, Wolf, Goblin, Slime, Ghost
- Each has: hp, ac, dice, bonus, xp, gold
- Scaling: HP +8/level, AC +1/3 levels, damage dice +1 die/4 levels, bonus +1/2 levels
- Enemy level range: [max(1, player-2), player] (caps at player level)
- Level 1-2: always level 1 enemies

### dice.py
- roll("2d6+3") → int
- roll_4d6_drop_lowest() → int (for stat generation)
-   The format: NdX+Y
    * N	Number of dice to roll	2 = roll two dice
    * d	Dice separator	just notation
    * X	Number of sides per die	d6 = 6-sided die (1-6)
    * +Y	Flat bonus added after the roll	+3 = add 3 to total 
    
    Examples
    
    |Roll |	What happens|Range|
    | :--- | :---| :---| 
    1d6 | Roll one 6-sided die |  1–6
    2d6	| Roll two 6-sided dice, sum them | 2–12
    1d20+3 | Roll one 20-sided die, add 3 | 4–23
    3d4+2 | Roll three 4-sided dice, add 2 | 5–14 
    
    ```
    roll("1d20")        # 1–20 (single d20)
    roll("2d6+3")       # 5–15 (two d6 + 3)
    roll("3d4-1")       # 2–11 (three d4 - 1)
    roll_4d6_drop_lowest()  # 3–18 (for character stats)
    ```

### ui.py
- menu(title, options, body="") → int (arrow-key navigation)
- get_key() → "up", "down", "left", "right", "enter", "esc", or letter
- clear_screen(), show(text), prompt(text), press_any_key()
- Works on Windows (msvcrt)

### save_load.py
- Multi-save: each save is a JSON file in saves/
- Save: player name, race, class, level, xp, gold, stats, hp, equipment, inventory
- Load: recreate Player from JSON, restore state
- list_saves(): returns all saves with metadata for load menu

### game_server.py (NEW - Flask Web Server)
- Flask app that serves the game over HTTP
- Routes: /, /state, /start, /action, /save, /load_list, /shop_buy, /custom_save, /create_form
- /create_form returns race/class data with stat bonuses for the character creation form
- /start accepts JSON {name, race, class} and creates character via make_character()
- /action handles all game logic: town, combat, shop, inventory, save, load, stat boost
- /shop_buy accepts JSON {item, qty} from the buy quantity popup
- Combat is state-machine driven (no blocking while-true loop)
- Player death returns to main menu
- Enemy level range caps at player level (no enemies above player)
- Character creation uses make_character() instead of terminal create_character()
- Server auto-restarts on file changes (debug mode)

### templates/index.html (NEW - Browser UI)
- Single-page HTML/CSS/JS interface
- Styling: dark D&D theme, monospace font, gold accents (#c9a84c)
- Layout: left column (title + body + options + log), right sidebar (player stats)
- HP bar (green) and XP bar (blue) with animated fill
- Character creation form: name input, race dropdown, class dropdown
- Info box below form shows race stat bonuses and class HP/primary stat, updates on selection change
- All game screens rendered as option buttons (> style)
- Shop buy overlay: popup with quantity input and Buy/Cancel buttons
- Log section at bottom shows latest game events
- Uses fetch() API to communicate with Flask backend
- Navigation: each screen type has a handleClick() function that routes to the correct API call

### player.py additions
- Added make_character(name, race, class_name) - creates character without terminal interaction
  * Rolls 4d6-drop-lowest for stats
  * Applies race bonuses (Human gets +1 all, others get specific bonuses)
  * Assigns starting gear (weapon + armor + 3 Healing Potions)
  * Returns fully built Player object

## Custom Save Problem (SOLVED)

### What was broken
- Custom save (`/custom_save` endpoint + prompt dialog in browser) was unreliable:
  - `/custom_save` lacked a `None`-check for `gs["player"]`, so Flask debug reloads caused silent 500 errors
  - `save_menu` options included "Enter custom name" with a browser `prompt()` dialog that could be blocked or cancelled
  - No error handling on client fetch calls (errors swallowed silently)
  - `gs["screen"]` was never updated to `"save_menu"`, causing server/client state desync
  - The `/action` handler had no `"save_menu"` case (fell through to `get_state()`)

### What i did
1. **Removed custom save entirely** — deleted `/custom_save` route and `doCustomSave()` JS function
2. **Simplified save menu** — options are now just `["Save as '{name}'", "(Back)"]` using the character's bare name (no `_LvX` suffix)
3. **Added duplicate save detection** — new `save_exists(name)` in `save_load.py` checks `saves/{name}.json` before overwriting
4. **Overwrite confirmation** — in browser, `/save` returns `"confirm_overwrite"` screen with Yes/No; in terminal, prompts `"Overwrite? (y/n)"`
5. **New `/force_save` endpoint** — called after user confirms overwrite; stores pending name in `gs["pending_save_name"]`
6. **Server state tracking** — `gs["screen"]` now properly set to `"save_menu"`, `handle_action()` handles both `"save_menu"` and `"confirm_overwrite"` screens
7. **Load list format** — changed from `"{save_name:<20} {name} {class} Lv.{level}"` to `"{name} {race} {class} Lv.{level}"` (shows human-readable info, not filenames)

### Files changed
- `save_load.py` — added `save_exists()`
- `game_server.py` — import `save_exists`, new `gs` keys, simplified save default, overwrite check in `/save`, new `/force_save`, confirm_overwrite action handler, load list format
- `templates/index.html` — removed `doCustomSave`, added `doForceSave`, `confirm_overwrite` case in `handleClick`
- `main.py` — import `save_exists`, simplified save default, overwrite prompt before saving, load list format

## World Map (Visual Only)

### What was added
- A static SVG world map displayed below the log section in the browser UI
- Shows 4 locations as connected nodes:
  - **Town** (gold dot, center-left) — connects to Village 1 and Village 2
  - **Village 2** (teal dot, top-right) — connected from Town
  - **Village 1** (teal dot, bottom-right) — connected from Town
  - **Dungeon** (red dot, far-right) — connected from Village 1
- Connecting lines styled as muted paths (road-like appearance)
- Labels centered above each dot with matching colors
- Map is purely visual — no interaction or navigation yet
- Dark background matching the game's theme

### Files changed
- `templates/index.html` — added `#map-container` CSS + SVG element after `#log`

### Next
- Make locations clickable → transition to location screen
- Implement town/village/dungeon screens and gameplay

## Items & Shops Expanded + Stat Bonuses

### What was added
- **`stats_bonus` field** on all item classes (Weapon, Armor, Item) — items can now grant stat bonuses when equipped (e.g. Arcane Staff gives +1 INT, Dragon Scale gives +1 CON, Wizard Robe gives +1 INT, Arcane Ring gives +1 INT)
- **`effective_stats()`** on Player — combines base stats with equipment stat bonuses
- **`get_equipment_stat_bonus()`** on Player — sums all stats_bonus from equipped weapon, armor, and shield
- **`modifier()`** now uses `effective_stats()` — stat bonuses from equipment automatically affect:
  - Attack rolls and damage (STR/DEX from weapons)
  - Armor class (DEX from armor)
  - Max HP (CON from equipment via `recalc_hp()`)
- **`recalc_hp()`** on Player — recalculates max HP when CON changes from equipment (also called on equip)

### New items (16 new weapons, 10 new armors, 6 new items)

**Weapons added:** Greatsword, Battle Axe, War Hammer, Flail, Spear, Rapier, Quarterstaff, Longbow, Crossbow, Hand Crossbow, Arcane Staff, Wand

**Armors added:** Studded Leather, Hide, Scale Mail, Breastplate, Half Plate, Ring Mail, Splint, Wizard Robe (with +1 INT)
```
Light armor:  AC = base_armor + DEX mod
Medium armor: AC = base_armor + min(DEX mod, 2)
Heavy armor:  AC = base_armor (no DEX)
No armor:     AC = 10 + DEX mod
Shield:       AC += 2
```

**Items added:** Greater Healing Potion (heals 20), Mana Potion, Antidote, Scroll of Fireball, Scroll of Healing, Arcane Ring (with +1 INT)

### New shops
- **Archer** — sells Shortbow, Longbow, Crossbow, Hand Crossbow
- **Wizard** — sells Magic Staff, Wand, Arcane Staff (+1 INT), Wizard Robe (+1 INT), Arcane Ring (+1 INT), Lampada
- Existing shops expanded with new items at level-appropriate prices

### How stat bonuses work (example)
If a Fighter equips an **Arcane Staff** (+1 INT):
- `effective_stats()["INT"]` = base INT + 1
- `modifier("INT")` = (effective_INT - 10) // 2  (one higher than before)
- Does NOT affect Fighter's damage (which uses STR), but would affect Wizard's spell attacks in the future

If a player equips **Dragon Scale** (+1 CON):
- `modifier("CON")` increases by 1
- `recalc_hp()` adds +1 max HP per level

### Files changed
- `items.py` — all classes get `stats_bonus` param; 32 new items added; `create_item()` copies `stats_bonus`
- `shop.py` — Archer + Wizard shops added; all shops expanded with new items
- `player.py` — `effective_stats()`, `get_equipment_stat_bonus()`, `recalc_hp()` added; `modifier()` uses effective stats; `equip_weapon()`/`equip_armor()` call `recalc_hp()`
- `game_server.py` — `player_json()` returns `stats`, `effective_stats`, `stat_bonuses`; `inventory_action()`/`combat_item_action()` handle Greater Healing Potion and other items; calls `recalc_hp()` on equip
- `inventory.py` (terminal) — handles Greater Healing Potion; calls `recalc_hp()` and `calc_ac()` on equip

## `__init__` Order Bug (Fixed)

### The error
```
File "...\DND_project\player.py", line 64, in effective_stats
    for stat, val in self.get_equipment_stat_bonus().items():
                     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "...\DND_project\player.py", line 56, in get_equipment_stat_bonus
    for item in [self.weapon, self.armor, self.shield]
                 ^^^^^^^^^^^


AttributeError: 'Player' object has no attribute 'weapon'
```
Raised from `get_equipment_stat_bonus()` at line 56 in `player.py`.

### Why it happened
When `modifier()` was changed to use `effective_stats()` → `get_equipment_stat_bonus()`, the latter iterates `[self.weapon, self.armor, self.shield]`. But in `Player.__init__`, those attributes were assigned **after** `self.max_hp = ... + self.modifier("CON")` and `self.ac = self.calc_ac()`. So the first call to `modifier()` (for HP calculation) tried to access `self.weapon` before it existed:

```
self.stats = stats                          # line 43
self.max_hp = ... + self.modifier("CON")    # line 44 ← calls effective_stats → get_equipment_stat_bonus → needs self.weapon
...
self.weapon = None                          # line 47 ← assigned too late
```

### The fix
Moved `self.weapon`, `self.armor`, and `self.shield` assignment to right after `self.stats`, before `max_hp` and `ac` are calculated. Now all attributes exist before any method that reads them is called.

## Interactive World Map

### What was added
- **`world_map.py`** — new file defining all map locations (Town, Village 1, Village 2, Dungeon) with coordinates, types, and connection graph (`connects_to` list)
- **`/map_data` endpoint** — returns all locations with their properties
- **`/travel` endpoint** — POST with `{location: id}`, validates connection graph, updates `gs["current_location"]`, returns log message
- **`gs["current_location"]`** — tracks where the player is on the map; auto-set to "town" whenever the town screen is shown
- **Dynamic SVG map** — replaces the old static SVG. Rendered in JS from `world_map.py` data
  - **Current location** — larger gold dot with pulsing ring animation
  - **Connected locations** — full brightness, clickable (cursor: pointer)
  - **Unreachable locations** — dimmed to 35% opacity, not clickable
  - **Click a dot** → POST `/travel` → location updates → map redraws
  - **Corner label** — `"You are at: Town"` in top-left of SVG
  - **Lines** — drawn between all connected node pairs (deduplicated)
- **Dungeon screen** — travelling to the dungeon shows `"The entrance looms before you..."` with Enter/Back options (Enter not implemented yet)
- **Village screen** — travelling to a village shows a generic screen with Back option

### How travel works
1. Player clicks a connected (bright) dot on the map
2. Client sends `POST /travel {location: "village1"}`
3. Server checks `current_location.connects_to` includes target
4. If valid: updates `gs["current_location"]`, returns screen for that location type
5. If invalid: returns error message, stays put
6. Map redraws with new current location — reachable connections change accordingly

### Files created/changed
- `world_map.py` — NEW: location definitions
- `game_server.py` — import `LOCATIONS`, `gs["current_location"]`, `/map_data`, `/travel` endpoints, `respond()` includes `current_location` and auto-sets it for town screen, action handlers for `location`/`dungeon` screens
- `templates/index.html` — replaced static SVG with JS `drawMap()` function, added `travel()`, `loadMapData()`, `mapLocations` global, `drawMap()` call at end of `render()`, startup calls `loadMapData()` + `fetchState()`, handleClick cases for `location`/`dungeon` screens

## Shop NPC Selection Bug Chain (Fixed)

### Problem 1: NPC menu appeared twice
When clicking "Visit Shop" in town, the NPC selection menu appeared → user picks an NPC → NPC menu appears again → user picks again → finally enters the shop.

**Root cause**: In `town_action(1)`, the server set `gs["screen"] = "shop"` (line 199), but the response sent `screen="shop_select"`. When the user clicked an NPC, `handle_action()` checked `gs["screen"]` — it was still `"shop"`, so it routed to `shop_action()` (returns NPC list) instead of `shop_select_action()` (enters the shop).

**Fix 1**: Changed `gs["screen"] = "shop"` → `gs["screen"] = "shop_select"` on line 199.

### Problem 2: Village 2 skipped the NPC list
After Fix 1, Village 2 (only Potion Merchant) went directly into the shop when clicking "Visit Shop" — no NPC list shown. The user wanted to see the NPC list first everywhere.

**Root cause**: A shortcut in `shop_state()` that checked `if len(shop_names) == 1` and skipped the selection menu.

**Fix 2**: Removed the single-shop shortcut from `shop_state()`. All locations now show the NPC list before entering a shop.

### Problem 3: Village 1 opened wrong shop on Back
After Fixes 1 + 2, Village 1 worked normally. But entering Potion Merchant and pressing Back opened the Weaponsmith's shop instead of the NPC list.

**Root cause**: `respond()` never synced `gs["screen"]` with the response. When `show_shop()` returned `respond("shop", ...)`, the server's `gs["screen"]` remained as whatever it was before (`"shop_select"`). Pressing Back sent an action to the server, which checked `gs["screen"]` — still `"shop_select"` — so it routed to `shop_select_action()` instead of `shop_action()`. The Back index happened to be a valid NPC index in the location's shop list, so it opened that NPC's shop instead of going back.

This was a **systemic state-desync bug**: every response sent a `screen` value to the client, but the server never updated its own `gs["screen"]` to match.

### Final fix: `gs["screen"]` sync in `respond()`
Added one line at the top of `respond()`:
```python
gs["screen"] = screen
```

Now every response automatically syncs the server's internal screen state with what the client receives. This permanently prevents any future state-desync bugs between server and client.

### Files changed (final)
- `game_server.py` — line 199: `"shop"` → `"shop_select"`; removed single-shop shortcut from `shop_state()`; added `gs["screen"] = screen` inside `respond()`

### Lesson
The root cause of all three bugs was the same: **server-side `gs["screen"]` was not kept in sync with the response screen**. The final fix (syncing inside `respond()`) eliminates the entire class of bugs at the source rather than patching each symptom individually.

## Dungeon System

### What was built
A 10-floor dungeon crawl accessible from Village 1 with progressive enemy scaling, a mid-way merchant stop, and a boss encounter on the final floor.

### Screen flow
```
[Dungeon Entrance] → Enter → [Floor N: enemy info] → Attack → [Combat] → Win → [Floor cleared]
                                                                                      │
                                                                            Floors 1-4, 6-9: auto → next floor
                                                                            Floor 5:  ["Visit Merchant", "Descend to Floor 6"]
                                                                            Floor 10: ["Visit Merchant", "Attack Boss"]
                                                                                                  │
                                                                                       Floor 10 boss killed
                                                                                              ↓
                                                                                    [DUNGEON CLEARED!]
                                                                                    Bonus 500g + 500 XP
                                                                                    Return to Village 1
```

### State tracking
- `gs["dungeon_floor"]` — `0` = outside dungeon, `1–10` = current floor number
- Initialized to `0` in the global state dict
- Reset to `0` on game over (player death) and on dungeon victory

### Enemy scaling (`enemy.py`)
- **Normal floors (1–9)**: picks from the 7 base templates, enemy level = `player_level + floor // 2`
- **Boss floor (10)**: picks from 2 new boss templates:
  - **Demon Lord** (HP 60, AC 15, d10, +5 bonus)
  - **Elder Dragon** (HP 75, AC 18, d12, +6 bonus)
- Boss enemy level = `player_level + 3` — significantly harder than any overworld enemy

### Key design decisions

**1. Floor screen as a separate state (`dungeon_floor`) rather than folding directly into combat.**
- Shows the enemy before engaging (player can size up the threat)
- Provides a clean transition point for merchant/descend options after clearing
- Avoids complicating the existing `combat` / `town` screen handlers

**2. No Flee in the dungeon.**
- `combat_state()` checks `gs["dungeon_floor"] > 0` and omits "Flee" from options
- `combat_action()` blocks any flee attempt with `"You cannot flee from the dungeon!"`
- Creates tension — the player must fight through or die trying

**3. Merchant at floor 5 (after clear) and floor 10 (before boss).**
- Reuses the existing shop system: `dungeon_merchant()` sets `gs["shop_name"] = "Potion Merchant"` and renders the Potion Merchant's inventory
- `shop_action()` was modified to check `gs["dungeon_floor"] > 0` and return to the dungeon floor instead of the shop selection menu
- Prevents softlock: player can buy potions before the boss, but can't escape the dungeon

**4. Dungeon victory at floor 10 (boss death).**
- `combat_reward()` routes to `dungeon_combat_reward()` when in dungeon
- Boss kill grants 500 bonus gold + 500 bonus XP
- `after_dungeon_combat()` helper prevents the `stat_boost_action` re-entry bug: if a level-up stat boost interrupts the boss victory flow, calling `after_dungeon_combat()` shows the victory screen without re-adding the bonus rewards

**5. Dungeon merchant Back button handled via `shop_action()` check.**
- Single line `if gs["dungeon_floor"] > 0: return dungeon_floor_state()` at the top of `shop_action()`
- No need for a separate dungeon shop endpoint or client-side changes
- After buying potions and pressing Back, the player returns to the floor screen

### Files changed

**`enemy.py`:**
- Added 2 boss templates (Demon Lord, Elder Dragon) to `TEMPLATES`
- Added `generate_dungeon_enemy(floor, player_level)` with floor-scaled level selection
- Added `BOSS_NAMES` list for the floor-10 boss filter

**`game_server.py`:**
- Added `"dungeon_floor": 0` to `gs`
- New functions: `enter_dungeon()`, `dungeon_floor_state()`, `dungeon_floor_action()`, `advance_dungeon_floor()`, `dungeon_combat_reward()`, `after_dungeon_combat()`, `dungeon_merchant()`
- Modified: `combat_state()` (hide Flee), `combat_action()` (block Flee), `combat_reward()` (route to dungeon), `stat_boost_action()` (return to dungeon), `shop_action()` (return to dungeon floor), `handle_action()` (add `dungeon_floor` / `dungeon_victory` routing, replace dungeon placeholder), game_over handler (reset floor)

**`templates/index.html`:**
- Added `handleClick` cases for `"dungeon_floor"` and `"dungeon_victory"` screens

### Analysis

**What went well:**
- The dungeon system integrates cleanly with the existing state-machine architecture — no blocking loops or new client-side state required
- Boss templates reuse the existing `Enemy` class without special-casing; only `generate_dungeon_enemy()` differs
- Merchant reuses the shop system with minimal modification (one line in `shop_action()`)
- The `after_dungeon_combat()` / `dungeon_combat_reward()` split correctly handles the edge case where a level-4/8/12 stat boost interrupts the post-boss reward flow

**What could be improved:**
- No save option in the dungeon (intentional — player must commit or die). Could add a mid-dungeon save point on floor 5
- Map still shows the overworld while in the dungeon (cosmetic — could hide map or show a dungeon floor plan)
- No loot drops from bosses besides gold/XP (a unique boss weapon/armor drop would add replay value)
- Floor 5 merchant sells only Healing Potion for low-level characters (Greater Healing Potion requires level 5). Could add a dungeon-specific stock

### Future possibilities
- Randomized dungeon layout (branching paths, dead ends)
- Trap rooms, treasure rooms, and mini-boss rooms between normal floors
- Unique boss loot (boss-specific weapons/armors)
- Dungeon floor map display instead of the world map
- Mid-dungeon save point

## Files changed reference (all Dungeon commits)
- `enemy.py` — bosses + `generate_dungeon_enemy()`
- `game_server.py` — state + 7 new functions + 6 modified functions
- `templates/index.html` — 2 new handleClick cases

## Skill Point System (replaces old stat boost)

### What changed
The old system gave a single +1 to any stat every 4 levels. The new system gives flexible skill points that the player can distribute freely across all stats.

### Point rewards
- **Every level**: +1 skill point
- **Levels 4, 8, 12, 16…**: +5 skill points (1 normal + 4 bonus)
- Points accumulate across multiple level-ups and are spent in one session

### How it works
1. `handle_level_up()` in `game_server.py` adds skill points instead of triggering the old stat-boost return
2. After all level-ups are processed (in `combat_reward()`), if `player.skill_points > 0`, the allocation screen is shown
3. The allocation screen (`screen="stat_allocation"`) shows all 6 stats with their current values and `[+]` buttons
4. Player clicks `[+]` on any stat → server spends 1 point, updates stat, recalculates AC, and if CON was increased, recalculates HP via `recalc_hp()`
5. When all points are spent, an autosave fires (if `current_save` is set) and the game continues
6. This works identically for both 1-point and multi-point sessions — same bulk screen

### What each stat does

| Stat | Effect | Formula |
|---|---|---|
| **STR** | Melee attack & damage (non-finesse, non-ranged weapons) | `modifier = (STR - 10) // 2` added to attack roll & damage |
| **DEX** | Finesse/ranged attack & damage, **Armor Class** | Light armor: `AC = base + DEX mod`; Medium: `AC = base + min(DEX mod, 2)`; No armor: `AC = 10 + DEX mod` |
| **CON** | **Max HP** | `max_hp` recalculated via `recalc_hp()` — each point of CON modifier adds +1 HP per level |
| **INT** | *No current effect* (reserved for Wizard spells) | — |
| **WIS** | *No current effect* (reserved for Cleric spells) | — |
| **CHA** | *No current effect* | — |

**INT, WIS, CHA** have no gameplay effect yet. They exist on the character sheet and can be allocated points, but don't influence damage, AC, HP, or any other mechanic.

### Boss bonus XP change
The 500 bonus XP for clearing floor 10 was moved from `dungeon_combat_reward()` into `combat_reward()`. This means all XP (enemy + boss bonus) is processed together before the allocation screen, so the player sees all skill points from all level-ups at once instead of being interrupted twice.

### Functions removed/replaced
| Old function | Replaced by |
|---|---|
| `stat_boost_action()` | `allocation_state()` + `allocation_action()` |
| `after_dungeon_combat()` | `after_combat()` (handles both town and dungeon) |
| `dungeon_combat_reward()` bonus logic | moved into `combat_reward()` |
| `"stat_boost"` screen | `"stat_allocation"` screen |

### Files changed
- `player.py` — added `self.skill_points = 0` to `Player.__init__`
- `save_load.py` — saves/loads `skill_points` (defaults to 0 for old saves)
- `game_server.py` — rewrote `handle_level_up()`, `combat_reward()`, removed `stat_boost_action()`, added `allocation_state()` + `allocation_action()` + `after_combat()`, removed bonus XP from `dungeon_combat_reward()`, updated `handle_action()` routing
- `templates/index.html` — replaced `"stat_boost"` handler with `"stat_allocation"` handler

## XP Carry-Over Fix

### The bug
When leveling up, XP was never subtracted from the total. The `while` loop checked `p.xp >= p.xp_to_next()` but `p.xp` never decreased, so excess XP kept being counted at full value, causing way too many level-ups.

### The fix
Added `p.xp -= p.xp_to_next()` before `handle_level_up()` in `combat_reward()`. Each level-up now subtracts the required XP threshold, and the remaining XP carries over correctly.

Example: gain 350 XP at level 1 → subtract 100 (reach level 2) → subtract 200 (reach level 3) → 50 XP remaining, correct.

### File changed
- `game_server.py` — one line added in `combat_reward()`

## Combat Item Group Display

### The problem
The "Use Item" screen in combat showed every inventory entry as a separate option. Having 5 Healing Potions displayed 5 identical "Healing Potion" buttons instead of "Healing Potion x5".

### The fix
Grouped consumables by name (same pattern as the inventory screen). The options now show `"Healing Potion x5"` and clicking it uses one from that stack.

### Files changed
- `game_server.py` — `combat_action()` and `combat_item_action()` both build a grouped item dict and index into group names instead of raw item list

## Hosting moved to Cloudflare

> **Superseded:** the deployment originally shipped through **GitHub Pages**. That
> path is gone — `.nojekyll` deleted, the README no longer describes it, and the Pages
> deployment was removed from the repository. The GitHub Pages notes further down
> are kept only as a record of what was done at the time.

The game now lives at **https://dnd-project.ap-tzortzakis.workers.dev** — a Cloudflare
**Worker serving the repository as static assets**, connected to GitHub through
Cloudflare's Git integration. A push to `main` still deploys automatically — only
the host changed.

| Removed | Replaced with |
|---|---|
| `.nojekyll` (stopped GitHub Pages running Jekyll) | nothing needed |
| GitHub Pages deployment on the repo | Cloudflare Worker `dnd-project` |
| README "Settings — Pages — Deploy from a branch" steps | Workers — `dnd-project` — Settings — Builds (Git connection, production branch `main`) |

Note the host is a Worker on a `workers.dev` subdomain, not Cloudflare Pages
(`pages.dev`) — the two products are configured in different places, so the README
documents the Worker path.

Added: **`_headers`**, which asks Cloudflare not to serve a stale `sw.js` or
`index.html` from its CDN:

```
/sw.js
  Cache-Control: no-cache
/index.html
  Cache-Control: no-cache
```

That is the piece GitHub Pages did not need. In testing the Worker already served
both as `must-revalidate`, so this is a guarantee rather than a fix — without it the
CDN could pin an old service worker in a player's browser and no push would ever
reach them. The `CACHE_VERSION` bump in `sw.js` is still required for game-code
changes; these headers make sure the browser is even *told* there is a new worker.

Nothing else moved: all asset paths were already relative, so the build works
unchanged from a domain root or a project subdomain. Verified by byte-comparing the
served `index.html` against the repository — identical (SHA-256 `AC82F448`
`F81053BC`) — before the old deployment was switched off.

## PWA Port (originally GitHub Pages, fully client-side)

### Goal
Run the game from a GitHub repository with no Python host, installable on a phone and playable offline. GitHub Pages is static-only, so the Flask layer was replaced by a browser port of the same game logic.

### What was added
- **`index.html` (root)** — the existing browser UI, with `fetch()` calls to the Flask endpoints replaced by direct calls into `Game.*`. Also gained the PWA head tags (viewport, manifest, theme colour, Apple meta tags) and service worker registration.
- **`manifest.json`** — app name, `#1a1a2e` theme/background, `display: standalone`, relative `start_url`/`scope` so it works at both `user.github.io/` and `user.github.io/repo/`.
- **`sw.js`** — pre-caches the 15 app assets into `dnd-pwa-v1`. Navigations are network-first (so updates land) with a cache fallback; everything else is cache-first.
- **`icons/`** — placeholder 192 / 512 / maskable-512 / apple-touch PNGs, generated as gold-on-navy art to be swapped later.
- **`.nojekyll`** — stops GitHub Pages running Jekyll over the repo.
- **`js/`** — the port:

| Python | JavaScript |
|---|---|
| `dice.py` | `js/dice.js` |
| `items.py` | `js/items.js` |
| `enemy.py` | `js/enemy.js` |
| `player.py` | `js/player.js` |
| `shop.py` | `js/shop.js` |
| `world_map.py` | `js/world_map.js` |
| `save_load.py` | `js/saves.js` (localStorage instead of `saves/*.json`) |
| `game_server.py` (routes + `gs` dict + handlers) | `js/game.js` (same functions, returns the same JSON object instead of `jsonify`) |

The UI was left alone deliberately: `respond()` returns the exact object Flask used to serialise, so `render()` and `handleClick()` work unchanged.

### Design decisions
1. **Plain `<script>` tags, no bundler / no modules** — no build step to push to Pages, and nothing to break if someone opens the file directly.
2. **Saves moved to `localStorage`** under one `dnd_saves` key, keeping the exact save schema the Python version writes (so the JSON shape stays familiar). Works per-device/per-browser rather than on the server.
3. **`gs["screen"] = screen` inside `respond()`** — the state-desync fix from the shop bug chain was carried over, so the client and the in-page state machine can't drift apart.

### Saves: where they live and when they disappear

Every save is written to `localStorage` under a single `dnd_saves` key as
`{ "<save_name>": { ...player data } }`, using the same field names the Python
version writes to `saves/*.json`. Nothing is ever sent to GitHub — the data
never leaves the device.

This is the trade-off for going server-free, and it is worth knowing before
you hand the link to someone:

| Situation | Save still there? |
|---|---|
| Same device, same browser, days/weeks later | ✅ Yes |
| Same device, fully offline (no Wi-Fi/cellular) | ✅ Yes |
| Same device after closing the tab / browser / reboot | ✅ Yes |
| Same device, **different browser** (Chrome → Safari) | ❌ No — separate storage |
| A different device (your phone vs their phone) | ❌ No — not synced |
| Browser "Clear cookies and site data" | ❌ **Wiped** |
| Android: uninstalling the installed PWA | ❌ **Wiped** |
| iOS: removing the home-screen icon | ⚠️ Usually kept, not guaranteed |

So a friend who plays on their phone, saves a Wizard, and reopens the game
next week on that same phone still has their Wizard. But the saves are
device-local, unbacked, and lost if the site data is cleared — they cannot be
moved to another device or shared with another player without a manual
copy/paste of the JSON.

Two ways to fix that later, in increasing order of effort:
1. **Export / import a save as a file** — a "Download save" button that writes
   the character JSON out (shareable over WhatsApp/AirDrop) and an "Import"
   that reads it back. Stays 100% static, needs a `Blob` + file input in
   `js/saves.js` and two buttons in the save menu.
2. **Real sync** — needs a backend (the Flask build, or a hosted DB), which
   puts you back to needing a host, i.e. the thing GitHub Pages can't do.

### Porting bugs caught and fixed
1. **Dungeon shop list** — Python's `loc.get("shops", default)` returns the *empty* list for the Dungeon (only missing keys get the default). The first JS version treated `[]` as falsy and offered all 5 shops there. Fixed with `hasOwnProperty`, and covered by a test.
2. **Corrupt/missing save** — `loadGame()` returns `null` now instead of throwing on `player.current_save`.
3. **Offline navigation through a proxy** — the first service worker only fell back to cache when `fetch()` *rejected*. A proxy answering `502` resolves normally, so an error page was shown instead of the cached app. Any non-OK navigation response now falls back to the cached shell.

### Verification
- Node harness runs the whole state machine end-to-end: main menu → creation → fight → shop buy/overwrite save → load → inventory equip/heal → map travel (incl. the unreachable and no-shop cases) → full 10-floor dungeon → death. Passing repeatedly with random dice.
- Browser check on `localhost`: character creation, combat math (`40 xp * level/2 = 20` matches Python), save → reload → load, all 15 assets cached, manifest + icons return 200.
- **True offline test**: killed the web server mid-session and reloaded — the shell, all scripts, the save data and combat all worked from the service worker cache with zero console errors.

### Files changed
- `index.html` (new, root) — PWA head tags + `Game.*` instead of `fetch()`
- `manifest.json`, `sw.js`, `.nojekyll`, `icons/*` (new)
- `js/*.js` (8 new files — port of the Python modules)
- `README.md` — two run options, PWA/install section, icon replacement guide
- `PROGRESS.md` — this entry

### Notes
- The Flask build (`python game_server.py` + `templates/index.html`) still works untouched; it is now the server-side variant.
- When you change game rules, change both `*.py` and `js/*`.
- When you replace the icons, bump `CACHE_VERSION` in `sw.js` so returning visitors get them.

## UI Overhaul, Combat Log & Monster Portraits

### What changed

**1. A CON skill point now heals you to full.**
`allocation_action()` / `allocationAction()` already called `recalc_hp()` for CON (raising max HP) but left current HP untouched, so a new point felt dead. It now also sets `p.hp = p.max_hp`, in both the Python and JS builds.

**2. The combat chat accumulates instead of being wiped.**
`combat_action()` used to do `gs["log"] = [result]` on every attack, so each exchange erased the previous one and you only ever saw the last round. It now appends:

| Action | Before | After |
|---|---|---|
| Player attacks | `log = [result]` (wiped) | `log.append(result)` |
| Enemy attacks | appended | appended (unchanged) |
| Failed flee | `log = ["Failed to flee!"]` | appended |
| Drink potion in combat | `log = ["Drank ..."]` | appended |
| Out of potions / cannot flee in dungeon | `log = [...]` | appended |

Victory still resets the log, so a new fight starts with a clean "A wild X appears!" line.

**3. Monster portraits.** Each of the 9 monsters now has a hand-drawn inline SVG (`MONSTER_ART` in `index.html`): Zombie, Skeleton, Spider, Wolf, Goblin, Slime, Ghost, Demon Lord, Elder Dragon, plus a fallback. The portrait appears on combat screens and on a live dungeon floor, with the monster's name, HP bar and AC; the duplicated first line of the screen body ("Lv.1 Zombie HP 12/22 AC 8") is stripped while it is showing.

**4. The monster reacts to damage.** A `--dmg` custom property (0 = untouched, 1 = nearly dead) drives progressive distortion, and landing a hit plays a shake:

```css
transform: rotate(calc(var(--dmg) * 7deg)) skewX(calc(var(--dmg) * 8deg)) scale(calc(1 - var(--dmg) * 0.05));
filter: blur(calc(var(--dmg) * 1.3px)) saturate(calc(1 - var(--dmg) * 0.45)) hue-rotate(calc(var(--dmg) * 55deg));
```
```css
@keyframes monster-hit { /* 11px shake + brightness flash, 450ms */ }
```
The class is applied by comparing the incoming enemy HP with `lastEnemyHp` from the previous render — a **miss** deliberately does not shake it.

**5. The map gets out of the way during a fight.** `body.in-combat` hides `#map-container` and lets `#log` stretch (`flex: 1`), so the chat fills the free space instead of scrolling in a 100px box. The class is set whenever a monster is on screen *or* `in_dungeon` is true.

**6. Responsive UI for phones.** The old layout was a fixed two-column flex with a `min-width: 220px` sidebar, which squashed on a phone:

- `@media (max-width: 760px)` — single column, player panel moves to the top as a 2-column grid (`order: -1`), buttons grow to `min-height: 46px` / `font-size: 1em`, monster portrait drops to 92px
- `@media (max-width: 400px)` — portrait stacks above the HP bar
- `#buy-box` no longer has a `min-width: 300px` that overflowed narrow screens (`max-width: 92vw`)
- Map nodes got an invisible `r + 11` hit area so they're tappable on a phone, plus `<title>` tooltips
- `env(safe-area-inset-bottom)` padding for notched phones, and `viewport-fit=cover`

**7. Desktop niceties.** `1`–`9` pick an option, `↑`/`↓` move a gold-highlighted selection and `Enter` confirms; a subtle `1-9 or ↑/↓ + Enter` hint sits under the buttons; the sidebar rows use flex instead of `float: right`; the log stamps each line with its own timestamp and auto-scrolls to the newest.

**8. "Quit" removed from the main menu.** It never did anything — `handleClick()` ignores index 2 on `main_menu`. `MENU_OPTIONS` is now `["New Game", "Load Game"]` (5 call sites in Python, 1 constant in JS). The town screen's Quit still works and is the way back to the menu.

### Bug found while testing the above
`render()` ended up calling `renderStage()` twice (once inline, once left over next to `drawMap()`). The second call rebuilt `stage.innerHTML`, wiping the `hit` class the first call had just added, so **the hit animation never played**. Caught by asserting on `getAnimations()` synchronously after a programmatic attack, and fixed by keeping a single call.

### Also changed
- `respond()` now includes `enemy` (`name/level/hp/max_hp/ac`) and `in_dungeon`, so the UI can render the portrait (mirrored in `game_server.py` with `enemy_json()`)
- `CACHE_VERSION` bumped to `dnd-pwa-v2` — **`js/*.js` is cache-first**, so without a bump returning players keep running the old game code even though the HTML updates

### Files changed
- `js/game.js` — CON full heal, appending combat log, `enemy`/`in_dungeon` in the payload, main menu without Quit
- `game_server.py` — the same four changes, mirrored
- `index.html` — monster SVGs, `#combat-stage`, hit/distortion CSS, responsive CSS, map hit areas, keyboard shortcuts, log timestamps, duplicate-render fix
- `sw.js` — cache version bump

## Character Reference Tables

Stats are rolled with **4d6-drop-lowest** (each 3–18), then the race bonus is applied.

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

### Starting health and armour class

| Class | HP at level 1 | AC range | AC formula |
|---|---|---|---|
| Fighter | 15 + CON mod | 14 – 16 | `14 + min(DEX mod, 2)` — Chainmail, medium (DEX capped at +2) |
| Rogue | 13 + CON mod | 8 – 17 | `11 + DEX mod` — Leather, light (the Dagger's +1 DEX counts) |
| Wizard | 11 + CON mod | 7 – 16 | `10 + DEX mod` — no armour |
| Cleric | 13 + CON mod | 17 flat | `17` — Plate, heavy (DEX ignored) |

Modifiers are `floor((stat - 10) / 2)`. Max HP is
`class HP + (level - 1) × HP per level + CON mod × level`.

### What each stat does

| Stat | Effect | Formula |
|---|---|---|
| **STR** | Melee attack rolls & damage | `STR mod` on the attack roll and on damage |
| **DEX** | Ranged/finesse attack & damage, **AC** | see the AC column above |
| **CON** | **Max HP** | `+1 HP per level` per CON modifier point (and heals to full when spent) |
| **INT** | *No effect yet* — reserved for Wizard spells | — |
| **WIS** | *No effect yet* — reserved for Cleric spells | — |
| **CHA** | *No effect yet* | — |

### Levelling

| Event | Effect |
|---|---|
| XP to next level | `level × 100` |
| HP on level up | class HP per level + 2 per CON modifier point, healed to full |
| Gold on level up | `new level × 10` |
| Skill points | +1 per level, +5 extra at levels 4, 8, 12, … |
| Combat accuracy | `d20 + proficiency + stat mod` vs target AC, proficiency `= floor((level - 1) / 4) + 2` |

### Combat rewards

Kills pay **+40% XP** and **+60% gold** (`XP_REWARD_MULTIPLIER = 1.4`, `GOLD_REWARD_MULTIPLIER = 1.6`), rounded to whole numbers.

| Monster | Base XP | Base gold | XP at Lv.1 | Gold at Lv.1 | XP at Lv.5 | Gold at Lv.5 |
|---|---|---|---|---|---|---|
| Goblin | 30 | 8 | 21 | 12 | 105 | 64 |
| Spider | 50 | 4 | 35 | 6 | 175 | 32 |
| Slime | 40 | 3 | 28 | 4 | 140 | 24 |
| Zombie / Skeleton / Wolf | 50 | 5 – 6 | 35 | 8 – 9 | 175 | 40 – 48 |
| Ghost | 80 | 10 | 56 | 16 | 280 | 80 |
| Demon Lord (boss) | 200 | 50 | 140 | 80 | 700 | 400 |
| Elder Dragon (boss) | 250 | 80 | 175 | 128 | 875 | 640 |

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

> ⚠️ `Wizard Robe` (+9 INT) and `Dragon Scale` (+8 CON) look like typos for +1 in the item data — that's +4 to the modifier, and Dragon Scale grants +4 CON per level. Reproduced as-is in both `items.py` and `js/items.js`; worth fixing in both.

## Difficulty Tuning & New Colour Palette

### Balance changes

**1. +5 base HP for every class.** Dying to the very first monster was the complaint, so `CLASSES[...]` went up by 5 across the board. Because `recalc_hp()` rebuilds max HP from the class value, this lifts every level, not just level 1.

| Class | Before | After |
|---|---|---|
| Fighter | 10 | 15 |
| Rogue | 8 | 13 |
| Wizard | 6 | 11 |
| Cleric | 8 | 13 |

**2. 15 Healing Potions at the start** (was 6), for every class. The repeated `"Healing Potion", "Healing Potion", …` lists in `STARTING_GEAR` were replaced with a single source of truth so the count only has to change in one place:

```python
STARTING_POTIONS = ["Healing Potion"] * 15          # Python
STARTING_GEAR = {"Fighter": {..., "items": list(STARTING_POTIONS)}, ...}
```
```js
const STARTING_POTIONS = Array(15).fill("Healing Potion");   // JS
```

**3. +40% XP and +60% gold** from every kill, as named constants in `enemy.py` / `js/enemy.js` so the balance is retunable in one spot:

```python
XP_REWARD_MULTIPLIER = 1.4    # +40% XP
GOLD_REWARD_MULTIPLIER = 1.6  # +60% gold
```

**Floating point trap:** the original formula was `xp_reward = t["xp"] * (level/2)`, which is already a float in Python 3. Multiplying that by 1.4 produced things like `35.000000000000004`, which the log would print verbatim. Both builds now round:

```python
self.xp_reward = int(t["xp"] * (level / 2) * XP_REWARD_MULTIPLIER)
```
```js
this.xp_reward = Math.floor(t.xp * (level / 2) * XP_REWARD_MULTIPLIER);
```
```python
def gold_drop(self):
    return int(TEMPLATES[self.name]["gold"] * self.level * GOLD_REWARD_MULTIPLIER)
```

A test now walks every monster at levels 1–15 asserting both rewards stay whole numbers.

### New palette: black / grey / gold / emerald

The navy-blue theme (`#1a1a2e`, `#16213e`, `#0f3460`, `#a8d8ea`, `#5dade2`, `#85c1e9`) was replaced everywhere in **both** UIs — the PWA `index.html` and the Flask `templates/index.html` — so the two builds no longer look like different games.

| Old | New | Used for |
|---|---|---|
| `#1a1a2e` | `#0b0b0c` | page background |
| `#16213e` | `#151517` | panels, combat stage, map background |
| `#0f3460` | `#1e1e21` | buttons, inputs, info box |
| `#1a5276` / `#0b2545` | `#2a2a2e` / `#242428` | button hover / active |
| `#111` | `#0e0e0f` | log background |
| `#333` | `#2e2e33` | borders, dividers |
| `#a8d8ea` | `#9a9aa0` | sidebar labels, muted text |
| `#aaa` | `#8a8a8a` | log text |
| `#555` | `#3a3a40` | map roads |
| `#5dade2` / `#85c1e9` | `#2fbf71` / `#5fd39a` | **emerald** village nodes and labels |
| `#27ae60` | `#2fbf71` | HP bar |
| `#e0e0e0` | `#d6d6d6` | body text |

Kept: gold `#c9a84c` / `#dbb95c` (titles, borders, town node, XP bar, buttons) and red `#c0392b` / `#e74c3c` (enemy HP, danger).

Also updated: `manifest.json` theme/background colour, and the four placeholder icons were regenerated in the new colours (near-black background, gold diamond, **emerald** centre pip). The monster portraits keep their own creature colours, and their drop shadows moved from `#000` to `#33333a` — pure black is invisible on a near-black panel.

The colour swap was done with a single scripted pass (`.NET UTF-8 read/write without BOM`) so the `⚔` and `×` characters in the files survive; verified afterwards that every touched file is still valid UTF-8 with no BOM.

### Files changed
- `player.py`, `js/player.js` — `CLASSES` base HP +5
- `items.py`, `js/items.js` — `STARTING_POTIONS` (15), de-duplicated `STARTING_GEAR`
- `enemy.py`, `js/enemy.js` — reward multipliers + integer rounding
- `index.html`, `templates/index.html` — full palette swap, monster shadow colour
- `manifest.json`, `icons/*.png` — new theme colour and icons
- `sw.js` — `CACHE_VERSION` → `dnd-pwa-v3`
- `README.md`, `PROGRESS.md` — updated tables + new sections

### Noted, not changed
The floor-10 boss bonus is still a flat **+500 gold / +500 XP** on top of the (now much larger) boss kill reward. At level 10 an Elder Dragon alone pays 1750 XP, so the bonus is proportionally small. Easy to scale it in `combat_reward()` if you want.

## Shop Detail Panels, New Map & Monster Art

### 1. The shop now explains each item inline

Clicking an item used to open a modal with a quantity box. It now expands a **panel directly under that item's row**, in the right-hand corner of which is a **Buy** button:

```
> Shield (25g)                        <- click me
┌──────────────────────────────────────────────┐
│ Shield — 25g                               │
│ Armour        2 AC · shield                │
│ AC 16 → 18 (+2)                            │
│                              [ Buy · 25g ]  │
└──────────────────────────────────────────────┘
```

- **Always exactly one item.** The quantity prompt is gone; `shopBuy(name, 1)` is called directly, so you cannot accidentally buy 40 potions.
- **It says what the item gives you**, not just its price: damage dice and damage type, properties (`finesse`, `ranged`, `two-handed`, …), armour type, stat bonuses, and for consumables their effect.
- **It previews the AC change** ("AC 16 → 18 (+2)") so you can compare before spending. `acPreview()` re-implements `Player.calc_ac()` client-side, substituting the candidate item, so the number is computed with the game's real formula rather than guessed.
- **Every purchase is written into the chat log**: `Bought 1 × Shield for 25g!`
- **Broke? The button disables itself** (`Not enough gold`) instead of letting you click and get an error.
- A gold line sits at the top of the list: *"You have 900g — tap an item to see what it gives you"*.

Details: `#options.shop`, `.shop-row`, `.shop-detail`, `.shop-buy` CSS; `renderShop`/`renderOptions`, `toggleShopItem`, `shopDetailHtml`, `itemStatRows`, `acPreview` in `index.html`. The keyboard handler now selects `#options button[data-opt]`, so the new Buy buttons are skipped by `1`–`9` and the arrow keys.

The old quantity modal (`#buy-overlay`, `#buy-box`, `showBuy`/`buyConfirm`) is left in the markup but is now unreachable — it can be deleted safely.

### 2. The world map was redrawn

The old map was four flat dots joined by straight grey lines. It is now an illustrated fantasy map:

| Layer | What's there |
|---|---|
| Ground | vertical gradient (`#0d0d10` → `#17171c`) plus a radial vignette |
| Hills | soft translucent ellipses |
| River | a bezier sweep across the map with a faint emerald highlight |
| Forest | 10 hand-placed conifers near the villages |
| Mountains | a 4-peak range around the dungeon, with snow caps |
| Roads | **curved** quadratic paths drawn twice — a dark casing plus a dashed gold centreline — and dimmed when the endpoint is out of reach |
| Nodes | gold / emerald / red discs with a **castle**, **house** or **cave** glyph inside, a label pill, and a pulsing ring + glow on your current location |
| Chrome | "You are at: X" caption, a "Tap a lit marker to travel" hint, and a Town/Village/Dungeon legend bottom-left |

Helpers: `roadPath()` (perpendicular-offset bezier so curves stay generic), `tree()`, `mountain()`, `nodeGlyph()`. Nodes grow slightly on hover (`.mn:hover` with `transform-box: fill-box`) and the invisible `r + 12` tap targets remain for phones.

A **legend/dungeon overlap** was caught and fixed: the legend panel originally sat at `x=330 y=318`, directly under the Dungeon node (470, 310) and its label — moved to the bottom-left.

The renderer is self-contained (its CSS lives in an SVG `<style>` block), so the identical block was copied into `templates/index.html` — **both builds show the same map**. It was synced with a script that re-extracts the block, so re-run that if the map changes.

### 3. New Wolf and Elder Dragon portraits

- **Wolf** — redrawn as a snarling side profile: layered ear shapes with dark inner ears, a lighter ruff, angled gold eyes, muzzle with nose and fangs, and a wider ground shadow.
- **Elder Dragon** — redrawn from a plain oval into a proper dragon head: swept-back horns with lighter inner ridges, a brow ridge, a scaled snout with a defined nostril bridge, four teeth over a pale jaw line, glowing gold eyes with slit pupils and a heavy brow, and a jaw crease.

**On using a Minecraft Elder Dragon image:** that art is owned by Mojang/Microsoft, and copying it into this repository would put your public GitHub project at risk of a takedown or DMCA claim — and you'd need a separate licence to redistribute it. Everything in this project is original inline SVG, so I drew the dragon from scratch instead. If you want a licensed dragon image later, the clean route is to buy one from an asset store (e.g. itch.io art packs), drop the PNG in `icons/`-style art, and point `MONSTER_ART` at it — the portrait pipeline doesn't care whether it's SVG or a file.

### Catalogue-drift guard

While testing I found the two item catalogues had drifted: `items.py` defines 5 shields (`Iron Shield`, `Tower Shield`, `Magic Shield`, `Dragon Shield`, `Aegis Shield`) that **do not exist in `js/items.js`**. Nothing sells them yet, so it was harmless — but if they get added to `shop.py` without `js/shop.js`, the PWA would call `createItem()` for an unknown name, get `null`, push `null` into the inventory, and the next inventory/shop render would throw.

Both builds now refuse the purchase instead:

```python
if not get_item(item_name):
    gs["log"] = ["That item is not available."]
    return show_shop(shop_name)
```
```js
if (!getItem(item)) {
    gs.log = ["That item is not available."];
    return showShop(gs.shop_name);
}
```

The check runs **before** `spend_gold()`, so gold is never taken for an item that can't be created. Covered by a test that lists a fake item in the Armorer, buys it, and asserts: the shop stays open, gold is unchanged, nothing null lands in the inventory, and the inventory still renders.

**Rule for adding items:** define in **both** `items.py` and `js/items.js`, and sell in **both** `shop.py` and `js/shop.js`. With the guard in place a forgotten entry degrades to "not available" rather than a crash.

### Files changed
- `index.html` — shop panels, new `drawMap` + scenery helpers, Wolf and Elder Dragon art
- `templates/index.html` — the same map block (via sync script), XP bar colour
- `js/game.js`, `game_server.py` — purchase message now reads `Bought 1 × Shield for 25g!`, plus the catalogue-drift guard
- `sw.js` — `CACHE_VERSION` → `dnd-pwa-v4`

## Flask Build Verification & Run-State Reset Fix

### Does `python game_server.py` still work? Yes — verified end to end

The Flask build was exercised over real HTTP against a live `py game_server.py`, not just assumed. All 29 checks passed:

| Area | Checks |
|---|---|
| Page | `GET /` 200, template contains the new illustrated map, no PWA manifest/SW leaked into it |
| Menu | `/state` → main_menu with **no Quit** |
| Creation | `/create_form` reports the new base HP (15 / 13 / 11 / 13) |
| Start | `/start` → town, payload has `enemy` and `in_dungeon` |
| Combat | enemy payload present, combat log **appends** across exchanges |
| Shop | real purchase logs `Bought 1 × …` and charges gold; an unlisted item is ignored and charges nothing |
| Map | `/map_data` returns 4 locations; unreachable `/travel` refused; Village 1 reachable |
| Dungeon | entering sets `in_dungeon: true` and spawns a live enemy |

**Environment note:** the `python` on PATH here is an MSYS2 build (`C:\msys64\ucrt64\bin\python.exe`) with **no pip**, so `python game_server.py` fails with `ModuleNotFoundError: No module named 'flask'`. Flask 3.1.3 *is* installed for the Windows launcher (`py` → Python 3.14), so `py game_server.py` works — which is exactly why the README lists both forms. Install for the other one with `python -m pip install flask` (after pointing it at a real Python, e.g. `C:\Python312\python.exe -m pip install flask`).

### Bug found and fixed: run state leaked between characters

Testing hit a failure that turned out to be a real defect: **`/start` and the load-game handler never reset `dungeon_floor`.** Because `gs` is module-global and lives for the life of the process, starting a new character while a previous run sat inside the dungeon silently inherited it:

- no **Flee** option (that is dungeon-only), 
- the world map stayed hidden (`in_dungeon` true),
- and death would route to the dungeon-victory screen instead of the menu.

My test suite hit it because a previous run had left the server on floor 1. Fixed in both builds with a `reset_run()` / `resetRun()` called from new-game **and** load-game:

```python
def reset_run():
    gs["enemy"] = None
    gs["dungeon_floor"] = 0
    gs["pending_save_name"] = None
    gs["shop_name"] = None
```

Covered by tests in both suites: set `dungeon_floor = 7` with a live enemy, start a new game, then assert the floor is `0`, the enemy is gone and a fresh overworld fight offers Flee.

### Early-game death rate, measured

4,000 simulated level-1 fights against the first overworld monster, using the real combat code:

| Class | Trials | Win | **Death** | Avg HP | Avg rounds | Avg potions |
|---|---|---|---|---|---|---|
| Fighter | 1019 | 99.4% | **0.6%** | 16.3 | 5.2 | 0.40 |
| Cleric | 986 | 99.1% | **0.9%** | 14.3 | 6.4 | 0.39 |
| Wizard | 1041 | 91.9% | **8.1%** | 12.2 | 6.9 | 1.27 |
| Rogue | 954 | 91.4% | **8.6%** | 14.2 | 6.9 | 1.05 |
| **All** | 4000 | 95.5% | **4.5%** | | | |

Without drinking potions the death rate jumps to **31.1%** — the 15 starting potions are doing most of the work. Rogue and Wizard are the fragile ones: lowest base HP *and* the weakest starting weapons (Dagger `1d4`, Staff `1d6`) so fights last longer (6.9 rounds vs 5.2).

The remaining risk is a bad CON roll: `CON 3` gives a −4 modifier, so a fresh character starts at Fighter 11 / Rogue 9 / Wizard 7 / Cleric 9 HP against level-1 monsters averaging 4–6 damage per hit.

If you want it even safer, the cheapest options are a **minimum starting HP floor** (e.g. never below 12), or **healing to full after every overworld fight**. Neither is implemented — flagged as data, not changed.

## Quests, Selling, Drops & 60 New Items

### 1. Selling at any NPC

Every NPC now buys items at **20% under the cheapest price that item sells for**:

```python
SELL_RATIO = 0.8
def sell_price(item_name):
    item = create_item(item_name)
    if item is None or is_material(item):
        return None                      # quest materials are not for sale
    prices = [shop["items"][item_name]["price"]
              for shop in SHOP_NPCS.values() if item_name in shop["items"]]
    return int(min(prices) * SELL_RATIO) if prices else None
```

- New `/sell` endpoint (Flask) and `Game.sellItem()` (PWA); the shop screen gained a **Buy / Sell** tab
- Equipped gear is listed too, marked *(equipped)*, and selling it recomputes AC and max HP immediately
- **Quest materials return `None`** — they can only be turned in
- Nothing is removed from the catalogue, so `sellPrice()` is derived rather than stored

### 2. The "last weapon" warning

Selling the only weapon or the only armour you own is a trap, so it asks first:

```
That is your last weapon - you will have nothing equipped!
Selling it leaves that slot empty.        [Cancel]  [Continue]
```

`isLastOfItsKind()` counts the item in storage **plus** the equipped slot, and only warns for weapons and armour (selling your last potion should not nag). Cancel leaves everything untouched; Continue performs the sale. This also forced a real fix: `sellItem()` originally only searched the inventory, so **you could not sell your equipped gear at all** — exactly the case the warning exists for.

### 3. Monster drops → quest materials

| Monster | Drops |
|---|---|
| Goblin | Metal Fragments |
| Spider | Web String |
| Slime | Slime Ball |
| Zombie | Rotten Flesh |
| Skeleton | Bone |
| Wolf | Fur |
| Ghost | Plasma |

`DROPS` maps monster → material; `Enemy.roll_drop()` returns `(material, count)` or `None` (75% chance, 1–3 pieces). Bosses deliberately drop nothing yet. Drops are added in `combat_reward()` and written to the log: `Collected 2 × Bone!`

Quest materials are marked with `effect="material"`, exposed as `MATERIALS` / `is_material()`, which is what makes them unsellable.

### 4. Three repeatable quest givers (Town only)

New `quests.py` / `js/quests.js`. NPC **names are rolled fresh on every new run** from a first-name + epithet pool, so campaigns do not all feature the same quest givers.

| NPC role | Quests |
|---|---|
| Alchemist | Plasma ×8 (260g/140xp) · Slime Ball ×8 (220g/120xp) |
| Bone Collector | Bone ×10 (300g/160xp) · Rotten Flesh ×8 (200g/110xp) |
| Trapper | Fur ×10 (280g/150xp) · Web String ×8 (210g/115xp) · Metal Fragments ×10 (320g/170xp) |

Flow: `Town → Quests (new 5th option) → NPC → [Accept] → farm → return → [Turn in]`. Completing keeps the quest accepted, so it can be handed in again indefinitely.

**Bug fixed while testing:** a quest that levelled you up dropped you back in Town (`after_combat()`) instead of the NPC you were standing at. `gs["return_to"]` now records where to come back to, and `after_combat()` honours it.

### 5. 30 new weapons and 30 new armours

The catalogue went from 42 to **109 items** (48 weapons, 49 armours/shields, 12 items). Both catalogues were generated from one source of truth and then compared **field by field**:

```
JS : {"weapon":48,"armor":49,"item":12} total 109 | materials 7
PY : {"weapon":48,"armor":49,"item":12} total 109 | materials 7
compared 109 items: 0 field diffs, 0 stock diffs
CATALOGUES IN SYNC
```

That check immediately caught **two real bugs in my own generator** and **one pre-existing drift**:

1. **`Armor(name, ac, type, dex_limit, properties, stats_bonus)` is positional.** Writing `Armor("Steel Plate", 17, "heavy", {"CON": 1})` puts the stat bonus in the **`dex_limit`** slot, and `Armor("Shadowcloth", 12, "light", ["magic"])` puts the property list there instead. About 17 armours had a broken DEX limit and empty `properties` in **both** languages. Both writers now emit explicit `None`/`null` placeholders.
2. Empty property lists were emitted as `[]`, which is truthy in JS and again shifted the arguments.
3. The 5 shields added by hand to `items.py` (Iron/Tower/Magic/Dragon/Aegis) were **missing from `js/items.js`** — the drift reported earlier. They are now mirrored and verified.

New items are level-gated and stocked in the Weaponsmith (18), Archer (7), Wizard (5) and Armorer (30). No crafting recipes were added, per request.

### 6. Map clicks fixed

Hovering/clicking a marker did the wrong thing: the **visible** circle was painted on top of the invisible hit area and had no `onclick`, so clicking the middle of a node did nothing while the ring around it worked.

Each node is now **one `<g>` that carries the click**, containing the big transparent hit area, the marker, the glyph and the label pill:

```js
const attrs = clickable ? ` class="mn" style="cursor:pointer" onclick="travel('${id}')"` : ` class="mn"`;
```

Clicks on any part of the node — centre, glyph or label — bubble to the group and travel. The pulsing current-location ring was also moved out of the node loop and given `pointer-events="none"` so it can never intercept a click. Verified in the browser: clicking the r=9 visible circle now travels correctly.

### Files changed
- `items.py`, `js/items.js` — +30 weapons, +30 armours, 7 materials, `MATERIALS`/`is_material()`, 5 shields mirrored
- `shop.py`, `js/shop.js` — new stock, `SELL_RATIO` + `sell_price()`/`sellPrice()`
- `enemy.py`, `js/enemy.js` — `DROPS`, `roll_drop()`
- `quests.py`, `js/quests.js` (new) — quest givers, quests, random names
- `game_server.py`, `js/game.js` — `/sell`, quest screens/handlers, drop collection, `return_to`
- `index.html`, `templates/index.html` — Buy/Sell tabs, last-weapon warning, quest routing, map node groups
- `sw.js` — `CACHE_VERSION` → `dnd-pwa-v5`, `js/quests.js` added to the precache
- `README.md` — selling, drops, quests, boss-drop ideas, new item counts

### Verification
- Node suite: 109-item catalogue, drop table, sell prices, equipped-gear sale, quest accept → collect → hand in → repeat, plus everything from before
- Catalogue parity: every field of every item compared between Python and JS
- Flask HTTP suite: quest hub → accept → hand in, `/sell` (including equipped weapon, AC drop 16 → 13), unsellable materials, and a live fight loop that collected 7 materials in 15 kills (matches the 75% rate)
- Browser: sell tab lists equipped gear with prices, warning + Continue sells and unequips, Cancel changes nothing, map clicks travel

## To Do
- **Export / import saves** as a file (see "Saves: where they live" above) so characters can be backed up and moved between devices
- Quest system (quest lines with objectives and rewards)
- Crafting system (craft items using enemy drops)
- More items (scrolls, rings, materials, etc.)
- More races and classes
- Skills in combat (special abilities and actions)
- More potions (variety of consumables)
- Sell back items to shop
- Difficulty scaling options
