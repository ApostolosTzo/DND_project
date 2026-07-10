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

## To Do
- Maps (towns and dungeons to explore)
- Dungeon floors (multi-floor dungeons with bosses on final floor)
- Quest system (quest lines with objectives and rewards)
- Crafting system (craft items using enemy drops)
- More items (scrolls, rings, materials, etc.)
- More races and classes
- Skills in combat (special abilities and actions)
- More potions (variety of consumables)
- Sell back items to shop
- Difficulty scaling options ==> idk cause the game is scaling
