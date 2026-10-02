from flask import Flask, render_template, jsonify, request
from player import Player, create_character, make_character, STAT_ORDER, CLASSES, RACES
from items import (ITEMS, create_item, get_item, is_material, is_potion, heal_amount,
                   is_two_handed, two_handed_bonus, damage_type, element_of,
    usable_by, item_classes, ALL_CLASSES)
from enemy import generate_enemy, generate_dungeon_enemy
from dice import roll
from save_load import save_game, load_game, list_saves, save_exists
from world_map import LOCATIONS
from quests import QUESTS, roll_quest_npcs, quests_for
from shop import SHOP_NPCS, sell_price, NPC_CLASS, NPC_NOTE

app = Flask(__name__)

# The town menu. Keep in step with templates/index.html handleClick().
TOWN_OPTIONS = ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"]
# No "Quit" on the main menu: it never did anything, and everything else in
# the game is reachable from the town screen's Quit option.
MENU_OPTIONS = ["New Game", "Load Game"]

gs = {
    "player": None,
    "enemy": None,
    "screen": "main_menu",
    "log": [],
    "pending_stat_boost": None,
    "pending_save_name": None,
    "current_location": None,
    "dungeon_floor": 0,
    "shop_mode": "buy",
    "quest_npcs": [],
    "quest_accepted": {},
    "quest_done": {},
    "quest_npc_index": 0,
    "return_to": None,
    # Damage dealt on the last exchange, or None for a miss. The UI draws it
    # as a floating number over the monster's health bar, then clears it.
    "last_damage": None,
}

def player_json(p):
    if not p:
        return None
    return {
        "name": p.name,
        "race": p.race,
        "class": p.class_name,
        "level": p.level,
        "hp": p.hp,
        "max_hp": p.max_hp,
        "ac": p.ac,
        "gold": p.gold,
        "xp": p.xp,
        "xp_to_next": p.xp_to_next(),
        "weapon": p.weapon.name if p.weapon else "None",
        "armor": p.armor.name if p.armor else "None",
        "offhand": p.offhand.name if p.offhand else "None",
        "hands_full": p.hands_full(),
        "stats": p.stats,
        "effective_stats": p.effective_stats(),
        "stat_bonuses": p.get_equipment_stat_bonus(),
    }

def enemy_json(e):
    if not e:
        return None
    return {
        "name": e.name,
        "level": e.level,
        "hp": e.hp,
        "max_hp": e.max_hp,
        "ac": e.ac,
    }

# Function to respond with the current game state

def town_name():
    # Get the name of the current location based on the game state. 
    # If the current location is not set, default to "Town".
    loc = LOCATIONS.get(gs["current_location"])
    return loc["name"] if loc else "Town"

def respond(screen, title, body, options, extra=None):
    gs["screen"] = screen
    out = {
        "screen": screen,
        "title": title,
        "body": body,
        "options": options,
        "player": player_json(gs["player"]),
        "enemy": enemy_json(gs["enemy"]),
        "in_dungeon": gs["dungeon_floor"] > 0,
        "log": gs["log"],
        # Include the current location in the response
        "current_location": gs["current_location"],
        "last_damage": gs["last_damage"],
    }
    if extra:
        out.update(extra)
    return jsonify(out)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/state")
def get_state():
    gs["log"] = []
    return respond("main_menu", "DUNGEONS & DRAGONS", "", ["New Game", "Load Game"])

@app.route("/create_form")
def create_form():
    race_list = []
    for r in RACES:
        bonuses = RACES[r]["bonuses"]
        bonus_str = ", ".join(f"{s}+{v}" for s, v in bonuses.items())
        race_list.append((r, f"{r} - {RACES[r]['desc']}", bonus_str))
    class_list = []
    for c in CLASSES:
        class_list.append((c, f"{c} - {CLASSES[c]['desc']}", CLASSES[c]["hp"], CLASSES[c]["primary"]))
    return jsonify({"races": race_list, "classes": class_list})

# Clears anything left over from a previous run: a live enemy, a half-finished
# dungeon crawl, a pending overwrite prompt or the last shop. Without this, a
# new game (or a loaded save) started while the previous run was inside the
# dungeon would silently inherit that state - no Flee option, and the world map
# would stay hidden.
def reset_run():
    gs["enemy"] = None
    gs["dungeon_floor"] = 0
    gs["pending_save_name"] = None
    gs["shop_name"] = None
    gs["shop_mode"] = "buy"
    # Fresh quest givers and a clean quest log for every new run.
    gs["quest_npcs"] = roll_quest_npcs()
    gs["quest_accepted"] = {}
    gs["quest_done"] = {}
    gs["quest_npc_index"] = 0
    gs["return_to"] = None
    gs["last_damage"] = None

@app.route("/start", methods=["POST"])
def start_game():
    data = request.json
    name = data.get("name", "Adventurer")
    race = data.get("race", "Human")
    class_name = data.get("class", "Fighter")
    reset_run()
    gs["player"] = make_character(name, race, class_name)
    gs["screen"] = "town"
    gs["current_location"] = "town"
    gs["log"] = ["Welcome, adventurer!"]
    return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])

# Function to handle player actions
# locations and their connections are defined in world_map.py
@app.route("/action", methods=["POST"])
def handle_action():
    data = request.json
    choice = data.get("choice", 0)

    # Determine the current screen and call the appropriate action handler
    
    if gs["screen"] == "town":
        return town_action(choice)
    elif gs["screen"] == "combat":
        return combat_action(choice)
    elif gs["screen"] == "combat_item":
        return combat_item_action(choice)
    elif gs["screen"] == "shop_select":
        return shop_select_action(choice)
    elif gs["screen"] == "shop":
        return shop_action(choice)
    elif gs["screen"] == "inventory":
        return inventory_action(choice)
    elif gs["screen"] == "stat_allocation":
        return allocation_action(choice)
    elif gs["screen"] == "save_menu":
        gs["screen"] = "town"
        gs["log"] = []
        return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])
    elif gs["screen"] == "confirm_overwrite":
        if choice == 0:
            return force_save()
        gs["screen"] = "town"
        gs["pending_save_name"] = None
        gs["log"] = []
        return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])
    elif gs["screen"] == "load_menu":
        return load_action(choice)
    elif gs["screen"] == "quest_hub":
        return quest_hub_action(choice)
    elif gs["screen"] == "quest_npc":
        return quest_npc_action(gs.get("quest_npc_index", 0), choice)
    # Handle location travel
    elif gs["screen"] == "location":
        gs["screen"] = "town"
        gs["log"] = []
        return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])
    elif gs["screen"] == "dungeon":
        if choice == 0:
            return enter_dungeon()
        gs["screen"] = "town"
        gs["log"] = []
        return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])
    elif gs["screen"] == "dungeon_floor":
        return dungeon_floor_action(choice)
    elif gs["screen"] == "dungeon_victory":
        gs["dungeon_floor"] = 0
        gs["current_location"] = "village1"
        gs["screen"] = "town"
        gs["log"] = ["You return to Village 1, victorious!"]
        return respond("town", "Village 1", "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])
    elif gs["screen"] == "game_over":
        gs["player"] = None
        gs["enemy"] = None
        gs["dungeon_floor"] = 0
        gs["screen"] = "main_menu"
        gs["log"] = []
        return respond("main_menu", "DUNGEONS & DRAGONS", "", ["New Game", "Load Game"])

    return get_state()

@app.route("/save", methods=["POST"])
def do_save():
    p = gs["player"]
    if not p:
        return get_state()
    data = request.json
    name = data.get("name", p.name)
    if save_exists(name):
        gs["screen"] = "confirm_overwrite"
        gs["pending_save_name"] = name
        gs["log"] = [f"Save '{name}' already exists. Overwrite?"]
        return respond("confirm_overwrite", "Overwrite Save?", f"Save '{name}' already exists. Overwrite?", ["Yes", "No"])
    save_game(p, name)
    p.current_save = name
    gs["log"] = [f"Game saved as '{name}'!"]
    return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])

@app.route("/force_save", methods=["POST"])
def force_save():
    p = gs["player"]
    if not p or not gs["pending_save_name"]:
        return get_state()
    name = gs["pending_save_name"]
    gs["pending_save_name"] = None
    save_game(p, name)
    p.current_save = name
    gs["screen"] = "town"
    gs["log"] = [f"Game saved as '{name}'!"]
    return respond("town", "Saved!", "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])

# ---- Town ----
def town_action(choice):
    p = gs["player"]
    if not p:
        return get_state()

    if choice == 0:  # Fight
        e = generate_enemy(p.level)
        gs["enemy"] = e
        gs["screen"] = "combat"
        gs["log"] = [f"A wild {e.name} appears!"]
        return combat_state()

    elif choice == 1:  # Shop
        gs["screen"] = "shop_select"
        gs["log"] = []
        return shop_state()

    elif choice == 2:  # Inventory
        gs["screen"] = "inventory"
        gs["log"] = []
        return inventory_state()

    elif choice == 3:  # Save
        gs["screen"] = "save_menu"
        default = p.current_save or p.name
        return respond("save_menu", "Save Game", "", [f"Save as '{default}'", "(Back)"])

    elif choice == 4:  # Quests
        return quest_hub_state()

    elif choice == 5:  # Quit
        gs["player"] = None
        gs["enemy"] = None
        gs["screen"] = "main_menu"
        gs["log"] = []
        return respond("main_menu", "DUNGEONS & DRAGONS", "", ["New Game", "Load Game"])

    return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])

#==============================
# ---- Combat ----
#=============================
def prof_bonus(p):
    """Proficiency bonus, shared by the main-hand and off-hand rolls."""
    return (p.level - 1) // 4 + 2

# Half damage, rounded down, never less than 1.
OFFHAND_DAMAGE_DIVISOR = 2

def has_offhand_weapon(p):
    """A weapon in the off-hand gets its own attack this turn.

    A shield is not a weapon, so it contributes no extra swing.
    """
    return bool(p and p.offhand and p.offhand.category == "weapon")

def weapon_mod(p, weapon):
    """Which stat an attack with this weapon uses."""
    if weapon and ("finesse" in weapon.properties or "ranged" in weapon.properties):
        return p.modifier("DEX")
    return p.modifier("STR")

def attack_roll_info(p, weapon, is_offhand):
    """One line of "what am I about to roll", used by the dice tray."""
    mod = weapon_mod(p, weapon)
    full = mod + (0 if is_offhand else two_handed_bonus(weapon))
    return {
        "label": "Off-hand Attack" if is_offhand else "Attack",
        "weapon": weapon.name if weapon else "Bare hands",
        "hit_die": "1d20",
        "hit_bonus": prof_bonus(p) + mod,
        "mod": mod,
        "damage_die": weapon.damage_dice if weapon else "1",
        # Only the off-hand is halved - the main hand keeps its full bonus.
        "damage_bonus": (full // OFFHAND_DAMAGE_DIVISOR if is_offhand else full),
        "type": damage_type(weapon.damage_type) if weapon else None,
        "offhand": bool(is_offhand),
    }

def combat_state():
    e = gs["enemy"]
    p = gs["player"]
    status = e.status_text()
    header = e.display() + (f"\n{status}" if status else "")
    body = f"{header}\n\n{player_json(p)['name']}: HP {p.hp}/{p.max_hp}  AC {p.ac}"

    # Attacks are not list options any more: they live in the dice tray as
    # Roll buttons, so this list only holds what has no dice attached.
    options = ["Use Item"]
    if gs["dungeon_floor"] == 0:
        options.append("Flee")

    # Everything the dice tray needs to show the pending rolls.
    attacks = [attack_roll_info(p, p.weapon, False)]
    if has_offhand_weapon(p):
        attacks.append(attack_roll_info(p, p.offhand, True))

    return respond("combat", "COMBAT", body, options, extra={"attacks": attacks})


def combat_item_list(p):
    """Everything the player could reach for mid-fight, best potion first.

    Quest materials and other drops used to be hidden here, which made the list
    look empty right after a monster dropped something useful.
    """
    counts = {}
    for item in p.inventory:
        if item in (p.weapon, p.armor, p.offhand):
            continue
        counts.setdefault(item.name, []).append(item)

    entries = [{"name": name,
                "count": len(list_),
                "heal": heal_amount(name) if is_potion(name) else 0}
               for name, list_ in counts.items()]

    def sort_key(entry):
        # Usable healing first, strongest first; then alphabetical so the list
        # does not jump around between turns.
        if entry["heal"]:
            return (0, -entry["heal"], entry["name"])
        return (1, 0, entry["name"])

    return sorted(entries, key=sort_key)


def combat_item_label(entry):
    return f"{entry['name']} x{entry['count']}" if entry["count"] > 1 else entry["name"]


def use_item_in_combat(p, name):
    """Only healing potions work in combat; everything else is refused."""
    heal = heal_amount(name)
    if not heal:
        return f"Cannot use {name} in combat yet."
    index = next((i for i, item in enumerate(p.inventory) if item.name == name), None)
    if index is None:
        return f"You don't have {name} any more."
    before = p.hp
    p.hp = min(p.hp + heal, p.max_hp)
    p.inventory.pop(index)
    return f"Drank {name}! Restored {p.hp - before} HP ({heal} attempted)."


def combat_item_state():
    """The Use Item screen, rebuilt from scratch after every use."""
    p = gs["player"]
    entries = combat_item_list(p)
    if not entries:
        gs["log"].append("You have nothing left to use.")
        return combat_state()
    options = [combat_item_label(e) for e in entries] + ["(Back)"]
    gs["screen"] = "combat_item"
    return respond("combat_item", "Use Item",
                   "Choose an item - strongest healing potion first. Items that "
                   "cannot be used in combat yet are listed greyed out.",
                   options,
                   {"combat_items": [e["name"] for e in entries]})


# One player attack, from the dice tray. is_offhand picks the off-hand
# swing; either way it costs the whole turn and the monster retaliates.
def player_attack(is_offhand=False):
    p = gs["player"]
    e = gs["enemy"]
    # A Roll button can be pressed with nothing to fight - no enemy yet, or the
    # fight already ended. Bailing out to the menu rather than reaching into a
    # None enemy, which used to 500.
    if not p or not e or not e.is_alive():
        return get_state()
    if is_offhand and not has_offhand_weapon(p):
        return combat_state()

    # The combat log accumulates: every exchange stays visible in the chat.
    gs["log"].append(web_offhand_attack(p, e) if is_offhand
                      else web_player_attack(p, e))

    if not e.is_alive():
        return combat_reward("Victory!")

    # Burn and poison bite before the monster gets to swing back.
    for line in e.tick_status():
        gs["log"].append(line)
    if not p.is_alive():
        gs["screen"] = "game_over"
        return respond("game_over", "GAME OVER", "You have died...",
                       ["Return to Menu"])
    if not e.is_alive():
        return combat_reward("Victory!")

    gs["log"].append(web_enemy_attack(p, e))
    if not p.is_alive():
        gs["screen"] = "game_over"
        return respond("game_over", "GAME OVER", "You have died...",
                       ["Return to Menu"])

    return combat_state()

def combat_action(choice):
    p = gs["player"]
    e = gs["enemy"]

    # Use Item
    if choice == 0:
        if not combat_item_list(p):
            gs["log"].append("You have nothing to use!")
            return combat_state()
        return combat_item_state()

    # Flee (not allowed in dungeon)
    elif choice == 1:
        if gs["dungeon_floor"] > 0:
            gs["log"].append("You cannot flee from the dungeon!")
            return combat_state()
        if roll("1d20") >= 10:
            gs["enemy"] = None
            gs["screen"] = "town"
            gs["log"] = ["You fled successfully!"]
            return respond("town", "Fled!", "What do you want to do?",
                           ["Fight", "Visit Shop", "Inventory", "Save Game",
                            "Quests", "Quit"])
        else:
            gs["log"].append("Failed to flee!")
            gs["log"].append(web_enemy_attack(p, e))
            if not p.is_alive():
                gs["screen"] = "game_over"
                return respond("game_over", "GAME OVER", "You have died...",
                               ["Return to Menu"])
            return combat_state()

    return combat_state()


# Use Item
def combat_item_action(choice):
    p = gs["player"]
    e = gs["enemy"]
    entries = combat_item_list(p)

    # (Back) is the only thing that leaves this screen - using an item leaves
    # you standing here so the fight does not jump back to the main menu.
    if choice >= len(entries):
        gs["screen"] = "combat"
        return combat_state()

    name = entries[choice]["name"]
    message = use_item_in_combat(p, name)
    gs["log"].append(message)

    if heal_amount(name):
        if not e.is_alive():
            return combat_reward("Victory!")
        return combat_item_state()

    # Unusable: it costs you the turn.
    gs["log"].append(web_enemy_attack(p, e))

    if not p.is_alive():
        gs["screen"] = "game_over"
        return respond("game_over", "GAME OVER", "You have died...", ["Return to Menu"])

    return combat_item_state()

# Player Attack
def web_player_attack(p, e):
    mod = weapon_mod(p, p.weapon)
    prof = prof_bonus(p)
    atk = roll("1d20") + prof + mod

    if atk >= e.ac:
        heavy = two_handed_bonus(p.weapon)
        if p.weapon:
            dmg = max(roll(p.weapon.damage_dice) + mod + heavy, 1)
        else:
            dmg = max(1 + mod, 1)
        # The weapon's damage type decides how hard this lands: skeletons
        # crumble to bludgeoning, slimes shrug off steel.
        type_name = damage_type(p.weapon.damage_type) if p.weapon else None
        total, note = e.apply_damage(dmg, type_name)
        effect = e.inflict_element(element_of(p.weapon), p)
        gs["last_damage"] = {"amount": total, "kind": "hit",
                                "weak": "WEAK" in note}
        line = (f"You hit the {e.name} for {total} damage!{note} "
                f"(d20 + {prof} + {mod} = {atk} vs AC {e.ac})")
        if heavy > 0:
            line += f" +{heavy} two-handed"
        return line + effect
    gs["last_damage"] = None   # a miss shows no floating number
    return f"You missed! (d20 + {prof} + {mod} = {atk} vs AC {e.ac})"

# Off-hand Attack
def web_offhand_attack(p, e):
    """The off-hand swing: its own hit roll, half damage.

    It is a whole turn of its own, so using it gives up the main-hand attack and
    lets the monster retaliate.
    """
    w = p.offhand
    mod = weapon_mod(p, w)
    prof = prof_bonus(p)
    atk = roll("1d20") + prof + mod

    if atk >= e.ac:
        # Half of (dice + modifier), rounded down, never less than 1. The
        # two-handed bonus is deliberately absent - it cannot be held anyway.
        full = max(roll(w.damage_dice) + mod, 1)
        dmg = max(full // OFFHAND_DAMAGE_DIVISOR, 1)
        type_name = damage_type(w.damage_type)
        total, note = e.apply_damage(dmg, type_name)
        effect = e.inflict_element(element_of(w), p)
        gs["last_damage"] = {"amount": total, "kind": "hit",
                                "weak": "WEAK" in note}
        return (f"Off-hand {w.name} hits the {e.name} for {total} damage!{note} "
                f"(d20 + {prof} + {mod} = {atk} vs AC {e.ac}, half damage)"
                + effect)

    gs["last_damage"] = None   # a miss shows no floating number
    return f"Off-hand {w.name} missed! (d20 + {prof} + {mod} = {atk} vs AC {e.ac})"

# Enemy Attack
def web_enemy_attack(p, e):
    # A frozen monster loses its whole turn.
    if e.is_frozen():
        e.status["freeze_rounds"] -= 1
        left = max(0, e.status["freeze_rounds"])
        return (f"{e.name} is frozen solid and cannot attack!"
                + (f" ({left} round{'s' if left > 1 else ''} left)" if left else ""))

    bonus = e.level // 2 + 2
    atk = roll("1d20") + bonus

    if atk >= p.ac:
        dmg = max(e.attack_damage(), 1)
        p.hp -= dmg
        if p.hp < 0:
            p.hp = 0
        return f"{e.name} hits you for {dmg} damage! (d20 + {bonus} = {atk} vs your AC {p.ac})"
    else:
        return f"{e.name} missed you! (d20 + {bonus} = {atk} vs your AC {p.ac})"

# Combat Reward
def combat_reward(title):
    p = gs["player"]
    e = gs["enemy"]
    gold = e.gold_drop()
    xp = e.xp_reward
    p.add_gold(gold)
    gs["log"] = [f"{e.name} defeated!", f"Looted {gold} gold!", f"Gained {xp} XP!"]

    if gs["dungeon_floor"] == 10:
        bonus_gold = 500
        bonus_xp = 500
        p.add_gold(bonus_gold)
        xp += bonus_xp
        gs["log"].append(f"Dungeon cleared! Bonus: {bonus_gold} gold, {bonus_xp} XP!")

    # Quest materials from the kill (bosses drop nothing yet).
    drop = e.roll_drop()
    if drop:
        material, count = drop
        for _ in range(count):
            p.add_item(create_item(material))
        gs["log"].append(f"Collected {count} × {material}!")

    grant_xp(p, xp)

    gs["enemy"] = None
    if p.skill_points > 0:
        return allocation_state()
    return after_combat()

# Add XP and run any level-ups it triggers.
def grant_xp(p, xp):
    p.xp += xp
    while p.xp >= p.xp_to_next():
        p.xp -= p.xp_to_next()
        handle_level_up()

# Level up handling
def handle_level_up():
    p = gs["player"]
    p.level += 1
    hp_gain = p.hp_per_level()
    p.max_hp += hp_gain
    p.hp = p.max_hp
    gold_r = p.level * 10
    p.add_gold(gold_r)
    gs["log"].append(f"LEVEL UP! Now level {p.level}! HP +{hp_gain}, +{gold_r} gold!")

    if p.level % 4 == 0:
        p.skill_points += 5
    else:
        p.skill_points += 1

# Stat Allocation
def allocation_state():
    p = gs["player"]
    body_lines = [f"{s}: {p.stats[s]}" for s in STAT_ORDER]
    return respond("stat_allocation", f"Allocate Skill Points ({p.skill_points} left)", "\n".join(body_lines), [f"[+] {s}" for s in STAT_ORDER])

def allocation_action(choice):
    p = gs["player"]
    if p.skill_points <= 0:
        return after_combat()
    chosen = STAT_ORDER[choice]
    old_con = p.modifier("CON")
    p.stats[chosen] += 1
    p.ac = p.calc_ac()
    if chosen == "CON":
        p.recalc_hp()
        # A CON point raises max HP and heals the character to full.
        p.hp = p.max_hp
    p.skill_points -= 1
    gs["log"] = [f"{chosen} increased to {p.stats[chosen]}!"]

    if p.skill_points <= 0:
        if p.current_save:
            save_game(p, p.current_save)
            gs["log"].append("Game autosaved!")
        return after_combat()
    return allocation_state()

#==============================
# ---- Quests (Town only) ----
#==============================
# Three repeatable quest givers live in Town. Accept a job, kill what they want,
# then bring the material back to the same NPC to collect gold and XP.

def _count_material(p, material):
    return sum(1 for item in p.inventory if item.name == material)

def _take_material(p, material, amount):
    taken = 0
    for item in list(p.inventory):
        if item.name == material and taken < amount:
            p.remove_item(item)
            taken += 1
    return taken

def quest_hub_state():
    p = gs["player"]
    if not p:
        return get_state()
    npcs = gs["quest_npcs"]
    options = []
    body = []
    for i, npc in enumerate(npcs):
        ready = 0
        for q in quests_for(i):
            key = f"{i}:{q['index']}"
            if gs["quest_accepted"].get(key) and _count_material(p, q["material"]) >= q["amount"]:
                ready += 1
        mark = f" — {ready} ready to hand in!" if ready else ""
        options.append(f"{npc['name']}{mark}")
        body.append(f"{npc['name']}: {len(quests_for(i))} standing job(s)")
    options.append("(Back)")
    return respond("quest_hub", "Quest Givers", "\n".join(body), options)

def quest_hub_action(choice):
    npcs = gs["quest_npcs"]
    if choice >= len(npcs):
        gs["return_to"] = None  # back to the town menu
        return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])
    gs["return_to"] = "quest_npc"
    gs["quest_npc_index"] = choice
    return quest_npc_state(choice)

def quest_npc_state(npc_index):
    p = gs["player"]
    if not p:
        return get_state()
    npcs = gs["quest_npcs"]
    if npc_index >= len(npcs):
        return quest_hub_state()
    gs["quest_npc_index"] = npc_index
    quests = quests_for(npc_index)
    options = []
    body = []
    for q in quests:
        key = f"{npc_index}:{q['index']}"
        have = _count_material(p, q["material"])
        accepted = gs["quest_accepted"].get(key, False)
        done = gs["quest_done"].get(key, 0)
        times = f" (handed in {done}×)" if done else ""
        body.append(f"{q['material']} ×{q['amount']}  →  {q['gold']}g, {q['xp']} XP{times}")
        if not accepted:
            options.append(f"[Accept] {q['material']} ×{q['amount']}")
        elif have >= q["amount"]:
            options.append(f"[Turn in] {q['material']} ×{q['amount']} (you have {have})")
        else:
            options.append(f"[Waiting] {q['material']} ×{q['amount']} — you have {have}")
    options.append("(Back)")
    return respond("quest_npc", npcs[npc_index]["name"], "\n".join(body), options,
                   extra={"quest_npc_index": npc_index})

def quest_npc_action(npc_index, choice):
    p = gs["player"]
    if not p:
        return get_state()
    quests = quests_for(npc_index)
    if choice >= len(quests):
        return quest_hub_state()
    q = quests[choice]
    key = f"{npc_index}:{q['index']}"

    if not gs["quest_accepted"].get(key):
        gs["quest_accepted"][key] = True
        gs["log"] = [f"You accepted: {q['material']} ×{q['amount']}"]
        return quest_npc_state(npc_index)

    have = _count_material(p, q["material"])
    if have < q["amount"]:
        gs["log"] = [f"You need {q['amount']} × {q['material']} (you have {have})."]
        return quest_npc_state(npc_index)

    _take_material(p, q["material"], q["amount"])
    p.add_gold(q["gold"])
    gs["quest_done"][key] = gs["quest_done"].get(key, 0) + 1
    gs["log"] = [
        f"Quest complete: {q['material']} ×{q['amount']}!",
        f"Paid {q['gold']} gold and {q['xp']} XP.",
    ]
    grant_xp(p, q["xp"])
    if p.skill_points > 0:
        return allocation_state()
    return quest_npc_state(npc_index)

#==============================
# ---- Shop ----
#==============================
from shop import SHOP_NPCS

# Shop State
def shop_state():
    loc_id = gs["current_location"] # Get the current location ID from the game state
    loc = LOCATIONS.get(loc_id, {}) # Get the current location data from LOCATIONS
    # Get the list of shops available at the current location, 
    # defaulting to all shops if none are specified
    shop_names = loc.get("shops", list(SHOP_NPCS.keys())) 
    # If there are no shops available at the current location, 
    # set the log message and return to the town screen
    if not shop_names: 
        gs["log"] = ["No shops here."]
        return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])
    return respond("shop_select", "Which shop?", "", shop_names + ["(Back)"])

# Shop Select Action
def shop_select_action(choice):
    loc_id = gs["current_location"]
    loc = LOCATIONS.get(loc_id, {})
    shop_names = loc.get("shops", list(SHOP_NPCS.keys()))
    # If the choice is out of bounds (e.g., "(Back)" option), return to town
    if choice >= len(shop_names): 
        gs["screen"] = "town"
        return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])

    # If a valid shop is selected, set the current shop in the game state and show the shop interface
    shop_name = shop_names[choice]
    gs["shop_name"] = shop_name
    return show_shop(shop_name)

def shop_action(choice):
    if gs["dungeon_floor"] > 0:
        gs["screen"] = "dungeon_floor"
        return dungeon_floor_state()
    loc_id = gs["current_location"]
    loc = LOCATIONS.get(loc_id, {})
    shop_names = loc.get("shops", list(SHOP_NPCS.keys()))
    gs["screen"] = "shop_select"
    return respond("shop_select", "Which shop?", "", shop_names + ["(Back)"])

@app.route("/shop_buy", methods=["POST"])
def shop_buy():
    p = gs["player"]
    data = request.json
    item_name = data["item"]
    qty = data["qty"]
    shop_name = gs["shop_name"]
    shop = SHOP_NPCS.get(shop_name)
    if not shop or item_name not in shop["items"]:
        return show_shop(shop_name)

    # Guard: a shop can list an item that items.py does not define (the two
    # catalogues can drift). Without this, create_item() returns None, None lands
    # in the inventory and the next inventory/shop render raises.
    item = get_item(item_name)
    if not item:
        gs["log"] = ["That item is not available."]
        return show_shop(shop_name)

    # The UI already greys another class's weapons out, but this is the guard
    # that matters: without it the flag is decoration and /shop_buy will happily
    # sell a Fighter a Frost Staff.
    if not usable_by(item, p.class_name):
        gs["log"] = [f"{item_name} is a {shop.get('class') or 'other'} weapon - "
                     f"{NOT_YOUR_WEAPON}."]
        return show_shop(shop_name)

    price = shop["items"][item_name]["price"]
    total = price * qty
    if p.spend_gold(total):
        for _ in range(qty):
            p.add_item(create_item(item_name))
        gs["log"] = [f"Bought {qty} × {item_name} for {total}g!"]
    else:
        gs["log"] = [f"Not enough gold! Need {total}g, you have {p.gold}g."]

    return show_shop(shop_name)

@app.route("/sell", methods=["POST"])
def sell_item():
    """Sell one item to the NPC you are standing at, at 20% under shop price."""
    p = gs["player"]
    if not p:
        return get_state()
    data = request.json
    item_name = data.get("item")
    price = sell_price(item_name)
    if not price:
        gs["log"] = ["Nobody wants to buy that."]
        return show_shop(gs.get("shop_name") or next(iter(SHOP_NPCS)))

    index = next((i for i, item in enumerate(p.inventory) if item.name == item_name), None)
    if index is not None:
        item = p.inventory.pop(index)
    elif p.weapon and p.weapon.name == item_name:
        item, p.weapon = p.weapon, None
    elif p.armor and p.armor.name == item_name:
        item, p.armor = p.armor, None
    elif p.offhand and p.offhand.name == item_name:
        item, p.offhand = p.offhand, None
    else:
        gs["log"] = ["You don't have that any more."]
        return show_shop(gs.get("shop_name") or next(iter(SHOP_NPCS)))

    # Selling equipped gear leaves you unequipped until you equip something else.
    if item is p.weapon or item is p.armor or item is p.offhand:
        p.ac = p.calc_ac()
        p.recalc_hp()

    p.add_gold(price)
    gs["log"] = [f"Sold {item.name} for {price}g."]
    return show_shop(gs.get("shop_name") or next(iter(SHOP_NPCS)))

# Shown next to a greyed-out item when the stall belongs to another class.
NOT_YOUR_WEAPON = "not your class's weapon"


def shop_class_flags(p, shop, available):
    """Which of the listed items this character is allowed to buy.

    Every armory stocks its own gear plus the universal ranged kit, so a Fighter
    walking into the Wizard's stall sees the Wizard's staves greyed out while
    the bows and the plain Wand stay buyable. The UI renders these as disabled
    rows with NOT_YOUR_WEAPON; shop_buy re-checks server-side so the flag is a
    display convenience and never the only guard.
    """
    flags = []
    for name in available:
        item = get_item(name)
        flags.append(item is None or usable_by(item, p.class_name))
    return flags


def show_shop(shop_name):
    p = gs["player"]
    shop = SHOP_NPCS[shop_name]
    available = {n: d for n, d in shop["items"].items() if p.level >= d["min_level"]}
    items_list = [f"{n} ({d['price']}g)" for n, d in available.items()]
    return respond("shop", shop_name, NPC_NOTE.get(shop_name, ""),
                   items_list + ["(Back)"],
                   extra={"shop_items": list(available.keys()),
                          "shop_prices": [d["price"] for d in available.values()],
                          # Only potions get the quantity stepper.
                          "shop_potions": [is_potion(n) for n in available.keys()],
                          # False = greyed out, this class cannot wield it.
                          "shop_usable": shop_class_flags(p, shop, available),
                          "shop_npc_class": NPC_CLASS.get(shop_name)})

# ---- Inventory ----
def inventory_state():
    p = gs["player"]
    lines = []
    if p.weapon:
        lines.append(f"Weapon: {p.weapon.name}")
    if p.armor:
        lines.append(f"Armor: {p.armor.name}")
    if p.offhand:
        lines.append(f"Off-hand: {p.offhand.name}")
    if p.hands_full():
        lines.append("(both hands are full)")

    storage = [item for item in p.inventory if item != p.weapon and item != p.armor and item != p.offhand]
    grouped = {}
    for item in storage:
        grouped.setdefault(item.name, []).append(item)

    storage_lines = []
    for name, items_list in grouped.items():
        storage_lines.append(f"{name} x{len(items_list)}" if len(items_list) > 1 else name)

    # Per-item reason an Equip button should be disabled, so the panel can
    # explain the refusal instead of letting the player hit a dead end.
    blocked = {}
    for name, item_list in grouped.items():
        refusal = equip_refusal(p, item_list[0])
        if refusal:
            blocked[name] = refusal

    body = "Equipped:\n  " + ("\n  ".join(lines) if lines else "None") + "\n\nStorage:\n  " + ("\n  ".join(storage_lines) if storage_lines else "(empty)")
    gs["screen"] = "inventory"
    options = list(storage_lines) + ["(Close)"] if storage_lines else ["(Close)"]
    return respond("inventory", "INVENTORY", body, options,
                   extra={"inv_items": list(grouped.keys()),
                          "inv_blocked": blocked})

def equip_target_for(p, item):
    """Which slot an item would go into when equipped.

    Weapons are the interesting case. A two-handed weapon always takes the main
    hand and hands the off-hand back; a one-handed weapon takes the main hand if
    it is free, otherwise the off-hand (that is how you end up dual-wielding),
    and only replaces the main hand once both hands are busy.
    """
    if item.category == "weapon":
        if is_two_handed(item):
            return "weapon"
        if not p.weapon:
            return "weapon"
        if is_two_handed(p.weapon):
            return "weapon"      # main hand owns both
        if not p.offhand:
            return "offhand"
        return "weapon"
    if item.category == "armor":
        if item.armor_type == "shield":
            return "offhand"
        return "armor"
    return None

def equip_refusal(p, item):
    """Why this item cannot be equipped right now, or None if it can."""
    slot = equip_target_for(p, item)
    if slot is None:
        return None
    if slot == "offhand" and not p.can_equip_offhand(item):
        return p.offhand_block_reason() or "That cannot go in your off-hand."
    return None

def inventory_action(choice):
    """Selecting an entry never equips or drinks anything - it only opens the
    detail panel. The Equip and Use buttons call the routes below."""
    p = gs["player"]
    storage = [item for item in p.inventory if item != p.weapon and item != p.armor and item != p.offhand]
    grouped = {}
    for item in storage:
        grouped.setdefault(item.name, []).append(item)

    names = list(grouped.keys())
    if not names or choice >= len(names):
        gs["screen"] = "town"
        return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])

    return inventory_state()

def _remove_one(p, name):
    index = next((i for i, item in enumerate(p.inventory) if item.name == name), None)
    return p.inventory.pop(index) if index is not None else None

@app.route("/inventory_equip", methods=["POST"])
def inventory_equip():
    """Moves one item out of storage and into its slot."""
    p = gs["player"]
    name = (request.json or {}).get("item")
    item = get_item(name)
    if item is None:
        gs["log"] = [f"You don't have {name} any more."]
        return inventory_state()
    item = create_item(name)

    refusal = equip_refusal(p, item)
    if refusal:
        gs["log"] = [refusal]
        return inventory_state()

    slot = equip_target_for(p, item)
    if _remove_one(p, name) is None:
        gs["log"] = [f"You don't have {name} any more."]
        return inventory_state()

    if slot == "weapon":
        if p.weapon:
            p.inventory.append(p.weapon)
        p.weapon = item
        stowed = p.stow_offhand() if is_two_handed(item) else None
        p.ac = p.calc_ac()
        p.recalc_hp()
        gs["log"] = [f"Equipped {item.name}!" +
                     (f" {stowed.name} went back to storage." if stowed else "")]
    elif slot == "armor":
        if p.armor:
            p.inventory.append(p.armor)
        p.armor = item
        p.ac = p.calc_ac()
        p.recalc_hp()
        gs["log"] = [f"Equipped {item.name}!"]
    elif slot == "offhand":
        old = p.offhand
        p.offhand = item
        if old:
            p.inventory.append(old)
        p.ac = p.calc_ac()
        p.recalc_hp()
        gs["log"] = [f"Equipped {item.name} in your off-hand!"]
    else:
        p.inventory.append(item)
        gs["log"] = [f"You cannot equip {item.name}."]

    return inventory_state()

@app.route("/inventory_use", methods=["POST"])
def inventory_use():
    """Drinks a potion out of combat."""
    p = gs["player"]
    name = (request.json or {}).get("item")
    if not is_potion(name):
        gs["log"] = [f"Cannot use {name} yet."]
        return inventory_state()
    if _remove_one(p, name) is None:
        gs["log"] = [f"You don't have {name} any more."]
        return inventory_state()
    before = p.hp
    heal = heal_amount(name)
    p.hp = min(p.hp + heal, p.max_hp)
    gs["log"] = [f"Drank {name}! Restored {p.hp - before} HP ({heal} attempted)."]
    return inventory_state()

# ---- Load Game ----
@app.route("/load_list")
def load_list():
    saves = list_saves()
    gs["screen"] = "load_menu"
    if not saves:
        return respond("main_menu", "No saves found", "", ["New Game", "Load Game"])
    options = [f"{s[1]} {s[2]} {s[3]} Lv.{s[4]}" for s in saves]
    return respond("load_menu", "Load Game", "", options + ["(Back)"])

def load_action(choice):
    saves = list_saves()
    if choice >= len(saves):
        gs["screen"] = "main_menu"
        gs["log"] = []
        return respond("main_menu", "DUNGEONS & DRAGONS", "", ["New Game", "Load Game"])

    name = saves[choice][0]
    player = load_game(name)
    reset_run()
    player.current_save = name
    gs["player"] = player
    gs["enemy"] = None
    gs["screen"] = "town"
    gs["current_location"] = "town"
    gs["log"] = [f"Loaded '{name}'!"]
    return respond("town", "Game Loaded!", "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])

#================================
# ---- Map ----
#================================
# This section handles the world map data and travel between locations. 
# The locations and their connections are defined in world_map.py.
def _item_details():
    """Flat catalogue for the UI's detail panels.

    Mirrors what js/items.js exposes to the PWA: damage and damage type, the
    two-handed bonus, the element a weapon carries, and whether an item can be
    used. The inventory additionally annotates offhand_block per equipped item.
    """
    out = {}
    for name, item in ITEMS.items():
        entry = {"category": item.category}
        if item.category == "weapon":
            entry["damage"] = item.damage_dice
            entry["type"] = damage_type(item.damage_type)
            entry["two_handed"] = two_handed_bonus(item)
            entry["element"] = element_of(item)
            entry["properties"] = item.properties
            # Which class may wield it, so the UI can say "not your class's
            # weapon" without duplicating the armory table in JavaScript.
            classes = item_classes(item)
            entry["classes"] = classes
            entry["any_class"] = len(classes) == len(ALL_CLASSES)
        elif item.category == "armor":
            entry["ac"] = item.base_ac
            entry["kind"] = item.armor_type
        else:
            entry["description"] = item.description
            entry["heal"] = heal_amount(name)
            entry["usable"] = is_potion(name)
        if item.stats_bonus:
            entry["bonus"] = [f"{k} +{v}" for k, v in item.stats_bonus.items()]
        out[name] = entry
    return out

@app.route("/item_details")
def item_details():
    return jsonify({"items": _item_details()})

@app.route("/attack", methods=["POST"])
def attack():
    """One player attack, triggered by a Roll button in the dice tray."""
    data = request.json or {}
    return player_attack(bool(data.get("offhand")))

@app.route("/map_data")
def map_data():
    current_id = gs["current_location"]
    return jsonify({
        "locations": {k: {"name": v["name"], "x": v["x"], "y": v["y"], "type": v["type"], "connects_to": v["connects_to"]} for k, v in LOCATIONS.items()},
        "current_location": current_id,
    })

# travel endpoint to move between locations
# The travel endpoint checks if the player can move to the target location 
# based on the current location and the connections defined in LOCATIONS. 
# It updates the game state accordingly and responds with the new location's information.

@app.route("/travel", methods=["POST"])
def travel():
    p = gs["player"]
    if not p:
        return get_state()
    data = request.json
    target_id = data.get("location")
    current_id = gs["current_location"] or "town"
    if target_id == current_id:
        gs["log"] = ["You are already here."]
        return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])
    current = LOCATIONS.get(current_id)
    if not current or target_id not in current["connects_to"]:
        gs["log"] = ["You can't reach that location from here."]
        return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])
    target = LOCATIONS.get(target_id)
    if not target:
        return get_state()
    gs["current_location"] = target_id
    gs["log"] = [f"You arrive at {target['name']}."]
    if target["type"] in ("town", "village"):
        gs["screen"] = "town"
        return respond("town", target["name"], "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])
    elif target["type"] == "dungeon":
        gs["screen"] = "dungeon"
        return respond("dungeon", target["name"], "The entrance looms before you...", ["Enter", "(Back)"])
    else:
        gs["screen"] = "location"
        return respond("location", target["name"], "Nothing to do here yet.", ["(Back)"])

#================================
# ---- Dungeon ----
#================================

# Dungeon logic is handled here, 
# including entering the dungeon, progressing through floors, 
# and handling combat and rewards.
def enter_dungeon():
    gs["dungeon_floor"] = 1
    e = generate_dungeon_enemy(1, gs["player"].level)
    gs["enemy"] = e
    gs["log"] = ["You descend into the dungeon... Floor 1"]
    return dungeon_floor_state()

# Handle the state for each dungeon floor
def dungeon_floor_state():
    p = gs["player"]
    title = f"Dungeon - Floor {gs['dungeon_floor']}/10"
    e = gs["enemy"]
    if e and e.is_alive():
        body = f"{e.display()}\n\n{p.name}: HP {p.hp}/{p.max_hp}  AC {p.ac}"
        return respond("dungeon_floor", title, body, ["Attack"])
    else:
        body = "Floor cleared!"
        floor = gs["dungeon_floor"]
        if floor == 5:
            return respond("dungeon_floor", title, body, ["Visit Merchant", "Descend to Floor 6"])
        elif floor == 10:
            return respond("dungeon_floor", title, body, ["Visit Merchant", "Attack Boss"])
        else:
            return respond("dungeon_floor", title, body, [f"Descend to Floor {floor + 1}"])

# Handle actions on the dungeon floor, 
# including combat and merchant visits
def dungeon_floor_action(choice):
    e = gs["enemy"]
    floor = gs["dungeon_floor"]

    if e and e.is_alive():
        gs["screen"] = "combat"
        gs["log"] = []
        return combat_state()

    if floor == 5:
        if choice == 0:
            return dungeon_merchant()
        else:
            return advance_dungeon_floor()

    if floor == 10:
        if choice == 0:
            return dungeon_merchant()
        else:
            gs["screen"] = "combat"
            gs["log"] = ["The boss stands before you!"]
            return combat_state()

    return advance_dungeon_floor()

# Advance to the next dungeon floor, generating a new enemy
def advance_dungeon_floor():
    gs["dungeon_floor"] += 1
    floor = gs["dungeon_floor"]
    e = generate_dungeon_enemy(floor, gs["player"].level)
    gs["enemy"] = e
    gs["log"] = [f"You descend to Floor {floor}"]
    return dungeon_floor_state()

# After all combat/level-up/allocation is done, continue the game
def after_combat():
    # Quests put you back in front of the NPC you were talking to instead of
    # dropping you in the middle of Town.
    if gs.get("return_to") == "quest_npc":
        return quest_npc_state(gs.get("quest_npc_index", 0))
    if gs.get("return_to") == "quest_hub":
        return quest_hub_state()

    if gs["dungeon_floor"] > 0:
        if gs["dungeon_floor"] == 10:
            return respond("dungeon_victory", "DUNGEON CLEARED!", "You defeated the boss and conquered the dungeon!", ["Return to Village 1"])
        return dungeon_floor_state()
    gs["screen"] = "town"
    return respond("town", "Victory!", "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])

# Dungeon Merchant
def dungeon_merchant():
    gs["shop_name"] = "Potion Merchant"
    shop = SHOP_NPCS["Potion Merchant"]
    available = {n: d for n, d in shop["items"].items() if gs["player"].level >= d["min_level"]}
    items_list = [f"{n} ({d['price']}g)" for n, d in available.items()]
    gs["screen"] = "shop"
    return respond("shop", "Dungeon Merchant", "", items_list + ["(Back)"], extra={"shop_items": list(available.keys()), "shop_prices": [d["price"] for d in available.values()], "dungeon_shop": True})

if __name__ == "__main__":
    app.run(debug=True)