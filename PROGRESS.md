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

## To Do
### Location-specific shops
- Each location now has a `shops` list in `world_map.py`
- **Town**: all 5 NPCs (Potion Merchant, Weaponsmith, Armorer, Archer, Wizard)
- **Village 2**: Potion Merchant only
- **Village 1**: Weaponsmith and Armorer
- **Dungeon**: no shops
- Villages now use the town screen (fight/shop/inventory/save) instead of a generic "location" screen — only the available shops change per location
- Screen title dynamically shows the location name via `town_name()` helper function
- `shop_state()` and `shop_select_action()` filter shop names by `LOCATIONS[current_location].shops`
- Terminal version (main.py) unaffected — no map/location system there

### Files changed
- `world_map.py` — added `shops` list to each location
- `game_server.py` — `shop_state()`/`shop_select_action()` filter by current location's shops, `/travel` uses town screen for villages, added `town_name()` helper, removed auto-location-set from `respond()`, explicit `current_location` in `start_game`/`load_action`, all town-screen titles use `town_name()`

- Interactive locations on map (town/village/dungeon gameplay)
- Dungeon floors (multi-floor dungeons with bosses on final floor)
- Quest system (quest lines with objectives and rewards)
- Crafting system (craft items using enemy drops)
- More items (scrolls, rings, materials, etc.)
- More races and classes
- Skills in combat (special abilities and actions)
- More potions (variety of consumables)
- Sell back items to shop
- Difficulty scaling options ==> idk cause the game is scaling
